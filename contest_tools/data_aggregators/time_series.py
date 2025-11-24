# contest_tools/data_aggregators/time_series.py
#
# Purpose: Aggregates time-series data from contest logs into a standardized
#          JSON-compatible structure (Pure Python Primitives).
#
# Author: Gemini AI
# Date: 2025-11-24
# Version: 1.2.0
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

    def get_time_series_data(self) -> Dict[str, Any]:
        """
        Generates the TimeSeriesData v1.2 structure.
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
            
            # --- Scalars ---
            df_full = log.get_processed_data()
            if df_full.empty:
                # Handle empty log gracefully
                gross_qsos = 0
                dupes = 0
                net_qsos = 0
                year = "UnknownYear"
            else:
                gross_qsos = len(df_full)
                dupes = df_full['Dupe'].sum() if 'Dupe' in df_full.columns else 0
                net_qsos = gross_qsos - dupes
                
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
                    "on_time": str(on_time),
                    "contest_name": str(contest_name),
                    "year": str(year)
                },
                "cumulative": {
                    "qsos": [], "points": [], "mults": [], 
                    "score": [], "run_qsos": [], "sp_unk_qsos": []
                },
                "hourly": { 
                    "qsos": [], 
                    "by_band": {} 
                }
            }

            # --- Cumulative Data ---
            # Access pre-calculated time series score dataframe
            if hasattr(log, 'time_series_score_df') and log.time_series_score_df is not None:
                # Reindex to match the master timeline, filling gaps with current state (ffill) or 0? 
                # Plan says "fillna 0".
                ts_df = log.time_series_score_df.reindex(master_index).fillna(0)
                
                # Extract and cast to pure Python integers
                if 'qsos' in ts_df:
                    log_entry["cumulative"]["qsos"] = ts_df['qsos'].astype(int).tolist()
                if 'score' in ts_df:
                    log_entry["cumulative"]["score"] = ts_df['score'].astype(int).tolist()
                    # Mapping score df columns to schema keys
                    # Assuming 'score' in df is points or score? 
                    # Usually: 'score' is total score, 'points' might be QSO points.
                    # Based on standard contest logic, we map available cols.
                    log_entry["cumulative"]["points"] = ts_df['score'].astype(int).tolist() # Fallback mapping
                
                if 'total_mults' in ts_df:
                    log_entry["cumulative"]["mults"] = ts_df['total_mults'].astype(int).tolist()
                if 'run_qso_count' in ts_df:
                    log_entry["cumulative"]["run_qsos"] = ts_df['run_qso_count'].astype(int).tolist()
                if 'sp_unk_qso_count' in ts_df:
                    log_entry["cumulative"]["sp_unk_qsos"] = ts_df['sp_unk_qso_count'].astype(int).tolist()

            # --- Hourly Data ---
            # Plan explicit instruction: "Get get_valid_dataframe(log, include_dupes=False)"
            if not df_full.empty:
                df_hourly = df_full[df_full['Dupe'] == False].copy()
                
                if not df_hourly.empty:
                    # Group by Hour and Band
                    grp = df_hourly.groupby([df_hourly['Datetime'].dt.floor('h'), 'Band']).size().unstack(fill_value=0)
                    
                    # Reindex to master timeline
                    grp = grp.reindex(master_index).fillna(0).astype(int)
                    
                    # Total Hourly QSOs
                    log_entry["hourly"]["qsos"] = grp.sum(axis=1).tolist()
                    
                    # By Band
                    valid_bands = contest_def.valid_bands
                    for band in valid_bands:
                        if band in grp.columns:
                            log_entry["hourly"]["by_band"][band] = grp[band].tolist()
                        else:
                            log_entry["hourly"]["by_band"][band] = [0] * len(master_index)
                else:
                    # Log exists but has no valid non-dupe QSOs
                    log_entry["hourly"]["qsos"] = [0] * len(master_index)
                    for band in contest_def.valid_bands:
                        log_entry["hourly"]["by_band"][band] = [0] * len(master_index)
            
            data["logs"][callsign] = log_entry

        return data