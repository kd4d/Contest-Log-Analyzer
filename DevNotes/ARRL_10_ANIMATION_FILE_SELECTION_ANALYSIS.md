# ARRL 10 Animation - File Selection Problem Analysis

## Summary

This document analyzes the file selection/overwriting problem in the ARRL 10 Meter Animation report, where animation files are being overwritten when generating single-log vs multi-log versions.

## Problem Description

### Symptom
- Animation report consistently shows data for only the **alphabetically last callsign** entered
- When processing multiple logs (e.g., HK3RD and VP2VMM), only VP2VMM data appears
- Single-log animations overwrite each other, resulting in incorrect filenames and data mismatches

### Root Cause: Filename/Callsign Mismatch

**The Core Issue:**
- Filename generation uses callsigns from **cached time series data** (which contains ALL logs)
- Actual data being generated uses callsigns from **current report instance** (which may be a subset)
- Result: Filename includes all callsigns, but data only contains a subset

## Technical Analysis

### Current Filename Generation Logic

**Location:** `contest_tools/reports/plot_interactive_animation.py`

**Band Dimension (`_prepare_data_band`, ~line 604):**
```python
ts_raw = self._get_cached_ts_data()
callsigns = sorted(list(ts_raw['logs'].keys()))  # ❌ WRONG: Uses cached data
```

**Mode Dimension (`_prepare_data_mode`, ~line 701):**
```python
ts_raw = self._get_cached_ts_data()
callsigns = sorted(list(ts_raw['logs'].keys()))  # ❌ WRONG: Uses cached data
```

**Filename Construction (line 543):**
```python
filename = f"interactive_animation--{build_callsigns_filename_part(callsigns)}.html"
```

### Why This Fails

1. **Cache Contains All Logs:**
   - `ReportGenerator._ts_aggregator` is initialized with ALL logs: `TimeSeriesAggregator(self.logs)`
   - The cache is shared across all report instances
   - Even when a single-log report is created, the cache still contains all callsigns

2. **Data Uses Current Logs:**
   - `MatrixAggregator` is called with `self.logs` (only current logs for this report instance)
   - `matrix_raw['logs']` contains only the callsigns from `self.logs`
   - The mismatch: filename has all callsigns, but data has only some

### Example: HK3RD + VP2VMM

**Scenario 1: Multi-Log Generation**
- `self.logs = [HK3RD, VP2VMM]`
- `callsigns` (from cache) = `['HK3RD', 'VP2VMM']` ✅
- `matrix_raw['logs']` = `{'HK3RD': ..., 'VP2VMM': ...}` ✅
- Filename: `interactive_animation--hk3rd_vp2vmm.html` ✅ **Correct**

**Scenario 2: Single-Log Generation (HK3RD)**
- `self.logs = [HK3RD]`
- `callsigns` (from cache) = `['HK3RD', 'VP2VMM']` ❌ **WRONG!**
- `matrix_raw['logs']` = `{'HK3RD': ...}` ✅
- Filename: `interactive_animation--hk3rd_vp2vmm.html` ❌ **Should be `hk3rd.html`**

**Scenario 3: Single-Log Generation (VP2VMM)**
- `self.logs = [VP2VMM]`
- `callsigns` (from cache) = `['HK3RD', 'VP2VMM']` ❌ **WRONG!**
- `matrix_raw['logs']` = `{'VP2VMM': ...}` ✅
- Filename: `interactive_animation--hk3rd_vp2vmm.html` ❌ **Should be `vp2vmm.html`**
- **Overwrites the file from Scenario 2!**

## Solution

### Fix: Extract Callsigns from Actual Logs

**Change callsign extraction to use `self.logs` instead of cached data:**

**Option 1: Use `self.logs` directly (Recommended)**
```python
# Extract callsigns from actual logs being processed (not cached data)
callsigns = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
```

**Option 2: Use `matrix_raw['logs'].keys()` (Alternative)**
```python
# Extract callsigns from the matrix data (which is already filtered to current logs)
callsigns = sorted(list(matrix_raw['logs'].keys()))
```

### Implementation Details

**Lines to Change:**
- Line ~604 (`_prepare_data_band`): Replace `callsigns = sorted(list(ts_raw['logs'].keys()))`
- Line ~701 (`_prepare_data_mode`): Replace `callsigns = sorted(list(ts_raw['logs'].keys()))`

**Recommended Fix:**
```python
# In _prepare_data_band and _prepare_data_mode:
# Extract callsigns from actual logs being processed (not cached data)
# This ensures filename matches the data being generated (fixes single-log overwriting issue)
callsigns = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
```

## Impact

### Before Fix
- ❌ Single-log animations overwrite each other
- ❌ Filenames don't match data content
- ❌ Only alphabetically last callsign's data appears

### After Fix
- ✅ Single-log files: `interactive_animation--hk3rd.html`
- ✅ Multi-log files: `interactive_animation--hk3rd_vp2vmm.html`
- ✅ Filenames match data content
- ✅ No file conflicts or overwrites

## Related Files

- `contest_tools/reports/plot_interactive_animation.py`: Main report file
- `DevNotes/ARRL_10_ANIMATION_DAL_ANALYSIS.md`: Related DAL usage analysis
- `TECHNICAL_DEBT.md`: Technical debt tracking for this issue

## Status

**Status:** [x] Fixed  
**Commit:** `5c98b05` - "fix(animation): remove diagnostic code and fix scoring inconsistencies"  
**Date Fixed:** 2026-01-17

The fix was implemented by extracting callsigns from `self.logs` instead of cached time series data, ensuring filename generation matches the actual data being processed.
