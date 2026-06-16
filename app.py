# app.py
# HARTstikke Gezond Dashboard — UI

import glob

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from data_utils import data_processing, prepare_group_data
from ecg_utils import (
    calculate_activity_per_window,
    calculate_bpm,
    compute_active_minutes,
    find_r_peaks,
    samengestelde_vector,
    tijdberekening,
)
from health_utils import (
    benchmark_values,
    better_when_higher,
    get_status_color,
    make_single_tooltip,
)

st.set_page_config(
    page_title="HARTstikke gezond",
    page_icon="🫀",
    layout="wide"
)


# BPM + bewegingsgrafiek

def render_activity_chart(activity_window_data: pd.DataFrame, data: pd.DataFrame):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=activity_window_data['Tijd (s)'],
        y=activity_window_data['BPM'],
        mode='lines',
        name='BPM',
        line=dict(color='red', width=2),
        hovertemplate='<b>Tijd:</b> %{x:.1f}s<br><b>BPM:</b> %{y:.1f}<extra></extra>'
    ))

    movement_threshold = data['Beweging'].quantile(0.45)
    active_mask = activity_window_data['Beweging'] > movement_threshold

    shapes = []
    in_active_region = False
    region_start = None

    for i, has_movement in enumerate(active_mask):
        time_val = activity_window_data['Tijd (s)'].iloc[i]

        if has_movement and not in_active_region:
            region_start = time_val
            in_active_region = True
        elif not has_movement and in_active_region:
            region_end = activity_window_data['Tijd (s)'].iloc[i - 1]
            shapes.append(dict(
                type="rect", xref="x", yref="paper",
                x0=region_start, y0=0, x1=region_end, y1=1,
                fillcolor="green", opacity=0.15, layer="below", line_width=0,
            ))
            in_active_region = False

    if in_active_region:
        region_end = activity_window_data['Tijd (s)'].iloc[-1]
        shapes.append(dict(
            type="rect", xref="x", yref="paper",
            x0=region_start, y0=0, x1=region_end, y1=1,
            fillcolor="green", opacity=0.15, layer="below", line_width=0,
        ))

    fig.update_layout(
        shapes=shapes,
        hovermode='x unified',
        title='Activiteit over tijd',
        xaxis_title='Tijd (s)',
        yaxis_title='BPM',
        height=400,
        template='plotly_white',
        margin=dict(l=50, r=50, t=50, b=50),
    )

    st.plotly_chart(fig, use_container_width=True)


# buurtvergelelijkingstabel

def render_buurt_table(active_minutes: int):
    st.subheader("Buurtvergelijking")

    buurt_file = r'BuurtData\anonieme_buurtbewoners_gezondheid.csv'
    group_data = prepare_group_data(buurt_file)

    gemiddelde_per_buurt = (
        group_data
        .groupby('Buurt')
        .mean(numeric_only=True)
        .reset_index()
        .round(2)
    )

    columns = [
        'Buurt',
        'Cholesterol_mmol_L',
        'Systolisch',
        'Diastolisch',
        'Bloedsuiker_mmol_L',
        'Actieve_minuten_per_dag',
    ]

    # CSS + tabel 
    html = """
    <style>
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    .comparison-table th,
    .comparison-table td {
        border: 1px solid #ddd;
        padding: 8px;
    }
    .comparison-table th {
        background: #f5f5f5;
    }
    .cell-tooltip {
        position: relative;
        display: inline-block;
    }
    .tooltip-content {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        width: 240px;
        background: white;
        border: 1px solid #ccc;
        padding: 10px;
        z-index: 1000;
        top: 24px;
        left: 0;
        transition: opacity 0.2s;
    }
    .cell-tooltip:hover .tooltip-content {
        visibility: visible;
        opacity: 1;
    }
    .status-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-left: 6px;
    }
    </style>
    """

    html += '<table class="comparison-table"><thead><tr>'
    for col in columns:
        html += f'<th>{col.replace("_", " ")}</th>'
    html += '</tr></thead><tbody>'

    for _, row in gemiddelde_per_buurt.iterrows():
        html += '<tr>'
        for col in columns:
            if col == 'Buurt':
                html += f'<td>{row[col]}</td>'
                continue

            value = row[col]
            benchmark = benchmark_values.get(col)
            color = get_status_color(value, benchmark, better_when_higher[col], col)
            tooltip_html = make_single_tooltip(row, col)

            html += f"""
            <td>
                <span class="cell-tooltip">
                    {value:.2f}
                    <span class="status-dot" style="background:{color};"></span>
                    <span class="tooltip-content">{tooltip_html}</span>
                </span>
            </td>
            """
        html += '</tr>'

    html += '</tbody></table>'
    components.html(html, height=500, scrolling=True)


# ── Hoofdfunctie ──────────────────────────────────────────────────────────────

def main():

    # Session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'data_location' not in st.session_state:
        st.session_state.data_location = None

    # Sidebar: bestandskeuze
    st.sidebar.title("CSV Bestand")
    csv_files = glob.glob('Bestanden/*.csv')
    csv_files.sort()

    if not csv_files:
        st.sidebar.warning("Geen CSV bestanden gevonden.")
        return

    selected_file = st.sidebar.selectbox("Selecteer bestand", csv_files)

    if selected_file:
        st.session_state.data_location = selected_file
        st.session_state.data = pd.read_csv(selected_file, sep=',')
        st.session_state.data.columns = st.session_state.data.columns.str.strip()

    # Data laden & verwerken
    raw_data = st.session_state.data
    data = data_processing(raw_data)

    if data is None:
        st.warning("Geen data geladen.")
        return

    # Sidebar: actieve-minuten instellingen
    st.sidebar.markdown("---")
    st.sidebar.header("Actieve minuten instellingen")

    age = st.sidebar.number_input(
        "Leeftijd (jaar)",
        min_value=10, max_value=120, value=30,
        help="Gebruikersleeftijd voor maximale hartslag (220 - leeftijd)"
    )
    enforce_uninterrupted = st.sidebar.checkbox(
        "Gebruik onafgebroken-regel (minimaal 10 minuten)",
        value=False
    )
    min_continuous_minutes = st.sidebar.number_input(
        "Minimale aaneengesloten actieve minuten",
        min_value=1, max_value=60, value=10,
        help="Als de onafgebroken-regel aanstaat telt alleen een reeks van minstens dit aantal minuten"
    )

    # Titel
    st.title("🫀 HARTstikke gezond Dashboard")
    st.markdown("Dashboard voor analyse van ECG-, bewegings- en gezondheidsdata.")

    # ECG verwerking
    data = tijdberekening(data)
    data['Beweging'] = samengestelde_vector(data, 'accX', 'accY', 'accZ')

    threshold = data['ECG'].max() * 0.8
    peaks = find_r_peaks(data['ECG'], threshold)
    bpm = calculate_bpm(data, peaks)

    activity_window_data = calculate_activity_per_window(
        data,
        data['ECG'],
        threshold,
        window_seconds=10,
        distance=40,
        movement_threshold_percentile=30,
        age=int(age)
    )

    # BPM + bewegingsgrafiek
    st.subheader("Activiteit: BPM + Beweging")
    col1, col2 = st.columns([8, 2])

    with col1:
        render_activity_chart(activity_window_data, data)

    with col2:
        active_minutes, df_minutes = compute_active_minutes(
            data,
            peaks,
            age=int(age),
            activity_window_data=activity_window_data,
            threshold_pct=0.6,
            minute_window=60,
            min_continuous_minutes=int(min_continuous_minutes),
            enforce_uninterrupted=bool(enforce_uninterrupted)
        )

        st.metric(label="Actieve minuten", value=f"{active_minutes}")

        st.markdown(
            "<div style='display:flex; align-items:center; font-size:12px;'>"
            "<span style='margin-right:12px;'>Een minuut telt als actief wanneer de gemiddelde hartslag "
            "in die minuut boven 60% van de maximale hartslag (220 - leeftijd) ligt en er beweging aanwezig is.</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='display:flex; align-items:center; margin-top:6px;'>"
            "<div style='width:12px; height:12px; background:green; border-radius:2px; margin-right:8px;'></div>"
            "<div style='font-size:12px;'>Gedetecteerde beweging</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    # Buurtvergelelijking
    render_buurt_table(active_minutes)

    # Navigatie naar kaart
    st.markdown("---")
    if st.button("📍 Naar kaart"):
        st.switch_page("pages/Kaart.py")


if __name__ == "__main__":
    main()
