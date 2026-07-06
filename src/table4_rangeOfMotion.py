import os
from typing import Dict
import src.lib.directory as dir
import src.lib.globals as globals
import pandas as pd
import src.lib.processing as proc


def get_expected_rom(filename: str) -> float:
    base = os.path.basename(filename)
    split = base.split('.')
    motion = split[0].lower()

    ROM_MAPPINGS = {
        'bicepc' : 110,     
        'bodylean' : 35,    
        'chestaa' : 110,    
        'shoulderaa' : 140, 
        'shoulderfe' : 170  
    }
    expected_rom = ROM_MAPPINGS[motion]
    return expected_rom


def get_motion(filename: str) -> str:
    base = os.path.basename(filename)
    split = base.split('.')
    motion = split[0]
    return motion

def get_speed(filename: str) -> str:
    base = os.path.basename(filename)
    split = base.split('.')
    all_speed = split[3]
    speed = all_speed[2:].lower()
    return speed


def evaluate_rom(filename: str, df: pd.DataFrame, col_name: str) -> Dict:
    data = df[col_name]
    rom = proc.calc_rom(data)
    expected_rom = get_expected_rom(filename)
    modality = 'moca' if 'moca' in col_name.lower() else 'mp'
    speed = get_speed(filename)
    row = {
        'file' : os.path.basename(filename),
        'mode' : modality,
        'motion' : get_motion(filename),
        'speed' : speed,
        'successful_rom' : (rom <= (expected_rom * 1.3)) & (rom >= (expected_rom / 1.3)),
        'actual_rom' : rom
    }
    return row


def create_df() -> pd.DataFrame:
    temp_lst = []
    
    files = dir.get_files(globals.ALIGNED_DATA)
    for file in files:
        df = dir.file_to_df(file)
        moca_row = evaluate_rom(file, df, 'moca_angles')
        mp_row = evaluate_rom(file, df, 'mp_angles')

        temp_lst.append(moca_row)
        temp_lst.append(mp_row)

    out_df = pd.DataFrame(temp_lst)
    return out_df


def main():
    aggregate_df = create_df()
    grouped = aggregate_df.groupby(['mode', 'motion'])
    
    grouped = aggregate_df.groupby(['mode', 'motion'])['successful_rom'].sum()
    AGG_OUTPATH = os.path.join(globals.AGGREGATE, 'rom_eval_aggregate.csv')
    aggregate_df.to_csv(AGG_OUTPATH)
    print(grouped) 
    
    # Group by 'mode' and 'motion', then sum the True counts in 'successful_rom'
    grouped = aggregate_df.groupby(['mode', 'motion', 'speed'])['successful_rom'].sum()
    
    AGG_OUTPATH = os.path.join(globals.AGGREGATE, 'rom_eval_aggregate.csv')
    aggregate_df.to_csv(AGG_OUTPATH)
    print(grouped) 
    
    return


if __name__ == "__main__":
    main()
