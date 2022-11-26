import api_requests
import pandas as pd

from models import ConfigModel
from pathlib import Path

# Paths
DATA_PATH = Path(__file__).parent.parent / 'data'
MAPPING_PATH = DATA_PATH / 'mapping.csv'
VOLUME_PATH = DATA_PATH / 'volumes.csv'
CONTENT_PATH = DATA_PATH / 'content'


# Config file
_config = ConfigModel.parse_file(DATA_PATH / 'config.json')

# API
api = _config.api

# Download data
if not VOLUME_PATH.exists():
    api_requests.refresh_volume()

if not MAPPING_PATH.exists():
    api_requests.refresh_mapping()

# Load data
VOLUME = pd.read_csv(DATA_PATH / 'volumes.csv')
ITEM_MAPPING = pd.read_csv(DATA_PATH / 'mapping.csv')


# Additional configuration data
def __getattr__(name: str):
    return _config.__getattribute__(name)