# Contest Log Analyzer/contest_tools/log_manager.py
#
# Purpose: Defines the LogManager class, which handles loading and storing
#          multiple ContestLog instances for comparative analysis.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.23.0-Beta
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

class LogManager:
    """
    Manages a collection of ContestLog instances for analysis.
    """
    def __init__(self):
        self._logs: Dict[str, ContestLog] = {}
        self._expected_contest_name: Optional[str] = None
        self._expected_location_type: Optional[str] = None # 'W/VE' or 'DX'
        
        data_dir = os.environ.get('CONTEST_DATA_DIR')
        if not data_dir:
            raise ValueError("CONTEST_DATA_DIR environment variable not set.")
        cty_dat_path = os.path.join(data_dir.strip().strip('"').strip("'"), 'cty.dat')
        self.cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)


    def _get_station_location_type(self, callsign: str) -> str:
        """Determines if a station is W/VE or DX for ARRL DX Contest purposes."""
        info = self.cty_lookup.get_cty(callsign)
        if info.name in ["United States", "Canada"]:
            return "W/VE"
        return "DX"

    def load_log(self, cabrillo_filepath: str) -> Optional[ContestLog]:
        """
        Loads a Cabrillo file, creates a ContestLog instance, applies all
        annotations, exports a processed CSV, and stores the instance.

        Args:
            cabrillo_filepath (str): The path to the Cabrillo log file.

        Returns:
            Optional[ContestLog]: The loaded ContestLog instance, or None if loading fails.
        """
        try:
            print(f"Loading log: {cabrillo_filepath}...")
            # Auto-detect contest name from the file
            contest_name = self._get_contest_name_from_file(cabrillo_filepath)
            
            # --- Contest Name Validation Check ---
            if self._expected_contest_name is None:
                self._expected_contest_name = contest_name
            elif self._expected_contest_name != contest_name:
                raise ValueError(
                    f"Contest name mismatch. Expected '{self._expected_contest_name}' "
                    f"but found '{contest_name}' in {os.path.basename(cabrillo_filepath)}."
                )
            
            log = ContestLog(contest_name=contest_name, cabrillo_filepath=cabrillo_filepath)
            
            # --- ARRL-DX Location Type Validation ---
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
            
            # Export the processed DataFrame to a CSV file
            base_name = os.path.splitext(cabrillo_filepath)[0]
            output_csv_path = f"{base_name}_processed.csv"
            log.export_to_csv(output_csv_path)
            
            callsign_key = log.get_metadata().get('MyCall', os.path.basename(cabrillo_filepath))
            self._logs[callsign_key] = log
            print(f"Successfully loaded and processed log for {callsign_key}.")
            return log
        except (ValueError, FileNotFoundError, KeyError, IOError) as e:
            print(f"Error loading log {cabrillo_filepath}: {e}")
            return None

    def get_log(self, callsign: str) -> Optional[ContestLog]:
        """Retrieves a loaded log by its callsign."""
        return self._logs.get(callsign)

    def get_all_logs(self) -> List[ContestLog]:
        """Returns a list of all loaded ContestLog instances."""
        return list(self._logs.values())

    @staticmethod
    def _get_contest_name_from_file(filepath: str) -> str:
        """Quickly scans a Cabrillo file to find the CONTEST header."""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.upper().strip().startswith('CONTEST:'):
                    return line[len('CONTEST:'):].strip()
        raise ValueError(f"Could not find a 'CONTEST:' header in {filepath}")