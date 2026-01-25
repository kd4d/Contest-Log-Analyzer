# contest_tools/contest_specific_annotations/arrl_dx_location_resolver.py
#
# Purpose: A contest-specific location resolver for the ARRL DX contest.
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

from typing import Dict, Any, Optional
import os
from ..core_annotations import CtyLookup

def resolve_location_type(metadata: Dict[str, Any], cty_dat_path: str) -> Optional[str]:
    """
    Determines if the logger is W/VE or DX for the ARRL DX contest.
    
    Hawaii (KH6), Alaska (KL7), St. Paul Is. (CY9), and Sable Is. (CY0) 
    stations participate as DX stations.
    """
    my_call = metadata.get('MyCall')
    if not my_call:
        return None

    cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
    info = cty_lookup.get_cty_DXCC_WAE(my_call)._asdict()
    
    # Check for Alaska, Hawaii, and US possessions - these are DX, not W/VE
    dxcc_pfx = info.get('DXCCPfx', '')
    if dxcc_pfx in ['KH6', 'KL7', 'CY9', 'CY0']:
        return "DX"
    
    # W/VE = 48 contiguous US States + Canada provinces
    dxcc_name = info.get('DXCCName', '')
    if dxcc_name in ["United States", "Canada"]:
        return "W/VE"
    
    return "DX"
