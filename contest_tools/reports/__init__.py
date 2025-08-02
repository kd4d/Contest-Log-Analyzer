# Contest Log Analyzer/contest_tools/reports/__init__.py
#
# Purpose: Makes the 'reports' directory a Python package and discovers
#          all available report generator classes.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.25.1-Beta
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
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).

## [0.25.1-Beta] - 2025-08-01
### Changed
# - The report discovery process is now silent unless an error occurs to
#   reduce unnecessary console output.

## [0.23.5-Beta] - 2025-08-01
### Fixed
# - Added the missing 'mults_from_zero_point_qsos' property to the class.

## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.

## [0.10.0-Beta] - 2025-07-21
# - Initial release of the report discovery mechanism.

import os
import importlib
import traceback
from typing import Dict, Type
from .report_interface import ContestReport

# Dictionary to store discovered report classes, keyed by their report_id
AVAILABLE_REPORTS: Dict[str, Type[ContestReport]] = {}

def discover_reports():
    """
    Dynamically imports all modules in this directory and discovers
    classes that inherit from ContestReport.
    """
    if AVAILABLE_REPORTS: # Discover only once
        return

    current_dir = os.path.dirname(__file__)
    for filename in sorted(os.listdir(current_dir)):
        if filename.endswith('.py') and not filename.startswith('__') and not filename.startswith('_'):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f".{module_name}", package=__name__)
                if hasattr(module, 'Report') and issubclass(module.Report, ContestReport):
                    report_id = module.Report.report_id.fget(None)
                    if report_id in AVAILABLE_REPORTS:
                        print(f"  - WARNING: Duplicate report_id '{report_id}' found in {filename}. The original report will be overwritten.")
                    AVAILABLE_REPORTS[report_id] = module.Report
            except Exception:
                print(f"  - FAILED to load report from {filename}.")
                print("  - Traceback:")
                # Indent the traceback for readability
                tb_lines = traceback.format_exc().splitlines()
                for line in tb_lines:
                    print(f"    {line}")
    
    print(f"--- Report Discovery Finished: {len(AVAILABLE_REPORTS)} reports loaded. ---")


# Automatically discover reports when the package is imported
discover_reports()
