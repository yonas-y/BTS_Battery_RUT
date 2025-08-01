from pathlib import Path
from pymongo import MongoClient

# MongoDB connection!
MONGO_URI = "mongodb://192.168.80.1:27017"
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)

# Paths!
operational_data_dir = Path("../../../Datasets/BTS/csv_files/operational_data/used_btss")
fault_alarm_data_dir = Path("../../../Datasets/BTS/csv_files/fault/")

# Important parameters!
sampling_time = 5 / 60  # Sampling time of the time series data!
