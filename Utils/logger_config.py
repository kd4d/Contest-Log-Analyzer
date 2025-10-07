# Utils/logger_config.py
#
# Purpose: This module provides a centralized configuration for the application's
#          logging system.
#
# Author: Gemini AI
# Date: 2025-10-01
# Version: 0.90.0-Beta
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
# --- Revision History ---
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

import logging
import sys

def setup_logging(verbose: bool = False):
    """
    Configures the root logger for the application.

    Args:
        verbose (bool): If True, sets the logging level to INFO to include
                        detailed status messages. Defaults to False, which
                        only shows WARNING and ERROR messages.
    """
    level = logging.INFO if verbose else logging.WARNING
    
    # Use a custom format that includes the module name
    log_format = '%(levelname)s: (%(module)s) %(message)s'
    
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Clear any existing handlers to prevent duplicate output in interactive environments
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.setLevel(level)
    
    # Create a handler to write to the console (stdout)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Create a formatter and add it to the handler
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    
    # Add the handler to the root logger
    root_logger.addHandler(handler)
