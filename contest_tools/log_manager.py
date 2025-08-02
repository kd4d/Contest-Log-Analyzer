# Contest Log Analyzer/contest_tools/log_manager.py
#
# Purpose: Defines the LogManager class, which handles loading and storing
#          multiple ContestLog instances for comparative analysis.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.25.0-Beta
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

## [0.25.0-Beta] - 2025-08-01
### Added
# - The LogManager now calculates a master time index for the entire contest
#   period and pre-aligns all time-series data for consistent reporting.

## [0.23.0-Beta] - 2025-08-01
### Added
# - For ARRL-DX contests, the LogManager now validates that all loaded logs
#   are of the same type (either all W/VE or all DX), raising an error on a mismatch.

## [0.22.0-Beta] - 2025-07-31
### Added
# - The LogManager now validates that all loaded logs are for the same
#   contest, raising a ValueError if a mismatch is found.

## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.

## [0.12.0-Beta] - 2025-07-22
### Changed
# - The load_log method now automatically exports a '_processed.csv' file for
#   each log after all annotations are applied.

## [0.10.0-Beta] - 2025-07-21
# - Initial release of the LogManager class.

from typing import Dict, List, Optional
from .contest_log import ContestLog
from .core_annotations import CtyLookup
import os
import pandas as pd
from datetime import timedelta

class LogManager:
    """
    Manages a collection of ContestLog instances for analysis.
    """
    def __init__(self):
        self._logs: Dict[str, ContestLog] = {}
        self._expected_contest_name: Optional[str] = None
        self._expected_location_type: Optional[str] = None # 'W/VE' or 'DX'
        self.master_time_index: Optional[pd.DatetimeIndex] = None
        
        data_dir = os.environ.get('CONTEST_DATA_DIR')
        if not data_dir:
            raise ValueError("CONTEST_DATA_DIR environment variable not set.")
        self.cty_dat_path = os.path.join(data_dir.strip().strip('"').strip("'"), 'cty.dat')
        self.cty_lookup = CtyLookup(cty_dat_path=self.cty_dat_path)


    def _get_station_location_type(self, callsign: str) -> str:
        """Determines if a station is W/VE or DX for ARRL DX Contest purposes."""
        info = self.cty_lookup.get_cty(callsign)
        if info.name in ["United States", "Canada"]:
            return "W/VE"
        return "DX"
        
    def _calculate_master_time_index(self, all_log_paths: List[str]):
        """Calculates the full contest period time index."""
        if not self._logs or self.master_time_index is not None:
            return

        first_log = next(iter(self._logs.values()))
        contest_def = first_log.contest_definition
        period_info = contest_def.contest_period

        if not period_info:
            # Fallback for contests without a defined period
            all_datetimes = []
            for log in self._logs.values():
                all_datetimes.extend(log.get_processed_data()['Datetime'])
            if not all_datetimes:
                return
            start_time = min(all_datetimes).floor('h')
            end_time = max(all_datetimes).ceil('h')
        else:
            # Calculate from contest rules
            first_qso_time = first_log.get_processed_data()['Datetime'].min()
            
            day_map = {'Saturday': 5, 'Sunday': 6, 'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4}
            start_day_of_week = day_map[period_info['start_day']]
            end_day_of_week = day_map[period_info['end_day']]

            # Find the date of the contest's start day
            start_date = first_qso_time.date()
            while start_date.weekday() != start_day_of_week:
                start_date -= timedelta(days=1)
            
            start_time_str = period_info['start_time'].replace(' UTC', '')
            start_time = pd.to_datetime(f"{start_date} {start_time_str}", utc=True)

            # Find the date of the contest's end day
            end_date = start_date
            while end_date.weekday() != end_day_of_week:
                end_date += timedelta(days=1)

            end_time_str = period_info['end_time'].replace(' UTC', '')
            end_time = pd.to_datetime(f"{end_date} {end_time_str}", utc=True)

        self.master_time_index = pd.date_range(start=start_time, end=end_time, freq='h', inclusive='left')

    def load_log(self, cabrillo_filepath: str, all_log_paths: List[str]):
        """
        Loads a Cabrillo file, creates a ContestLog instance, applies all
        annotations, exports a processed CSV, and stores the instance.
        """
        try:
            print(f"Loading log: {cabrillo_filepath}...")
            contest_name = self._get_contest_name_from_file(cabrillo_filepath)
            
            if self._expected_contest_name is None:
                self._expected_contest_name = contest_name
            elif self._expected_contest_name != contest_name:
                raise ValueError(
                    f"Contest name mismatch. Expected '{self._expected_contest_name}' "
                    f"but found '{contest_name}' in {os.path.basename(cabrillo_filepath)}."
                )
            
            log = ContestLog(contest_name=contest_name, cabrillo_filepath=cabrillo_filepath)
            log._log_manager_ref = self # Give log a reference back to the manager
            
            if "ARRL-DX" in contest_name.upper():
                callsign = log.get_metadata().get('MyCall')
                location_type = self._get_station_location_type(callsign)
                
                if self._expected_location_type is None:
                    self._expected_location_type = location_type
                elif self._expected_location_type != location_type:
                    raise ValueError(
                        f"ARRL-DX Log Mismatch. All logs must be of the same type.\n"
                        f"  - Expected station type: {self._expected_location_type}\n"
                        f"  - Found '{location_type}' for call {callsign} in {os.path.basename(cabrillo_filepath)}"
                    )

            log.apply_annotations()
            
            base_name = os.path.splitext(cabrillo_filepath)[0]
            output_csv_path = f"{base_name}_processed.csv"
            log.export_to_csv(output_csv_path)
            
            callsign_key = log.get_metadata().get('MyCall', os.path.basename(cabrillo_filepath))
            self._logs[callsign_key] = log
            print(f"Successfully loaded and processed log for {callsign_key}.")

            # After all logs are loaded, calculate the master index
            if len(self._logs) == len(all_log_paths):
                self._calculate_master_time_index(all_log_paths)

            return log
        except (ValueError, FileNotFoundError, KeyError, IOError) as e:
            print(f"Error loading log {cabrillo_filepath}: {e}")
            return None

    def get_log(self, callsign: str) -> Optional[ContestLog]:
        return self._logs.get(callsign)

    def get_all_logs(self) -> List[ContestLog]:
        return list(self._logs.values())

    @staticmethod
    def _get_contest_name_from_file(filepath: str) -> str:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.upper().strip().startswith('CONTEST:'):
                    return line[len('CONTEST:'):].strip()
        raise ValueError(f"Could not find a 'CONTEST:' header in {filepath}")
