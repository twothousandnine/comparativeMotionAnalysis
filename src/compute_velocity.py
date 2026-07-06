import src.lib.globals as globals
import src.lib.directory as directory
import logging
import pandas as pd 


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FRAME_RATE = 60

def add_velocity_all_files():
    """
    Adds a 'velocity' column to all data files in the RAW_DATA directory.
    The velocity is calculated as the difference in 'angles' multiplied by FRAME_RATE.
    Rows with empty 'angles' remain unaffected.
    """
    INPUT_DIR = globals.RAW_DATA
    try:
        all_files = directory.search(directory=INPUT_DIR)
        logging.info(f"Found {len(all_files)} files in {INPUT_DIR}")
    except Exception as e:
        logging.error(f"Error searching directory {INPUT_DIR}: {e}")
        return

    for file in all_files:
        try:
            df = directory.file_to_df(file)
            
            if 'angles' not in df.columns:
                logging.warning(f"'angles' column not found in {file}. Skipping.")
                continue
            
            df['angles'] = pd.to_numeric(df['angles'], errors='coerce')
            df['velocity'] = df['angles'].diff() * FRAME_RATE
            df.loc[df['angles'].isna(), 'velocity'] = pd.NA
            num_angles_nan = df['angles'].isna().sum()
            num_velocity_nan = df['velocity'].isna().sum()
            if num_velocity_nan < num_angles_nan:
                logging.warning(f"Some 'velocity' NaNs are missing in {file}")

            directory.df_to_file(df, file)
            logging.info(f"Processed and updated {file}")
        except Exception as e:
            logging.error(f"Error processing file {file}: {e}")

def main():
    add_velocity_all_files()

if __name__ == "__main__":
    main()
