# Interactive Animation Chart - Band vs Mode Dimension Discussion

**Date:** 2026-01-07  
**Issue:** For ARRL-10 Meter, the interactive animation chart shows "Overall Band: 10 meters" but the bar charts are actually broken down by mode (CW and SSB), which is confusing.

## Problem Analysis

### Current Behavior:
- **X-Axis Label:** "Band" (hardcoded on lines 293-294)
- **X-Axis Data:** `bands = ["10M"]` (for ARRL-10, single band contest)
- **Actual Data Structure:** Bars show mode breakdown (CW/SSB) stacked by Run/S&P
- **Result:** Misleading - shows "Band: 10M" but data is actually mode-based

### Why This Happens:
1. **ARRL-10 Characteristics:**
   - Single-band contest (only 10M)
   - Mode-based multipliers (CW and SSB are separate multipliers)
   - The meaningful comparison dimension is **Mode**, not Band

2. **Current Code Logic:**
   - `MatrixAggregator.get_stacked_matrix_data()` always returns data grouped by **band** first
   - The animation chart assumes multi-band contests and uses bands as the x-axis
   - For single-band contests, this creates a meaningless single-category x-axis

### Data Structure:
The matrix data structure is: `logs -> call -> band -> mode -> [hourly_values]`

For ARRL-10:
- Only one band: `bands = ["10M"]`
- Multiple modes: `modes = ["CW", "SSB"]` (inferred from data)
- The stacked bars show Run/S&P breakdown, but they're grouped by the single band, which is meaningless

## Solution Options

### Option 1: Detect Single-Band and Switch to Mode Dimension
**Logic:**
- If `len(bands) == 1`, check if there are multiple modes
- If multiple modes exist, use modes as the x-axis dimension instead of bands
- Update axis labels and data extraction logic accordingly

**Pros:**
- Makes sense for single-band contests with mode-based multipliers
- Improves clarity for ARRL-10

**Cons:**
- Requires restructuring data access pattern (band -> mode vs mode -> band)
- May need to aggregate differently for the matrix data

### Option 2: Contest-Specific Configuration
**Logic:**
- Add a flag in contest definition JSON: `"animation_dimension": "mode"` or `"band"`
- Default to `"band"` for backwards compatibility
- ARRL-10 would set `"animation_dimension": "mode"`

**Pros:**
- Explicit control per contest
- Future-proof for other single-band contests
- Doesn't affect multi-band contests

**Cons:**
- Requires JSON changes and more configuration
- Less automatic/intelligent

### Option 3: Hybrid - Auto-Detect with Contest Override
**Logic:**
- Auto-detect: if `len(bands) == 1` and `len(modes) > 1`, use mode dimension
- Allow contest definition override if needed
- Default to band dimension for multi-band contests

**Pros:**
- Intelligent default behavior
- Can override if needed
- Handles edge cases automatically

**Cons:**
- More complex logic
- Need to ensure mode data is available when bands are single

## Recommended Approach

**Option 3 (Hybrid)** seems best because:
1. ARRL-10 will automatically work correctly
2. Doesn't require JSON changes (can add override later if needed)
3. Handles the common case (single-band + mode-based multipliers) intelligently

## Implementation Requirements

### Code Changes Needed:

1. **In `_prepare_data()`:**
   - Detect if `len(bands) == 1`
   - If single-band, check available modes from the data
   - If multiple modes, restructure data to use mode as primary dimension
   - Return a flag indicating which dimension is used (`dimension_type: "band" | "mode"`)

2. **In `generate()`:**
   - Use the dimension flag to determine x-axis labels
   - Update subplot titles: "By Mode" instead of "By Band & Mode" when mode dimension
   - Update data access pattern: `data[call][mode][band]` instead of `data[call][band][mode]`

3. **Matrix Data Restructuring:**
   - Need to transpose: `band -> mode` to `mode -> band` when using mode dimension
   - Keep Run/S&P stacking logic the same (that's fine)

### Questions to Consider:

1. **What about the title?** "Hourly Rate (By Band & Mode)" becomes "Hourly Rate (By Mode)" for single-band?
2. **What if there's only one mode too?** (Unlikely, but edge case - maybe show combined?)
3. **Should this apply to other charts?** (Comparative activity butterfly, etc.)

## Other Charts Potentially Affected

### Charts with Band-Based Subplots/Structure:

1. **Interactive Animation** (`plot_interactive_animation.py`)
   - X-axis: Bands (for bottom charts)
   - **Issue:** Single-band creates meaningless single-category axis
   - **Impact:** HIGH - Primary visualization is misleading

2. **Comparative Activity Butterfly** (`chart_comparative_activity_butterfly.py`)
   - Subplot structure: One subplot per band (rows 2..N+1)
   - Subplot titles: `f"Band: {band}"`
   - **Issue:** Single-band = single subplot with only header, looks broken
   - **Impact:** MEDIUM - Chart structure assumes multi-band

3. **QSO Breakdown Chart** (`chart_qso_breakdown.py`)
   - Subplot grid: One subplot per band
   - X-axis labels: Band names
   - **Issue:** Single-band = single subplot, losing comparison utility
   - **Impact:** MEDIUM - Less useful with single band

4. **Point Contribution** (`chart_point_contribution.py`)
   - Subplot grid: One subplot per band
   - Subplot titles: `f"{band} Band Points"`
   - **Issue:** Single-band = single pie chart, still meaningful but different layout
   - **Impact:** LOW - Still functional, just different presentation

5. **Comparative Band Activity** (`plot_comparative_band_activity.py`)
   - Subplot structure: One subplot per band (rows)
   - Subplot titles: `f"Band: {band}"`
   - **Issue:** Single-band = single subplot
   - **Impact:** MEDIUM - Chart structure assumes multi-band

6. **Comparative Run/S&P** (`plot_comparative_run_sp.py`)
   - Subplot structure: One subplot per band (pagination)
   - Subplot titles: `f"Band: {band}"`
   - **Issue:** Single-band = single subplot/page
   - **Impact:** LOW - Still functional, just single page

### Text Reports:
Most text reports use "All Bands" in titles but handle single-band gracefully by just showing data for that band. These are less problematic.

## Should Charts Be Different for Multi-Band vs Single-Band Contests?

### Current Assumption:
**All charts assume multi-band structure.** This works well for:
- CQ WW (6 bands: 160M, 80M, 40M, 20M, 15M, 10M)
- ARRL DX (6 bands)
- Most major contests

### Problem Cases:
1. **ARRL-10** (1 band, 2 modes) - Band dimension is meaningless
2. **Future single-band contests** - Same issue

### Complex Cases:
- **ARRL FD** - 3 modes, 8 bands → Band dimension still makes sense
- **CQ 160** - 1 band, 2 modes → Same as ARRL-10
- **Future contests** - Could have any combination

## The Core Question: When Should We Use Band vs Mode Dimension?

### Heuristics That DON'T Work:
1. ❌ "If single-band, use mode" - ARRL FD still needs band breakdown
2. ❌ "If single-band + multi-mode, use mode" - Too simplistic
3. ❌ "If multiplier_report_scope == 'per_mode', use mode" - Not directly related

### The Real Question:
**What makes a dimension meaningful for visualization?**
- **Band dimension:** Meaningful when operators make strategic choices about which bands to use (multi-band contests)
- **Mode dimension:** Meaningful when modes have different scoring/multiplier significance (e.g., ARRL-10 where CW and SSB are separate multipliers)

### Possible Approaches:

#### Approach A: Contest-Specific Configuration
Add to contest definition JSON:
```json
{
  "visualization_dimension": "band" | "mode" | "auto"
}
```
- **Pros:** Explicit control, handles all cases
- **Cons:** Requires JSON changes, configuration burden

#### Approach B: Infer from Contest Characteristics
- If `len(valid_bands) == 1` AND `multiplier_report_scope == "per_mode"` → Use mode
- Otherwise → Use band (default)
- **Pros:** Automatic, no configuration
- **Cons:** Might not work for all edge cases (but handles common ones)

#### Approach C: Let Charts Decide Differently
Different charts could have different logic:
- **Interactive Animation:** Could use mode for single-band contests
- **Butterfly Charts:** Could use mode OR show single-band differently
- **Breakdown Charts:** Could collapse band dimension when single-band
- **Pros:** Chart-specific optimization
- **Cons:** Inconsistent behavior, more complexity

#### Approach D: Show Both Dimensions When Appropriate
- For single-band: Show mode breakdown prominently, still indicate band
- For multi-band: Show band breakdown as primary
- **Pros:** More information, handles all cases
- **Cons:** More complex charts, potential visual clutter

## Discussion Points

1. **Is this only the Interactive Animation chart?** No - several charts assume multi-band structure, but Interactive Animation is the most visible/confusing one.

2. **Should charts be different for multi-band contests?** Yes, but the question is HOW:
   - Same chart type, different dimension? (Band vs Mode)
   - Different chart type entirely? (e.g., mode-based animation vs band-based)
   - Same chart, but different labeling/structure?

3. **What's the best long-term solution?**
   - Configuration-driven (most flexible, most upfront work)
   - Heuristic-based (works for common cases, may fail for edge cases)
   - Chart-specific logic (handles each case optimally, but more maintenance)

## Next Steps

1. **Immediate:** Fix Interactive Animation for ARRL-10 (most visible issue)
2. **Short-term:** Identify which other charts have similar issues and assess priority
3. **Long-term:** Design a generic solution that works for:
   - Single-band contests (ARRL-10, CQ-160)
   - Multi-band contests (CQ-WW, ARRL-DX)
   - Complex contests (ARRL-FD with 3 modes, 8 bands)
   - Future unknown contests

## Questions for Discussion

1. Is the Interactive Animation the highest priority, or should we fix all affected charts at once?
2. For single-band contests, should we:
   - Use mode dimension instead of band?
   - Keep band but improve labeling (e.g., "10M Band - Mode Breakdown")?
   - Show a completely different chart structure?
3. Should this be configuration-driven (JSON) or heuristic-based?
4. How should we handle edge cases like ARRL-FD where we have both many bands AND many modes?
