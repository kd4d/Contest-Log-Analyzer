# Animation Variants Architecture - Technical Discussion

**Date:** 2026-01-07  
**Context:** Interactive animation needs dimension flexibility. User wants discussion from UI/UX, software engineering, and web best practices perspectives.

## Contest Landscape (Corrected Understanding)

### Single-Axis Contests (One Primary Dimension):
- **CQ WW** (6 bands, 1 mode per weekend) → **Band dimension**
- **ARRL DX** (6 bands, 1 mode per weekend) → **Band dimension**
- **CQ 160** (1 band, 2 weekends - not mode multipliers) → **Band dimension** (single band)
- **ARRL 10** (1 band, 2 modes - mode-based multipliers) → **Mode dimension**

**Key Insight:** The meaningful comparison dimension depends on the contest's scoring structure, not just data availability.

### Two-Axis Contests (Both Dimensions Significant):
- **ARRL FD** (8 bands, 3 modes) → **Both Band AND Mode**
- **VHF Contests** (likely multiple bands, multiple modes) → **Both Band AND Mode**

**Key Insight:** When both dimensions are meaningful, we need a different visualization approach.

## Architecture Decision: Variants vs Monolithic

### User's Position:
- **Two variants**: One-axis (band OR mode) and Two-axis (band AND mode)
- **JSON selection** determines which variant to use
- **Defer butterfly charts** for now
- **Other charts**: Handle as they arise
- **Overall approach**: JSON selection + code variants with shared utilities
- **Rationale**: Too many special cases for monolithic branching

### My Analysis:

#### From Software Engineering Perspective:

**Configuration Over Code Branching:**
- **Pros of Variants + JSON:**
  - Explicit: Contest definition clearly states which visualization to use
  - Testable: Each variant can be tested independently
  - Maintainable: Changes to one variant don't affect others
  - Extensible: Easy to add new variants (e.g., "score-based", "time-based") without touching existing code
  - Clear boundaries: Each variant has a focused responsibility

- **Cons of Variants + JSON:**
  - More files: Need `plot_interactive_animation_one_axis.py` and `plot_interactive_animation_two_axis.py`
  - More IDs: Need to manage report IDs in JSON
  - Potential duplication: Risk of copying code between variants
  - Decision complexity: Each contest needs explicit configuration

**Mitigation Strategies:**
- **Shared Utilities:** Extract common logic (`_format_time_display()`, `_get_mode_color()`, frame generation) to base class or utility module
- **Report ID Strategy:** Use descriptive IDs (`interactive_animation_one_axis`, `interactive_animation_two_axis`) rather than generic suffixes
- **Documentation:** Clear JSON schema/docs for when to use which variant

#### From UI/UX Perspective:

**User Mental Models:**
- **Consistency:** Users develop expectations based on contest type. Single-axis contest → simple comparison. Multi-axis → complex comparison.
- **Clarity:** Showing the "wrong" dimension (band when mode matters) creates cognitive load and confusion
- **Progressive Complexity:** One-axis charts are easier to understand; two-axis charts are more powerful but more complex
- **Discoverability:** If variants are clearly named, users understand why they're seeing different visualizations

**Design Principles:**
- **Progressive Disclosure:** Show complexity when needed (two-axis), simplicity when possible (one-axis)
- **Appropriate Metaphors:** Single-axis = "racing bars" comparison; Two-axis = "heatmap" or "grid" comparison
- **Visual Hierarchy:** Single-axis focuses attention on one dimension; Two-axis allows cross-dimensional analysis

**Potential UX Concerns:**
- **Inconsistency:** Different visualizations for different contests might feel like "broken" behavior if not explained
- **Learning Curve:** Users familiar with one variant might struggle with the other
- **Context Switching:** Mental switch between "band-focused" and "mode-focused" thinking

**Mitigation:**
- **Clear Titles:** Chart titles explicitly state the dimension(s) (e.g., "Band Activity Animation" vs "Mode Activity Animation" vs "Band & Mode Activity Animation")
- **Help/Guide:** Dashboard help explains why different contests have different visualizations
- **Consistent Layout:** Keep racing bars on top, detailed view on bottom (familiar structure across variants)

#### From Web Best Practices Perspective:

**Progressive Enhancement:**
- **Start Simple:** One-axis variant is simpler, works for most contests
- **Enhance When Needed:** Two-axis variant adds capability for complex contests
- **Graceful Degradation:** If two-axis variant fails, could fall back to one-axis (though probably not needed here)

**Performance Considerations:**
- **Bundle Size:** Having multiple variants means more code, but:
  - Variants are loaded dynamically based on contest type (only one loads per session)
  - Shared utilities reduce duplication
  - Modern bundlers can tree-shake unused code

**Maintainability:**
- **Single Responsibility:** Each variant has one job
- **Open/Closed Principle:** Add new variants without modifying existing ones
- **Dependency Inversion:** Both variants depend on shared utilities, not each other

**API Design:**
- **Explicit Over Implicit:** JSON configuration is explicit and discoverable
- **Convention Over Configuration:** Default could be one-axis if not specified (backward compatibility)
- **Schema Validation:** JSON schema could validate that contests specify animation variant

## Proposed Architecture

### Report Structure:

```
contest_tools/reports/
  plot_interactive_animation_base.py    # Shared utilities and base logic
  plot_interactive_animation_one_axis.py  # One-axis variant (band OR mode)
  plot_interactive_animation_two_axis.py  # Two-axis variant (band AND mode)
```

### JSON Configuration:

```json
{
  "contest_name": "ARRL-10",
  "animation_variant": "one_axis_mode",  // or "one_axis_band", "two_axis"
  ...
}
```

**Variant Values:**
- `"one_axis_band"`: Band dimension (default for multi-band contests)
- `"one_axis_mode"`: Mode dimension (for ARRL-10)
- `"two_axis"`: Both band and mode dimensions (for ARRL FD, VHF)

**Default Behavior:**
- If not specified, auto-detect based on contest characteristics:
  - `len(valid_bands) == 1` AND `multiplier_report_scope == "per_mode"` → `"one_axis_mode"`
  - `len(valid_bands) > 1` AND multiple modes → `"two_axis"` (could be flagged in JSON)
  - Otherwise → `"one_axis_band"` (backward compatible)

### Shared Utilities Base Class:

```python
class AnimationBase:
    """Shared utilities for interactive animation variants"""
    
    def _format_time_display(self, iso_string: str) -> Tuple[str, str]:
        # Shared time formatting
    
    def _get_mode_color(self, base_hex: str, mode: str) -> str:
        # Shared color calculation
    
    def _generate_racing_bars(self, fig, data, ...):
        # Shared racing bars logic (top pane)
    
    def _configure_layout(self, fig, title, footer, ...):
        # Shared layout configuration
```

### Variant Implementation:

```python
# plot_interactive_animation_one_axis.py
class Report(ContestReport, AnimationBase):
    report_id = "interactive_animation_one_axis"
    
    def _prepare_data(self, dimension: str, **kwargs):
        # Prepare data for one-axis (band OR mode)
    
    def _generate_detail_charts(self, fig, data, dimension, ...):
        # Generate bottom charts for one-axis variant

# plot_interactive_animation_two_axis.py
class Report(ContestReport, AnimationBase):
    report_id = "interactive_animation_two_axis"
    
    def _prepare_data(self, **kwargs):
        # Prepare data for two-axis (band AND mode)
    
    def _generate_detail_charts(self, fig, data, ...):
        # Generate bottom charts for two-axis variant (grid/heatmap approach?)
```

## Questions for Discussion

### 1. JSON Configuration Strategy:

**Option A: Explicit `animation_variant` field**
```json
{
  "animation_variant": "one_axis_mode"
}
```
- **Pros:** Clear, explicit, no ambiguity
- **Cons:** Every contest needs to specify (unless we auto-detect with fallback)

**Option B: Auto-detect with optional override**
```json
{
  "animation_variant": "one_axis_mode"  // Optional, auto-detect if missing
}
```
- **Pros:** Backward compatible, intelligent defaults
- **Cons:** Auto-detection logic could be wrong for edge cases

**Option C: Derived from contest characteristics**
- Use existing fields (`valid_bands`, `multiplier_report_scope`) to determine
- No new JSON field needed
- **Pros:** No JSON changes required
- **Cons:** Less explicit, harder to override if logic is wrong

**Recommendation:** **Option B** - Auto-detect with optional override. Provides intelligent defaults while allowing explicit control.

### 2. Report ID Strategy:

**Option A: Single ID with variant suffix in JSON**
- Report ID: `interactive_animation`
- JSON specifies which variant implementation to load
- **Pros:** Users always see `interactive_animation` in dashboard
- **Cons:** Requires report loader changes to handle variant routing

**Option B: Multiple IDs, JSON includes the right one**
- Report IDs: `interactive_animation_one_axis`, `interactive_animation_two_axis`
- JSON includes the appropriate ID in `included_reports` or excludes others
- **Pros:** Explicit, works with existing report system
- **Cons:** Dashboard shows different report IDs for different contests

**Recommendation:** **Option B** - Multiple IDs. Simpler implementation, works with existing infrastructure, explicit control.

### 3. Shared Utilities Organization:

**Option A: Base class with mixin pattern**
- `AnimationBase` class, variants inherit from it
- **Pros:** Clean inheritance, shared methods automatically available
- **Cons:** Multiple inheritance complexity

**Option B: Utility module with helper functions**
- `animation_utils.py` with standalone functions
- **Pros:** No inheritance complexity, easy to test
- **Cons:** Need to import utilities explicitly

**Option C: Composition with shared helper class**
- `AnimationHelpers` class instantiated in each variant
- **Pros:** Clean separation, easy to test
- **Cons:** More boilerplate

**Recommendation:** **Option A** - Base class. Common pattern, reduces duplication, shared methods are clearly inherited.

### 4. Two-Axis Visualization Design:

For ARRL FD and VHF (both band and mode dimensions):

**Option A: Grid/Heatmap Approach**
- X-axis: Time
- Y-axis: Bands (rows)
- Color: Modes (or vice versa)
- **Pros:** Shows all dimensions simultaneously
- **Cons:** Complex, might be hard to read

**Option B: Toggle/Selector Approach**
- User selects: Band filter OR Mode filter
- Chart shows selected dimension with other stacked
- **Pros:** Familiar pattern, less complex
- **Cons:** Requires interaction, doesn't show both simultaneously

**Option C: Multiple Bottom Charts**
- Two bottom charts: One by band, one by mode
- **Pros:** Shows both dimensions clearly
- **Cons:** More screen space, more complex

**Recommendation:** **Defer decision** - Need to see actual ARRL FD data and user needs. Start with simpler approach, enhance if needed.

## Implementation Phases

### Phase 1: One-Axis Variants (Immediate - ARRL-10)
1. Extract shared utilities to `AnimationBase`
2. Create `plot_interactive_animation_one_axis.py`
3. Add auto-detection logic for `one_axis_band` vs `one_axis_mode`
4. Add JSON override capability
5. Update ARRL-10 JSON to specify `"animation_variant": "one_axis_mode"`

### Phase 2: Two-Axis Variant (Defer - ARRL FD, VHF)
1. Design two-axis visualization approach
2. Create `plot_interactive_animation_two_axis.py`
3. Add JSON configuration for two-axis contests
4. Test with ARRL FD data

### Phase 3: Other Charts (As Needed)
- Handle butterfly charts when they cause issues
- Handle other charts on case-by-case basis

## Final Recommendation

**Architecture:** JSON-driven variants with shared utilities
- **Two variants initially:** `one_axis` (band or mode) and `two_axis` (deferred)
- **JSON configuration:** Explicit `animation_variant` with auto-detection fallback
- **Shared utilities:** Base class with common methods
- **Report IDs:** Multiple IDs (`interactive_animation_one_axis`, `interactive_animation_two_axis`)
- **Other charts:** Handle as they arise (butterfly charts deferred)

**Rationale:**
- Explicit configuration scales better than branching logic
- Shared utilities prevent duplication
- Variants are testable and maintainable independently
- Progressive approach: Start with one-axis, add two-axis when needed
- Follows software engineering principles: Configuration over code, explicit over implicit

**Open Questions:**
- Two-axis visualization design (defer until we have data)
- Default auto-detection logic (what's the fallback?)
- Naming conventions (report IDs, JSON fields)

---

## Status: IMPLEMENTED (Final Decision Differs)

**Date Completed:** 2026-01-07  
**Final Decision:** **Generic Report with JSON-Controlled Dimension Selection** (not separate variants)

**See:** `ANIMATION_DIMENSION_IMPLEMENTATION_SUMMARY.md` for complete implementation details.

### Key Changes from Initial Recommendation:

**Initial Recommendation (this document):**
- Multiple report IDs (`interactive_animation_one_axis`, `interactive_animation_two_axis`)
- Separate variant files with shared utilities
- Explicit JSON selection via `animation_variant` field

**Final Implementation:**
- **Single report ID:** `interactive_animation` (generic report)
- **Single file:** `plot_interactive_animation.py` with dimension routing
- **JSON field:** `animation_dimension` (`"band"`, `"mode"`, or future `"two_axis"`)
- **Auto-detection:** Mode-divided contests auto-detect `"band"` dimension

### Rationale for Change:

- **High code similarity** (~70-80% shared between band/mode dimensions)
- **Single report ID** simpler for users and dashboard configuration
- **Generic report** extensible for future (can add `two_axis` routing later)
- **Less file proliferation** - one file instead of multiple variants

### Current Status:

- ✅ Generic report implemented with `_prepare_data_band()` and `_prepare_data_mode()` methods
- ✅ ARRL-10 configured with `animation_dimension: "mode"`
- ✅ Auto-detection working for mode-divided contests
- ⏳ Two-axis variant: Deferred until ARRL FD/VHF integration (as planned)
