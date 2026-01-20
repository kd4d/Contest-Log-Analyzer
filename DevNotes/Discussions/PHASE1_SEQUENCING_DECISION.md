# Phase 1 Sequencing Decision: Before or After ARRL 10 Meter?

## Context

- **Current State**: CQ-WW has a working dashboard (`dashboard.html`)
- **Next Contest**: ARRL 10 Meter (single-band, different multipliers, mode-based)
- **Question**: Do Phase 1 (Template Composition) first, or start ARRL 10 and refactor after?

---

## ARRL 10 Meter Characteristics

From `arrl_10.json` and related files:

### Similarities to CQ-WW:
- ✅ Same scoreboard structure (callsign, QSOs, multipliers, score)
- ✅ Same navigation needs (QSO dashboard, Multiplier dashboard links)
- ✅ Same header/footer structure (title, back button, download link)
- ✅ Same strategic breakdown concept (hourly animation, QSO reports, mult reports)

### Key Differences from CQ-WW:
- ⚠️ **Single band** (10M only) vs CQ-WW's multi-band
  - Band breakdowns/spectrum visualizations less relevant
  - May not need "QSOs by Band" section
  
- ⚠️ **Different multiplier structure**:
  - ARRL 10: States, Provinces, Mexican States, DXCC, ITU Regions (mutually exclusive, mode-based)
  - CQ-WW: Countries, Zones (per-band)
  - Scoreboard columns will be different
  
- ⚠️ **Mode-based multipliers** vs CQ-WW's band-based
  - Multiplier dashboard may need mode breakdowns instead of band breakdowns
  - Reporting structure likely different

- ⚠️ **Scoring differences**:
  - ARRL 10: 4 pts CW, 2 pts Phone
  - CQ-WW: 3/2/1 by band/zone
  - (Likely affects reports more than dashboard)

---

## Analysis: Phase 1 Before vs After ARRL 10

### Option A: Do Phase 1 First (Recommended)

**Approach**: Extract only the **obviously common** elements from CQ-WW, then implement ARRL 10.

**What to Extract (Focused Phase 1):**
1. ✅ **Dashboard header** (`partials/dashboard_header.html`)
   - Title, contest name, back button
   - Clearly reusable, no contest-specific logic
   
2. ✅ **Scoreboard table structure** (`partials/scoreboard_table.html`)
   - Table shell (callsign, QSOs, Run QSOs, Run %, multipliers, Score)
   - Columns are dynamic (`mult_headers`), so structure is reusable
   
3. ✅ **Dashboard navigation** (`partials/dashboard_navigation.html`)
   - Links to QSO dashboard, Multiplier dashboard
   - Same for all contests (so far)
   
4. ✅ **Dashboard footer** (`partials/dashboard_footer.html`)
   - "Download All Reports" section
   - Same for all contests

**What NOT to Extract Yet:**
- ❌ Strategic Breakdown section (may vary by contest)
- ❌ QSO/Multiplier dashboard internals (too complex, need ARRL 10 patterns first)

**Benefits:**
- ✅ Immediate cleanup of CQ-WW template
- ✅ ARRL 10 implementation can reuse header/scoreboard/nav/footer
- ✅ Reduces duplication between CQ-WW and ARRL 10
- ✅ Low risk - only extracting obviously common parts
- ✅ Doesn't lock us into a structure that might not fit ARRL 10

**Risks:**
- ⚠️ Might extract something that ARRL 10 doesn't need
- ⚠️ But header/scoreboard/nav/footer are so generic they'll be used anyway

---

### Option B: Do ARRL 10 First, Then Phase 1

**Approach**: Build ARRL 10 dashboard from scratch (or copy CQ-WW), then extract commonalities.

**Benefits:**
- ✅ See actual ARRL 10 requirements before refactoring
- ✅ No risk of extracting wrong things

**Risks:**
- ❌ **Duplication**: Will copy ~146 lines of `dashboard.html` → `arrl_10_dashboard.html`
- ❌ **Technical Debt**: Now have 2 large templates to maintain
- ❌ **Harder Refactor**: After ARRL 10 exists, refactoring touches 2 files instead of 1
- ❌ **Slower**: Build ARRL 10, then refactor both dashboards

---

## Recommendation: **Focused Phase 1 Before ARRL 10**

### Strategy: "Extract the Obvious, Defer the Uncertain"

**Step 1: Extract Common Shell (This Week)**
- Create `partials/dashboard_header.html`
- Create `partials/scoreboard_table.html`  
- Create `partials/dashboard_navigation.html`
- Create `partials/dashboard_footer.html`
- Refactor `dashboard.html` to use these partials
- **Test with CQ-WW** - ensure nothing breaks

**Step 2: Build ARRL 10 Dashboard (Next)**
- Use the same partials for header/scoreboard/nav/footer
- Build ARRL 10-specific sections (may need different strategic breakdown)
- Discover what else should be extracted

**Step 3: Complete Phase 1 (After ARRL 10)**
- Based on ARRL 10 experience, extract any additional common patterns
- Refactor `qso_dashboard.html` and `multiplier_dashboard.html` to use shared partials
- Identify what's contest-specific vs generic

---

## What This Gets Us

### Immediate (Before ARRL 10):
- ✅ Cleaner `dashboard.html` (from 146 lines → ~40 lines + partials)
- ✅ Reusable header/scoreboard/nav/footer for ARRL 10
- ✅ Easier to maintain common elements (change once, affects all)

### After ARRL 10:
- ✅ Two dashboards sharing common structure
- ✅ Clear understanding of what's reusable vs contest-specific
- ✅ Foundation for Phase 2 (configuration-driven template selection)

---

## Implementation Plan

### Phase 1A: Focused Extraction (1-2 days)

1. **Create partials directory structure**:
   ```
   templates/analyzer/partials/
     - dashboard_header.html
     - scoreboard_table.html
     - dashboard_navigation.html
     - dashboard_footer.html
   ```

2. **Extract from `dashboard.html`**:
   - Lines 25-31 → `dashboard_header.html`
   - Lines 35-76 → `scoreboard_table.html`
   - Lines 78-132 → `dashboard_navigation.html` (strategic breakdown section)
   - Lines 134-144 → `dashboard_footer.html`

3. **Refactor `dashboard.html`**:
   ```django
   {% extends 'base.html' %}
   {% load static %}
   
   {% block content %}
     {% include 'analyzer/partials/dashboard_header.html' %}
     {% include 'analyzer/partials/scoreboard_table.html' %}
     {% include 'analyzer/partials/dashboard_navigation.html' %}
     {% include 'analyzer/partials/dashboard_footer.html' %}
   {% endblock %}
   ```

4. **Test**: Run CQ-WW analysis, verify dashboard looks identical

### Phase 1B: ARRL 10 Implementation (After Phase 1A)

1. Create `arrl_10_dashboard.html` using same partials
2. Determine ARRL 10-specific sections (may need different strategic breakdown)
3. Identify any new partials needed

### Phase 1C: Complete Phase 1 (After ARRL 10)

1. Extract any additional common patterns discovered during ARRL 10
2. Refactor QSO/Multiplier dashboards
3. Document what's generic vs contest-specific

---

## Decision Matrix

| Factor | Phase 1 First | ARRL 10 First |
|--------|---------------|---------------|
| **Code Duplication** | ✅ Low (reuse partials) | ❌ High (copy template) |
| **Refactor Risk** | ✅ Low (test with CQ-WW) | ⚠️ Medium (touches 2 files) |
| **Speed to ARRL 10** | ✅ Faster (reuse partials) | ⚠️ Slower (copy & modify) |
| **Technical Debt** | ✅ Low (clean structure) | ❌ High (2 large templates) |
| **Learning Value** | ⚠️ Medium (extract obvious) | ✅ High (see actual needs) |
| **Maintainability** | ✅ High (shared partials) | ❌ Low (duplicated code) |

**Winner: Phase 1 First** (5 wins, 1 tie)

---

## Final Answer

**✅ Do Phase 1 first, but keep it focused.**

Extract only the **obviously common** elements (header, scoreboard table structure, navigation, footer) before starting ARRL 10. This gives you:
- Immediate cleanup of CQ-WW
- Reusable components for ARRL 10
- Foundation without over-engineering
- Ability to learn from ARRL 10 and complete Phase 1 properly

**Defer extracting** the Strategic Breakdown section until you see what ARRL 10 needs. It might be very different (single-band vs multi-band), so extracting it now might lock you into the wrong structure.

This is the **"YAGNI meets DRY"** approach: extract what's clearly reusable, defer what's uncertain until you have more information.
