# Contest Log Analyzer/contest_tools/log_manager.py
#
# Purpose: Defines the LogManager class, which is responsible for orchestrating
#          the loading, processing, and management of one or more ContestLog
#          instances. It serves as the primary entry point for the core
#          analysis engine.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-09-29
# Version: 0.89.9-Beta
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
## [0.89.9-Beta] - 2025-09-29
### Changed
# - Updated load_log to handle the new tuple return from CtyManager
#   and log the selected CTY file's date for traceability.
## [0.89.5-Beta] - 2025-09-29
### Changed
# - Modified load_log to accept a cty_specifier and pass the
#   resolved cty.dat path to the ContestLog constructor.
## [0.87.2-Beta] - 2025-09-14
### Fixed
# - Fixed a regression in `_create_master_time_index` by using a
#   periods-based calculation, resolving the 'extra hour' bug in all
#   time-series reports.
## [0.87.1-Beta] - 2025-09-14
### Fixed
# - Fixed a bug in `_create_master_time_index` that created an extra hour
#   in the timeline by subtracting one second from the max time before
#   applying the ceiling function.
## [0.87.0-Beta] - 2025-09-13
### Fixed
# - Fixed a regression by adding a call to the `_pre_calculate_time_series_score`
#   method for each log, ensuring score data is available for reports.
## [0.85.6-Beta] - 2025-09-13
### Fixed
# - Corrected an order-of-operations bug by setting the _log_manager_ref
#   on the ContestLog object *before* calling apply_annotations. This
#   ensures score calculators can access the master time index.
## [0.70.2-Beta] - 2025-09-12
### Fixed
# - Corrected an order-of-operations bug by setting the _log_manager_ref
#   on the ContestLog object *before* calling apply_annotations. This
#   ensures score calculators can access the master time index.
## [0.70.1-Beta] - 2025-09-09
### Changed
# - Refactored methods to accept path variables as parameters instead of
#   reading environment variables directly, in compliance with Principle 15.
## [0.62.2-Beta] - 2025-09-08
### Changed
# - Updated script to read the new CONTEST_REPORTS_DIR environment variable.
## [0.55.5-Beta] - 2025-08-30
### Added
# - Added a hook to the `finalize_loading` method to support a new
#   pluggable, contest-specific ADIF exporter architecture.
## [0.37.0-Beta] - 2025-08-17
### Added
# - Added a conditional call to the new `export_to_adif` method,
#   triggered by a key in the contest's JSON definition file.
## [0.35.10-Beta] - 2025-08-14
### Added
# - Added validation to finalize_loading to ensure all logs are from the
#   same contest and event, raising a ValueError on mismatch.
## [0.31.32-Beta] - 2025-08-10
### Added
# - Added a warning to detect and report if logs from different
#   months/years are loaded in the same session.
## [0.30.24-Beta] - 2025-08-05
# - No functional changes. Synchronizing version numbers.
## [0.30.14-Beta] - 2025-08-05
### Changed
# - Added `event_id` to each log's metadata.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
import pandas as pd
from .contest_log import ContestLog
from .utils.cty_manager import CtyManager
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

    def load_log(self, cabrillo_filepath: str, root_input_dir: str, cty_specifier: str):
        """
        Loads and processes a single Cabrillo log file.
        """
        try:
            logging.info(f"Loading log: {cabrillo_filepath}...")
            
            # --- CTY File Resolution ---
            cty_manager = CtyManager(root_input_dir)
            first_qso_date = self._get_first_qso_date_from_log(cabrillo_filepath)
            
            if cty_specifier in ['before', 'after']:
                cty_dat_path, cty_file_info = cty_manager.find_cty_file_by_date(first_qso_date, cty_specifier)
            else:
                cty_dat_path, cty_file_info = cty_manager.find_cty_file_by_name(cty_specifier)

            if not cty_dat_path:
                raise FileNotFoundError(f"Could not find a suitable CTY.DAT file for specifier '{cty_specifier}' and date '{first_qso_date}'.")
            
            logging.info(f"Using CTY file: {os.path.basename(cty_dat_path)} (Date: {cty_file_info.get('date')})")
            
            contest_name = self._get_contest_name_from_header(cabrillo_filepath)
            if not contest_name:
                logging.warning(f"  - Could not determine contest name from file header. Skipping.")
                return

            log = ContestLog(contest_name=contest_name, cabrillo_filepath=cabrillo_filepath, root_input_dir=root_input_dir, cty_dat_path=cty_dat_path)
            
            # Set the back-reference BEFORE running annotations that might need it.
            setattr(log, '_log_manager_ref', self)
            
            log.apply_annotations()
            
            self.logs.append(log)
            
            logging.info(f"Successfully loaded and processed log for {log.get_metadata().get('MyCall', 'Unknown')}.")

        except Exception as e:
            logging.error(f"Error loading log {cabrillo_filepath}: {e}")

    def finalize_loading(self, root_reports_dir: str):
        """
        Should be called after all logs are loaded to perform final,
        cross-log processing steps like creating the master time index and
        saving the processed data files.
        """
        if not self.logs:
            return
            
        # --- Validation for Multi-Log Runs ---
        if len(self.logs) > 1:
            mismatch_errors = []
            first_log = self.logs[0]

            # 1. Same Contest Check
            first_contest_name = first_log.get_metadata().get('ContestName', 'Unknown')
            for log in self.logs[1:]:
                current_contest_name = log.get_metadata().get('ContestName', 'Unknown')
                if current_contest_name != first_contest_name:
                    msg = (f"  - {log.get_metadata().get('MyCall')}: Incorrect contest '{current_contest_name}' "
                           f"(expected '{first_contest_name}')")
                    mismatch_errors.append(msg)

            # 2. Same Event Check
            first_event_id = self._get_event_id(first_log)
            for log in self.logs[1:]:
                current_event_id = self._get_event_id(log)
                if current_event_id != first_event_id:
                    msg = (f"  - {log.get_metadata().get('MyCall')}: Incorrect event '{current_event_id}' "
                           f"(expected '{first_event_id}')")
                    mismatch_errors.append(msg)
            
            if mismatch_errors:
                error_summary = "Log file validation failed:\n" + "\n".join(mismatch_errors)
                raise ValueError(error_summary)

        self._create_master_time_index()

        # --- Pre-calculate Time-Series Scores ---
        # This must be done after the master time index is created but before
        # any reports are generated.
        logging.info("Pre-calculating time-series scores for all logs...")
        for log in self.logs:
            log._pre_calculate_time_series_score()

        if not self.logs:
            return
            
        # The root directory is now passed in as a parameter.
        root_dir = root_reports_dir
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
            
            # --- CSV Export ---
            output_filename = f"{base_filename}_processed.csv"
            output_filepath = os.path.join(output_dir, output_filename)
            log.export_to_csv(output_filepath)
            
            # --- ADIF Export (if enabled for this contest) ---
            if getattr(log.contest_definition, 'enable_adif_export', False):
                adif_filename = f"{base_filename}_N1MMADIF.adi"
                adif_filepath = os.path.join(output_dir, adif_filename)
                
                # Use custom exporter if defined, otherwise fall back to generic
                if custom_exporter_name := getattr(log.contest_definition, 'custom_adif_exporter', None):
                    try:
                        exporter_module = importlib.import_module(f"contest_tools.adif_exporters.{custom_exporter_name}")
                        exporter_module.export_log(log, adif_filepath)
                    except Exception as e:
                        logging.error(f"Could not run custom ADIF exporter '{custom_exporter_name}': {e}")
                else:
                    # Fallback to the generic method in ContestLog
                    log.export_to_adif(adif_filepath)


    def _get_event_id(self, log: ContestLog) -> str:
        """
        Determines the unique event ID for a contest.
        """
        resolver_name = log.contest_definition.contest_specific_event_id_resolver
        if resolver_name:
            try:
                # Check if there's any data to get a timestamp from
                if log.get_processed_data().empty or 'Datetime' not in log.get_processed_data().columns:
                    return "NoQSOData"
                
                first_qso_time = log.get_processed_data()['Datetime'].iloc[0]
                if pd.isna(first_qso_time):
                    return "InvalidTime"

                resolver_module = importlib.import_module(f"contest_tools.event_resolvers.{resolver_name}")
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
        if all_datetimes.empty or all_datetimes.isna().all():
            logging.info("  - No valid QSO datetimes found. Skipping master time index creation.")
            return

        min_time = all_datetimes.min().floor('h')
        max_time = all_datetimes.max().floor('h')
        
        # Calculate the number of hourly periods from the actual min/max times
        periods = int((max_time - min_time).total_seconds() / 3600) + 1
        self.master_time_index = pd.date_range(start=min_time, periods=periods, freq='h', tz='UTC')
        logging.info("Master time index created.")


    def _get_first_qso_date_from_log(self, filepath: str) -> pd.Timestamp:
        """Reads the first QSO line to determine the contest date."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.upper().startswith('QSO:'):
                        parts = line.split()
                        date_str = parts[3]
                        return pd.to_datetime(date_str)
        except Exception:
            return pd.Timestamp.now(tz='UTC')
        return pd.Timestamp.now(tz='UTC')

    def _get_contest_name_from_header(self, filepath: str) -> str:
        """
        Reads just the CONTEST: line from a Cabrillo file.
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.upper().startswith('CONTEST:'):
                        return line.split(':', 1)[1].strip()
        except Exception as e:
            logging.warning(f"Could not read contest name from {filepath}: {e}")
        return ""

    def get_logs(self):
        return self.logs