# contest_tools/reports/text_enhanced_missed_multipliers.py
#
# Purpose: Enhanced missed multipliers report for Sweepstakes contest.
#          Shows which logs worked each missed multiplier, bands/modes worked,
#          and Run/S&P/Unknown breakdown.
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

from typing import List, Dict, Any
import os
import logging
from ..contest_log import ContestLog
from ..data_aggregators.multiplier_stats import MultiplierStatsAggregator
from .report_interface import ContestReport
from contest_tools.utils.report_utils import get_standard_footer, get_standard_title_lines
from contest_tools.utils.callsign_utils import build_callsigns_filename_part

logger = logging.getLogger(__name__)

class Report(ContestReport):
    """
    Generates an enhanced missed multipliers report for Sweepstakes.
    Shows which logs worked each missed multiplier, bands/modes, and Run/S&P/Unknown counts.
    Only generates for Sweepstakes contests.
    """
    report_id: str = "enhanced_missed_multipliers"
    report_name: str = "Enhanced Missed Multipliers Breakdown"
    report_type: str = "text"
    supports_single = False
    supports_multi = True
    supports_pairwise = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """Generates the enhanced missed multipliers report (Sweepstakes only)."""
        # Check if this is a Sweepstakes contest
        if not self.logs:
            return "Error: No logs provided."
        
        contest_def = self.logs[0].contest_definition
        contest_name = contest_def.contest_name if contest_def else None
        
        if not contest_name or not contest_name.startswith("ARRL-SS"):
            # Not Sweepstakes - skip generation
            return f"Skipped: Enhanced missed multipliers report only available for Sweepstakes contests."
        
        mult_name = kwargs.get('mult_name')
        mode_filter = kwargs.get('mode_filter')
        
        if not mult_name:
            return f"Error: 'mult_name' argument is required for '{self.report_name}' report."
        
        # Get enhanced breakdown from aggregator
        aggregator = MultiplierStatsAggregator(self.logs)
        agg_results = aggregator.get_missed_data(mult_name, mode_filter, enhanced=True)
        
        if 'error' in agg_results:
            return agg_results['error']
        
        enhanced_breakdown = agg_results.get('enhanced_breakdown', [])
        
        # If no missed multipliers, skip generation
        if not enhanced_breakdown:
            return f"Skipped: No missed multipliers found for '{mult_name}'."
        
        all_calls = agg_results['all_calls']
        mult_rule = agg_results['mult_rule']
        
        # Generate report content
        lines = []
        
        # Header
        title_lines = get_standard_title_lines(
            f"{self.report_name}: {mult_name}",
            self.logs,
            "All Bands",
            mode_filter,
            set()  # modes_present - not critical for this report
        )
        lines.extend(title_lines)
        lines.append("")
        lines.append("Note: 'Worked By' lists callsigns that worked this multiplier.")
        lines.append("      'Unknown' indicates Run/S&P classification could not be reliably determined.")
        lines.append("")
        
        # Calculate column widths dynamically based on content
        max_section_width = max(len(item['multiplier_display']) for item in enhanced_breakdown) if enhanced_breakdown else 12
        max_section_width = max(max_section_width, 12)  # Minimum 12
        
        max_worked_by_width = 0
        max_bands_modes_width = 0
        for item in enhanced_breakdown:
            worked_by = ', '.join(item['worked_by_calls']) if item['worked_by_calls'] else '--'
            bands_modes = []
            if item['bands_worked']:
                bands_modes.extend(item['bands_worked'])
            if item['modes_worked']:
                bands_modes.extend(item['modes_worked'])
            bands_modes_str = ', '.join(bands_modes) if bands_modes else '--'
            max_worked_by_width = max(max_worked_by_width, len(worked_by))
            max_bands_modes_width = max(max_bands_modes_width, len(bands_modes_str))
        
        # Set reasonable column widths
        section_width = min(max_section_width, 20)  # Cap at 20
        worked_by_width = min(max(max_worked_by_width, 15), 30)  # Min 15, max 30
        bands_modes_width = min(max(max_bands_modes_width, 20), 35)  # Min 20, max 35
        
        # Table header
        header_line = (f"{'Section':<{section_width}} "
                      f"{'Worked By':<{worked_by_width}} "
                      f"{'Bands/Modes':<{bands_modes_width}} "
                      f"{'Run':>6} "
                      f"{'S&P':>6} "
                      f"{'Unknown':>8}")
        lines.append(header_line)
        lines.append("-" * len(header_line))
        
        # Table rows
        for item in enhanced_breakdown:
            section = item['multiplier_display']
            # Truncate section name if too long
            if len(section) > section_width:
                section = section[:section_width-3] + '...'
            
            worked_by = ', '.join(item['worked_by_calls']) if item['worked_by_calls'] else '--'
            # Truncate worked_by if too long
            if len(worked_by) > worked_by_width:
                worked_by = worked_by[:worked_by_width-3] + '...'
            
            bands_modes = []
            if item['bands_worked']:
                bands_modes.extend(item['bands_worked'])
            if item['modes_worked']:
                bands_modes.extend(item['modes_worked'])
            bands_modes_str = ', '.join(bands_modes) if bands_modes else '--'
            # Truncate bands_modes if too long
            if len(bands_modes_str) > bands_modes_width:
                bands_modes_str = bands_modes_str[:bands_modes_width-3] + '...'
            
            run = str(item['run_count']) if item['run_count'] > 0 else '0'
            sp = str(item['sp_count']) if item['sp_count'] > 0 else '0'
            unk = str(item['unk_count']) if item['unk_count'] > 0 else '0'
            
            row_line = (f"{section:<{section_width}} "
                       f"{worked_by:<{worked_by_width}} "
                       f"{bands_modes_str:<{bands_modes_width}} "
                       f"{run:>6} "
                       f"{sp:>6} "
                       f"{unk:>8}")
            lines.append(row_line)
        
        lines.append("")
        lines.append("-" * 80)
        lines.append("")
        
        # Summary
        total_worked_by_all = sum(1 for item in enhanced_breakdown if len(item['worked_by_calls']) == len(all_calls))
        total_worked_by_some = sum(1 for item in enhanced_breakdown if 0 < len(item['worked_by_calls']) < len(all_calls))
        total_worked_by_none = sum(1 for item in enhanced_breakdown if len(item['worked_by_calls']) == 0)
        
        lines.append("Summary:")
        lines.append(f"  Total Missed Multipliers: {len(enhanced_breakdown)}")
        lines.append(f"  Worked by All Logs: {total_worked_by_all}")
        lines.append(f"  Worked by Some Logs: {total_worked_by_some}")
        lines.append(f"  Worked by No Logs: {total_worked_by_none}")
        lines.append("")
        
        # Footer
        standard_footer = get_standard_footer(self.logs)
        lines.append(standard_footer)
        
        # Save to file
        all_calls_sorted = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        callsigns_part = build_callsigns_filename_part(all_calls_sorted)
        filename = f"enhanced_missed_multipliers--{callsigns_part}.txt"
        output_file = os.path.join(output_path, filename)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return f"Generated: {filename}"
