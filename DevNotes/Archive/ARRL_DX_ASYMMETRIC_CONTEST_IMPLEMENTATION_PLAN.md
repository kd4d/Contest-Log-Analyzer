# ARRL DX Asymmetric Contest Implementation Plan

**Date:** 2026-01-17  
**Status:** Completed  
**Last Updated:** 2026-01-19  
**Context:** ARRL DX is an asymmetric contest where only logs from the same category (W/VE or DX) can be compared. This plan documents the required fixes to properly implement this.

---

## Overview

ARRL DX Contest has asymmetric rules:
- **W/VE**: 48 contiguous US States + VE provinces
- **DX**: Everything else, including Alaska (KL7), Hawaii (KH6), and other US possessions (CY9, CY0)

**Key Requirement:** All logs in a batch must be from the same category (all W/VE or all DX). This must be validated at ingest time because multipliers and scoring differ between categories.

---

## Implementation Tasks

### Task 1: Fix Location Resolver (Alaska/Hawaii Classification)

**File:** `contest_tools/contest_specific_annotations/arrl_dx_location_resolver.py`

**Current Issue:**
- Line 30: `return "W/VE" if info.get('DXCCName') in ["United States", "Canada"] else "DX"`
- This incorrectly classifies Alaska (KL7) and Hawaii (KH6) as W/VE
- They should be DX

**Required Change:**
```python
def resolve_location_type(metadata: Dict[str, Any], cty_dat_path: str) -> Optional[str]:
    """
    Determines if the logger is W/VE or DX for the ARRL DX contest.
    
    W/VE = 48 contiguous US States + VE provinces
    DX = Everything else, including Alaska (KL7), Hawaii (KH6), and other US possessions (CY9, CY0)
    """
    my_call = metadata.get('MyCall')
    if not my_call:
        return None

    cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
    info = cty_lookup.get_cty_DXCC_WAE(my_call)._asdict()
    
    dxcc_pfx = info.get('DXCCPfx', '')
    dxcc_name = info.get('DXCCName', '')
    
    # Check for Alaska, Hawaii, and US possessions - these are DX, not W/VE
    if dxcc_pfx in ['KH6', 'KL7', 'CY9', 'CY0']:
        return "DX"
    
    # W/VE = 48 contiguous US States + Canada provinces
    # Note: Alaska and Hawaii are part of "United States" in DXCC but have prefixes KH6/KL7
    if dxcc_name in ["United States", "Canada"]:
        return "W/VE"
    
    return "DX"
```

**Key Points:**
- Check `DXCCPfx` first for Alaska/Hawaii/US possessions (KH6, KL7, CY9, CY0)
- These are DX even though `DXCCName` is "United States"
- Then check `DXCCName` for United States/Canada (these are W/VE)
- Everything else is DX

---

### Task 2: Fix Scoring Module

**File:** `contest_tools/contest_specific_annotations/arrl_dx_scoring.py`

**Current Issue:**
- Line 53: `my_location_type = "W/VE" if my_entity_name in ["United States", "Canada"] else "DX"`
- Same issue: doesn't handle Alaska/Hawaii correctly
- Also needs to check `DXCCPfx` for logger's own location

**Required Change:**
```python
def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on ARRL DX rules.
    
    W/VE = 48 contiguous US States + VE provinces
    DX = Everything else, including Alaska (KL7), Hawaii (KH6), and other US possessions (CY9, CY0)
    """
    my_dxcc_pfx = my_call_info.get('DXCCPfx', '')
    my_entity_name = my_call_info.get('DXCCName')
    if not my_entity_name:
        raise ValueError("Logger's own DXCC Name must be provided for scoring.")
    
    # Same logic as arrl_dx_location_resolver
    if my_dxcc_pfx in ['KH6', 'KL7', 'CY9', 'CY0']:
        my_location_type = "DX"
    elif my_entity_name in ["United States", "Canada"]:
        my_location_type = "W/VE"
    else:
        my_location_type = "DX"

    return df.apply(
        _calculate_single_qso_points, 
        axis=1,
        my_location_type=my_location_type
    )
```

**Key Points:**
- Use same logic as location resolver
- Check `DXCCPfx` first, then `DXCCName`
- `_calculate_single_qso_points` already handles worked station correctly (lines 30-35)

---

### Task 3: Fix Parser

**File:** `contest_tools/contest_specific_annotations/arrl_dx_parser.py`

**Current Issue:**
- Line 60: `logger_location_type = "W/VE" if info['DXCCName'] in ["United States", "Canada"] else "DX"`
- Same issue: doesn't handle Alaska/Hawaii correctly

**Required Change:**
```python
    logging.info(f"  - Extracted logger callsign: {logger_call}")
    cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
    info = cty_lookup.get_cty_DXCC_WAE(logger_call)._asdict()
    
    # Determine location type: W/VE = 48 contiguous US States + VE provinces
    # DX = Everything else, including Alaska (KL7), Hawaii (KH6), and other US possessions (CY9, CY0)
    dxcc_pfx = info.get('DXCCPfx', '')
    dxcc_name = info.get('DXCCName', '')
    
    if dxcc_pfx in ['KH6', 'KL7', 'CY9', 'CY0']:
        logger_location_type = "DX"
    elif dxcc_name in ["United States", "Canada"]:
        logger_location_type = "W/VE"
    else:
        logger_location_type = "DX"
    
    logging.info(f"  - Determined logger location type: '{logger_location_type}'")
```

**Key Points:**
- Use same logic as location resolver and scoring
- This determines which exchange parsing rule to use (W/VE vs DX format)
- Critical for correct parsing

---

### Task 4: Add Ingest-Time Validation in LogManager

**File:** `contest_tools/log_manager.py`

**Current State:**
- No validation to prevent mixing W/VE and DX logs
- This must be added in `load_log_batch()` method

**Required Change:**
Add validation after CTY file selection (around line 141, after CTY file is determined) but before full log loading (before line 147).

**Location:** After line 141 (`logging.info(f"Using CTY file...")`), before line 142 (`# --- 2.5. Create Shared Instances`)

**Implementation:**
```python
        # --- 2.5. ARRL DX Location Type Validation (if applicable) ---
        # For ARRL DX contests, ensure all logs are from the same category (W/VE or DX)
        # This must happen after CTY file selection so we can determine location types
        if log_filepaths and len(log_filepaths) > 1 and cty_dat_path:
            first_contest = None
            if header_data:
                first_contest = header_data[0].get('contest')
            else:
                first_contest = self._get_contest_name_from_header(log_filepaths[0])
                if wrtc_year and first_contest == 'IARU-HF':
                    first_contest = f"WRTC-{wrtc_year}"
            
            if first_contest in ['ARRL-DX-CW', 'ARRL-DX-SSB']:
                logging.info("ARRL DX contest detected. Validating location type consistency...")
                location_types = []
                temp_cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
                
                # Use header_data if available, otherwise read from files
                data_to_check = header_data if header_data else [
                    {'call': self._get_callsign_from_header(path), 'filename': os.path.basename(path)} 
                    for path in log_filepaths
                ]
                
                for item in data_to_check:
                    call = item['call']
                    info = temp_cty_lookup.get_cty_DXCC_WAE(call)._asdict()
                    dxcc_pfx = info.get('DXCCPfx', '')
                    dxcc_name = info.get('DXCCName', '')
                    
                    # Same logic as arrl_dx_location_resolver
                    if dxcc_pfx in ['KH6', 'KL7', 'CY9', 'CY0']:
                        location_type = "DX"
                    elif dxcc_name in ["United States", "Canada"]:
                        location_type = "W/VE"
                    else:
                        location_type = "DX"
                    
                    location_types.append({
                        'call': call,
                        'location_type': location_type,
                        'filename': item.get('filename', os.path.basename(item.get('call', 'Unknown')))
                    })
                
                unique_location_types = set(item['location_type'] for item in location_types)
                if len(unique_location_types) > 1:
                    location_summary = ", ".join([
                        f"{item['call']} ({item['location_type']})" 
                        for item in location_types
                    ])
                    raise ValueError(
                        f"ARRL DX Location Type Mismatch: All logs must be from the same category (W/VE or DX). "
                        f"Found: {location_summary}. "
                        f"W/VE = 48 contiguous US States + VE provinces. "
                        f"DX = Everything else (including Alaska, Hawaii, and other US possessions)."
                    )
                else:
                    common_location_type = list(unique_location_types)[0]
                    logging.info(f"All ARRL DX logs are from category: {common_location_type}")
```

**Key Points:**
- Only validate if multiple logs AND ARRL DX contest
- Must happen after CTY file is selected (needed for lookup)
- Use same location type logic as resolver/scoring/parser
- Raise `ValueError` with clear message if mismatch
- Log success if all logs are same category

**Required Imports:**
- Ensure `CtyLookup` is imported (should already be at top of file)
- Ensure `os` is imported (should already be at top of file)

---

### Task 5: Enable Public Log Fetch for ARRL DX

**File:** `contest_tools/utils/log_fetcher.py`

**Current State:**
- Lines 40-41: ARRL-DX-CW and ARRL-DX-SSB are commented out
- Need to uncomment and implement disambiguation logic

**Required Changes:**

#### 5.1: Uncomment Contest Codes
```python
ARRL_CONTEST_CODES = {
    'ARRL-10': '10m',
    'ARRL-DX-CW': 'dx',
    'ARRL-DX-SSB': 'dx',
    # Add other ARRL contests as they're implemented
}
```

#### 5.2: Update `_get_arrl_eid_iid()` Function

**Current Signature:** `def _get_arrl_eid_iid(year: str, contest_code: str) -> Optional[Tuple[str, str]]:`

**Required Change:** Add optional `contest_name` parameter:
```python
def _get_arrl_eid_iid(year: str, contest_code: str, contest_name: str = None) -> Optional[Tuple[str, str]]:
    """
    Discovers the event ID (eid) and instance ID (iid) for a given ARRL contest and year.
    
    Args:
        year: Year as string (e.g., '2024')
        contest_code: ARRL contest code (e.g., '10m', 'dx')
        contest_name: Optional contest name for disambiguation (e.g., 'ARRL-DX-CW', 'ARRL-DX-SSB')
                      Used when contest_code is 'dx' to distinguish between CW and Phone
        
    Returns:
        Tuple of (eid, iid) if found, None otherwise
    """
```

**Implementation Logic:**
After loading selector page (around line 228), add disambiguation logic:

```python
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # For ARRL DX (cn=dx), we need to distinguish between CW and Phone
        # They have different eid values. Try to find the eid from the dropdown or use known values
        if contest_code == 'dx' and contest_name:
            is_cw = 'CW' in contest_name.upper() or contest_name == 'ARRL-DX-CW'
            is_phone = 'SSB' in contest_name.upper() or 'PHONE' in contest_name.upper() or contest_name == 'ARRL-DX-SSB'
            
            # Try to find the eid from the dropdown select options
            select = soup.find('select')
            if select:
                for option in select.find_all('option'):
                    option_text = option.get_text().strip().upper()
                    option_value = option.get('value', '')
                    
                    # Check if this option matches our contest
                    if is_cw and ('DX CW' in option_text or 'INTERNATIONAL DX CW' in option_text):
                        # Extract eid from option value if it's a URL
                        if 'eid=' in option_value:
                            match = re.search(r'eid=(\d+)', option_value)
                            if match:
                                eid_from_option = match.group(1)
                                # Now navigate to that eid page to get year links
                                eid_url = f"{ARRL_PUBLICLOGS_URL}?eid={eid_from_option}"
                                response = requests.get(eid_url, timeout=10)
                                response.raise_for_status()
                                soup = BeautifulSoup(response.text, 'html.parser')
                                break
                    elif is_phone and ('DX PHONE' in option_text or 'INTERNATIONAL DX PHONE' in option_text):
                        if 'eid=' in option_value:
                            match = re.search(r'eid=(\d+)', option_value)
                            if match:
                                eid_from_option = match.group(1)
                                eid_url = f"{ARRL_PUBLICLOGS_URL}?eid={eid_from_option}"
                                response = requests.get(eid_url, timeout=10)
                                response.raise_for_status()
                                soup = BeautifulSoup(response.text, 'html.parser')
                                break
        
        # Find year links - they appear as links with year text
        year_links = soup.find_all('a', href=True, string=re.compile(rf'^{year}$'))
```

**Key Points:**
- Check if `contest_code == 'dx'` and `contest_name` is provided
- Determine if CW or Phone from contest_name
- Scrape dropdown to find matching option
- Extract eid from option value
- Navigate to eid page to get year links
- Continue with existing year link extraction logic

#### 5.3: Update Function Signatures

Update these functions to accept `contest_name` parameter:

1. **`fetch_arrl_log_index()`:**
   ```python
   def fetch_arrl_log_index(year: str, contest_code: str, contest_name: str = None) -> List[str]:
   ```
   - Pass `contest_name` to `_get_arrl_eid_iid()` call

2. **`fetch_arrl_log_mapping()`:**
   ```python
   def fetch_arrl_log_mapping(year: str, contest_code: str, contest_name: str = None) -> Dict[str, str]:
   ```
   - Pass `contest_name` to `_get_arrl_eid_iid()` call

3. **`download_arrl_logs()`:**
   ```python
   def download_arrl_logs(callsigns: List[str], year: str, contest_code: str, output_dir: str, contest_name: str = None) -> List[str]:
   ```
   - Pass `contest_name` to `fetch_arrl_log_mapping()` call

**Update all internal calls** to pass `contest_name` parameter through the chain.

---

### Task 6: UI Integration

#### 6.1: Backend - `get_log_index_view()`

**File:** `web_app/analyzer/views.py`

**Location:** Around line 313, in `get_log_index_view()` function

**Required Change:**
Add ARRL DX handling after ARRL-10 handling (around line 343):

```python
    elif contest in ['ARRL-DX-CW', 'ARRL-DX-SSB'] and year:
        # ARRL DX CW and SSB use contest code 'dx' but need contest_name for disambiguation
        try:
            from contest_tools.utils.log_fetcher import fetch_arrl_log_index, ARRL_CONTEST_CODES
            contest_code = ARRL_CONTEST_CODES.get(contest)
            if contest_code:
                callsigns = fetch_arrl_log_index(year, contest_code, contest_name=contest)
                return JsonResponse({'callsigns': callsigns})
            else:
                return JsonResponse({'error': f'{contest} contest code not found'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
```

**Key Points:**
- Handle both 'ARRL-DX-CW' and 'ARRL-DX-SSB'
- Pass `contest_name=contest` to `fetch_arrl_log_index()`
- Error handling same as ARRL-10

#### 6.2: Backend - `analyze_logs()`

**File:** `web_app/analyzer/views.py`

**Location:** Around line 473, in `analyze_logs()` function, in the download section

**Required Change:**
Add ARRL DX handling after ARRL-10 handling:

```python
                elif contest in ['ARRL-DX-CW', 'ARRL-DX-SSB']:
                    from contest_tools.utils.log_fetcher import download_arrl_logs, ARRL_CONTEST_CODES
                    contest_code = ARRL_CONTEST_CODES.get(contest)
                    if contest_code:
                        log_paths = download_arrl_logs(callsigns, year, contest_code, session_path, contest_name=contest)
                    else:
                        raise ValueError(f'{contest} contest code not found')
```

**Key Points:**
- Handle both 'ARRL-DX-CW' and 'ARRL-DX-SSB'
- Pass `contest_name=contest` to `download_arrl_logs()`
- Error handling same as ARRL-10

#### 6.3: Frontend - Contest Dropdown

**File:** `web_app/analyzer/templates/analyzer/home.html`

**Location:** Around line 200, in the `archiveContest` select element

**Required Change:**
Add options after ARRL-10:
```html
<option value="ARRL-DX-CW">ARRL DX CW</option>
<option value="ARRL-DX-SSB">ARRL DX SSB</option>
```

#### 6.4: Frontend - JavaScript Logic

**File:** `web_app/analyzer/templates/analyzer/home.html`

**Location:** Around line 422, in contest selection event handler

**Required Change:**
Add ARRL DX handling:
```javascript
} else if (contest === 'ARRL-DX-CW' || contest === 'ARRL-DX-SSB') {
    yearSelect.disabled = false;
    modeSelect.disabled = true; // ARRL DX contests don't use mode selector
```

**Location:** Around line 486, in year selection event handler

**Required Change:**
Add ARRL DX to the list:
```javascript
if (contest === 'ARRL-10' || contest === 'ARRL-DX-CW' || contest === 'ARRL-DX-SSB') {
    // ARRL contests: Fetch index when year is selected (no mode needed)
    fetchLogIndex();
```

**Key Points:**
- ARRL DX doesn't need mode selector (mode is in contest name)
- Fetch log index when year is selected (same as ARRL-10)
- Mode is already determined by contest selection (CW vs SSB)

---

## Location Type Logic (Consistent Across All Files)

**Critical:** The same logic must be used in all four places:
1. `arrl_dx_location_resolver.py`
2. `arrl_dx_scoring.py`
3. `arrl_dx_parser.py`
4. `log_manager.py` (validation)

**Logic:**
```python
dxcc_pfx = info.get('DXCCPfx', '')
dxcc_name = info.get('DXCCName', '')

# Check for Alaska, Hawaii, and US possessions - these are DX, not W/VE
if dxcc_pfx in ['KH6', 'KL7', 'CY9', 'CY0']:
    location_type = "DX"
# W/VE = 48 contiguous US States + Canada provinces
elif dxcc_name in ["United States", "Canada"]:
    location_type = "W/VE"
else:
    location_type = "DX"
```

**Key Rules:**
- **W/VE**: 48 contiguous US States + VE provinces
- **DX**: Everything else, including:
  - Alaska (KL7 prefix)
  - Hawaii (KH6 prefix)
  - Other US possessions (CY9, CY0 prefixes)
  - All non-US/Canada entities

---

## Testing Checklist

### Test 1: Location Type Classification
- [ ] Test Alaska (KL7) → should be DX
- [ ] Test Hawaii (KH6) → should be DX
- [ ] Test US possession (CY9, CY0) → should be DX
- [ ] Test 48-state US → should be W/VE
- [ ] Test Canada (VE) → should be W/VE
- [ ] Test DX entity → should be DX

### Test 2: Ingest-Time Validation
- [ ] Test: Upload 2 W/VE logs → should succeed
- [ ] Test: Upload 2 DX logs → should succeed
- [ ] Test: Upload 1 W/VE + 1 DX log → should fail with clear error message
- [ ] Test: Upload 3 logs (2 W/VE + 1 DX) → should fail
- [ ] Test: Single log (no validation needed) → should succeed

### Test 3: Scoring
- [ ] Test: W/VE logger working DX → 3 points
- [ ] Test: W/VE logger working W/VE → 0 points
- [ ] Test: DX logger working W/VE → 3 points
- [ ] Test: DX logger working DX → 0 points
- [ ] Test: Alaska logger (DX) working W/VE → 3 points
- [ ] Test: Hawaii logger (DX) working W/VE → 3 points

### Test 4: Public Log Fetch
- [ ] Test: Fetch ARRL DX CW log index for a year
- [ ] Test: Fetch ARRL DX SSB log index for a year
- [ ] Test: Download ARRL DX CW logs
- [ ] Test: Download ARRL DX SSB logs
- [ ] Test: Verify CW and SSB are correctly distinguished

### Test 5: UI Integration
- [ ] Test: Select ARRL DX CW → year dropdown enables
- [ ] Test: Select ARRL DX SSB → year dropdown enables
- [ ] Test: Select year → log index fetches
- [ ] Test: Select callsigns → download works
- [ ] Test: Analyze downloaded logs → works correctly

### Test 6: End-to-End
- [ ] Test: Upload ARRL DX CW log → analyze → reports generated
- [ ] Test: Upload ARRL DX SSB log → analyze → reports generated
- [ ] Test: Fetch public logs → download → analyze → works
- [ ] Test: Mixed W/VE and DX logs → validation catches it

---

## Implementation Order

**Recommended Order:**
1. **Task 1**: Fix location resolver (foundation)
2. **Task 2**: Fix scoring (depends on location type)
3. **Task 3**: Fix parser (depends on location type)
4. **Task 4**: Add validation (uses location type logic)
5. **Task 5**: Enable public log fetch (independent)
6. **Task 6**: UI integration (depends on Task 5)

**Rationale:**
- Tasks 1-4 are core logic fixes (must be consistent)
- Task 5 is independent (public log fetch)
- Task 6 depends on Task 5 (UI uses public log fetch)

---

## Edge Cases and Important Notes

### Edge Case 1: Single Log Upload
- Validation only runs if `len(log_filepaths) > 1`
- Single log doesn't need validation (nothing to compare)

### Edge Case 2: Header Data Availability
- Validation should use `header_data` if available (from pre-flight validation)
- Fallback to reading from files if `header_data` is empty
- This handles both code paths

### Edge Case 3: CTY File Required
- Validation only runs if `cty_dat_path` is set
- Location type determination requires CTY lookup
- Validation must happen after CTY file selection

### Edge Case 4: Public Log Fetch Disambiguation
- ARRL DX CW and SSB both use `cn=dx` parameter
- They have different `eid` values
- Must scrape dropdown to find correct `eid` based on contest name
- Fallback: Could use known eid values if scraping fails (not implemented)

### Edge Case 5: Error Messages
- Validation error must be clear and actionable
- Include which logs are which category
- Explain what W/VE and DX mean

---

## Files to Modify

1. `contest_tools/contest_specific_annotations/arrl_dx_location_resolver.py`
2. `contest_tools/contest_specific_annotations/arrl_dx_scoring.py`
3. `contest_tools/contest_specific_annotations/arrl_dx_parser.py`
4. `contest_tools/log_manager.py`
5. `contest_tools/utils/log_fetcher.py`
6. `web_app/analyzer/views.py`
7. `web_app/analyzer/templates/analyzer/home.html`

---

## Success Criteria

1. ✅ Alaska, Hawaii, US possessions correctly classified as DX
2. ✅ 48-state US and Canada correctly classified as W/VE
3. ✅ Ingest-time validation prevents mixing W/VE and DX logs
4. ✅ Clear error message when validation fails
5. ✅ Public log fetch works for both ARRL DX CW and SSB
6. ✅ UI correctly handles ARRL DX contests
7. ✅ End-to-end: upload → analyze → reports works
8. ✅ End-to-end: fetch → download → analyze works

---

## Related Documents

- `DevNotes/DIRECTORY_STRUCTURE_REFACTORING_FUTURE_WORK.md` - Discussion of premature refactoring (not needed)
- `TECHNICAL_DEBT.md` - WRTC architecture (deferred)
- `contest_tools/contest_definitions/arrl_dx_cw.json` - ARRL DX CW definition
- `contest_tools/contest_definitions/arrl_dx_ssb.json` - ARRL DX SSB definition

---

## Notes for Implementation Agent

1. **Consistency is Critical:** The location type logic must be identical in all four files (resolver, scoring, parser, validation)

2. **Test Incrementally:** Test each task as you complete it, don't wait until the end

3. **Error Messages:** Make validation error messages user-friendly and actionable

4. **Public Log Fetch:** The disambiguation logic is the trickiest part - test thoroughly with actual ARRL website

5. **Backward Compatibility:** These changes should not break existing functionality for other contests

6. **No Directory Structure Changes:** Do NOT change directory structure - use existing structure (`reports/{year}/{contest_name}/{event_id}/{callsign}/`)

---

## Questions or Issues During Implementation

If you encounter issues:
1. Check that location type logic is consistent across all files
2. Verify CTY file is available before validation
3. Test public log fetch with actual ARRL website (may have rate limiting)
4. Ensure error messages are clear and helpful

Good luck with the implementation!
