# ARRL 10 Animation - DAL Usage and Filename Generation Analysis

## Summary

This document analyzes:
1. Whether the animation report consistently uses the Data Aggregation Layer (DAL)
2. The historical context of mode-based data in the DAL
3. The filename generation problem and its relationship to DAL usage

## DAL Usage Analysis

### Current Implementation: **YES, Consistently Uses DAL**

The animation report (`plot_interactive_animation.py`) **consistently uses aggregators** from the DAL:

#### Band Dimension (`_prepare_data_band`)
- **TimeSeriesAggregator**: Gets time series data (line 592/588)
- **MatrixAggregator**: Gets stacked matrix data via `get_stacked_matrix_data()` (line 601/598)
- **Structure**: Band x Time x RunStatus
- **Uses cached aggregators** when available (performance optimization)

#### Mode Dimension (`_prepare_data_mode`)
- **TimeSeriesAggregator**: Gets time series data (line 698/695)
- **MatrixAggregator**: Gets mode-based matrix data via `get_mode_stacked_matrix_data()` (line 713)
- **Structure**: Mode x Time x RunStatus
- **Uses cached aggregators** when available (performance optimization)

### DAL Methods Used

**MatrixAggregator provides both band and mode methods:**

1. **`get_stacked_matrix_data()`** (Band-based, line 137 in matrix_stats.py)
   - Groups by: `Band x Time x RunStatus`
   - Returns: `logs[CALLSIGN][BAND][RunStatus] = [values]`
   - Structure: `{"time_bins": [...], "bands": [...], "logs": {...}}`

2. **`get_mode_stacked_matrix_data()`** (Mode-based, line 257 in matrix_stats.py)
   - Groups by: `Mode x Time x RunStatus`
   - Returns: `logs[CALLSIGN][MODE][RunStatus] = [values]`
   - Structure: `{"time_bins": [...], "modes": [...], "logs": {...}}`

**Both methods:**
- Use the same pivot logic (index=[Band|Mode, RunStatus], columns=Time)
- Ensure time alignment via `master_time_index`
- Return pure Python primitives (no Pandas objects)
- Follow the DAL pattern consistently

### Historical Context: Mode-Based Data in DAL

**The mode-based method exists and is parallel to band-based:**

- `get_mode_stacked_matrix_data()` was added to support mode-dimension visualizations
- It mirrors `get_stacked_matrix_data()` but groups by radio Mode (CW, PH, SSB) instead of Band
- Both methods were likely added around the same time or mode support was added later
- **The DAL now supports both dimensions**, so there's no historical gap

## Filename Generation Problem

### Root Cause: Mismatch Between Cached Data and Actual Logs

**The Problem:**
- Filename is generated from `callsigns` list (line 543: `build_callsigns_filename_part(callsigns)`)
- `callsigns` comes from `ts_raw['logs'].keys()` (lines 604, 701)
- `ts_raw` comes from **cached** `_get_cached_ts_data()` (lines 588, 695)
- The cache uses `TimeSeriesAggregator(self.logs)` where `self.logs` in the **ReportGenerator** context contains **ALL logs**
- Even when a single-log report instance is created with `ReportClass([log])`, the cached data still contains all callsigns

**The Mismatch:**
- `callsigns` (for filename) = **ALL callsigns** (from cached ts_raw with all logs)
- `matrix_raw['logs']` (actual data) = **Only callsigns from `self.logs`** (from MatrixAggregator with current logs)
- Result: Filename includes all callsigns, but data only contains some

**Example (ARRL 10 with HK3RD + VP2VMM):**
1. **Multi-log generation**: `self.logs = [HK3RD, VP2VMM]`
   - `callsigns = ['HK3RD', 'VP2VMM']` (from cached ts_raw)
   - `matrix_raw['logs'] = {'HK3RD': ..., 'VP2VMM': ...}` (from MatrixAggregator with both logs)
   - Filename: `interactive_animation--hk3rd_vp2vmm.html` ✅ **Correct**

2. **Single-log generation (HK3RD)**: `self.logs = [HK3RD]`
   - `callsigns = ['HK3RD', 'VP2VMM']` (from cached ts_raw - **WRONG!**)
   - `matrix_raw['logs'] = {'HK3RD': ...}` (from MatrixAggregator with one log)
   - Filename: `interactive_animation--hk3rd_vp2vmm.html` ❌ **Wrong! Should be hk3rd.html**

3. **Single-log generation (VP2VMM)**: `self.logs = [VP2VMM]`
   - `callsigns = ['HK3RD', 'VP2VMM']` (from cached ts_raw - **WRONG!**)
   - `matrix_raw['logs'] = {'VP2VMM': ...}` (from MatrixAggregator with one log)
   - Filename: `interactive_animation--hk3rd_vp2vmm.html` ❌ **Wrong! Should be vp2vmm.html**
   - **Overwrites previous file!**

### Why This Happens

The cached aggregator in `ReportGenerator` is initialized once with all logs:
```python
self._ts_aggregator = TimeSeriesAggregator(self.logs)  # ALL logs
```

When a single-log report is created:
```python
instance = ReportClass([log])  # Only ONE log
enhanced_kwargs = self._prepare_report_kwargs([log], **report_kwargs)
```

The `_prepare_report_kwargs` passes the cached `_get_cached_ts_data` function which uses the aggregator with ALL logs, not just the current `self.logs`.

### Solution: Extract Callsigns from Actual Logs

**Fix:** Use `self.logs` or `matrix_raw['logs'].keys()` to determine callsigns for filename, not the cached time series data.

**Option 1: Use `self.logs` directly (Recommended)**
```python
callsigns = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
```

**Option 2: Use `matrix_raw['logs'].keys()` (Alternative)**
```python
callsigns = sorted(list(matrix_raw['logs'].keys()))
```

Both approaches ensure the filename matches the actual data being generated.

## Recommendations

### Immediate Fix: Extract Callsigns from Actual Logs

**Location:** `contest_tools/reports/plot_interactive_animation.py`

**Lines to Change:**
- Line 604 (band dimension): Change `callsigns = sorted(list(ts_raw['logs'].keys()))`
- Line 701 (mode dimension): Change `callsigns = sorted(list(ts_raw['logs'].keys()))`

**Suggested Fix:**
```python
# Extract callsigns from actual logs being processed (not cached data)
callsigns = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
```

This ensures:
- Single-log files: `interactive_animation--hk3rd.html`
- Multi-log files: `interactive_animation--hk3rd_vp2vmm.html`
- No overwriting between single and multi-log versions

### Keep Single-Log Support

Since single-log animations are needed, the fix above ensures:
- Single-log versions generate correctly with proper filenames
- Multi-log versions generate correctly with proper filenames
- No file conflicts or overwrites

## Conclusion

1. **DAL Usage:** ✅ The report consistently uses DAL aggregators for both band and mode dimensions
2. **Mode Support:** ✅ The DAL has full mode support via `get_mode_stacked_matrix_data()`
3. **Filename Issue:** ❌ The problem is in callsign extraction, not DAL usage
4. **Solution:** Extract callsigns from `self.logs` instead of cached time series data

The DAL is working correctly. The issue is purely in the filename generation logic.
