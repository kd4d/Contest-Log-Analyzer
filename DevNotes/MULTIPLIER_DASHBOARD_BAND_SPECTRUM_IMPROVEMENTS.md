# Multiplier Dashboard Band Spectrum Improvements - Discussion

**Date:** 2025-01-XX  
**Context:** Three improvements needed for the Multiplier Dashboard Band Spectrum section.

---

## Current State

### Band Spectrum Structure
- **Location:** `web_app/analyzer/templates/analyzer/multiplier_dashboard.html` (lines 142-313)
- **Tabs:** "All Multipliers" + one tab per multiplier type (e.g., Countries, Zones, States, etc.)
- **Data Source:** `breakdown_data['bands']` from `MultiplierStatsAggregator.get_multiplier_breakdown_data()`
- **Layout:** Vertical spectrum chart showing unique multipliers per band
- **Colors:** Uses `bg-run` (green), `bg-sp` (blue), `bg-unk` (grey) CSS classes

### Current Issues

1. **Missing Legend:**
   - No legend explaining what the colors mean (Run, S&P, Unknown)
   - Users can't understand the stacked bar segments

2. **Incomplete Legend (if one exists elsewhere):**
   - If there's a legend elsewhere, it likely only shows Run and S&P
   - Missing Unknown (grey) color explanation

3. **Band vs Mode Dimension:**
   - Always shows breakdown by **bands** (160M, 80M, 40M, 20M, 15M, 10M)
   - For single-band, multi-mode contests (e.g., ARRL 10 Meter), should show **modes** (CW, PH) instead
   - This applies to all 6 tabs (All Multipliers + 5 multiplier type tabs)

---

## Required Changes

### 1. Add Legend to Band Spectrum

**Location:** Above or below the Band Spectrum container

**Content:**
- Run (Green) - `#22c55e`
- S&P (Blue) - `#3b82f6`
- Unknown (Grey) - `#9ca3af`

**Implementation Options:**
- **Option A:** Add legend above the tab pills (before line 147)
- **Option B:** Add legend below the Band Spectrum container (after line 313)
- **Option C:** Add legend inside each tab pane (redundant but clear)

**Recommendation:** Option A - Single legend above tabs, visible for all tabs

### 2. Ensure Unknown is in Legend

**Current CSS Colors (from `dashboard.css`):**
```css
--color-run: #22c55e;  /* Green */
--color-sp: #3b82f6;   /* Blue */
--color-unk: #9ca3af;  /* Grey */
```

**Verification:** The colors are already defined. Need to ensure the legend includes all three.

### 3. Mode-Based Breakdown for Single-Band, Multi-Mode Contests

**Detection Logic:**
- Check if contest is single-band, multi-mode (same logic as QSO Dashboard)
- If `len(valid_bands) == 1` and `len(valid_modes) > 1` → use mode dimension

**Data Structure Changes:**

**Current Structure:**
```python
breakdown_data = {
    'totals': [...],
    'bands': [
        {'label': '160M', 'rows': [...]},
        {'label': '80M', 'rows': [...]},
        ...
    ]
}
```

**Needed for Mode Dimension:**
```python
breakdown_data = {
    'totals': [...],
    'modes': [  # Instead of 'bands'
        {'label': 'CW', 'rows': [...]},
        {'label': 'PH', 'rows': [...]},
        ...
    ]
}
```

**Implementation Options:**

**Option A: Modify Aggregator (Recommended)**
- Add `get_multiplier_breakdown_data(dimension='band')` parameter
- When `dimension='mode'`, group by mode instead of band
- Return structure with `'modes'` key instead of `'bands'` key

**Option B: Transform in View**
- Keep aggregator as-is (band-based)
- In `multiplier_dashboard` view, detect contest type
- Transform band data to mode data if needed
- More complex, but doesn't change aggregator API

**Option C: Dual Structure**
- Aggregator returns both `'bands'` and `'modes'` keys
- View selects which to use based on contest type
- More data, but flexible

**Recommendation:** Option A - Cleanest, most maintainable

---

## Implementation Plan

### Phase 1: Add Legend

1. **Template Changes:**
   - Add legend HTML above tab pills (line ~146)
   - Use Bootstrap styling to match dashboard theme
   - Include all three colors: Run, S&P, Unknown

2. **CSS Verification:**
   - Ensure colors match CSS variables
   - Test visual appearance

### Phase 2: Mode Dimension Support

1. **Aggregator Changes:**
   - Modify `MultiplierStatsAggregator.get_multiplier_breakdown_data()`
   - Add optional `dimension` parameter (default 'band')
   - When `dimension='mode'`, group by mode instead of band
   - Return appropriate key ('bands' or 'modes')

2. **View Changes:**
   - Detect contest type (single-band, multi-mode)
   - Pass `dimension` parameter to aggregator
   - Update context to use `low_modes_data` / `high_modes_data` instead of `low_bands_data` / `high_bands_data`
   - Or use generic `low_items_data` / `high_items_data` for flexibility

3. **Template Changes:**
   - Update template to handle both `bands` and `modes` data
   - Use conditional logic: `{% if is_single_band and is_multi_mode %}`
   - Update column headers: "Band" → "Mode" when appropriate
   - Update labels: "All Bands" → "All Modes" when appropriate

### Phase 3: Testing

1. **Multi-Band Contest (CQ WW):**
   - Verify band breakdown still works
   - Verify legend appears correctly

2. **Single-Band, Multi-Mode Contest (ARRL 10 Meter):**
   - Verify mode breakdown appears
   - Verify all 6 tabs show mode data
   - Verify legend includes Unknown

---

## Data Structure Details

### Current Band-Based Structure:
```python
{
    'totals': [
        {'label': 'TOTAL', 'stations': [...]},
        {'label': 'Countries', 'stations': [...]},
        {'label': 'Zones', 'stations': [...]}
    ],
    'bands': [
        {
            'label': '160M',
            'rows': [
                {'label': '160M', 'stations': [...]},
                {'label': '160M_Countries', 'stations': [...]},
                {'label': '160M_Zones', 'stations': [...]}
            ]
        },
        ...
    ]
}
```

### Needed Mode-Based Structure:
```python
{
    'totals': [
        {'label': 'TOTAL', 'stations': [...]},
        {'label': 'States', 'stations': [...]},
        {'label': 'Provinces', 'stations': [...]},
        ...
    ],
    'modes': [
        {
            'label': 'CW',
            'rows': [
                {'label': 'CW', 'stations': [...]},
                {'label': 'CW_States', 'stations': [...]},
                {'label': 'CW_Provinces', 'stations': [...]},
                ...
            ]
        },
        {
            'label': 'PH',
            'rows': [
                {'label': 'PH', 'stations': [...]},
                {'label': 'PH_States', 'stations': [...]},
                {'label': 'PH_Provinces', 'stations': [...]},
                ...
            ]
        }
    ]
}
```

---

## Questions to Resolve

1. **Mode Ordering:**
   - Should modes be sorted in a specific order? (CW, PH, RTTY, etc.)
   - Use same order as `valid_modes` from contest definition?

2. **Low/High Split for Modes:**
   - Currently bands are split into "low" (160M, 80M, 40M) and "high" (20M, 15M, 10M)
   - For modes, should we split? Or show all modes together?
   - **Recommendation:** Show all modes together (no split needed)

3. **Legend Placement:**
   - Above tabs? Below tabs? Inside each tab?
   - **Recommendation:** Above tabs, single legend for all tabs

4. **Backward Compatibility:**
   - Ensure multi-band contests still work correctly
   - Default to band dimension if not explicitly mode

---

## Summary

**Three Changes Required:**

1. ✅ **Add Legend** - Include Run, S&P, and Unknown colors
2. ✅ **Include Unknown** - Ensure grey (Unknown) is in the legend
3. ✅ **Mode Dimension** - For single-band, multi-mode contests, show modes instead of bands

**Complexity:** Medium
- Legend: Simple template addition
- Mode dimension: Requires aggregator changes + view logic + template updates

**Impact:** High
- Improves usability (legend explains colors)
- Enables proper visualization for ARRL 10 Meter and similar contests
- Maintains backward compatibility for multi-band contests
