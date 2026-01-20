# ARRL DX Public Log Archive Issues - Analysis

**Date:** 2026-01-17  
**Status:** Resolved  
**Last Updated:** 2026-01-19  
**Context:** Analysis of reported issues with ARRL DX public log archive selector

---

## Issue Summary

### Issue 1: "ARRL DX is not listed in supported contests"

**Status:** ✅ **Actually Listed** - ARRL DX is in the dropdown (lines 200-201 of `home.html`)

**Possible Causes:**
- Browser cache - user needs to refresh page
- User looking at wrong section of UI
- JavaScript error preventing dropdown from populating

**Verification:**
- Check browser console for JavaScript errors
- Hard refresh (Ctrl+F5) to clear cache
- Verify dropdown shows: "ARRL DX CW" and "ARRL DX SSB"

---

### Issue 2: "ARRL DX CW/SSB in dropdown AND mode selector exists"

**Status:** ⚠️ **Partially Fixed** - Mode selector should be disabled, but there's a bug

**Root Cause:**
The mode selector is always visible in the HTML (lines 210-218), but should be **disabled** for ARRL DX. The JavaScript correctly disables it on contest selection (line 424), but:

1. **The mode selector is always visible** - it's not hidden, just disabled
2. **`enableAllFormControls()` function** (line 657-658) doesn't handle ARRL-DX - only handles ARRL-10
3. **User might be seeing it enabled** if form gets reset or re-enabled

**Fix Applied:**
- Updated `enableAllFormControls()` to also disable mode selector for ARRL-DX (line 657)

**Remaining Issue:**
- Mode selector is still **visible** (just disabled). For better UX, we could hide it entirely for ARRL DX, but that's a UI enhancement, not a bug.

**Recommendation:**
- Current behavior (disabled but visible) is acceptable
- If user wants it hidden, we can add CSS/JavaScript to hide it for ARRL DX

---

### Issue 3: "No callsign matches when selecting ARRL DX CW, 2025, CW"

**Status:** ❌ **Backend Not Complete** - This is expected until backend Task 5 is done

**Root Cause Analysis:**

1. **ARRL-DX entries are commented out** in `log_fetcher.py` (lines 40-41):
   ```python
   ARRL_CONTEST_CODES = {
       'ARRL-10': '10m',
       # 'ARRL-DX-CW': 'dx',  # ← Still commented out!
       # 'ARRL-DX-SSB': 'dx',  # ← Still commented out!
   }
   ```

2. **When API is called:**
   - `ARRL_CONTEST_CODES.get('ARRL-DX-CW')` returns `None`
   - Code checks `if contest_code:` (line 513)
   - Returns error: `f'{contest} contest code not found'` (line 517)

3. **Error handling issue:**
   - JavaScript might not be showing the error properly
   - Error might be silently failing

4. **Function signature mismatch:**
   - `fetch_arrl_log_index()` only accepts `year` and `contest_code`
   - Backend plan requires adding `contest_name` parameter for disambiguation
   - This hasn't been implemented yet

**What Needs to Happen:**

1. **Uncomment ARRL-DX entries** in `log_fetcher.py`:
   ```python
   ARRL_CONTEST_CODES = {
       'ARRL-10': '10m',
       'ARRL-DX-CW': 'dx',  # ← Uncomment
       'ARRL-DX-SSB': 'dx',  # ← Uncomment
   }
   ```

2. **Update `_get_arrl_eid_iid()`** to accept `contest_name` parameter and add disambiguation logic (per backend Task 5)

3. **Update `fetch_arrl_log_index()`** to accept `contest_name` parameter

4. **Update `fetch_arrl_log_mapping()`** to accept `contest_name` parameter

5. **Update `download_arrl_logs()`** to accept `contest_name` parameter

**Current State:**
- Web interface code is ready (expects `contest_name` parameter)
- Backend code is NOT ready (entries commented out, no disambiguation logic)

---

## Fixes Applied

### Fix 1: Improved Error Handling in JavaScript

**File:** `web_app/analyzer/templates/analyzer/home.html`

**Change:** Enhanced error handling in `fetchLogIndex()` to:
- Check for `data.error` in response
- Show alert with error message
- Handle empty callsign list
- Better error messages

**Result:** Users will now see clear error messages when backend isn't ready

### Fix 2: Mode Selector in `enableAllFormControls()`

**File:** `web_app/analyzer/templates/analyzer/home.html`

**Change:** Added ARRL-DX handling to ensure mode selector stays disabled

**Result:** Mode selector won't get incorrectly enabled when form is reset

---

## Recommendations

### Immediate Actions:

1. **Uncomment ARRL-DX entries** in `log_fetcher.py` (backend Task 5)
2. **Implement disambiguation logic** in `_get_arrl_eid_iid()` (backend Task 5)
3. **Update function signatures** to accept `contest_name` parameter (backend Task 5)

### UI Enhancements (Optional):

1. **Hide mode selector** for ARRL DX (instead of just disabling)
2. **Add loading indicator** while fetching log index
3. **Better error messages** explaining what to do if fetch fails

### Testing:

Once backend Task 5 is complete:
1. Test ARRL DX CW log fetch
2. Test ARRL DX SSB log fetch
3. Verify disambiguation works (CW vs SSB)
4. Test error handling

---

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Frontend Dropdown | ✅ Complete | ARRL-DX-CW and ARRL-DX-SSB listed |
| Frontend JavaScript | ✅ Complete | Handles ARRL DX correctly |
| Frontend Error Handling | ✅ Improved | Better error messages |
| Backend ARRL_CONTEST_CODES | ❌ Not Done | Entries still commented out |
| Backend Disambiguation | ❌ Not Done | No contest_name parameter support |
| API Endpoint | ⚠️ Partial | Code ready, but depends on backend |

---

## Next Steps

1. **Complete backend Task 5** (uncomment entries, add disambiguation)
2. **Test end-to-end** once backend is ready
3. **Consider UI enhancements** (hiding mode selector, loading indicators)

---

## Error Message User Will See

Until backend is complete, users will see:
```
Failed to fetch log index: ARRL-DX-CW contest code not found
```

This is expected and indicates backend Task 5 needs to be completed.
