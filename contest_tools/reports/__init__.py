# Contest Log Analyzer/contest_tools/reports/__init__.py
#
# Purpose: Makes the 'reports' directory a Python package and discovers
#          all available report generator classes.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-21
# Version: 0.10.0-Beta
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

## [0.10.0-Beta] - 2025-07-21
# - Initial release of the report discovery mechanism.

### Changed
# - (None)

### Fixed
# - (None)

### Removed
# - (None)

import os
import importlib
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
    for filename in os.listdir(current_dir):
        if filename.endswith('.py') and not filename.startswith('__') and filename != 'report_interface.py':
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f".{module_name}", package=__name__)
                if hasattr(module, 'Report') and issubclass(module.Report, ContestReport):
                    # Instantiate temporarily to get the report_id
                    report_id = module.Report.report_id.fget(None) 
                    AVAILABLE_REPORTS[report_id] = module.Report
                    print(f"Discovered report: '{report_id}'")
            except Exception as e:
                print(f"Could not load report from {filename}: {e}")

# Automatically discover reports when the package is imported
discover_reports()
