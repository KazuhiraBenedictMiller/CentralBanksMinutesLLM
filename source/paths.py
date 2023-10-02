from pathlib import Path
import os

PARENT_DIR = Path("__file__").parent.resolve().parent
DATA_DIR = PARENT_DIR / "data"
TRANSFORMED_DATA_DIR = DATA_DIR / "transformed"

if not Path(DATA_DIR).exists():
    os.mkdir(DATA_DIR)
    
if not Path(TRANSFORMED_DATA_DIR).exists():
    os.mkdir(TRANSFORMED_DATA_DIR)