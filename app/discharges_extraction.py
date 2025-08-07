# ===== Load packages ====== #
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from app.config import VOLTAGE_THRESHOLD, TIME_STEP_MINUTES

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
    time_step_minutes: float = TIME_STEP_MINUTES
) -> List[Any]:
    """
    Post-process a single discharge: shift times, check voltage, trim end.
    Returns [start_shifted, end_shifted] or None if not valid.
    """
    current_drop_ratio = 0.2

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
    return [start_shifted.isoformat(), end_shifted.isoformat()]

def extract_all_discharges(
    bts_data: Dict[str, pd.DataFrame],
    voltage_threshold: float = VOLTAGE_THRESHOLD,
    time_step_minutes: float = TIME_STEP_MINUTES
) -> Dict:
    """
    Main extraction function for all BTS discharges.
    Returns a dictionary of bts_id -> list of [start, end] discharges.
    """

    all_BTS_discharges_dict = {}

    for bts_id, bts_considered in bts_data.items():
        if bts_considered.empty or 'timestamp' not in bts_considered.columns:
            continue

        # Convert 'timestamp' to native Python datetime (avoid pandas.Timestamp)
        bts_considered['timestamp'] = bts_considered['timestamp'].apply(lambda x: x.to_pydatetime())
        
        # Now set as index
        bts_considered.set_index('timestamp', inplace=True)
        BTS_Discharges = bts_discharges(bts_considered)
        if BTS_Discharges.size == 0:
            continue
        
        BTS_Discharges_Sorted = BTS_Discharges[BTS_Discharges[:, 2].astype(int).argsort()[::-1]]

        updated_discharges = []
        for discharge in BTS_Discharges_Sorted:
            result = process_discharge(
                bts_considered, discharge,
                voltage_threshold, 
                time_step_minutes
            )
            if result:
                updated_discharges.append(result)
        if updated_discharges:
            all_BTS_discharges_dict[bts_id] = updated_discharges

    return all_BTS_discharges_dict
