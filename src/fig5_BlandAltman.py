import  os
import  numpy as np
import  pandas as pd
from    typing import List,Tuple
from    icecream import ic
from    src.lib.globals import *
import  matplotlib.pyplot as plt
import  src.lib.directory as dir
import  src.lib.plot_styles as ps
import scipy.stats as stats
import src.lib.globals as globals


SAVE = True
SHOW = False
FILEPATH = os.path.join(globals.FIGURES, 'ba_angles_motions.tiff')


def get_datapoints(motion: str) -> Tuple[pd.Series, pd.Series]:
    moca_data_list = []
    mp_data_list = []

    for file in dir.search(motion, directory=ALIGNED_DATA):
        df = dir.file_to_df(file)
        moca_data_list.extend(df['moca_angles'].values)
        mp_data_list.extend(df['mp_angles'].values)

    data_a = pd.Series(mp_data_list)
    data_b = pd.Series(moca_data_list)
    return data_a, data_b


def add_subplot(ax, motion: str, x_label: str, y_label: str) -> None:
    data_a, data_b = get_datapoints(motion)

    # Calculate the mean and differences
    mean = (data_a + data_b) / 2
    differences = data_a - data_b

    # Apply custom styling
    ps.color_style()

    # Create a scatter plot
    ax.scatter(mean, differences, s=0.4, alpha=0.2)

    lower_limit = np.percentile(differences, 5)
    upper_limit = np.percentile(differences, 95)

    ax.axhline(lower_limit, color='red', linestyle='--', label='5th Percentile Limit')
    ax.axhline(upper_limit, color='blue', linestyle='--', label='95th Percentile Limit')

    title_font = {'fontweight': 'bold', 'fontsize': 20}
    x_axis_font = {'fontweight': 'bold', 'fontsize': 14}
    y_axis_font = {'fontweight': 'bold', 'fontsize': 11}

    title = get_title(motion)
    ax.set_title(title, **title_font)
    ax.set_xlabel(x_label, **x_axis_font)
    ax.set_ylabel(y_label, **y_axis_font)
    
    print(f'\nMotion: {motion}')
    print(f"5th Percentile (Lower Limit): {round(lower_limit,3)}")
    print(f"95th Percentile (Upper Limit): {round(upper_limit,3)}")
    return


def get_title(motion: str) -> str:
    title_mappings = {
        "BicepC" : "Bicep Curl",
        "BodyLean" : "Body Lean",
        "ChestAA" : "Chest AA",
        "ShoulderAA" : "Shoulder AA",
        "ShoulderFE" : "Shoulder FE"
    }
    return title_mappings[motion]


def add_letter(ax, letter: str) -> None:
    letter_size = 24
    ax.text(-0.15, 1.1, letter,
            transform=ax.transAxes, size=letter_size,
            weight='bold', fontfamily='Arial')
    return


def create_plot(motions: List[str]):
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))

    for i, (motion, ax) in enumerate(zip(motions, axes.flatten())):
        x_label = "Average Angles (°)"
        y_label = "Difference (MP - MoCa)"
        subfigure_letter = chr(97 + i)
        add_subplot(ax, motion, x_label, y_label)
        add_letter(ax,  subfigure_letter)
    
    for j in range(len(motions), len(axes.flatten())):
        axes.flatten()[j].set_visible(False)

    plt.subplots_adjust(
        left=0.05, right=0.95, 
        top=0.95, bottom=0.1,
        wspace=0.3, hspace=0.5
    )
    
    plt.savefig(FILEPATH, dpi=300)
    plt.show()

    plt.close()
    return


def test_normality(motion: str) -> None:
    data_a, data_b = get_datapoints(motion)
    differences = data_a - data_b
    ic(len(differences))

    # Plot the distribution of differences
    plt.hist(differences, bins=30, density=True, alpha=0.6, color='g')

    # Plot the KDE using a normal distribution fit
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = stats.norm.pdf(x, np.mean(differences), np.std(differences))
    plt.plot(x, p, 'k', linewidth=2)

    plt.title('Distribution of Differences')
    plt.xlabel('Difference')
    plt.ylabel('Density')
    plt.show()

    # Perform and print results of normality test
    stat, p_value = stats.shapiro(differences)
    print(f"Shapiro-Wilk Test Statistic: {stat:.4f}, p-value: {p_value:.4e}")

    if p_value > 0.05:
        print("The differences are likely normally distributed (fail to reject null hypothesis).")
    else:
        print("The differences are not normally distributed (reject null hypothesis).")


def test_each_motion_normality():
    motions = get_motions()
    for motion in motions:
        ic(motion)
        test_normality(motion)


def get_motions() -> List[str]:
    return [
        "BicepC",
        "ChestAA",
        "ShoulderAA",
        "ShoulderFE",
        "BodyLean"
    ]


def main():
    motions = get_motions()
    create_plot(motions)
    return


if __name__ == "__main__":
    main()

