# contest_tools/data_aggregators/time_series.py
#
# Purpose: Aggregates time-series data from contest logs into a standardized
#          JSON-compatible structure (Pure Python Primitives).
#
# Author: Gemini AI
# Date: 2025-12-06
# Version: 1.4.0
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.
# If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# --- Revision History ---
# [1.4.0] - 2025-12-06
# - Updated get_time_series_data to populate 'by_mode' and 'by_band_mode'.
# - Improved groupby logic to handle multi-level aggregation.
# [1.3.1] - 2025-11-24
# - Implemented run_points and sp_unk_points logic.
# - Added band_filter and mode_filter arguments to get_time_series_data.
# - Enforced strict separation: Points are raw sums, Score is from calculator.
# [1.2.0] - 2025-11-24
# - Initial creation implementing the TimeSeriesData v1.2 schema.
import pandas as pd
import numpy as np
from typing import List, Dict, Any

class TimeSeriesAggregator:
    """
    Aggregates log data into a unified time-series structure.
    Returns pure Python primitives (dict, list, int, str) suitable for JSON serialization.
    """
    def __init__(self, logs: List[Any]):
        self.logs = logs

    def get_time_series_data(self, band_filter: str = None, mode_filter: str = None) -> Dict[str, Any]:
        """
        Generates the TimeSeriesData v1.4.0 structure.
        
        Args:
            band_filter: Optional band string (e.g., '20M').
            mode_filter: Optional mode string (e.g., 'CW').
        """
        data = {
            "time_bins": [],
            "logs": {}
        }
        
        if not self.logs:
            return data

        # 1. Establish Master Index
        # Prefer the LogManager's master index if available to ensure alignment
        if hasattr(self.logs[0], '_log_manager_ref') and self.logs[0]._log_manager_ref:
             master_index = self.logs[0]._log_manager_ref.master_time_index
        else:
             # Fallback: Union of all times in all logs
             all_times = pd.concat([log.get_processed_data()['Datetime'] for log in self.logs])
             master_index = all_times.dt.floor('h').dropna().unique().sort_values()

        # Convert to ISO strings for JSON compatibility
        data["time_bins"] = [t.isoformat() for t in master_index]

        # 2. Iterate Logs
        for log in self.logs:
            metadata = log.get_metadata()
            callsign = metadata.get('MyCall', 'UnknownCall')
            contest_def = log.contest_definition
            
            # --- Prepare Data ---
            df_full = log.get_processed_data()
            
            # Apply Filters (Schema v1.3.1)
            if band_filter and band_filter != 'All':
                df_full = df_full[df_full['Band'] == band_filter]
            if mode_filter:
                df_full = df_full[df_full['Mode'] == mode_filter]

            # --- Scalars ---
            if df_full.empty:
                gross_qsos = 0
                dupes = 0
                net_qsos = 0
                points_sum = 0
                year = "UnknownYear"
            else:
                gross_qsos = len(df_full)
                dupes = df_full['Dupe'].sum() if 'Dupe' in df_full.columns else 0
                net_qsos = gross_qsos - dupes
                # Raw Points Sum (Dynamic Calculation)
                points_sum = df_full['QSOPoints'].sum() if 'QSOPoints' in df_full.columns else 0
                
                # Extract Year
                date_series = df_full['Date'].dropna()
                year = date_series.iloc[0].split('-')[0] if not date_series.empty else "UnknownYear"

            on_time = metadata.get('OnTime', "") 
            contest_name = metadata.get('ContestName', 'UnknownContest')

            log_entry = {
                "scalars": {
                    "gross_qsos": int(gross_qsos),
                    "net_qsos": int(net_qsos),
                    "dupes": int(dupes),
                    "points_sum": int(points_sum),
                    "on_time": str(on_time),
                    "contest_name": str(contest_name),
                    "year": str(year)
                },
                "cumulative": {
                    "qsos": [], "points": [], "mults": [], 
                    "score": [], "run_qsos": [], "sp_unk_qsos": [],
                    "run_points": [], "sp_unk_points": []
                },
                "hourly": { 
                    "qsos": [], 
                    "by_band": {},
                    "by_mode": {},
                    "by_band_mode": {}
                }
            }

            # --- Cumulative Data (Schema v1.3.1) ---
            
            # Helper to process time series
            def process_series(s):
                # Align to master index, fill gaps forward (cumulative), fill initial NaNs with 0
                return s.cumsum().reindex(master_index).ffill().fillna(0).astype(int).tolist()

            zeros = [0] * len(master_index)

            if not df_full.empty:
                df_valid = df_full[df_full['Dupe'] == False].copy()
                
                if not df_valid.empty:
                    # Resample Setup
                    hourly_grp = df_valid.set_index('Datetime').resample('h')
                    
                    # 1. Total QSOs
                    s_qsos = hourly_grp.size()
                    log_entry["cumulative"]["qsos"] = process_series(s_qsos)

                    # 2. Total Points (Raw Sum)
                    s_points = hourly_grp['QSOPoints'].sum()
                    log_entry["cumulative"]["points"] = process_series(s_points)

                    # 3. Run/S&P Splits
                    run_mask = df_valid['Run'] == 'Run'
                    
                    # Split Dataframes
                    df_run = df_valid[run_mask]
                    df_sp = df_valid[~run_mask]

                    # Run QSOs / Points
                    if not df_run.empty:
                         run_grp = df_run.set_index('Datetime').resample('h')
                         log_entry["cumulative"]["run_qsos"] = process_series(run_grp.size())
                         log_entry["cumulative"]["run_points"] = process_series(run_grp['QSOPoints'].sum())
                    else:
                        log_entry["cumulative"]["run_qsos"] = zeros
                        log_entry["cumulative"]["run_points"] = zeros
                    
                    # S&P QSOs / Points
                    if not df_sp.empty:
                        sp_grp = df_sp.set_index('Datetime').resample('h')
                        log_entry["cumulative"]["sp_unk_qsos"] = process_series(sp_grp.size())
                        log_entry["cumulative"]["sp_unk_points"] = process_series(sp_grp['QSOPoints'].sum())
                    else:
                        log_entry["cumulative"]["sp_unk_qsos"] = zeros
                        log_entry["cumulative"]["sp_unk_points"] = zeros
                else:
                    # Log exists but only dupes?
                    for k in ["qsos", "points", "run_qsos", "sp_unk_qsos", "run_points", "sp_unk_points"]:
                        log_entry["cumulative"][k] = zeros
            else:
                for k in ["qsos", "points", "run_qsos", "sp_unk_qsos", "run_points", "sp_unk_points"]:
                    log_entry["cumulative"][k] = zeros

            # --- Score & Mults (Global Only) ---
            # Protocol: If filters are active, Score/Mults are strictly 0 because
            # we cannot accurately re-calculate contest score on a partial slice without
            # the full calculator context.
            is_filtered = (band_filter and band_filter != 'All') or (mode_filter is not None)

            if not is_filtered and hasattr(log, 'time_series_score_df') and log.time_series_score_df is not None:
                # Use ffill to propagate the score across hours where no QSOs occurred
                ts_df = log.time_series_score_df.reindex(master_index).ffill().fillna(0)
                
                if 'score' in ts_df:
                    log_entry["cumulative"]["score"] = ts_df['score'].astype(int).tolist()
                else:
                     log_entry["cumulative"]["score"] = zeros
                     
                if 'total_mults' in ts_df:
                    log_entry["cumulative"]["mults"] = ts_df['total_mults'].astype(int).tolist()
                else:
                    log_entry["cumulative"]["mults"] = zeros
            else:
                log_entry["cumulative"]["score"] = zeros
                log_entry["cumulative"]["mults"] = zeros


            # --- Hourly Data ---
            if not df_full.empty:
                df_hourly = df_full[df_full['Dupe'] == False].copy()
                
                if not df_hourly.empty:
                    # -- 1. By Band --
                    # Group by Hour and Band
                    grp_band = df_hourly.groupby([df_hourly['Datetime'].dt.floor('h'), 'Band']).size().unstack(fill_value=0)
                    grp_band = grp_band.reindex(master_index).fillna(0).astype(int)
                    
                    # Total Hourly QSOs
                    log_entry["hourly"]["qsos"] = grp_band.sum(axis=1).tolist()
                    
                    valid_bands = contest_def.valid_bands
                    for band in valid_bands:
                        if band in grp_band.columns:
                            log_entry["hourly"]["by_band"][band] = grp_band[band].tolist()
                        else:
                            log_entry["hourly"]["by_band"][band] = [0] * len(master_index)

                    # -- 2. By Mode --
                    if 'Mode' in df_hourly.columns:
                        grp_mode = df_hourly.groupby([df_hourly['Datetime'].dt.floor('h'), 'Mode']).size().unstack(fill_value=0)
                        grp_mode = grp_mode.reindex(master_index).fillna(0).astype(int)
                        
                        # Populate by_mode for all modes present in log
                        for mode in grp_mode.columns:
                            log_entry["hourly"]["by_mode"][mode] = grp_mode[mode].tolist()

                    # -- 3. By Band + Mode --
                    if 'Band' in df_hourly.columns and 'Mode' in df_hourly.columns:
                        grp_bm = df_hourly.groupby([df_hourly['Datetime'].dt.floor('h'), 'Band', 'Mode']).size().unstack(['Band', 'Mode'], fill_value=0)
                        grp_bm = grp_bm.reindex(master_index).fillna(0).astype(int)

                        # grp_bm columns are MultiIndex (Band, Mode). 
                        # Flatten to keys "Band_Mode" (e.g. "20M_CW")
                        for col in grp_bm.columns:
                            # col is tuple (Band, Mode)
                            band_key, mode_key = col
                            key = f"{band_key}_{mode_key}"
                            log_entry["hourly"]["by_band_mode"][key] = grp_bm[col].tolist()

                else:
                    # Log empty after dupe filtering
                    log_entry["hourly"]["qsos"] = zeros
                    for band in contest_def.valid_bands:
                        log_entry["hourly"]["by_band"][band] = zeros
            else:
                # Log completely empty
                log_entry["hourly"]["qsos"] = zeros
                for band in contest_def.valid_bands:
                    log_entry["hourly"]["by_band"][band] = zeros
            
            data["logs"][callsign] = log_entry

        return data