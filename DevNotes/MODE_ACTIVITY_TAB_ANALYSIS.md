# Mode Activity Tab Analysis: Band Activity → Mode Activity for Single-Band Multi-Mode Contests

**Date:** 2025-01-XX  
**Context:** ARRL 10 Meter contest (single-band, multi-mode) needs "Mode Activity" tab instead of "Band Activity" tab in QSO Dashboard.

---

## Current Implementation

### Band Activity Tab Structure

1. **Report Used:** `chart_comparative_activity_butterfly`
   - Report ID: `chart_comparative_activity_butterfly`
   - Report Name: "Comparative Activity Butterfly Chart"
   - Location: `contest_tools/reports/chart_comparative_activity_butterfly.py`

2. **Data Source:** `MatrixAggregator.get_stacked_matrix_data()`
   - Groups by: **Band x Time x RunStatus**
   - Returns structure: `logs[CALLSIGN][BAND][RunStatus] = [values]`
   - Creates one subplot per band showing Run/S&P/Unknown activity over time

3. **Dashboard Integration:**
   - Tab ID: `band-activity`
   - Tab Label: "Band Activity Comparison"
   - Tab Title: "Band Activity Butterfly Chart"
   - JavaScript container: `chart-band-activity`
   - View logic: `web_app/analyzer/views.py` lines 1203-1204 (discovers artifacts)

4. **Chart Structure:**
   - Header row with legend (Run, S&P, Unknown)
   - One subplot row per band
   - Each subplot: Butterfly chart (Log 1 positive, Log 2 negative)
   - X-axis: Time (UTC)
   - Y-axis: QSO count (stacked by RunStatus)

---

## ARRL 10 Meter Contest Characteristics

From `contest_tools/contest_definitions/arrl_10.json`:

- **Single Band:** `valid_bands: ["10M"]`
- **Multi-Mode:** `valid_modes: ["CW", "PH"]`
- **Animation Dimension:** `animation_dimension: "mode"` (indicates mode is the meaningful dimension)
- **Multiplier Scope:** `multiplier_report_scope: "per_mode"` (multipliers counted separately per mode)

**Key Insight:** For ARRL 10 Meter, showing activity by **mode** (CW vs PH) is more meaningful than showing activity by **band** (only one band: 10M).

---

## Available Infrastructure

### Data Aggregation Layer (DAL) Support

✅ **`MatrixAggregator.get_mode_stacked_matrix_data()`** already exists:
- Location: `contest_tools/data_aggregators/matrix_stats.py` (line 257)
- Groups by: **Mode x Time x RunStatus**
- Returns structure: `logs[CALLSIGN][MODE][RunStatus] = [values]`
- Used by: `plot_interactive_animation.py` for mode-dimension animations

### Dashboard Detection Logic

✅ **Dashboard already detects contest type:**
- `web_app/analyzer/views.py` lines 1078-1087:
  ```python
  is_single_band = len(valid_bands) == 1
  is_multi_mode = len(valid_modes) > 1
  diff_selector_type = 'mode' if (is_single_band and is_multi_mode) else 'band'
  ```

This logic is already used for the Rate Differential selector, indicating the codebase recognizes single-band, multi-mode contests as a special case.

---

## Solution Options

### Option A: Modify Existing Butterfly Chart Report (Recommended)

**Approach:** Enhance `chart_comparative_activity_butterfly.py` to support both band and mode dimensions.

**Pros:**
- ✅ Single report to maintain
- ✅ Reuses existing chart structure and styling
- ✅ Consistent user experience (same chart type, different dimension)
- ✅ Leverages existing DAL method (`get_mode_stacked_matrix_data()`)
- ✅ Minimal dashboard changes (just tab label/title)

**Cons:**
- ⚠️ Report becomes more complex (needs dimension detection logic)
- ⚠️ Need to handle both data structures (bands vs modes)

**Implementation Details:**

1. **Report Changes:**
   - Add dimension detection: Check if contest is single-band, multi-mode
   - Use `get_mode_stacked_matrix_data()` when mode dimension is appropriate
   - Use `get_stacked_matrix_data()` when band dimension is appropriate
   - Update subplot titles: "Band: {b}" → "Mode: {m}" for mode dimension
   - Update chart title: "All Bands" → "All Modes" for mode dimension

2. **Dashboard Changes:**
   - Conditionally change tab label: "Band Activity" → "Mode Activity" for single-band, multi-mode
   - Conditionally change chart title: "Band Activity Butterfly Chart" → "Mode Activity Butterfly Chart"
   - Keep same container IDs and JavaScript logic (chart structure unchanged)

3. **Report ID/Name:**
   - Keep same report ID: `chart_comparative_activity_butterfly`
   - Report name can remain generic: "Comparative Activity Butterfly Chart"
   - Or make it dynamic: "Comparative Band Activity" vs "Comparative Mode Activity"

---

### Option B: Create New Mode Activity Report

**Approach:** Create `chart_comparative_mode_activity_butterfly.py` as a separate report.

**Pros:**
- ✅ Clear separation of concerns
- ✅ Simpler individual reports
- ✅ Can optimize each report for its specific dimension

**Cons:**
- ❌ Code duplication (butterfly chart logic duplicated)
- ❌ Two reports to maintain
- ❌ Dashboard needs conditional logic to select which report to use
- ❌ Manifest/artifact discovery becomes more complex

**Implementation Details:**

1. **New Report:**
   - Copy `chart_comparative_activity_butterfly.py` → `chart_comparative_mode_activity_butterfly.py`
   - Replace `get_stacked_matrix_data()` with `get_mode_stacked_matrix_data()`
   - Update subplot titles to "Mode: {m}"
   - Update report ID: `chart_comparative_mode_activity_butterfly`
   - Update report name: "Comparative Mode Activity Butterfly Chart"

2. **Report Generator:**
   - Add conditional logic to generate appropriate report based on contest type
   - Or generate both and let dashboard select which to display

3. **Dashboard Changes:**
   - Discover both report types from manifest
   - Conditionally show "Band Activity" or "Mode Activity" tab
   - Use appropriate report artifact based on contest type

---

### Option C: Hybrid Approach (Report Variant)

**Approach:** Keep single report but add a "variant" parameter or auto-detect dimension.

**Pros:**
- ✅ Single report codebase
- ✅ Explicit control when needed
- ✅ Backward compatible

**Cons:**
- ⚠️ Similar complexity to Option A
- ⚠️ May need variant configuration in contest definitions

**Implementation Details:**

Similar to Option A, but potentially add explicit configuration:
- Contest definition: `"butterfly_chart_dimension": "mode"` (optional, auto-detected if missing)
- Or use existing `animation_dimension` field as hint

---

## Recommended Approach: Option A (Modify Existing Report)

### Rationale

1. **Infrastructure Already Exists:**
   - DAL method `get_mode_stacked_matrix_data()` is ready
   - Dashboard detection logic already identifies single-band, multi-mode contests
   - Chart structure is identical (just swap bands → modes)

2. **Minimal Code Changes:**
   - Report: Add dimension detection + conditional data fetching
   - Dashboard: Update tab labels/titles conditionally
   - No new files needed

3. **Consistency:**
   - Same chart type, same user experience
   - Follows existing pattern (animation report already does this)

4. **Maintainability:**
   - Single report to maintain
   - Clear dimension detection logic
   - Easy to extend to other dimensions if needed

---

## Implementation Plan (Option A)

### Phase 1: Report Enhancement

**File:** `contest_tools/reports/chart_comparative_activity_butterfly.py`

1. **Add Dimension Detection:**
   ```python
   def _determine_dimension(self) -> str:
       """Determine if chart should use band or mode dimension."""
       # Check contest definition
       if self.logs:
           contest_def = self.logs[0].contest_definition
           valid_bands = contest_def.valid_bands
           valid_modes = contest_def.valid_modes
           
           # Single-band, multi-mode → mode dimension
           if len(valid_bands) == 1 and len(valid_modes) > 1:
               return "mode"
       
       # Default: band dimension
       return "band"
   ```

2. **Update `generate()` method:**
   - Call `_determine_dimension()`
   - Use `get_mode_stacked_matrix_data()` if dimension is "mode"
   - Use `get_stacked_matrix_data()` if dimension is "band"
   - Pass dimension to `_create_figure()`

3. **Update `_create_figure()` method:**
   - Accept `dimension` parameter ("band" or "mode")
   - Use `data['modes']` instead of `data['bands']` when dimension is "mode"
   - Update subplot titles: `f"Mode: {m}"` vs `f"Band: {b}"`
   - Update title lines: "All Modes" vs "All Bands"

### Phase 2: Dashboard Updates

**File:** `web_app/analyzer/views.py`

1. **Tab Label Logic:**
   - Add to context: `'activity_tab_label': 'Mode Activity' if (is_single_band and is_multi_mode) else 'Band Activity'`
   - Add to context: `'activity_tab_title': 'Mode Activity Butterfly Chart' if (is_single_band and is_multi_mode) else 'Band Activity Butterfly Chart'`

**File:** `web_app/analyzer/templates/analyzer/qso_dashboard.html`

1. **Tab Button:**
   - Change label from hardcoded "Band Activity Comparison" to `{{ activity_tab_label }} Comparison`

2. **Tab Pane:**
   - Change card header from "Band Activity Butterfly Chart" to `{{ activity_tab_title }}`

3. **JavaScript:**
   - No changes needed (container IDs and logic remain the same)

### Phase 3: Testing

1. **ARRL 10 Meter (Single-Band, Multi-Mode):**
   - Verify tab shows "Mode Activity"
   - Verify chart shows CW and PH subplots
   - Verify butterfly chart works correctly

2. **CQ WW (Multi-Band, Single-Mode):**
   - Verify tab shows "Band Activity" (backward compatibility)
   - Verify chart shows band subplots
   - Verify no regression

3. **ARRL FD (Multi-Band, Multi-Mode):**
   - Verify tab shows "Band Activity" (band is primary dimension)
   - Verify chart shows band subplots

---

## Alternative Considerations

### Should We Support Both Dimensions Simultaneously?

**Question:** For multi-band, multi-mode contests (e.g., ARRL FD), should we show both band and mode activity?

**Answer:** Not initially. The butterfly chart is designed for pairwise comparison, and showing both dimensions would require:
- Two separate tabs (Band Activity + Mode Activity)
- Or a complex 2D visualization (band x mode matrix)

**Recommendation:** Start with single dimension (band for multi-band, mode for single-band multi-mode). Add mode dimension support for multi-band contests later if needed.

### Should We Use `animation_dimension` Field?

**Question:** Should we use the existing `animation_dimension: "mode"` field from ARRL 10 contest definition?

**Answer:** Yes, as a hint, but also check `valid_bands` and `valid_modes` for robustness:
- If `animation_dimension == "mode"` AND single-band AND multi-mode → use mode
- Otherwise → use band (default)

This provides explicit configuration while maintaining auto-detection fallback.

---

## Summary

**Recommended Solution:** **Option A - Modify Existing Report**

**Key Changes:**
1. Enhance `chart_comparative_activity_butterfly.py` to detect dimension and use appropriate DAL method
2. Update dashboard tab labels/titles conditionally based on contest type
3. Keep same chart structure and JavaScript logic

**Benefits:**
- ✅ Minimal code changes
- ✅ Leverages existing infrastructure
- ✅ Maintains consistency
- ✅ Backward compatible

**Files to Modify:**
- `contest_tools/reports/chart_comparative_activity_butterfly.py` (add dimension detection)
- `web_app/analyzer/views.py` (add conditional tab labels to context)
- `web_app/analyzer/templates/analyzer/qso_dashboard.html` (use conditional labels)

**Estimated Complexity:** Low-Medium (straightforward dimension swap with existing DAL support)
