# Contest Log Analyzer/contest_tools/core_annotations/_core_utils.py
#
# Purpose: A utility module providing shared helper functions for the
#          core annotation engine.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.31.0-Beta
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
## [0.31.0-Beta] - 2025-08-07
# - Initial release of Version 0.31.0-Beta.
import pandas as pd

def is_dx(cty_data):
    """
    Determines if a location is considered DX based on CTY data.
    """
    return cty_data.name not in ["United States", "Canada"]