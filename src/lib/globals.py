import os

_file_path = os.path.abspath(__file__)
_parent_dir = os.path.dirname(_file_path)
src_dir = os.path.dirname(_parent_dir) 
CODE_DIR = os.path.dirname(src_dir)

RAW_DATA = os.path.join(CODE_DIR, 'data', 'raw')
ALIGNED_DATA = os.path.join(CODE_DIR, 'data', 'aligned')
AGGREGATE = os.path.join(CODE_DIR, 'data', 'aggregate')
FIGURES = os.path.join(CODE_DIR, "figures")

ANGLE_GRAPHS = FIGURES
CORR_GRAPHS = FIGURES
