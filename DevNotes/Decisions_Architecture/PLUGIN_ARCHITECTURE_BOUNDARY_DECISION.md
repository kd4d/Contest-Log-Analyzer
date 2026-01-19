# Plugin Architecture Boundary Decision

## Date
2026-01-19

## Context

The project follows the architectural principle: **"Contest-specific weirdness is implemented in code (plugins)"**. However, there has been ambiguity about where to draw the boundary between:
- **Core modules** (like `StandardCalculator`) that handle common patterns
- **Contest-specific plugins** (like `wae_calculator`, `naqp_calculator`) that handle unique logic

### The Issue

**ARRL DX Contest Example:**
- Uses `StandardCalculator` (default, no custom calculator specified)
- Has asymmetric multiplier rules with `applies_to` filtering:
  - DXCC rule: `applies_to: "W/VE"`, uses `Mult1` column
  - STPROV rule: `applies_to: "DX"`, also uses `Mult1` column
- `StandardCalculator` was not respecting `applies_to` filtering
- This caused multipliers to be counted twice (2x scores)

**Question:** Should ARRL DX need a custom calculator plugin, or should `StandardCalculator` handle `applies_to` filtering?

## Analysis

### Current State

1. **ScoreStatsAggregator** already handles `applies_to` correctly (lines 156-159 in `score_stats.py`)
2. **TimeSeriesAggregator** already handles `applies_to` correctly (lines 425-429 in `time_series.py`)
3. **StandardCalculator** was missing `applies_to` logic
4. This inconsistency caused different calculation paths to produce different results

### Software Engineering Principles

1. **DRY (Don't Repeat Yourself)**
   - `applies_to` logic exists in other core modules
   - Should not require duplicate implementation in plugins

2. **Separation of Concerns**
   - `applies_to` is **declarative metadata** (defined in JSON), not algorithmic complexity
   - Core modules should respect declarative rules from contest definitions

3. **Principle of Least Astonishment**
   - When a contest uses `StandardCalculator` (default), users expect correct behavior
   - Default calculator should respect all rules defined in the contest definition

4. **Open/Closed Principle**
   - Core modules should be open for extension (handling new declarative patterns)
   - Core modules should be closed for algorithmic complexity (requires plugins)

## Decision

### Refined Architecture Principle

**Original Principle:**
> "Contest-specific weirdness is implemented in code (plugins)"

**Refined Principle:**
> **"Contest-specific algorithmic weirdness is implemented in code (plugins). Common declarative rules defined in contest definitions are handled by core modules."**

### Boundary Definition

#### Core Modules Should Handle:
1. **Declarative Rules from Contest Definitions**
   - `applies_to` filtering (e.g., ARRL DX DXCC/STPROV asymmetry)
   - `totaling_method` variations (`once_per_log`, `sum_by_band`, `once_per_mode`, etc.)
   - Standard score formulas (`points_times_mults`, `qsos_times_mults`, `total_points`)
   - Multiplier column mappings (`value_column`, `name_column`)
   - Zero-point QSO filtering (`mults_from_zero_point_qsos`)

2. **Common Patterns**
   - Standard multiplier counting logic
   - Standard score calculation formulas
   - Standard time-series accumulation

**Rationale:**
- These are metadata-driven rules defined in JSON
- They follow standard patterns that can be handled generically
- Multiple core modules already handle these patterns correctly
- Requiring plugins for metadata differences creates unnecessary complexity

#### Plugins Should Handle:
1. **Algorithmic Complexity**
   - Complex stateful calculations (e.g., WAE credit accumulation)
   - Non-standard formulas that can't be expressed declaratively
   - Special scoring rules (e.g., QTCs, weighted multipliers)
   - Contest-specific time-series logic that differs fundamentally from standard

2. **Unique Logic**
   - Calculations that don't fit standard patterns
   - Multi-step algorithms with contest-specific dependencies
   - Rules that require custom state management

**Rationale:**
- These require custom algorithms, not just configuration
- They fundamentally differ from standard patterns
- They benefit from isolated implementation in plugins
- They represent true "weirdness" that can't be generalized

### Examples

#### Core Module Examples (StandardCalculator should handle)

**ARRL DX** - Asymmetric multipliers:
```json
{
  "multiplier_rules": [
    {"name": "DXCC", "applies_to": "W/VE", "value_column": "Mult1"},
    {"name": "STPROV", "applies_to": "DX", "value_column": "Mult1"}
  ]
}
```
- ✅ Uses `StandardCalculator` (default)
- ✅ `applies_to` filtering is declarative → core module handles it

**CQ WW** - Symmetric multipliers:
```json
{
  "multiplier_rules": [
    {"name": "CQZone", "value_column": "Mult1"},
    {"name": "DXCC", "value_column": "Mult2"}
  ]
}
```
- ✅ Uses `StandardCalculator` (default)
- ✅ No special logic needed → core module handles it

#### Plugin Examples

**WAE** - Custom calculator (`wae_calculator`):
- Complex credit accumulation rules
- Stateful calculation across QSOs
- ✅ Requires custom plugin

**NAQP** - Custom calculator (`naqp_calculator`):
- Special multiplier counting rules
- Contest-specific time-series logic
- ✅ Requires custom plugin

**WRTC** - Custom calculator (`wrtc_calculator`):
- Weighted scoring rules
- Custom score formulas
- ✅ Requires custom plugin

## Implementation Guidelines

### For Core Modules (StandardCalculator, etc.)

1. **Respect all declarative rules** from contest definitions
   - Check `applies_to` and filter by location type
   - Respect `totaling_method` variations
   - Respect `mults_from_zero_point_qsos` setting

2. **Handle common patterns generically**
   - Don't require plugins for metadata-driven differences
   - Use configuration-driven logic where possible

3. **Maintain consistency**
   - Core modules should produce the same results as each other
   - If one core module handles a pattern, others should too

### For Plugin Development

1. **Only create plugins for algorithmic complexity**
   - Don't create plugins just for `applies_to` filtering
   - Don't create plugins for standard `totaling_method` variations

2. **Respect declarative rules**
   - Plugins should still respect `applies_to`, `totaling_method`, etc.
   - Plugins handle the "how" (algorithm), core modules handle the "what" (rules)

3. **Document why a plugin is needed**
   - Explain what algorithmic complexity requires a custom implementation
   - Justify why core modules can't handle it

## Impact

### Benefits

1. **Reduced Plugin Proliferation**
   - Contests like ARRL DX don't need custom calculators
   - Only truly complex contests need plugins

2. **Consistency**
   - All core modules handle declarative rules the same way
   - Fewer places for bugs to hide

3. **Maintainability**
   - Declarative rules are handled in one place (core modules)
   - Plugin logic focuses on true algorithmic complexity

4. **Correctness**
   - Default calculator handles common patterns correctly
   - Fewer opportunities for calculation errors

### Risks and Mitigation

**Risk:** StandardCalculator becomes too complex
- **Mitigation:** Limit to declarative patterns from contest definitions. Keep algorithmic complexity in plugins.

**Risk:** Ambiguity about what belongs in core vs. plugin
- **Mitigation:** Use this decision as a guideline. If it's in the JSON definition and follows standard patterns, it belongs in core. If it requires custom algorithms, it belongs in a plugin.

**Risk:** Breaking existing contests
- **Mitigation:** Adding `applies_to` handling to StandardCalculator is additive. Contests without `applies_to` are unaffected. Contests with `applies_to` get correct behavior.

## Related Decisions

- [ARCHITECTURE_RULE_ENFORCEMENT_DISCUSSION.md](./ARCHITECTURE_RULE_ENFORCEMENT_DISCUSSION.md) - Plugin architecture rules for AI agents
- [SCORING_ARCHITECTURE_ANALYSIS.md](../Discussions/SCORING_ARCHITECTURE_ANALYSIS.md) - Scoring calculation paths analysis

## Status

**Decision Status:** ✅ Accepted and Documented

**Implementation Status:** 
- ✅ `StandardCalculator` should handle `applies_to` filtering (decision documented, implementation pending)
- ✅ Core modules (ScoreStatsAggregator, TimeSeriesAggregator) already handle `applies_to` correctly

## Notes

- This decision refines but does not contradict the original principle
- The boundary is between "declarative metadata" and "algorithmic complexity"
- When in doubt, ask: "Is this algorithmic complexity or just metadata filtering?"
- Core modules should be opinionated about handling declarative rules; plugins should be opinionated about algorithms
