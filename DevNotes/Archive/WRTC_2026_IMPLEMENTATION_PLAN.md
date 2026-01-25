# WRTC-2026 Contest Implementation Plan

**Date:** 2026-01-20  
**Status:** Completed  
**Last Updated:** 2026-01-20  
**Category:** Planning

---

## Overview

This document outlines the implementation plan for adding WRTC-2026 contest support to the Contest Log Analyzer. WRTC-2026 is a standalone contest (like ARRL-10) that uses IARU-HF log format and the IARU public log archive, but applies different scoring rules.

**Key Architectural Decision:**
- WRTC-2026 is a **standalone contest** (not an overlay or variant)
- Contest name `WRTC-2026` defines fixed scoring rules
- Log year is a separate parameter (can apply WRTC-2026 rules to any year's IARU logs)
- Uses same public log archive as IARU-HF

---

## Contest Rules Summary

### Basic Information
- **Contest Name:** `WRTC-2026` (in system, not Cabrillo header - logs are IARU format)
- **Period:** Saturday 12:00 UTC to Sunday 11:59 UTC (same as IARU-HF)
- **Bands:** 3.5, 7, 14, 21, 28 MHz (80M, 40M, 20M, 15M, 10M)
- **Modes:** CW and SSB only (no Digital/DG)

### Scoring Rules
- **QSO Points:**
  - Within Europe: 2 points
  - Outside Europe: 5 points
- **Multipliers (once per band, regardless of mode):**
  - DXCC Countries
  - IARU Member Society HQ Stations
  - IARU Officials (max 4 per band: AC, R1, R2, R3)
- **Rule 8.2:** HQ Stations and Officials do NOT count for DXCC multipliers
- **Final Score:** Total multipliers × Sum of QSO points

### Log Sources
- IARU public log archive (same as IARU-HF)
- Uploaded log files (IARU-HF format)

---

## Implementation Tasks

### Task 1: Add IARU Public Log Fetching Support

**File:** `contest_tools/utils/log_fetcher.py`

**Current State:**
- ARRL public log fetching exists (`fetch_arrl_log_index`, `download_arrl_logs`)
- IARU uses same archive structure as ARRL
- Need to add IARU to contest code mapping

**Required Changes:**
1. Add `'IARU-HF': 'iaruhf'` to `ARRL_CONTEST_CODES` mapping
2. Existing ARRL functions work for IARU (same URL structure)
3. Optional: Add convenience wrapper `fetch_iaru_log_index(year)` for clarity

**Implementation:**
```python
# In ARRL_CONTEST_CODES mapping:
ARRL_CONTEST_CODES = {
    'ARRL-10': '10m',
    'ARRL-DX-CW': 'dx',
    'ARRL-DX-SSB': 'dx',
    'IARU-HF': 'iaruhf',  # NEW
}

# Optional convenience function:
def fetch_iaru_log_index(year: str) -> List[str]:
    """Fetches IARU HF log index for a given year."""
    return fetch_arrl_log_index(year, 'iaruhf', contest_name='IARU-HF')
```

**Verification:**
- Test fetching IARU log index for 2024
- Verify eid/iid discovery works (`cn=iaruhf` → year links)
- Test downloading specific logs

---

### Task 2: Create Shared IARU Multiplier Utilities

**File:** `contest_tools/core_annotations/_iaru_mult_utils.py` (NEW)

**Purpose:**
- Shared utilities for IARU HQ Stations and IARU Officials multipliers
- Used by both IARU-HF and WRTC contests
- Eliminates code duplication

**Implementation:**
```python
"""
Shared utilities for IARU HQ Stations and IARU Officials multipliers.
Used by both IARU-HF and WRTC contests.
"""
import os
from typing import Set, Optional, Dict

_OFFICIALS_SET_CACHE: Set[str] = set()

def load_officials_set(root_input_dir: str) -> Set[str]:
    """
    Loads the iaru_officials.dat file into a set for fast lookups.
    
    Returns set containing: {'AC', 'R1', 'R2', 'R3'}
    """
    global _OFFICIALS_SET_CACHE
    if _OFFICIALS_SET_CACHE:
        return _OFFICIALS_SET_CACHE
    
    try:
        root_dir = root_input_dir.strip().strip('"').strip("'")
        data_dir = os.path.join(root_dir, 'data')
        filepath = os.path.join(data_dir, 'iaru_officials.dat')
        with open(filepath, 'r', encoding='utf-8') as f:
            _OFFICIALS_SET_CACHE = {line.strip().upper() for line in f if line.strip()}
    except Exception as e:
        print(f"Warning: Could not load iaru_officials.dat file. Official multiplier check will be disabled. Error: {e}")
        _OFFICIALS_SET_CACHE = set()
    
    return _OFFICIALS_SET_CACHE

def resolve_iaru_hq_official(exchange: str, officials_set: Set[str]) -> Dict[str, Optional[str]]:
    """
    Parses exchange to identify HQ Station or IARU Official.
    
    Args:
        exchange: Received exchange value (from RcvdMult column)
        officials_set: Set of valid IARU official abbreviations (AC, R1, R2, R3)
    
    Returns:
        Dict with keys 'hq' and 'official', values are the multiplier value or None
    """
    if not exchange or pd.isna(exchange):
        return {'hq': None, 'official': None}
    
    exchange = str(exchange).strip()
    
    # Check if it's an IARU Official
    if exchange.upper() in officials_set:
        return {'hq': None, 'official': exchange.upper()}
    
    # Assume it's an IARU HQ station if it's alphabetic
    if exchange.isalpha():
        return {'hq': exchange.upper(), 'official': None}
    
    return {'hq': None, 'official': None}
```

**Key Points:**
- Shared by IARU-HF and WRTC
- IARU-HF also uses Zones (not shared)
- WRTC uses DXCC instead of Zones (not shared)

---

### Task 3: Update IARU-HF Multiplier Resolver to Use Shared Utilities

**File:** `contest_tools/contest_specific_annotations/iaru_hf_multiplier_resolver.py`

**Current State:**
- Has own `_load_officials_set()` function
- Has own `_resolve_row()` function for HQ/Official parsing

**Required Changes:**
1. Import from `_iaru_mult_utils`
2. Replace `_load_officials_set()` with `load_officials_set()` from shared module
3. Update `_resolve_row()` to use `resolve_iaru_hq_official()` for HQ/Official
4. Keep Zone parsing logic (IARU-HF specific)

**Implementation:**
```python
from ..core_annotations._iaru_mult_utils import load_officials_set, resolve_iaru_hq_official

def _resolve_row(row: pd.Series, officials_set: Set[str]) -> Dict[str, Optional[str]]:
    """Parses the received exchange for a single QSO."""
    mult_zone, mult_hq, mult_official = None, None, None
    
    exchange = row.get('RcvdMult')
    
    if pd.notna(exchange):
        exchange = str(exchange).strip()
        
        # 1. Check if it's a numeric ITU Zone (IARU-HF specific)
        if exchange.isnumeric():
            mult_zone = exchange
        
        # 2. Use shared utility for HQ/Official
        hq_official = resolve_iaru_hq_official(exchange, officials_set)
        mult_hq = hq_official['hq']
        mult_official = hq_official['official']
    
    return {'zone': mult_zone, 'hq': mult_hq, 'official': mult_official}
```

**Verification:**
- Test IARU-HF multiplier resolution still works
- Verify HQ and Official multipliers resolve correctly
- Verify Zone multipliers still work

---

### Task 4: Create WRTC-2026 Contest Definition

**File:** `contest_tools/contest_definitions/wrtc_2026.json` (NEW - standalone, no inheritance)

**Current State:**
- `wrtc.json` exists (base with inheritance)
- `wrtc_2026.json` exists (inherits from wrtc.json)
- Need to make `wrtc_2026.json` standalone

**Required Changes:**
1. Remove `inherits_from` field
2. Include all necessary fields directly
3. Remove "DG" from valid_modes (CW and SSB only)
4. Set `contest_name: "WRTC-2026"`
5. Reference `iaru_hf_parser` and `iaru_hf_adif` (composition, not inheritance)

**Implementation:**
```json
{
  "_filename": "contest_tools/contest_definitions/wrtc_2026.json",
  "contest_name": "WRTC-2026",
  "valid_modes": ["CW", "PH"],
  "valid_bands": ["80M", "40M", "20M", "15M", "10M"],
  "scoring_module": "wrtc_2026_scoring",
  "custom_multiplier_resolver": "wrtc_multiplier_resolver",
  "time_series_calculator": "wrtc_calculator",
  "contest_period": {
    "start_day": "Saturday",
    "start_time": "12:00:00 UTC",
    "end_day": "Sunday",
    "end_time": "11:59:59 UTC"
  },
  "dupe_check_scope": "per_band",
  "score_formula": "points_times_mults",
  "enable_adif_export": true,
  "custom_adif_exporter": "iaru_hf_adif",
  "custom_parser_module": "iaru_hf_parser",
  "included_reports": [
    "wrtc_propagation",
    "wrtc_propagation_animation"
  ],
  "exchange_parsing_rules": {
    "IARU-HF-ZONE-LOGGER": {
      "regex": "(\\d{2,3})\\s+(\\d{1,2})\\s+([A-Z0-9/]+)\\s+(\\d{2,3})\\s+([A-Z0-9]+)(?:\\s+(\\d))?",
      "groups": ["SentRST", "SentZone", "Call", "RST", "RcvdMult", "Transmitter"]
    }
  },
  "mutually_exclusive_mults": [["Mult_DXCC", "Mult_HQ", "Mult_Official"]],
  "multiplier_rules": [
    {
      "name": "Countries",
      "value_column": "Mult_DXCC",
      "name_column": "Mult_DXCCName",
      "totaling_method": "once_per_band_no_mode"
    },
    {
      "name": "HQ Stations",
      "value_column": "Mult_HQ",
      "totaling_method": "once_per_band_no_mode"
    },
    {
      "name": "IARU Officials",
      "value_column": "Mult_Official",
      "totaling_method": "once_per_band_no_mode"
    }
  ],
  "default_qso_columns": [
    "ContestName", "MyCall", "Frequency", "Mode", "Datetime", "SentRST", "SentRS",
    "SentZone", "Call", "RST", "RS", "RcvdMult", "Band", "Date", "Hour", "Dupe",
    "DXCCName", "DXCCPfx", "CQZone", "ITUZone", "Continent", "Run", "QSOPoints",
    "Mult_DXCC", "Mult_DXCCName", "Mult_HQ", "Mult_Official"
  ]
}
```

**Key Points:**
- Standalone (no inheritance)
- References `iaru_hf_parser` and `iaru_hf_adif` (composition)
- Valid modes: CW and PH only (no DG)
- Multiplier rules: DXCC, HQ, Official (no Zones)

---

### Task 5: Update WRTC Multiplier Resolver to Use Shared Utilities

**File:** `contest_tools/contest_specific_annotations/wrtc_multiplier_resolver.py`

**Current State:**
- Calls `iaru_hf_multiplier_resolver.resolve_multipliers()` to get HQ/Official
- Then adds DXCC logic
- WRTC doesn't use Zones

**Required Changes:**
1. Import from `_iaru_mult_utils`
2. Use shared utilities for HQ/Official parsing
3. Keep DXCC logic (WRTC-specific)
4. Remove dependency on IARU resolver

**Implementation:**
```python
from ..core_annotations._iaru_mult_utils import load_officials_set, resolve_iaru_hq_official

def resolve_multipliers(df: pd.DataFrame, my_location_type: str, root_input_dir: str, contest_def: ContestDefinition) -> pd.DataFrame:
    """
    Resolves multipliers for WRTC contests.
    Multipliers: DXCC Countries, HQ Stations, IARU Officials.
    Rule: Counted once per band, regardless of mode.
    """
    if df.empty:
        return df
    
    # Initialize multiplier columns
    df['Mult_DXCC'] = pd.NA
    df['Mult_DXCCName'] = pd.NA
    df['Mult_HQ'] = pd.NA
    df['Mult_Official'] = pd.NA
    
    # Load officials set
    officials_set = load_officials_set(root_input_dir)
    
    # Process each row
    for idx, row in df.iterrows():
        exchange = row.get('RcvdMult')
        
        # Use shared utility for HQ/Official
        hq_official = resolve_iaru_hq_official(exchange, officials_set)
        if hq_official['hq']:
            df.loc[idx, 'Mult_HQ'] = hq_official['hq']
        if hq_official['official']:
            df.loc[idx, 'Mult_Official'] = hq_official['official']
        
        # DXCC multiplier (WRTC-specific)
        dxcc_pfx = row.get('DXCCPfx')
        dxcc_name = row.get('DXCCName')
        
        if pd.notna(dxcc_pfx) and pd.notna(dxcc_name):
            df.loc[idx, 'Mult_DXCC'] = dxcc_pfx
            df.loc[idx, 'Mult_DXCCName'] = dxcc_name
    
    # Rule 8.2: HQ/Officials do not count for DXCC
    hq_or_official_mask = df['Mult_HQ'].notna() | df['Mult_Official'].notna()
    df.loc[hq_or_official_mask, ['Mult_DXCC', 'Mult_DXCCName']] = pd.NA
    
    return df
```

**Key Points:**
- Uses shared utilities (no dependency on IARU resolver)
- WRTC-specific: DXCC logic
- WRTC-specific: Rule 8.2 enforcement

---

### Task 6: Remove `--wrtc` Flag Logic from LogManager

**File:** `contest_tools/log_manager.py`

**Current State:**
- Lines 65-66: `if wrtc_year and base_contest == 'IARU-HF': effective_contest = f"WRTC-{wrtc_year}"`
- Lines 157-159: Similar logic in another method
- Special-case transformation logic

**Required Changes:**
1. Remove `wrtc_year` parameter from `load_log_batch()`
2. Remove all `--wrtc` flag transformation logic
3. WRTC-2026 is now a normal contest (like ARRL-10)

**Implementation:**
- Remove `wrtc_year: int = None` parameter
- Remove conditional logic that transforms IARU-HF → WRTC-{year}
- Contest name comes directly from Cabrillo header or user selection

**Verification:**
- Test loading WRTC-2026 logs directly (contest name in header or explicit selection)
- Test loading IARU-HF logs (no transformation)
- Verify no special-case logic remains

---

### Task 7: Verify WRTC-2026 Scoring Module

**File:** `contest_tools/contest_specific_annotations/wrtc_2026_scoring.py`

**Current State:**
- Already implements 2/5 point scoring (Within Europe 2, Outside Europe 5)
- Validates logger is in Europe

**Required Changes:**
- None (already correct)

**Verification:**
- Test scoring with European logger
- Test scoring with non-European logger (should warn and return 0)
- Verify point values: EU=2, non-EU=5

---

### Task 8: Update Web UI for Contest/Year Selection

**Files:** `web_app/analyzer/views.py`, templates

**Current State:**
- Contest selection dropdown
- Year selection for public logs

**Required Changes:**
1. Add `WRTC-2026` to contest dropdown
2. When `WRTC-2026` selected, use IARU public log archive
3. Year selector works independently (can select any year for logs)
4. Clarify: Contest name = rules, Year = log source

**Implementation Notes:**
- Contest selection: `WRTC-2026` appears in dropdown
- Public log fetching: When `WRTC-2026` selected, call `fetch_arrl_log_index(year, 'iaruhf')`
- Year selection: Independent of contest name (can analyze 2024 logs with WRTC-2026 rules)

---

## Testing Checklist

### Unit Tests
- [ ] IARU public log fetching (index and download)
- [ ] Shared IARU multiplier utilities (HQ/Official parsing)
- [ ] IARU-HF multiplier resolver (still works with shared utilities)
- [ ] WRTC multiplier resolver (uses shared utilities, adds DXCC)
- [ ] WRTC-2026 scoring (2/5 points, Europe validation)

### Integration Tests
- [ ] Load WRTC-2026 log from file
- [ ] Load WRTC-2026 logs from IARU public archive
- [ ] Apply WRTC-2026 rules to 2024 IARU logs (practice year)
- [ ] Apply WRTC-2026 rules to 2026 IARU logs (actual competition)
- [ ] Verify multiplier counting (DXCC, HQ, Official, once per band)
- [ ] Verify Rule 8.2 (HQ/Official don't count for DXCC)

### Regression Tests
- [ ] IARU-HF contest still works (no breaking changes)
- [ ] Existing contests unaffected
- [ ] Public log fetching for ARRL contests still works

---

## Architecture Notes

### Contest Name vs Log Year
- **Contest Name (`WRTC-2026`):** Defines scoring rules (fixed)
- **Log Year:** Source of log data (can be any year)
- **Example:** Apply `WRTC-2026` rules to 2024 IARU logs for practice analysis

### Shared Utilities Pattern
- **`_iaru_mult_utils.py`:** Shared HQ/Official parsing
- **IARU-HF:** Uses shared utilities + Zone parsing (IARU-specific)
- **WRTC:** Uses shared utilities + DXCC logic (WRTC-specific)

### Public Log Archive
- **IARU-HF and WRTC-2026:** Use same archive (`cn=iaruhf`)
- **Same functions:** `fetch_arrl_log_index(year, 'iaruhf')`
- **Different rules:** Applied after log loading

---

## Related Files

### New Files
- `contest_tools/core_annotations/_iaru_mult_utils.py` - Shared utilities
- `contest_tools/contest_definitions/wrtc_2026.json` - Standalone contest definition

### Modified Files
- `contest_tools/utils/log_fetcher.py` - Add IARU to contest codes
- `contest_tools/contest_specific_annotations/iaru_hf_multiplier_resolver.py` - Use shared utilities
- `contest_tools/contest_specific_annotations/wrtc_multiplier_resolver.py` - Use shared utilities
- `contest_tools/log_manager.py` - Remove `--wrtc` flag logic
- `web_app/analyzer/views.py` - Add WRTC-2026 to UI

### Files to Review/Remove
- `contest_tools/contest_definitions/wrtc.json` - May be obsolete (check if used)
- `contest_tools/contest_definitions/wrtc_2023.json` - Check if still needed
- `contest_tools/contest_definitions/wrtc_2025.json` - Check if still needed

---

## Dependencies

### External
- IARU public log archive (same as ARRL archive)
- `iaru_officials.dat` file (already exists in data/)

### Internal
- IARU-HF parser (`iaru_hf_parser`)
- IARU-HF ADIF exporter (`iaru_hf_adif`)
- WRTC calculator (`wrtc_calculator`)
- WRTC-2026 scoring (`wrtc_2026_scoring`)

---

## Success Criteria

1. ✅ WRTC-2026 appears as standalone contest in system
2. ✅ Can fetch IARU logs from public archive
3. ✅ Can apply WRTC-2026 rules to any year's IARU logs
4. ✅ Multiplier resolution uses shared utilities (no code duplication)
5. ✅ IARU-HF contest still works (no breaking changes)
6. ✅ No special-case logic (`--wrtc` flag removed)
7. ✅ Web UI supports contest/year selection

---

**Last Updated:** 2026-01-20
