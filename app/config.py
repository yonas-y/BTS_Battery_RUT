from pathlib import Path
from pymongo import MongoClient

# MongoDB connection!
# MONGO_URI = "mongodb://192.168.80.1:27017"
MONGO_URI = "mongodb://host.docker.internal:27017"
DATABASE_NAME = "BTS_Dataset"
COLLECTION_NAME = "bts_oper_data_soc"
UNIQUE_ID = "bts_id"

# Create a MongoDB client
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)

# Paths!
operational_data_dir = Path("../../../Datasets/BTS/csv_files/operational_data/used_btss")
fault_alarm_data_dir = Path("../../../Datasets/BTS/csv_files/fault/")
OUTPUT_DIR = Path("outputs/")

# Configurable parameters
sampling_time = 5 / 60  # Sampling time of the time series data!

VOLTAGE_THRESHOLD = 46.2    # Considered fault below this voltage!
TIME_STEP_MINUTES = 5       # Time step for processing discharges in minutes!


# Selected BTSs to work on and their full sample positions.
full_stamp_sample = {
    'bts111127': 5000, 'bts111171': 5000, 'bts111172': 0, 'bts111180': 3800,
    'bts111191': 0, 'bts111210': 2400, 'bts111217': 5000, 'bts111218': 0,
    'bts111220': 13000, 'bts111222': 2300, 'bts111428': 31000, 'bts111429': 30500
}
