# Contest Log Analyzer/contest_tools/reports/html_qso_comparison.py
#
# Purpose: Generates a comprehensive HTML report comparing QSO counts,
#          broken down by band and operating style (Run/S&P/Unknown),
#          for one or more logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-26
# Version: 0.51.0-Beta
#
# --- Revision History ---
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
    report_type: str = "chart" # Treated as a visual report
    supports_single = True
    supports_multi = True
    supports_pairwise = False

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Main controller for generating the HTML QSO comparison report(s).
        """
        created_files = []

        # Generate individual reports for each log
        for log in self.logs:
            single_log_files = self._generate_single_log_report(log, output_path, **kwargs)
            created_files.extend(single_log_files)

        # Generate a comparative report if there are multiple logs
        if len(self.logs) > 1:
            multi_log_files = self._generate_multi_log_report(self.logs, output_path, **kwargs)
            created_files.extend(multi_log_files)

        if not created_files:
            return "No HTML QSO comparison reports were generated."
        return "HTML QSO comparison reports saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])

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
        Aggregates all necessary data for single or multi-log reports.
        """
        all_data = {}
        all_calls = [log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(logs)]
        
        # Get a complete list of all bands present across all logs
        all_dfs = [get_valid_dataframe(log, False) for log in logs]
        all_bands_in_logs = pd.concat([df['Band'] for df in all_dfs if not df.empty]).dropna().unique()
        canonical_band_order = [band[1] for band in ContestLog._HF_BANDS]
        sorted_bands = sorted(list(all_bands_in_logs), key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)

        for band in sorted_bands:
            band_data = {}
            
            # --- Per-Log Data ---
            calls_on_band = {call: set(df[df['Band'] == band]['Call']) for call, df in zip(all_calls, all_dfs)}
            
            for i, log in enumerate(logs):
                call = all_calls[i]
                df_band = all_dfs[i][all_dfs[i]['Band'] == band]
                
                # --- Multi-Log Specific Calculations (Unique/Common) ---
                if len(logs) > 1:
                    other_calls_on_band = set()
                    for other_call in all_calls:
                        if other_call != call:
                            other_calls_on_band.update(calls_on_band[other_call])
                    
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
                else: # Single-Log Mode
                    total_counts = self._get_run_sp_unk_counts(df_band)
                    band_data[call] = {
                        'total': len(df_band),
                        'run': total_counts['run'],
                        'sp': total_counts['sp'],
                        'unk': total_counts['unk'],
                    }
            
            all_data[band] = band_data
        
        return all_data

    def _generate_html(self, aggregated_data: Dict, logs: List[ContestLog], is_multi_log: bool) -> str:
        """
        Generates the final HTML string from the aggregated data.
        """
        all_calls = [log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(logs)]
        
        # --- Build Table HTML for each band ---
        all_tables_html = ""
        for band, band_data in aggregated_data.items():
            
            # --- Build Table Body Rows ---
            table_rows_html = ""
            for call in all_calls:
                data = band_data.get(call, {})
                if not data or data.get('total', 0) == 0: continue

                if is_multi_log:
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
                else: # Single Log Mode
                    table_rows_html += f"""
                    <tr class="border-b border-gray-400">
                        <td class="p-3 text-left font-medium border-r-2 border-r-gray-500 whitespace-nowrap">{call}</td>
                        <td class="p-3 text-right border-r-2 border-r-gray-500">{data.get('total', 0):,}</td>
                        <td class="p-3 text-right border-r border-gray-400">{data.get('run', 0):,}</td>
                        <td class="p-3 text-right border-r border-gray-400">{data.get('sp', 0):,}</td>
                        <td class="p-3 text-right">{data.get('unk', 0):,}</td>
                    </tr>
                    """

            # --- Assemble the full table for the band ---
            if table_rows_html: # Only create a table if there's data for this band
                
                header_html = ""
                if is_multi_log:
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
                else: # Single Log Mode
                    header_html = """
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r-2 border-r-gray-500"></th>
                            <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r-2 border-r-gray-500">Total QSOs</th>
                            <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">Run</th>
                            <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">S&P</th>
                            <th class="p-3 font-semibold text-center border-b-2 border-gray-500">Unk</th>
                        </tr>
                    </thead>
                    """

                all_tables_html += f"""
                <h2 class="text-xl font-semibold text-gray-700 mt-8 mb-4">--- {band} ---</h2>
                <div class="overflow-hidden rounded-lg border-2 border-gray-500">
                    <table class="text-sm">
                        {header_html}
                        <tbody class="bg-white">
                            {table_rows_html}
                        </tbody>
                    </table>
                </div>
                """
        
        # --- Final HTML Template ---
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
        {all_tables_html}
    </div>
</body>
</html>
        """

    def _generate_single_log_report(self, log: ContestLog, output_path: str, **kwargs) -> List[str]:
        """Generates the HTML report for a single log."""
        callsign = log.get_metadata().get('MyCall', 'Unknown')
        aggregated_data = self._aggregate_data([log])
        
        if not aggregated_data:
            return []

        if kwargs.get("debug_data", False):
            debug_filename = f"{self.report_id}_{callsign}_debug.txt"
            save_debug_data(True, output_path, aggregated_data, debug_filename)

        html_content = self._generate_html(aggregated_data, [log], is_multi_log=False)
        
        filename = f"{self.report_id}_{callsign}.html"
        filepath = os.path.join(output_path, filename)
        create_output_directory(output_path)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return [filepath]

    def _generate_multi_log_report(self, logs: List[ContestLog], output_path: str, **kwargs) -> List[str]:
        """Generates the comparative HTML report for multiple logs."""
        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in logs])
        aggregated_data = self._aggregate_data(logs)

        if not aggregated_data:
            return []

        if kwargs.get("debug_data", False):
            debug_filename = f"{self.report_id}_{'_vs_'.join(all_calls)}_debug.txt"
            save_debug_data(True, output_path, aggregated_data, debug_filename)
            
        html_content = self._generate_html(aggregated_data, logs, is_multi_log=True)
        
        filename = f"{self.report_id}_{'_vs_'.join(all_calls)}.html"
        filepath = os.path.join(output_path, filename)
        create_output_directory(output_path)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return [filepath]
