import os
from icecream import ic
import pandas as pd
import numpy as np
from typing import List,Tuple,Dict
import src.lib.globals as globals
import src.lib.directory as dir
from scipy.signal import butter, filtfilt


def columns_from_stamps(stamps: str, col_names: str) -> Tuple:
    data = [None] * 2 * len(stamps)
    for col in col_names:
        colwords = col.lower().split()
        for i in range(len(stamps)):
            if stamps[i].lower() in colwords and "x" in colwords[-1].lower() \
            and 'smoothed' not in colwords[-1].lower():
                data[2 * i] = col
            if stamps[i].lower() in colwords and "y" in colwords[-1].lower() \
            and 'smoothed' not in colwords[-1].lower():
                data[2 * i + 1] = col

    return tuple(data)


def smoothed_columns_from_stamps(stamps: str, col_names: str) -> Tuple:
    data = [None] * 2 * len(stamps)
    for col in col_names:
        colwords = col.lower().split()
        for i in range(len(stamps)):
            if stamps[i].lower() in colwords and "x" in colwords[-1].lower() \
            and 'smoothed' in colwords[-1].lower():
                data[2 * i] = col
            if stamps[i].lower() in colwords and "y" in colwords[-1].lower() \
            and 'smoothed' in colwords[-1].lower():
                data[2 * i + 1] = col

    return tuple(data)


def stamps_from_motion(mode: str, motion: str, filename: str) -> Tuple:
    key = f"{mode.lower()}_{motion.lower()}"
    mappings = {
        "mediapipe_bicepc": ("right_elbow", "right_shoulder", "right_pinky"),
        "mediapipe_bodylean": ("left_hip",  "left_knee", "nose"),
        "mediapipe_chestaa": ("right_shoulder", "nose", "right_pinky"),
        "mediapipe_shoulderaa": ("right_shoulder", "right_hip", "right_pinky"),
        "mediapipe_shoulderfe": ("right_shoulder", "right_pinky", "right_hip"),

        "moca_bicepc": ("elbow", "hand", "shoulder"),
        "moca_bodylean": ("back", "neck", "leg"),
        "moca_chestaa": ("shoulder", "hand", "head"),
        "moca_shoulderaa": ("shoulder", "hand", "body"),
        "moca_shoulderfe": ("shoulder", "body", "hand"),
    }

    if key not in mappings:
        assert False, f"Motion mapping not found for {filename}"

    return mappings[key]


def get_file_info(filename: str) -> Dict[str, any]:
    filename = os.path.basename(filename)
    filename = filename.replace('cropped_', '')
    title_elems = filename.removesuffix(".csv").split(".")

    labels = ["mode", "motion", "subject", "camera", "run"]
    num_elems = len(labels)
    if len(title_elems) != num_elems:
        raise ValueError(f"File {filename} must have {num_elems} elements.")

    info = {label: elem.lower() for label, elem in zip(labels, title_elems)}

    return info


def get_original_columns(filename: str) -> List[str]:
    info = get_file_info(filename)
    df = dir.file_to_df(filename)
    stamps = stamps_from_motion(info['mode'], info['motion'], filename)
    columns = columns_from_stamps(stamps, df.columns)
    return columns


def calculate_angle(df: pd.DataFrame, columns: Tuple[str],  wrap: bool = False) -> pd.Series:
    assert all(column in df for column in columns)
    px, py, lx, ly, rx, ry = columns

    vector_pr = df[[rx, ry]].values - df[[px, py]].values
    vector_pl = df[[lx, ly]].values - df[[px, py]].values

    angle_pl = np.degrees(np.arctan2(vector_pl[:, 1], vector_pl[:, 0]))
    angle_pr = np.degrees(np.arctan2(vector_pr[:, 1], vector_pr[:, 0]))

    left_turn_angle = angle_pl - angle_pr

    if wrap:
        unwrapped_angles = np.unwrap(np.radians(left_turn_angle))
        angles = np.degrees(unwrapped_angles)
    else:
        angles = (left_turn_angle + 360) % 360

    return pd.Series(angles)


def apply_ema(series, alpha):
    return series.ewm(alpha=alpha, adjust=False).mean()


def get_smoothed_columns(filename: str, df: pd.DataFrame) -> List[str]:
    info = get_file_info(filename)
    stamps = stamps_from_motion(info['mode'], info['motion'], filename)
    columns = smoothed_columns_from_stamps(stamps, df.columns)

    smoothed_cols = []
    for col in columns:
        if '_smoothed' in col:
            smoothed_cols.append(col)
    
    return smoothed_cols


def smooth_all_markers(df: pd.DataFrame, filename: str, cutoff: float, order: int = 2) -> None:
    original_columns = get_original_columns(filename)
    
    def apply_butterworth_filter(series, cutoff_freq, filter_order):
        nyquist = 0.5  # Assuming normalized frequencies (sampling rate of 1)
        normal_cutoff = cutoff_freq / nyquist
        b, a = butter(filter_order, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, series)
    
    for col in original_columns:
        smoothed_series = apply_butterworth_filter(df[col], cutoff, order)
        df[f"{col}_smoothed"] = smoothed_series


def add_angles(file: str) -> pd.Series:
    df = dir.file_to_df(file)
    smooth_all_markers(df, file, cutoff=0.1, order=3)

    base = os.path.basename(file.lower())
    wrap = "shoulderfe" in base
    smoothed_columns = get_smoothed_columns(file, df)
    new_angles =  calculate_angle(df, smoothed_columns, wrap=wrap)
    smoothed_angles = apply_ema(new_angles, alpha=0.4)
    df['angles'] = smoothed_angles

    
    df.to_csv(file, index=False)
    return


def main():
    INPUT_FOLDER = globals.RAW_DATA
    all_files = dir.search(directory=INPUT_FOLDER)

    for file in all_files:
        ic(file)
        add_angles(file)
    
    return


if __name__ == "__main__":
    main()
