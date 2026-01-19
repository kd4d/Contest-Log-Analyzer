# contest_tools/data_aggregators/time_series.py
#
# Purpose: Aggregates time-series data from contest logs into a standardized
#          JSON-compatible structure (Pure Python Primitives).
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

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
            # Use same data source as scoreboard to ensure matching counts
            from ..utils.report_utils import get_valid_dataframe
            df_full = get_valid_dataframe(log, include_dupes=False)
            
            # Filter out zero-point QSOs if contest rules require it (match scoreboard logic)
            if not contest_def.mults_from_zero_point_qsos:
                df_full = df_full[df_full['QSOPoints'] > 0].copy()

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
                scalar_run_qsos = 0
                scalar_run_percent = 0.0
            else:
                gross_qsos = len(df_full)
                dupes = df_full['Dupe'].sum() if 'Dupe' in df_full.columns else 0
                net_qsos = gross_qsos - dupes
                # Raw Points Sum (Dynamic Calculation)
                points_sum = df_full['QSOPoints'].sum() if 'QSOPoints' in df_full.columns else 0
                
                # Calculate Scalar Run Metrics (Net QSOs only)
                df_valid_scalars = df_full[df_full['Dupe'] == False]
                scalar_run_qsos = df_valid_scalars[df_valid_scalars['Run'] == 'Run'].shape[0]
                scalar_run_percent = (scalar_run_qsos / net_qsos * 100) if net_qsos > 0 else 0.0

                # Extract Year
                date_series = df_full['Date'].dropna()
                year = date_series.iloc[0].split('-')[0] if not date_series.empty else "UnknownYear"

            on_time = metadata.get('OnTime', "") 
            contest_name = metadata.get('ContestName', 'UnknownContest')
            
            # Calculate Multiplier Breakdown (Scalars)
            mult_breakdown = {}
            final_score_scalar = 0
            
            if not df_full.empty:
                df_valid_scalars = df_full[df_full['Dupe'] == False].copy()
                if not df_valid_scalars.empty:
                    for rule in contest_def.multiplier_rules:
                        mult_name = rule.get('name', 'Unknown')
                        col = rule.get('value_column')
                        method = rule.get('totaling_method', 'sum_by_band')

                        if col and col in df_valid_scalars.columns:
                            # Filter out 'Unknown' or NaNs before counting
                            valid_mults = df_valid_scalars[df_valid_scalars[col].notna() & (df_valid_scalars[col] != 'Unknown')]
                            
                            if method == 'once_per_log':
                                mult_breakdown[mult_name] = int(valid_mults[col].nunique())
                            elif method == 'once_per_mode':
                                mult_breakdown[mult_name] = int(valid_mults.groupby('Mode')[col].nunique().sum())
                            else: # sum_by_band (default) or once_per_band_no_mode
                                mult_breakdown[mult_name] = int(valid_mults.groupby('Band')[col].nunique().sum())

            log_entry = {
                "scalars": {
                    "gross_qsos": int(gross_qsos),
                    "net_qsos": int(net_qsos),
                    "dupes": int(dupes),
                    "points_sum": int(points_sum),
                    "on_time": str(on_time),
                    "contest_name": str(contest_name),
                    "year": str(year),
                    "final_score": int(final_score_scalar),
                    "mult_breakdown": mult_breakdown,
                    "run_qsos": int(scalar_run_qsos),
                    "run_percent": round(float(scalar_run_percent), 1)
                },
                "cumulative": {
                    "qsos": [], "points": [], "mults": [], 
                    "score": [], "run_qsos": [], "sp_unk_qsos": [],
                    "run_points": [], "sp_unk_points": [],
                    "sp_qsos": [], "unknown_qsos": [], "sp_points": [], "unknown_points": []
                },
                "hourly": { 
                    "qsos": [], 
                    "by_band": {},
                    "by_mode": {},
                    "by_band_mode": {},
                    "new_mults_by_band": {},
                    "new_mults_by_mode": {},
                    "cumulative_mults": []
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
                    sp_mask = df_valid['Run'] == 'S&P'
                    unk_mask = df_valid['Run'] == 'Unknown'
                    
                    # Split Dataframes
                    df_run = df_valid[run_mask]
                    df_sp_unk = df_valid[~run_mask]
                    df_sp_only = df_valid[sp_mask]
                    df_unk_only = df_valid[unk_mask]

                    # Run QSOs / Points
                    if not df_run.empty:
                        run_grp = df_run.set_index('Datetime').resample('h')
                        log_entry["cumulative"]["run_qsos"] = process_series(run_grp.size())
                        log_entry["cumulative"]["run_points"] = process_series(run_grp['QSOPoints'].sum())
                    else:
                        log_entry["cumulative"]["run_qsos"] = zeros
                        log_entry["cumulative"]["run_points"] = zeros
                    
                    # S&P+Unknown QSOs / Points (Legacy Support)
                    if not df_sp_unk.empty:
                        sp_grp = df_sp_unk.set_index('Datetime').resample('h')
                        log_entry["cumulative"]["sp_unk_qsos"] = process_series(sp_grp.size())
                        log_entry["cumulative"]["sp_unk_points"] = process_series(sp_grp['QSOPoints'].sum())
                    else:
                        log_entry["cumulative"]["sp_unk_qsos"] = zeros
                        log_entry["cumulative"]["sp_unk_points"] = zeros

                    # Strict S&P QSOs / Points (New)
                    if not df_sp_only.empty:
                        sp_only_grp = df_sp_only.set_index('Datetime').resample('h')
                        log_entry["cumulative"]["sp_qsos"] = process_series(sp_only_grp.size())
                        log_entry["cumulative"]["sp_points"] = process_series(sp_only_grp['QSOPoints'].sum())
                    else:
                        log_entry["cumulative"]["sp_qsos"] = zeros
                        log_entry["cumulative"]["sp_points"] = zeros

                    # Unknown QSOs / Points (New)
                    if not df_unk_only.empty:
                        unk_grp = df_unk_only.set_index('Datetime').resample('h')
                        log_entry["cumulative"]["unknown_qsos"] = process_series(unk_grp.size())
                        log_entry["cumulative"]["unknown_points"] = process_series(unk_grp['QSOPoints'].sum())
                    else:
                        log_entry["cumulative"]["unknown_qsos"] = zeros
                        log_entry["cumulative"]["unknown_points"] = zeros

                else:
                    # Log exists but only dupes?
                    for k in ["qsos", "points", "run_qsos", "sp_unk_qsos", "run_points", "sp_unk_points", "sp_qsos", "unknown_qsos", "sp_points", "unknown_points"]:
                        log_entry["cumulative"][k] = zeros
            else:
                for k in ["qsos", "points", "run_qsos", "sp_unk_qsos", "run_points", "sp_unk_points", "sp_qsos", "unknown_qsos", "sp_points", "unknown_points"]:
                    log_entry["cumulative"][k] = zeros

            # --- Score & Mults (Global Only) ---
            # Protocol: If filters are active, Score/Mults are strictly 0 because
            # we cannot accurately re-calculate contest score on a partial slice without
            # the full calculator context.
            is_filtered = (band_filter and band_filter != 'All') or (mode_filter is not None)

            if not is_filtered and hasattr(log, 'time_series_score_df') and log.time_series_score_df is not None:
                # Extract final score for scalars
                if not log.time_series_score_df.empty and 'score' in log.time_series_score_df.columns:
                    log_entry["scalars"]["final_score"] = int(log.time_series_score_df['score'].iloc[-1])
                
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
            
            # --- Hourly Multiplier Data ---
            if not df_full.empty and not is_filtered:
                # df_full already has dupes filtered and zero-point QSOs filtered (if applicable)
                df_valid = df_full.copy()
                if not df_valid.empty:
                    log_location_type = getattr(log, '_my_location_type', None)
                    hourly_mult_data = self._calculate_hourly_multipliers(
                        df_valid, master_index, contest_def, log_location_type, log=log
                    )
                    log_entry["hourly"]["new_mults_by_band"] = hourly_mult_data["new_mults_by_band"]
                    log_entry["hourly"]["new_mults_by_mode"] = hourly_mult_data["new_mults_by_mode"]
                    log_entry["hourly"]["cumulative_mults"] = hourly_mult_data["cumulative_mults"]
                else:
                    # Initialize empty structures
                    for band in contest_def.valid_bands:
                        log_entry["hourly"]["new_mults_by_band"][band] = zeros
                    log_entry["hourly"]["cumulative_mults"] = zeros
            else:
                # Initialize empty structures
                for band in contest_def.valid_bands:
                    log_entry["hourly"]["new_mults_by_band"][band] = zeros
                log_entry["hourly"]["cumulative_mults"] = zeros
            
            data["logs"][callsign] = log_entry

        return data
    
    def _calculate_hourly_multipliers(
        self, df: pd.DataFrame, master_index: pd.DatetimeIndex, contest_def, log_location_type: str = None, log: Any = None
    ) -> Dict[str, Any]:
        """
        Calculates NEW multipliers per hour per band/mode and cumulative multipliers.
        
        Returns:
            {
                "new_mults_by_band": {band: [counts_per_hour, ...]},
                "new_mults_by_mode": {mode: [counts_per_hour, ...]},
                "cumulative_mults": [cum_counts_per_hour, ...]
            }
        """
        result = {
            "new_mults_by_band": {},
            "new_mults_by_mode": {},
            "cumulative_mults": [0] * len(master_index)
        }
        
        if df.empty or not contest_def.multiplier_rules:
            # Initialize empty structures
            valid_bands = contest_def.valid_bands
            for band in valid_bands:
                result["new_mults_by_band"][band] = [0] * len(master_index)
            return result
        
        # Get all multiplier columns
        mult_cols = [rule['value_column'] for rule in contest_def.multiplier_rules 
                    if rule.get('value_column') in df.columns]
        
        if not mult_cols:
            logger.warning(f"_calculate_hourly_multipliers: No multiplier columns found in dataframe")
            # Initialize empty structures
            valid_bands = contest_def.valid_bands
            for band in valid_bands:
                result["new_mults_by_band"][band] = [0] * len(master_index)
            return result
        
        # Filter valid multipliers (not NaN, not 'Unknown')
        # IMPORTANT: For mutually exclusive multipliers (like ARRL 10), each QSO has only ONE multiplier column populated
        # So we need to filter to rows where ANY multiplier column has a valid value, not ALL columns
        df_valid = df.copy()
        
        # Build a mask for rows that have at least one valid multiplier
        has_valid_mult = pd.Series([False] * len(df_valid), index=df_valid.index)
        for col in mult_cols:
            if col in df_valid.columns:
                col_valid = df_valid[col].notna() & (df_valid[col] != 'Unknown')
                has_valid_mult = has_valid_mult | col_valid
        
        df_valid = df_valid[has_valid_mult]
        
        if df_valid.empty and not df.empty:
            logger.warning(f"_calculate_hourly_multipliers: All rows filtered out after multiplier validation. Original rows: {len(df)}, after filter: {len(df_valid)}")
            logger.warning(f"_calculate_hourly_multipliers: Multiplier columns checked: {mult_cols}")
            # Log sample values for debugging if no valid multipliers found
            for col in mult_cols:
                if col in df.columns:
                    sample_vals = df[col].dropna().head(10).tolist()
                    logger.warning(f"_calculate_hourly_multipliers: Column {col} sample values (first 10): {sample_vals}")
        
        if df_valid.empty:
            # Initialize empty structures
            valid_bands = contest_def.valid_bands
            for band in valid_bands:
                result["new_mults_by_band"][band] = [0] * len(master_index)
            return result
        
        # Initialize result structures
        valid_bands = contest_def.valid_bands
        for band in valid_bands:
            result["new_mults_by_band"][band] = [0] * len(master_index)
        
        # Filter multiplier rules by location type for ARRL DX and determine totaling_method
        applicable_rules = []
        for rule in contest_def.multiplier_rules:
            applies_to = rule.get('applies_to')
            if applies_to is None or (log_location_type and applies_to == log_location_type):
                col = rule.get('value_column')
                if col and col in mult_cols:
                    applicable_rules.append(rule)
        
        if not applicable_rules:
            # No applicable rules, initialize empty and return
            return result
        
        # Determine totaling_method from applicable rules
        # If all rules have the same totaling_method, use that. Otherwise, default to sum_by_band.
        totaling_methods = [rule.get('totaling_method', 'sum_by_band') for rule in applicable_rules]
        if len(set(totaling_methods)) == 1:
            totaling_method = totaling_methods[0]
        else:
            # Mixed totaling_methods - use sum_by_band as default (most common)
            totaling_method = 'sum_by_band'
        
        # Track multipliers based on totaling_method
        if totaling_method == 'once_per_log':
            # Global tracking across all bands - multiplier counts once regardless of band
            seen_mults_global = set()
        elif totaling_method in ['sum_by_band', 'once_per_band_no_mode']:
            # Per-band tracking - same multiplier can count on different bands
            seen_mults_by_band = {band: set() for band in valid_bands}
        else:
            # Default to per-band tracking for other methods (once_per_mode handled separately)
            seen_mults_by_band = {band: set() for band in valid_bands}
        
        # For once_per_mode, track multipliers separately per mode per rule, then sum
        # For other methods, use single shared tracking
        if totaling_method == 'once_per_mode':
            # Track per rule per mode: {mode: {rule_col: set()}}
            # This matches score summary logic: count unique per rule per mode, then sum
            seen_mults_by_mode_by_rule = {}  # {mode: {col: set()}}
        else:
            seen_mults_by_mode = set()
        
        # Cumulative tracking (union of all multipliers across all dimensions)
        seen_mults_cumulative = set()
        
        # Get applicable multiplier columns
        applicable_mult_cols = [rule['value_column'] for rule in applicable_rules]
        
        # For each hour
        for hour_idx, hour_ts in enumerate(master_index):
            # Get QSOs in this hour
            hour_start = hour_ts
            hour_end = hour_ts + pd.Timedelta(hours=1)
            hour_df = df_valid[
                (df_valid['Datetime'] >= hour_start) & 
                (df_valid['Datetime'] < hour_end)
            ]
            
            
            # Calculate new multipliers per band
            for band in valid_bands:
                band_df = hour_df[hour_df['Band'] == band]
                if not band_df.empty:
                    # Collect all multiplier values from all multiplier columns for this hour/band
                    new_mults_this_hour_band = set()
                    for col in applicable_mult_cols:
                        if col in band_df.columns:
                            # Filter out NaN and 'Unknown' values
                            valid_mults = band_df[col].dropna()
                            valid_mults = valid_mults[valid_mults != 'Unknown']
                            for mult_val in valid_mults:
                                # Check if this is a NEW multiplier based on totaling_method
                                is_new_mult = False
                                if totaling_method == 'once_per_log':
                                    # Global tracking - multiplier counts once across all bands
                                    if mult_val not in seen_mults_global:
                                        is_new_mult = True
                                        seen_mults_global.add(mult_val)
                                elif totaling_method in ['sum_by_band', 'once_per_band_no_mode']:
                                    # Per-band tracking - same multiplier can count on different bands
                                    if mult_val not in seen_mults_by_band[band]:
                                        is_new_mult = True
                                        seen_mults_by_band[band].add(mult_val)
                                else:
                                    # Default to per-band tracking for other methods
                                    if mult_val not in seen_mults_by_band[band]:
                                        is_new_mult = True
                                        seen_mults_by_band[band].add(mult_val)
                                
                                if is_new_mult:
                                    new_mults_this_hour_band.add(mult_val)
                                    # Also add to cumulative tracking
                                    seen_mults_cumulative.add(mult_val)
                    
                    
                    result["new_mults_by_band"][band][hour_idx] = len(new_mults_this_hour_band)
            
            # Calculate new multipliers per mode (inside hour loop)
            if 'Mode' in df_valid.columns:
                modes_present = df_valid['Mode'].unique()
                for mode in modes_present:
                    if mode not in result["new_mults_by_mode"]:
                        result["new_mults_by_mode"][mode] = [0] * len(master_index)
                    
                    mode_df = hour_df[hour_df['Mode'] == mode]
                    if not mode_df.empty:
                        new_mults_this_hour_mode = set()
                        for col in applicable_mult_cols:
                            if col in mode_df.columns:
                                # Filter out NaN and 'Unknown' values
                                valid_mults = mode_df[col].dropna()
                                valid_mults = valid_mults[valid_mults != 'Unknown']
                                for mult_val in valid_mults:
                                    # Check if this is a NEW multiplier for this mode
                                    # For once_per_mode: track separately per mode per rule (column), then sum
                                    # This matches score summary: count unique per rule per mode, sum across rules
                                    # For other methods: use shared tracking across all modes
                                    is_new_mult = False
                                    if totaling_method == 'once_per_mode':
                                        # Track per rule (column) per mode - allows same multiplier value in different columns
                                        # to count separately (though for mutually exclusive, this shouldn't happen)
                                        if mode not in seen_mults_by_mode_by_rule:
                                            seen_mults_by_mode_by_rule[mode] = {}
                                        if col not in seen_mults_by_mode_by_rule[mode]:
                                            seen_mults_by_mode_by_rule[mode][col] = set()
                                        if mult_val not in seen_mults_by_mode_by_rule[mode][col]:
                                            is_new_mult = True
                                            seen_mults_by_mode_by_rule[mode][col].add(mult_val)
                                    else:
                                        # Shared tracking - multiplier counts once across all modes
                                        if mult_val not in seen_mults_by_mode:
                                            is_new_mult = True
                                            seen_mults_by_mode.add(mult_val)
                                    
                                    if is_new_mult:
                                        new_mults_this_hour_mode.add(mult_val)
                                        # Also add to cumulative tracking (for other totaling methods)
                                        if totaling_method != 'once_per_mode':
                                            seen_mults_cumulative.add(mult_val)
                        
                        result["new_mults_by_mode"][mode][hour_idx] = len(new_mults_this_hour_mode)
            
            # Calculate cumulative multipliers up to this hour
            # For once_per_mode: sum unique multipliers per mode (matches score summary logic)
            # For sum_by_band: use sum of per-band unique multipliers (matches band-by-band totals)
            # For once_per_log: use globally unique multipliers
            if totaling_method == 'once_per_log':
                # Global tracking - use globally unique count
                result["cumulative_mults"][hour_idx] = len(seen_mults_global) if 'seen_mults_global' in locals() else len(seen_mults_cumulative)
            elif totaling_method == 'once_per_mode':
                # Per-mode tracking - sum unique multipliers per rule per mode, then sum across rules
                # This matches score summary logic: for each rule, count unique per mode, sum across modes, then sum across rules
                # Structure: {mode: {col: set()}} - sum unique per col per mode, then sum across all cols and modes
                total_cumulative = 0
                for mode in seen_mults_by_mode_by_rule:
                    for col in seen_mults_by_mode_by_rule[mode]:
                        total_cumulative += len(seen_mults_by_mode_by_rule[mode][col])
                result["cumulative_mults"][hour_idx] = total_cumulative
            elif totaling_method in ['sum_by_band', 'once_per_band_no_mode']:
                # Per-band tracking - sum unique multipliers per band (matches band totals)
                result["cumulative_mults"][hour_idx] = sum(len(seen_mults_by_band[band]) for band in valid_bands)
            else:
                # Default: use cumulative tracking which includes all multipliers from both dimensions
                result["cumulative_mults"][hour_idx] = len(seen_mults_cumulative)
        
        return result