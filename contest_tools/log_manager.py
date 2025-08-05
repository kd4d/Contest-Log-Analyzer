# Contest Log Analyzer/contest_tools/log_manager.py
#
# Purpose: Defines the LogManager class, which is responsible for orchestrating
#          the loading, processing, and management of one or more ContestLog
#          instances. It serves as the primary entry point for the core
#          analysis engine.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.24-Beta
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
## [0.30.24-Beta] - 2025-08-05
# - No functional changes. Synchronizing version numbers.
## [0.30.14-Beta] - 2025-08-05
### Changed
# - Added `event_id` to each log's metadata.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
import pandas as pd
from .contest_log import ContestLog
import os
import importlib
from datetime import datetime
import logging

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
            logging.info(f"Loading log: {cabrillo_filepath}...")
            
            contest_name = self._get_contest_name_from_header(cabrillo_filepath)
            if not contest_name:
                logging.warning(f"  - Could not determine contest name from file header. Skipping.")
                return

            log = ContestLog(contest_name=contest_name, cabrillo_filepath=cabrillo_filepath)
            log.apply_annotations()
            
            setattr(log, '_log_manager_ref', self)
            
            self.logs.append(log)
            
            logging.info(f"Successfully loaded and processed log for {log.get_metadata().get('MyCall', 'Unknown')}.")

        except Exception as e:
            logging.error(f"Error loading log {cabrillo_filepath}: {e}")

    def finalize_loading(self):
        """
        Should be called after all logs are loaded to perform final,
        cross-log processing steps like creating the master time index and
        saving the processed data files.
        """
        if not self.logs:
            return

        self._create_master_time_index()

        if not self.logs:
            return
            
        root_dir = os.environ.get('CONTEST_LOGS_REPORTS').strip().strip('"').strip("'")
        first_log = self.logs[0]
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest').replace(' ', '_')
        
        df_first_log = first_log.get_processed_data()
        year = df_first_log['Date'].dropna().iloc[0].split('-')[0] if not df_first_log.empty and not df_first_log['Date'].dropna().empty else "UnknownYear"

        event_id = self._get_event_id(first_log)
        for log in self.logs:
            log.metadata['EventID'] = event_id
        
        all_calls = sorted([log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(self.logs)])
        callsign_combo_id = '_'.join(all_calls)

        output_dir = os.path.join(root_dir, 'reports', year, contest_name, event_id, callsign_combo_id)
        os.makedirs(output_dir, exist_ok=True)
            
        for log in self.logs:
            base_filename = os.path.splitext(os.path.basename(log.filepath))[0]
            output_filename = f"{base_filename}_processed.csv"
            output_filepath = os.path.join(output_dir, output_filename)
            log.export_to_csv(output_filepath)


    def _get_event_id(self, log: ContestLog) -> str:
        """
        Determines the unique event ID for a contest.
        """
        resolver_name = log.contest_definition.contest_specific_event_id_resolver
        if resolver_name:
            try:
                resolver_module = importlib.import_module(f"contest_tools.event_resolvers.{resolver_name}")
                first_qso_time = log.get_processed_data()['Datetime'].iloc[0]
                return resolver_module.resolve_event_id(first_qso_time)
            except (ImportError, AttributeError, IndexError) as e:
                logging.warning(f"Could not run event ID resolver '{resolver_name}': {e}")
                return "UnknownEvent"
        else:
            return ""

    def _create_master_time_index(self):
        """
        Creates a master time index from all logs.
        """
        logging.info("Creating master time index...")
        if len(self.logs) < 1:
            return
        
        all_datetimes = pd.concat([log.get_processed_data()['Datetime'] for log in self.logs if not log.get_processed_data().empty])
        if all_datetimes.empty:
            logging.info("  - No QSO data found. Skipping master time index creation.")
            return

        min_time = all_datetimes.min().floor('h')
        max_time = all_datetimes.max().ceil('h')
        self.master_time_index = pd.date_range(start=min_time, end=max_time, freq='h', tz='UTC')
        logging.info("Master time index created.")


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
            logging.warning(f"Could not read contest name from {filepath}: {e}")
        return ""

    def get_logs(self):
        return self.logs