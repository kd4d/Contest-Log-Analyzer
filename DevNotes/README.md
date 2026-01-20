# DevNotes Directory

This directory contains planning documents, architectural decisions, and development discussions.

---

## Directory Structure

```
DevNotes/
├── [Active Planning Documents]          # Current work - AI agents READ these
├── Archive/                              # Completed plans - AI agents IGNORE
├── Discussions/                          # Historical discussions - AI agents IGNORE
├── Decisions_Architecture/                # Important patterns/decisions - AI agents READ
└── README.md                              # This file
```

---

## Directory Purposes

### Root DevNotes/ (Active Work)
**Purpose:** Active planning documents for current or deferred work.

**Contains:**
- Implementation plans ready for work
- Future work planning documents
- Deferred work documentation

**AI Agent Behavior:** READ these files - they contain active work.

**Examples:**
- `ARRL_DX_ASYMMETRIC_CONTEST_IMPLEMENTATION_PLAN.md` - Ready for implementation
- `LAQP_Implementation_Plan.md` - Future planning
- `DIRECTORY_STRUCTURE_REFACTORING_FUTURE_WORK.md` - Deferred work

---

### Archive/ (Completed Plans)
**Purpose:** Completed implementation plans for historical reference.

**Contains:**
- Step-by-step implementation plans that are complete
- One-time reorganization plans (like DevNotes organization)

**AI Agent Behavior:** IGNORE unless user explicitly requests historical context.

**When to Review:**
- User asks: "How was X implemented?"
- Researching implementation details of completed work
- User explicitly requests review

---

### Discussions/ (Historical Discussions)
**Purpose:** Obsolete or complete discussions where decisions were made.

**Contains:**
- Historical problem-solving discussions
- Architecture discussions where decisions were finalized
- Analysis documents for issues that are resolved

**AI Agent Behavior:** IGNORE unless user explicitly requests historical context.

**When to Review:**
- User asks: "Why did we choose Y?"
- Researching why a decision was made
- User explicitly requests review

**Note:** The decisions themselves are documented in `Decisions_Architecture/` or in code.

---

### Decisions_Architecture/ (Important Patterns)
**Purpose:** Reusable patterns, architectural principles, and important decisions.

**Contains:**
- Reusable implementation patterns
- Architectural principles that guide future work
- Important decisions that affect multiple contests/features

**AI Agent Behavior:** READ these files - they contain important guidance.

**Examples:**
- `MUTUALLY_EXCLUSIVE_MULTIPLIER_FILTERING_PATTERN.md` - Pattern for handling mutually exclusive multipliers
- `ANIMATION_DIMENSION_IMPLEMENTATION_SUMMARY.md` - Pattern for animation dimension selection
- `ARCHITECTURE_RULE_ENFORCEMENT_DISCUSSION.md` - Plugin architecture rules

---

## File Status Standardization

All DevNotes files should include standardized metadata:

```markdown
**Status:** Active | Completed | Deferred | Obsolete
**Date:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Category:** Planning | Discussion | Decision | Pattern
```

---

## Maintenance Guidelines

### For AI Agents

**When creating new DevNotes files:**

1. **Determine appropriate location:**
   - **Active work** → Root DevNotes/
   - **Completed plan** → Archive/
   - **Historical discussion** → Discussions/
   - **Reusable pattern/decision** → Decisions_Architecture/

2. **Use the "Value Test":**
   - **Decisions_Architecture/**: Documents reusable patterns, architectural principles, or important decisions that future work should follow
   - **Discussions/**: Historical conversations where decisions were made (the decision itself may be documented elsewhere)
   - **Archive/**: Completed step-by-step implementation plans (historical reference)
   - **Root DevNotes/**: Active planning documents for current or deferred work

3. **Include standardized metadata** (Status, Date, Last Updated, Category)

4. **When work is completed:**
   - Update file status to "Completed"
   - Move completed implementation plans to Archive/
   - Move resolved discussions to Discussions/
   - Keep patterns/decisions in Decisions_Architecture/ (they remain useful)

**When updating existing files:**

1. **Update "Last Updated" date** when making changes
2. **Update status** if work state changes (Active → Completed, etc.)
3. **Move files** when status changes (e.g., Active → Archive when completed)

### For Humans

- **Finding active work:** Check root DevNotes/ for files with "Status: Active" or "Ready for Implementation"
- **Understanding patterns:** Check Decisions_Architecture/ for reusable patterns
- **Historical context:** Check Archive/ or Discussions/ if needed
- **Structure questions:** See `Docs/AI_AGENT_RULES.md` section "DevNotes Directory Structure"

---

## Related Documentation

- **AI Agent Rules:** `Docs/AI_AGENT_RULES.md` - Contains detailed AI agent behavior for DevNotes
- **Technical Debt:** `TECHNICAL_DEBT.md` - Tracks technical debt items
- **Handover:** `HANDOVER.md` - Complex multi-session workflow state (if exists)

---

## Quick Reference

| Location | AI Agents | Purpose | Example |
|----------|-----------|---------|---------|
| Root DevNotes/ | READ | Active work | Implementation plans |
| Decisions_Architecture/ | READ | Patterns/decisions | Reusable patterns |
| Archive/ | IGNORE | Completed plans | Historical reference |
| Discussions/ | IGNORE | Historical discussions | Why decisions were made |

---

**Last Updated:** 2026-01-19
