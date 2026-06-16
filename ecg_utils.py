# ecg_utils.py
# ECG- en BPM-rekenfuncties voor HARTstikke Gezond Dashboard

import numpy as np
import pandas as pd
import streamlit as st
from scipy.signal import find_peaks, savgol_filter


@st.cache_data
def samengestelde_vector(data, x_col, y_col, z_col):
    x = data[x_col].values
    y = data[y_col].values
    z = data[z_col].values
    return (x**2 + y**2 + z**2) ** 0.5


@st.cache_data
def tijdberekening(data):
    data = data.copy()
    data['time'] = pd.to_datetime(data['time'], unit='ms')
    data['duur_seconden'] = (
        data['time'] - data['time'].iloc[0]
    ).dt.total_seconds()
    return data


@st.cache_data
def find_r_peaks(ecg_signal, threshold, distance=20):
    peaks, _ = find_peaks(ecg_signal, height=threshold, distance=distance)
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
    bpm_threshold = 0.6 * max_hr
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
        is_active = bool(
            (not np.isnan(bpm))
            and (bpm > bpm_threshold)
            and (avg_movement > movement_threshold)
        )

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
def compute_active_minutes(
    data,
    peaks,
    age,
    activity_window_data=None,
    threshold_pct=0.6,
    minute_window=60,
    min_continuous_minutes=10,
    enforce_uninterrupted=False
):
    """
    Bereken actieve minuten.

    Als activity_window_data wordt doorgegeven, telt een minuut als actief wanneer:
    - Minstens één 10-seconden blok in die minuut Actief=True (BPM + beweging aanwezig)

    Anders (legacy): telt een minuut als actief wanneer BPM > threshold_pct * (220 - age)
    """
    if data is None or len(peaks) == 0:
        return 0, pd.DataFrame(columns=['minute_start', 'bpm', 'is_active'])

    max_hr = 220 - age
    active_threshold = threshold_pct * max_hr

    start_time = int(np.floor(data['duur_seconden'].iloc[0]))
    end_time = int(np.ceil(data['duur_seconden'].iloc[-1]))

    num_minutes = max(1, (end_time - start_time) // minute_window)
    minutes = []

    if activity_window_data is not None and len(activity_window_data) > 0:
        for m in range(num_minutes):
            window_start = start_time + m * minute_window
            window_end = window_start + minute_window

            mask = (
                (activity_window_data['Tijd (s)'] >= window_start)
                & (activity_window_data['Tijd (s)'] < window_end)
            )

            if mask.any():
                is_active = bool(activity_window_data['Actief'][mask].any())
                bpm_avg = (
                    activity_window_data['BPM'][mask].mean()
                    if len(activity_window_data['BPM'][mask]) > 0
                    else 0
                )
            else:
                is_active = False
                bpm_avg = 0

            minutes.append({
                'minute_start': window_start,
                'bpm': float(bpm_avg),
                'is_active': bool(is_active)
            })
    else:
        peak_times = data['duur_seconden'].iloc[peaks].values

        for m in range(num_minutes):
            window_start = start_time + m * minute_window
            window_end = window_start + minute_window

            count = np.sum(
                (peak_times >= window_start) & (peak_times < window_end)
            )
            bpm_minute = count
            is_active = bpm_minute > active_threshold

            minutes.append({
                'minute_start': window_start,
                'bpm': float(bpm_minute),
                'is_active': bool(is_active)
            })

    df_minutes = pd.DataFrame(minutes)

    if enforce_uninterrupted and len(df_minutes) > 0:
        flags = df_minutes['is_active'].values.astype(int)
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
