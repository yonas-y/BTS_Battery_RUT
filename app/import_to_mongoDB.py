import os
import pandas as pd
from pymongo import errors
from tqdm import tqdm
from app.config import operational_data_dir
from app.config import client

# Connect to the database!
db = client["BTS_Dataset"]

### 1. Upload BTS operational Data!
operational_data_collection = db["bts_operational_data"]

# Ensure unique index on timestamp + bts_id!
try:
    operational_data_collection.create_index(
        [("timestamp", 1), ("bts_id", 1)],
        unique=True,
        name="unique_timestamp_bts_id"
    )
except errors.OperationFailure as e:
    print(f"Index creation failed: {e}")

# List all .csv files
csv_files = [f for f in os.listdir(operational_data_dir) if f.endswith(".csv")]

# 📥 Load and insert data with deduplication and tqdm progress bar!
for file in tqdm(csv_files, desc="Uploading CSV files", unit="file"):
    if file.endswith(".csv"):
        bts_id = file.split(".")[0]  # btsA.csv -> btsA
        df = pd.read_csv(os.path.join(operational_data_dir, file), index_col=0, parse_dates=True)

        df["bts_id"] = bts_id

        # Include index as a column!
        df_reset = df.reset_index()

        # Rename the time column to 'timestamp' (whether named or not)
        if "index" in df_reset.columns:
            df_reset.rename(columns={"index": "timestamp"}, inplace=True)
        elif "Start Time" in df_reset.columns:
            df_reset.rename(columns={"Start Time": "timestamp"}, inplace=True)

        records = df_reset.to_dict(orient="records")

        # for record in records[:5]:  # just show a few
        #     print(record["timestamp"], record["bts_id"])

        try:
            operational_data_collection.insert_many(
                records,
                ordered=False  # continue on duplicate key errors
            )
            print(f"✅ Inserted all records from {file}")
        except errors.BulkWriteError as bwe:
            inserted_count = len([w for w in bwe.details["writeErrors"] if w["code"] != 11000])
            skipped_count = len([w for w in bwe.details["writeErrors"] if w["code"] == 11000])
            print(f"⚠️ Bulk write warning on {file} — Inserted: {inserted_count}, Skipped: {skipped_count} duplicates")
