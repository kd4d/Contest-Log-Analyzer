# CQ 160 CW PH Mode Suppression - Discussion

**Date:** 2026-01-07  
**Status:** Deferred  
**Context:** PH mode appears in hourly breakdown score report for CQ 160 CW contest when it should not.

## Issue

The CQ 160 CW contest is a CW-only variant, but the hourly breakdown report (`breakdown_report`) shows PH (Phone) mode columns because:

1. **Contest Definition**: `cq_160.json` defines `valid_modes: ["CW", "PH"]` to support both CW and SSB variants under a single definition file
2. **Report Logic**: `text_breakdown_report.py` uses `contest_def.valid_modes` directly when determining which mode columns to display (line 104)
3. **Single-Band, Multi-Mode**: CQ 160 is single-band (160M), so the breakdown report uses mode dimension instead of band dimension (line 62)

## Current Code Flow

1. **Parser** (`cq_160_parser.py`): Extracts specific contest variant from Cabrillo header (`CQ-160-CW` or `CQ-160-SSB`) and stores in `log.metadata['ContestName']`
2. **Data Aggregation** (`time_series.py` lines 280-287): Collects data for all modes present in log data, not filtered by variant
3. **Report Generation** (`text_breakdown_report.py` lines 59-62, 104):
   - Determines dimension (band vs mode) based on `is_single_band` and `is_multi_mode`
   - Uses `contest_def.valid_modes` directly without variant filtering
   - For CQ 160, this means both CW and PH columns are displayed

## Proposed Solutions

### Option 1: Filter Based on Contest Name (Recommended)
**Location:** `contest_tools/reports/text_breakdown_report.py` around line 104

Filter `valid_modes` based on actual contest name:
- If `contest_name == "CQ-160-CW"` → filter to `["CW"]`
- If `contest_name == "CQ-160-SSB"` → filter to `["PH"]` (or `["SSB"]` depending on mode mapping)
- Otherwise use `valid_modes` as-is

**Pros:**
- Minimal code change, localized
- Contest-specific logic isolated
- No impact on other contests

**Cons:**
- Contest-specific logic in report code
- Assumes PH maps to SSB for CQ 160

### Option 2: Filter Based on Actual Data
**Location:** `contest_tools/reports/text_breakdown_report.py` around line 104

Use modes that actually exist in the data:
```python
if dimension == 'mode':
    hourly_data = hourly.get('by_mode', {})
    valid_dimensions = [m for m in hourly_data.keys() if m in valid_modes]
```

**Pros:**
- No PH column if there's no PH data
- Works generically for any contest
- Data-driven approach

**Cons:**
- May hide valid modes that simply have zero QSOs
- Behavior depends on data presence, not configuration

### Option 3: Variant-Specific Mode Configuration
**Location:** `contest_tools/contest_definitions/cq_160.json` and `ContestDefinition` class

Add variant-specific mode configuration to JSON:
```json
"mode_variants": {
    "CQ-160-CW": ["CW"],
    "CQ-160-SSB": ["PH"]
}
```

**Pros:**
- Explicit configuration in contest definition
- Extensible to other multi-mode contests
- Separates variant logic from report code

**Cons:**
- Requires contest definition schema changes
- More complex implementation

### Option 4: Filter at TimeSeriesAggregator Level
**Location:** `contest_tools/data_aggregators/time_series.py` around line 286

Only aggregate modes that should be included based on contest variant.

**Pros:**
- Filters at source, benefits all reports
- Consistent data across reports

**Cons:**
- Complex to determine variant at aggregation time
- May hide data that other reports need

## Recommendation

**Option 1** is recommended for implementation when ready because:
- Minimal code changes required
- No schema modifications needed
- Easy to test and verify
- CQ 160 is a known edge case with explicit variant naming

## Implementation Notes

When implementing Option 1, key considerations:

1. **Mode Mapping**: Verify whether CQ 160 SSB uses "PH" or "SSB" in the Mode column
2. **Contest Name Matching**: Use exact match on `contest_name` from metadata (`CQ-160-CW`, `CQ-160-SSB`)
3. **Fallback**: Ensure other contests are unaffected by maintaining default behavior
4. **Testing**: Test with both CQ-160-CW and CQ-160-SSB logs to ensure correct filtering

## Related Files

- `contest_tools/contest_definitions/cq_160.json` - Contest definition with `valid_modes`
- `contest_tools/reports/text_breakdown_report.py` - Report generation logic
- `contest_tools/data_aggregators/time_series.py` - Data aggregation
- `contest_tools/contest_specific_annotations/cq_160_parser.py` - Parser that extracts contest variant
