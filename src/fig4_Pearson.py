import os
import src.lib.plot_styles as ps
from icecream import ic
import pandas as pd
import matplotlib.pyplot as plt
import src.lib.directory as dir
import src.lib.processing as proc
from typing import Dict
import src.lib.globals as globals
import numpy as np


def aggregate_correlations(motion: str) -> Dict:
    files = dir.search(motion, directory=globals.ALIGNED_DATA)
    all_correlations = []

    for file in files:
        df = dir.file_to_df(file)
        moca = df['moca_angles']
        mp = df['mp_angles']        
        correlation = moca.corr(mp, method='pearson')
        all_correlations.append(correlation)

    avg_corr = np.mean(all_correlations)
    MOTION_MAP = {
        'BicepC': 'Bicep\nCurl',
        'ChestAA': 'Chest\nAA',
        'ShoulderAA': 'Shoulder\nAA',
        'ShoulderFE': 'Shoulder\nFE',
        'BodyLean': 'Body\nLean'
    }

    aggregate_row = {
        'motion': MOTION_MAP[motion],
        'avg_corr': avg_corr
    }
    return aggregate_row


def create_df() -> pd.DataFrame:
    temp_lst = []

    motions = proc.get_all_motions()
    for motion in motions:
        row = aggregate_correlations(motion)
        temp_lst.append(row)

    df = pd.DataFrame(temp_lst)
    return df


def plot(df: pd.DataFrame) -> None:
    ps.color_style()
    plt.figure()

    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.bar(df['motion'].to_list(), df['avg_corr'].values.flatten(), zorder=2)
    plt.xlabel('Motions', fontsize=12)
    plt.ylabel('Avg Pearson Correlation', fontsize=12)
    plt.xticks(fontsize=8)

    OUTPATH = os.path.join(globals.FIGURES, 'avg_pearson.tiff')
    plt.savefig(OUTPATH, dpi=300)
    plt.show()
    plt.close()


def main():
    df = create_df()
    ic(df)
    plot(df)
    return


if __name__ == "__main__":
    main()
