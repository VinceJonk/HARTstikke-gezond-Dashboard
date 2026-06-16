# health_utils.py
# Gezondheidstabel-functies voor HARTstikke Gezond Dashboard

import base64
import io

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


# Benchmarks & richting

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


# Kleur per waarde 

def get_status_color(value, benchmark, higher_is_better, col=None):
    if pd.isna(value):
        return '#CCCCCC'

    # Speciale regel: bloedsuiker
    if col == 'Bloedsuiker_mmol_L':
        if 4.0 <= value <= 6.0:
            return '#4CAF50'
        elif 3.5 <= value < 4.0 or 6.0 < value <= 6.5:
            return '#FFC107'
        else:
            return '#F44336'

    # Speciale regel: actieve minuten
    if col == 'Actieve_minuten_per_dag':
        if value < 21:
            return '#FF4444'
        elif value <= 30:
            return '#4597CA'
        else:
            return '#257A25'

    # Standaard logica
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


# Staafdiagram (base64 PNG)

@st.cache_data
def make_bar_chart(value, benchmark, label):
    fig, ax = plt.subplots(figsize=(2.4, 1.5))

    ax.barh(['Buurt', 'Norm'], [value, benchmark])
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
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


# HTML-tooltip

def make_single_tooltip(row, col):
    value = row[col]
    benchmark = benchmark_values.get(col)

    if pd.isna(value) or benchmark is None:
        return ""

    label = col.replace('_', ' ')
    img_b64 = make_bar_chart(value, benchmark, label)

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
