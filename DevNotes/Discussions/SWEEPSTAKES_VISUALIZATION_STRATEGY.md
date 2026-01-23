# Sweepstakes Visualization Strategy Discussion

**Date:** 2025-01-XX  
**Context:** Sweepstakes contest has unique scoring rules that make standard multi-band visualizations misleading. Need to reframe visualization approach for contest-wide QSO/multiplier counting.  
**Status:** Phase 1 Implementation Complete - See `SWEEPSTAKES_VISUALIZATION_DETAILED_IMPLEMENTATION_PLAN.md` for implementation status.

---

## Core Problem Statement

Sweepstakes has unique scoring rules that make standard multi-band visualizations misleading:

1. **QSOs count once per contest** (`dupe_check_scope: "all_bands"`), not per band
2. **Multipliers count once per contest** (`totaling_method: "once_per_log"`), not per band
3. **Multiplier saturation**: Most competitors work 80+ of 85 available sections

This fundamentally impacts the usefulness of current graphical reports.

---

## Impact Analysis: Current Reports vs. Sweepstakes Reality

### 1. QSO Breakdown Chart (Band-by-Band)

**Current Behavior:**
- Shows one subplot per band
- Displays unique/common QSOs per band
- Implies QSOs are counted per band

**The Problem:**
- QSOs count once per contest, not per band
- Two stations may work the same stations but on different bands
- Band-by-band comparison doesn't reflect scoring reality
- Misleading for strategy analysis

**What's Needed:**
- **Primary View**: Contest-wide totals (one bar: Log1 Unique | Common | Log2 Unique)
  - Overall "Common" information is very useful
- **Secondary View**: QSO Band Distribution (DIFFERENT from current plot)
  - Shows band and Run/S&P distribution of stations worked by one of the two logs
  - "Uniques" are defined as: Stations worked by one of the two stations (in one of the two logs)
  - Categorized by band and mode just like current QSO Breakdown display but computed differently
  - "Common" information by band is NOT useful - only overall Common is useful

**Key Difference:**
- Current plot: Shows QSOs per band (misleading for contest-wide counting)
- New Band Distribution: Shows which stations were worked, categorized by band and Run/S&P
- This is NOT just "informational" - it's a different analysis showing band/mode distribution of worked stations

**Implementation Note:**
- Use `dupe_check_scope: "all_bands"` to detect contest-wide QSO counting
- **Do NOT** look at multiplier rules for this decision - that's the wrong signal

---

### 2. Multiplier Breakdown Reports (Existing)

**Current State:**
- Multiplier reports exist for Sweepstakes
- Text-based missed multipliers report may be acceptable
- Graphical reports may be less useful due to saturation

**Saturation Impact:**
- Most competitors work 80+ of 85 sections
- Standard breakdowns may show mostly "worked" with few "missed"
- Need to emphasize the missed sections and how they were missed

**Key Insights Needed:**
- Which of the 5-10 missed sections were not worked?
- How were they missed? (Run vs S&P, band selection)
- Were they worked by at least one of the logs being compared? (This is the ONLY definition of "available" - whether the multiplier appears in at least one of the logs being compared)

**Band Selection Importance:**
- Some sections may be easier on certain bands
- Band distribution of multiplier acquisition is strategy-relevant
- Run vs S&P breakdown per multiplier shows acquisition method

**Time Distribution:**
- Less critical for strategy
- Most multipliers are worked early
- Focus on missed multipliers and how they were missed, not when they were acquired

---

### 3. Multiplier Acquisition Timeline

**Current State:**
- Text report exists for multiplier acquisition timeline
- Shows hourly progression of unique multipliers
- Shows when each section was first worked

**Decision:**
- Keep this text report for Sweepstakes
- Include it in bulk download
- **Do NOT** include it in dashboards (not needed there)
- Focus dashboard on missed multipliers with Run/S&P and band context

---

## Missed Multipliers: The Critical Report

**What's Needed:**
- List of missed sections (the 5-10 not worked)
- For each missed section:
  - Was it worked by at least one of the logs being compared? (This is the ONLY definition of "available")
  - If worked by one of the logs, which bands was it worked on?
  - Was it worked via Run or S&P?
  - What performed correctly? (Key insight: whether the stations were worked and what performed correctly)

**Important Clarification:**
- "Available" is ONLY defined by whether the multiplier appears in at least one of the logs being compared
- We do NOT know whether a missed multiplier "could" have been worked - that knowledge is not available
- The key is whether the stations were worked and what performed correctly
- There is NO concept of "balance" between Run and S&P - this is not a useful distinction

**Visualization Approach:**
- Text table showing:
  - Section name
  - Worked by (which log(s) worked it, count)
  - Bands where it was worked (if worked by one of the logs)
  - Run vs S&P breakdown (if worked by one of the logs)

**This Informs:**
- Which stations were worked and what performed correctly
- Band selection: were certain bands used to acquire multipliers?
- Operating style: how were multipliers acquired (Run vs S&P)

---

## Contest Separation: CW vs PH

**Reality:**
- Sweepstakes CW and Sweepstakes PH are completely separate contests
- Different weekends, different logs, different competitors
- No need to combine or analyze together

**Implementation:**
- Treat as separate contest instances
- Each has its own analysis and reports
- No special handling for "multi-mode" analysis

**Why This Matters:**
- Simplifies implementation
- Each contest instance is self-contained
- No special cross-contest comparison needed

---

## Run/S&P Classification: "Unknown" is Correct

**Current Approach:**
- Run/S&P conflicts (same multiplier worked both Run and S&P) are classified as "Unknown"

**Assessment:**
- "Unknown" is MORE CORRECT than "Mixed" for Run/S&P conflicts
- There are times when rates are so low that Run vs S&P cannot be reliably estimated
- This is an important concept that needs to be emphasized in documentation (web and off-line)

**Key Insight:**
- The key is whether the stations were worked and what performed correctly
- There is NO concept of "balance" between Run and S&P - this is not a useful distinction
- "Unknown" correctly represents cases where Run/S&P cannot be reliably determined

**Documentation Requirement:**
- Must emphasize in documentation (web and off-line) that "Unknown" represents cases where Run/S&P cannot be reliably estimated
- This is particularly important when rates are very low
- Users need to understand that "Unknown" is a valid classification, not a data quality issue

---

## "Available" vs "Missed" Multipliers: Discussion

**Question:** What is the useful distinction between "Available" and "Missed" multipliers?

**Current Understanding:**
- "Available" = multiplier appears in at least one of the logs being compared
- "Missed" = multiplier does not appear in a particular log

**The Issue:**
- If we're comparing two logs, and a multiplier appears in one but not the other, is there a useful distinction between calling it "available" vs "missed"?
- Both terms describe the same fact: one log has it, the other doesn't

**Potential Value:**
- "Available" might indicate: "This multiplier was worked by at least one competitor in this comparison"
- "Missed" might indicate: "This multiplier was not worked by this particular log"
- But these are just two ways of describing the same data

**Need for Clarification:**
- What useful distinction does "available" provide that "missed" doesn't?
- Is there a use case where knowing "available" vs "missed" informs different decisions?
- Or are these just different labels for the same information?

**Current Approach:**
- Focus on what we can determine: which multipliers were worked by which logs
- Show band distribution and Run/S&P breakdown for multipliers that were worked
- Avoid implying knowledge we don't have (whether a multiplier "could" have been worked)

---

## Visualization Format for Missed Multipliers

**Context:**
- Typically 5-10 missed multipliers (out of 85)
- Need: which sections were missed, band distribution, Run/S&P breakdown

**Recommendation: Text Table with Structured Columns**

**Format:**
```
Section | Worked By | Bands Worked | Run | S&P | Mixed | Notes
--------|-----------|--------------|-----|-----|-------|------
WMA     | 2 of 3    | 20M, 40M     | 1   | 1   | 0     | Available on 2 bands
...
```

**Why Text Table:**
- Small dataset (5-10 items) fits perfectly in a table
- Easy to scan and compare
- Supports sorting/filtering
- Clear column structure

**When to Consider Graphical:**
- If dataset grows significantly
- If we need temporal patterns (not needed here)
- If we need spatial relationships (not applicable)

**Heatmap Consideration:**
- Heatmaps are useful for large, dense datasets
- For 5-10 items, table is more readable
- If we later analyze all 85 sections (worked + missed), heatmap could show patterns across full set

**Butterfly Charts:**
- Useful for time-series comparisons
- Less suitable for categorical "missed multiplier" analysis
- Better for activity/QSO rate comparisons

**Alternative: Enhanced Text Table with Visual Indicators**
- Color coding: red for "missed by all", yellow for "missed by some"
- Band indicators: icons or badges for bands where worked
- Run/S&P indicators: visual markers for acquisition method
- Keeps table format but adds visual cues

---

## Dashboard Architecture: Navigation and Organization Layer

**Core Principle:**
- Reports are the primary artifacts (generated, testable, reusable)
- Dashboards are navigation/visualization layers that organize and present reports

**Current Architecture:**
- Reports generate artifacts (HTML, JSON, text files)
- Dashboards discover and display these artifacts
- Dashboards provide navigation, context, and organization

**For Sweepstakes:**
- Generate appropriate reports (contest-wide QSO breakdown, enhanced missed multipliers, etc.)
- Multiplier Dashboard discovers and displays these reports
- Dashboard provides navigation between reports and context

**Modularity:**
- Reports are independent and reusable
- Dashboards can be contest-specific or generic
- Same report can appear in multiple dashboards
- Reports are testable in isolation

**Testability:**
- Test reports independently
- Test dashboard discovery/display separately
- Integration tests verify dashboard finds correct reports

**Reusability:**
- Reports can be reused across contests (with configuration)
- Dashboard components can be reused
- Contest-specific dashboards can mix generic and specialized reports

**Sweepstakes-Specific Dashboard:**
- May have different tab structure
- May emphasize different reports
- Still discovers and displays standard report artifacts
- Configuration controls which reports are generated/displayed

**Implementation Approach:**
1. Generate reports (contest-wide QSO breakdown, enhanced missed multipliers)
2. Dashboard discovers reports via manifest
3. Dashboard organizes reports into appropriate tabs/sections
4. Dashboard provides navigation and context

**Benefits:**
- Reports remain source of truth
- Dashboards are presentation layers
- Easy to add new reports without changing dashboards
- Easy to create contest-specific dashboards by selecting appropriate reports

---

## Visualization Recommendations Summary

**For Missed Multipliers (5-10 items):**
- **Primary**: Enhanced text table with columns for Section, Worked By, Bands, Run/S&P/Mixed counts
- **Visual Enhancements**: Color coding, band badges, acquisition method indicators
- **Sorting/Filtering**: By "Worked By" count, by band, by acquisition method

**For Multiplier Analysis:**
- **Text Summary**: Enhanced missed multipliers text report (table format)
- **Focus**: Which multipliers were worked, band distribution, Run/S&P breakdown
- **Note**: Do NOT pursue multiplier visualization at this time
- **Consideration**: Whether other contests would benefit from similar text summary approach

**For QSO Breakdown:**
- **Primary**: Contest-wide stacked bar (Log1 Unique | Common | Log2 Unique)
- **Secondary**: Band distribution view (informational, clearly labeled)
- **Butterfly Charts**: Use for time-series activity comparisons (existing pattern)

**When to Use Heatmaps:**
- If analyzing all 85 sections (worked + missed) in single view
- To show patterns across full multiplier set
- For large, dense datasets where patterns emerge visually
- **Not recommended** for 5-10 missed multipliers view

---

## Phase Breakdown (Refined)

### Phase 1: QSO Breakdown Refactoring
**Goal:** Fix misleading band-by-band QSO breakdown

**Tasks:**
- Detect contest-wide QSO counting (`dupe_check_scope: "all_bands"`)
- Generate contest-wide QSO breakdown report
- Generate band distribution report (informational)
- Dashboard discovers and displays both

**Deliverables:**
- Contest-wide QSO breakdown report (overall Common is very useful)
- QSO Band Distribution report (shows band and Run/S&P distribution of stations worked by one of the two logs)
- Note: "Common" information by band is NOT useful - only overall Common is useful
- Dashboard integration

---

### Phase 2: Enhanced Missed Multipliers Report
**Goal:** Provide actionable missed multiplier analysis

**Tasks:**
- Generate enhanced missed multipliers text report (table format)
- Include Run/S&P/Mixed breakdown
- Include band distribution
- Dashboard displays in Multiplier Dashboard

**Deliverables:**
- Enhanced missed multipliers report (text table)
- Shows which multipliers were worked by which logs
- Band distribution and Run/S&P breakdown for worked multipliers
- Dashboard integration

---

### Phase 3: Multiplier Text Summary
**Goal:** Provide text summary of multiplier analysis

**Tasks:**
- Enhanced missed multipliers text report (table format)
- Shows which multipliers were worked by which logs
- Band distribution and Run/S&P breakdown
- Consider whether other contests would benefit from similar approach

**Deliverables:**
- Enhanced missed multipliers text report
- Documentation of approach for potential reuse in other contests
- Note: Do NOT pursue multiplier visualization at this time

---

### Phase 4: Report Suppression and Configuration
**Goal:** Enable contest-specific report generation

**Tasks:**
- Implement report suppression via JSON configuration
- Configure Sweepstakes-specific report generation
- Test and validate

**Deliverables:**
- Configuration system for report suppression
- Contest-specific visualization rules
- Documentation

---

### Phase 5: Architecture Validation
**Goal:** Ensure modular, reusable architecture

**Tasks:**
- Ensure reports remain primary artifacts
- Ensure dashboards remain navigation layers
- Validate modularity and reusability

**Deliverables:**
- Architecture validation
- Reusability guidelines

---

## Key Design Decisions

1. **Run/S&P**: "Unknown" is correct for Run/S&P conflicts - rates may be too low to reliably estimate
2. **Visualization**: Text table for missed multipliers (5-10 items)
3. **QSO Band Distribution**: Shows band and Run/S&P distribution of stations worked by one of the two logs (DIFFERENT from current plot)
4. **Common Information**: Overall Common is very useful; Common by band is NOT useful
5. **Dashboard Role**: Navigation/organization layer over reports
6. **Reports**: Primary artifacts; dashboards discover and display them
7. **Band Display**: Show all bands (low/high grouping is just for display organization)
8. **Contest Separation**: CW and PH are separate contests; no cross-contest analysis needed
9. **Multiplier Timeline**: Keep text report, include in bulk download, NOT in dashboards
10. **Multiplier Visualization**: Do NOT pursue at this time; consider text summary approach for other contests

---

## Open Questions Resolved

1. **Band Distribution Granularity**: Show all bands (low/high grouping for display organization)
2. **Run/S&P Classification**: "Unknown" is correct for Run/S&P conflicts - must emphasize in documentation that rates may be too low to reliably estimate
3. **QSO Band Distribution**: Shows band and Run/S&P distribution of stations worked by one of the two logs (computed differently from current plot)
4. **Common Information**: Overall Common is very useful; Common by band is NOT useful
5. **Visualization Format**: Text table for 5-10 missed multipliers
6. **Integration**: Reports are primary artifacts; dashboards are navigation/visualization layers
7. **Multiplier Timeline**: Keep text report, include in bulk download, NOT in dashboards
8. **Multiplier Visualization**: Do NOT pursue at this time

## Open Questions for Discussion

1. **"Available" vs "Missed" Multipliers**: What is the useful distinction? Both describe the same fact (multiplier appears in one log but not the other). Is there a use case where this distinction informs different decisions?

---

## Future Considerations (Out of Scope)

**Big Data Analysis:**
- Field-wide multiplier availability analysis
- Access to contest databases/archives
- Cross-contest pattern analysis
- Would require significant infrastructure changes

**Note:** This is a potential enhancement, not technical debt. Tracked in `DevNotes/POTENTIAL_ENHANCEMENTS.md` under "Data Sources & Integration" category.
