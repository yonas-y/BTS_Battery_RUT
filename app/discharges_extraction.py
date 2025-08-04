# ===== Load packages ====== #
import numpy as np
import pandas as pd
import pickle
import os
from app.config import client

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

    b = bts_dataframe['Battery Current(A)'].values
    a = bts_dataframe['AC/DC System Output Current(A)'].values
    u = b.copy()
    u[u > 0] = 1  # Positive if charging or stable with small drawn current.
    u[u < 0] = -1  # When in case of discharging!

    m = np.flatnonzero(np.diff(u))  # Selects the entries where sign change is greater than zero!!!

    discharges_list = list()  # Finds negative values($[  )$) in the df!!
    for i in range(len(m) - 1):
        # Append only discharges which are longer than 30mins!
        if b[m[i] + 1] < 0 and a[m[i] + 1] <= 5 and m[i + 1] - m[i] > 6:
            discharges_list.append([m[i] + 1, m[i + 1] + 1, m[i + 1] - m[i]])

    return np.array(discharges_list)

# ====== Connect to MongoDB and import data from a selected BTS! ====== #
db = client["BTS_Dataset"]
collection = db["bts_oper_data_soc"]
unique_bts_ids = collection.distinct("bts_id")

