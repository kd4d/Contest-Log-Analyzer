# contest_tools/reports/text_score_report.py
#
# Purpose: A text report that generates a detailed score summary for each
#          log, broken down by band.
#
# Author: Gemini AI
# Date: 2025-12-20
# Version: 0.130.0-Beta
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
#
# --- Revision History ---
# [0.130.0-Beta] - 2025-12-20
# - Refactored to use `format_text_header` for standardized 3-line titles.
# - Integrated `get_cty_metadata` for provenance tracking.
# [0.125.0-Beta] - 2025-12-17
# - Updated import to use contest_tools.utils.pivot_utils for calculate_multiplier_pivot.
# [0.116.0-Beta] - 2025-12-15
# - Removed usage of get_copyright_footer.
# [0.115.3-Beta] - 2025-12-15
# - Added standardized copyright footer.
# [0.92.0-Beta] - 2025-12-06
# - Refactored score summary to use a hierarchical layout (Band -> Mode).
# - Implemented strict multiplier counts per mode row, with an 'ALL' summary row
#   showing the band total union.
# [0.91.0-Beta] - 2025-10-09
# - Added support for the 'once_per_band_no_mode' multiplier totaling
#   method to correctly calculate WRTC scores.
# [0.90.3-Beta] - 2025-10-05
# - Corrected scoring logic to sum the `QSOPoints` column instead of
#   counting all non-dupe QSOs, bringing it into alignment with the
#   correct logic in `wae_calculator.py`.
# [0.90.0-Beta] - 2025-10-01
# - Set new baseline version for release.
from typing import List, Dict, Set, Tuple
import pandas as pd
import os
import re
import json
import logging
import hashlib
from ..contest_log import ContestLog
from ..contest_definitions import ContestDefinition
from .report_interface import ContestReport
from ..utils.pivot_utils import calculate_multiplier_pivot
from ._report_utils import format_text_header, get_cty_metadata

class Report(ContestReport):
    """
    Generates a detailed score summary report for each log.
    """
    report_id: str = "score_report"
    report_name: str = "Score Summary"
    report_type: str = "text"
    supports_single = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        final_report_messages = []

        for log in self.logs:
            metadata = log.get_metadata()
            df_full = log.get_processed_data()

            callsign = metadata.get('MyCall', 'UnknownCall')
            contest_name = metadata.get('ContestName', 'UnknownContest')

            if df_full.empty:
                msg = f"Skipping score report for {callsign}: No QSO data available."
                final_report_messages.append(msg)
                continue

            # --- All calculations are now performed in a single, authoritative function ---
            summary_data, total_summary, final_score = self._calculate_all_scores(log, output_path, **kwargs)
            
            # --- Formatting ---
            if log.contest_definition.score_formula == 'total_points':
                mult_names = []
            else:
                mult_names = [rule['name'] for rule in log.contest_definition.multiplier_rules]
            
            col_order = ['Band', 'Mode', 'QSOs'] + mult_names + ['Points', 'AVG']
            col_widths = {key: len(str(key)) for key in col_order}

            all_data_for_width = summary_data + [total_summary]
            for row in all_data_for_width:
                for key, value in row.items():
                    if key in col_widths:
                        val_len = len(f"{value:,.0f}") if isinstance(value, (int, float)) and key not in ['AVG'] else len(str(value))
                        if isinstance(value, float) and key == 'AVG':
                            val_len = len(f"{value:.2f}")
                        
                        col_widths[key] = max(col_widths.get(key, 0), val_len)

            year = df_full['Date'].iloc[0].split('-')[0] if not df_full.empty and not df_full['Date'].dropna().empty else "----"
            
            header_parts = [f"{name:>{col_widths[name]}}" for name in col_order]
            header = "  ".join(header_parts)
            table_width = len(header)
            separator = "-" * table_width
            
            # --- New 3-Line Header ---
            title_lines = [
                f"--- {self.report_name} ---",
                f"{year} {contest_name} - {callsign}",
                "All Bands" # Score report is always a summary of all bands
            ]
            
            meta_lines = [
                "Contest Log Analytics by KD4D",
                get_cty_metadata([log])
            ]
            
            report_lines = []
            # Ensure table is at least wide enough for header
            min_header_width = max(len(l) for l in title_lines) + max(len(l) for l in meta_lines) + 5
            final_width = max(table_width, min_header_width)
            
            report_lines.extend(format_text_header(final_width, title_lines, meta_lines))
            
            report_lines.append("")
            on_time_str = metadata.get('OperatingTime')
            if on_time_str:
                report_lines.append(f"Operating Time: {on_time_str}")
            report_lines.append("")
            
            report_lines.append(header)
            report_lines.append(separator)

            # Data is already sorted hierarchically by _calculate_all_scores

            previous_band = None
            for item in summary_data:
                # Add separator between band groups
                current_band = item.get('Band')
                if previous_band is not None and current_band != previous_band:
                     report_lines.append(separator)
                previous_band = current_band

                data_parts = [f"{str(item.get(name, '')):{'>' if name != 'Band' else '<'}{col_widths[name]}}" for name in ['Band', 'Mode']]
                data_parts.append(f"{item.get('QSOs', 0):>{col_widths['QSOs']},.0f}")
                data_parts.extend([f"{item.get(name, 0):>{col_widths[name]},.0f}" for name in mult_names])
                data_parts.extend([
                    f"{item.get('Points', 0):>{col_widths['Points']},.0f}",
                    f"{item.get('AVG', 0):>{col_widths['AVG']}.2f}"
                ])
                report_lines.append("  ".join(data_parts))
            
            report_lines.append(separator)
            
            total_parts = [f"{str(total_summary.get(name, '')):{'>' if name != 'Band' else '<'}{col_widths[name]}}" for name in ['Band', 'Mode']]
            total_parts.append(f"{total_summary.get('QSOs', 0):>{col_widths['QSOs']},.0f}")
            total_parts.extend([f"{total_summary.get(name, 0):>{col_widths[name]},.0f}" for name in mult_names])
            total_parts.extend([
                f"{total_summary.get('Points', 0):>{col_widths['Points']},.0f}",
                f"{total_summary.get('AVG', 0):>{col_widths['AVG']}.2f}"
            ])
            report_lines.append("  ".join(total_parts))
            
            report_lines.append("=" * table_width)
            score_text = f"TOTAL SCORE : {final_score:,.0f}"
            report_lines.append(score_text.rjust(table_width))

            self._add_diagnostic_sections(report_lines, df_full, log)

            report_content = "\n".join(report_lines) + "\n"
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)

    def _add_diagnostic_sections(self, report_lines: List[str], df: pd.DataFrame, log: ContestLog):
        """Appends sections for 'Unknown' and 'Unassigned' multipliers."""
        if df.empty:
            return

        contest_def = log.contest_definition
        if getattr(contest_def, 'suppress_blank_mult_warnings', False):
            return
        
        log_location_type = getattr(log, '_my_location_type', None)
        exclusive_groups = contest_def.mutually_exclusive_mults

        for rule in contest_def.multiplier_rules:
            applies_to = rule.get('applies_to')
            if applies_to and log_location_type and applies_to != log_location_type:
                continue

            mult_name = rule['name']
            mult_col = rule['value_column']

            if mult_col not in df.columns:
                continue

            # --- Check for "Unknown" Multipliers ---
            unknown_df = df[df[mult_col] == 'Unknown']
            unknown_calls = sorted(list(unknown_df['Call'].unique()))
            if unknown_calls:
                report_lines.append("\n" + "-" * 40)
                report_lines.append(f"Callsigns with 'Unknown' {mult_name}:")
                report_lines.append("-" * 40)
                for i in range(0, len(unknown_calls), 5):
                    line_calls = unknown_calls[i:i+5]
                    report_lines.append("  ".join([f"{call:<12}" for call in line_calls]))

            # --- Check for "Unassigned" (NaN) Multipliers ---
            df_to_check = df
            if getattr(contest_def, 'is_naqp_ruleset', False):
                df_to_check = df[(df['Continent'] == 'NA') | (df['DXCCPfx'] == 'KH6')]
            
            unassigned_df = df_to_check[df_to_check[mult_col].isna()]
            
            # Filter out intentional blanks for mutually exclusive mults
            for group in exclusive_groups:
                if mult_col in group:
                    partner_cols = [p for p in group if p != mult_col and p in df.columns]
                    if partner_cols:
                        indices_to_check = unassigned_df.index
                        partner_values_exist = df.loc[indices_to_check, partner_cols].notna().any(axis=1)
                        unassigned_df = unassigned_df.loc[~partner_values_exist]
            
            unassigned_calls = sorted(list(unassigned_df['Call'].unique()))
            if unassigned_calls:
                report_lines.append("\n" + "-" * 40)
                report_lines.append(f"Callsigns with Unassigned {mult_name}:")
                report_lines.append("-" * 40)
                for i in range(0, len(unassigned_calls), 5):
                    line_calls = unassigned_calls[i:i+5]
                    report_lines.append("  ".join([f"{call:<12}" for call in line_calls]))

    def _calculate_all_scores(self, log: ContestLog, output_path: str, **kwargs) -> Tuple[List[Dict], Dict, int]:
        """
        Performs all score and multiplier calculations for the report.
        This function uses a hierarchical approach (Band -> Mode) for the summary rows,
        calculating strict multiplier counts for each slice, while using standard logic
        for the final total score.
        """
        df_full = log.get_processed_data()
        contest_def = log.contest_definition
        multiplier_rules = contest_def.multiplier_rules
        log_location_type = getattr(log, '_my_location_type', None)
        
        # Start with a DataFrame of non-duplicate QSOs
        df_net = df_full[df_full['Dupe'] == False].copy()
        
        # If the contest rules require it, filter out zero-point QSOs for all counts
        if not contest_def.mults_from_zero_point_qsos:
            df_net = df_net[df_net['QSOPoints'] > 0].copy()
        
        # --- Pre-computation for TOTAL multiplier calculations ---
        per_band_mult_counts = {}
        first_worked_mult_counts = {}
        
        for rule in multiplier_rules:
            mult_col = rule['value_column']
            if mult_col not in df_net.columns: continue

            df_valid_mults = df_net[df_net[mult_col].notna() & (df_net[mult_col] != 'Unknown')]
            
            if rule.get('totaling_method') == 'once_per_log':
                df_sorted = df_valid_mults.sort_values(by='Datetime')
                overall_seen_mults = set()
                new_mults_per_band_mode = {}
                
                band_mode_groups = df_sorted.groupby(['Band', 'Mode'])
                for (band, mode), group_df in band_mode_groups:
                    mults_in_group = set(group_df[mult_col].unique())
                    new_mults = mults_in_group - overall_seen_mults
                    new_mults_per_band_mode[(band, mode)] = len(new_mults)
                    overall_seen_mults.update(new_mults)
                first_worked_mult_counts[mult_col] = new_mults_per_band_mode
            else:
                pivot = calculate_multiplier_pivot(df_valid_mults, mult_col, group_by_call=False)
                per_band_mult_counts[mult_col] = (pivot > 0).sum(axis=0)

        # --- Hierarchical Band/Mode Summary Calculation ---
        summary_data = []
        if not df_net.empty:
            
            # Helper to calculate a summary row for a specific data slice
            def process_slice(slice_df, slice_band, slice_mode):
                row_summary = {'Band': slice_band, 'Mode': slice_mode}
                row_summary['QSOs'] = len(slice_df)
                row_summary['Points'] = slice_df['QSOPoints'].sum()

                for rule in multiplier_rules:
                    m_name = rule['name']
                    m_col = rule['value_column']
                    applies_to = rule.get('applies_to')

                    if applies_to and log_location_type and applies_to != log_location_type:
                        row_summary[m_name] = 0
                        continue
                    
                    if m_col not in slice_df.columns:
                        row_summary[m_name] = 0
                        continue
                    
                    df_slice_valid = slice_df[slice_df[m_col].notna() & (slice_df[m_col] != 'Unknown')]
                    
                    # Calculate strict unique count for this slice.
                    # This satisfies "Strict Count for that mode" and "Union... (Band Total)" for ALL row.
                    row_summary[m_name] = df_slice_valid[m_col].nunique()

                row_summary['AVG'] = (row_summary['Points'] / row_summary['QSOs']) if row_summary['QSOs'] > 0 else 0
                return row_summary

            # Iterate through canonical bands present in the data
            canonical_bands = [b[1] for b in ContestLog._HAM_BANDS]
            present_bands = [b for b in canonical_bands if b in df_net['Band'].unique()]

            for band in present_bands:
                band_df = df_net[df_net['Band'] == band]
                # Sort modes alphabetically for consistent output
                modes_on_band = sorted(band_df['Mode'].unique())

                if len(modes_on_band) > 1:
                    # Create 'ALL' summary row (Union of mults on band)
                    summary_data.append(process_slice(band_df, band, 'ALL'))
                    # Create individual mode rows (Strict count for mode)
                    for mode in modes_on_band:
                        mode_df = band_df[band_df['Mode'] == mode]
                        summary_data.append(process_slice(mode_df, band, mode))
                elif len(modes_on_band) == 1:
                     # Single mode: just create that mode row
                     mode = modes_on_band[0]
                     summary_data.append(process_slice(band_df, band, mode))
            
        # --- TOTAL Summary Calculation ---
        total_summary = {'Band': 'TOTAL', 'Mode': ''}
        total_summary['QSOs'] = df_net.shape[0]
        total_summary['Points'] = df_net['QSOPoints'].sum()

        total_multiplier_count = 0
        for rule in multiplier_rules:
            mult_name = rule['name']
            mult_col = rule['value_column']

            applies_to = rule.get('applies_to')
            if applies_to and log_location_type and applies_to != log_location_type:
                total_summary[mult_name] = 0
                continue
            
            if mult_col in df_net.columns:
                df_valid_mults = df_net[df_net[mult_col].notna() & (df_net[mult_col] != 'Unknown')]

                if rule.get('totaling_method') == 'once_per_log':
                    total_mults_for_rule = df_valid_mults[mult_col].nunique()
                elif rule.get('totaling_method') == 'once_per_mode':
                    mode_mults = df_valid_mults.groupby('Mode')[mult_col].nunique()
                    total_mults_for_rule = mode_mults.sum()
                elif rule.get('totaling_method') == 'once_per_band_no_mode':
                    # New logic for WRTC: Count unique mults per band, ignoring mode.
                    # Then sum those unique-per-band counts.
                    band_mults = df_valid_mults.groupby('Band')[mult_col].nunique()
                    total_mults_for_rule = band_mults.sum()
                else: # Default to sum_by_band
                    total_mults_for_rule = per_band_mult_counts.get(mult_col, pd.Series()).sum()
            
                total_summary[mult_name] = total_mults_for_rule
                total_multiplier_count += total_mults_for_rule
            
        total_summary['AVG'] = (total_summary['Points'] / total_summary['QSOs']) if total_summary['QSOs'] > 0 else 0
        
        # --- Data-driven score calculation ---
        if contest_def.score_formula == 'qsos_times_mults':
            final_score = total_summary['QSOs'] * total_multiplier_count
        elif contest_def.score_formula == 'total_points':
            final_score = total_summary['Points']
        else: # Default to points_times_mults
            final_score = total_summary['Points'] * total_multiplier_count
        
        return summary_data, total_summary, final_score