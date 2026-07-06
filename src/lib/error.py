import os
import  pandas as pd


class Error(Exception):
    pass


def check_column(df: pd.DataFrame, column: str) -> None:
    if column not in df:
        raise Error(f"Column '{column}' is missing from the DataFrame.")

    if df[column].isna().all():
        raise Error(f"Column '{column}' is present but contains only NaN values.")
    

def handle_file_error(file, error, DEBUG=False):
    base = os.path.basename(file)
    if DEBUG:
        raise Error(f"Error with file {base}; {error}")
    print(f"Skipping {base}")