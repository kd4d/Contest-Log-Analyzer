# contest_tools/reports/json_multiplier_breakdown.py
#
# Purpose: Generates a machine-readable JSON artifact of the Multiplier Breakdown.
#          This serves as a high-speed cache for the web dashboard.
#
# Author: Gemini AI
# Date: 2025-12-22
# Version: 0.138.7-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.
# If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# --- Revision History ---
# [0.138.7-Beta] - 2025-12-22
# - Fixed NameError by removing stray syntax artifacts.
# [0.138.3-Beta] - 2025-12-22
# - Fixed JSON Report Path Doubling.
# [0.138.2-Beta] - 2025-12-22
# - Fixed signature to match ReportGenerator interface.
# - Refactored NpEncoder to shared utility.
# [0.138.1-Beta] - 2025-12-22
# - Fixed ImportError by updating ContestReport import path.
# [0.138.0-Beta] - 2025-12-22
# - Initial creation.

import json
import os
import logging
from .report_interface import ContestReport
from contest_tools.data_aggregators.multiplier_stats import MultiplierStatsAggregator
from contest_tools.utils.json_encoders import NpEncoder
from ._report_utils import _sanitize_filename_part

logger = logging.getLogger(__name__)

class Report(ContestReport):
    """
    Generates a machine-readable JSON artifact of the Multiplier Breakdown.
    This serves as a high-speed cache for the web dashboard.
    """
    report_id = 'json_multiplier_breakdown'
    report_name = 'JSON Multiplier Breakdown Artifact'
    # We use 'text' type so it ends up in the text/ directory alongside readable reports
    report_type = 'text' 
    supports_multi = True

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Executes the MultiplierStatsAggregator and dumps the result to JSON.
        """
        # 1. Aggregate Data (Heavy Calculation happens here once)
        mult_agg = MultiplierStatsAggregator(self.logs)
        data = mult_agg.get_multiplier_breakdown_data()
        
        # 2. Prepare Standardized Filename
        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        combo_id = "_".join([_sanitize_filename_part(c) for c in all_calls])
        filename = f"json_multiplier_breakdown_{combo_id}.json"
        
        # 3. Determine Output Path
        # ReportGenerator already passes the correct .../text/ directory
        final_path = os.path.join(output_path, filename)

        # 4. Serialize to Disk
        try:
            with open(final_path, 'w') as f:
                json.dump(data, f, cls=NpEncoder)
            logger.info(f"Generated JSON artifact: {final_path}")
        except Exception as e:
            logger.error(f"Failed to generate JSON artifact: {e}")
            return f"Failed to generate JSON artifact: {e}"

        return f"JSON Data artifact saved to {final_path}"