# Animation Variant Configuration Strategy - Discussion

**Date:** 2026-01-07  
**Context:** Need to determine JSON configuration strategy for animation variants. Key insight: `multiplier_report_scope` doesn't indicate multi-mode contests.

## The Problem with Auto-Detection

### `multiplier_report_scope` Doesn't Indicate Multi-Mode:

**Example Cases:**
- **CQ WW**: Multi-band, single mode (CW weekend, SSB weekend - separate contests) → `multiplier_report_scope` might be `per_band`, but it's still single-mode per instance
- **ARRL 10**: Single band, multi-mode (CW and SSB in same contest) → `multiplier_report_scope: "per_mode"` because multipliers are counted separately per mode
- **ARRL FD**: Multi-band, multi-mode → Could have `per_band` multipliers even with multiple modes
- **Other contests**: Multi-mode but multipliers counted once per contest → `multiplier_report_scope` doesn't indicate mode structure

**Key Insight:** `multiplier_report_scope` tells us **how multipliers are counted**, not **what dimensions are meaningful for visualization**.

### Python Principle: "Explicit is better than implicit"

**Zen of Python:** At some point, implicit behavior (auto-detection) becomes ambiguous and error-prone. Explicit configuration is clearer, testable, and maintainable.

## Contest Landscape Analysis

### Single-Mode Contests (Can Auto-Detect):
- **CQ WW** (CW): 6 bands, 1 mode → **Band dimension** (auto-detect: single mode)
- **CQ WW** (SSB): 6 bands, 1 mode → **Band dimension** (auto-detect: single mode)
- **ARRL DX** (CW): 6 bands, 1 mode → **Band dimension** (auto-detect: single mode)
- **ARRL DX** (SSB): 6 bands, 1 mode → **Band dimension** (auto-detect: single mode)

**Auto-Detection Rule:** If contest has only one mode → use `one_axis_band` (default)

### Multi-Mode Contests (Need Explicit Config):
- **ARRL 10**: 1 band, 2 modes → **Mode dimension** (explicit: `one_axis_mode`)
- **ARRL FD**: 8 bands, 3 modes → **Two-axis** (explicit: `two_axis`)
- **VHF Contests**: Multi-band, multi-mode → **Two-axis** (explicit: `two_axis`)

**Key Challenge:** Can't determine visualization dimension from data structure alone - depends on contest scoring/rules.

## Configuration Strategy Options

### Option A: Explicit Always (Most Explicit)

**Approach:**
- **All contests** must specify `animation_variant` in JSON
- **No auto-detection** - explicit configuration required
- **Pros:**
  - Clear and unambiguous
  - Testable (each contest has explicit config)
  - Maintainable (no hidden logic)
  - Follows "Explicit is better than implicit"
- **Cons:**
  - Requires JSON changes for all contests (even single-mode)
  - More configuration burden
  - Feels verbose for simple cases

**JSON:**
```json
{
  "contest_name": "CQ-WW",
  "animation_variant": "one_axis_band",
  ...
}

{
  "contest_name": "ARRL-10",
  "animation_variant": "one_axis_mode",
  ...
}
```

### Option B: Explicit for Multi-Mode Only (Balanced)

**Approach:**
- **Single-mode contests:** Auto-detect → `one_axis_band` (default)
- **Multi-mode contests:** **Must specify** `animation_variant` explicitly
- **Pros:**
  - Minimal JSON changes (only multi-mode contests need config)
  - Explicit where it matters (multi-mode = ambiguous)
  - Backward compatible (single-mode contests unchanged)
  - Follows principle: "Explicit is better than implicit" for ambiguous cases
- **Cons:**
  - Need to detect "single-mode vs multi-mode" - how?
  - Still has some implicit behavior for single-mode

**JSON:**
```json
{
  "contest_name": "CQ-WW",
  // No animation_variant - auto-detects to "one_axis_band" (single mode)
  ...
}

{
  "contest_name": "ARRL-10",
  "animation_variant": "one_axis_mode",  // Required for multi-mode
  ...
}
```

**Detection:** How do we detect "single-mode"?
- Option B1: Count distinct modes in valid_modes (if exists in JSON)
- Option B2: Check if contest has mode filter in name (e.g., "CQ-WW-CW")
- Option B3: Require explicit `valid_modes` or `modes` field in JSON

### Option C: Explicit for Multi-Mode or Single-Band Multi-Mode (Specific)

**Approach:**
- **Single-mode contests:** Auto-detect → `one_axis_band`
- **Multi-band, multi-mode:** Auto-detect → `two_axis` (may need override)
- **Single-band, multi-mode:** **Must specify** (ambiguous: band or mode?)
- **Pros:**
  - Handles ambiguous case (single-band + multi-mode) explicitly
  - Less config burden for common cases
- **Cons:**
  - Still has implicit behavior
  - Multi-band, multi-mode might need explicit config too (ARRL FD vs others)

**JSON:**
```json
{
  "contest_name": "ARRL-10",
  "animation_variant": "one_axis_mode",  // Required: single-band + multi-mode
  ...
}

{
  "contest_name": "ARRL-FD",
  "animation_variant": "two_axis",  // Optional but recommended: multi-band + multi-mode
  ...
}
```

### Option D: Progressive Explicit (Evolutionary)

**Approach:**
- **Phase 1:** Auto-detect for single-mode contests, explicit for multi-mode
- **Phase 2:** As we encounter edge cases, add explicit config
- **Phase 3:** Eventually require explicit config for all contests
- **Pros:**
  - Gradual migration path
  - Doesn't break existing contests immediately
  - Can validate auto-detection logic before requiring explicit
- **Cons:**
  - Inconsistent approach during transition
  - Need migration plan

## Recommended Approach: Option B (Explicit for Multi-Mode)

### Rationale:

1. **"Explicit is better than implicit"** - But explicit is most important where ambiguity exists (multi-mode contests)

2. **Single-mode contests are unambiguous:**
   - If contest has only one mode → band dimension is always the meaningful axis
   - Auto-detection is safe and correct
   - No ambiguity to resolve

3. **Multi-mode contests are ambiguous:**
   - Single-band + multi-mode: Could be mode dimension (ARRL-10) or band dimension (unlikely but possible)
   - Multi-band + multi-mode: Could be band dimension, mode dimension, or two-axis
   - **Requires explicit configuration** to resolve ambiguity

4. **Minimal JSON changes:**
   - Existing single-mode contests need no changes (backward compatible)
   - Only multi-mode contests need configuration
   - Reduces migration burden

### Implementation:

**Auto-Detection Logic:**
```python
def determine_animation_variant(contest_def):
    # Explicit config always wins
    if hasattr(contest_def, 'animation_variant') and contest_def.animation_variant:
        return contest_def.animation_variant
    
    # Auto-detect: Check if contest is single-mode
    valid_modes = contest_def.valid_modes if hasattr(contest_def, 'valid_modes') else None
    
    if valid_modes and len(valid_modes) == 1:
        # Single mode contest → band dimension
        return "one_axis_band"
    
    # Multi-mode contest without explicit config → error or warning?
    # OR default to "one_axis_band" and log warning?
    return "one_axis_band"  # Default with warning
```

**JSON Schema:**
```json
{
  "contest_name": "ARRL-10",
  "valid_modes": ["CW", "SSB"],  // Indicates multi-mode
  "animation_variant": "one_axis_mode",  // Required for multi-mode
  ...
}

{
  "contest_name": "CQ-WW",
  // No valid_modes (or single mode) → auto-detects "one_axis_band"
  ...
}
```

### Future Migration Path:

**Phase 1 (Current):**
- Auto-detect single-mode → `one_axis_band`
- Require explicit for multi-mode
- Log warnings if multi-mode without explicit config

**Phase 2 (After validation):**
- Require explicit config for all contests
- Remove auto-detection
- All JSON files updated

**Phase 3 (Mature system):**
- JSON schema validation requires `animation_variant`
- Build-time validation catches missing config

## Open Questions

### 1. How to Detect "Single-Mode"?

**Option 1: `valid_modes` field in JSON**
```json
{
  "valid_modes": ["CW"]  // Single mode
}
```
- **Pros:** Explicit, clear
- **Cons:** New field required (but only for multi-mode)

**Option 2: Contest name pattern**
- Check if contest name ends with "-CW" or "-SSB"
- **Pros:** No new field needed
- **Cons:** Brittle, doesn't work for all naming conventions

**Option 3: Data-driven detection**
- Count distinct modes in actual log data
- **Pros:** Based on reality
- **Cons:** Requires parsing logs first, can't know before analysis

**Recommendation:** **Option 1** - `valid_modes` field. Clear, explicit, matches existing pattern (we already have `valid_bands`).

### 2. Default Behavior for Multi-Mode Without Config?

**Option A: Error/Fail Fast**
- Raise error if multi-mode contest lacks `animation_variant`
- **Pros:** Forces explicit configuration
- **Cons:** Breaks existing contests (need to update JSON)

**Option B: Warning + Default**
- Log warning, default to `one_axis_band`
- **Pros:** Backward compatible, graceful degradation
- **Cons:** Wrong visualization might be used

**Option C: Try to Auto-Detect Multi-Mode**
- Single-band + multi-mode → `one_axis_mode` (heuristic)
- Multi-band + multi-mode → `two_axis` (heuristic)
- **Pros:** Handles common cases automatically
- **Cons:** Still has ambiguity, might get it wrong

**Recommendation:** **Option A (with migration period) or Option B (with strong warning)** - Prefer explicit config, but allow graceful fallback during transition.

### 3. Should We Add `valid_modes` to All JSON Files?

**Current State:** JSON files don't have `valid_modes` field (or only some do)

**Options:**
- **Add to all JSON files** - Explicit, clear, matches `valid_bands` pattern
- **Only add to multi-mode contests** - Minimal changes
- **Optional field** - Auto-detect if missing

**Recommendation:** **Add to all JSON files** - Consistent pattern, explicit, helps with auto-detection logic.

## Final Recommendation

**Configuration Strategy:**
1. **Auto-detect single-mode contests** → `one_axis_band` (default)
2. **Require explicit `animation_variant` for multi-mode contests**
3. **Add `valid_modes` field to all JSON files** (consistent with `valid_bands`)
4. **Log warnings** if multi-mode contest lacks explicit config (during migration)
5. **Future:** Require explicit config for all contests (after validation period)

**Rationale:**
- Follows "Explicit is better than implicit" where it matters (multi-mode = ambiguous)
- Minimal JSON changes (only multi-mode contests need config)
- Backward compatible (single-mode contests unchanged)
- Provides migration path to fully explicit configuration

**Implementation Priority:**
1. Add `valid_modes` to JSON files (all contests)
2. Add `animation_variant` to multi-mode contests (ARRL-10, ARRL-FD, VHF)
3. Implement auto-detection logic
4. Add validation/warnings for multi-mode without config
5. Future: Require explicit config for all contests
