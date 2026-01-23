# Potential Enhancements Tracking

**Purpose:** Track ideas, proposals, and potential enhancements that are under consideration but not yet committed. These are items we MIGHT do.

**How This Differs:**
- **Technical Debt** (`TECHNICAL_DEBT.md`): Issues with existing code that need fixing
- **Future Work** (`DevNotes/FUTURE_WORK.md`): Committed work we will do (decided to proceed)
- **Potential Enhancements** (this document): Ideas we might do (not committed)

**How to Use:**
- **AI Agents:** Review this document when discussing new features or enhancements
- **Add items** when new capabilities are proposed or discussed
- **Update status** as items are evaluated, deferred, or rejected
- **Link** to related discussions

**Status Legend:**
- [ ] Proposed - Initial idea, needs discussion
- [ ] Under Discussion - Being evaluated/designed
- ~~[ ] Deferred~~ - Postponed for later consideration (with reason)
- ~~[ ] Rejected~~ - Decided not to implement (with reason)

**Note:** Items move to `FUTURE_WORK.md` when we decide to proceed.

---

## Data Sources & Integration

### Big Data Analysis: Field-Wide Multiplier Availability

**Status:** [ ] Proposed  
**Priority:** RESEARCH  
**Date Added:** 2025-01-XX

**Description:**
- Analyze all submitted logs from contest databases/archives
- Determine field-wide multiplier availability
- Identify which multipliers were "available" in the playing field
- Cross-contest pattern analysis

**Use Cases:**
- Identify multipliers that were available but not worked by competitors
- Understand field-wide multiplier distribution
- Compare individual performance against field-wide opportunities

**Requirements:**
- Access to contest databases/archives
- Infrastructure for processing large datasets
- Data aggregation and analysis capabilities

**Challenges:**
- Requires significant infrastructure changes
- May need partnerships with contest organizations
- Data privacy and access considerations

**Related:**
- `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md` - Mentioned as future consideration

**Notes:**
- Currently outside scope of application
- Would require significant infrastructure investment
- Research needed to determine feasibility and value

---

## Analysis & Reporting Enhancements

### Multiplier Text Summary for Other Contests

**Status:** [ ] Proposed  
**Priority:** LOW  
**Date Added:** 2025-01-XX

**Description:**
- Enhanced missed multipliers text report (table format) being developed for Sweepstakes
- Shows which multipliers were worked by which logs
- Band distribution and Run/S&P breakdown for worked multipliers
- Consider whether other contests would benefit from similar text summary approach

**Use Cases:**
- Apply Sweepstakes multiplier text summary pattern to other contests
- Provide consistent multiplier analysis across contests
- Text-based approach may be more useful than graphical for some contests

**Requirements:**
- Evaluate Sweepstakes implementation
- Identify other contests that would benefit
- Adapt text summary format for different contest types

**Related:**
- `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md` - Text summary approach for Sweepstakes
- `DevNotes/FUTURE_WORK.md` - Enhanced Missed Multipliers Report (Sweepstakes)

**Notes:**
- Wait for Sweepstakes implementation to complete
- Evaluate effectiveness of text summary approach
- Consider contest-specific adaptations needed

---

### Heatmap Visualization for All Multipliers

**Status:** [ ] Proposed  
**Priority:** LOW  
**Date Added:** 2025-01-XX

**Description:**
- Heatmap visualization for all multipliers (worked + missed)
- Pattern analysis across full multiplier set
- Cross-contest multiplier comparison

**Use Cases:**
- Visualize patterns across all 85 sections (Sweepstakes)
- Identify multiplier acquisition strategies
- Compare multiplier performance across contests

**Requirements:**
- Heatmap visualization library
- Data aggregation for full multiplier set
- Dashboard integration

**Related:**
- `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md` - Discussed as potential enhancement

**Notes:**
- Not needed for current 5-10 missed multipliers (text table better)
- Could be valuable for full multiplier set analysis
- Would require larger dataset to be useful
- **Decision**: Do NOT pursue multiplier visualization at this time

---

## Template for New Items

When adding new potential enhancement items, use this template:

```markdown
### [Item Name]

**Status:** [ ] Proposed  
**Priority:** HIGH/MEDIUM/LOW/RESEARCH  
**Date Added:** YYYY-MM-DD

**Description:**
- Brief description of the enhancement/capability

**Use Cases:**
- What problems does this solve?
- Who would benefit?

**Requirements:**
- What's needed to implement?
- Dependencies?

**Challenges:**
- What are the obstacles?
- What needs to be resolved?

**Related:**
- Links to discussions, implementation plans, or related items

**Notes:**
- Additional context, decisions, or considerations
```

---

## How to Use This Document

### Adding New Items

1. **Identify the Category**: Choose the most appropriate category
2. **Use the Template**: Copy the template and fill in details
3. **Set Status**: Start with "Proposed" unless already under discussion
4. **Set Priority**: Based on value and urgency
5. **Link Related Items**: Reference discussions, plans, or related potential enhancements

### Updating Items

1. **Status Changes**: Update status as item progresses
2. **Add Notes**: Document decisions, discussions, or changes
3. **Move to Future Work**: When we decide to proceed, move item to `FUTURE_WORK.md`
4. **Mark Deferred/Rejected**: Use strikethrough and explain why

### Lifecycle

1. **Proposed** → This document (Status: Proposed)
2. **Under Discussion** → This document (Status: Under Discussion)
3. **Decision to Proceed** → Move to `FUTURE_WORK.md` (Status: Planned)
4. **Deferred** → This document (Status: Deferred, with reason)
5. **Rejected** → This document (Status: Rejected, with reason)

---

## Notes

- This document tracks ideas and proposals - items we might do
- Items move to `FUTURE_WORK.md` when we decide to proceed
- Don't be afraid to defer or reject items that don't make sense
- Focus on items that provide real value
- Keep items actionable and specific
- Link to detailed discussions rather than duplicating content
