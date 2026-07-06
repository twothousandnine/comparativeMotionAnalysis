import os
from scipy.stats import mannwhitneyu
from icecream import ic
import pandas as pd
import matplotlib.pyplot as plt
import src.lib.directory as dir
import src.lib.processing as proc
from typing import Dict,List,Tuple
import src.lib.globals as globals
import numpy as np


def get_speed(filename: str) -> str:
    base = os.path.basename(filename)
    split = base.split('.')
    trial = split[3]
    speed = trial[2:].lower()
    return speed


def filter_files_by_speed(files: List, speed: str) -> List:
    def is_correct_speed(file: str, speed: str):
        trial_speed = get_speed(file)
        if speed == trial_speed:
            return True
        return False
    
    filtered = [file for file in files if is_correct_speed(file, speed)]
    return filtered


def agg_roughness(files: str, mode: str, title: str = '') -> float:
    all_roughness = []
    for file in files:
        df = dir.file_to_df(file)
        col = f'{mode}_roughness'
        if col in df.columns:
            roughness = df[col].mean()
            all_roughness.append(roughness)
        else:
            raise ValueError(f"Column '{col}' not found in file: {file}")
    
    # Plot the distribution of all roughness
    plt.figure(figsize=(8, 6))
    plt.hist(all_roughness, bins=20, color='blue', alpha=0.7, edgecolor='black')
    plt.title(title if title else f'Roughness Distribution ({mode})')
    plt.xlabel('Roughness')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.show()
    
    avg = np.mean(all_roughness)
    return avg


def calc_p_value(data1: List[float], data2: List[float]) -> float:
    test_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
    return test_stat, p_value


def gather_roughness(files: List[str], mode: str) -> List[str]:
    all_roughness = []
    for file in files:
        df = dir.file_to_df(file)
        col = f'{mode}_roughness'
        if col in df.columns:
            roughness = df[col].mean()
            all_roughness.append(roughness)
        else:
            raise ValueError(f"Column '{col}' not found in file: {file}")
    
    return all_roughness


def calc_motion(motion: str) -> Tuple[Dict, Dict]:
    files = dir.search(motion, directory=globals.ALIGNED_DATA)

    slow_files = filter_files_by_speed(files, 'slow')
    mp_slow = gather_roughness(slow_files, 'mp')
    moca_slow = gather_roughness(slow_files, 'moca')

    s_mp_med = round(np.median(mp_slow), 3)
    s_mp_q1, s_mp_q3 = np.percentile(mp_slow, [25, 75])
    s_mp_q1, s_mp_q3 = round(s_mp_q1, 3), round(s_mp_q3)
    
    s_moca_med = round(np.median(moca_slow), 3)
    s_moca_q1, s_moca_q3 = np.percentile(moca_slow, [25,75])
    s_moca_q1, s_moca_q3 = round(s_moca_q1, 3), round(s_moca_q3)

    s_u_stat, s_p_val = calc_p_value(mp_slow, moca_slow)
    s_u_stat, s_p_val = round(s_u_stat, 3), round(s_p_val, 3)

    slow_row = {
        'motion': motion,
        'trial_speed': 'slow',
        'moca median [IQR]': (s_moca_med, [s_moca_q1, s_moca_q3]),
        'mp median [IQR]': (s_mp_med, [s_mp_q1, s_mp_q3]),
        'U-statistic': s_u_stat,
        'p_value': s_p_val
    }

    fast_files = filter_files_by_speed(files, 'fast')
    mp_fast = gather_roughness(fast_files, 'mp')
    moca_fast = gather_roughness(fast_files, 'moca')

    f_mp_med = round(np.median(mp_fast), 3)
    f_mp_q1, f_mp_q3 = np.percentile(mp_fast, [25, 75])
    f_mp_q1, f_mp_q3 = round(f_mp_q1, 3), round(f_mp_q3, 3)

    f_moca_med = round(np.median(moca_fast), 3)
    f_moca_q1, f_moca_q3 = np.percentile(moca_fast, [25,75])
    f_moca_q1, f_moca_q3 = round(f_moca_q1, 3), round(f_moca_q3, 3)

    f_u_stat, f_p_val = calc_p_value(mp_fast, moca_fast)
    f_u_stat, f_p_val = round(f_u_stat, 3), round(f_p_val, 3)


    fast_row = {
        'motion': motion,
        'trial_speed': 'fast',
        'moca median [IQR]': (f_moca_med, [f_moca_q1, f_moca_q3]),
        'mp median [IQR]': (f_mp_med, [f_mp_q1, f_mp_q3]),
        'U-statistic': f_u_stat,
        'p_value': f_p_val
    }

    return slow_row, fast_row


def create_df() -> pd.DataFrame:
    temp_lst = []
    motions = proc.get_all_motions()
    for motion in motions:
        rows = calc_motion(motion)
        temp_lst.extend(rows)

    df = pd.DataFrame(temp_lst)
    return df


def main():
    df = create_df()
    ic(df)
    return


if __name__ == "__main__":
    main()
