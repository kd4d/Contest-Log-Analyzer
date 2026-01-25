# Callsign Naming Protocol Discussion: "--" Delimiter Consistency

**Date:** 2026-01-20  
**Status:** Discussion  
**Category:** Architecture  
**Last Updated:** 2026-01-20

---

## Executive Summary

This document discusses whether the `--` (double dash) delimiter protocol should be used consistently for both filenames and directory names containing callsigns. Currently, filenames use the `--` delimiter to separate metadata from callsigns, but directory names do not.

---

## Current State Analysis

### The "--" Protocol

**Purpose:** The `--` delimiter separates report metadata from callsigns in names, making it easy to:
- Parse the callsign portion programmatically
- Identify which part is metadata vs. callsigns
- Maintain consistency across the codebase

**Current Usage:**

1. **Filenames (✅ Using `--`):**
   - Format: `{report_id}_{band}_{mode}--{callsigns}.{ext}`
   - Examples:
     - `score_report--k3lr.txt`
     - `score_report_all_cw--k3lr_w3lpl.txt`
     - `interactive_animation--5b-yt7aw_k3lr.html`
     - `json_multiplier_breakdown--k3lr_w3lpl.json`

2. **Directory Names (❌ NOT Using `--`):**
   - Format: `{callsigns}` (just the callsigns part)
   - Examples:
     - `k3lr`
     - `k3lr_w3lpl`
     - `5b-yt7aw_k3lr`
   - Full path: `reports/2024/cq-ww-cw/jan/k3lr_w3lpl/`

3. **ZIP Filenames (✅ Using `--`):**
   - Format: `{year}_{contest}--{callsigns}.zip`
   - Examples:
     - `2024_cq-ww-cw--k3lr.zip`
     - `2024_cq-ww-cw--k3lr_w3lpl.zip`
     - `2024_iaru-hf--5b-yt7aw.zip`

---

## The "--" Protocol Specification

### Format Structure

```
{metadata_part}--{callsigns_part}
```

**Components:**
- **Metadata Part:** Report ID, band, mode, contest info, etc.
- **`--` Delimiter:** Double dash (two hyphens) - chosen to avoid conflicts with single dash used in callsigns (portable designators: `/` → `-`)
- **Callsigns Part:** Filename-safe callsigns joined with `_` (e.g., `k3lr_w3lpl`, `5b-yt7aw`)

### Benefits

1. **Parsing:** Easy to split on `--` to extract callsigns
2. **Identification:** Clear visual separation between metadata and callsigns
3. **Consistency:** Same pattern across filenames and ZIP archives
4. **Portable Designator Handling:** Single `-` in callsigns (from `/`) doesn't conflict with `--` delimiter

### Current Implementation

**Function:** `build_filename()` in `contest_tools/utils/report_utils.py`
```python
def build_filename(report_id: str, logs: list, band_filter: str = None, mode_filter: str = None) -> str:
    """
    Format: {report_id}_{band}_{mode}--{callsigns}
    Uses -- delimiter to separate report metadata from callsigns.
    """
    metadata_part = f"{report_id}_{filename_band}{mode_suffix}"
    callsigns_part = build_callsigns_filename_part(all_calls)
    return f"{metadata_part}--{callsigns_part}"
```

---

## Should Directory Names Use "--" Protocol?

### Option 1: Keep Current Approach (Directory Names Without `--`)

**Current Format:**
```
reports/2024/cq-ww-cw/jan/k3lr_w3lpl/
```

**Rationale:**
- Directory names are already in a structured hierarchy (`year/contest/event/callsigns`)
- The path structure itself provides context (year, contest, event)
- Adding `--` to directory names would be redundant
- Directory names are typically just the callsigns part (no metadata prefix)

**Pros:**
- ✅ Simpler directory names (shorter paths)
- ✅ Path structure already provides context
- ✅ No redundancy (metadata is in parent directories)
- ✅ Easier to navigate in file system

**Cons:**
- ❌ Inconsistent with filename convention
- ❌ Harder to programmatically extract callsigns from directory name alone
- ❌ If directory is moved/copied, context is lost

---

### Option 2: Use "--" Protocol for Directory Names

**Proposed Format:**
```
reports/2024/cq-ww-cw/jan/--k3lr_w3lpl/
```

Or with metadata prefix:
```
reports/2024/cq-ww-cw/jan/2024_cq-ww-cw--k3lr_w3lpl/
```

**Rationale:**
- Consistent with filename convention
- Makes callsigns extraction easier (always split on `--`)
- Self-documenting (directory name contains full context)

**Pros:**
- ✅ Consistent with filename convention
- ✅ Easier to parse callsigns programmatically
- ✅ Self-contained (context preserved if directory moved)
- ✅ Clear visual separation

**Cons:**
- ❌ Redundant (metadata already in path)
- ❌ Longer directory names
- ❌ More complex path structure
- ❌ Breaking change (would require migration)

---

### Option 3: Hybrid Approach (Current + Enhancement)

**Keep directory names as-is, but ensure consistency in parsing:**

- Directory names: `k3lr_w3lpl` (no `--`, no metadata prefix)
- Filenames: `{report_id}--{callsigns}.{ext}` (with `--`)
- ZIP filenames: `{year}_{contest}--{callsigns}.zip` (with `--`)

**Enhancement:** Use utility functions consistently:
- `build_callsigns_filename_part()` for directory names
- `build_filename()` for filenames
- Both use the same callsign formatting rules

**Pros:**
- ✅ No breaking changes
- ✅ Directory names remain simple
- ✅ Filenames maintain `--` protocol
- ✅ Consistent callsign formatting via utilities

**Cons:**
- ⚠️ Still inconsistent (directory vs. filename format)
- ⚠️ Requires careful parsing logic (different formats)

---

## Recommendation: Option 3 (Hybrid with Consistent Utilities)

### Rationale

1. **Directory Context:** Directory names exist within a structured hierarchy that already provides metadata (year, contest, event). Adding `--` and metadata prefix would be redundant.

2. **Filename Context:** Filenames are standalone entities that need to be self-describing. The `--` protocol makes it clear what part is metadata vs. callsigns.

3. **ZIP Filenames:** ZIP files are standalone archives that may be extracted anywhere. Using `--` protocol makes them self-describing.

4. **Consistency Through Utilities:** The key is ensuring all callsign formatting uses the same utility functions:
   - `build_callsigns_filename_part()` for directory names and callsign parts
   - `build_filename()` for complete filenames
   - Both handle portable designators consistently (`/` → `-`)

### Implementation Requirements

1. **Fix LogManager:** Use `build_callsigns_filename_part()` instead of `'_'.join(all_calls)`
2. **Document Protocol:** Clearly document when to use `--` (filenames, ZIP files) vs. when not to (directory names)
3. **Consistent Parsing:** Use `parse_callsigns_from_filename_part()` for extracting callsigns from both formats

---

## Current Inconsistencies to Fix

### Issue 1: LogManager Doesn't Use Utility Function

**Location:** `contest_tools/log_manager.py` line 204-205

**Current Code:**
```python
all_calls = sorted([log.get_metadata().get('MyCall', f'Log{i+1}').lower() for i, log in enumerate(self.logs)])
callsign_combo_id = '_'.join(all_calls)  # ❌ Doesn't handle "/" properly!
```

**Should Be:**
```python
from .utils.callsign_utils import build_callsigns_filename_part

all_calls = sorted([log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(self.logs)])
callsign_combo_id = build_callsigns_filename_part(all_calls)  # ✅ Handles "/" correctly
```

**Impact:** Directory names with portable callsigns (e.g., `5B/YT7AW`) won't be converted to filename-safe format (`5b-yt7aw`).

---

## Protocol Summary

### When to Use `--` Protocol

✅ **Use `--` for:**
- Report filenames: `{report_id}--{callsigns}.{ext}`
- ZIP archive filenames: `{year}_{contest}--{callsigns}.zip`
- Any standalone filename that needs to be self-describing

❌ **Don't use `--` for:**
- Directory names (context provided by path hierarchy)
- Callsign parts alone (just use `build_callsigns_filename_part()`)

### Utility Functions

**For Directory Names:**
```python
from contest_tools.utils.callsign_utils import build_callsigns_filename_part

callsigns_part = build_callsigns_filename_part(all_calls)
# Result: "k3lr_w3lpl" or "5b-yt7aw_k3lr"
```

**For Filenames:**
```python
from contest_tools.utils.report_utils import build_filename

filename = build_filename(report_id, logs, band_filter, mode_filter)
# Result: "score_report_all_cw--k3lr_w3lpl.txt"
```

**For Parsing:**
```python
from contest_tools.utils.callsign_utils import parse_callsigns_from_filename_part

# From directory name or callsign part
callsigns = parse_callsigns_from_filename_part("k3lr_w3lpl")
# Result: ["K3LR", "W3LPL"]

# From filename (extract callsigns part first)
if '--' in filename:
    callsigns_part = filename.rsplit('--', 1)[1].rsplit('.', 1)[0]
    callsigns = parse_callsigns_from_filename_part(callsigns_part)
```

---

## Conclusion

**Recommendation:** Keep the hybrid approach (Option 3) but ensure consistent use of utility functions:

1. **Directory names:** Use `build_callsigns_filename_part()` (no `--`, no metadata prefix)
2. **Filenames:** Use `build_filename()` (with `--` protocol)
3. **ZIP filenames:** Use `--` protocol (already implemented)
4. **Fix LogManager:** Use `build_callsigns_filename_part()` instead of manual join

This approach:
- Maintains simplicity for directory names (no redundancy)
- Ensures consistency through utility functions
- Preserves self-describing nature of filenames
- Handles portable designators correctly everywhere

---

## Related Files

- `contest_tools/utils/callsign_utils.py` - Callsign formatting utilities
- `contest_tools/utils/report_utils.py` - Filename building utilities
- `contest_tools/report_generator.py` - Directory structure creation
- `contest_tools/log_manager.py` - Needs fix to use utility function
- `web_app/analyzer/views.py` - ZIP filename generation (already uses `--`)

---

**Last Updated:** 2026-01-20
