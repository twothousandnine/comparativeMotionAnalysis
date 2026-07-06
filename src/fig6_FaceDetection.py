import os
from icecream import ic
import numpy as np
import src.lib.directory as dir
import src.lib.plot_styles as ps
import src.lib.globals as globals
import pandas as pd
import matplotlib.pyplot as plt


def create_df() -> pd.DataFrame:
    df_lst = []
    scores = {'moca': {}, 'mp': {}}

    face_dir = os.path.join(globals.CODE_DIR, 'data', 'face')
    for file in dir.get_files(face_dir):
        df = dir.file_to_df(file)
        mode = 'moca' if 'moca' in os.path.basename(file).lower() else 'mp'

        for _, row in df.iterrows():
            rotation = row['rotation']
            score = row['numb_found']
            
            if rotation not in scores[mode]:
                scores[mode][rotation] = []
            scores[mode][rotation].append(score)

    for mode, rotations in scores.items():
        for rotation, rotation_scores in rotations.items():
            df_lst.append({
                'mode': mode,
                'rotation': rotation,
                'score': np.mean(rotation_scores)
            })

    return pd.DataFrame(df_lst)


def plot(df: pd.DataFrame) -> None:
    rotations = [0, 45, 90, 135, 180]
    moca_scores = df[df['mode'] == 'moca'].set_index('rotation')['score']
    mp_scores = df[df['mode'] == 'mp'].set_index('rotation')['score']

    applicable_markers = {
        0: 11,
        45: 6,
        90: 5,
        135: 1,
        180: 0
    }
    total_markers = max(applicable_markers.values())

    ps.color_style()
    plt.figure(figsize=(8, 5))
    applicable_values = [applicable_markers[r] for r in rotations]
    total_values = [total_markers] * len(rotations)

    plt.fill_between(
        rotations,
        applicable_values,
        total_values,
        color='gray',
        alpha=0.3,
        label='Inapplicable Markers'
    )

    plt.plot(rotations, [moca_scores.get(r, 0) for r in rotations],
              label='MoCa', linestyle='-', marker='o', linewidth=3, markersize=8)
    plt.plot(rotations, [mp_scores.get(r, 0) for r in rotations],
             label='MediaPipe', linestyle='-', marker='o', linewidth=3, markersize=8)

    plt.xticks(rotations)
    plt.xlabel('Rotation from Camera (°)')
    plt.ylabel('Markers Tracked')
    plt.legend()
    plt.grid(alpha=0.3)

    
    plt.tight_layout()
    OUTPATH = os.path.join(globals.FIGURES, 'face_exp.tiff')
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
