# Contest Log Analyzer/contest_tools/reports/plot_comparative_heatmap.py
#
# Version: 0.39.8-Beta
# Date: 2025-08-19
#
# Purpose: A plot report that generates a comparative "split heatmap" chart to
#          visualize the band activity of two logs side-by-side.
#
# --- Revision History ---
## [0.39.8-Beta] - 2025-08-19
# - Renamed file and report_id to reflect new split-heatmap visualization.
# - Updated logic to use the new ComparativeHeatmapChart helper class.
## [0.39.6-Beta] - 2025-08-18
# - Initial release of the Split Heatmap Band Activity report.
#
import pandas as pd
import os
import logging
from typing import List, Dict, Any

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, ComparativeHeatmapChart

class Report(ContestReport):
    report_id: str = "comparative_heatmap"
    report_name: str = "Comparative Band Activity Heatmap"
    report_type: str = "plot"
    supports_pairwise = True

    def generate(self, output_path: str, **kwargs) -> str:
        """Generates the report content."""
        if len(self.logs) != 2:
            return f"Error: Report '{self.report_name}' requires exactly two logs."

        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        final_report_messages = []
        
        # --- 1. Data Preparation ---
        dfs = {}
        for call, log in [(call1, log1), (call2, log2)]:
            df = get_valid_dataframe(log, include_dupes=False)
            if df.empty or 'Datetime' not in df.columns or df['Datetime'].isna().all():
                msg = f"Skipping report for {call}: No valid QSOs with timestamps to report."
                return msg
            df['Datetime'] = df['Datetime'].dt.tz_localize('UTC')
            dfs[call] = df

        interval = '15min'
        min_time = min(df['Datetime'].min() for df in dfs.values()).floor('h')
        max_time = max(df['Datetime'].max() for df in dfs.values()).ceil('h')
        
        # --- 2. Logic to handle contests > 24 hours ---
        total_duration_hours = (max_time - min_time).total_seconds() / 3600
        num_charts = int(total_duration_hours // 24) + (1 if total_duration_hours % 24 > 0 else 0)

        for i in range(num_charts):
            chunk_start_time = min_time + pd.Timedelta(hours=i * 24)
            chunk_end_time = min_time + pd.Timedelta(hours=(i + 1) * 24)
            if chunk_end_time > max_time:
                chunk_end_time = max_time
            
            time_bins = pd.date_range(start=chunk_start_time, end=chunk_end_time, freq=interval, tz='UTC')
            
            # Use only bands with activity in either log
            active_bands1 = set(dfs[call1][dfs[call1]['Band'] != 'Invalid']['Band'].unique())
            active_bands2 = set(dfs[call2][dfs[call2]['Band'] != 'Invalid']['Band'].unique())
            all_bands = sorted(list(active_bands1 | active_bands2))
            
            if not all_bands:
                return "Skipping report: No bands with activity found in either log."

            pivot_dfs = {}
            for call, df in dfs.items():
                pivot = df.pivot_table(index='Band', columns=pd.Grouper(key='Datetime', freq=interval), aggfunc='size', fill_value=0)
                pivot = pivot.reindex(index=all_bands, columns=time_bins, fill_value=0)
                pivot_dfs[call] = pivot

            # --- 3. Plotting ---
            chart_title = f"{self.report_name}\n{call1} (Top) vs. {call2} (Bottom)"
            if num_charts > 1:
                chart_title += f" - Part {i+1}"
            
            output_suffix = f"_part_{i+1}" if num_charts > 1 else ""
            output_filename = os.path.join(output_path, f"{self.report_id}_{call1}_vs_{call2}{output_suffix}.png")

            chart = ComparativeHeatmapChart(
                data1=pivot_dfs[call1],
                data2=pivot_dfs[call2],
                call1=call1,
                call2=call2,
                title=chart_title,
                output_filename=output_filename
            )
            filepath = chart.plot()
            if filepath:
                final_report_messages.append(f"Plot saved to: {filepath}")

        return "\n".join(final_report_messages)