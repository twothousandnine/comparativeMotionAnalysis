import src.lib.directory as dir
import src.lib.globals as globals
import pandas as pd


def calculate_roughness(series: pd.Series, window_size: int = 5) -> pd.Series:
    if not isinstance(series, pd.Series):
        raise TypeError("Input must be a pandas Series.")
    
    # Calculate the first derivative
    first_derivative = series.diff()
    
    # Compute rolling variance (roughness) of the first derivative
    roughness_series = first_derivative.rolling(window=window_size, min_periods=2).var()
    
    return roughness_series


def process_file(filename: str):
    df = dir.file_to_df(filename)
    angles = df['angles']
    
    # Calculate per-row roughness
    df['roughness'] = calculate_roughness(angles)
    
    df.to_csv(filename, index=False)
    return


def process_all_files():
    INPUT_DIR = globals.RAW_DATA
    all_files = dir.search(directory=INPUT_DIR)

    for file in all_files:
        process_file(file)
    
    return


def main():
    return


if __name__ == "__main__":
    process_all_files()
