# Contest Log Analyzer/contest_tools/reports/html_qso_comparison.py
#
# Purpose: Generates a comprehensive HTML report comparing QSO counts,
#          broken down by band and operating style (Run/S&P/Unknown),
#          for multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-31
# Version: 0.56.5-Beta
#
# --- Revision History ---
# ## [0.56.5-Beta] - 2025-08-31
# ### Fixed
# - Updated band sorting logic to use the refactored _HAM_BANDS
#   variable from the ContestLog class, fixing an AttributeError.
# ## [0.51.6-Beta] - 2025-08-26
# ### Changed
# - Refactored width calculation to apply a single min-width to the
#   table's container div, ensuring all tables have a uniform width.
# ## [0.51.5-Beta] - 2025-08-26
# ### Changed
# - Refactored width calculation to use the "All Bands" table as a
#   template, ensuring all per-band tables have a consistent width.
# ## [0.51.4-Beta] - 2025-08-26
# ### Changed
# - Implemented logic to pre-calculate column widths and apply them as
#   inline styles, ensuring all tables in the report have a uniform width.
# ## [0.51.3-Beta] - 2025-08-26
# ### Added
# - Added an "All Bands" summary table to the report.
# ### Changed
# - Updated HTML template to center the tables on the page.
# ## [0.51.2-Beta] - 2025-08-26
# ### Changed
# - Refactored report to be a multi-log comparison only, removing all
#   single-log support and fixing a TypeError.
# ## [0.51.1-Beta] - 2025-08-26
# ### Changed
# - Changed report_type to 'html' to save output to the correct directory.
# - Updated HTML template to use dynamic table sizing.
# - Modified single-log report to use the consistent, nine-column format.
# ## [0.51.0-Beta] - 2025-08-26
# - Updated version number to align with project standards.
# ## [1.0.0-Beta] - 2025-08-25
# - Initial release of the HTML QSO Comparison report.
#
import pandas as pd
import os
from typing import List, Dict, Any

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, save_debug_data

class Report(ContestReport):
    report_id: str = "html_qso_comparison"
    report_name: str = "HTML QSO Comparison Report"
    report_type: str = "html" # Saves to the 'html' subdirectory
    supports_single = False
    supports_multi = True
    supports_pairwise = False

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Main controller for generating the HTML QSO comparison report.
        """
        if len(self.logs) < 2:
            return f"Report '{self.report_name}' requires at least two logs. Skipping."
        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        aggregated_data = self._aggregate_data(self.logs)

        if not aggregated_data:
            return "No data available to generate the report."
        if kwargs.get("debug_data", False):
            debug_filename = f"{self.report_id}_{'_vs_'.join(all_calls)}_debug.txt"
            save_debug_data(True, output_path, aggregated_data, debug_filename)
            
        html_content = self._generate_html(aggregated_data, self.logs)
        
        filename = f"{self.report_id}_{'_vs_'.join(all_calls)}.html"
        filepath = os.path.join(output_path, filename)
        create_output_directory(output_path)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return f"HTML QSO comparison report saved to:\n  - {filepath}"

    def _get_run_sp_unk_counts(self, df: pd.DataFrame) -> Dict[str, int]:
        """Helper to get a dictionary of Run/S&P/Unknown counts from a DataFrame."""
        if df.empty:
            return {'run': 0, 'sp': 0, 'unk': 0}
        
        counts = df['Run'].value_counts().to_dict()
        return {
            'run': counts.get('Run', 0),
            'sp': counts.get('S&P', 0),
            'unk': counts.get('Unknown', 0)
        }

    def _aggregate_data(self, logs: List[ContestLog]) -> Dict[str, Any]:
        """
        Aggregates all necessary data for multi-log reports.
        """
        all_data = {}
        all_calls = [log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(logs)]
        
        all_dfs = [get_valid_dataframe(log, False) for log in logs]
        all_bands_in_logs = pd.concat([df['Band'] for df in all_dfs if not df.empty]).dropna().unique()
        canonical_band_order = [band[1] for band in ContestLog._HAM_BANDS]
        sorted_bands = sorted(list(all_bands_in_logs), key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)

        # --- Calculate Per-Band Data ---
        for band in sorted_bands:
            band_data = {}
            calls_on_band = {call: set(df[df['Band'] == band]['Call']) for call, df in zip(all_calls, all_dfs)}
            
            for i, log in enumerate(logs):
                call = all_calls[i]
                df_band = all_dfs[i][all_dfs[i]['Band'] == band]
                
                other_calls_on_band = set()
                for other_call in all_calls:
                    if other_call != call:
                        other_calls_on_band.update(calls_on_band.get(other_call, set()))
                
                unique_calls = calls_on_band[call] - other_calls_on_band
                common_calls = calls_on_band[call].intersection(other_calls_on_band)

                df_unique = df_band[df_band['Call'].isin(unique_calls)]
                df_common = df_band[df_band['Call'].isin(common_calls)]
                
                unique_counts = self._get_run_sp_unk_counts(df_unique)
                common_counts = self._get_run_sp_unk_counts(df_common)

                band_data[call] = {
                    'total': len(df_band),
                    'unique': len(df_unique),
                    'common': len(df_common),
                    'run_unique': unique_counts['run'],
                    'sp_unique': unique_counts['sp'],
                    'unk_unique': unique_counts['unk'],
                    'run_common': common_counts['run'],
                    'sp_common': common_counts['sp'],
                    'unk_common': common_counts['unk'],
                }
            
            all_data[band] = band_data
        
        # --- Calculate "All Bands" Summary ---
        if len(sorted_bands) > 1:
            all_bands_summary = {}
            for call in all_calls:
                all_bands_summary[call] = {
                    'total': sum(all_data[band][call]['total'] for band in sorted_bands),
                    'unique': sum(all_data[band][call]['unique'] for band in sorted_bands),
                    'common': sum(all_data[band][call]['common'] for band in sorted_bands),
                    'run_unique': sum(all_data[band][call]['run_unique'] for band in sorted_bands),
                    'sp_unique': sum(all_data[band][call]['sp_unique'] for band in sorted_bands),
                    'unk_unique': sum(all_data[band][call]['unk_unique'] for band in sorted_bands),
                    'run_common': sum(all_data[band][call]['run_common'] for band in sorted_bands),
                    'sp_common': sum(all_data[band][call]['sp_common'] for band in sorted_bands),
                    'unk_common': sum(all_data[band][call]['unk_common'] for band in sorted_bands),
                }
            all_data["All Bands"] = all_bands_summary
        
        return all_data

    def _calculate_total_width(self, all_bands_data: Dict, all_calls: List[str]) -> int:
        """
        Calculates the total character width of the widest possible table.
        """
        col_keys = [
            'total', 'unique', 'common', 'run_unique', 'sp_unique',
            'unk_unique', 'run_common', 'sp_common', 'unk_common'
        ]
        widths = {
            'call': max(len(call) for call in all_calls) if all_calls else 4,
            'total': 5, 'unique': 6, 'common': 6,
            'run_unique': 3, 'sp_unique': 3, 'unk_unique': 3,
            'run_common': 3, 'sp_common': 3, 'unk_common': 3
        }

        for call, data in all_bands_data.items():
            for key in col_keys:
                widths[key] = max(widths[key], len(f"{data.get(key, 0):,}"))
        
        # Sum of all column widths + padding + borders
        total_width = sum(widths.values()) + (len(widths) * 2) + len(widths)
        return total_width

    def _generate_html(self, aggregated_data: Dict, logs: List[ContestLog]) -> str:
        """
        Generates the final HTML string from the aggregated data.
        """
        all_calls = [log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(logs)]
        
        is_multi_band = "All Bands" in aggregated_data
        total_table_width_ch = 0
        if is_multi_band:
            total_table_width_ch = self._calculate_total_width(aggregated_data["All Bands"], all_calls)

        report_order = ["All Bands"] + sorted(
            [b for b in aggregated_data.keys() if b != "All Bands"],
            key=lambda b: [band[1] for band in ContestLog._HAM_BANDS].index(b) if b in [band[1] for band in ContestLog._HAM_BANDS] else -1
        )

        all_tables_html = ""
        for band in report_order:
            if band not in aggregated_data: continue
            band_data = aggregated_data[band]
            
            table_rows_html = ""
            for call in all_calls:
                data = band_data.get(call, {})
                if not data or data.get('total', 0) == 0: continue

                table_rows_html += f"""
                <tr class="border-b border-gray-400">
                    <td class="p-3 text-left font-medium border-r-2 border-r-gray-500 whitespace-nowrap">{call}</td>
                    <td class="p-3 text-right border-r border-gray-400">{data.get('total', 0):,}</td>
                    <td class="p-3 text-right border-r border-gray-400">{data.get('unique', 0):,}</td>
                    <td class="p-3 text-right border-r-2 border-r-gray-500">{data.get('common', 0):,}</td>
                    <td class="p-3 text-right border-r border-gray-400">{data.get('run_unique', 0):,}</td>
                    <td class="p-3 text-right border-r border-gray-400">{data.get('sp_unique', 0):,}</td>
                    <td class="p-3 text-right border-r-2 border-r-gray-500">{data.get('unk_unique', 0):,}</td>
                    <td class="p-3 text-right border-r border-gray-400">{data.get('run_common', 0):,}</td>
                    <td class="p-3 text-right border-r border-gray-400">{data.get('sp_common', 0):,}</td>
                    <td class="p-3 text-right">{data.get('unk_common', 0):,}</td>
                </tr>
                """

            if table_rows_html:
                header_html = """
                <thead class="bg-gray-50">
                    <tr>
                        <th rowspan="2" class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r-2 border-r-gray-500"></th>
                        <th rowspan="2" class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">Total</th>
                        <th rowspan="2" class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">Unique</th>
                        <th rowspan="2" class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r-2 border-r-gray-500">Common</th>
                        <th colspan="3" class="p-3 font-semibold text-center border-b border-gray-400 border-r-2 border-r-gray-500 whitespace-nowrap">Unique QSOs</th>
                        <th colspan="3" class="p-3 font-semibold text-center border-b border-gray-400 whitespace-nowrap">Common QSOs</th>
                    </tr>
                    <tr>
                        <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">Run</th>
                        <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">S&P</th>
                        <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r-2 border-r-gray-500">Unk</th>
                        <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">Run</th>
                        <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">S&P</th>
                        <th class="p-3 font-semibold text-center border-b-2 border-gray-500">Unk</th>
                    </tr>
                </thead>
                """
                
                table_style = f'style="min-width: {total_table_width_ch}ch;"' if total_table_width_ch > 0 else ''
                
                all_tables_html += f"""
                <h2 class="text-xl font-semibold text-gray-700 mt-8 mb-4">--- {band} ---</h2>
                <div class="inline-block" {table_style}>
                    <div class="overflow-hidden rounded-lg border-2 border-gray-500">
                        <table class="w-full text-sm">
                            {header_html}
                            <tbody class="bg-white">
                                {table_rows_html}
                            </tbody>
                        </table>
                    </div>
                </div>
                """
        
        first_log = logs[0]
        metadata = first_log.get_metadata()
        df_first_log = get_valid_dataframe(first_log)
        year = df_first_log['Date'].dropna().iloc[0].split('-')[0] if not df_first_log.empty and not df_first_log['Date'].dropna().empty else "----"
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        
        title_line1 = self.report_name
        title_line2 = f"{year} {event_id} {contest_name}".strip()
        title_line3 = " vs ".join(all_calls)

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_line1}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style> body {{ font-family: 'Inter', sans-serif; }} </style>
</head>
<body class="bg-gray-100 p-4 sm:p-8">
    <div class="max-w-7xl mx-auto bg-white p-6 rounded-lg shadow-md">
        <div class="text-center">
            <h1 class="text-2xl font-bold text-gray-800">{title_line1}</h1>
            <p class="text-lg text-gray-600">{title_line2}</p>
            <p class="text-md text-gray-500">{title_line3}</p>
        </div>
        <div class="mt-8 flex justify-center">
            <div>
                {all_tables_html}
            </div>
        </div>
    </div>
</body>
</html>
        """