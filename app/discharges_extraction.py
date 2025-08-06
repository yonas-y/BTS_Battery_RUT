# ===== Load packages ====== #
import numpy as np
import pandas as pd
import pickle
import os
from typing import Dict, List, Any

# Configurable parameters
VOLTAGE_THRESHOLD = 46.2
CURRENT_DROP_RATIO = 0.2
TIME_STEP_MINUTES = 5

def bts_discharges(bts_dataframe: pd.DataFrame) -> np.ndarray:
    """
    Automatically annotate discharges in BTS dataframe.
    Returns a list of [start, end, length] for each discharge.
    """
    i_B = bts_dataframe['Battery Current(A)'].values
    i_AC = bts_dataframe['AC/DC System Output Current(A)'].values
    i_B_copy = i_B.copy()
    i_B_copy[i_B_copy > 0] = 1
    i_B_copy[i_B_copy < 0] = -1

    m = np.flatnonzero(np.diff(i_B_copy))
    discharges_list = []
    for i in range(len(m) - 1):
        # Append only discharges which are longer than 30mins!
        if i_B[m[i] + 1] < 0 and i_AC[m[i] + 1] <= 5 and m[i + 1] - m[i] > 6:
            discharges_list.append([
                bts_dataframe.index[m[i] + 1],
                bts_dataframe.index[m[i + 1] + 1],
                m[i + 1] - m[i]
            ])
    return np.array(discharges_list)

def process_discharge(
    bts_considered: pd.DataFrame,
    discharge: np.ndarray,
    voltage_threshold: float = VOLTAGE_THRESHOLD,
    current_drop_ratio: float = CURRENT_DROP_RATIO,
    time_step_minutes: int = TIME_STEP_MINUTES
) -> List[Any]:
    """
    Post-process a single discharge: shift times, check voltage, trim end.
    Returns [start_shifted, end_shifted] or None if not valid.
    """
    step = pd.Timedelta(minutes=time_step_minutes)
    start_shifted = discharge[0] + step
    end_shifted = discharge[1] - step

    voltage_series = bts_considered.loc[start_shifted:end_shifted]['Battery Voltage(V)']
    if voltage_series.empty or voltage_series.min() >= voltage_threshold:
        return None

    time_range = pd.date_range(start=start_shifted, end=end_shifted, freq=step)
    for t in time_range:
        try:
            curr = abs(bts_considered.loc[t]['Battery Current(A)'])
            prev = abs(bts_considered.loc[t-step]['Battery Current(A)'])
            if curr < current_drop_ratio * prev:
                end_shifted = t
                break
        except KeyError:
            continue
    return [start_shifted, end_shifted]

def extract_all_discharges(
    client,
    output_dir: str,
    voltage_threshold: float = VOLTAGE_THRESHOLD,
    current_drop_ratio: float = CURRENT_DROP_RATIO,
    time_step_minutes: int = TIME_STEP_MINUTES
) -> Dict[str, List[List[Any]]]:
    """
    Main extraction function for all BTS discharges.
    Returns a dictionary of bts_id -> list of [start, end] discharges.
    """
    db = client["BTS_Dataset"]
    collection = db["bts_oper_data_soc"]
    unique_bts_ids = collection.distinct("bts_id")
    all_BTS_discharges_dict = {}

    for bts_id in unique_bts_ids:
        bts_considered = pd.DataFrame(list(collection.find({"bts_id": bts_id})))
        if bts_considered.empty or 'timestamp' not in bts_considered.columns:
            continue
        bts_considered.set_index('timestamp', inplace=True)
        BTS_Discharges = bts_discharges(bts_considered)
        if BTS_Discharges.size == 0:
            continue
        BTS_Discharges_Sorted = BTS_Discharges[BTS_Discharges[:, 2].astype(int).argsort()[::-1]]

        updated_discharges = []
        for discharge in BTS_Discharges_Sorted:
            result = process_discharge(
                bts_considered, discharge,
                voltage_threshold, current_drop_ratio, time_step_minutes
            )
            if result:
                updated_discharges.append(result)
        if updated_discharges:
            all_BTS_discharges_dict[bts_id] = updated_discharges

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'all_BTS_discharges_dict.pkl')
    with open(output_path, 'wb') as handle:
        pickle.dump(all_BTS_discharges_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return all_BTS_discharges_dict
