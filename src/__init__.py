import warnings
from pathlib import Path

import pandas as pd
from sqlalchemy.exc import SAWarning

# suppress SQLAlchemy warnings, stemming from incorrect index configuration in the fizDB
warnings.filterwarnings(action="ignore", category=SAWarning)

# set src.PATH to be root directory
PATH = Path(__file__).parent.parent

# set better-to-read pandas options
pd.set_option("display.max_colwidth", 128)
pd.set_option("display.max_rows", 128)
