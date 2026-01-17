# Interactive Animation Implementation Strategy - Final Discussion

**Date:** 2026-01-07  
**Context:** Need to decide implementation approach for interactive animation variants. Key constraints: plugin-based architecture, design for current problem, don't preclude future expansion.

## Current Understanding

### JSON Structure Reality:
- **Mode-divided contests:** Some contests have separate JSON files per mode:
  - `cq_ww_cw.json`, `cq_ww_ssb.json`, `cq_ww_rtty.json` (3 files for CQ WW)
  - `cq_wpx_cw.json`, `cq_wpx_ssb.json`
  - `arrl_dx_cw.json`, `arrl_dx_ssb.json`
- **Mode-combined contests:** Some contests have modes in single JSON:
  - `arrl_10.json` (CW + SSB in same contest)
  - `arrl_fd.json` (CW + SSB + PH)

**Key Insight:** If contest has separate JSON files per mode → effectively single-mode contests at JSON level (auto-detect works). If contest has multiple modes in one JSON → need explicit configuration.

### Contest Distribution:
- **Multi-band, single-mode:** Most contests (CQ WW-CW, CQ WW-SSB, ARRL DX-CW, etc.)
- **Single-band, multi-mode:** ARRL-10 (1 band, 2 modes)
- **Multi-band, multi-mode:** ARRL FD (8 bands, 3 modes) - **DEFER**

### Design Principles:
1. **Contest-unique things in code plugins, not JSON config** - Parsing, multipliers, etc. are code-based
2. **Design for current problem but don't preclude future expansion**
3. **Explicit is better than implicit** - But where does explicit belong?

## The Question: Implementation Architecture

**How to handle one-axis animations?**

Three options:

### Option 1: Two Separate Reports (Band Axis vs Mode Axis)

**Approach:**
```python
# plot_interactive_animation_band.py
class Report(ContestReport):
    report_id = "interactive_animation_band"
    # Handles band dimension (call -> band -> mode structure)

# plot_interactive_animation_mode.py
class Report(ContestReport):
    report_id = "interactive_animation_mode"
    # Handles mode dimension (call -> mode -> band structure)
```

**JSON Configuration:**
```json
{
  "contest_name": "CQ-WW-CW",
  // Auto-detects: mode-divided JSON → includes "interactive_animation_band"
}

{
  "contest_name": "ARRL-10",
  "included_reports": ["interactive_animation_mode"]
  // OR: excludes "interactive_animation_band"
}
```

**Pros:**
- Clear separation of concerns
- Each implementation is focused and simple
- Easy to test independently
- Works with existing report inclusion/exclusion system
- Follows plugin pattern (separate code modules)

**Cons:**
- Two report IDs to manage
- Potential code duplication (racing bars, time formatting, etc.)
- JSON needs to include/exclude appropriately
- Need to decide which one for each contest

**Mitigation:**
- Shared utilities class to prevent duplication
- Auto-detection can determine which report to include

### Option 2: One Generic Report (Handles Both Dimensions)

**Approach:**
```python
# plot_interactive_animation.py
class Report(ContestReport):
    report_id = "interactive_animation"
    
    def _determine_dimension(self):
        """Determines which dimension to use: 'band' or 'mode'"""
        # Check explicit JSON config
        if hasattr(contest_def, 'animation_dimension'):
            return contest_def.animation_dimension
        
        # Auto-detect: mode-divided JSON → band dimension
        # Multi-mode JSON → need explicit config (error/warning)
        ...
    
    def _prepare_data(self, dimension: str, **kwargs):
        """Prepares data for specified dimension"""
        if dimension == 'band':
            return self._prepare_data_band(**kwargs)
        elif dimension == 'mode':
            return self._prepare_data_mode(**kwargs)
    
    def generate(self, **kwargs):
        dimension = self._determine_dimension()
        data = self._prepare_data(dimension, **kwargs)
        # Use dimension to determine chart structure
```

**JSON Configuration:**
```json
{
  "contest_name": "CQ-WW-CW",
  // Auto-detects: mode-divided JSON → "band" dimension (default)
}

{
  "contest_name": "ARRL-10",
  "animation_dimension": "mode"  // Explicit for multi-mode JSON
}
```

**Pros:**
- Single report ID (`interactive_animation`)
- No duplication (shared implementation)
- Dimension detection encapsulated in report
- Works with auto-detection
- Can add dimension detection as plugin/utility (future expansion)

**Cons:**
- More complex code (conditional logic)
- Multiple code paths to test
- Dimension determination logic needs to be robust

**Mitigation:**
- Clear internal methods: `_prepare_data_band()` vs `_prepare_data_mode()`
- Dimension detection as separate utility method (extensible)
- Comprehensive tests for both dimensions

### Option 3: Base Class + Dimension Variants (Inheritance)

**Approach:**
```python
# plot_interactive_animation_base.py
class AnimationBase(ContestReport):
    """Shared utilities and common logic"""
    def _format_time_display(self, ...):
        # Shared utility
    def _get_mode_color(self, ...):
        # Shared utility
    def _generate_racing_bars(self, ...):
        # Shared logic

# plot_interactive_animation_band.py
class Report(AnimationBase):
    report_id = "interactive_animation_band"
    def _prepare_data(self, ...):
        # Band-specific data prep
    def generate(self, ...):
        # Use base utilities + band logic

# plot_interactive_animation_mode.py
class Report(AnimationBase):
    report_id = "interactive_animation_mode"
    def _prepare_data(self, ...):
        # Mode-specific data prep
    def generate(self, ...):
        # Use base utilities + mode logic
```

**Pros:**
- Shared utilities prevent duplication
- Clear separation of dimension-specific logic
- Each variant is focused
- Follows inheritance pattern (extensible)
- Works with report inclusion/exclusion

**Cons:**
- Three files instead of one or two
- More complexity (inheritance)
- Still need to decide which report for each contest

## Analysis: Which Approach Fits Design Principles?

### Principle 1: "Contest-unique things in code plugins, not JSON config"

**Interpretation:** Contest-specific logic should be in Python code (parsers, multipliers, resolvers), not JSON configuration.

**For Animation:**
- **Dimension selection** is contest-specific logic (ARRL-10 uses mode, CQ-WW uses band)
- **Should this be code-based (plugin) or JSON-based (config)?**

**Argument for Code-Based (Plugin):**
- Dimension determination logic could be a plugin/utility
- Contest-specific logic encapsulated in code
- JSON just has data (valid_bands, valid_modes)

**Argument for JSON-Based (Config):**
- Dimension choice is a configuration decision (which visualization to show)
- Not algorithmic logic like parsing or multipliers
- More like "include this report" vs "exclude this report"

**Assessment:** Dimension selection is **configuration**, not algorithmic logic. JSON is appropriate.

### Principle 2: "Design for current problem but don't preclude future expansion"

**Current Problem:**
- One-axis animations (band OR mode)
- Two cases: Multi-band single-mode (most contests), Single-band multi-mode (ARRL-10)
- Two-axis case is deferred (current sub-panels don't work well)

**Future Expansion:**
- Two-axis animations (ARRL FD, VHF)
- Possibly other dimensions (score-based, time-based)
- Possibly different chart structures

**Which Approach Allows Future Expansion?**

**Option 1 (Two Separate Reports):**
- Easy to add new variants (e.g., `interactive_animation_two_axis.py`)
- Each variant is independent
- Clear pattern for adding new dimensions
- **Good for expansion**

**Option 2 (One Generic Report):**
- Can add dimension detection logic
- Can add new dimension cases to `_determine_dimension()`
- Can add new `_prepare_data_X()` methods
- **Good for expansion IF dimensions are similar**
- **Less good if two-axis needs completely different structure**

**Option 3 (Base Class + Variants):**
- Easy to add new variants inheriting from base
- Shared utilities remain shared
- Clear pattern for adding new dimensions
- **Best for expansion** (inheritance pattern, shared utilities)

### Principle 3: "Explicit is better than implicit"

**For Mode-Divided JSON:**
- If contest has separate JSON files per mode (`cq_ww_cw.json`) → effectively single-mode
- Auto-detect: "This is a mode-divided contest → use band dimension"
- **Implicit but safe** (no ambiguity)

**For Mode-Combined JSON:**
- If contest has multiple modes in one JSON (`arrl_10.json`) → need explicit config
- **Explicit required** (ambiguous which dimension)

**Assessment:** 
- **Auto-detect for mode-divided** is acceptable (implicit but unambiguous)
- **Explicit config for mode-combined** is required (follows principle)

## Recommendation: Option 2 (One Generic Report)

### Rationale:

1. **Fits Current Problem:**
   - One-axis animations are structurally similar (just dimension changes)
   - Data restructuring is the main difference (`band->mode` vs `mode->band`)
   - Shared logic (racing bars, time formatting, frames) is substantial

2. **Doesn't Preclude Future Expansion:**
   - Can add `_determine_dimension()` method that checks for `two_axis` variant
   - Can add `_prepare_data_two_axis()` method when needed
   - If two-axis needs completely different structure, can refactor to Option 1 or 3 later
   - JSON config pattern works for any number of variants

3. **Follows Plugin Pattern (Partially):**
   - Dimension detection logic can be a utility/helper method
   - Data preparation is pluggable (`_prepare_data_band()` vs `_prepare_data_mode()`)
   - Main structure is shared (not contest-unique)

4. **Balances Complexity:**
   - Less code duplication than Option 1
   - Less file complexity than Option 3
   - Single report ID (simpler for users)
   - Conditional logic is manageable (two cases now, maybe three later)

### Implementation Structure:

```python
class Report(ContestReport):
    report_id = "interactive_animation"
    
    def _determine_dimension(self, contest_def):
        """Determines visualization dimension: 'band' or 'mode'"""
        # Explicit config wins
        if hasattr(contest_def, 'animation_dimension'):
            return contest_def.animation_dimension
        
        # Auto-detect: Mode-divided JSON → band dimension
        # (Can check if contest name has mode suffix like "-CW", or valid_modes has 1 item)
        # For now: Default to 'band', multi-mode contests must specify 'mode'
        return 'band'  # Default with warning if multi-mode
        
    def _prepare_data_band(self, **kwargs):
        """Prepares data structure: call -> band -> mode"""
        # Existing logic from current implementation
        
    def _prepare_data_mode(self, **kwargs):
        """Prepares data structure: call -> mode -> band"""
        # Transpose band->mode to mode->band
        # Similar logic, different data access pattern
        
    def generate(self, **kwargs):
        dimension = self._determine_dimension(self.logs[0].contest_definition)
        data = self._prepare_data(dimension, **kwargs)
        # Use dimension for labels, titles, etc.
```

### JSON Configuration:

```json
{
  "contest_name": "CQ-WW-CW",
  // No animation_dimension - auto-detects 'band' (mode-divided JSON)
}

{
  "contest_name": "ARRL-10",
  "animation_dimension": "mode"  // Explicit for multi-mode JSON
}
```

### Future Expansion (Two-Axis):

When we need two-axis animations:

**Option A: Extend Generic Report**
```python
def _determine_dimension(self):
    if hasattr(contest_def, 'animation_dimension'):
        return contest_def.animation_dimension  # 'band', 'mode', or 'two_axis'
    # ... existing logic
```

**Option B: Refactor to Separate Variants**
- Create `interactive_animation_two_axis.py` when needed
- Generic report becomes `interactive_animation_one_axis.py`
- Pattern established for future variants

## Alternative Consideration: Option 1 (Two Separate Reports)

If you prefer clearer separation and explicit report selection:

**Pros:**
- More explicit (JSON includes/excludes specific report)
- Each implementation is simpler
- Better for future variants (clear pattern)

**Cons:**
- More files to maintain
- Need shared utilities to prevent duplication
- Two report IDs instead of one

## Questions for Discussion

1. **Is dimension selection "contest-unique logic" (code plugin) or "configuration" (JSON)?**
   - My interpretation: Configuration (which visualization to show)
   - But detection logic could be plugin/utility

2. **How similar are band-axis and mode-axis implementations?**
   - If very similar → Generic report (Option 2)
   - If very different → Separate reports (Option 1)

3. **Will two-axis need completely different structure?**
   - If yes → Separate reports make more sense (Option 1 or 3)
   - If maybe → Generic report can evolve (Option 2)

4. **Do we want one report ID or multiple report IDs?**
   - One ID → Generic report (Option 2)
   - Multiple IDs → Separate reports (Option 1 or 3)

---

## Status: IMPLEMENTED

**Date Completed:** 2026-01-07  
**Final Decision:** **Option 2 - Generic Report with JSON-Controlled Dimension Selection**

**See:** `ANIMATION_DIMENSION_IMPLEMENTATION_SUMMARY.md` for complete implementation details.

### Implementation Summary:

- ✅ **Single Report ID:** `interactive_animation` (one report, not variants)
- ✅ **JSON Configuration:** `animation_dimension` field in contest definition JSON
- ✅ **Auto-Detection:** Mode-divided contests auto-detect `"band"` dimension
- ✅ **Explicit Config:** Multi-mode contests require explicit `animation_dimension` field
- ✅ **Methods Implemented:** `_determine_dimension()`, `_prepare_data_band()`, `_prepare_data_mode()`
- ✅ **ARRL-10 Configured:** `arrl_10.json` includes `animation_dimension: "mode"`

### Key Decisions Made:

1. **Architecture:** Generic report (Option 2) - single report ID with dimension routing
2. **Configuration:** JSON `animation_dimension` field with auto-detection fallback
3. **Detection:** Based on contest definition JSON, not log data
4. **Two-Axis:** Deferred until ARRL FD/VHF integration

### Future Considerations:

- ⏳ Two-axis dimension: Defer until ARRL FD/VHF integration
- ⏳ Butterfly charts: Handle as they arise in integration
- ⏳ Other affected charts: Handle on case-by-case basis
