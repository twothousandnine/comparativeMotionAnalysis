from typing import List

import pandas as pd


def get_all_motions() -> List[str]:
    return [
        "BicepC",
        "ChestAA",
        "ShoulderAA",
        "ShoulderFE",
        "BodyLean"
    ]


def calc_rom(series: pd.Series) -> float:
    sorted_series = series.sort_values()
    n = len(sorted_series)

    cutoff = max(1, int(n * 0.025))

    bottom_avg = sorted_series.iloc[:cutoff].mean()
    top_avg = sorted_series.iloc[-cutoff:].mean()

    return top_avg - bottom_avg
