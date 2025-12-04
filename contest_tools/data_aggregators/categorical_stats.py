# contest_tools/data_aggregators/categorical_stats.py
#
# Purpose: DAL component to handle aggregation logic related to categorical data
#          such as QSO point breakdowns and set comparisons (unique/common QSOs).
#
# Author: Gemini AI
# Date: 2025-11-24
# Version: 0.93.0-Beta
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
# --- Revision History ---
# [0.93.0-Beta] - 2025-11-24
# - New file. Implements CategoricalAggregator with methods get_points_breakdown
#   and compute_comparison_breakdown. Adheres to Dict-in/Dict-out interface.
# - Implements dynamic uniqueness keying for comparison breakdown (Call or Call+Mode).

from typing import List, Dict, Union, Set, Tuple
import pandas as pd
# Assuming ContestLog is available for type hinting and has .get_valid_dataframe()
# from contest_tools.data_models.contest_log import ContestLog 

# Placeholder type for ContestLog as the actual class is not available in the manifest.
# The core requirement is that it exposes a .get_valid_dataframe() method.
class ContestLog:
    """Placeholder for the ContestLog domain object."""
    def get_valid_dataframe(self, filter_cols: List[str] = None) -> pd.DataFrame:
        pass


class CategoricalAggregator:
    """
    DAL Component: Handles aggregation logic related to categorical data
    such as QSO point breakdowns and set comparisons (unique/common QSOs).

    Strictly adheres to Interface Segregation:
    - Inputs: Domain objects (ContestLog) or primitives.
    - Outputs: Pure Python primitives (Dict, List, int, str).
    - Internal use of Pandas DataFrames is permitted.
    """

    def _apply_filters(self, df: pd.DataFrame, band_filter: str = None, mode_filter: str = None) -> pd.DataFrame:
        """Internal helper to apply optional band and mode filters to a DataFrame."""
        if df.empty:
            return df

        filtered_df = df.copy()

        if band_filter:
            filtered_df = filtered_df[filtered_df['Band'] == band_filter]
        
        if mode_filter:
            # Handle standard modes 'R' (Run) and 'S' (S&P). Unknown/None are handled implicitly.
            mode_filter = mode_filter.upper()
            if mode_filter in ['R', 'S']:
                filtered_df = filtered_df[filtered_df['QSOMode'] == mode_filter]
            # No explicit filter for 'Unk' here, as it's better handled outside this function
            # or requires a specific column check. Leaving simple 'R'/'S' filtering for now.

        return filtered_df

    def get_points_breakdown(self, logs: List[ContestLog], band_filter: str = None, mode_filter: str = None) -> Dict:
        """
        Calculates total points and a breakdown of points by QSO point value.

        Args:
            logs: List of ContestLog objects.
            band_filter: Optional band to filter by (e.g., '20M').
            mode_filter: Optional mode to filter by ('R' or 'S').

        Returns:
            A dictionary conforming to the plan's schema.
        """
        result: Dict = {"logs": {}}

        for log in logs:
            callsign = log.callsign if hasattr(log, 'callsign') else "UNKNOWN_LOG"
            
            # 1. Internal: Get DataFrame and apply filters
            # Ensure we fetch all necessary columns
            df = log.get_valid_dataframe(filter_cols=['QSOPoints', 'Band', 'QSOMode'])
            filtered_df = self._apply_filters(df, band_filter, mode_filter)

            if filtered_df.empty:
                result["logs"][callsign] = {
                    "total_points": 0,
                    "total_qsos": 0,
                    "breakdown": {}
                }
                continue

            # 2. Aggregation: Calculate totals and breakdown
            total_points = filtered_df['QSOPoints'].sum()
            total_qsos = len(filtered_df)
            
            # value_counts() gives a Series: index=point_value (int), value=count (int)
            breakdown_counts = filtered_df['QSOPoints'].value_counts()
            
            # Convert the Series to a dictionary { "point_value_str": count_int }
            breakdown = {str(k): int(v) for k, v in breakdown_counts.items()}

            # 3. Final structure assembly
            result["logs"][callsign] = {
                "total_points": int(total_points) if not pd.isna(total_points) else 0,
                "total_qsos": int(total_qsos),
                "breakdown": breakdown
            }
        
        return result

    def _get_qso_mode_counts(self, df: pd.DataFrame) -> Dict[str, int]:
        """Internal helper to categorize QSOs by R, S, or Unk."""
        if df.empty:
            return {'run': 0, 'sp': 0, 'unk': 0}
        
        # Use .str.upper().str.strip() for robustness
        modes = df['QSOMode'].astype(str).str.upper().str.strip()
        modes = modes.replace({'R': 'run', 'S': 'sp'})
        
        # Identify unknown/non-R/non-S modes
        valid_modes = {'run', 'sp'}
        modes = modes.apply(lambda x: x if x in valid_modes else 'unk')
        
        counts = modes.value_counts().to_dict()
        
        # Ensure all required keys exist, initialized to 0
        return {
            'run': counts.get('run', 0),
            'sp': counts.get('sp', 0),
            'unk': counts.get('unk', 0)
        }

    def compute_comparison_breakdown(self, log1: ContestLog, log2: ContestLog, band_filter: str = None, mode_filter: str = None) -> Dict:
        """
        Compares two logs for unique and common QSOs based on 'Call',
        and provides a breakdown of results by run/S&P mode.

        Args:
            log1: The primary ContestLog object (e.g., the submitted log).
            log2: The secondary ContestLog object (e.g., the checklog).
            band_filter: Optional band to filter by.
            mode_filter: Optional mode to filter by.

        Returns:
            A dictionary conforming to the set comparison schema.
        """
        # 1. Internal: Get DataFrames and apply filters
        df1_raw = log1.get_valid_dataframe(filter_cols=['Call', 'QSOMode', 'Band'])
        df2_raw = log2.get_valid_dataframe(filter_cols=['Call', 'QSOMode', 'Band'])
        
        df1 = self._apply_filters(df1_raw, band_filter, mode_filter)
        df2 = self._apply_filters(df2_raw, band_filter, mode_filter)
        
        # --- NEW LOGIC: Dynamic Uniqueness Key (per Plan 1.6.2) ---
        uniqueness_cols = ['Call']
        if not band_filter and not mode_filter:
            # Use Call and Mode to prevent mixed-mode collisions from counting as unique instances
            uniqueness_cols = ['Call', 'QSOMode']
            # Normalize QSOMode for set comparison integrity
            df1['QSOMode'] = df1['QSOMode'].astype(str).str.upper().str.strip()
            df2['QSOMode'] = df2['QSOMode'].astype(str).str.upper().str.strip()
            
        # 2. Set Analysis: Create sets of keys (strings or tuples)
        if uniqueness_cols == ['Call']:
            set1 = set(df1['Call'].unique())
            set2 = set(df2['Call'].unique())
        else:
            # Create a set of unique (Call, QSOMode) tuples
            set1 = set(tuple(row) for row in df1[uniqueness_cols].drop_duplicates().values)
            set2 = set(tuple(row) for row in df2[uniqueness_cols].drop_duplicates().values)

        common_keys = set1.intersection(set2)
        unique1_keys = set1.difference(set2)
        unique2_keys = set2.difference(set1)
        
        # Extract the Call list/set from the keys for steps 3 and 4, which require filtering by Call.
        # This derivation resolves the conflict between the Plan's dynamic key and the static schema requirement.
        
        def _extract_calls(keys: Set[Union[str, Tuple]]) -> Set[str]:
            """Helper to extract callsigns regardless if the input set contains strings or tuples."""
            if not keys:
                return set()
            # If keys are tuples (Call, Mode), extract the first element (Call)
            if isinstance(list(keys)[0], tuple):
                return set(k[0] for k in keys)
            # Otherwise, keys are strings (Call)
            return keys
        
        common_calls: Set[str] = _extract_calls(common_keys)
        unique1_calls: Set[str] = _extract_calls(unique1_keys)
        unique2_calls: Set[str] = _extract_calls(unique2_keys)

        # 3. Categorical Breakdown for Unique Sets (Filter original DFs by CALL)
        df1_unique = df1[df1['Call'].isin(unique1_calls)].copy()
        df2_unique = df2[df2['Call'].isin(unique2_calls)].copy()
        
        log1_unique_breakdown = self._get_qso_mode_counts(df1_unique)
        log2_unique_breakdown = self._get_qso_mode_counts(df2_unique)

        # 4. Categorical Breakdown for Common Set (Complex: Mode Must Match)
        common_breakdown: Dict[str, int] = {'run_both': 0, 'sp_both': 0, 'mixed': 0}
        
        if common_calls:
            # Get the records corresponding to common calls (filtered by band/mode already)
            df_common_1 = df1[df1['Call'].isin(common_calls)].copy()
            df_common_2 = df2[df2['Call'].isin(common_calls)].copy()

            # Merge to align common QSOs and their modes
            # Only keep the first unique record for each callsign in each log for comparison
            df_merged = pd.merge(
                df_common_1[['Call', 'QSOMode']].drop_duplicates(subset=['Call']).rename(columns={'QSOMode': 'Mode1'}),
                df_common_2[['Call', 'QSOMode']].drop_duplicates(subset=['Call']).rename(columns={'QSOMode': 'Mode2'}),
                on='Call',
                how='inner' 
            )

            if not df_merged.empty:
                df_merged['Mode1'] = df_merged['Mode1'].astype(str).str.upper().str.strip()
                df_merged['Mode2'] = df_merged['Mode2'].astype(str).str.upper().str.strip()
                
                # run_both: Both are 'R'
                common_breakdown['run_both'] = len(df_merged[
                    (df_merged['Mode1'] == 'R') & (df_merged['Mode2'] == 'R')
                ])
                
                # sp_both: Both are 'S'
                common_breakdown['sp_both'] = len(df_merged[
                    (df_merged['Mode1'] == 'S') & (df_merged['Mode2'] == 'S')
                ])
                
                # mixed: All others (one is R/S, other is UNK, or R/S mismatch)
                common_breakdown['mixed'] = len(df_merged) - (common_breakdown['run_both'] + common_breakdown['sp_both'])

        # 5. Metrics
        metrics = {
            # Total QSOs in the *filtered* logs
            "total_1": len(df1),
            "total_2": len(df2),
            # Count the size of the key sets (which reflects the dynamic uniqueness key)
            "unique_1": len(unique1_keys),
            "unique_2": len(unique2_keys),
            "common_total": len(common_keys)
        }
        
        # 6. Final structure assembly
        return {
            "log1_unique": log1_unique_breakdown,
            "log2_unique": log2_unique_breakdown,
            "common": common_breakdown,
            "metrics": metrics
        }
# --- EOF: End of File contest_tools/data_aggregators/categorical_stats.py ---