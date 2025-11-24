# contest_tools/data_aggregators/multiplier_stats.py
#
# Purpose: Centralizes the calculation logic for multiplier statistics,
#          serving both the 'Multiplier Summary' and 'Missed Multipliers' reports.
#
# Author: Gemini AI
# Date: 2025-11-23
# Version: 0.93.0
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
# [0.93.0] - 2025-11-23
# - Initial creation. Extracted logic from text_multiplier_summary.py and
#   text_missed_multipliers.py.

from typing import List, Dict, Any, Set
import pandas as pd
from ..contest_log import ContestLog
from ..reports._report_utils import calculate_multiplier_pivot

class MultiplierStatsAggregator:
    def __init__(self, logs: List[ContestLog]):
        if not logs:
            raise ValueError("Aggregator requires at least one log.")
        self.logs = logs
        # Assume all logs share the same definition
        self.contest_def = logs[0].contest_definition

    def _get_run_sp_status(self, series: pd.Series) -> str:
        """Determines if a multiplier was worked via Run, S&P, Unknown, or a combination."""
        modes = set(series.unique())
        has_run = "Run" in modes
        has_sp = "S&P" in modes
        if has_run and has_sp: return "Both"
        elif has_run: return "Run"
        elif has_sp: return "S&P"
        elif "Unknown" in modes: return "Unk"
        return ""

    def get_summary_data(self, mult_name: str, mode_filter: str = None) -> Dict[str, Any]:
        """
        Extracts logic from text_multiplier_summary.py.
        Returns a dictionary containing the pivot table and metadata needed for rendering.
        """
        # --- 1. Filter Data ---
        log_data_to_process = []
        for log in self.logs:
            df = log.get_processed_data()
            if mode_filter:
                filtered_df = df[df['Mode'] == mode_filter].copy()
            else:
                filtered_df = df.copy()
            log_data_to_process.append({'df': filtered_df, 'meta': log.get_metadata()})

        # --- 2. Determine Callsigns ---
        all_dfs = []
        all_calls = []
        
        # Handle Single vs Multi logic
        if len(log_data_to_process) == 1:
            log_data = log_data_to_process[0]
            df = log_data['df'][log_data['df']['Dupe'] == False]
            my_call = log_data['meta'].get('MyCall', 'Unknown')
            all_calls = [my_call]
            all_dfs = [df]
        else:
            for log_data in log_data_to_process:
                df = log_data['df'][log_data['df']['Dupe'] == False].copy()
                if not df.empty:
                    my_call = log_data['meta'].get('MyCall', 'Unknown')
                    df['MyCall'] = my_call
                    all_calls.append(my_call)
                    all_dfs.append(df)
            all_calls.sort()

        # --- 3. Validate Rules ---
        mult_rule = next((r for r in self.contest_def.multiplier_rules if r.get('name', '').lower() == mult_name.lower()), None)
        if not mult_rule or 'value_column' not in mult_rule:
             return {'error': f"Error: Multiplier type '{mult_name}' not found in definition."}
        
        mult_column = mult_rule['value_column']
        
        # --- 4. Combine and Filter Main DF ---
        combined_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
        
        if combined_df.empty or mult_column not in combined_df.columns:
             # Return empty structures but sufficient to render "No data" message
             return {
                 'pivot': pd.DataFrame(), 
                 'all_calls': all_calls,
                 'mult_column': mult_column,
                 'mult_rule': mult_rule,
                 'combined_df': pd.DataFrame(),
                 'main_df': pd.DataFrame(),
                 'bands': self.contest_def.valid_bands
             }

        main_df = combined_df[combined_df[mult_column].notna()]
        main_df = main_df[main_df[mult_column] != 'Unknown']

        if not self.contest_def.mults_from_zero_point_qsos:
            main_df = main_df[main_df['QSOPoints'] > 0]

        # --- 5. Calculate Pivot ---
        is_comparative = len(all_calls) > 1
        pivot = calculate_multiplier_pivot(main_df, mult_column, group_by_call=is_comparative)

        return {
            'pivot': pivot,
            'all_calls': all_calls,
            'mult_column': mult_column,
            'mult_rule': mult_rule,
            'combined_df': combined_df,
            'main_df': main_df,
            'bands': self.contest_def.valid_bands
        }

    def get_missed_data(self, mult_name: str, mode_filter: str = None) -> Dict[str, Any]:
        """
        Extracts logic from text_missed_multipliers.py.
        Returns a dictionary mapping bands to their respective missed/worked sets.
        """
        # --- 1. Setup Rules and Calls ---
        mult_rule = next((r for r in self.contest_def.multiplier_rules if r.get('name', '').lower() == mult_name.lower()), None)
        if not mult_rule or 'value_column' not in mult_rule:
             return {'error': f"Error: Multiplier type '{mult_name}' not found."}

        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        
        # --- 2. Filter Data ---
        log_data_to_process = []
        for log in self.logs:
            df = log.get_processed_data()
            if mode_filter:
                filtered_df = df[df['Mode'] == mode_filter].copy()
            else:
                filtered_df = df.copy()
            log_data_to_process.append({'df': filtered_df, 'meta': log.get_metadata()})

        # --- 3. Determine Bands ---
        bands_to_process = ["All Bands"] if mult_rule.get('totaling_method') == 'once_per_log' else self.contest_def.valid_bands

        full_results = {
            'bands_to_process': bands_to_process,
            'all_calls': all_calls,
            'mult_rule': mult_rule,
            'band_data': {}
        }

        # --- 4. Iterate Bands (Logic from _aggregate_band_data) ---
        mult_column = mult_rule['value_column']
        name_column = mult_rule.get('name_column')

        for band in bands_to_process:
            band_data_map: Dict[str, pd.DataFrame] = {}
            mult_sets: Dict[str, Set[str]] = {call: set() for call in all_calls}
            prefix_to_name_map = {}

            for log_data in log_data_to_process:
                callsign = log_data['meta'].get('MyCall', 'Unknown')
                df = log_data['df'][log_data['df']['Dupe'] == False].copy()
                if df.empty or mult_column not in df.columns: continue
                
                df_scope = df if band == "All Bands" else df[df['Band'] == band].copy()
                
                df_scope = df_scope[df_scope[mult_column] != 'Unknown']
                df_scope = df_scope[df_scope[mult_column].notna()]
                if df_scope.empty: continue
                
                if name_column and name_column in df_scope.columns:
                    name_map_df = df_scope[[mult_column, name_column]].dropna().drop_duplicates()
                    for _, row in name_map_df.iterrows():
                        prefix_to_name_map[row[mult_column]] = row[name_column]

                agg_data = df_scope.groupby(mult_column).agg(
                    QSO_Count=('Call', 'size'), Run_SP_Status=('Run', self._get_run_sp_status))
                band_data_map[callsign] = agg_data
                mult_sets[callsign].update(agg_data.index)

            union_of_all_mults = set.union(*mult_sets.values()) if mult_sets.values() else set()
            
            missed_mults_on_band = set()
            for call in all_calls:
                missed_mults_on_band.update(union_of_all_mults.difference(mult_sets[call]))

            full_results['band_data'][band] = {
                "band_data": band_data_map, 
                "mult_sets": mult_sets, 
                "prefix_to_name_map": prefix_to_name_map,
                "union_of_all_mults": union_of_all_mults, 
                "missed_mults_on_band": missed_mults_on_band
            }

        return full_results