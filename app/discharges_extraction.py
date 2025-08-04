# ===== Load packages ====== #
import numpy as np
import pandas as pd
import pickle
import os
from app.config import client, output_dir

def bts_discharges(bts_dataframe):
    """
    Script to automatically annotate discharges!
    Returns a list of lists of the whole discharges (if any) from the data supplied!!!

    Script to annotate the discharges automatically!!!
    It returns the ranges where the battery current is being negative (Discharging)!!!

    Inputs:
        bts_dataframe : The dataframe of the bts data!!!

    Outputs:
        discharges_list : List of lists of discharge + length of each discharge
    """

    i_B = bts_dataframe['Battery Current(A)'].values
    i_AC = bts_dataframe['AC/DC System Output Current(A)'].values
    i_B_copy = i_B.copy()
    i_B_copy[i_B_copy > 0] = 1  # Positive if charging or stable with small drawn current.
    i_B_copy[i_B_copy < 0] = -1  # When in case of discharging!

    m = np.flatnonzero(np.diff(i_B_copy))  # Selects the entries where sign change is greater than zero!!!

    discharges_list = list()  # Finds negative values($[  )$) in the df!!
    for i in range(len(m) - 1):
        # Append only discharges which are longer than 30mins!
        if i_B[m[i] + 1] < 0 and i_AC[m[i] + 1] <= 5 and m[i + 1] - m[i] > 6:
            discharges_list.append([bts_dataframe.index[m[i] + 1], bts_dataframe.index[m[i + 1] + 1], m[i + 1] - m[i]])

    return np.array(discharges_list)

# ====== Connect to MongoDB and import data from a selected BTS! ====== #
db = client["BTS_Dataset"]
collection = db["bts_oper_data_soc"]
unique_bts_ids = collection.distinct("bts_id")

# ===== Select all usable discharges from the different BTSs ======= #
"""
The selection criteria are:
    1. Discharges which are reach below some threshold value (46.2V)!
    2. In some cases the battery current remains negative after the load is disconnected!
        In such situations remove those values!!
    3. Store all the discharges starting and ending index in a list!!!!

"""
all_BTS_discharges_dict = {}

# Process each bts_id!
for bts_id in unique_bts_ids:
    bts_considered = pd.DataFrame(list(collection.find({"bts_id": bts_id})))
    bts_considered.set_index('timestamp', inplace=True)

    BTS_Discharges = bts_discharges(bts_considered)
    BTS_Discharges_Sorted = BTS_Discharges[BTS_Discharges[:, 2].astype(int).argsort()[::-1]]

    updated_discharges = []
    for key in BTS_Discharges_Sorted:
        # Shift times
        step = pd.Timedelta(minutes=5)
        start_shifted = key[0] + step
        end_shifted = key[1] - step

        if min(bts_considered.loc[start_shifted:end_shifted]['Battery Voltage(V)']) < 46.2:

            # Create list of timestamps from start to end with 5-minute intervals
            time_range = pd.date_range(start=start_shifted, end=end_shifted, freq=step)

            for t in time_range:
                # If the battery load observed while discharging is less than 20% of what is seen
                # a step before, that is the battery discharge end!
                # This is to leave out entries after the battery is empty!!!
                if (abs(bts_considered.loc[t]['Battery Current(A)']) <
                        abs(0.2 * bts_considered.loc[t-step]['Battery Current(A)'])):
                    end_shifted = t
                    break
            updated_discharges.append([start_shifted, end_shifted])

    if updated_discharges:
        # Checks if the list is not empty!
        all_BTS_discharges_dict[bts_id] = updated_discharges

# Store the bts discharges!
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'all_BTS_discharges_dict.pkl')

with open(output_path, 'wb') as handle:
    pickle.dump(all_BTS_discharges_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
