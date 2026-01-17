# Report Architecture: Monolithic vs Variants Discussion

**Date:** 2026-01-07  
**Context:** Interactive animation chart shows wrong dimension (band vs mode) for ARRL-10. Need to decide architecture approach.

## Current Understanding

### Contest Characteristics:
- **ARRL-10**: 1 band (10M), 2 modes (CW/SSB), **mode-based multipliers** (`multiplier_report_scope: "per_mode"`)
- **CQ-160**: 1 band (160M), 2 modes (CW/SSB) but **single contest with two weekends** (not mode-based multipliers)
- **ARRL FD**: 8 bands, 3 modes - band dimension still makes sense
- **CQ WW**: 6 bands, 2 modes - band dimension makes sense

### Report Inclusion/Exclusion:
- **Default behavior**: All reports are included unless excluded
- **`excluded_reports`**: Array of report IDs to skip (e.g., `["text_wae_score_report"]`)
- **`included_reports`**: Array of report IDs to include (if specified, ONLY these run)
- **`is_specialized`**: If `True`, report only runs if in `included_reports` (e.g., WRTC uses this)

### Current Report Structure:
All reports are discovered dynamically and follow a common interface:
- Single `Report` class per file
- `report_id`, `report_name`, `report_type` attributes
- `supports_single`, `supports_pairwise`, `supports_multi` flags
- `generate()` method

## The Question

For complex charts like `interactive_animation` that need different logic based on contest characteristics:

**Should we:**
1. **Monolithic Report with Branching Logic** - One report class with internal filtering/conditional logic
2. **Multiple Report Variants** - Separate report classes (e.g., `interactive_animation_band`, `interactive_animation_mode`)
3. **Shared Utilities + Report Variants** - Common utility classes/functions with contest-specific report wrappers

## Analysis: Interactive Animation Report

### Current Structure:
- **File**: `plot_interactive_animation.py`
- **Class**: Single `Report` class
- **Complexity**: ~500 lines, includes:
  - `_prepare_data()` - data aggregation
  - `_create_figure()` - figure generation
  - `_format_time_display()` - utility
  - `_get_mode_color()` - utility
  - `generate()` - main entry point

### What Would Change:
For band vs mode dimension:
- Data structure: `call -> band -> mode` vs `call -> mode -> band`
- X-axis labels: "Band" vs "Mode"
- Subplot titles: "By Band & Mode" vs "By Mode"
- Data access pattern throughout `_prepare_data()` and frame generation

### Complexity Assessment:
- **Data preparation**: Significant restructuring needed
- **Visualization logic**: Moderate changes (labels, axes)
- **Frame generation**: Data access pattern changes
- **Shared utilities**: `_format_time_display()`, `_get_mode_color()` stay the same

## Architecture Options Analysis

### Option 1: Monolithic Report with Branching Logic

**Approach:**
```python
class Report(ContestReport):
    def _prepare_data(self, **kwargs):
        # Detect dimension to use
        bands = matrix_raw['bands']
        contest_def = self.logs[0].contest_definition
        
        if len(bands) == 1 and contest_def.multiplier_report_scope == "per_mode":
            dimension = "mode"
            # Restructure data for mode dimension
        else:
            dimension = "band"
            # Use existing band structure
        
        return {..., 'dimension': dimension, 'bands_or_modes': ...}
    
    def generate(self, **kwargs):
        data = self._prepare_data(**kwargs)
        if data['dimension'] == "mode":
            # Use mode-specific figure generation
        else:
            # Use band-specific figure generation
```

**Pros:**
- Single report ID: `interactive_animation`
- No JSON configuration needed (auto-detects)
- All logic in one place
- Shared utilities remain shared

**Cons:**
- Complex conditional logic throughout
- Harder to test (need multiple test scenarios)
- Code paths that may never execute for certain contests
- Risk of bugs when adding new contest types
- Harder to maintain as complexity grows

### Option 2: Multiple Report Variants

**Approach:**
```python
# plot_interactive_animation_band.py
class Report(ContestReport):
    report_id = "interactive_animation_band"
    # Band-based implementation

# plot_interactive_animation_mode.py
class Report(ContestReport):
    report_id = "interactive_animation_mode"
    # Mode-based implementation

# Contest JSON:
{
  "excluded_reports": ["interactive_animation"],
  "included_reports": ["interactive_animation_mode"]  # For ARRL-10
}
```

**Pros:**
- Clear separation of concerns
- Each variant is simpler, focused
- Easier to test each variant independently
- Explicit contest configuration (JSON)
- Can have different features per variant if needed

**Cons:**
- Multiple report IDs to manage
- JSON configuration required per contest
- Potential code duplication (utilities)
- Need to decide which variant to use for each contest
- More files to maintain

### Option 3: Shared Utilities + Report Variants

**Approach:**
```python
# plot_interactive_animation_base.py
class AnimationBase:
    """Shared utilities and common logic"""
    def _format_time_display(self, ...):
        # Shared utility
    def _get_mode_color(self, ...):
        # Shared utility
    def _generate_frames(self, data, dimension, ...):
        # Shared frame generation logic

# plot_interactive_animation_band.py
class Report(ContestReport, AnimationBase):
    report_id = "interactive_animation_band"
    def _prepare_data(self, ...):
        # Band-specific data prep
    def generate(self, ...):
        # Use base utilities + band logic

# plot_interactive_animation_mode.py
class Report(ContestReport, AnimationBase):
    report_id = "interactive_animation_mode"
    def _prepare_data(self, ...):
        # Mode-specific data prep
    def generate(self, ...):
        # Use base utilities + mode logic
```

**Pros:**
- Shared utilities avoid duplication
- Each variant is focused and simple
- Easy to add new variants if needed
- Testable independently

**Cons:**
- Most complex file structure
- Multiple report IDs still need JSON configuration
- More files overall
- Need to decide which variant per contest

## Decision Factors

### Complexity of the Report:
- **High complexity** (like interactive_animation): Favors separation/variants
- **Low complexity**: Favors monolithic with branching

### How Different Are the Variants?
- **Very different** (band vs mode dimension = structural changes): Favors variants
- **Slightly different** (labels, colors): Favors monolithic with parameters

### Contest Distribution:
- **Most contests use one pattern** (band): Monolithic with exception handling
- **Many contests use different patterns**: Variants with JSON selection

### Maintenance:
- **Will this need more variants?** (e.g., time-based, score-based): Favors utilities + variants
- **One-time fix for specific contest**: Favors monolithic branching

## Case-by-Case Assessment

### Interactive Animation Chart:
- **Complexity**: HIGH (~500 lines, multiple methods)
- **Structural Difference**: HIGH (data structure change: band->mode vs mode->band)
- **Contest Distribution**: Most use band, ARRL-10 uses mode (edge case)
- **Future Variants**: Unlikely to need more variants

**Assessment**: **Tend toward monolithic with branching** - It's an edge case, but the structural difference is significant enough that clean branching is important.

### Comparative Activity Butterfly:
- **Complexity**: MEDIUM (~270 lines)
- **Structural Difference**: MEDIUM (subplot structure changes, labels change)
- **Contest Distribution**: Most use band, ARRL-10 is edge case

**Assessment**: **Monolithic with branching** - Similar to interactive animation, but less complex.

### QSO Breakdown Chart:
- **Complexity**: LOW-MEDIUM (~165 lines)
- **Structural Difference**: LOW (just subplot grid changes)
- **Contest Distribution**: Works for single-band, just shows fewer subplots

**Assessment**: **Monolithic** - Already handles single-band (just shows one subplot), no changes needed.

## Recommendation

**Hybrid Approach by Complexity:**

1. **High Complexity Reports** (Interactive Animation):
   - **Monolithic with clean branching**
   - Use clear internal methods: `_prepare_data_band()` vs `_prepare_data_mode()`
   - Detect dimension once, route to appropriate methods
   - Keep shared utilities shared

2. **Medium Complexity Reports** (Butterfly Charts):
   - **Monolithic with branching**
   - Similar pattern to interactive animation
   - Simpler, so easier to maintain

3. **Low Complexity Reports** (Breakdown Charts):
   - **Already handle edge cases** - No changes needed
   - Single-band just shows fewer subplots

**Rationale:**
- ARRL-10 is an edge case (only one contest needs mode dimension currently)
- Monolithic approach avoids JSON configuration overhead
- Clear branching keeps code maintainable
- Shared utilities stay shared (no duplication)
- Can refactor to variants later if more contests need different dimensions

## Questions for Discussion

1. **Is ARRL-10 likely to be the only contest needing mode dimension for interactive animation?**
   - If yes → Monolithic with branching
   - If more coming → Consider variants

2. **Should we add JSON configuration for dimension preference?**
   - Can start with auto-detection, add config later if needed

3. **Are there other complex reports that might need similar treatment?**
   - Should we establish a pattern now?

4. **For simpler reports that already handle single-band gracefully, do we need to change anything?**
