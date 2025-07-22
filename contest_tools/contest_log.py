# Contest Log Analyzer/contest_tools/contest_log.py
#
# Purpose: Defines the ContestLog class, which manages the ingestion, processing,
#          and analysis of Cabrillo log data. It orchestrates the parsing,
#          data cleaning, and calculation of various contest metrics.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-22
# Version: 0.13.0-Beta
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

## [0.13.0-Beta] - 2025-07-22
### Changed
# - The 'apply_annotations' method now passes the ContestDefinition object
#   to the country data processing function, enabling the use of
#   contest-specific country files.

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

        try:
            self.contest_definition = ContestDefinition.from_json(contest_name)
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to load contest definition for '{contest_name}': {e}")

        if cabrillo_filepath:
            self._ingest_cabrillo_data(cabrillo_filepath)

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
            if 'Run' not in self.qsos_df.columns:
                self.qsos_df['Run'] = pd.NA

        try:
            print("Applying DXCC/Zone lookup annotation...")
            # Pass the contest definition to the lookup function
            self.qsos_df = process_dataframe_for_cty_data(self.qsos_df, self.contest_definition)
            print("DXCC/Zone lookup annotation complete.")
        except Exception as e:
            print(f"Error during DXCC/Zone lookup: {e}. Skipping.")
            cty_cols = ['DXCCName', 'DXCCPfx', 'CQZone', 'ITUZone', 'Continent', 'WAEName', 'WAEPfx', 'Lat', 'Lon', 'Tzone']
            for col in cty_cols:
                if col not in self.qsos_df.columns:
                    self.qsos_df[col] = pd.NA
        
        self.apply_contest_specific_annotations()


    def apply_contest_specific_annotations(self):
        print("Applying contest-specific annotations (Scoring)...")
        
        my_call = self.metadata.get('MyCall')
        if not my_call:
            print("Warning: 'MyCall' not found in metadata. Cannot calculate QSO points.")
            self.qsos_df['QSOPoints'] = 0
            return
            
        try:
            # Determine which country file to use for our own callsign lookup
            country_file_to_use = self.contest_definition.country_file_name
            base_cty_path = os.environ.get('CTY_DAT_PATH').strip().strip('"').strip("'")
            if country_file_to_use:
                base_dir = os.path.dirname(base_cty_path)
                cty_dat_path = os.path.join(base_dir, country_file_to_use)
            else:
                cty_dat_path = base_cty_path

            cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
            my_call_info = cty_lookup.get_cty_DXCC_WAE(my_call)._asdict()
        except Exception as e:
            print(f"Warning: Could not determine own location for scoring due to CTY error: {e}")
            self.qsos_df['QSOPoints'] = 0
            return

        # --- Dynamically load the scoring module with fallback ---
        scoring_module = None
        try:
            module_name_specific = self.contest_name.lower().replace('-', '_')
            scoring_module = importlib.import_module(f"contest_tools.contest_specific_annotations.{module_name_specific}_scoring")
            print(f"Using specific scoring module for {self.contest_name}.")
        except ImportError:
            try:
                base_contest_name = self.contest_name.rsplit('-', 1)[0]
                module_name_generic = base_contest_name.lower().replace('-', '_')
                scoring_module = importlib.import_module(f"contest_tools.contest_specific_annotations.{module_name_generic}_scoring")
                print(f"Using generic scoring module for {self.contest_name} (rules for '{base_contest_name}').")
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
