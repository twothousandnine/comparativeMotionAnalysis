import os
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import src.lib.directory as dir


def get_mode(filename: str) -> str:
    info = get_file_info(filename)
    return info['mode']


def get_ending_angle(df):
    return df["corrected_angles"][-30:].mean()


def get_variance(df):
    vars_ = []
    for column in df.columns:
        if column.endswith(" X") or column.endswith(" Y"):
            vars_.append(df[column].var())
    return sum(vars_) / len(vars_)


def get_duration(df: pd.DataFrame, framerate=60):
    frames = len(df)
    return round(frames / framerate, 2)


def smooth_motion(s: pd.Series, window_size=40) -> pd.Series:
    return s.rolling(window=window_size, min_periods=1).mean().shift(-window_size//2)


def get_file_info(filename: str) -> Dict[str, any]:
    # Remove any directory
    filename = os.path.basename(filename)
    title_elems = filename.removesuffix(".csv").split(".")

    labels = ["mode", "motion", "subject", "camera", "run"]
    num_elems = len(labels)
    if len(title_elems) != num_elems:
        raise ValueError(f"File {filename} must have {num_elems} elements.")

    info = {label: elem.lower() for label, elem in zip(labels, title_elems)}

    return info


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


def columns_from_stamps(stamps: str, col_names: str) -> Tuple:
    data = [None] * 2 * len(stamps)
    for col in col_names:
        colwords = col.lower().split()
        for i in range(len(stamps)):
            if stamps[i].lower() in colwords and "x" in colwords[-1].lower():
                data[2 * i] = col
            if stamps[i].lower() in colwords and "y" in colwords[-1].lower():
                data[2 * i + 1] = col

    return tuple(data)


def calculate_angle(df: pd.DataFrame, columns: Tuple[str], wrap: bool = False):
    assert all(column in df for column in columns)
    px, py, lx, ly, rx, ry = columns

    vector_pr = df[[rx, ry]].values - df[[px, py]].values
    vector_pl = df[[lx, ly]].values - df[[px, py]].values

    angle_pl = np.degrees(np.arctan2(vector_pl[:, 1], vector_pl[:, 0]))
    angle_pr = np.degrees(np.arctan2(vector_pr[:, 1], vector_pr[:, 0]))

    left_turn_angle = angle_pl - angle_pr

    if wrap:
        unwrapped_angles = np.unwrap(np.radians(left_turn_angle))
        df["corrected_angles"] = np.degrees(unwrapped_angles)
    else:
        df["corrected_angles"] = (left_turn_angle + 360) % 360


def add_angles(df: pd.DataFrame, filename: str) -> None:
    info = get_file_info(filename)

    stamps = stamps_from_motion(info['mode'], info['motion'], filename)
    columns = columns_from_stamps(stamps, df.columns)

    base = os.path.basename(filename.lower())
    wrap = "shoulderfe" in base

    calculate_angle(df, columns, wrap=wrap)


def get_motion(filename: str) -> str:
    file_split = filename.split(".")
    motion_column_indx = 1
    motion = file_split[motion_column_indx]

    return motion


def get_speed(filename):
    file_split = filename.split(".")
    run_speed = file_split[4]
    speed = run_speed[2:]

    return speed


def get_all_motions() -> List[str]:
    return [
        "BicepC",
        "ChestAA",
        "ShoulderAA",
        "ShoulderFE",
        "BodyLean"
    ]


def get_correlating_moca(mp_file: str, directory: str):
    basename = os.path.basename(mp_file)
    basename = basename.replace('cropped_', '')
    common_filename = basename[len("MEDIAPIPE."):-len(".csv")]

    moca_file = dir.search("MOCA", common_filename, directory=directory)
    assert len(moca_file) == 1, f"Incorrect number of files matched: {moca_file}"
    return moca_file[0]


def calc_rom(series: pd.Series) -> float:
    sorted_series = series.sort_values()
    n = len(sorted_series)
    
    cutoff = max(1, int(n * 0.025))
    
    bottom_avg = sorted_series.iloc[:cutoff].mean()
    top_avg = sorted_series.iloc[-cutoff:].mean()
    
    return top_avg - bottom_avg
