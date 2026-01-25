# Louisiana QSO Party (LAQP) Implementation Plan

**Status:** Planning Phase  
**Date:** 2026-01-11  
**Last Updated:** 2026-01-11  
**Category:** Planning  
**Target Contest:** Louisiana QSO Party (LAQP)

---

## Executive Summary

This document outlines the implementation plan for adding the Louisiana QSO Party (LAQP) contest to the Contest Log Analyzer. LAQP presents several unique challenges that require custom plugins:

- **Asymmetric contest rules** (different rules for Louisiana vs non-Louisiana stations)
- **Rover stations** that can be worked from multiple parishes
- **Exchange-based location determination** (CTY.dat doesn't distinguish Louisiana)
- **Rover-aware duplicate checking** (must check callsign + band + parish)
- **Parish-based multipliers** (64 Louisiana parishes with 4-letter abbreviations)

This implementation will establish patterns reusable for other state/county QSO parties.

---

## Architecture Decisions

### Core Principle
**Handle contest-specific complexity in code, not JSON.** JSON provides simple configuration; Python modules handle the logic.

### Plugin Pattern
All custom logic follows the established plugin pattern:
- JSON specifies plugin name: `"custom_dupe_checker": "laqp_dupe_checker"`
- Python module implements the logic: `contest_tools/contest_specific_annotations/laqp_dupe_checker.py`
- Function signature matches existing patterns for consistency

### Default Behavior
- If no custom plugin specified → use standard/default behavior
- Custom plugins override standard behavior when specified
- This maintains backward compatibility

---

## Contest Rules Summary

### Basic Information
- **Contest Name:** `LAQP` (in Cabrillo header: `CONTEST: LAQP`)
- **Period:** 14:00 UTC Saturday to 02:00 UTC Sunday (12 hours)
- **Bands:** 160M, 80M, 40M, 20M, 15M, 10M, 6M, 2M (WARC excluded)
- **Modes:** CW, Phone, Digital (separate multipliers per mode)

### Asymmetric Participation
- **Louisiana stations:** Can work all stations
- **Non-Louisiana stations:** Can work only Louisiana stations

### Exchange Format
- **Louisiana stations send:** Callsign, RST, **Parish Abbreviation** (4-letter code, e.g., `ORLN`, `JEFF`)
- **Non-Louisiana stations send:** Callsign, RST, **State/Province/Country** (e.g., `MA`, `ON`, `DX`)

### Scoring
- **QSO Points:**
  - Phone: 2 points
  - CW/Digital: 4 points
- **Multipliers (per band/mode):**
  - **Non-Louisiana:** Louisiana parishes only (64 max per band/mode)
  - **Louisiana:** Louisiana parishes + US states (except LA) + Canadian provinces + DXCC entities
- **Final Score:** QSO points × total multipliers
- **Bonus:** 100 points for working N5LCC (one-time, not per QSO)

### Rover Rules
- Rovers can operate from multiple parishes
- Can be worked once per mode per band per parish activated
- Parish-line operations: Can log contacts for both parishes (separate QSO entries)
- No special callsign format required (use normal callsign)
- Identified by `CATEGORY-STATION: ROVER` in Cabrillo header

### Dupe Checking
- **Standard stations:** `(Call, Band, Mode)` - standard dupe check
- **Rover stations:** `(Call, Band, Mode, OperatingParish)` - must check parish from exchange
- Applies to both in-LA and out-LA stations working rovers

---

## Implementation Steps

### Phase 1: Infrastructure Setup

#### Step 1.1: Add Custom Dupe Checker Support to ContestLog
**File:** `contest_tools/contest_log.py`  
**Location:** In `apply_contest_specific_annotations()` method

**Changes:**
- Add hook to check for `custom_dupe_checker` in contest definition
- Call custom dupe checker after multiplier resolution, before scoring
- Follow same pattern as `custom_multiplier_resolver`

**Code Pattern:**
```python
# After multiplier resolution, before scoring
dupe_checker_name = self.contest_definition.custom_dupe_checker
if dupe_checker_name:
    try:
        dupe_checker_module = importlib.import_module(
            f"contest_tools.contest_specific_annotations.{dupe_checker_name}"
        )
        self.qsos_df = dupe_checker_module.check_dupes(
            self.qsos_df,
            self._my_location_type,
            self.root_input_dir,
            self.contest_definition
        )
        logging.info(f"Successfully applied '{dupe_checker_name}' dupe checker.")
    except Exception as e:
        logging.warning(f"Could not run '{dupe_checker_name}' dupe checker: {e}")
        # Fall back to standard dupe check (already done)
```

**Dependencies:** None (uses existing infrastructure)

**Testing:** Verify standard dupe checking still works when no custom checker specified

---

#### Step 1.2: Add custom_dupe_checker Property to ContestDefinition
**File:** `contest_tools/contest_definitions/__init__.py`

**Changes:**
- Add property method for `custom_dupe_checker`
- Follow same pattern as `custom_multiplier_resolver`

**Code:**
```python
@property
def custom_dupe_checker(self) -> Optional[str]:
    return self._data.get('custom_dupe_checker')
```

**Dependencies:** None

**Testing:** Verify property returns correct value from JSON

---

### Phase 2: Data Files

#### Step 2.1: Create LAQPParishes.dat
**File:** `CONTEST_LOGS_REPORTS/data/LAQPParishes.dat`  
**Format:** Same as `NAQPmults.dat` (alias:official_abbr (Full Name))

**Content:**
- 64 Louisiana parishes
- 4-letter abbreviations (e.g., `ACAD`, `ORLN`, `JEFF`)
- Full parish names
- No aliases needed initially (parish codes are standardized)

**Example Format:**
```
ACAD:ACAD (Acadia)
ALLN:ALLN (Allen)
ASCN:ASCN (Ascension)
ASMP:ASMP (Assumption)
AVLS:AVLS (Avoyelles)
...
```

**Source:** Official list from https://laqp.louisianacontestclub.org/la-parish-abbreviations/

**Dependencies:** None

**Testing:** Verify file loads correctly with `AliasLookup` utility

---

### Phase 3: Location Resolution

#### Step 3.1: Create laqp_location_resolver.py
**File:** `contest_tools/contest_specific_annotations/laqp_location_resolver.py`

**Purpose:** Determine if logger is Louisiana or non-Louisiana based on exchange data

**Function Signature:**
```python
def determine_location_type(sent_location: str, 
                           parish_lookup: AliasLookup,
                           state_prov_lookup: AliasLookup) -> str:
    """
    Determines if logger is Louisiana or non-Louisiana based on SentLocation.
    
    Returns:
        "LA" if SentLocation is a valid parish code
        "NON_LA" if SentLocation is a state/province/country code
        "UNKNOWN" if ambiguous or invalid
    """
```

**Logic:**
1. Check if `sent_location` matches a parish code (4-letter, check against `LAQPParishes.dat`)
2. If not, check if it matches state/province code (check against `NAQPmults.dat`)
3. Return appropriate location type

**Dependencies:**
- `LAQPParishes.dat`
- `NAQPmults.dat` (for state/province validation)
- `AliasLookup` utility

**Testing:**
- Test with valid parish codes → returns "LA"
- Test with state codes → returns "NON_LA"
- Test with ambiguous codes → returns "UNKNOWN"
- Test with invalid codes → returns "UNKNOWN"

**Integration:** Called from custom parser or multiplier resolver

---

### Phase 4: Parsing

#### Step 4.1: Create laqp_parser.py
**File:** `contest_tools/contest_specific_annotations/laqp_parser.py`

**Purpose:** Custom parser to handle exchange parsing and rover detection

**Function Signature:**
```python
def parse_log(filepath: str, contest_definition: ContestDefinition, 
              root_input_dir: str, cty_dat_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
```

**Key Features:**
1. **Header Scanning:**
   - Detect `CATEGORY-STATION: ROVER` for rover identification
   - Extract logger callsign

2. **Exchange Parsing:**
   - Use `exchange_parsing_rules` from JSON definition
   - Parse `SentLocation` and `RcvdLocation` from exchange
   - Handle both Louisiana (4-letter parish) and non-Louisiana (2-3 letter state/province) formats

3. **Rover Tracking:**
   - Store `SentLocation` as `OperatingParish` column for each QSO
   - This identifies which parish the rover was in for that specific QSO

4. **QSO Validation:**
   - Flag invalid QSOs (non-LA working non-LA) during parsing
   - Can set a flag column for later processing

**Exchange Parsing Rules (JSON):**
```json
"exchange_parsing_rules": {
  "LAQP": {
    "regex": "(\\d{3})\\s+([A-Z]{2,4})\\s+([A-Z0-9/]+)\\s+(\\d{3})\\s+([A-Z]{2,4})",
    "groups": [
      "SentRST",
      "SentLocation",
      "Call",
      "RST",
      "RcvdLocation"
    ]
  }
}
```

**Dependencies:**
- `exchange_parsing_rules` from JSON
- `parse_qso_common_fields` from `cabrillo_parser`
- Location resolver (for validation)

**Testing:**
- Test with Louisiana station log
- Test with non-Louisiana station log
- Test with rover log (multiple parishes)
- Test with invalid QSOs (non-LA working non-LA)

---

### Phase 5: Duplicate Checking

#### Step 5.1: Create Shared QSO Party Utilities
**File:** `contest_tools/contest_specific_annotations/_qso_party_utils.py`

**Purpose:** Reusable utilities for state/county QSO parties

**Functions:**
```python
def detect_rovers_by_location(df: pd.DataFrame,
                              location_column: str,
                              valid_locations: Set[str]) -> pd.Series:
    """
    Generic rover detection: stations with multiple unique locations.
    Returns boolean Series indicating which worked stations are rovers.
    """

def check_rover_aware_dupes_base(df: pd.DataFrame,
                                 location_column: str,
                                 is_rover_column: str = 'IsRover',
                                 dupe_scope: str = 'per_band') -> pd.DataFrame:
    """
    Generic rover-aware dupe checking.
    Returns new DataFrame with Dupe column updated.
    """
```

**Rationale:** Many QSO parties will need similar rover logic. Create reusable utilities.

**Dependencies:** None (pure utility functions)

**Testing:** Unit tests for rover detection and dupe checking logic

---

#### Step 5.2: Create laqp_dupe_checker.py
**File:** `contest_tools/contest_specific_annotations/laqp_dupe_checker.py`

**Purpose:** LAQP-specific duplicate checking with rover awareness

**Function Signature:**
```python
def check_dupes(df: pd.DataFrame, my_location_type: Optional[str],
                root_input_dir: str, contest_def: ContestDefinition) -> pd.DataFrame:
    """
    Performs rover-aware duplicate checking for LAQP.
    Returns new DataFrame with Dupe column updated.
    """
```

**Logic Flow:**
1. Load `LAQPParishes.dat` using `AliasLookup`
2. Detect rovers: Stations with multiple unique `RcvdLocation` values that are valid parishes
3. For rovers: Check dupes using `(Call, Band, Mode, RcvdLocation)`
4. For non-rovers: Check dupes using `(Call, Band, Mode)` (standard)
5. Return new DataFrame with updated `Dupe` column

**Performance Optimizations:**
- Cache rover detection results in `IsRover` column
- Use vectorized operations where possible
- Early exit if no rovers detected

**Dependencies:**
- `_qso_party_utils.py` (shared utilities)
- `LAQPParishes.dat`
- `AliasLookup` utility

**Testing:**
- Test with fixed station log (no rovers)
- Test with rover log (multiple parishes)
- Test with mixed log (some rovers, some fixed)
- Test with parish-line operations (same time, different parishes)
- Performance test with large log (1000+ QSOs)

---

### Phase 6: Multiplier Resolution

#### Step 6.1: Create laqp_multiplier_resolver.py
**File:** `contest_tools/contest_specific_annotations/laqp_multiplier_resolver.py`

**Purpose:** Resolve multipliers based on logger location (asymmetric rules)

**Function Signature:**
```python
def resolve_multipliers(df: pd.DataFrame, my_location_type: Optional[str],
                        root_input_dir: str, contest_def: ContestDefinition) -> pd.DataFrame:
```

**Logic:**

**For Non-Louisiana Stations:**
- Multiplier = Louisiana parishes only
- Source: `RcvdLocation` (parish code from Louisiana station)
- Validate: `RcvdLocation` must be valid parish code
- If not valid parish → invalid QSO (no multiplier, will get 0 points in scoring)

**For Louisiana Stations:**
- Multiple multiplier types:
  1. **Louisiana Parishes:** From `RcvdLocation` when working other LA stations, or from `SentLocation` when working non-LA stations
  2. **US States:** From `RcvdLocation` when working non-LA US stations (use `NAQPmults.dat`)
  3. **Canadian Provinces:** From `RcvdLocation` when working Canadian stations (use `NAQPmults.dat`)
  4. **DXCC Entities:** From DXCC lookup for DX stations

**Rover Handling:**
- For rovers, track which parish each QSO was from (`OperatingParish` or `RcvdLocation`)
- Same callsign in different parishes = separate multipliers

**Dependencies:**
- `LAQPParishes.dat`
- `NAQPmults.dat` (for states/provinces)
- `cty.dat` (for DXCC)
- `AliasLookup` utility
- Location resolver (to determine `my_location_type`)

**Testing:**
- Test non-LA station multiplier resolution
- Test LA station multiplier resolution (all types)
- Test rover multiplier counting
- Test invalid QSO handling (non-LA working non-LA)

---

### Phase 7: Scoring

#### Step 7.1: Create laqp_scoring.py
**File:** `contest_tools/contest_specific_annotations/laqp_scoring.py`

**Purpose:** Calculate QSO points with validation

**Function Signature:**
```python
def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
```

**Logic:**
1. **Validate QSO Eligibility:**
   - Non-LA stations working non-LA stations = 0 points (invalid QSO)
   - Check: If logger is non-LA AND `RcvdLocation` is not a valid parish code → invalid

2. **Calculate Base Points:**
   - Phone: 2 points
   - CW/Digital: 4 points
   - Dupes: 0 points (already flagged by dupe checker)
   - Invalid QSOs: 0 points

3. **N5LCC Bonus:**
   - Detect if `Call == "N5LCC"` (case-insensitive) anywhere in log
   - Count once per log (not per QSO)
   - Note: Bonus added to final score, not QSO points (handled separately)

**Dependencies:**
- `LAQPParishes.dat` (for validation)
- Location resolver (to determine logger location)
- `Dupe` column (from dupe checker)

**Testing:**
- Test point calculation (2 for phone, 4 for CW/Digital)
- Test dupe handling (0 points)
- Test invalid QSO handling (non-LA working non-LA = 0 points)
- Test N5LCC detection

---

### Phase 8: Contest Definition

#### Step 8.1: Create laqp.json
**File:** `contest_tools/contest_definitions/laqp.json`

**Structure:**
```json
{
  "_filename": "contest_tools/contest_definitions/laqp.json",
  "contest_name": "LAQP",
  "scoring_module": "laqp_scoring",
  "valid_bands": ["160M", "80M", "40M", "20M", "15M", "10M", "6M", "2M"],
  "dupe_check_scope": "per_band",
  "score_formula": "points_times_mults",
  "enable_adif_export": true,
  "custom_parser_module": "laqp_parser",
  "custom_multiplier_resolver": "laqp_multiplier_resolver",
  "custom_location_resolver": "laqp_location_resolver",
  "custom_dupe_checker": "laqp_dupe_checker",
  "exchange_parsing_rules": {
    "LAQP": {
      "regex": "(\\d{3})\\s+([A-Z]{2,4})\\s+([A-Z0-9/]+)\\s+(\\d{3})\\s+([A-Z]{2,4})",
      "groups": ["SentRST", "SentLocation", "Call", "RST", "RcvdLocation"]
    }
  },
  "multiplier_rules": [
    {
      "name": "Parishes",
      "value_column": "Mult1",
      "name_column": "Mult1Name",
      "totaling_method": "sum_by_band"
    },
    {
      "name": "States",
      "value_column": "Mult2",
      "name_column": "Mult2Name",
      "totaling_method": "sum_by_band",
      "applies_to": "LA"
    },
    {
      "name": "Provinces",
      "value_column": "Mult3",
      "name_column": "Mult3Name",
      "totaling_method": "sum_by_band",
      "applies_to": "LA"
    },
    {
      "name": "DXCC",
      "value_column": "Mult4",
      "name_column": "Mult4Name",
      "totaling_method": "sum_by_band",
      "applies_to": "LA"
    }
  ],
  "excluded_reports": [
    "text_wae_score_report",
    "text_wae_comparative_score_report"
  ],
  "default_qso_columns": [
    "ContestName", "MyCall", "Frequency", "Mode", "Datetime",
    "SentRST", "SentLocation", "Call", "RST", "RcvdLocation",
    "OperatingParish", "Band", "Date", "Hour", "Dupe",
    "DXCCName", "DXCCPfx", "Run", "QSOPoints",
    "Mult1", "Mult1Name", "Mult2", "Mult2Name",
    "Mult3", "Mult3Name", "Mult4", "Mult4Name"
  ]
}
```

**Dependencies:** All previous modules

**Testing:** Verify JSON loads correctly and all fields are accessible

---

## File Structure

```
contest_tools/
├── contest_definitions/
│   └── laqp.json                          # Contest definition
├── contest_specific_annotations/
│   ├── _qso_party_utils.py                # Shared QSO party utilities
│   ├── laqp_parser.py                     # Custom parser
│   ├── laqp_location_resolver.py          # Location determination
│   ├── laqp_dupe_checker.py               # Rover-aware dupe checking
│   ├── laqp_multiplier_resolver.py         # Asymmetric multiplier resolution
│   └── laqp_scoring.py                    # Point calculation & validation
└── contest_log.py                         # (Modified) Add dupe checker hook

CONTEST_LOGS_REPORTS/
└── data/
    └── LAQPParishes.dat                   # 64 parishes with abbreviations
```

---

## Testing Strategy

### Unit Tests

**For Each Module:**
1. Test with valid inputs
2. Test with edge cases (missing data, invalid codes, etc.)
3. Test error handling
4. Test performance with large datasets

**Specific Test Cases:**

**Location Resolver:**
- Valid parish code → "LA"
- Valid state code → "NON_LA"
- Invalid code → "UNKNOWN"
- Ambiguous code → "UNKNOWN"

**Parser:**
- Louisiana station log
- Non-Louisiana station log
- Rover log (multiple parishes)
- Invalid QSOs (non-LA working non-LA)

**Dupe Checker:**
- Fixed station (no rovers)
- Rover with multiple parishes
- Parish-line operations
- Mixed log (rovers + fixed)

**Multiplier Resolver:**
- Non-LA station (parishes only)
- LA station (all multiplier types)
- Rover multiplier counting
- Invalid QSO handling

**Scoring:**
- Point calculation (2/4 based on mode)
- Dupe handling (0 points)
- Invalid QSO handling (0 points)
- N5LCC bonus detection

### Integration Tests

1. **End-to-End Test:**
   - Load sample LAQP log
   - Run through full pipeline
   - Verify scores match expected values

2. **Rover Test:**
   - Load rover log with multiple parishes
   - Verify dupes checked correctly
   - Verify multipliers counted correctly

3. **Asymmetric Test:**
   - Test with LA station log
   - Test with non-LA station log
   - Verify different multiplier rules applied

### Regression Tests

- Verify existing contests still work (no breaking changes)
- Verify standard dupe checking still works when no custom checker specified

---

## Dependencies & Prerequisites

### Data Files Required
- `LAQPParishes.dat` (new, to be created)
- `NAQPmults.dat` (existing, for states/provinces)
- `cty.dat` (existing, for DXCC)
- `band_allocations.dat` (existing, for frequency validation)

### Code Dependencies
- `AliasLookup` utility (existing)
- `ContestDefinition` class (existing)
- `parse_qso_common_fields` (existing)
- Standard dupe checking (existing, as fallback)

### External Dependencies
- Official parish abbreviations list from laqp.org
- Sample LAQP Cabrillo logs for testing

---

## Edge Cases & Special Handling

### 1. Rover Detection Ambiguity
**Issue:** How to distinguish rover from fixed station with wrong exchange?  
**Solution:** Use `CATEGORY-STATION: ROVER` header as primary indicator, exchange analysis as validation

### 2. Parish-Line Operations
**Issue:** Same time, same station, different parishes  
**Solution:** Both are valid (different `RcvdLocation` values = different QSOs)

### 3. Invalid QSOs (Non-LA Working Non-LA)
**Issue:** Should these be filtered out or flagged?  
**Solution:** Flag with 0 points, keep in log for analysis/reporting

### 4. Missing Location Data
**Issue:** What if `RcvdLocation` is `pd.NA`?  
**Solution:** Treat as non-rover, use standard dupe check, may indicate invalid QSO

### 5. Ambiguous Location Codes
**Issue:** Code matches both parish and state?  
**Solution:** Prioritize parish codes (longer/more specific), or use lookup order

### 6. N5LCC Bonus
**Issue:** How to add bonus to final score?  
**Solution:** Detect in scoring module, add to final score calculation (not QSO points)

### 7. Performance with Large Logs
**Issue:** Rover detection requires grouping, could be slow  
**Solution:** Cache results, use vectorized operations, early exit if no rovers

---

## Implementation Order

### Recommended Sequence

1. **Phase 1:** Infrastructure (dupe checker hook, ContestDefinition property)
2. **Phase 2:** Data file (LAQPParishes.dat)
3. **Phase 3:** Location resolver (foundation for other modules)
4. **Phase 4:** Parser (needed for exchange data)
5. **Phase 5:** Dupe checker (needed before scoring)
6. **Phase 6:** Multiplier resolver (needed for scoring)
7. **Phase 7:** Scoring (depends on all previous)
8. **Phase 8:** Contest definition (ties everything together)

### Why This Order?

- **Infrastructure first:** Establishes the plugin pattern
- **Data file early:** Needed by multiple modules
- **Location resolver early:** Foundation for asymmetric logic
- **Parser before dupe checker:** Dupe checker needs parsed exchange data
- **Dupe checker before scoring:** Scoring depends on correct dupe flags
- **Multiplier resolver before scoring:** Scoring may need multiplier data
- **Contest definition last:** Requires all modules to be complete

---

## Future Considerations

### Reusability for Other QSO Parties

This implementation establishes patterns reusable for other state/county QSO parties:

1. **Shared Utilities:** `_qso_party_utils.py` can be extended for other contests
2. **Plugin Pattern:** Custom dupe checker pattern can be reused
3. **Exchange-Based Location:** Pattern for contests where CTY.dat is insufficient
4. **Rover Handling:** Generic rover detection and dupe checking logic

### Potential Enhancements

1. **Rover Detection Improvements:**
   - Configurable thresholds (min parishes to be considered rover)
   - Confidence scoring for rover detection

2. **Performance Optimizations:**
   - Caching rover detection across multiple logs
   - Parallel processing for large datasets

3. **Validation Enhancements:**
   - More detailed invalid QSO reporting
   - Warnings for ambiguous location codes

4. **Year-Specific Rules:**
   - Use WRTC overlay pattern if rules change year-to-year
   - Create `laqp_2025.json`, `laqp_2026.json` if needed

---

## Success Criteria

### Functional Requirements
- [ ] LAQP contest definition loads correctly
- [ ] Louisiana stations can work all stations
- [ ] Non-Louisiana stations can only work Louisiana stations (validation)
- [ ] Rover stations detected correctly
- [ ] Rover-aware dupe checking works correctly
- [ ] Multipliers resolved correctly for both LA and non-LA stations
- [ ] Points calculated correctly (2 for phone, 4 for CW/Digital)
- [ ] N5LCC bonus detected and added to final score
- [ ] Invalid QSOs (non-LA working non-LA) get 0 points

### Performance Requirements
- [ ] Processing time acceptable for logs with 1000+ QSOs
- [ ] Memory usage reasonable
- [ ] No significant performance regression for other contests

### Quality Requirements
- [ ] All modules follow existing code patterns
- [ ] Error handling is robust
- [ ] Logging provides useful diagnostics
- [ ] Code is well-documented
- [ ] Tests provide good coverage

---

## Questions & Decisions Needed

### Open Questions

1. **N5LCC Bonus Implementation:**
   - Should bonus be added in scoring module or time-series calculator?
   - Recommendation: Handle in scoring module, add to final score calculation

2. **Invalid QSO Reporting:**
   - Should invalid QSOs be included in reports with 0 points?
   - Recommendation: Yes, include for analysis/reporting purposes

3. **Rover Detection Threshold:**
   - Minimum number of unique parishes to be considered rover?
   - Recommendation: 2+ unique parishes, or header `CATEGORY-STATION: ROVER`

4. **Parish Data File Format:**
   - Include aliases or just official codes?
   - Recommendation: Start with official codes only, add aliases if needed

### Decisions Made

- ✅ Use exchange-based location determination (Option B)
- ✅ Custom dupe checker plugin pattern
- ✅ Return new DataFrame (immutability)
- ✅ Default to standard dupe checking if no custom checker specified
- ✅ Shared utilities for QSO party patterns
- ✅ Handle complexity in code, not JSON

---

## References

### Official Sources
- LAQP Rules: https://laqp.louisianacontestclub.org/laqso-rules-htm/
- Parish Abbreviations: https://laqp.louisianacontestclub.org/la-parish-abbreviations/

### Code References
- Multiplier Resolver Pattern: `naqp_multiplier_resolver.py`
- Custom Parser Pattern: `arrl_dx_parser.py`
- Scoring Module Pattern: `wae_scoring.py`
- Location Resolver Pattern: `wae_location_resolver.py`

### Documentation
- ProgrammersGuide.md: Section on adding contests
- Contributing.md: Coding standards and git workflow

---

## Notes for AI Agents

### Key Patterns to Follow

1. **Function Signatures:** Match existing patterns exactly
2. **Error Handling:** Use try/except with logging
3. **DataFrame Operations:** Return new DataFrame, don't modify in-place
4. **Logging:** Use appropriate log levels (info, warning, error)
5. **Type Hints:** Include type hints for all function parameters and returns

### Common Pitfalls to Avoid

1. **Don't modify DataFrame in-place:** Always return `df.copy()` or new DataFrame
2. **Don't assume location type:** Use location resolver, don't hardcode
3. **Don't forget rover detection:** Check for rovers before dupe checking
4. **Don't skip validation:** Always validate QSO eligibility
5. **Don't ignore edge cases:** Handle missing data, invalid codes, etc.

### Testing Checklist

Before considering implementation complete:
- [ ] Unit tests for each module
- [ ] Integration test with sample log
- [ ] Test with rover log
- [ ] Test with invalid QSOs
- [ ] Performance test with large log
- [ ] Regression test (other contests still work)

---

## Revision History

- **2026-01-11:** Initial plan created
- Future revisions will be tracked here
