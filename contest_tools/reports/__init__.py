# Contest Log Analyzer/contest_tools/reports/__init__.py
#
# Purpose: This module dynamically discovers and imports all available report
#          generator classes from the other Python files in this directory. It
#          creates the AVAILABLE_REPORTS dictionary, which is used by the main
#          CLI and ReportGenerator to access and run reports.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.0-Beta
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
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
import os
import importlib
import inspect
import logging

# Dynamically discover and load all available report classes
AVAILABLE_REPORTS = {}

# Get the directory of the current module
current_dir = os.path.dirname(os.path.abspath(__file__))

# Iterate over all files in the directory
for filename in os.listdir(current_dir):
    # Process only Python files that are not __init__.py itself
    if filename.endswith('.py') and not filename.startswith('__'):
        module_name = filename[:-3]
        
        try:
            # Import the module dynamically
            module = importlib.import_module(f".{module_name}", package='contest_tools.reports')
            
            # Find the 'Report' class within the imported module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name == 'Report':
                    # Check if the class has the required 'report_id' attribute
                    if hasattr(obj, 'report_id'):
                        report_id = obj.report_id
                        AVAILABLE_REPORTS[report_id] = obj
                    else:
                        logging.warning(f"Report class in {filename} is missing 'report_id' attribute.")
        except Exception as e:
            logging.error(f"Failed to load report from {filename}: {e}")