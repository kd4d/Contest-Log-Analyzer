# Explicit JSON Configuration - Analysis and Discussion

**Date:** 2026-01-07  
**Context:** Need to determine what should be explicit in JSON vs defaults. User emphasis: "Explicit is better than implicit" but don't be dogmatic.

## Current JSON State Analysis

### Bands: Mostly Explicit, Some Use Default

**Findings:**
- **Explicit `valid_bands`:**
  - `cq_160.json`: `["160M"]` ✅
  - `arrl_10.json`: `["10M"]` ✅
  - `arrl_fd.json`: `["160M", "80M", ..., "SAT"]` ✅
  - `naqp.json`: `["160M", "80M", ..., "10M"]` ✅
  - `wae_cw.json`: Has `valid_bands` ✅
  - `wae_ssb.json`: Has `valid_bands` ✅
  - `cq_ww_rtty.json`: Has `valid_bands` ✅
  - `wrtc.json`: Has `valid_bands` ✅

- **Missing `valid_bands` (Use Default):**
  - `cq_ww_cw.json`: ❌ (uses default: `['160M', '80M', '40M', '20M', '15M', '10M']`)
  - `cq_ww_ssb.json`: (likely same)
  - `arrl_dx_cw.json`: ❌ (uses default)
  - `arrl_dx_ssb.json`: (likely same)
  - `cq_wpx_cw.json`: (likely same)
  - `cq_wpx_ssb.json`: (likely same)

**Default Fallback (from `__init__.py`):**
```python
def valid_bands(self) -> List[str]:
    return self._data.get('valid_bands', [
        '160M', '80M', '40M', '20M', '15M', '10M'
    ])
```

**Assessment:** Default exists for standard 6 bands (160M-10M). Most contests explicitly define bands. CQ WW and ARRL DX use default (but they are standard 6-band contests).

### Modes: Implicit (Filename/Contest Name Pattern)

**Findings:**
- **No `valid_modes` field in any JSON files** ❌
- **Modes are indicated by:**

1. **Filename pattern:**
   - `cq_ww_cw.json` → CW mode
   - `cq_ww_ssb.json` → SSB mode
   - `cq_ww_rtty.json` → RTTY mode

2. **Contest name pattern:**
   - `"contest_name": "CQ-WW-CW"` → CW mode
   - `"contest_name": "ARRL-DX-CW"` → CW mode

3. **Exchange parsing rules keys:**
   - `naqp.json`: Has `"NAQP-CW"`, `"NAQP-PH"`, `"NAQP-RTTY"` keys → Multi-mode contest
   - `cq_160.json`: Has `"CQ-160-CW"` and `"CQ-160-SSB"` keys → Multi-mode contest
   - `arrl_10.json`: Single parsing rule `"ARRL-10-DX-LOGGER"` → Mode info in contest structure (Mode column in data)

**Assessment:** Modes are **implicit** - determined by filename, contest name, or parsing rule keys. No explicit `valid_modes` field.

## The `animation_dimension` Question

### User's Position:
- **Explicit JSON field preferred** over autodetection (except obvious cases)
- **"Explicit is better than implicit"** - but don't be dogmatic
- JSON should SELECT/control differences implemented in code

### Options for `animation_dimension`:

#### Option A: Always Explicit (Most Explicit)

```json
{
  "contest_name": "CQ-WW-CW",
  "valid_bands": ["160M", "80M", "40M", "20M", "15M", "10M"],  // Make explicit
  "animation_dimension": "band",  // Explicit
  ...
}

{
  "contest_name": "ARRL-10",
  "valid_bands": ["10M"],
  "animation_dimension": "mode",  // Explicit
  ...
}
```

**Pros:**
- Completely explicit, no ambiguity
- All configuration visible in JSON
- Testable (each contest has explicit config)
- Follows "explicit is better than implicit" completely

**Cons:**
- Requires updating all JSON files (even standard 6-band contests)
- More verbose for simple cases
- Some might argue it's overkill for obvious cases

#### Option B: Explicit Where Needed (Balanced)

```json
{
  "contest_name": "CQ-WW-CW",
  // No animation_dimension - auto-detects "band" (obvious: mode-divided JSON = single mode = band dimension)
  ...
}

{
  "contest_name": "ARRL-10",
  "animation_dimension": "mode",  // Explicit (multi-mode JSON, not obvious)
  ...
}
```

**Pros:**
- Minimal JSON changes (only multi-mode contests need config)
- Explicit where it matters (multi-mode = ambiguous)
- Backward compatible (single-mode contests unchanged)
- Follows principle: "Explicit is better than implicit" where it matters

**Cons:**
- Still has implicit behavior for single-mode
- Need to define "obvious case" (mode-divided JSON)

#### Option C: Progressive Explicit (Evolutionary)

- **Phase 1:** Only multi-mode contests need `animation_dimension`
- **Phase 2:** Gradually add to all contests
- **Phase 3:** Require explicit for all contests

**Pros:**
- Gradual migration path
- Doesn't break existing contests immediately

**Cons:**
- Inconsistent during transition
- Need migration plan

## Recommendation: Option B (Explicit Where Needed) + Make Bands Explicit

### Rationale:

1. **"Explicit is better than implicit" but don't be dogmatic:**
   - **Obvious case:** Mode-divided JSON (like `cq_ww_cw.json`) → clearly single-mode → band dimension is obvious
   - **Not obvious:** Mode-combined JSON (like `arrl_10.json`) → multi-mode → dimension is ambiguous → **requires explicit**

2. **Make `valid_bands` explicit everywhere:**
   - Even standard 6-band contests should specify
   - Removes dependency on default fallback
   - Makes configuration complete and self-documenting
   - Easy to do (just add the field)

3. **`animation_dimension` explicit for multi-mode contests only:**
   - Mode-divided JSON → auto-detect "band" (obvious from filename/contest name)
   - Mode-combined JSON → **require explicit** (ambiguous)

### Implementation Plan:

#### Phase 1: Add `valid_bands` to All Contests (Make Bands Explicit)

**Files needing updates:**
- `cq_ww_cw.json`: Add `"valid_bands": ["160M", "80M", "40M", "20M", "15M", "10M"]`
- `cq_ww_ssb.json`: Same
- `cq_ww_rtty.json`: (check if has it)
- `arrl_dx_cw.json`: Add `"valid_bands": ["160M", "80M", "40M", "20M", "15M", "10M"]`
- `arrl_dx_ssb.json`: Same
- `cq_wpx_cw.json`: (check)
- `cq_wpx_ssb.json`: (check)

**Rationale:**
- Makes all configuration explicit
- Removes dependency on default
- Self-documenting JSON files

#### Phase 2: Add `animation_dimension` to Multi-Mode Contests

**Files needing updates:**
- `arrl_10.json`: Add `"animation_dimension": "mode"`
- `arrl_fd.json`: Add `"animation_dimension": "two_axis"` (when we implement it)

**Rationale:**
- Only contests where dimension is ambiguous need explicit config
- Mode-divided contests auto-detect "band" (obvious from filename)

### Detection Logic:

```python
def _determine_dimension(self, contest_def):
    """Determines visualization dimension from contest definition"""
    # Explicit JSON config wins
    if hasattr(contest_def, 'animation_dimension') and contest_def.animation_dimension:
        return contest_def.animation_dimension
    
    # Auto-detect: Mode-divided JSON → "band" dimension
    # How to detect "mode-divided"?
    # - Check if contest_name ends with "-CW", "-SSB", "-RTTY", "-PH"?
    # - Or check if there are multiple exchange_parsing_rules keys with mode suffixes?
    
    # For now: Default to "band" for mode-divided contests
    # Mode-combined contests MUST specify explicit config (should error/warn if missing)
    return "band"  # Default with warning if multi-mode without explicit
```

## Questions for Discussion:

### 1. Should We Add `valid_bands` to All Contests?

**My recommendation: YES**
- Makes configuration explicit
- Removes dependency on default
- Self-documenting
- Easy to do (just copy-paste the array)

### 2. How to Detect "Mode-Divided" vs "Mode-Combined"?

**Option A: Contest Name Pattern**
```python
if contest_def.contest_name.endswith(('-CW', '-SSB', '-RTTY', '-PH')):
    # Mode-divided JSON → auto-detect "band"
```

**Option B: Check Exchange Parsing Rules Keys**
```python
parsing_rules = contest_def._data.get('exchange_parsing_rules', {})
if any(key.endswith(('-CW', '-SSB', '-RTTY', '-PH')) for key in parsing_rules.keys()):
    # Multi-mode contest → need explicit config
else:
    # Single-mode contest → auto-detect "band"
```

**Option C: Explicit `valid_modes` Field**
```json
{
  "valid_modes": ["CW"]  // Single mode
}
```
- **Pros:** Explicit, clear
- **Cons:** New field, all JSON files need update

**Recommendation:** **Option B** - Check exchange parsing rules keys. More robust than filename pattern.

### 3. What Should Happen if Multi-Mode Contest Lacks `animation_dimension`?

**Option A: Error/Fail Fast**
- Raise error if multi-mode contest lacks `animation_dimension`
- **Pros:** Forces explicit configuration
- **Cons:** Breaks existing contests (need to update JSON)

**Option B: Warning + Default**
- Log warning, default to `"band"`
- **Pros:** Backward compatible, graceful degradation
- **Cons:** Wrong visualization might be used

**Option C: Heuristic with Warning**
- Try to detect: Single-band + multi-mode → `"mode"` (heuristic)
- Multi-band + multi-mode → `"two_axis"` (heuristic)
- Log warning about using heuristic
- **Pros:** Handles common cases automatically
- **Cons:** Might get it wrong, still implicit

**Recommendation:** **Option B** (Warning + Default) during migration, then **Option A** (Error) once all JSON files updated.

## Final Recommendation:

1. **Make `valid_bands` explicit in all JSON files** (remove default dependency)
2. **Add `animation_dimension` to multi-mode contests only** (`arrl_10.json`: `"mode"`)
3. **Auto-detect "band" for mode-divided contests** (check parsing rules or contest name pattern)
4. **Log warnings** if multi-mode contest lacks explicit `animation_dimension`
5. **Future:** Require explicit `animation_dimension` for all contests (after validation)

**Rationale:**
- Follows "explicit is better than implicit" where it matters (multi-mode = ambiguous)
- Makes bands explicit everywhere (removes defaults)
- Backward compatible (mode-divided contests unchanged)
- Provides migration path to fully explicit configuration
