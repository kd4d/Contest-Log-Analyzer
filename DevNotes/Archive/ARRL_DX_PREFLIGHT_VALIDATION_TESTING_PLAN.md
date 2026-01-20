# ARRL DX Pre-Flight Validation Testing Plan

**Date:** 2026-01-17  
**Status:** Completed  
**Last Updated:** 2026-01-19  
**Context:** Testing strategy for pre-flight validation implementation

---

## Testing Approach

### 1. Unit Tests (Standalone Scripts)

Create test scripts in `test_code/` to test helper functions in isolation.

### 2. Integration Tests (Manual + Automated)

Test with real log files through the web interface.

### 3. Edge Case Tests

Test error handling, missing data, etc.

---

## Test Data Requirements

### Required Test Logs

We need sample ARRL DX logs with known location types:

1. **W/VE Logs:**
   - 48-state US station (e.g., K3LR, W1AW)
   - Canadian station (e.g., VE3XYZ, VE1ABC)

2. **DX Logs:**
   - Alaska station (KL7 prefix, e.g., KL7ABC)
   - Hawaii station (KH6 prefix, e.g., KH6ABC)
   - US possession (CY9, CY0 prefixes)
   - International DX station (e.g., G3ABC, JA1XYZ)

3. **Test Log Sources:**
   - `CONTEST_LOGS_REPORTS/Logs/` (if ARRL DX logs exist)
   - ARRL public logs archive (download test logs)
   - Create minimal test logs if needed

---

## Unit Tests

### Test Script: `test_code/test_arrl_dx_preflight_validation.py`

**Purpose:** Test helper functions in isolation

**Test Cases:**

#### 1. `_read_cabrillo_header()` Tests

```python
def test_read_cabrillo_header_valid():
    """Test reading valid Cabrillo header"""
    # Create temporary test file with header
    # Verify all fields are read correctly
    
def test_read_cabrillo_header_missing_fields():
    """Test reading header with missing fields"""
    # Should return partial dict, not crash
    
def test_read_cabrillo_header_empty_file():
    """Test reading empty file"""
    # Should return empty dict
    
def test_read_cabrillo_header_no_qso_section():
    """Test reading file with no QSO section"""
    # Should read all lines as header
```

#### 2. `_get_cty_file_for_validation()` Tests

```python
def test_get_cty_file_custom():
    """Test with custom CTY file"""
    # Should return custom path if provided
    
def test_get_cty_file_default():
    """Test with default CTY file selection"""
    # Should use CtyManager to find appropriate file
    
def test_get_cty_file_no_dates():
    """Test when no QSO dates found"""
    # Should use current date as fallback
    
def test_get_cty_file_missing_logs():
    """Test with invalid log paths"""
    # Should handle gracefully, return None or default
```

#### 3. `_validate_arrl_dx_location_types()` Tests

```python
def test_validate_single_log():
    """Test with single log (should skip validation)"""
    # Should return {'valid': True, 'error_message': None}
    
def test_validate_two_wve_logs():
    """Test with 2 W/VE logs (should pass)"""
    # Should return valid=True
    
def test_validate_two_dx_logs():
    """Test with 2 DX logs (should pass)"""
    # Should return valid=True
    
def test_validate_mixed_wve_dx():
    """Test with 1 W/VE + 1 DX log (should fail)"""
    # Should return valid=False with clear error message
    
def test_validate_non_arrl_dx_contest():
    """Test with non-ARRL-DX contest (should skip)"""
    # Should return valid=True (skip validation)
    
def test_validate_missing_contest_header():
    """Test with missing CONTEST header"""
    # Should skip validation gracefully
    
def test_validate_missing_callsign_header():
    """Test with missing CALLSIGN header"""
    # Should skip that log, continue with others
    
def test_validate_alaska_as_dx():
    """Test that Alaska (KL7) is classified as DX"""
    # Critical test - Alaska should be DX, not W/VE
    
def test_validate_hawaii_as_dx():
    """Test that Hawaii (KH6) is classified as DX"""
    # Critical test - Hawaii should be DX, not W/VE
    
def test_validate_us_possessions_as_dx():
    """Test that US possessions (CY9, CY0) are classified as DX"""
    # Critical test - US possessions should be DX
    
def test_validate_error_message_format():
    """Test error message format and content"""
    # Should include:
    # - Clear title
    # - Explanation of W/VE vs DX
    # - List of which logs are which category
```

---

## Integration Tests

### Test Script: `test_code/test_arrl_dx_preflight_integration.py`

**Purpose:** Test full validation flow with real log files

**Test Cases:**

#### 1. Manual Upload Flow Tests

```python
def test_manual_upload_two_wve_logs():
    """Test manual upload of 2 W/VE logs"""
    # Should proceed to analysis
    
def test_manual_upload_two_dx_logs():
    """Test manual upload of 2 DX logs"""
    # Should proceed to analysis
    
def test_manual_upload_mixed_logs():
    """Test manual upload of mixed W/VE + DX"""
    # Should show error, stay on upload screen
    
def test_manual_upload_single_log():
    """Test manual upload of single log"""
    # Should proceed (no validation needed)
    
def test_manual_upload_custom_cty():
    """Test manual upload with custom CTY file"""
    # Should use custom CTY for validation
```

#### 2. Public Fetch Flow Tests

```python
def test_fetch_two_wve_logs():
    """Test fetching 2 W/VE logs from archive"""
    # Should proceed to analysis
    
def test_fetch_two_dx_logs():
    """Test fetching 2 DX logs from archive"""
    # Should proceed to analysis
    
def test_fetch_mixed_logs():
    """Test fetching mixed W/VE + DX logs"""
    # Should show error, stay on fetch screen
```

---

## Manual Testing Checklist

### Setup

- [ ] Ensure test logs are available in `CONTEST_LOGS_REPORTS/Logs/` or download from ARRL archive
- [ ] Verify CTY file is available in `CONTEST_LOGS_REPORTS/data/CTY/`
- [ ] Start web application (Django dev server or Docker)

### Test 1: Single Log Upload (No Validation)

1. [ ] Navigate to web interface
2. [ ] Select "Upload Logs" tab
3. [ ] Upload single ARRL DX CW log (W/VE station)
4. [ ] Click "Analyze"
5. [ ] **Expected:** Analysis proceeds, dashboard loads
6. [ ] **Verify:** No validation error shown

### Test 2: Two W/VE Logs (Should Pass)

1. [ ] Navigate to web interface
2. [ ] Select "Upload Logs" tab
3. [ ] Upload two ARRL DX CW logs (both W/VE stations)
4. [ ] Click "Analyze"
5. [ ] **Expected:** Analysis proceeds, dashboard loads
6. [ ] **Verify:** No validation error shown

### Test 3: Two DX Logs (Should Pass)

1. [ ] Navigate to web interface
2. [ ] Select "Upload Logs" tab
3. [ ] Upload two ARRL DX CW logs (both DX stations)
4. [ ] Click "Analyze"
5. [ ] **Expected:** Analysis proceeds, dashboard loads
6. [ ] **Verify:** No validation error shown

### Test 4: Mixed W/VE + DX Logs (Should Fail)

1. [ ] Navigate to web interface
2. [ ] Select "Upload Logs" tab
3. [ ] Upload one W/VE log and one DX log
4. [ ] Click "Analyze"
5. [ ] **Expected:** Error message shown, stays on upload screen
6. [ ] **Verify:** Error message includes:
   - Clear title "ARRL DX Contest Error"
   - Explanation of W/VE vs DX
   - List showing which logs are which category
7. [ ] **Verify:** User can correct and try again

### Test 5: Alaska Station (KL7) as DX

1. [ ] Upload log from Alaska station (KL7 prefix)
2. [ ] Upload log from 48-state US station (K prefix)
3. [ ] Click "Analyze"
4. [ ] **Expected:** Error message (Alaska is DX, US is W/VE)
5. [ ] **Verify:** Error message correctly identifies Alaska as DX

### Test 6: Hawaii Station (KH6) as DX

1. [ ] Upload log from Hawaii station (KH6 prefix)
2. [ ] Upload log from 48-state US station (K prefix)
3. [ ] Click "Analyze"
4. [ ] **Expected:** Error message (Hawaii is DX, US is W/VE)
5. [ ] **Verify:** Error message correctly identifies Hawaii as DX

### Test 7: Public Fetch - Mixed Logs

1. [ ] Navigate to web interface
2. [ ] Select "Fetch from Archive" tab
3. [ ] Select "ARRL DX CW" contest
4. [ ] Select year (e.g., 2024)
5. [ ] Select one W/VE callsign
6. [ ] Select one DX callsign
7. [ ] Click "Fetch & Analyze"
8. [ ] **Expected:** Error message shown, stays on fetch screen
9. [ ] **Verify:** Error message is clear and actionable

### Test 8: Non-ARRL-DX Contest (Should Skip Validation)

1. [ ] Upload two CQ-WW logs (different categories if applicable)
2. [ ] Click "Analyze"
3. [ ] **Expected:** Analysis proceeds (validation only for ARRL DX)
4. [ ] **Verify:** No validation error shown

### Test 9: Custom CTY File

1. [ ] Upload custom CTY file
2. [ ] Upload two ARRL DX logs (one W/VE, one DX)
3. [ ] Click "Analyze"
4. [ ] **Expected:** Validation uses custom CTY file
5. [ ] **Verify:** Error message shown (validation still works)

### Test 10: Missing Headers (Edge Case)

1. [ ] Create test log with missing CONTEST header
2. [ ] Upload with valid ARRL DX log
3. [ ] Click "Analyze"
4. [ ] **Expected:** Should skip validation for log with missing header, proceed with other log
5. [ ] **Verify:** No crash, graceful handling

### Test 11: Error Message Format

1. [ ] Upload mixed W/VE + DX logs
2. [ ] Click "Analyze"
3. [ ] **Verify Error Message Contains:**
   - [ ] Title: "ARRL DX Contest Error"
   - [ ] Explanation of asymmetric nature
   - [ ] Definition of W/VE
   - [ ] Definition of DX
   - [ ] List of logs with their categories (e.g., "K3LR (W/VE), KL7ABC (DX)")
4. [ ] **Verify:** Error message is readable (line breaks preserved)

---

## Automated Test Script

### Create: `test_code/test_arrl_dx_preflight_validation.py`

**Structure:**

```python
#!/usr/bin/env python3
"""
Unit tests for ARRL DX pre-flight validation functions.

Run from project root:
    python test_code/test_arrl_dx_preflight_validation.py
"""

import sys
import os
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.analyzer.views import (
    _read_cabrillo_header,
    _get_cty_file_for_validation,
    _validate_arrl_dx_location_types
)

def create_test_log(content: str) -> str:
    """Create temporary test log file"""
    fd, path = tempfile.mkstemp(suffix='.log', text=True)
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return path

def test_read_cabrillo_header_valid():
    """Test reading valid Cabrillo header"""
    log_content = """START-OF-LOG: 3.0
CALLSIGN: K3LR
CONTEST: ARRL-DX-CW
CATEGORY-OPERATOR: SINGLE-OP
CATEGORY-BAND: ALL
CATEGORY-MODE: CW
QSO: 28000 CW 2024-03-02 0000 K3LR         599 001 PA        W1AW         599 001 CT
QSO: 28000 CW 2024-03-02 0001 K3LR         599 002 PA        G3ABC        599 001
END-OF-LOG:
"""
    log_path = create_test_log(log_content)
    try:
        header = _read_cabrillo_header(log_path)
        assert header['CALLSIGN'] == 'K3LR'
        assert header['CONTEST'] == 'ARRL-DX-CW'
        assert header['CATEGORY-OPERATOR'] == 'SINGLE-OP'
        print("✓ test_read_cabrillo_header_valid: PASSED")
    finally:
        os.remove(log_path)

def test_validate_two_wve_logs():
    """Test validation with 2 W/VE logs"""
    # Create two test logs with W/VE callsigns
    # Mock CTY lookup or use real CTY file
    # Verify validation passes
    pass

def test_validate_mixed_logs():
    """Test validation with mixed W/VE + DX logs"""
    # Create test logs with one W/VE and one DX
    # Verify validation fails with clear error
    pass

# ... more tests ...

if __name__ == '__main__':
    print("Running ARRL DX Pre-Flight Validation Tests...\n")
    
    test_read_cabrillo_header_valid()
    # ... run all tests ...
    
    print("\nAll tests completed!")
```

---

## Test Execution Strategy

### Phase 1: Unit Tests (Isolated)

1. **Create test script** in `test_code/`
2. **Run standalone** to verify helper functions work
3. **Fix any issues** before integration testing

### Phase 2: Integration Tests (Web Interface)

1. **Prepare test logs:**
   - Download or create ARRL DX logs with known location types
   - Ensure variety: W/VE, DX, Alaska, Hawaii, etc.

2. **Manual testing:**
   - Go through checklist above
   - Document any issues

3. **Automated integration tests:**
   - Create script that simulates web requests
   - Test both upload and fetch flows

### Phase 3: Edge Cases

1. **Test error handling:**
   - Missing headers
   - Invalid CTY files
   - Network issues (for fetch)

2. **Test performance:**
   - Large number of logs
   - Slow CTY file lookup

---

## Success Criteria

### Unit Tests

- [ ] All helper functions tested
- [ ] Edge cases covered
- [ ] Error handling verified
- [ ] Location type logic matches backend (Alaska=DX, etc.)

### Integration Tests

- [ ] Manual upload flow works correctly
- [ ] Public fetch flow works correctly
- [ ] Validation catches W/VE + DX mismatches
- [ ] Validation allows same-category logs
- [ ] Error messages are clear and actionable
- [ ] User stays on upload/fetch screen on error

### Edge Cases

- [ ] Missing headers handled gracefully
- [ ] Invalid CTY files handled gracefully
- [ ] Single log upload works (no validation)
- [ ] Non-ARRL-DX contests skip validation

---

## Test Data Preparation

### Option 1: Use Existing Logs

If ARRL DX logs exist in `CONTEST_LOGS_REPORTS/Logs/`:
- Identify W/VE vs DX logs
- Use for testing

### Option 2: Download from ARRL Archive

1. Use ARRL public logs API (once backend Task 5 is complete)
2. Download test logs with known callsigns
3. Verify location types manually

### Option 3: Create Minimal Test Logs

Create minimal Cabrillo logs with:
- Valid headers (CONTEST, CALLSIGN)
- Minimal QSO data (just enough for validation)
- Known location types

**Example minimal log:**
```
START-OF-LOG: 3.0
CALLSIGN: K3LR
CONTEST: ARRL-DX-CW
CATEGORY-OPERATOR: SINGLE-OP
CATEGORY-BAND: ALL
CATEGORY-MODE: CW
QSO: 28000 CW 2024-03-02 0000 K3LR         599 001 PA        W1AW         599 001 CT
END-OF-LOG:
```

---

## Regression Testing

After implementation:
1. Run existing regression tests (`run_regression_test.py`)
2. Verify no regressions in other contests
3. Add ARRL DX test cases to regression suite

---

## Next Steps

1. **Create test script** (`test_code/test_arrl_dx_preflight_validation.py`)
2. **Prepare test data** (logs with known location types)
3. **Run unit tests** to verify helper functions
4. **Run manual tests** through web interface
5. **Document results** and fix any issues
6. **Add to regression suite** for ongoing testing

---

## Notes

- Tests should be run in development environment first
- Use real CTY files for accurate location type determination
- Test with actual ARRL DX logs when possible
- Document any test failures with steps to reproduce
