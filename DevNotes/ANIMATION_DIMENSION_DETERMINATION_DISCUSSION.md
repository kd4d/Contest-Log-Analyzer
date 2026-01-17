# Animation Dimension Determination - Discussion

**Date:** 2026-01-07  
**Context:** Need to clarify what "determine_dimension" should do. User insight: Contest sets parameters, individual logs may not use all available dimensions.

## The Key Insight

**Contest Definition (JSON) ≠ Individual Log Data**

### Contest Definition (JSON):
- Defines **what dimensions are available/supported** by contest rules
- Example: `valid_bands: ["160M", "80M", "40M", "20M", "15M", "10M"]`
- Example: Contest might allow CW and SSB (multi-mode contest)
- **This is what the contest rules allow**

### Individual Log Data:
- **What dimensions are actually used** in a specific log file
- Example: A CQ WW log might only have QSOs on 20M, 15M, and 10M (not all 6 bands)
- Example: An ARRL 10 log might only have CW QSOs (no SSB)
- **This is what the operator actually did**

## The Question: What Should "Determine Dimension" Do?

### Current Understanding (Incorrect):

I was thinking:
```python
def _determine_dimension(self, contest_def, logs):
    """Looks at actual log data to determine dimension"""
    bands_in_data = set()
    modes_in_data = set()
    for log in logs:
        df = get_valid_dataframe(log)
        bands_in_data.update(df['Band'].unique())
        modes_in_data.update(df['Mode'].unique())
    
    # If only one band but multiple modes → use mode dimension
    # If multiple bands → use band dimension
```

**Problem:** This determines dimension based on **what's in the logs**, not **what the contest supports**.

### Correct Understanding:

The dimension should be determined by:
1. **Contest definition (JSON)** - What dimensions are meaningful for this contest
2. **Contest visualization strategy** - Which dimension is the primary comparison axis

**NOT by:**
- What bands/modes are actually in the log data
- What the operator actually used

## Examples:

### CQ WW (Mode-Divided JSON):
- **Contest Definition:** 6 bands available, 1 mode per instance (CW or SSB separately)
- **Log Data:** Operator might only use 3 bands (20M, 15M, 10M)
- **Visualization Dimension:** **Band** (because contest is about band selection)
- **Chart Shows:** Those 3 bands (even if others are empty)

### ARRL 10 (Mode-Combined JSON):
- **Contest Definition:** 1 band (10M), 2 modes available (CW, SSB)
- **Log Data:** Operator might only have CW QSOs (no SSB)
- **Visualization Dimension:** **Mode** (because contest is about mode-based multipliers)
- **Chart Shows:** CW mode (SSB might be empty)

### ARRL FD (Multi-Mode, Multi-Band):
- **Contest Definition:** 8 bands available, 3 modes available (CW, SSB, PH)
- **Log Data:** Operator might use 5 bands and 2 modes
- **Visualization Dimension:** **Two-axis** (both band and mode matter)
- **Chart Shows:** Those 5 bands × 2 modes (even if other combinations are empty)

## What Should `_determine_dimension()` Actually Do?

### Option A: Read Contest Definition Only

```python
def _determine_dimension(self, contest_def):
    """Reads contest JSON to determine visualization dimension"""
    # Explicit JSON config wins
    if hasattr(contest_def, 'animation_dimension'):
        return contest_def.animation_dimension
    
    # Auto-detect from contest structure
    # Mode-divided JSON → 'band' dimension
    # Mode-combined JSON with multiple modes → 'mode' dimension (or require explicit)
    
    # Don't look at log data - use contest definition
    return 'band'  # Default
```

**Pros:**
- Based on contest rules, not log data
- Consistent for all logs of same contest
- Makes sense conceptually (contest determines visualization strategy)

**Cons:**
- Doesn't adapt to what's actually in the logs

### Option B: Read Contest Definition + Validate Against Log Data

```python
def _determine_dimension(self, contest_def, logs):
    """Reads contest JSON, validates against log data"""
    # Explicit JSON config wins
    if hasattr(contest_def, 'animation_dimension'):
        dimension = contest_def.animation_dimension
        # Validate dimension makes sense for this contest
        self._validate_dimension(dimension, contest_def)
        return dimension
    
    # Auto-detect from contest structure
    # Don't use log data to determine dimension, only to validate
    ...
```

**Pros:**
- Based on contest rules (primary)
- Can validate that dimension is appropriate for the data

**Cons:**
- More complex
- What if dimension doesn't match data? (Still use it, just show empty dimensions?)

### Option C: Read Contest Definition, Use Log Data for Display

```python
def _determine_dimension(self, contest_def):
    """Reads contest JSON only - dimension is contest-level decision"""
    # Explicit JSON config
    if hasattr(contest_def, 'animation_dimension'):
        return contest_def.animation_dimension
    
    # Auto-detect from contest structure (not log data)
    return 'band'  # Default

def _prepare_data(self, dimension, **kwargs):
    """Prepares data - uses dimension from contest, filters by actual log data"""
    if dimension == 'band':
        # Use band dimension, but only show bands that have data
        bands = self._get_bands_with_data()  # From actual logs
        ...
```

**Pros:**
- Dimension determined by contest (what's meaningful)
- Display filtered by actual data (what's relevant)
- Best of both worlds

**Cons:**
- Need to handle empty dimensions gracefully

## The Real Question:

**Should dimension determination:**
1. **Only read contest JSON** (contest determines visualization strategy)
2. **Read contest JSON + check log data** (validate dimension makes sense)
3. **Read contest JSON + use log data for display** (dimension from contest, filtering from logs)

## My Interpretation:

**`_determine_dimension()` should:**
- **Read contest definition JSON only** (what dimensions are supported/meaningful)
- **Return the dimension that's meaningful for this contest's visualization**
- **NOT depend on what's actually in the log data**

**`_prepare_data()` should:**
- **Use the dimension from contest definition**
- **Filter/display only dimensions that have actual data** (empty bands/modes are fine, just show empty)

**Example:**
```python
# ARRL-10: Contest defines mode dimension (1 band, 2 modes available)
# Log might only have CW QSOs (SSB empty)
# Chart shows mode dimension with CW (SSB section is empty/zero)

# CQ WW: Contest defines band dimension (6 bands, 1 mode)
# Log might only use 3 bands
# Chart shows band dimension with those 3 bands (others are empty/zero)
```

## Questions for Discussion:

1. **Should `_determine_dimension()` read contest JSON only?** (Not log data)
   - Contest determines visualization strategy
   - Log data determines what's displayed within that strategy

2. **What if a dimension is specified but has no data?** (e.g., ARRL-10 with mode dimension, but log only has CW)
   - Show empty/zero for missing modes?
   - Hide empty dimensions?
   - Default to showing all possible dimensions (from contest) even if empty?

3. **Should we validate dimension against contest definition?**
   - Can't use 'mode' dimension if contest only has 1 mode?
   - Or can we, just it would be meaningless?

4. **What's the "obvious case" for autodetection?**
   - Mode-divided JSON files (`cq_ww_cw.json`) → auto-detect 'band'?
   - Or should even that be explicit in JSON?
