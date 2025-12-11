# contest_tools/data_aggregators/matrix_stats.py
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from ..contest_log import ContestLog
from ..reports._report_utils import get_valid_dataframe

class MatrixAggregator:
    """
    Aggregates log data into 2D matrices (Band x Time) for heatmaps and timelines.
    Returns Pure Python primitives (no Pandas objects in return values) to ensure
    decoupling between data logic and presentation layers.
    """
    def __init__(self, logs: List[ContestLog]):
        self.logs = logs

    def _determine_activity_status(self, series: pd.Series) -> str:
        """
        Determines the dominant activity type for a time bin.
        Returns: 'Run', 'S&P', 'Mixed', or 'Inactive'.
        """
        if series.empty:
            return 'Inactive'
        
        statuses = set(series.unique())
        is_run = 'Run' in statuses
        is_sp = 'S&P' in statuses
        
        if is_run and not is_sp:
            return 'Run'
        elif is_sp and not is_run:
            return 'S&P'
        else:
            return 'Mixed'

    def get_matrix_data(self, bin_size: str = '15min', mode_filter: Optional[str] = None, time_index: pd.DatetimeIndex = None) -> Dict[str, Any]:
        """
        Generates aligned 2D grids for all logs.
        Args:
            bin_size: Pandas frequency string (default '15min').
            mode_filter: Optional mode string (e.g., 'CW', 'PH') to filter data.
            time_index: Optional pre-calculated DatetimeIndex to force alignment.
        Returns:
        {
            "time_bins": [iso_str, ...], # X-Axis
            "bands": [band_str, ...],    # Y-Axis (Sorted)
            "logs": {
                "CALLSIGN": {
                    "qso_counts": [[row_band_1], [row_band_2]...], # List[List[int]]
                    "activity_status": [[row_band_1], [row_band_2]...] # List[List[str]]
                }
            }
        }
        """
        # --- 1. Establish Global Dimensions ---
        all_dfs = []
        all_bands = set()
        
        for log in self.logs:
            df = get_valid_dataframe(log, include_dupes=False)
            if not df.empty:
                if mode_filter:
                    df = df[df['Mode'] == mode_filter]
                
                if not df.empty:
                    all_dfs.append(df)
                    all_bands.update(df['Band'].unique())

        if not all_dfs:
            return {"time_bins": [], "bands": [], "logs": {}}

        # Global Time Range
        if time_index is None:
            full_concat = pd.concat(all_dfs)
            min_time = full_concat['Datetime'].min().floor('h')
            max_time = full_concat['Datetime'].max().ceil('h')
            time_index = pd.date_range(start=min_time, end=max_time, freq=bin_size, tz='UTC')
        
        # Global Band Order
        canonical_band_order = [b[1] for b in ContestLog._HAM_BANDS]
        sorted_bands = sorted(list(all_bands), key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)

        result = {
            "time_bins": [t.isoformat() for t in time_index],
            "bands": sorted_bands,
            "logs": {}
        }

        # --- 2. Populate Data Per Log ---
        for log in self.logs:
            call = log.get_metadata().get('MyCall', 'Unknown')
            df = get_valid_dataframe(log, include_dupes=False)
            
            # Apply filter locally
            if mode_filter and not df.empty:
                df = df[df['Mode'] == mode_filter]

            log_data = {
                "qso_counts": [],
                "activity_status": []
            }

            if df.empty:
                # Fill with zeros/inactive if log is empty for this mode/slice
                zeros = [0] * len(time_index)
                inactive = ['Inactive'] * len(time_index)
                for _ in sorted_bands:
                    log_data["qso_counts"].append(zeros)
                    log_data["activity_status"].append(inactive)
            else:
                # A. Pivot for QSO Counts
                # We reindex to ensure every band and time bin is present
                pivot_counts = df.pivot_table(
                    index='Band', 
                    columns=pd.Grouper(key='Datetime', freq=bin_size), 
                    aggfunc='size', 
                    fill_value=0
                ).reindex(index=sorted_bands, columns=time_index, fill_value=0)

                # B. Group for Activity Status
                # We calculate status per band-row
                status_grid = []
                for band in sorted_bands:
                    df_band = df[df['Band'] == band]
                    if df_band.empty:
                        status_row = ['Inactive'] * len(time_index)
                    else:
                        # Group by 15min bin and apply logic
                        resampled = df_band.set_index('Datetime').groupby(pd.Grouper(freq=bin_size))['Run'].apply(self._determine_activity_status)
                        # Reindex to full time range
                        resampled = resampled.reindex(time_index, fill_value='Inactive')
                        status_row = resampled.tolist()
                    status_grid.append(status_row)

                # Convert Numpy/Pandas structures to Pure Python Lists
                # astype(int) ensures we don't return numpy.int64
                log_data["qso_counts"] = pivot_counts.fillna(0).astype(int).values.tolist()
                log_data["activity_status"] = status_grid

            result["logs"][call] = log_data

        return result

    def get_stacked_matrix_data(self, bin_size: str = '60min', mode_filter: Optional[str] = None, time_index: pd.DatetimeIndex = None) -> Dict[str, Any]:
        """
        Generates 3D data (Band x Time x RunStatus) for stacked charts.
        Args:
            bin_size: Pandas frequency string.
            mode_filter: Optional filter.
            time_index: Optional pre-calculated DatetimeIndex to force alignment.
        Returns:
        {
            "time_bins": [iso_str, ...],
            "bands": [band_str, ...],
            "logs": {
                "CALLSIGN": {
                    "BAND_NAME": {
                        "Run": [int, ...],
                        "S&P": [int, ...],
                        "Unknown": [int, ...]
                    }
                }
            }
        }
        """
        # --- 1. Establish Global Dimensions ---
        all_dfs = []
        all_bands = set()
        
        for log in self.logs:
            df = get_valid_dataframe(log, include_dupes=False)
            if not df.empty:
                if mode_filter:
                    df = df[df['Mode'] == mode_filter]
                
                if not df.empty:
                    all_dfs.append(df)
                    all_bands.update(df['Band'].unique())

        if not all_dfs:
            return {"time_bins": [], "bands": [], "logs": {}}

        # Global Time Range
        if time_index is None:
            full_concat = pd.concat(all_dfs)
            min_time = full_concat['Datetime'].min().floor('h')
            max_time = full_concat['Datetime'].max().ceil('h')
            time_index = pd.date_range(start=min_time, end=max_time, freq=bin_size, tz='UTC')
        
        # Global Band Order
        canonical_band_order = [b[1] for b in ContestLog._HAM_BANDS]
        sorted_bands = sorted(list(all_bands), key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)

        result = {
            "time_bins": [t.isoformat() for t in time_index],
            "bands": sorted_bands,
            "logs": {}
        }

        # --- 2. Populate Data Per Log ---
        for log in self.logs:
            call = log.get_metadata().get('MyCall', 'Unknown')
            df = get_valid_dataframe(log, include_dupes=False)
            
            # Apply filter locally
            if mode_filter and not df.empty:
                df = df[df['Mode'] == mode_filter]

            result["logs"][call] = {}

            if df.empty:
                # Initialize empty structure for all bands
                zeros = [0] * len(time_index)
                for band in sorted_bands:
                    result["logs"][call][band] = {
                        "Run": list(zeros),
                        "S&P": list(zeros),
                        "Unknown": list(zeros)
                    }
                continue

            # Standardize Run Status for grouping
            # If 'Run' column exists, map NaNs to 'Unknown'.
            # If it doesn't exist, treat all as 'Unknown'.
            if 'Run' in df.columns:
                df = df.copy()
                df['RunStatus'] = df['Run'].fillna('Unknown')
                # Ensure values are strictly mapped to our 3 keys if needed, 
                # but 'Run'/'S&P' are standard. Any deviation becomes 'Unknown'.
                known_statuses = {'Run', 'S&P'}
                df.loc[~df['RunStatus'].isin(known_statuses), 'RunStatus'] = 'Unknown'
            else:
                df = df.copy()
                df['RunStatus'] = 'Unknown'

            # Pivot: Index=[Band, RunStatus], Columns=Time
            pivot = df.pivot_table(
                index=['Band', 'RunStatus'],
                columns=pd.Grouper(key='Datetime', freq=bin_size),
                aggfunc='size',
                fill_value=0
            )

            # Iterate through bands to build the nested structure
            for band in sorted_bands:
                band_data = {
                    "Run": [],
                    "S&P": [],
                    "Unknown": []
                }
                
                for status in ["Run", "S&P", "Unknown"]:
                    if (band, status) in pivot.index:
                        # Extract the row, reindex to master time index to ensure alignment
                        row = pivot.loc[(band, status)]
                        row = row.reindex(time_index, fill_value=0)
                        band_data[status] = row.astype(int).tolist()
                    else:
                        band_data[status] = [0] * len(time_index)
                
                result["logs"][call][band] = band_data

        return result