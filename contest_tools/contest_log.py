# Contest Log Analyzer/contest_tools/contest_log.py
#
# Purpose: Defines the ContestLog class, which manages the ingestion, processing,
#          and analysis of Cabrillo log data. It orchestrates the parsing,
#          data cleaning, and calculation of various contest metrics.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.28.5-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).
## [0.28.5-Beta] - 2025-08-04
### Changed
# - The `dxcc` multiplier source logic now correctly excludes contacts with
#   the USA and Canada to prevent "double multipliers".
# - The logic also inherently prevents a station from getting their own
#   country as a DXCC multiplier.
## [0.28.4-Beta] - 2025-08-03
### Added
# - A new method, `_calculate_operating_time`, to calculate on-time based on
#   rules from the contest definition (min_off_time, max_hours).
# - The calculated on-time is now determined and stored in the log's metadata
#   after all other annotations are applied.
from typing import List
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, Set, Tuple
import os
import re
import json
import importlib

# Relative imports from within the contest_tools package
from .cabrillo_parser import parse_cabrillo_file
from .contest_definitions import ContestDefinition
from .core_annotations import CtyLookup, process_dataframe_for_cty_data, process_contest_log_for_run_s_p

class ContestLog:
    """
    High-level broker class to manage a single amateur radio contest log.
    """

    _HF_BANDS = [
        (( 1800.,  2000.), '160M'),
        (( 3500.,  4000.), '80M'),
        (( 7000.,  7300.), '40M'),
        ((10100., 10150.), '30M'),
        ((14000., 14350.), '20M'),
        ((18068., 18168.), '17M'),
        ((21000., 21450.), '15M'),
        ((24890., 24990.), '12M'),
        ((28000., 29700.), '10M'),
        ((50000., 54000.), '6M'),
        ((144000., 148000.), '2M'),
        ((222000., 225000.), '1.25M'),
        ((420000., 450000.), '70CM'),
    ]

    @staticmethod
    def _derive_band_from_frequency(frequency_khz: float) -> str:
        if pd.isna(frequency_khz):
            return 'Invalid'
        frequency_int = int(frequency_khz)
        for band_range, band_name in ContestLog._HF_BANDS:
            if band_range[0] <= frequency_int <= band_range[1]:
                return band_name
        return 'Invalid'

    def __init__(self, contest_name: str, cabrillo_filepath: Optional[str] = None):
        self.contest_name = contest_name
        self.qsos_df: pd.DataFrame = pd.DataFrame()
        self.metadata: Dict[str, Any] = {}
        self.dupe_sets: Dict[str, Set[Tuple[str, str]]] = {}
        self.filepath = cabrillo_filepath
        self._my_location_type: Optional[str] = None # W/VE or DX

        try:
            self.contest_definition = ContestDefinition.from_json(contest_name)
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to load contest definition for '{contest_name}': {e}")

        if cabrillo_filepath:
            self._ingest_cabrillo_data(cabrillo_filepath)
            self._determine_own_location_type()


    def _ingest_cabrillo_data(self, cabrillo_filepath: str):
        raw_df, metadata = parse_cabrillo_file(cabrillo_filepath, self.contest_definition)
        self.metadata.update(metadata)

        if raw_df.empty:
            self.qsos_df = pd.DataFrame(columns=self.contest_definition.default_qso_columns)
            return

        raw_df['Frequency'] = pd.to_numeric(raw_df.get('FrequencyRaw'), errors='coerce')
        raw_df['Datetime'] = pd.to_datetime(
            raw_df.get('DateRaw', '') + ' ' + raw_df.get('TimeRaw', ''),
            format='%Y-%m-%d %H%M',
            errors='coerce'
        )
        raw_df.dropna(subset=['Frequency', 'Datetime'], inplace=True)

        if raw_df.empty:
            self.qsos_df = pd.DataFrame(columns=self.contest_definition.default_qso_columns)
            return

        raw_df['Band'] = raw_df['Frequency'].apply(self._derive_band_from_frequency)
        raw_df['Date'] = raw_df['Datetime'].dt.strftime('%Y-%m-%d')
        raw_df['Hour'] = raw_df['Datetime'].dt.strftime('%H')

        for col in ['MyCallRaw', 'Call', 'Mode']:
            if col in raw_df.columns:
                raw_df[col.replace('Raw','')] = raw_df[col].fillna('').astype(str).str.upper()

        raw_df.drop(columns=['FrequencyRaw', 'DateRaw', 'TimeRaw', 'MyCallRaw'], inplace=True, errors='ignore')
        self.qsos_df = raw_df.reindex(columns=self.contest_definition.default_qso_columns)
        self._check_dupes()

    def _check_dupes(self):
        self.qsos_df['Dupe'] = False
        self.dupe_sets.clear()
        
        dupe_scope = self.contest_definition.dupe_check_scope
        
        if dupe_scope == 'all_bands':
            all_bands_dupe_set = set()
            for idx in self.qsos_df.index:
                call = self.qsos_df.loc[idx, 'Call']
                if not call:
                    continue
                if call in all_bands_dupe_set:
                    self.qsos_df.loc[idx, 'Dupe'] = True
                else:
                    all_bands_dupe_set.add(call)
        else:
            for band in self.qsos_df['Band'].unique():
                if band == 'Invalid' or not band:
                    continue
                
                self.dupe_sets[band] = set()
                band_indices = self.qsos_df[self.qsos_df['Band'] == band].index
                
                for idx in band_indices:
                    call = self.qsos_df.loc[idx, 'Call']
                    mode = self.qsos_df.loc[idx, 'Mode']
                    
                    if not call or not mode:
                        continue
                    
                    qso_tuple = (call, mode)
                    if qso_tuple in self.dupe_sets[band]:
                        self.qsos_df.loc[idx, 'Dupe'] = True
                    else:
                        self.dupe_sets[band].add(qso_tuple)

    def _calculate_operating_time(self) -> Optional[str]:
        rules = self.contest_definition.operating_time_rules
        if not rules:
            return None

        min_off_time = pd.Timedelta(minutes=rules.get('min_off_time_minutes', 30))
        
        df = self.qsos_df[self.qsos_df['Dupe'] == False].sort_values(by='Datetime')
        
        if len(df) < 2:
            return "00:00"

        total_duration = df['Datetime'].iloc[-1] - df['Datetime'].iloc[0]
        gaps = df['Datetime'].diff()
        off_time_gaps = gaps[gaps > min_off_time]
        total_off_time = off_time_gaps.sum()
        
        on_time = total_duration - total_off_time

        total_seconds = on_time.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        on_time_str = f"{hours:02d}:{minutes:02d}"
        
        category = self.metadata.get('CategoryOperator', 'SINGLE-OP').upper()
        if 'MULTI' in category:
            max_hours = rules.get('multi_op_max_hours', 48)
        else:
            max_hours = rules.get('single_op_max_hours', 48)

        return f"{on_time_str} of {max_hours}:00 allowed"
        
    def _determine_own_location_type(self):
        my_call = self.metadata.get('MyCall')
        if my_call:
            data_dir = os.environ.get('CONTEST_DATA_DIR').strip().strip('"').strip("'")
            cty_dat_path = os.path.join(data_dir, 'cty.dat')
            cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
            info = cty_lookup.get_cty(my_call)
            self._my_location_type = "W/VE" if info.name in ["United States", "Canada"] else "DX"
            print(f"Logger location type determined as: {self._my_location_type}")

    def apply_annotations(self):
        if self.qsos_df.empty:
            print("No QSOs loaded. Cannot apply annotations.")
            return

        try:
            print("Applying Run/S&P annotation...")
            self.qsos_df = process_contest_log_for_run_s_p(self.qsos_df)
            print("Run/S&P annotation complete.")
        except Exception as e:
            print(f"Error during Run/S&P annotation: {e}. Skipping.")

        try:
            print("Applying Universal DXCC/Zone lookup...")
            self.qsos_df = process_dataframe_for_cty_data(self.qsos_df)
            print("Universal DXCC/Zone lookup complete.")
        except Exception as e:
            print(f"Error during Universal DXCC/Zone lookup: {e}. Skipping.")
        
        self.apply_contest_specific_annotations()
        
        try:
            self.metadata['OperatingTime'] = self._calculate_operating_time()
        except Exception as e:
            print(f"Error during on-time calculation: {e}. Skipping.")

    def apply_contest_specific_annotations(self):
        print("Applying contest-specific annotations (Multipliers & Scoring)...")
        
        resolver_name = self.contest_definition.custom_multiplier_resolver
        if resolver_name:
            try:
                resolver_module = importlib.import_module(f"contest_tools.contest_specific_annotations.{resolver_name}")
                self.qsos_df = resolver_module.resolve_multipliers(self.qsos_df, self._my_location_type)
                print(f"Successfully applied '{resolver_name}' multiplier resolver.")
            except Exception as e:
                print(f"Warning: Could not run '{resolver_name}' multiplier resolver: {e}")

        multiplier_rules = self.contest_definition.multiplier_rules
        if multiplier_rules:
            print("Calculating contest multipliers...")
            for rule in multiplier_rules:
                applies_to = rule.get('applies_to')
                if applies_to and self._my_location_type and applies_to != self._my_location_type:
                    continue

                dest_col = rule.get('value_column')
                dest_name_col = rule.get('name_column')
                source = rule.get('source')
                
                if not dest_col: continue

                if source == 'dxcc':
                    # --- New logic to exclude W/VE from DXCC multipliers ---
                    temp_mult_col = self.qsos_df['DXCCPfx'].copy()
                    is_w_ve_qso = self.qsos_df['DXCCName'].isin(['United States', 'Canada'])
                    temp_mult_col[is_w_ve_qso] = pd.NA
                    self.qsos_df[dest_col] = temp_mult_col
                    
                    if dest_name_col:
                        temp_name_col = self.qsos_df['DXCCName'].copy()
                        temp_name_col[is_w_ve_qso] = pd.NA
                        self.qsos_df[dest_name_col] = temp_name_col
                
                elif source == 'wae_dxcc':
                    self.qsos_df[dest_col] = self.qsos_df['WAEPfx'].where(self.qsos_df['WAEPfx'].notna() & (self.qsos_df['WAEPfx'] != ''), self.qsos_df['DXCCPfx'])
                    if dest_name_col:
                        self.qsos_df[dest_name_col] = self.qsos_df['WAEName'].where(self.qsos_df['WAEName'].notna() & (self.qsos_df['WAEName'] != ''), self.qsos_df['DXCCName'])

                elif 'source_column' in rule:
                    source_col = rule.get('source_column')
                    if source_col in self.qsos_df.columns:
                        self.qsos_df[dest_col] = self.qsos_df[source_col]
                    else:
                        print(f"Warning: Source column '{source_col}' not found for multiplier '{rule.get('name')}'.")
                
                elif source == 'calculation_module':
                    module_name = rule.get('module_name')
                    function_name = rule.get('function_name')
                    if not module_name or not function_name:
                        print(f"Warning: 'module_name' or 'function_name' not specified for multiplier '{rule.get('name')}'.")
                        continue
                    try:
                        calc_module = importlib.import_module(f"contest_tools.contest_specific_annotations.{module_name}")
                        calc_function = getattr(calc_module, function_name)
                        self.qsos_df[dest_col] = calc_function(self.qsos_df)
                        print(f"Successfully calculated '{rule.get('name')}' multipliers.")
                    except (ImportError, AttributeError) as e:
                        print(f"Warning: Could not load or run calculation module for multiplier '{rule.get('name')}': {e}")


        # --- Scoring Calculation ---
        my_call = self.metadata.get('MyCall')
        if not my_call:
            print("Warning: 'MyCall' not found in metadata. Cannot calculate QSO points.")
            self.qsos_df['QSOPoints'] = 0
            return
            
        try:
            data_dir = os.environ.get('CONTEST_DATA_DIR').strip().strip('"').strip("'")
            cty_dat_path = os.path.join(data_dir, 'cty.dat')
            cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
            my_call_info = cty_lookup.get_cty_DXCC_WAE(my_call)._asdict()
        except Exception as e:
            print(f"Warning: Could not determine own location for scoring due to CTY error: {e}")
            self.qsos_df['QSOPoints'] = 0
            return

        scoring_module = None
        try:
            module_name_specific = self.contest_name.lower().replace('-', '_')
            scoring_module = importlib.import_module(f"contest_tools.contest_specific_annotations.{module_name_specific}_scoring")
        except ImportError:
            try:
                base_contest_name = self.contest_name.rsplit('-', 1)[0]
                module_name_generic = base_contest_name.lower().replace('-', '_')
                scoring_module = importlib.import_module(f"contest_tools.contest_specific_annotations.{module_name_generic}_scoring")
            except (ImportError, IndexError):
                print(f"Warning: No scoring module found for contest '{self.contest_name}'. Points will be 0.")
                self.qsos_df['QSOPoints'] = 0
                return
        
        try:
            self.qsos_df['QSOPoints'] = scoring_module.calculate_points(self.qsos_df, my_call_info)
            print(f"Scoring complete.")
        except Exception as e:
            print(f"Error during {self.contest_name} scoring: {e}")
            self.qsos_df['QSOPoints'] = 0


    def export_to_csv(self, output_filepath: str):
        if self.qsos_df.empty:
            print(f"No QSOs to export. CSV file '{output_filepath}' will not be created.")
            return

        try:
            df_for_output = self.qsos_df.copy()
            
            if 'Datetime' in df_for_output.columns:
                df_for_output['Datetime'] = df_for_output['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

            df_for_output = df_for_output.reindex(columns=self.contest_definition.default_qso_columns)

            for col in df_for_output.columns:
                if pd.api.types.is_integer_dtype(df_for_output[col]) and isinstance(df_for_output[col].dtype, pd.Int64Dtype):
                    df_for_output[col] = df_for_output[col].astype(object)

            df_for_output.fillna('', inplace=True)

            df_for_output.to_csv(output_filepath, index=False)
            print(f"Processed log saved to: {output_filepath}")
        except Exception as e:
            print(f"Error exporting log to CSV '{output_filepath}': {e}")
            raise

    def get_processed_data(self) -> pd.DataFrame:
        return self.qsos_df

    def get_metadata(self) -> Dict[str, Any]:
        return self.metadata