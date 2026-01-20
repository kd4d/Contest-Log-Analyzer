# ARRL DX Contest Web Interface Implementation Plan

**Date:** 2026-01-17  
**Status:** Completed  
**Last Updated:** 2026-01-19  
**Context:** This plan focuses specifically on the web interface implementation for the asymmetrical ARRL DX Contest, building upon the backend implementation plan in `ARRL_DX_ASYMMETRIC_CONTEST_IMPLEMENTATION_PLAN.md`.

---

## Executive Summary

The ARRL DX Contest is an **asymmetric contest** where:
- **W/VE**: 48 contiguous US States + VE provinces
- **DX**: Everything else (including Alaska/KL7, Hawaii/KH6, and other US possessions)

**Key Web Interface Requirements:**
1. Contest selection (ARRL-DX-CW and ARRL-DX-SSB) in dropdown
2. Public log fetching (similar to ARRL-10, no mode selector needed)
3. Dashboard support (routing and display)
4. Asymmetric validation feedback (clear error messages when mixing W/VE and DX)
5. Location type indication in UI (optional but helpful)
6. QSO Dashboard support (band activity charts)

---

## Architecture Overview

### Current Web Interface Structure

The web interface follows this flow:
1. **Home Page** (`home.html`): Contest selection → Year → Mode (if needed) → Callsign selection
2. **Analysis Pipeline** (`views.py`): Upload/Fetch → Parse → Validate → Generate Reports
3. **Dashboard** (`dashboard.html`): Scoreboard, visualizations, reports
4. **QSO Dashboard** (`qso_dashboard.html`): QSO-level analysis, butterfly charts

### ARRL DX Specific Considerations

1. **No Mode Selector**: Mode is embedded in contest name (CW vs SSB)
2. **Asymmetric Validation**: Must prevent mixing W/VE and DX logs
3. **Dashboard Routing**: Must be added to supported contests list
4. **Public Log Fetch**: Uses ARRL public logs API (similar to ARRL-10)

---

## Implementation Tasks

### Task 1: Frontend - Contest Dropdown

**File:** `web_app/analyzer/templates/analyzer/home.html`

**Location:** Around line 199, in the `archiveContest` select element

**Required Change:**
Add ARRL DX options after ARRL-10:
```html
<option value="ARRL-10">ARRL 10 Meter</option>
<option value="ARRL-DX-CW">ARRL DX CW</option>
<option value="ARRL-DX-SSB">ARRL DX SSB</option>
```

**Rationale:**
- Users need to select which ARRL DX contest they want
- CW and SSB are separate contests (different scoring, different public logs)

---

### Task 2: Frontend - JavaScript Contest Handling

**File:** `web_app/analyzer/templates/analyzer/home.html`

**Location 1:** Around line 417, in contest selection event handler

**Required Change:**
Add ARRL DX handling:
```javascript
} else if (contest === 'ARRL-10') {
    yearSelect.disabled = false;
    modeSelect.disabled = true; // ARRL-10 has no modes
} else if (contest === 'ARRL-DX-CW' || contest === 'ARRL-DX-SSB') {
    yearSelect.disabled = false;
    modeSelect.disabled = true; // ARRL DX contests don't use mode selector
} else {
    yearSelect.disabled = true;
    modeSelect.disabled = true;
    slotsDiv.classList.add('d-none');
}
```

**Location 2:** Around line 481, in year selection event handler

**Required Change:**
Add ARRL DX to the list:
```javascript
if (contest === 'ARRL-10') {
    // ARRL-10: Fetch index when year is selected (no mode needed)
    fetchLogIndex();
} else if (contest === 'ARRL-DX-CW' || contest === 'ARRL-DX-SSB') {
    // ARRL DX: Fetch index when year is selected (no mode needed)
    fetchLogIndex();
} else if (contest === 'CQ-WW' || contest === 'CQ-160') {
    // CQ-WW and CQ-160: Enable mode selection after year is selected
    modeSelect.disabled = false;
}
```

**Location 3:** Around line 437, in `fetchLogIndex()` function

**Required Change:**
Update the condition to include ARRL DX:
```javascript
// CQ-WW and CQ-160 require mode, ARRL-10 and ARRL-DX don't
if ((contest === 'CQ-WW' || contest === 'CQ-160') && !mode) {
    return; // Wait for mode selection
}
```

**Rationale:**
- ARRL DX behaves like ARRL-10 (no mode selector, fetch index on year selection)
- Mode is determined by contest selection (CW vs SSB)

---

### Task 3: Backend - Log Index API

**File:** `web_app/analyzer/views.py`

**Location:** Around line 332, in `get_log_index_view()` function

**Required Change:**
Add ARRL DX handling after ARRL-10:
```python
elif contest == 'ARRL-10' and year:
    # ARRL 10 Meter doesn't have modes - contest code is '10m'
    try:
        from contest_tools.utils.log_fetcher import fetch_arrl_log_index, ARRL_CONTEST_CODES
        contest_code = ARRL_CONTEST_CODES.get('ARRL-10')
        if contest_code:
            callsigns = fetch_arrl_log_index(year, contest_code)
            return JsonResponse({'callsigns': callsigns})
        else:
            return JsonResponse({'error': 'ARRL-10 contest code not found'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
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

**Rationale:**
- ARRL DX needs `contest_name` parameter for disambiguation (CW vs SSB)
- Uses same pattern as ARRL-10 but with additional parameter

---

### Task 4: Backend - Log Download Handler

**File:** `web_app/analyzer/views.py`

**Location:** Around line 473, in `analyze_logs()` function, in the download section

**Required Change:**
Add ARRL DX handling after ARRL-10:
```python
elif contest == 'ARRL-10':
    from contest_tools.utils.log_fetcher import download_arrl_logs, ARRL_CONTEST_CODES
    contest_code = ARRL_CONTEST_CODES.get('ARRL-10')
    if contest_code:
        log_paths = download_arrl_logs(callsigns, year, contest_code, session_path)
    else:
        raise ValueError('ARRL-10 contest code not found')
elif contest in ['ARRL-DX-CW', 'ARRL-DX-SSB']:
    from contest_tools.utils.log_fetcher import download_arrl_logs, ARRL_CONTEST_CODES
    contest_code = ARRL_CONTEST_CODES.get(contest)
    if contest_code:
        log_paths = download_arrl_logs(callsigns, year, contest_code, session_path, contest_name=contest)
    else:
        raise ValueError(f'{contest} contest code not found')
```

**Rationale:**
- Pass `contest_name` parameter to distinguish CW from SSB
- Same error handling pattern as ARRL-10

---

### Task 5: Backend - Dashboard Routing

**File:** `web_app/analyzer/views.py`

**Location:** Around line 656, in `dashboard_view()` function

**Note:** Also update `_extract_contest_name_from_path()` to explicitly handle ARRL-DX (for consistency with CQ-160 pattern, even though uppercase conversion already works).

**Required Change:**
Add ARRL DX to supported contests with case-insensitive comparison:
```python
# Contest-Specific Routing
contest_name = context.get('contest_name', '').upper()  # Already uppercased, but explicit for clarity
# Enable same dashboard structure for CQ-WW, CQ-160, ARRL-10, and ARRL-DX
# CQ-160 is single-band, multi-mode (like ARRL-10), so it uses the same dashboard architecture
# ARRL-DX is multi-band, single-mode (like CQ-WW), so it uses the same dashboard architecture
if not (contest_name.startswith('CQ-WW') or 
        contest_name.startswith('CQ-160') or 
        contest_name.startswith('ARRL-10') or
        contest_name.startswith('ARRL-DX')):
    return render(request, 'analyzer/dashboard_construction.html', context)
```

**Note:** We use `.upper()` on `contest_name` for explicit case-insensitive comparison, even though it's likely already uppercase. This is defensive programming.

**Also Update:** `_extract_contest_name_from_path()` function (around line 742) - Add explicit comment for ARRL-DX (for consistency with CQ-160 pattern):

```python
def _extract_contest_name_from_path(report_rel_path: str) -> str:
    # ... existing code ...
    contest_name = contest_name_lower.upper().replace('_', '-')
    
    # Normalize CQ-160 variants (CQ-160-CW, CQ-160-SSB) to base contest name
    if contest_name.startswith('CQ-160-'):
        contest_name = 'CQ-160'
    
    # ARRL-DX-CW and ARRL-DX-SSB are separate contests (separate JSON files)
    # No normalization needed - uppercase conversion already handles them correctly
    # Explicit comment for clarity and consistency with CQ-160 pattern
    
    return contest_name
```

**Rationale:**
- ARRL DX should use the full dashboard (not construction page)
- Multi-band, single-mode structure similar to CQ-WW

---

### Task 6: Backend - Pre-Flight Validation (REQUIRED)

**File:** `web_app/analyzer/views.py`

**Location:** In `analyze_logs()` function, after saving/fetching logs but BEFORE `_run_analysis_pipeline()`

**Requirement:** Check location types BEFORE logs are processed. If mismatch, show error and stay on upload/fetch screen.

**Implementation:**

#### 6.1: Create Helper Function

Add new helper function (before `analyze_logs()`):
```python
def _validate_arrl_dx_location_types(log_paths: List[str], custom_cty_path: str = None, cty_specifier: str = 'after') -> Dict[str, Any]:
    """
    Pre-flight validation: Checks if all ARRL DX logs are from the same category (W/VE or DX).
    
    Returns:
        Dict with 'valid' (bool) and 'error_message' (str) keys
    """
    if len(log_paths) <= 1:
        return {'valid': True, 'error_message': None}
    
    # 1. Read headers to get contest name and callsigns
    headers = []
    for path in log_paths:
        header = _read_cabrillo_header(path)
        headers.append({
            'path': path,
            'contest': header.get('CONTEST', '').strip(),
            'callsign': header.get('CALLSIGN', '').strip(),
            'filename': os.path.basename(path)
        })
    
    # 2. Check if ARRL DX contest
    first_contest = headers[0]['contest']
    if first_contest not in ['ARRL-DX-CW', 'ARRL-DX-SSB']:
        return {'valid': True, 'error_message': None}  # Not ARRL DX, skip validation
    
    # 3. Determine CTY file (same logic as LogManager)
    cty_dat_path = _get_cty_file_for_validation(log_paths, custom_cty_path, cty_specifier)
    if not cty_dat_path:
        # If we can't determine CTY file, skip validation (will fail later anyway)
        return {'valid': True, 'error_message': None}
    
    # 4. Look up location types
    from contest_tools.core_annotations import CtyLookup
    cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
    location_types = []
    
    for header in headers:
        call = header['callsign']
        if not call:
            continue
        
        try:
            info = cty_lookup.get_cty_DXCC_WAE(call)._asdict()
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
                'filename': header['filename']
            })
        except Exception as e:
            logger.warning(f"Could not determine location type for {call}: {e}")
            continue
    
    # 5. Check for mismatch
    if len(location_types) < 2:
        return {'valid': True, 'error_message': None}  # Not enough logs to validate
    
    unique_location_types = set(item['location_type'] for item in location_types)
    if len(unique_location_types) > 1:
        # Mismatch found
        location_summary = ", ".join([
            f"{item['call']} ({item['location_type']})" 
            for item in location_types
        ])
        error_message = (
            "ARRL DX Contest Error: All logs must be from the same category.\n\n"
            "ARRL DX is an asymmetric contest:\n"
            "• W/VE = 48 contiguous US States + VE provinces\n"
            "• DX = Everything else (including Alaska, Hawaii, and other US possessions)\n\n"
            f"Found: {location_summary}"
        )
        return {'valid': False, 'error_message': error_message}
    
    return {'valid': True, 'error_message': None}

def _read_cabrillo_header(filepath: str) -> Dict[str, str]:
    """
    Lightweight header reader - only reads header lines, doesn't parse QSOs.
    Returns dict with header fields (CONTEST, CALLSIGN, etc.)
    """
    header = {}
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('QSO:'):
                    break  # End of header
                if ':' in line:
                    key, value = line.split(':', 1)
                    header[key.strip()] = value.strip()
    except Exception as e:
        logger.warning(f"Error reading header from {filepath}: {e}")
    return header

def _get_cty_file_for_validation(log_paths: List[str], custom_cty_path: str = None, cty_specifier: str = 'after') -> Optional[str]:
    """
    Determines CTY file for validation (same logic as LogManager).
    """
    if custom_cty_path and os.path.exists(custom_cty_path):
        return custom_cty_path
    
    # Read contest date from first log
    first_header = _read_cabrillo_header(log_paths[0])
    start_of_log = first_header.get('START-OF-LOG', '')
    
    if start_of_log:
        try:
            # Parse date from START-OF-LOG line (format: "START-OF-LOG: 3.0 CREATED-BY: N1MM Logger+ 1.0.9239.0 CALLSIGN: K3LR CONTEST: ARRL-DX-CW ...")
            # Date is typically in the line, but we need to extract it
            # For now, use CtyManager with default logic
            from contest_tools.utils.cty_manager import CtyManager
            cty_manager = CtyManager()
            # Use default 'after' specifier for now
            # Full implementation would parse date and use CtyManager.find_cty_file_by_date()
            # This is a simplified version - full implementation should match LogManager logic
            cty_dat_path, _ = cty_manager.find_cty_file_by_date(None, cty_specifier)
            if cty_dat_path:
                return cty_dat_path
        except Exception as e:
            logger.warning(f"Error determining CTY file: {e}")
    
    return None
```

#### 6.2: Integrate into Manual Upload Flow

**Location:** In `analyze_logs()`, after saving files (around line 396), before `_run_analysis_pipeline()`:

```python
# 3. Handle Custom CTY File (if uploaded)
custom_cty_path = None
cty_file_choice = form.cleaned_data.get('cty_file_choice', 'default')
if cty_file_choice == 'upload' and 'custom_cty_file' in request.FILES:
    cty_file = request.FILES['custom_cty_file']
    custom_cty_path = os.path.join(session_path, cty_file.name)
    with open(custom_cty_path, 'wb+') as destination:
        for chunk in cty_file.chunks():
            destination.write(chunk)
    logger.info(f"Custom CTY file uploaded: {cty_file.name}")

# 4. Pre-flight validation for ARRL DX (if multiple logs)
if len(log_paths) > 1:
    validation_result = _validate_arrl_dx_location_types(log_paths, custom_cty_path, cty_specifier='after')
    if not validation_result['valid']:
        return render(request, 'analyzer/home.html', {
            'form': form, 
            'error': validation_result['error_message']
        })

return _run_analysis_pipeline(request_id, log_paths, session_path, session_key, custom_cty_path=custom_cty_path)
```

#### 6.3: Integrate into Public Fetch Flow

**Location:** In `analyze_logs()`, after downloading logs (around line 463), before `_run_analysis_pipeline()`:

```python
elif contest in ['ARRL-DX-CW', 'ARRL-DX-SSB']:
    from contest_tools.utils.log_fetcher import download_arrl_logs, ARRL_CONTEST_CODES
    contest_code = ARRL_CONTEST_CODES.get(contest)
    if contest_code:
        log_paths = download_arrl_logs(callsigns, year, contest_code, session_path, contest_name=contest)
    else:
        raise ValueError(f'{contest} contest code not found')
else:
    raise ValueError(f'Unsupported contest: {contest}')

# Pre-flight validation for ARRL DX (if multiple logs)
if len(log_paths) > 1:
    validation_result = _validate_arrl_dx_location_types(log_paths, custom_cty_path, cty_specifier='after')
    if not validation_result['valid']:
        return render(request, 'analyzer/home.html', {
            'form': UploadLogForm(), 
            'error': validation_result['error_message']
        })

return _run_analysis_pipeline(request_id, log_paths, session_path, session_key, custom_cty_path=custom_cty_path)
```

**Rationale:**
- Validation happens BEFORE expensive log processing
- User sees error immediately, stays on upload/fetch screen
- Uses same location type logic as backend (consistent!)
- Clear error messages explain the issue

**Key Points:**
- Only validate if multiple logs AND ARRL DX contest
- Must determine CTY file (same logic as LogManager)
- Use lightweight header reader (doesn't parse full log)
- Return user-friendly error message

---

### Task 7: Location Type Display in Dashboard

**File:** `web_app/analyzer/views.py`

**Location:** In `dashboard_view()` function, when building context

**Required Change:**
Extract location type from log metadata and add to context:

```python
# After loading score reports data, extract location type
location_type = None
if lm and lm.logs:
    first_log_meta = lm.logs[0].get_metadata()
    location_type = first_log_meta.get('LocationType')  # Set by arrl_dx_location_resolver
    # Or extract from _my_location_type attribute if stored differently

# Add to context
context = {
    # ... existing context ...
    'location_type': location_type,  # 'W/VE' or 'DX' for ARRL DX, None for other contests
}
```

**File:** `web_app/analyzer/templates/analyzer/dashboard.html`

**Location:** In dashboard header, next to contest name

**Required Change:**
Display location type badge if available:

```html
<h2 class="mb-0 text-secondary">Analysis Results: <span class="text-dark">{{ full_contest_title }}</span>
    {% if location_type %}
        <span class="badge bg-{% if location_type == 'W/VE' %}primary{% else %}success{% endif %} ms-2">
            {{ location_type }}
        </span>
    {% endif %}
</h2>
```

**Rationale:**
- Helps users understand the analysis context
- Shows why certain comparisons are valid/invalid
- Visual indicator of contest category

---

### Task 8: QSO Dashboard Support

**File:** `web_app/analyzer/views.py`

**Location:** Around line 1386, in `qso_dashboard()` function

**Current State:**
The QSO dashboard automatically determines contest type from contest definition. ARRL DX should work automatically, but we should verify:

**Verification Points:**
1. Contest definition loads correctly (`arrl_dx_cw.json`, `arrl_dx_ssb.json`)
2. Valid bands are extracted correctly (multi-band)
3. Valid modes are extracted correctly (single-mode: CW or SSB)
4. Selector type is determined correctly (should be 'band' for multi-band, single-mode)
5. Activity tab label is correct (should be 'Band Activity')

**Expected Behavior:**
- ARRL DX is multi-band, single-mode
- Should use band selector (like CQ-WW)
- Should show "Band Activity" butterfly chart
- Should show "QSOs by Band" and "Points by Band" tabs

**Action Required:**
- Test QSO dashboard after implementing other tasks
- Verify all charts and selectors work correctly
- No code changes should be needed if contest definitions are correct

---

### Task 9: Frontend - Error Display Enhancement (Optional)

**File:** `web_app/analyzer/templates/analyzer/home.html`

**Location:** Wherever error messages are displayed

**Enhancement:**
If error messages contain newlines (from Task 6), ensure they're displayed correctly:
```html
{% if error %}
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
        <pre class="mb-0">{{ error }}</pre>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
{% endif %}
```

Or use CSS to preserve whitespace:
```css
.error-message {
    white-space: pre-wrap;
}
```

**Rationale:**
- Multi-line error messages need proper formatting
- Makes validation errors more readable

---

## Testing Checklist

### Test 1: Contest Selection
- [ ] Select "ARRL DX CW" → year dropdown enables, mode stays disabled
- [ ] Select "ARRL DX SSB" → year dropdown enables, mode stays disabled
- [ ] Select year → log index fetches automatically
- [ ] Verify callsigns appear in dropdown

### Test 2: Public Log Fetch
- [ ] Fetch ARRL DX CW log index for a year (e.g., 2024)
- [ ] Fetch ARRL DX SSB log index for a year
- [ ] Verify CW and SSB return different callsign lists
- [ ] Select callsigns and download logs
- [ ] Verify logs download correctly

### Test 3: Manual Upload
- [ ] Upload single ARRL DX CW log → should succeed
- [ ] Upload single ARRL DX SSB log → should succeed
- [ ] Upload 2 W/VE logs → should succeed
- [ ] Upload 2 DX logs → should succeed
- [ ] Upload 1 W/VE + 1 DX log → should fail with clear error message
- [ ] Verify error message explains W/VE vs DX

### Test 4: Dashboard Display
- [ ] Analyze ARRL DX CW log → dashboard loads correctly
- [ ] Analyze ARRL DX SSB log → dashboard loads correctly
- [ ] Verify scoreboard displays correctly
- [ ] Verify all report links work
- [ ] Verify location type is correct (W/VE or DX)

### Test 5: QSO Dashboard
- [ ] Navigate to QSO dashboard for ARRL DX
- [ ] Verify band selector appears (not mode selector)
- [ ] Verify "Band Activity" tab label
- [ ] Verify butterfly chart displays correctly
- [ ] Verify "QSOs by Band" and "Points by Band" tabs work
- [ ] Test band filtering

### Test 6: Error Handling
- [ ] Upload mixed W/VE and DX logs → verify error message is clear
- [ ] Verify error message explains asymmetric nature
- [ ] Verify error message shows which logs are which category
- [ ] Test with 3 logs (2 W/VE + 1 DX) → verify error

### Test 7: End-to-End
- [ ] Fetch public logs → download → analyze → dashboard works
- [ ] Upload manual logs → analyze → dashboard works
- [ ] Verify all reports generate correctly
- [ ] Verify location type classification is correct (Alaska = DX, etc.)

---

## Implementation Order

**Recommended Order:**
1. **Task 6**: Pre-flight validation (REQUIRED - must be first to prevent wasted processing)
2. **Task 1**: Frontend contest dropdown (foundation)
3. **Task 2**: Frontend JavaScript handling (enables UI flow)
4. **Task 3**: Backend log index API (enables public log fetch)
5. **Task 4**: Backend log download handler (completes public log fetch)
6. **Task 5**: Backend dashboard routing (enables dashboard display)
7. **Task 7**: Location type display (approved enhancement)
8. **Task 8**: QSO dashboard verification (testing, may not need changes)
9. **Task 9**: Frontend error display (optional enhancement)

**Rationale:**
- Task 6 must be first - prevents wasted processing if validation fails
- Tasks 1-2 enable the UI flow
- Tasks 3-4 enable public log fetching
- Task 5 enables dashboard display
- Task 7 shows location type (approved)
- Tasks 8-9 are verification/enhancement

---

## Dependencies

### Backend Dependencies (from `ARRL_DX_ASYMMETRIC_CONTEST_IMPLEMENTATION_PLAN.md`)

These must be completed first:
1. ✅ Task 1: Fix location resolver
2. ✅ Task 2: Fix scoring module
3. ✅ Task 3: Fix parser
4. ✅ Task 4: Add ingest-time validation (in LogManager - this is a backup, pre-flight validation is primary)
5. ✅ Task 5: Enable public log fetch (uncomment ARRL-DX entries in `log_fetcher.py`, add disambiguation logic)

**Note:** 
- The web interface implementation assumes these backend tasks are complete. If not, the web interface will not work correctly.
- **Task 5 is critical** - The `ARRL_CONTEST_CODES` dictionary must have ARRL-DX entries uncommented, and `_get_arrl_eid_iid()` must support disambiguation.
- Pre-flight validation (Task 6) uses the same location type logic as the backend, ensuring consistency.

---

## Edge Cases and Considerations

### Edge Case 1: Contest Name Format
- Contest names in context may be uppercase: `ARRL-DX-CW` vs `arrl-dx-cw`
- Dashboard routing uses `.startswith()` which is case-sensitive
- Ensure consistent case handling (use `.upper()` or `.lower()`)

### Edge Case 2: Public Log Fetch Failures
- ARRL website may be down or rate-limited
- Error handling should be graceful
- Show user-friendly error message

### Edge Case 3: Single Log Upload
- Validation only runs for multiple logs
- Single log upload should always work (no validation needed)
- Dashboard should still display correctly

### Edge Case 4: Mixed Upload Methods
- User uploads 1 log manually + fetches 1 log
- Validation should still catch W/VE + DX mismatch
- Error message should be clear

### Edge Case 5: Location Type Display
- Consider showing location type in dashboard (W/VE or DX)
- Could add to context or extract from logs
- Optional enhancement, not required

---

## UI/UX Considerations

### User Experience Flow

1. **Contest Selection:**
   - User selects "ARRL DX CW" or "ARRL DX SSB"
   - Year dropdown enables immediately
   - Mode selector stays disabled (mode is in contest name)

2. **Year Selection:**
   - User selects year
   - Log index fetches automatically
   - Callsign dropdowns populate

3. **Callsign Selection:**
   - User types/selects callsigns
   - Validation happens on backend (if mixing W/VE and DX)
   - Clear error message if validation fails

4. **Analysis:**
   - Progress bar shows steps
   - Dashboard loads on completion
   - Location type is implicit (not shown, but used for scoring)

### Error Message Design

**Good Error Message:**
```
ARRL DX Contest Error: All logs must be from the same category.

ARRL DX is an asymmetric contest:
• W/VE = 48 contiguous US States + VE provinces
• DX = Everything else (including Alaska, Hawaii, and other US possessions)

Found: K3LR (W/VE), KL7ABC (DX)
```

**Rationale:**
- Clear title
- Explains what asymmetric means
- Lists which logs are which category
- Actionable (user knows what to do)

---

## Files to Modify

1. `web_app/analyzer/templates/analyzer/home.html` (Tasks 1, 2, 9)
2. `web_app/analyzer/views.py` (Tasks 3, 4, 5, 6, 7)
3. `web_app/analyzer/templates/analyzer/dashboard.html` (Task 7 - location type display)

**Files to Verify (No Changes Expected):**
- `web_app/analyzer/templates/analyzer/qso_dashboard.html` (should work automatically)

---

## Success Criteria

1. ✅ ARRL DX CW and SSB appear in contest dropdown
2. ✅ Year selection enables log index fetch (no mode selector)
3. ✅ Public log fetch works for both CW and SSB
4. ✅ Pre-flight validation catches W/VE + DX mismatch BEFORE processing
5. ✅ Validation errors show on upload/fetch screen (user doesn't wait for processing)
6. ✅ Dashboard displays correctly for ARRL DX
7. ✅ Location type (W/VE or DX) displayed in dashboard header
8. ✅ QSO dashboard works correctly (band selector, charts)
9. ✅ Validation errors are clear and actionable
10. ✅ Single log upload works
11. ✅ Multiple same-category logs work
12. ✅ Mixed W/VE and DX logs are rejected with clear error (pre-flight)
13. ✅ End-to-end flow works (fetch → download → analyze → dashboard)

---

## Related Documents

- `DevNotes/ARRL_DX_ASYMMETRIC_CONTEST_IMPLEMENTATION_PLAN.md` - Backend implementation plan
- `contest_tools/contest_definitions/arrl_dx_cw.json` - ARRL DX CW definition
- `contest_tools/contest_definitions/arrl_dx_ssb.json` - ARRL DX SSB definition
- `web_app/analyzer/views.py` - Current web interface implementation
- `web_app/analyzer/templates/analyzer/home.html` - Home page template

---

## Notes for Implementation

1. **Test Incrementally:** Test each task as you complete it
2. **Backend First:** Ensure backend tasks are complete before web interface
3. **Error Messages:** Make validation errors user-friendly
4. **Consistency:** Follow existing patterns (ARRL-10 is a good reference)
5. **Dashboard:** ARRL DX should work automatically if contest definitions are correct

---

## Questions or Issues

If you encounter issues:
1. Verify backend tasks are complete
2. Check contest definitions are correct
3. Test with actual ARRL public logs
4. Verify location type logic is consistent
5. Check error messages are clear

Good luck with the implementation!
