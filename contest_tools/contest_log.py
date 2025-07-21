# Contest Log Analyzer/contest_tools/contest_log.py
#
# Purpose: Defines the ContestLog class, which manages the ingestion, processing,
#          and analysis of Cabrillo log data. It orchestrates the parsing,
#          data cleaning, and calculation of various contest metrics.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-21
# Version: 0.10.0-Beta
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

## [0.10.0-Beta] - 2025-07-21
# - Refactored to integrate with the new LogManager and reports packages.
# - Renamed `apply_generic_annotations` to `apply_annotations`.

### Changed
# - (None)

### Fixed
# - (None)

### Removed
# - (None)

import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, Set, Tuple
import os
import re
import json

# Relative imports from within the contest_tools package
from .cabrillo_parser import parse_cabrillo_file
from .contest_definitions import ContestDefinition
from .core_annotations import process_dataframe_for_cty_data, process_contest_log_for_run_s_p


class ContestLog:
    """
    High-level broker class to manage a single amateur radio contest log.
    It orchestrates Cabrillo file ingestion, data cleaning, annotation (Run/S&P, DXCC),
    and prepares the data for analysis and export.
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
        """
        Determines the amateur radio band from a given frequency in kHz.
        """
        if pd.isna(frequency_khz):
            return 'Invalid'
        frequency_int = int(frequency_khz)
        for band_range, band_name in ContestLog._HF_BANDS:
            if band_range[0] <= frequency_int <= band_range[1]:
                return band_name
        return 'Invalid'

    def __init__(self, contest_name: str, cabrillo_filepath: Optional[str] = None):
        """
        Initializes a ContestLog instance.
        """
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
        """
        Internal method to parse a Cabrillo file and populate the DataFrame.
        """
        raw_df, metadata = parse_cabrillo_file(cabrillo_filepath, self.contest_definition)
        self.metadata.update(metadata)

        if raw_df.empty:
            self.qsos_df = pd.DataFrame(columns=self.contest_definition.default_qso_columns)
            return

        # Perform data type conversions and derive essential fields
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

        # Derive helper fields
        raw_df['Band'] = raw_df['Frequency'].apply(self._derive_band_from_frequency)
        raw_df['Date'] = raw_df['Datetime'].dt.strftime('%Y-%m-%d')
        raw_df['Hour'] = raw_df['Datetime'].dt.strftime('%H')

        # Clean up key string columns
        for col in ['MyCallRaw', 'Call', 'Mode']:
             if col in raw_df.columns:
                raw_df[col.replace('Raw','')] = raw_df[col].fillna('').astype(str).str.upper()

        # Drop raw columns
        raw_df.drop(columns=['FrequencyRaw', 'DateRaw', 'TimeRaw', 'MyCallRaw'], inplace=True, errors='ignore')

        # Final reindex to ensure all default columns exist
        self.qsos_df = raw_df.reindex(columns=self.contest_definition.default_qso_columns)
        
        # Dupe Checking
        self._check_dupes()

    def _check_dupes(self):
        """
        Identifies and flags duplicate QSOs in the DataFrame.
        """
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
        """
        Applies all generic annotations (Run/S&P, DXCC) to the log DataFrame.
        """
        if self.qsos_df.empty:
            print("No QSOs loaded. Cannot apply annotations.")
            return

        # Apply Run/S&P annotation
        try:
            print("Applying Run/S&P annotation...")
            self.qsos_df = process_contest_log_for_run_s_p(self.qsos_df)
            print("Run/S&P annotation complete.")
        except Exception as e:
            print(f"Error during Run/S&P annotation: {e}. Skipping.")
            if 'Run' not in self.qsos_df.columns:
                self.qsos_df['Run'] = pd.NA

        # Apply DXCC/Zone lookup annotation
        try:
            print("Applying DXCC/Zone lookup annotation...")
            self.qsos_df = process_dataframe_for_cty_data(self.qsos_df)
            print("DXCC/Zone lookup annotation complete.")
        except Exception as e:
            print(f"Error during DXCC/Zone lookup: {e}. Skipping.")
            cty_cols = ['DXCCName', 'DXCCPfx', 'CQZone', 'ITUZone', 'Continent', 'WAEName', 'WAEPfx', 'Lat', 'Lon', 'Tzone']
            for col in cty_cols:
                if col not in self.qsos_df.columns:
                    self.qsos_df[col] = pd.NA

    def export_to_csv(self, output_filepath: str):
        """
        Exports the current state of the ContestLog's DataFrame to a CSV file.
        """
        if self.qsos_df.empty:
            print(f"No QSOs to export. CSV file '{output_filepath}' will not be created.")
            return

        try:
            df_for_output = self.qsos_df.copy()
            
            # Format Datetime for clean CSV output
            if 'Datetime' in df_for_output.columns:
                df_for_output['Datetime'] = df_for_output['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

            # Ensure final column order and fill NA
            df_for_output = df_for_output.reindex(columns=self.contest_definition.default_qso_columns)

            # FIX: Before filling NA, convert Int64 columns to a type that allows empty strings (object)
            for col in df_for_output.columns:
                if pd.api.types.is_integer_dtype(df_for_output[col]) and isinstance(df_for_output[col].dtype, pd.Int64Dtype):
                    df_for_output[col] = df_for_output[col].astype(object)

            # Now, this fillna operation will succeed
            df_for_output.fillna('', inplace=True)

            df_for_output.to_csv(output_filepath, index=False)
            print(f"Processed log saved to: {output_filepath}")
        except Exception as e:
            print(f"Error exporting log to CSV '{output_filepath}': {e}")
            raise

    def get_processed_data(self) -> pd.DataFrame:
        """
        Returns the internally stored DataFrame of processed QSOs.
        """
        return self.qsos_df

    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns the extracted log header metadata.
        """
        return self.metadata
