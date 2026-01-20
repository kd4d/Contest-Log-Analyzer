# ARRL DX Web Interface - Discussion & Clarifications

**Date:** 2026-01-17  
**Status:** Resolved  
**Last Updated:** 2026-01-19  
**Context:** Clarifications and decisions for ARRL DX web interface implementation

---

## 1. Backend Status - Public Log Fetch

### Question Clarification

**What I meant:** The `ARRL_CONTEST_CODES` dictionary in `contest_tools/utils/log_fetcher.py` has ARRL-DX entries commented out (lines 40-41):

```python
ARRL_CONTEST_CODES = {
    'ARRL-10': '10m',
    # Add other ARRL contests as they're implemented
    # 'ARRL-DX-CW': 'dx',
    # 'ARRL-DX-SSB': 'dx',
}
```

**Discussion:** This is part of the **backend implementation** (Task 5 in `ARRL_DX_ASYMMETRIC_CONTEST_IMPLEMENTATION_PLAN.md`). The backend plan requires:
1. Uncommenting these lines
2. Adding disambiguation logic to `_get_arrl_eid_iid()` to distinguish CW from SSB
3. Updating function signatures to accept `contest_name` parameter

**Decision:** This is backend work, not web interface work. The web interface implementation assumes this backend work is complete. If it's not done, the web interface will fail when trying to fetch ARRL DX logs.

**Action:** Verify backend Task 5 is complete before implementing web interface Task 3 (log index API) and Task 4 (log download handler).

---

## 2. Contest Name Extraction - Explicit vs Implicit Handling

### Current Implementation

The `_extract_contest_name_from_path()` function currently:
1. Extracts contest name from path (e.g., `reports/2024/arrl-dx-cw/jan/k1lz`)
2. Uppercases it: `arrl-dx-cw` → `ARRL-DX-CW`
3. Has explicit normalization for CQ-160: `CQ-160-CW` → `CQ-160`

### Best Practice Analysis

**Option A: Implicit (Current Approach)**
- Uppercase conversion handles most cases
- Less code to maintain
- Works for ARRL-DX-CW and ARRL-DX-SSB automatically

**Option B: Explicit (Like CQ-160)**
- More explicit and clear intent
- Easier to understand for future developers
- Consistent with existing pattern (CQ-160 normalization)
- Better for debugging if path structure changes

### Recommendation: **Explicit Handling**

**Rationale:**
1. **Consistency:** We already have explicit handling for CQ-160, so ARRL-DX should follow the same pattern
2. **Clarity:** Makes it obvious that ARRL-DX-CW and ARRL-DX-SSB are separate contests (not normalized)
3. **Maintainability:** If path structure changes, explicit handling is easier to debug
4. **No Downside:** Minimal code, clear benefit

**Implementation:**
```python
def _extract_contest_name_from_path(report_rel_path: str) -> str:
    # ... existing code ...
    contest_name = contest_name_lower.upper().replace('_', '-')
    
    # Normalize CQ-160 variants (CQ-160-CW, CQ-160-SSB) to base contest name
    if contest_name.startswith('CQ-160-'):
        contest_name = 'CQ-160'
    
    # ARRL-DX-CW and ARRL-DX-SSB are separate contests, no normalization needed
    # (Explicit handling for clarity, even though uppercase conversion already works)
    # This makes it clear they are distinct contests, not variants of a base contest
    
    return contest_name
```

**Note:** Actually, since ARRL-DX-CW and ARRL-DX-SSB are separate contests (separate JSON files), we don't need normalization. The explicit comment is helpful for clarity.

---

## 3. Location Type Display in Dashboard

### Decision: **Yes, implement this**

**Implementation Approach:**
1. Extract location type from log metadata during analysis pipeline
2. Store in dashboard context JSON
3. Display as badge/indicator in dashboard header

**Details:**
- Location type is determined by `arrl_dx_location_resolver` during log processing
- Stored in `ContestLog.metadata` (via `_my_location_type` attribute)
- Can be extracted from `lm.logs[0].get_metadata().get('LocationType')` or similar
- Display format: Badge showing "W/VE" or "DX" in dashboard header

**UI Design:**
- Small badge next to contest name
- Color coding: W/VE (blue), DX (green) or similar
- Tooltip explaining what it means

---

## Concerns & Solutions

### Concern 1: Pre-Flight Validation (REQUIRED)

**Requirement:** Check location types **BEFORE** logs are processed. If mismatch, show error on upload/fetch screen (don't proceed to analysis).

**Current Flow:**
1. User uploads/fetches logs
2. Logs saved to session directory
3. `_run_analysis_pipeline()` called
4. `LogManager.load_log_batch()` processes logs
5. Validation happens inside `LogManager` (too late!)

**Required Flow:**
1. User uploads/fetches logs
2. Logs saved to session directory
3. **NEW: Pre-flight validation** - Check location types
4. If valid → proceed to `_run_analysis_pipeline()`
5. If invalid → show error, stay on upload/fetch screen

**Implementation Strategy:**

#### For Manual Upload:
```python
# In analyze_logs(), after saving files but before _run_analysis_pipeline()
if len(log_paths) > 1:
    # Pre-flight validation for ARRL DX
    contest_name = _get_contest_name_from_first_log(log_paths[0])
    if contest_name in ['ARRL-DX-CW', 'ARRL-DX-SSB']:
        validation_result = _validate_arrl_dx_location_types(
            log_paths, custom_cty_path, cty_specifier='after'
        )
        if not validation_result['valid']:
            # Show error, stay on upload screen
            return render(request, 'analyzer/home.html', {
                'form': form, 
                'error': validation_result['error_message']
            })
```

#### For Public Fetch:
```python
# In analyze_logs(), after downloading logs but before _run_analysis_pipeline()
if len(log_paths) > 1:
    # Same validation logic
    contest_name = contest  # We know it from the form
    if contest_name in ['ARRL-DX-CW', 'ARRL-DX-SSB']:
        validation_result = _validate_arrl_dx_location_types(
            log_paths, custom_cty_path, cty_specifier='after'
        )
        if not validation_result['valid']:
            return render(request, 'analyzer/home.html', {
                'form': UploadLogForm(), 
                'error': validation_result['error_message']
            })
```

**Helper Function:**
```python
def _validate_arrl_dx_location_types(log_paths: List[str], custom_cty_path: str = None, cty_specifier: str = 'after') -> Dict[str, Any]:
    """
    Pre-flight validation: Checks if all ARRL DX logs are from the same category (W/VE or DX).
    
    Returns:
        Dict with 'valid' (bool) and 'error_message' (str) keys
    """
    # 1. Determine CTY file (similar to LogManager logic)
    # 2. Read headers to get callsigns
    # 3. Look up location types
    # 4. Check for mismatch
    # 5. Return validation result
```

**Key Points:**
- Must happen **before** `LogManager.load_log_batch()`
- Only validate if multiple logs AND ARRL DX contest
- Use same location type logic as backend (consistent!)
- Clear error message with which logs are which category

---

### Concern 2: Case-Insensitive Dashboard Routing

**Current Implementation:**
```python
contest_name = context.get('contest_name', '').upper()
if not (contest_name.startswith('CQ-WW') or contest_name.startswith('CQ-160') or contest_name.startswith('ARRL-10')):
    return render(request, 'analyzer/dashboard_construction.html', context)
```

**Issue:** `.startswith()` is case-sensitive, but we already uppercase `contest_name`. However, for robustness, we should make the comparison explicitly case-insensitive.

**Recommendation:** Use `.upper()` on both sides for explicit case-insensitive comparison:

```python
contest_name = context.get('contest_name', '').upper()
if not (contest_name.startswith('CQ-WW') or 
        contest_name.startswith('CQ-160') or 
        contest_name.startswith('ARRL-10') or
        contest_name.startswith('ARRL-DX')):
    return render(request, 'analyzer/dashboard_construction.html', context)
```

**Rationale:**
- We already uppercase `contest_name`, so this is defensive programming
- Makes intent clear: case-insensitive comparison
- If `contest_name` comes from a different source in the future, it still works
- Minimal performance impact

---

### Concern 3: ARRL Website Changes

**Decision:** No fallback logic. If ARRL website changes, code must be updated. User workaround: download logs locally and upload manually.

**Rationale:**
- Fallback logic adds complexity
- ARRL website changes are infrequent
- Manual upload is always available
- Simpler codebase is better

**Action:** Document this in code comments and user-facing error messages.

---

### Concern 4: Mixed Upload/Fetch

**Decision:** Not supported. User must use either:
- All manual uploads, OR
- All public fetch

**Rationale:**
- Simplifies validation logic
- Clearer user experience
- Current codebase doesn't support it anyway

**Action:** No code changes needed - current implementation already enforces this (separate form branches).

---

## Optional Enhancements Still Viable

After removing pre-flight validation from "optional" (it's now required), here's what remains:

### 1. Location Type Display in Dashboard ✅ (Approved)
- Show W/VE or DX badge in dashboard header
- Extract from log metadata
- Display next to contest name

### 2. Enhanced Error Formatting (Optional)
- Better formatting for validation errors
- Use Bootstrap alerts with icons
- Table showing which logs are which category
- **Status:** Nice to have, not required

### 3. Help Text/Tooltips (Optional)
- Tooltip explaining asymmetric nature when ARRL DX selected
- Help text in contest dropdown
- Link to contest rules
- **Status:** Nice to have, not required

### 4. Pre-Flight Validation API (Optional Enhancement)
- Could add AJAX endpoint to check location types as user selects callsigns
- Real-time feedback before submission
- **Status:** Advanced feature, defer to future

---

## Additional Concerns & Questions

### 1. Contest Name Extraction from Headers

**Question:** For pre-flight validation, we need to read contest name from log headers. Should we:
- A) Use existing `LogManager._get_contest_name_from_header()` method (if accessible)
- B) Create a lightweight header reader utility
- C) Reuse existing Cabrillo parser header reading logic

**Recommendation:** Option B - Create lightweight utility function that only reads headers (doesn't parse full log). This is faster and doesn't require full log parsing.

**Implementation:**
```python
def _read_cabrillo_header(filepath: str) -> Dict[str, str]:
    """
    Lightweight header reader - only reads header lines, doesn't parse QSOs.
    Returns dict with header fields (CONTEST, CALLSIGN, etc.)
    """
    header = {}
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('QSO:'):
                if line.startswith('QSO:'):
                    break  # End of header
                continue
            if ':' in line:
                key, value = line.split(':', 1)
                header[key.strip()] = value.strip()
    return header
```

### 2. CTY File Selection for Pre-Flight Validation

**Question:** Pre-flight validation needs CTY file to look up location types. Should we:
- A) Use same CTY selection logic as LogManager (determine from contest date)
- B) Always use default CTY file
- C) Use custom CTY if provided, otherwise default

**Recommendation:** Option A - Use same logic as LogManager for consistency. This means:
1. Read contest date from first log header
2. Use CtyManager to find appropriate CTY file
3. Use custom CTY if provided

**Implementation:**
```python
def _get_cty_file_for_validation(log_paths: List[str], custom_cty_path: str = None, cty_specifier: str = 'after') -> str:
    """
    Determines CTY file for validation (same logic as LogManager).
    """
    if custom_cty_path and os.path.exists(custom_cty_path):
        return custom_cty_path
    
    # Read contest date from first log
    first_header = _read_cabrillo_header(log_paths[0])
    contest_date_str = first_header.get('START-OF-LOG', '').split()[0] if 'START-OF-LOG' in first_header else None
    
    if contest_date_str:
        # Parse date and use CtyManager
        # (Similar to LogManager logic)
        pass
    
    # Fallback to default
    return default_cty_path
```

### 3. Error Message Format

**Question:** Should validation errors be:
- A) Plain text (current approach)
- B) Formatted with HTML (Bootstrap alerts)
- C) Structured JSON for JavaScript handling

**Recommendation:** Option A for now (plain text), but use `white-space: pre-wrap` CSS to preserve line breaks. Option B (Bootstrap alerts) can be added as optional enhancement.

**Current Error Display:**
```html
{% if error %}
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ error }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
{% endif %}
```

**Enhanced (Optional):**
```html
{% if error %}
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
        <h5><i class="bi bi-exclamation-triangle me-2"></i>Validation Error</h5>
        <pre class="mb-0">{{ error }}</pre>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
{% endif %}
```

---

## Implementation Priority

### Phase 1: Core Functionality (Required)
1. ✅ Pre-flight validation (before LogManager)
2. ✅ Contest dropdown (ARRL-DX-CW, ARRL-DX-SSB)
3. ✅ JavaScript handling (no mode selector)
4. ✅ Backend log index API
5. ✅ Backend log download handler
6. ✅ Dashboard routing (case-insensitive)
7. ✅ Location type display in dashboard

### Phase 2: Polish (Optional)
1. Enhanced error formatting
2. Help text/tooltips
3. Pre-flight validation API (AJAX)

---

## Summary of Decisions

1. **Backend Status:** Verify Task 5 complete before web interface work
2. **Contest Name Extraction:** Explicit handling (like CQ-160) for clarity
3. **Location Type Display:** ✅ Implement in dashboard
4. **Pre-Flight Validation:** ✅ REQUIRED - before LogManager
5. **Dashboard Routing:** Case-insensitive comparison (use `.upper()`)
6. **ARRL Website Changes:** No fallback, document workaround
7. **Mixed Upload/Fetch:** Not supported (already enforced)
8. **Error Formatting:** Plain text with `pre-wrap` CSS (enhancement optional)

---

## Next Steps

1. Verify backend Task 5 (public log fetch) is complete
2. Implement pre-flight validation helper function
3. Integrate pre-flight validation into `analyze_logs()`
4. Implement core web interface tasks (1-7)
5. Test with actual ARRL DX logs
6. Add optional enhancements if time permits
