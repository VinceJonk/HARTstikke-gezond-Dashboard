# HARTstikke Gezond Dashboard

import base64
import glob
import io
import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from scipy.signal import find_peaks, savgol_filter
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="HARTstikke gezond",
    page_icon="🫀",
    layout="wide"
)

# FUNCTIES ECG / BPM

@st.cache_data
def samengestelde_vector(data, x_col, y_col, z_col):

    x = data[x_col].values
    y = data[y_col].values
    z = data[z_col].values

    return (x**2 + y**2 + z**2) ** 0.5


@st.cache_data
def tijdberekening(data):

    data = data.copy()

    data['time'] = pd.to_datetime(
        data['time'],
        unit='ms'
    )

    data['duur_seconden'] = (
        data['time'] - data['time'].iloc[0]
    ).dt.total_seconds()

    return data


@st.cache_data
def find_r_peaks(ecg_signal, threshold, distance=20):

    peaks, _ = find_peaks(
        ecg_signal,
        height=threshold,
        distance=distance
    )

    return peaks


def detect_ecg_peaks(ecg_signal, base_threshold, distance=20):
    """
    Detecteer ECG-pieken met licht smoothing en een adaptieve drempel.
    """
    signal = np.asarray(ecg_signal, dtype=float)

    if len(signal) >= 15:
        smooth_window = 15 if len(signal) >= 15 else len(signal) // 2 * 2 + 1
        if smooth_window % 2 == 0:
            smooth_window += 1
        signal_smoothed = savgol_filter(signal, smooth_window, 3)
    else:
        signal_smoothed = signal

    if len(signal_smoothed) > 5:
        candidates, _ = find_peaks(signal_smoothed, distance=distance)
        if len(candidates) >= 3:
            heights = signal_smoothed[candidates]
            threshold = max(
                np.percentile(heights, 35),
                np.mean(signal_smoothed) + 0.25 * np.std(signal_smoothed),
                base_threshold * 0.3
            )
            threshold = min(threshold, base_threshold)
        else:
            threshold = max(
                np.mean(signal_smoothed) + 0.25 * np.std(signal_smoothed),
                base_threshold * 0.25
            )
            threshold = min(threshold, base_threshold)
    else:
        threshold = base_threshold * 0.5

    peaks, properties = find_peaks(
        signal_smoothed,
        height=threshold,
        distance=distance,
        prominence=max(np.std(signal_smoothed) * 0.2, 1)
    )

    return peaks, properties, signal_smoothed, threshold


def calculate_bpm(data, peaks):

    totale_tijd = (
        data['duur_seconden'].iloc[-1]
        - data['duur_seconden'].iloc[0]
    )

    if totale_tijd <= 0:
        return 0

    bpm = (len(peaks) / totale_tijd) * 60

    return round(bpm, 1)


@st.cache_data
def calculate_bpm_per_window(
    data,
    ecg_signal,
    threshold,
    window_seconds=30,
    distance=20
):

    downsample_factor = 1
    if len(ecg_signal) > 100_000:
        downsample_factor = 10

    ecg_signal_ds = ecg_signal.iloc[::downsample_factor].reset_index(drop=True)
    data_ds = data.iloc[::downsample_factor].copy().reset_index(drop=True)

    adjusted_distance = max(distance // downsample_factor, 1)

    peaks, _, _, used_threshold = detect_ecg_peaks(
        ecg_signal_ds,
        threshold,
        distance=adjusted_distance
    )

    peak_times = data_ds['duur_seconden'].iloc[peaks].values
    start_time = data_ds['duur_seconden'].iloc[0]
    end_time = data_ds['duur_seconden'].iloc[-1]

    if len(peak_times) < 2:
        windows = []
        current_time = start_time
        while current_time < end_time:
            windows.append({'Tijd (s)': current_time, 'BPM': 0.0})
            current_time += window_seconds
        return pd.DataFrame(windows)

    rr_intervals = np.diff(peak_times)
    instant_bpm = 60.0 / (rr_intervals + 1e-6)
    interval_times = peak_times[:-1] + rr_intervals / 2.0

    windows = []
    current_time = start_time

    while current_time < end_time:
        window_end = current_time + window_seconds
        mask = (interval_times >= current_time) & (interval_times < window_end)

        if np.any(mask):
            bpm_value = float(np.mean(instant_bpm[mask]))
        else:
            before = instant_bpm[interval_times < current_time]
            after = instant_bpm[interval_times >= window_end]
            neighbors = []
            if len(before) > 0:
                neighbors.append(before[-1])
            if len(after) > 0:
                neighbors.append(after[0])
            bpm_value = float(np.mean(neighbors)) if len(neighbors) > 0 else np.nan

        windows.append({
            'Tijd (s)': current_time,
            'BPM': round(bpm_value, 1) if not np.isnan(bpm_value) else np.nan
        })

        current_time = window_end

    bpm_df = pd.DataFrame(windows)
    bpm_df['BPM'] = bpm_df['BPM'].interpolate(method='linear', limit_direction='both')
    bpm_df['BPM'] = bpm_df['BPM'].fillna(0)

    return bpm_df


@st.cache_data
def calculate_activity_per_window(
    data,
    ecg_signal,
    threshold,
    window_seconds=5,
    distance=40,
    movement_threshold_percentile=30,
    age=30
):
    """
    Bereken BPM per vaste blokken op basis van RR-intervallen.
    """
    data_ds = data.copy().reset_index(drop=True)
    ecg_signal_ds = ecg_signal.reset_index(drop=True)

    if len(data_ds) < 2:
        return pd.DataFrame(columns=['Tijd (s)', 'BPM', 'Beweging', 'Actief'])

    dt = np.median(np.diff(data_ds['duur_seconden'].values))
    fs = int(round(1.0 / dt)) if dt > 0 else 100
    if fs < 1:
        fs = 100

    block = fs * window_seconds
    n_blocks = len(ecg_signal_ds) // block

    max_hr = 220 - age
    bpm_threshold = 0.5 * max_hr
    movement_threshold = data_ds['Beweging'].quantile(movement_threshold_percentile / 100)

    windows = []

    for i in range(n_blocks):
        start_idx = i * block
        end_idx = start_idx + block
        segment = ecg_signal_ds.iloc[start_idx:end_idx].values
        segment_time = data_ds['duur_seconden'].iloc[start_idx]
        movement_segment = data_ds['Beweging'].iloc[start_idx:end_idx]

        if len(segment) > distance:
            peaks, _ = find_peaks(
                segment,
                distance=distance,
                height=np.percentile(segment, 60)
            )
        else:
            peaks = np.array([], dtype=int)

        if len(peaks) > 1:
            rr = np.diff(peaks) / fs * 1000
            rr_clean = rr[(rr > 300) & (rr < 1500)]
            bpm = round(60000 / rr_clean.mean(), 1) if len(rr_clean) > 1 else np.nan
        else:
            bpm = np.nan

        avg_movement = movement_segment.mean() if len(movement_segment) > 0 else np.nan
        is_active = bool((not np.isnan(bpm)) and (bpm > bpm_threshold) and (avg_movement > movement_threshold))

        windows.append({
            'Tijd (s)': round(segment_time),
            'BPM': bpm,
            'Beweging': round(avg_movement, 3) if not np.isnan(avg_movement) else np.nan,
            'Actief': is_active
        })

    bpm_df = pd.DataFrame(windows)
    bpm_df['BPM'] = bpm_df['BPM'].interpolate(method='linear', limit_direction='both')
    bpm_df['BPM'] = bpm_df['BPM'].fillna(0)

    return bpm_df


@st.cache_data
def compute_active_minutes(data, peaks, age, activity_window_data=None, threshold_pct=0.6, minute_window=60, min_continuous_minutes=10, enforce_uninterrupted=False):
    """
    Bereken actieve minuten.
    
    Als activity_window_data wordt doorgegeven, telt een minuut als actief wanneer:
    - Minstens één 10-seconden blok in die minuut Actief=True (dus zowel BPM als beweging aanwezig)
    
    Anders (legacy): telt een minuut als actief wanneer BPM > threshold_pct * (220 - age)
    """

    if data is None or len(peaks) == 0:
        return 0, pd.DataFrame(columns=['minute_start', 'bpm', 'is_active'])

    max_hr = 220 - age
    active_threshold = threshold_pct * max_hr

    start_time = int(np.floor(data['duur_seconden'].iloc[0]))
    end_time = int(np.ceil(data['duur_seconden'].iloc[-1]))

    # number of full minutes in the recording
    num_minutes = max(1, (end_time - start_time) // minute_window)

    minutes = []

    if activity_window_data is not None and len(activity_window_data) > 0:
        # Gebruik de Actief kolom uit activity_window_data (combineert BPM + beweging)
        for m in range(num_minutes):
            window_start = start_time + m * minute_window
            window_end = window_start + minute_window

            # Controleer welke 10-sec blokken in deze minuut vallen
            mask = (activity_window_data['Tijd (s)'] >= window_start) & (activity_window_data['Tijd (s)'] < window_end)
            
            if mask.any():
                # Een minuut is actief als minstens één 10-sec blok Actief=True is
                is_active = bool(activity_window_data['Actief'][mask].any())
                bpm_avg = activity_window_data['BPM'][mask].mean() if len(activity_window_data['BPM'][mask]) > 0 else 0
            else:
                is_active = False
                bpm_avg = 0

            minutes.append({
                'minute_start': window_start,
                'bpm': float(bpm_avg),
                'is_active': bool(is_active)
            })
    else:
        # Legacy berekening: alleen op basis van peaks/BPM
        peak_times = data['duur_seconden'].iloc[peaks].values

        for m in range(num_minutes):
            window_start = start_time + m * minute_window
            window_end = window_start + minute_window

            # count peaks in this minute
            count = np.sum((peak_times >= window_start) & (peak_times < window_end))

            bpm_minute = count  # beats per minute wanneer de window precies 60 seconden is

            is_active = bpm_minute > active_threshold

            minutes.append({
                'minute_start': window_start,
                'bpm': float(bpm_minute),
                'is_active': bool(is_active)
            })

    df_minutes = pd.DataFrame(minutes)

    if enforce_uninterrupted and len(df_minutes) > 0:
        flags = df_minutes['is_active'].values.astype(int)

        # find runs of consecutive ones
        counted = np.zeros_like(flags)

        i = 0
        while i < len(flags):
            if flags[i] == 1:
                j = i
                while j < len(flags) and flags[j] == 1:
                    j += 1

                run_len = j - i

                if run_len >= min_continuous_minutes:
                    counted[i:j] = 1

                i = j
            else:
                i += 1

        df_minutes['counted'] = counted.astype(bool)
        active_minutes = int(df_minutes['counted'].sum())
    else:
        df_minutes['counted'] = df_minutes['is_active']
        active_minutes = int(df_minutes['is_active'].sum())

    return active_minutes, df_minutes


# FUNCTIES GEZONDHEIDSTABEL

benchmark_values = {
    'Cholesterol_mmol_L': 5.0,
    'Systolisch': 120.0,
    'Diastolisch': 80.0,
    'Bloedsuiker_mmol_L': 4.0,
    'Actieve_minuten_per_dag': 30.0,
}

better_when_higher = {
    'Cholesterol_mmol_L': False,
    'Systolisch': False,
    'Diastolisch': False,
    'Bloedsuiker_mmol_L': False,
    'Actieve_minuten_per_dag': True,
}


def get_status_color(value, benchmark, higher_is_better, col=None):

    if pd.isna(value):
        return '#CCCCCC'

    # SPECIALE REGEL BLOEDSUIKER
    if col == 'Bloedsuiker_mmol_L':

        if 4.0 <= value <= 6.0:
            return '#4CAF50'   

        elif 3.5 <= value < 4.0 or 6.0 < value <= 6.5:
            return '#FFC107'   

        else:
            return '#F44336'   

    # SPECIALE REGEL ACTIEVE MINUTEN
    if col == 'Actieve_minuten_per_dag':

        if value < 21:
            return '#FF4444'   

        elif value <= 30:
            return '#4597CA'   

        else:
            return '#257A25'   
        
    # STANDAARD LOGICA
    if higher_is_better:

        if value > benchmark:
            return '#4CAF50'

        elif value == benchmark:
            return '#FFC107'

        else:
            return '#F44336'

    else:

        if value < benchmark:
            return '#4CAF50'

        elif value == benchmark:
            return '#FFC107'

        else:
            return '#F44336'


@st.cache_data
def make_bar_chart(value, benchmark, label):

    fig, ax = plt.subplots(figsize=(2.4, 1.5))

    ax.barh(
        ['Buurt', 'Norm'],
        [value, benchmark]
    )

    max_value = max(value, benchmark, 1)

    ax.set_xlim(0, max_value * 1.2)

    ax.set_xlabel(label)

    ax.set_xticks([])

    for i, x in enumerate([value, benchmark]):

        ax.text(
            x + max_value * 0.02,
            i,
            f'{x:.1f}',
            va='center',
            fontsize=8
        )

    fig.tight_layout()

    buf = io.BytesIO()

    plt.savefig(
        buf,
        format='png',
        dpi=120,
        bbox_inches='tight',
        transparent=True
    )

    plt.close(fig)

    buf.seek(0)

    return base64.b64encode(
        buf.read()
    ).decode('utf-8')

def data_processing(data):
    time_col = None
    for col in ['time_ms', 'time', 'timestamp', 'Time']:
        if col in data.columns:
            time_col = col
            break
    
    if time_col is None:
        raise ValueError(f"Geen tijd kolom gevonden. Beschikbare kolommen: {list(data.columns)}")
    
    # Rename to standard 'time' for consistent processing
    data = data.rename(columns={time_col: 'time'})

    return data

def make_single_tooltip(row, col):

    value = row[col]

    benchmark = benchmark_values.get(col)

    if pd.isna(value) or benchmark is None:
        return ""

    label = col.replace('_', ' ')

    img_b64 = make_bar_chart(
        value,
        benchmark,
        label
    )

# EEN HTML-STRING MET DE TOOLTIP-INHOUD, INCLUSIEF DE GEGENEREERDE GRAFIEK
    html = f"""
    <div style="line-height:1.4;">

        <div style="font-size:14px; margin-bottom:6px;">
            <strong>{row["Buurt"]}</strong>
        </div>

        <div style="font-size:12px; margin-bottom:6px;">
            {label}
        </div>

        <img
            src="data:image/png;base64,{img_b64}"
            style="width:220px; height:auto;"
        />

    </div>
    """

    return html


# =========================================
# HOOFDFUNCTIE
# =========================================

def main():

    # SESSION STATE

    if 'data' not in st.session_state:
        st.session_state.data = None

    if 'data_location' not in st.session_state:
        st.session_state.data_location = None

    # SIDEBAR

    st.sidebar.title("CSV Bestand")

    csv_files = glob.glob('Bestanden/*.csv')
    csv_files.sort()

    if not csv_files:
        st.sidebar.warning("Geen CSV bestanden gevonden.")
        return

    selected_file = st.sidebar.selectbox(
        "Selecteer bestand",
        csv_files
    )

    if selected_file:

        st.session_state.data_location = selected_file

        st.session_state.data = pd.read_csv(
            selected_file,
            sep=','
        )

        st.session_state.data.columns = (
            st.session_state.data.columns.str.strip()
        )

    # DATA

    raw_data = st.session_state.data

    data = data_processing(raw_data)

    if data is None:
        st.warning("Geen data geladen.")
        return

    # SIDEBAR: gebruiker-instellingen voor actieve minuten
    st.sidebar.markdown("---")
    st.sidebar.header("Actieve minuten instellingen")

    age = st.sidebar.number_input(
        "Leeftijd (jaar)",
        min_value=10,
        max_value=120,
        value=30,
        help="Gebruikersleeftijd voor maximale hartslag (220 - leeftijd)"
    )

    enforce_uninterrupted = st.sidebar.checkbox(
        "Gebruik onafgebroken-regel (minimaal 10 minuten)",
        value=False
    )

    min_continuous_minutes = st.sidebar.number_input(
        "Minimale aaneengesloten actieve minuten",
        min_value=1,
        max_value=60,
        value=10,
        help="Als de onafgebroken-regel aanstaat telt alleen een reeks van minstens dit aantal minuten"
    )

    # TITEL

    st.title("🫀 HARTstikke gezond Dashboard")

    st.markdown(
        """
        Dashboard voor analyse van ECG-,
        bewegings- en gezondheidsdata.
        """
    )

    # ECG DATA

    data = tijdberekening(data)

    data['Beweging'] = samengestelde_vector(
        data,
        'accX',
        'accY',
        'accZ'
    )

    threshold = data['ECG'].max() * 0.8

    peaks = find_r_peaks(
        data['ECG'],
        threshold
    )

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

    # BPM GRAFIEK

    st.subheader("Activiteit: BPM + Beweging")

    col1, col2 = st.columns([8, 2])

    with col1:
        # Interactieve grafiek met Plotly
        fig = go.Figure()
        
        # Voeg BPM lijn toe
        fig.add_trace(go.Scatter(
            x=activity_window_data['Tijd (s)'],
            y=activity_window_data['BPM'],
            mode='lines',
            name='BPM',
            line=dict(color='red', width=2),
            hovertemplate='<b>Tijd:</b> %{x:.1f}s<br><b>BPM:</b> %{y:.1f}<extra></extra>'
        ))
        
        # Voeg groene achtergrond toe waar beweging hoog is
        movement_threshold = data['Beweging'].quantile(0.45)
        active_mask = activity_window_data['Beweging'] > movement_threshold
        
        # Creëer shapes voor groene gebieden
        shapes = []
        in_active_region = False
        region_start = None
        
        for i, has_movement in enumerate(active_mask):
            time_val = activity_window_data['Tijd (s)'].iloc[i]
            
            if has_movement and not in_active_region:
                region_start = time_val
                in_active_region = True
            elif not has_movement and in_active_region:
                region_end = activity_window_data['Tijd (s)'].iloc[i-1]
                shapes.append(dict(
                    type="rect",
                    xref="x",
                    yref="paper",
                    x0=region_start,
                    y0=0,
                    x1=region_end,
                    y1=1,
                    fillcolor="green",
                    opacity=0.15,
                    layer="below",
                    line_width=0,
                ))
                in_active_region = False
        
        # Sluit de laatste regio als deze nog open staat
        if in_active_region:
            region_end = activity_window_data['Tijd (s)'].iloc[-1]
            shapes.append(dict(
                type="rect",
                xref="x",
                yref="paper",
                x0=region_start,
                y0=0,
                x1=region_end,
                y1=1,
                fillcolor="green",
                opacity=0.15,
                layer="below",
                line_width=0,
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

    with col2:
        # Bereken actieve minuten (nu met BPM + beweging combinatie)
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
        
        st.metric(
            label="Actieve minuten",
            value=f"{active_minutes}"
        )

        # tooltip / uitleg: korte uitleg + groene legenda
        st.markdown(
            "<div style='display:flex; align-items:center; font-size:12px;'>"
            "<span style='margin-right:12px;'>Een minuut telt als actief wanneer de gemiddelde hartslag in die minuut boven 60% van de maximale hartslag (220 - leeftijd) ligt en er beweging aanwezig is.</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        # Kleine legenda met groen blokje
        st.markdown(
            "<div style='display:flex; align-items:center; margin-top:6px;'>"
            "<div style='width:12px; height:12px; background:green; border-radius:2px; margin-right:8px;'></div>"
            "<div style='font-size:12px;'>Gedetecteerde beweging</div>"
            "</div>",
            unsafe_allow_html=True,
        )



    # BUURTGEGEVENS

    st.subheader("Buurtvergelijking")

    buurt_file = r'BuurtData\anonieme_buurtbewoners_gezondheid.csv'
    buurt_mtime = os.path.getmtime(buurt_file)

    @st.cache_data
    def load_group_data(path, mtime):
        return pd.read_csv(path)

    group_data = load_group_data(buurt_file, buurt_mtime)

    group_data.columns = (
        group_data.columns.str.strip()
    )

    group_data[['Systolisch', 'Diastolisch']] = (
        group_data['Bloeddruk_mmHg']
        .str.split('/', expand=True)
        .astype(float)
    )

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
        'Actieve_minuten_per_dag'
    ]


    # HTML TABEL MET TOOLTIPS
    
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

    html += '<table class="comparison-table">'
    html += '<thead><tr>'

    for col in columns:

        label = col.replace('_', ' ')

        html += f'<th>{label}</th>'

    html += '</tr></thead><tbody>'

    for _, row in gemiddelde_per_buurt.iterrows():

        html += '<tr>'

        for col in columns:

            if col == 'Buurt':

                html += f'<td>{row[col]}</td>'

                continue

            value = row[col]

            benchmark = benchmark_values.get(col)

            color = get_status_color(
                value,
                benchmark,
                better_when_higher[col],
                col
            )

            tooltip_html = make_single_tooltip(row, col)

            html += f"""
            <td>

                <span class="cell-tooltip">

                    {value:.2f}

                    <span
                        class="status-dot"
                        style="background:{color};">
                    </span>

                    <span class="tooltip-content">
                        {tooltip_html}
                    </span>

                </span>

            </td>
            """

        html += '</tr>'

    html += '</tbody></table>'

    components.html(
        html,
        height=500,
        scrolling=True
    )


    # knop naar kaart

    st.markdown("---")

    if st.button("📍 Naar kaart"):
        st.switch_page("pages/Kaart.py")


# START APP

if __name__ == "__main__":
    main()
