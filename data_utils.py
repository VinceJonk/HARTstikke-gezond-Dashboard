# data_utils.py
# Datalaad- en verwerkingsfuncties voor HARTstikke Gezond Dashboard

import os

import pandas as pd
import streamlit as st


def data_processing(data: pd.DataFrame) -> pd.DataFrame:
    """
    Zoek de tijdkolom, hernoem naar 'time' en geef het DataFrame terug.
    Gooit een ValueError als er geen bekende tijdkolom gevonden wordt.
    """
    time_col = None
    for col in ['time_ms', 'time', 'timestamp', 'Time']:
        if col in data.columns:
            time_col = col
            break

    if time_col is None:
        raise ValueError(
            f"Geen tijdkolom gevonden. Beschikbare kolommen: {list(data.columns)}"
        )

    data = data.rename(columns={time_col: 'time'})
    return data


@st.cache_data
def load_group_data(path: str, mtime: float) -> pd.DataFrame:
    """
    Laad buurtdata als CSV. mtime wordt meegestuurd zodat de cache
    automatisch verloopt als het bestand op disk wijzigt.
    """
    return pd.read_csv(path)


def prepare_group_data(buurt_file: str) -> pd.DataFrame:
    """
    Laad, schoon en bereid de buurtdata voor.
    Splitst de bloeddrukkolom in Systolisch en Diastolisch.
    """
    mtime = os.path.getmtime(buurt_file)
    group_data = load_group_data(buurt_file, mtime)

    group_data.columns = group_data.columns.str.strip()

    group_data[['Systolisch', 'Diastolisch']] = (
        group_data['Bloeddruk_mmHg']
        .str.split('/', expand=True)
        .astype(float)
    )

    return group_data
