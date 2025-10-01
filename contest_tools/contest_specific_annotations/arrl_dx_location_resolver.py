# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_dx_location_resolver.py
#
# Author: Gemini AI
# Date: 2025-09-30
# Version: 0.90.15-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#
# Purpose: A contest-specific location resolver for the ARRL DX contest.
#
# --- Revision History ---
## [0.90.15-Beta] - 2025-09-30
### Changed
# - Refactored function to accept an explicit `cty_dat_path` parameter,
#   removing the hardcoded path logic to fix a FileNotFoundError.
## [0.88.0-Beta] - 2025-09-15
### Added
# - Added a new "How to Add a New Contest: A Step-by-Step Guide"
#   section to provide a clear, tutorial-based workflow for developers.
from typing import Dict, Any, Optional
import os
from ..core_annotations import CtyLookup

def resolve_location_type(metadata: Dict[str, Any], cty_dat_path: str) -> Optional[str]:
    """
    Determines if the logger is W/VE or DX for the ARRL DX contest.
    """
    my_call = metadata.get('MyCall')
    if not my_call:
        return None

    cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
    info = cty_lookup.get_cty_DXCC_WAE(my_call)._asdict()
    
    return "W/VE" if info.get('DXCCName') in ["United States", "Canada"] else "DX"