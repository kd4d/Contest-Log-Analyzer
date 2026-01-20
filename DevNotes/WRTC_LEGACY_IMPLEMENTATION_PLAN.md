# WRTC Legacy Contest Implementation Plan (2018, 2022)

**Date:** 2026-01-20  
**Status:** Active  
**Last Updated:** 2026-01-20  
**Category:** Planning

---

## Overview

This document outlines the implementation plan for adding legacy WRTC contest support (WRTC-2018 and WRTC-2022) following the WRTC-2026 standalone contest architecture pattern.

**Key Architectural Decision:**
- WRTC-2018 and WRTC-2022 are **standalone contests** (not overlays or variants)
- Each contest name (e.g., `WRTC-2018`, `WRTC-2022`) defines fixed scoring rules
- Log year is a separate parameter (can apply WRTC rules to any year's IARU logs)
- Uses same public log archive as IARU-HF
- Follows the pattern established in WRTC-2026 implementation

---

## Current State Analysis

### Existing WRTC Contest Definitions

1. **WRTC-2026** ✅ (Standalone, complete)
   - File: `contest_tools/contest_definitions/wrtc_2026.json`
   - Scoring: `wrtc_2026_scoring.py`
   - Status: Fully implemented, follows new architecture

2. **WRTC-2022** ✅ (Renamed from 2023, converted to standalone)
   - File: `contest_tools/contest_definitions/wrtc_2022.json`
   - Scoring: `wrtc_2022_scoring.py`
   - Status: ✅ Converted to standalone pattern (same rules as WRTC-2026)
   - **Note:** Contest was held in 2023 due to COVID, but rules are for 2022

3. **WRTC-2018** ❌ (Does not exist)
   - Needs to be created from scratch
   - **Note:** Rules may differ from 2022/2026 - needs research

### Existing Scoring Modules

1. **`wrtc_2026_scoring.py`** ✅
   - Points: 2 (EU) / 5 (non-EU) - same for CW and SSB
   - Europe-only rule enforced

2. **`wrtc_2022_scoring.py`** ✅ (Renamed from 2023, legacy implementation)
   - Points: CW: 2 (EU) / 5 (non-EU), SSB: 3 (EU) / 6 (non-EU)
   - Europe-only rule enforced
   - **Note:** Legacy implementation with mode-specific points (different from 2026)

---

## Implementation Tasks

### Task 1: Research and Document WRTC-2018 Rules

**Status:** ✅ Completed

**Rules Confirmed:**
- Points: Within Europe 2, Outside Europe 5 (uniform for both CW and SSB, same as 2026)
- Multipliers: DXCC Countries, HQ Stations, IARU Officials (max 4 per band: AC, R1, R2, R3)
- Rule 8.2: HQ/Officials do not count for DXCC multipliers (mutually exclusive)
- Score: Total multipliers × Sum of QSO points
- Once per band regardless of mode
- Europe-only rule enforced
- Bands: 80M, 40M, 20M, 15M, 10M
- Modes: CW and SSB only

---

### Task 2: Convert WRTC-2022 to Standalone Pattern

**Status:** ✅ Completed

**Completed Actions:**
- ✅ Renamed `wrtc_2023.json` → `wrtc_2022.json`
- ✅ Renamed `wrtc_2023_scoring.py` → `wrtc_2022_scoring.py`
- ✅ Converted from inheritance pattern to standalone (removed `inherits_from`)
- ✅ Restored legacy WRTC-2022 scoring (mode-specific: CW 2/5, SSB 3/6)
- ✅ Updated contest name to "WRTC-2022"
- ✅ Deleted `wrtc_2025.json` (does not exist)

**Rules Confirmed (Legacy Implementation):**
- Points: CW: Within Europe 2, Outside Europe 5; SSB: Within Europe 3, Outside Europe 6
- Multipliers: DXCC Countries, HQ Stations, IARU Officials (once per band, no mode)
- Rule 8.2: HQ/Officials do not count for DXCC multipliers
- Score: Total multipliers × Sum of QSO points
- **Note:** Contest was held in 2023 due to COVID, but rules are for 2022
- **Note:** Different from WRTC-2026 (2022 has mode-specific points, 2026 has uniform points)

---

### Task 3: Create WRTC-2018 Contest Definition

**Status:** ✅ Completed

**File:** `contest_tools/contest_definitions/wrtc_2018.json`

**Pattern:** WRTC-2026 standalone pattern (no inheritance)

**Required Fields:**
```json
{
  "_filename": "contest_tools/contest_definitions/wrtc_2018.json",
  "contest_name": "WRTC-2018",
  "valid_modes": ["CW", "PH"],  // Confirm: likely no DG
  "valid_bands": ["80M", "40M", "20M", "15M", "10M"],
  "scoring_module": "wrtc_2018_scoring",  // NEW module
  "time_series_calculator": "wrtc_calculator",
  "custom_multiplier_resolver": "wrtc_multiplier_resolver",
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
  "mutually_exclusive_mults": [
    ["Mult_DXCC", "Mult_HQ", "Mult_Official"]
  ],
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
  "default_qso_columns": [/* same as WRTC-2026 */]
}
```

**Dependencies:**
- Task 1 (Research WRTC-2018 rules)
- Task 4 (Create scoring module)

---

### Task 4: Create WRTC-2018 Scoring Module

**Status:** ✅ Completed

**File:** `contest_tools/contest_specific_annotations/wrtc_2018_scoring.py`

**Pattern:** `wrtc_2026_scoring.py` (uniform points: 2/5 for both modes)

**Implementation:**
- Points: Within Europe 2, Outside Europe 5 (same for CW and SSB)
- Europe-only rule enforced
- Same as WRTC-2026 scoring rules

---

### Task 5: Handle WRTC-2022 (Rename or Create)

**Status:** ✅ Completed

**Actions Taken:**
- ✅ Renamed `wrtc_2023.json` → `wrtc_2022.json`
- ✅ Converted to standalone pattern (removed inheritance)
- ✅ Renamed `wrtc_2023_scoring.py` → `wrtc_2022_scoring.py`
- ✅ Restored legacy WRTC-2022 scoring (mode-specific: CW 2/5, SSB 3/6)
- ✅ Deleted `wrtc_2025.json` (does not exist)

**Rules (Legacy Implementation):**
- CW: 2 points (EU) / 5 points (non-EU)
- SSB: 3 points (EU) / 6 points (non-EU)
- Multipliers: DXCC + HQ + Officials (once per band, no mode)
- Europe-only rule enforced
- **Note:** Different from WRTC-2026 (mode-specific vs uniform points)

---

### Task 6: Update WRTC Contest Discovery API

**File:** `web_app/analyzer/views.py`

**Current State:**
- `get_wrtc_contests_view()` filters to only show contests with year-specific scoring modules
- Pattern: `wrtc_(\d{4})\.json` → expects `wrtc_YYYY_scoring.py`

**Required Changes:**
- No changes needed if following naming pattern
- API will automatically discover new contests once files are created

**Verification:**
- Test that WRTC-2018 and WRTC-2022 appear in dropdown after implementation

---

### Task 7: Remove Old Inheritance-Based Definitions (Cleanup)

**Status:** ✅ Completed

**Actions Taken:**
- ✅ Deleted `wrtc_2025.json` (does not exist)
- ✅ Converted `wrtc_2022.json` from inheritance to standalone (removed `inherits_from`)
- ⏳ Keep `wrtc.json` for now (may be referenced elsewhere, review after WRTC-2018 implementation)

**Remaining:**
- `wrtc.json` - Base definition (review if still needed after all migrations complete)

---

### Task 8: Testing

**Test Cases:**

1. **WRTC-2018:**
   - [ ] Load IARU-HF log from 2018 (or any year)
   - [ ] Select WRTC-2018 from dropdown
   - [ ] Verify scoring matches expected rules
   - [ ] Verify multipliers counted correctly
   - [ ] Verify Europe-only rule enforced
   - [ ] Verify score calculation (points × multipliers)

2. **WRTC-2022:**
   - [ ] Load IARU-HF log from 2022 (or any year)
   - [ ] Select WRTC-2022 from dropdown
   - [ ] Verify scoring matches expected rules
   - [ ] Verify multipliers counted correctly
   - [ ] Verify Europe-only rule enforced
   - [ ] Verify score calculation

3. **UI:**
   - [ ] Verify WRTC-2018 appears in dropdown
   - [ ] Verify WRTC-2022 appears in dropdown
   - [ ] Verify only implemented contests shown (filter works)
   - [ ] Verify public log archive works for IARU-HF → WRTC selection

4. **Regression:**
   - [ ] Verify WRTC-2026 still works
   - [ ] Verify IARU-HF still works
   - [ ] Verify no breaking changes

---

## Implementation Order

1. **✅ Completed:**
   - Task 1: Research WRTC-2018 rules
   - Task 2: Converted WRTC-2022 to standalone pattern
   - Task 3: Created WRTC-2018 contest definition
   - Task 4: Created WRTC-2018 scoring module
   - Task 5: Renamed and updated WRTC-2022
   - Task 7: Removed WRTC-2025 placeholder

2. **Remaining Work:**
   - Task 8: Comprehensive testing (WRTC-2018 and WRTC-2022)

---

## Success Criteria

1. ✅ WRTC-2018 appears as standalone contest in system
2. ✅ WRTC-2022 appears as standalone contest in system
3. ✅ Can fetch IARU logs from public archive for any year
4. ✅ Can apply WRTC-2022 rules to any year's IARU logs
5. ✅ Can apply WRTC-2018 rules to any year's IARU logs
6. ✅ WRTC-2022 scoring matches historical contest rules (mode-specific: CW 2/5, SSB 3/6)
7. ✅ WRTC-2018 scoring matches historical contest rules (uniform: 2/5 for both modes)
8. ✅ Multiplier resolution uses shared utilities (no code duplication)
9. ✅ IARU-HF and WRTC-2026 still work (no breaking changes)
10. ✅ No special-case logic (all follow WRTC-2026 pattern)
11. ✅ Web UI supports contest selection for WRTC-2022
12. ✅ Web UI supports contest selection for WRTC-2018
13. ✅ Only implemented contests appear in dropdown (filter works)

---

## Implementation Summary

**WRTC-2018 Rules (Confirmed):**
- Points: Within Europe 2, Outside Europe 5 (uniform for both CW and SSB)
- Multipliers: DXCC Countries, HQ Stations, IARU Officials (max 4 per band: AC, R1, R2, R3)
- Rule 8.2: HQ/Officials do not count for DXCC multipliers
- Score: Total multipliers × Sum of QSO points
- Once per band regardless of mode
- Europe-only rule enforced

**WRTC Scoring Comparison:**
- **WRTC-2018:** Uniform points (2/5) - same as 2026
- **WRTC-2022:** Mode-specific points (CW: 2/5, SSB: 3/6) - legacy implementation
- **WRTC-2026:** Uniform points (2/5) - same as 2018

**Testing:**
- Real logs available for 2018 and 2023 (under WRTC-2022 rules)
- Can use these to validate WRTC-2018 and WRTC-2022 scoring

---

## Related Documentation

- `DevNotes/Archive/WRTC_2026_IMPLEMENTATION_PLAN.md` - WRTC-2026 implementation reference
- `contest_tools/contest_definitions/wrtc_2026.json` - Reference implementation
- `contest_tools/contest_specific_annotations/wrtc_2026_scoring.py` - Scoring reference
- `contest_tools/core_annotations/_iaru_mult_utils.py` - Shared multiplier utilities
- `DevNotes/Decisions_Architecture/SHARED_IARU_MULTIPLIER_UTILITIES_PATTERN.md` - Pattern documentation

---

**Last Updated:** 2026-01-20
