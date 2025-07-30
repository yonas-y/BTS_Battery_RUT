import os
import pandas as pd
from pymongo import errors
from app.config import operational_data_dir
from app.config import client

# Connect to the database!
db = client["BTS_Dataset"]

### 1. Upload BTS operational Data!
operational_data_collection = db["bts_operational_data"]

# 🔐 Ensure unique index on timestamp + bts_id
operational_data_collection.create_index(
    [("timestamp", 1), ("bts_id", 1)],
    unique=True,
    name="unique_timestamp_bts_id"
)

# 📥 Load and insert data with deduplication
for file in os.listdir(operational_data_dir):
    if file.endswith(".csv"):
        bts_id = file.split(".")[0]  # btsA.csv -> btsA
        df = pd.read_csv(os.path.join(operational_data_dir, file), index_col=0, parse_dates=True)

        df["bts_id"] = bts_id

        # Include index as a column
        df_reset = df.reset_index()
        df_reset.rename(columns={'index': 'timestamp'}, inplace=True)

        records = df_reset.to_dict(orient="records")

        inserted, skipped = 0, 0
        for record in records:
            try:
                operational_data_collection.insert_one(record)
                inserted += 1
            except errors.DuplicateKeyError:
                skipped += 1

        print(f"✅ Processed {file} — Inserted: {inserted}, Skipped: {skipped} (duplicates)")
