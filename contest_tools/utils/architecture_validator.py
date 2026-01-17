# contest_tools/utils/architecture_validator.py
#
# Purpose: Validates architectural compliance rules, ensuring code follows
#          established patterns like DAL, plugin architecture, and single source of truth.
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

import logging
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..contest_log import ContestLog

logger = logging.getLogger(__name__)

class ArchitectureValidator:
    """
    Validates architectural compliance rules.
    
    Ensures code follows established patterns:
    - Plugin architecture (contest-specific calculators as single source of truth)
    - DAL pattern (aggregators handle data processing)
    - Scoring consistency (plugin and aggregator results match)
    """
    
    def __init__(self):
        """Initialize the architecture validator."""
        self.warnings = []
        self.errors = []
    
    def validate_scoring_consistency(self, log: 'ContestLog', tolerance: int = 1) -> List[str]:
        """
        Validates that scoring calculations are consistent with plugins.
        
        Checks if calculator (plugin) output matches aggregator calculation.
        The calculator should be authoritative, aggregator should match or warn.
        
        Args:
            log: ContestLog instance to validate
            tolerance: Allowable difference in score (default 1 for rounding)
        
        Returns:
            List of warning messages if inconsistencies found (empty if consistent)
        """
        warnings = []
        callsign = log.get_metadata().get('MyCall', 'UnknownCall')
        
        # Check if calculator output exists (plugin architecture)
        has_calculator_output = (
            hasattr(log, 'time_series_score_df') and 
            log.time_series_score_df is not None and 
            not log.time_series_score_df.empty and
            'score' in log.time_series_score_df.columns
        )
        
        if not has_calculator_output:
            # Calculator output not available - this is expected for some cases
            # (e.g., filtered data, calculator not run yet)
            return warnings
        
        # Get calculator's final score (authoritative source)
        calc_final_score = int(log.time_series_score_df['score'].iloc[-1])
        
        # Calculate via ScoreStatsAggregator for comparison
        try:
            from ..data_aggregators.score_stats import ScoreStatsAggregator
            
            score_agg = ScoreStatsAggregator([log])
            agg_result = score_agg.get_score_breakdown()
            agg_final_score = agg_result["logs"].get(callsign, {}).get('final_score', 0)
            
            # Check if scores differ beyond tolerance
            score_diff = abs(calc_final_score - agg_final_score)
            if score_diff > tolerance:
                warning_msg = (
                    f"Scoring inconsistency detected for {callsign}: "
                    f"Calculator (plugin)={calc_final_score:,}, "
                    f"Aggregator={agg_final_score:,}, "
                    f"Difference={score_diff:,}. "
                    f"Calculator should be authoritative - investigate aggregator calculation."
                )
                warnings.append(warning_msg)
                logger.warning(warning_msg)
            elif score_diff > 0:
                # Small difference within tolerance (likely rounding)
                logger.debug(
                    f"Scoring difference within tolerance for {callsign}: "
                    f"Calculator={calc_final_score:,}, Aggregator={agg_final_score:,}, Diff={score_diff}"
                )
                
        except Exception as e:
            # If aggregator calculation fails, log but don't treat as architecture violation
            logger.warning(f"Could not validate scoring consistency for {callsign}: {e}")
        
        return warnings
    
    def validate_plugin_usage(self, log: 'ContestLog') -> List[str]:
        """
        Validates that plugin architecture is respected.
        
        Checks if contest has plugins defined and if they're being used appropriately.
        
        Args:
            log: ContestLog instance to validate
        
        Returns:
            List of warning messages if violations found
        """
        warnings = []
        contest_def = log.contest_definition
        callsign = log.get_metadata().get('MyCall', 'UnknownCall')
        
        # Check if contest has time_series_calculator defined
        if contest_def.time_series_calculator:
            calculator_name = contest_def.time_series_calculator
            # Verify calculator output exists
            if not (hasattr(log, 'time_series_score_df') and 
                    log.time_series_score_df is not None and 
                    not log.time_series_score_df.empty):
                warning_msg = (
                    f"Contest {contest_def.contest_name} defines calculator '{calculator_name}' "
                    f"but calculator output not available for {callsign}. "
                    f"Ensure calculator is run before using aggregators that need it."
                )
                warnings.append(warning_msg)
                logger.warning(warning_msg)
        
        return warnings
    
    def validate_all(self, logs: List['ContestLog'], tolerance: int = 1) -> dict:
        """
        Runs all validation checks on a list of logs.
        
        Args:
            logs: List of ContestLog instances to validate
            tolerance: Score difference tolerance for consistency checks
        
        Returns:
            Dictionary with validation results:
            {
                'warnings': List[str],  # All warnings collected
                'errors': List[str],     # All errors collected (currently unused)
                'summary': str           # Summary message
            }
        """
        all_warnings = []
        all_errors = []
        
        for log in logs:
            # Validate scoring consistency
            scoring_warnings = self.validate_scoring_consistency(log, tolerance=tolerance)
            all_warnings.extend(scoring_warnings)
            
            # Validate plugin usage
            plugin_warnings = self.validate_plugin_usage(log)
            all_warnings.extend(plugin_warnings)
        
        # Generate summary
        warning_count = len(all_warnings)
        if warning_count == 0:
            summary = f"Architecture validation passed for {len(logs)} log(s)."
        else:
            summary = (
                f"Architecture validation found {warning_count} warning(s) "
                f"for {len(logs)} log(s). Review warnings above."
            )
        
        return {
            'warnings': all_warnings,
            'errors': all_errors,
            'summary': summary
        }
