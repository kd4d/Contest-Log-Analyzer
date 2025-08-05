# Contest Log Analyzer/contest_tools/reports/plot_qso_breakdown_chart.py
#
# Purpose: Generates a stacked bar chart comparing the unique and common QSOs
#          between two logs, broken down by Run/S&P status.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.13-Beta
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
## [0.30.13-Beta] - 2025-08-05
### Fixed
# - Corrected the report_id to 'qso_breakdown_chart' (removing 'plot_').
# - Standardized the output filename to use '_vs_' as the separator.
## [0.30.7-Beta] - 2025-08-05
### Fixed
# - Corrected AttributeError and SettingWithCopyWarning.
## [0.30.6-Beta] - 2025-08-05
### Fixed
# - Corrected a TypeError.
## [0.30.4-Beta] - 2025-08-05
### Fixed
# - Corrected a syntax error.
## [0.30.2-Beta] - 2025-08-05
### Fixed
# - Corrected the key for sorting bands to prevent a ValueError.
## [0.30.1-Beta] - 2025-08-05
### Fixed
# - Changed import from the old 'ReportInterface' to the new 'ContestReport'.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import logging
from ..contest_log import ContestLog

class Report(ContestReport):
    report_id = "qso_breakdown_chart"
    report_name = "QSO Breakdown by Run/S&P"
    report_type = "chart"
    supports_single = False
    supports_pairwise = True
    supports_multi = False

    def generate(self, output_path: str, **kwargs) -> str:
        create_output_directory(output_path)
        include_dupes = kwargs.get('include_dupes', False)

        if len(self.logs) != 2:
            return f"Report '{self.report_name}' requires exactly two logs. Skipping."

        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        
        df1 = get_valid_dataframe(log1, include_dupes)
        df2 = get_valid_dataframe(log2, include_dupes)

        if df1.empty or df2.empty:
            return f"Skipping '{self.report_name}': At least one log has no valid QSOs."

        # Find common and unique QSOs
        common_calls = pd.merge(df1, df2, on='Call', how='inner')['Call']
        unique_to_1 = df1[~df1['Call'].isin(common_calls)]
        unique_to_2 = df2[~df2['Call'].isin(common_calls)]

        # Get counts by band and Run/S&P status
        canonical_band_order = [band[1] for band in ContestLog._HF_BANDS]
        all_bands_in_logs = pd.concat([df1['Band'], df2['Band']]).unique()
        bands = sorted(all_bands_in_logs, key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)
        
        common_counts = df1[df1['Call'].isin(common_calls)].groupby('Band').size().reindex(bands, fill_value=0)
        unique_counts_1 = self._get_run_sp_counts(unique_to_1, bands)
        unique_counts_2 = self._get_run_sp_counts(unique_to_2, bands)

        # Plotting
        fig, ax = plt.subplots(figsize=(12, 8))
        bar_width = 0.35
        index = np.arange(len(bands))

        left_pos = common_counts / 2
        ax.bar(index, -unique_counts_1['Run'].values, bar_width, bottom=-left_pos.values, color='red', label=f'{call1} Unique Run')
        ax.bar(index, -unique_counts_1['S&P'].values, bar_width, bottom=(-left_pos - unique_counts_1['Run']).values, color='orange', label=f'{call1} Unique S&P')

        ax.bar(index, common_counts.values, bar_width, color='gray', label='Common QSOs')

        right_pos = common_counts / 2
        ax.bar(index, unique_counts_2['Run'].values, bar_width, bottom=right_pos.values, color='blue', label=f'{call2} Unique Run')
        ax.bar(index, unique_counts_2['S&P'].values, bar_width, bottom=(right_pos + unique_counts_2['Run']).values, color='cyan', label=f'{call2} Unique S&P')

        # Formatting
        ax.axvline(0, color='black', linewidth=0.8)
        ax.set_ylabel('QSO Count')
        ax.set_xticks(index)
        ax.set_xticklabels(bands)
        ax.set_title(f'QSO Breakdown: {call1} vs {call2}', fontsize=16)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        plt.tight_layout()
        
        output_filename = os.path.join(output_path, f"{self.report_id}_{call1}_vs_{call2}.png")
        try:
            plt.savefig(output_filename, dpi=150)
            plt.close(fig)
            return f"'{self.report_name}' saved to {output_filename}"
        except Exception as e:
            logging.error(f"Error saving plot: {e}")
            plt.close(fig)
            return f"Error generating report '{self.report_name}'"

    def _get_run_sp_counts(self, df_in, bands):
        df = df_in.copy()
        
        run_sp_map = { 'Run': 'Run', 'S&P': 'S&P', 'Unknown': 'S&P' }
        df['PlotCategory'] = df['Run'].map(run_sp_map)
        
        counts = df.groupby(['Band', 'PlotCategory']).size().unstack(fill_value=0)
        counts = counts.reindex(bands, fill_value=0)
        
        if 'Run' not in counts.columns: counts['Run'] = 0
        if 'S&P' not in counts.columns: counts['S&P'] = 0
        
        return counts[['Run', 'S&P']]