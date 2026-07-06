import  os
import  matplotlib.pyplot as plt



BW = "bw"
COLOR = "color"
DEBUG = "debug"


def load_style(style: str) -> None:
    current_dir = os.path.dirname(__file__)
    style_path = os.path.join(current_dir, 'styles', f'{style}.mplstyle')

    plt.style.use(style_path)    


def color_style():
    load_style(COLOR)

