# Mutually Exclusive Multiplier Filtering Pattern

**Date:** 2026-01-18  
**Status:** Fixed  
**Context:** Critical bug fix for ARRL 10 Meter breakdown report showing zero multipliers

## Issue

For contests with mutually exclusive multipliers (where each QSO has only ONE multiplier column populated), filtering logic that requires ALL multiplier columns to be valid removes all rows.

### Example: ARRL 10 Meter
- **Multiplier columns:** `Mult_State`, `Mult_VE`, `Mult_XE`, `Mult_DXCC`, `Mult_ITU`
- **Mutually exclusive:** Each QSO has exactly ONE of these columns populated, others are NaN
- **Bug:** Filter `df[df[col1].notna() & df[col2].notna() & ...]` removes all rows because no row has all columns populated

## The Bug Pattern

**Incorrect (AND logic):**
```python
df_valid = df.copy()
for col in mult_cols:
    if col in df_valid.columns:
        # This progressively filters out rows that don't have THIS column valid
        # For mutually exclusive, this eventually removes all rows
        df_valid = df_valid[df_valid[col].notna() & (df_valid[col] != 'Unknown')]
```

**Problem:** Each iteration filters to rows where THIS column is valid, AND all previous columns were valid. For mutually exclusive multipliers, this removes all rows because:
- First iteration: Keep rows where `Mult_State` is valid
- Second iteration: Keep rows where `Mult_State` AND `Mult_VE` are valid → EMPTY (none exist)

## The Fix Pattern

**Correct (OR logic):**
```python
df_valid = df.copy()

# Build a mask for rows that have at least one valid multiplier
has_valid_mult = pd.Series([False] * len(df_valid), index=df_valid.index)
for col in mult_cols:
    if col in df_valid.columns:
        col_valid = df_valid[col].notna() & (df_valid[col] != 'Unknown')
        has_valid_mult = has_valid_mult | col_valid  # OR condition

df_valid = df_valid[has_valid_mult]
```

**Why it works:** Keep rows where ANY multiplier column has a valid value, not ALL columns.

## When to Use This Pattern

**Use OR logic when:**
- Contest has `mutually_exclusive_mults` defined in JSON
- Need to filter to rows with valid multipliers across ALL multiplier columns
- Processing hourly multipliers or any aggregate that needs to check all multiplier types

**Use AND logic (individual column filtering) when:**
- Processing a SPECIFIC multiplier column (e.g., only `Mult_State`)
- Already working with a filtered dataset for that specific multiplier
- Example: `df_valid_mults = df[df[mult_col].notna() & (df[mult_col] != 'Unknown')]` ✅

## Affected Code

### Fixed
- ✅ `contest_tools/data_aggregators/time_series.py` - `_calculate_hourly_multipliers()`
  - **Line 379-398:** Changed from AND to OR logic for filtering valid multiplier rows

### Code That's Already Correct (Individual Column Filtering)
- ✅ `contest_tools/data_aggregators/score_stats.py` (line 113)
  - Filters per column individually for scalar calculations - correct
- ✅ `contest_tools/data_aggregators/time_series.py` (line 116)
  - Filters per column individually for scalar calculations - correct

## Related Contests

Contests using mutually exclusive multipliers:
- **ARRL 10 Meter:** `Mult_State`, `Mult_VE`, `Mult_XE`, `Mult_DXCC`, `Mult_ITU`
- **CQ 160:** `Mult1` (STPROV), `Mult2` (DXCC)
- **WAE:** Various mutually exclusive multiplier groups
- **NAQP:** Call areas and states
- **IARU HF:** Multiple mutually exclusive groups
- **WRTC:** `Mult_DXCC`, `Mult_HQ`, `Mult_Official`

## Testing

When testing contests with `mutually_exclusive_mults`:
1. Verify breakdown reports show multipliers correctly (not all zeros)
2. Verify cumulative multipliers increase over time
3. Check that mode/band breakdowns show multipliers for each dimension
4. Verify scalar multiplier counts match hourly cumulative multipliers

## Related

- `contest_tools/contest_definitions/arrl_10.json` - Example of mutually exclusive multipliers
- `contest_tools/data_aggregators/time_series.py` - Fixed implementation
- `TECHNICAL_DEBT.md` - Breakdown report multiplier issue (now fixed)
