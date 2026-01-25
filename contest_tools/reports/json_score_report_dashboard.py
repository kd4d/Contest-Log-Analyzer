# contest_tools/reports/json_score_report_dashboard.py
#
# Purpose: Generates a machine-readable JSON artifact of the Score Summary
#          for dashboard consumption. This is a lightweight variant that
#          excludes Points and AVG columns, focusing on Band/Mode/QSOs/Multipliers.
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

import json
import os
import logging
import pandas as pd
from .report_interface import ContestReport
from contest_tools.data_aggregators.score_stats import ScoreStatsAggregator
from contest_tools.utils.json_encoders import NpEncoder
from contest_tools.utils.report_utils import get_valid_dataframe
from contest_tools.utils.callsign_utils import callsign_to_filename_part

logger = logging.getLogger(__name__)

class Report(ContestReport):
    """
    Generates a machine-readable JSON artifact of the Score Summary for dashboard.
    This serves as a high-speed cache for the web dashboard, providing simplified
    score data without Points/AVG columns.
    """
    report_id = 'json_score_report_dashboard'
    report_name = 'JSON Score Report Dashboard Artifact'
    # We use 'text' type so it ends up in the text/ directory alongside readable reports
    report_type = 'text' 
    supports_single = True

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Executes the ScoreStatsAggregator and dumps simplified result to JSON.
        """
        final_report_messages = []

        for log in self.logs:
            metadata = log.get_metadata()
            callsign = metadata.get('MyCall', 'UnknownCall')
            contest_name = metadata.get('ContestName', 'UnknownContest')

            # Check for valid data
            df_full = get_valid_dataframe(log, include_dupes=True)  # Only for Year extraction
            if df_full.empty:
                msg = f"Skipping JSON score report for {callsign}: No QSO data available."
                final_report_messages.append(msg)
                logger.warning(msg)
                continue

            # --- Data Aggregation (DAL) ---
            aggregator = ScoreStatsAggregator([log])
            all_scores = aggregator.get_score_breakdown()
            log_scores = all_scores["logs"].get(callsign)
            
            if not log_scores:
                msg = f"Skipping JSON score report for {callsign}: No score data available."
                final_report_messages.append(msg)
                logger.warning(msg)
                continue

            summary_data = log_scores['summary_data']
            total_summary = log_scores['total_summary']
            final_score = log_scores['final_score']
            
            # Extract year from dataframe
            year = df_full['Date'].iloc[0].split('-')[0] if not df_full.empty and not df_full['Date'].dropna().empty else "----"
            
            # Determine multiplier names (exclude Points and AVG)
            if log.contest_definition.score_formula == 'total_points':
                mult_names = []
            else:
                mult_names = [rule['name'] for rule in log.contest_definition.multiplier_rules]
            
            # Filter summary_data to exclude Points and AVG columns
            filtered_summary_data = []
            for row in summary_data:
                filtered_row = {
                    'Band': row.get('Band', ''),
                    'Mode': row.get('Mode', ''),
                    'QSOs': int(row.get('QSOs', 0) or 0)
                }
                # Add multiplier columns
                for mult_name in mult_names:
                    filtered_row[mult_name] = int(row.get(mult_name, 0) or 0)
                filtered_summary_data.append(filtered_row)
            
            # Filter total_summary similarly
            filtered_total_summary = {
                'Band': total_summary.get('Band', 'TOTAL'),
                'Mode': total_summary.get('Mode', ''),
                'QSOs': int(total_summary.get('QSOs', 0) or 0)
            }
            for mult_name in mult_names:
                filtered_total_summary[mult_name] = int(total_summary.get(mult_name, 0) or 0)
            
            # Build JSON structure
            json_data = {
                'callsign': callsign,
                'contest_name': contest_name,
                'year': year,
                'summary_data': filtered_summary_data,
                'total_summary': filtered_total_summary,
                'final_score': int(final_score),
                'multiplier_names': mult_names
            }
            
            # Prepare filename
            filename = f"{self.report_id}_{callsign_to_filename_part(callsign)}.json"
            final_path = os.path.join(output_path, filename)

            # Serialize to Disk
            try:
                os.makedirs(output_path, exist_ok=True)
                with open(final_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, cls=NpEncoder, indent=2)
                logger.info(f"Generated JSON score report artifact: {final_path}")
                final_report_messages.append(f"JSON score report saved to: {final_path}")
            except Exception as e:
                error_msg = f"Failed to generate JSON score report artifact: {e}"
                logger.error(error_msg)
                final_report_messages.append(error_msg)

        return "\n".join(final_report_messages)
