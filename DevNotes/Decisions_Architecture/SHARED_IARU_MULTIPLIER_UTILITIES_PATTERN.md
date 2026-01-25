# Shared IARU Multiplier Utilities Pattern

**Date:** 2026-01-20  
**Status:** Active  
**Last Updated:** 2026-01-20  
**Category:** Pattern

---

## Overview

This document describes the pattern for sharing IARU HQ Station and IARU Official multiplier parsing logic between contests that use these multiplier types.

**Problem:**
- IARU-HF and WRTC contests both use IARU HQ Stations and IARU Officials multipliers
- Both contests parse the same exchange format to identify these multipliers
- Code duplication existed between `iaru_hf_multiplier_resolver.py` and `wrtc_multiplier_resolver.py`

**Solution:**
- Create shared utility module: `contest_tools/core_annotations/_iaru_mult_utils.py`
- Extract common HQ/Official parsing logic
- Both contests import and use shared utilities
- Contest-specific logic (Zones for IARU, DXCC for WRTC) remains in contest-specific resolvers

---

## Pattern Structure

### Shared Utilities Module

**Location:** `contest_tools/core_annotations/_iaru_mult_utils.py`

**Purpose:**
- Load IARU officials.dat file (AC, R1, R2, R3)
- Parse exchange to identify HQ Station or IARU Official
- Provide reusable functions for any contest using IARU multipliers

**Functions:**
```python
def load_officials_set(root_input_dir: str) -> Set[str]:
    """Loads iaru_officials.dat file into a set."""

def resolve_iaru_hq_official(exchange: str, officials_set: Set[str]) -> Dict[str, Optional[str]]:
    """Parses exchange to identify HQ Station or IARU Official."""
```

### Contest-Specific Usage

**IARU-HF:**
- Uses shared utilities for HQ/Official
- Adds Zone parsing (IARU-HF specific)
- Resolver: `iaru_hf_multiplier_resolver.py`

**WRTC:**
- Uses shared utilities for HQ/Official
- Adds DXCC logic (WRTC specific)
- Resolver: `wrtc_multiplier_resolver.py`

---

## Implementation Pattern

### Step 1: Create Shared Module

Create `_iaru_mult_utils.py` with:
- `load_officials_set()` - Loads data file
- `resolve_iaru_hq_official()` - Parses exchange

### Step 2: Update Contest Resolvers

**IARU-HF Resolver:**
```python
from ..core_annotations._iaru_mult_utils import load_officials_set, resolve_iaru_hq_official

def resolve_multipliers(...):
    officials_set = load_officials_set(root_input_dir)
    
    for row in df:
        exchange = row.get('RcvdMult')
        
        # Zone parsing (IARU-HF specific)
        if exchange.isnumeric():
            mult_zone = exchange
        
        # HQ/Official (shared)
        hq_official = resolve_iaru_hq_official(exchange, officials_set)
        mult_hq = hq_official['hq']
        mult_official = hq_official['official']
```

**WRTC Resolver:**
```python
from ..core_annotations._iaru_mult_utils import load_officials_set, resolve_iaru_hq_official

def resolve_multipliers(...):
    officials_set = load_officials_set(root_input_dir)
    
    for row in df:
        exchange = row.get('RcvdMult')
        
        # HQ/Official (shared)
        hq_official = resolve_iaru_hq_official(exchange, officials_set)
        mult_hq = hq_official['hq']
        mult_official = hq_official['official']
        
        # DXCC logic (WRTC specific)
        mult_dxcc = row.get('DXCCPfx')
```

---

## When to Use This Pattern

**Use shared utilities when:**
- Multiple contests use the same multiplier parsing logic
- The logic is complex enough to warrant extraction
- The shared logic is stable (unlikely to change per contest)

**Keep contest-specific when:**
- Logic differs significantly between contests
- Logic is simple (one-liner)
- Logic is tightly coupled to contest-specific rules

---

## Benefits

1. **Code Reuse:** Single source of truth for HQ/Official parsing
2. **Maintainability:** Bug fixes in one place benefit all contests
3. **Consistency:** All contests parse IARU multipliers the same way
4. **Testability:** Shared utilities can be tested independently

---

## Related Patterns

- **Plugin Architecture:** Contest-specific resolvers remain as plugins
- **Composition over Inheritance:** Shared utilities via function calls, not inheritance
- **Separation of Concerns:** Common logic in shared module, contest-specific logic in resolvers

---

## Examples

### IARU-HF Multiplier Resolver
- Uses: Shared utilities (HQ/Official) + Contest-specific (Zones)
- Location: `contest_tools/contest_specific_annotations/iaru_hf_multiplier_resolver.py`

### WRTC Multiplier Resolver
- Uses: Shared utilities (HQ/Official) + Contest-specific (DXCC)
- Location: `contest_tools/contest_specific_annotations/wrtc_multiplier_resolver.py`

---

## Future Considerations

If other contests need IARU multipliers:
- Import from `_iaru_mult_utils`
- Add contest-specific multiplier logic
- Follow same pattern

---

**Last Updated:** 2026-01-20
