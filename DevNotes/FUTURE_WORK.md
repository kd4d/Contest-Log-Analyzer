# Future Work Tracking

**Purpose:** Track committed work that we have decided to proceed with. These are items we WILL implement, though most won't be in the first release.

**How This Differs:**
- **Technical Debt** (`TECHNICAL_DEBT.md`): Issues with existing code that need fixing
- **Future Work** (this document): Committed work we will do (decided to proceed)
- **Potential Enhancements** (`DevNotes/POTENTIAL_ENHANCEMENTS.md`): Ideas we might do (not committed)

**How to Use:**
- **AI Agents:** Review this document when planning work
- **Add items** when we decide to proceed with an enhancement
- **Update status** as work progresses
- **Link** to implementation plans when created

**Status Legend:**
- [ ] Planned - Committed to doing, not yet started
- [ ] In Progress - Currently being implemented
- [x] Completed - Implemented and verified
- ~~[ ] Deferred~~ - Postponed (with reason)
- ~~[ ] Cancelled~~ - Decided not to proceed (with reason)

**Note:** Most items in this document will NOT be in the first release. This tracks committed work for future releases.

---

## Sweepstakes Visualization Enhancements

### Contest-Wide QSO Breakdown Report

**Status:** [x] Completed  
**Priority:** HIGH  
**Date Added:** 2025-01-XX  
**Date Completed:** 2026-01-24

**Description:**
- Generate contest-wide QSO breakdown report (not band-by-band)
- Primary view: Contest totals (Log1 Unique | Common | Log2 Unique)
- Secondary view: Band distribution (informational only, clearly labeled)

**Implementation:**
- Contest-wide QSO breakdown report implemented
- QSO Band Distribution report implemented
- Dashboard integration complete with conditional tabs

**Related:**
- `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md`
- `DevNotes/Archive/SWEEPSTAKES_VISUALIZATION_IMPLEMENTATION_PLAN.md`
- `DevNotes/Archive/SWEEPSTAKES_VISUALIZATION_DETAILED_IMPLEMENTATION_PLAN.md`

---

### Enhanced Missed Multipliers Report

**Status:** [x] Completed  
**Priority:** HIGH  
**Date Added:** 2025-01-XX  
**Date Completed:** 2026-01-24

**Description:**
- Enhanced missed multipliers report with Run/S&P and band context
- Shows which logs worked each missed multiplier
- Shows bands where multiplier was worked
- Shows Run/S&P/Unknown breakdown

**Implementation:**
- `MultiplierStatsAggregator.get_missed_data()` enhanced with `enhanced=True` parameter
- `text_enhanced_missed_multipliers.py` report created
- Dashboard integration complete
- Report appears in Multiplier Dashboard when missed multipliers exist

**Related:**
- `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md`
- `DevNotes/Archive/SWEEPSTAKES_VISUALIZATION_IMPLEMENTATION_PLAN.md`
- `DevNotes/Archive/SWEEPSTAKES_VISUALIZATION_DETAILED_IMPLEMENTATION_PLAN.md`

---

### Multiplier Acquisition Timeline (Phase 3)

**Status:** [ ] Planned  
**Priority:** MEDIUM  
**Date Added:** 2025-01-XX

**Description:**
- Multiplier acquisition timeline text reports (single-log and multi-log comparison)
- Show hourly progression of unique multipliers (when each multiplier is first worked)
- Follow rate sheet report structure pattern
- Include in bulk download, exclude from dashboards

**Requirements:**
- Create `text_multiplier_timeline.py` (single-log version)
- Create `text_multiplier_timeline_comparison.py` (multi-log version)
- Include in bulk download
- Exclude from dashboards (per design decision)

**Related:**
- `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md`
- `DevNotes/Archive/SWEEPSTAKES_VISUALIZATION_IMPLEMENTATION_PLAN.md` (Phase 3)

---

## Template for New Items

When adding new future work items, use this template:

```markdown
### [Item Name]

**Status:** [ ] Planned  
**Priority:** HIGH/MEDIUM/LOW  
**Date Added:** YYYY-MM-DD

**Description:**
- Brief description of the work

**Requirements:**
- What's needed to implement?
- Dependencies?

**Related:**
- Links to discussions, implementation plans, or related items

**Notes:**
- Additional context, decisions, or considerations
```

---

## How to Use This Document

### Adding New Items

1. **Decision Point**: Item must be decided to proceed (moved from Potential Enhancements)
2. **Use the Template**: Copy the template and fill in details
3. **Set Status**: Start with "Planned" (committed but not started)
4. **Set Priority**: Based on value and urgency
5. **Link Related Items**: Reference discussions, plans, or related future work

### Updating Items

1. **Status Changes**: Update status as item progresses
2. **Add Notes**: Document decisions, discussions, or changes
3. **Link Implementations**: When ready, create implementation plan and link
4. **Mark Completed**: When implemented and verified

### Lifecycle

1. **Proposed** → `POTENTIAL_ENHANCEMENTS.md` (Status: Proposed)
2. **Under Discussion** → `POTENTIAL_ENHANCEMENTS.md` (Status: Under Discussion)
3. **Decision to Proceed** → Move to `FUTURE_WORK.md` (Status: Planned)
4. **Ready to Implement** → Create implementation plan (separate document)
5. **Implementation** → `FUTURE_WORK.md` (Status: In Progress)
6. **Completed** → `FUTURE_WORK.md` (Status: Completed)

---

## Notes

- This document tracks committed work - items we have decided to proceed with
- Most items will NOT be in the first release
- Items move here from `POTENTIAL_ENHANCEMENTS.md` when we decide to proceed
- Implementation plans are created separately when ready to implement
- Keep items actionable and specific
