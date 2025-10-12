# contest_tools/log_manager.py
#
# Purpose: Defines the LogManager class, which is responsible for orchestrating
#          the loading, processing, and management of one or more ContestLog
#          instances. It serves as the primary entry point for the core
#          analysis engine.
#
# Author: Gemini AI
# Date: 2025-10-09
# Version: 0.91.5-Beta
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
# [0.91.5-Beta] - 2025-10-09
# - Removed obsolete warning suppression logic for hourly ADIF files and
#   updated the `export_to_adif` call to pass a new context parameter.
# [0.91.3-Beta] - 2025-10-09
# - No functional changes. Synchronizing version number with `__init__.py`
#   for a consolidated bugfix release.
# [0.91.2-Beta] - 2025-10-09
# - Fixed latent bug in _create_master_time_index by changing ceil('h')
#   to floor('h') to prevent creation of an extra, empty hour.
# [0.91.1-Beta] - 2025-10-09
# - Fixed regression by restoring the implicit generic/specific file loading
#   logic as a fallback for definitions that do not use "inherits_from".
# [0.91.0-Beta] - 2025-10-09
# - Added logic to `load_log_batch` to handle the `--wrtc` flag, allowing
#   IARU-HF logs to be scored with a specific WRTC ruleset.
# [0.90.8-Beta] - 2025-10-06
# - Added Excel-compatible text formatting to the `QTC_GRP` column in the WAE QTC CSV export.
# [0.90.7-Beta] - 2025-10-06
# - Added logic to `finalize_loading` to export a `_qtcs.csv` file for WAE logs.
# [0.90.6-Beta] - 2025-10-05
# - Added logic to `finalize_loading` to generate hourly ADIF debug files when `--debug-data` is enabled.
# --- Revision History ---
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

import pandas as pd
from typing import List
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

    def load_log_batch(self, log_filepaths: List[str], root_input_dir: str, cty_specifier: str, wrtc_year: int = None):
        """
        Performs pre-flight validation on a batch of log files, selects a single
        CTY file, and then loads and processes all logs.
        """
        # --- 1. Pre-flight Validation Phase ---
        if len(log_filepaths) > 1:
            logging.info("Performing pre-flight validation on log batch...")
            header_data = []
            for path in log_filepaths:
                call = self._get_callsign_from_header(path)
                
                base_contest = self._get_contest_name_from_header(path)
                if wrtc_year and base_contest == 'IARU-HF':
                    effective_contest = f"WRTC-{wrtc_year}"
                else:
                    effective_contest = base_contest

                date = self._get_first_qso_date_from_log(path)
                
                temp_log = ContestLog(contest_name=effective_contest, cabrillo_filepath=None, root_input_dir=root_input_dir, cty_dat_path=None)
                temp_log.get_processed_data()['Datetime'] = pd.Series([date]) # Minimal data for resolver
                event_id = self._get_event_id(temp_log)
                header_data.append({'call': call, 'contest': effective_contest, 'date': date, 'event_id': event_id})

            first_log_info = header_data[0]
            mismatches = []
            for other_log_info in header_data[1:]:
                if other_log_info['contest'] != first_log_info['contest'] or other_log_info['event_id'] != first_log_info['event_id']:
                    mismatches = header_data
                    break
            
            if mismatches:
                error_lines = ["Log file validation failed: Mismatched contest or event found."]
                for info in mismatches:
                    error_lines.append(f"  - Callsign: {info['call']}, Contest: {info['contest']}, End Date: {info['date'].date()}")
                raise ValueError("\n".join(error_lines))
            
            logging.info("Validation successful.")

        # --- 2. Single CTY File Selection ---
        logging.info("Resolving CTY file for batch...")
        cty_manager = CtyManager(root_input_dir)
        
        if cty_specifier in ['before', 'after']:
            all_dates = [self._get_first_qso_date_from_log(path) for path in log_filepaths]
            target_date = min(all_dates) if cty_specifier == 'before' else max(all_dates)
        else:
            # If a specific filename is given, we need a date for the sync check.
            # We'll just use the first log's date as it's a reasonable proxy.
            target_date = self._get_first_qso_date_from_log(log_filepaths[0])

        # Conditionally update the index based on the determined target date
        cty_manager.sync_index(contest_date=target_date)

        if cty_specifier in ['before', 'after']:
            cty_dat_path, cty_file_info = cty_manager.find_cty_file_by_date(target_date, cty_specifier)
        else:
            cty_dat_path, cty_file_info = cty_manager.find_cty_file_by_name(cty_specifier)
        
        if not cty_dat_path:
            raise FileNotFoundError(f"Could not find a suitable CTY.DAT file for specifier '{cty_specifier}'.")
        logging.info(f"Using CTY file for all logs: {os.path.basename(cty_dat_path)} (Date: {cty_file_info.get('date')})")

        # --- 3. Full Log Loading Phase ---
        for path in log_filepaths:
            try:
                logging.info(f"Loading log: {path}...")
                base_contest_name = self._get_contest_name_from_header(path)
                if not base_contest_name:
                    logging.warning(f"  - Could not determine contest name from file header. Skipping.")
                    continue

                if wrtc_year and base_contest_name == 'IARU-HF':
                    contest_name = f"WRTC-{wrtc_year}"
                    logging.info(f"  --wrtc flag is set. Scoring as '{contest_name}'.")
                else:
                    contest_name = base_contest_name

                log = ContestLog(contest_name=contest_name, cabrillo_filepath=path, root_input_dir=root_input_dir, cty_dat_path=cty_dat_path)
                setattr(log, '_log_manager_ref', self)
                log.apply_annotations()
                self.logs.append(log)
                logging.info(f"Successfully loaded and processed log for {log.get_metadata().get('MyCall', 'Unknown')}.")

            except Exception as e:
                logging.error(f"Error loading log {path}: {e}")

    def finalize_loading(self, root_reports_dir: str, debug_data: bool = False):
        """
        Should be called after all logs are loaded to perform final,
        cross-log processing steps like creating the master time index and
        saving the processed data files.
        """
        if not self.logs:
            return

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

            # --- WAE QTC Data Export ---
            if log.contest_definition.contest_name.startswith('WAE'):
                qtcs_df = getattr(log, 'qtcs_df', pd.DataFrame())
                if not qtcs_df.empty:
                    qtcs_filename = f"{base_filename}_qtcs.csv"
                    qtcs_filepath = os.path.join(output_dir, qtcs_filename)
                    # Format QTC_GRP to prevent Excel from auto-formatting as a date
                    qtcs_df['QTC_GRP'] = '="' + qtcs_df['QTC_GRP'].astype(str) + '"'
                    qtcs_df.to_csv(qtcs_filepath, index=False, na_rep='')
                    logging.info(f"WAE QTC data saved to: {qtcs_filepath}")

            # --- Hourly ADIF Debug File Generation ---
            if debug_data:
                debug_adif_dir = os.path.join(output_dir, "Debug", "adif_files")
                os.makedirs(debug_adif_dir, exist_ok=True)
                logging.info(f"Generating hourly ADIF debug files in: {debug_adif_dir}")

                if log._log_manager_ref and log._log_manager_ref.master_time_index is not None:
                    for hour in log._log_manager_ref.master_time_index:
                        hourly_df = log.qsos_df[log.qsos_df['Datetime'].dt.floor('h') == hour]

                        filename = f"{hour.strftime('%Y-%m-%d_%H00')}.adi"
                        filepath = os.path.join(debug_adif_dir, filename)
                        
                        # Create a lightweight, temporary log object for export
                        temp_log = ContestLog(
                            contest_name=log.contest_name, cabrillo_filepath=None,
                            root_input_dir=log.root_input_dir, cty_dat_path=log.cty_dat_path
                        )
                        temp_log.qsos_df = hourly_df
                        temp_log.metadata = log.metadata
                        
                        # The standard ADIF export handles empty dataframes gracefully
                        temp_log.export_to_adif(filepath, is_debug_hour=True)

            
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
                        return pd.to_datetime(date_str).tz_localize('UTC')
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

    def _get_callsign_from_header(self, filepath: str) -> str:
        """
        Reads just the CALLSIGN: line from a Cabrillo file.
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.upper().startswith('CALLSIGN:'):
                        return line.split(':', 1)[1].strip()
        except Exception as e:
            logging.warning(f"Could not read callsign from {filepath}: {e}")
        return "Unknown"

    def get_logs(self):
        return self.logs