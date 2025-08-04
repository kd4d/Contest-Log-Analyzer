# Contest Log Analyzer/contest_tools/log_manager.py
#
# Purpose: Defines the LogManager class, which is responsible for orchestrating
#          the loading, processing, and management of one or more ContestLog
#          instances. It serves as the primary entry point for the core
#          analysis engine.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.28.12-Beta
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
## [0.28.12-Beta] - 2025-08-04
### Changed
# - Redesigned the time index logic. The manager now only creates the master
#   time index and no longer modifies the log dataframes, fixing the
#   "duplicate labels" bug.
## [0.28.11-Beta] - 2025-08-04
### Changed
# - Reworked the log loading process to pre-align all dataframes to a
#   master time index, fixing bugs in single-log time-series reports.
import pandas as pd
from .contest_log import ContestLog
import os

class LogManager:
    """
    Manages the loading and processing of one or more contest logs.
    """

    def __init__(self):
        self.logs = []
        self.master_time_index = None

    def load_log(self, cabrillo_filepath: str):
        """
        Loads and processes a single Cabrillo log file.
        """
        try:
            print(f"Loading log: {cabrillo_filepath}...")
            
            contest_name = self._get_contest_name_from_header(cabrillo_filepath)
            if not contest_name:
                print(f"  - Error: Could not determine contest name from file header. Skipping.")
                return

            log = ContestLog(contest_name=contest_name, cabrillo_filepath=cabrillo_filepath)
            log.apply_annotations()
            
            setattr(log, '_log_manager_ref', self)
            
            self.logs.append(log)
            
            output_dir = os.path.dirname(cabrillo_filepath)
            base_filename = os.path.splitext(os.path.basename(cabrillo_filepath))[0]
            output_filename = f"{base_filename}_processed.csv"
            output_filepath = os.path.join(output_dir, output_filename)
            log.export_to_csv(output_filepath)

            print(f"Successfully loaded and processed log for {log.get_metadata().get('MyCall', 'Unknown')}.")

        except Exception as e:
            print(f"Error loading log {cabrillo_filepath}: {e}")

    def finalize_loading(self):
        """
        Should be called after all logs are loaded to perform final,
        cross-log processing steps like creating the master time index.
        """
        if not self.logs:
            return
        self._create_master_time_index()

    def _create_master_time_index(self):
        """
        Creates a master time index from all logs.
        """
        print("Creating master time index...")
        if len(self.logs) < 1:
            return
        
        all_datetimes = pd.concat([log.get_processed_data()['Datetime'] for log in self.logs if not log.get_processed_data().empty])
        if all_datetimes.empty:
            print("  - No QSO data found. Skipping master time index creation.")
            return

        min_time = all_datetimes.min().floor('h')
        max_time = all_datetimes.max().ceil('h')
        self.master_time_index = pd.date_range(start=min_time, end=max_time, freq='h', tz='UTC')
        print("Master time index created.")


    def _get_contest_name_from_header(self, filepath: str) -> str:
        """
        Reads just the CONTEST: line from a Cabrillo file.
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.startswith('CONTEST:'):
                        return line.split(':', 1)[1].strip()
        except Exception as e:
            print(f"  - Could not read contest name from {filepath}: {e}")
        return ""

    def get_logs(self):
        return self.logs