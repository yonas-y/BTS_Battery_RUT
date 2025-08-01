import os
import pandas as pd
import numpy as np
from pymongo import errors
from tqdm import tqdm
from app.config import sampling_time
from app.config import client

# Connect to the database!
db = client["BTS_Dataset"]

### 1. Upload BTS operational Data!
operational_data_collection = db["bts_oper_data_original"]
operational_data_collection_soc = db["bts_oper_data_soc"]  # store processed results

# Get unique values of 'bts_id'
unique_bts_ids = operational_data_collection.distinct("bts_id")

# Function to fill NaNs using previous day's same time value
def fill_from_previous_day(df):
    for idx in df[df.isnull().any(axis=1)].index:
        prev_day_idx = idx - pd.Timedelta(days=1)
        if prev_day_idx in df.index:
            df.loc[idx] = df.loc[prev_day_idx]
    return df

# Process each bts_id!
for bts_id in tqdm(unique_bts_ids, desc="Processing BTS IDs"):
    df = pd.DataFrame(list(operational_data_collection.find({"bts_id": bts_id})))
    if df.empty or "timestamp" not in df.columns:
        continue

    # Ensure 'timestamp' is datetime and drop NaT
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.drop(columns=['_id'], errors='ignore')
    df = df.sort_values('timestamp').set_index('timestamp')

    # Resample to 5-minute intervals (will introduce NaNs)
    df_resampled = df.resample('5min').asfreq()

    # Apply the filling logic
    df_filled = fill_from_previous_day(df_resampled)

    # Forward fill remaining NaNs (if any)
    df_filled = df_filled.ffill()

    # Reset index if needed
    df_filled = df_filled.reset_index()

    BC = df_filled['Battery Current(A)'].values
    AC = df_filled['AC/DC System Output Current(A)'].values

    Q = np.zeros(len(df_filled))
    for m in range(1, len(BC)):
        if (5 > BC[m] > -5 and AC[m] > 10) or (Q[m] < 0):
            """
            If the AC is ON and the battery is not charging, then we deduce it's Full.
            If the battery charge becomes negative, them put it to zero since it is not possible!
            Q = 0, Full battery status!
            """
            Q[m] = 0
        else:
            """
            It is charging or discharging.
            """
            Q[m] = Q[m - 1] + sampling_time * BC[m] * -1

    df_filled['SoC'] = Q

    # Convert to records for MongoDB
    records = df_filled.to_dict(orient='records')

    # Insert processed records
    operational_data_collection_soc.insert_many(records)

    print(f"⏱️ SoC calculated and loaded for : {bts_id}")
