# Versioning Policy Quick Reference

**For:** AI Agent Implementation  
**Date:** 2026-01-24  
**Current Project Version:** 1.0.0-alpha.10

---

## Category Quick Reference

| Category | Files | Version Rule | Compatible With? | Update Trigger |
|----------|-------|--------------|------------------|----------------|
| **A: User Docs** | UsersGuide.md, InstallationGuide.md, ReportInterpretationGuide.md | Match project | No | Every release |
| **B: Programmer Ref** | ProgrammersGuide.md | Match project | No | Every release |
| **C: Algorithm Specs** | CallsignLookupAlgorithm.md, RunS&PAlgorithm.md, WPXPrefixLookup.md | Independent | Yes (range format) | Every release (field), or when algorithm changes |
| **D: Style Guides** | CLAReportsStyleGuide.md | Independent | No | When style rules change |

---

## Current File Status

### Needs Update to 1.0.0-alpha.10
- UsersGuide.md: 1.0.0-alpha.4 → 1.0.0-alpha.10
- InstallationGuide.md: 1.0.0-alpha.3 → 1.0.0-alpha.10
- ReportInterpretationGuide.md: 0.160.0-Beta → 1.0.0-alpha.10
- ProgrammersGuide.md: 0.160.0-Beta → 1.0.0-alpha.10

### Needs Compatible With Field
- CallsignLookupAlgorithm.md: Add "Compatible with: up to v1.0.0-alpha.10"
- RunS&PAlgorithm.md: Add "Compatible with: up to v1.0.0-alpha.10"
- WPXPrefixLookup.md: Add "Compatible with: up to v1.0.0-alpha.10"

### Needs Category Metadata
- All files need "Category:" field
- CLAReportsStyleGuide.md: Add "Category: Style Guide"

---

## Standardized Metadata Template

### Category A & B Template
```markdown
**Version:** 1.0.0-alpha.10
**Date:** 2026-01-24
**Last Updated:** 2026-01-24
**Category:** User Guide | Programmer Reference
```

### Category C Template
```markdown
**Version:** 0.90.11-Beta
**Date:** 2025-10-06
**Last Updated:** 2026-01-24
**Category:** Algorithm Spec
**Compatible with:** up to v1.0.0-alpha.10
```

### Category D Template
```markdown
**Version:** 1.4.0
**Date:** 2026-01-07
**Last Updated:** 2026-01-24
**Category:** Style Guide
```

---

## Revision History Template

### Category A & B (Version Bump Only)
```markdown
## [1.0.0-alpha.10] - 2026-01-24
### Changed
- Updated version to match project release v1.0.0-alpha.10 (no content changes)
```

### Category C (Compatible With Update)
```markdown
## [0.90.11-Beta] - 2026-01-24
### Changed
- Updated "Compatible with" field to include project version v1.0.0-alpha.10
```

---

## Compatible With Field Rules

**Format:** `up to v1.0.0-alpha.10` (range format)

**Update Rule:** Update "up to" version with EVERY project release

**Breaking Change Rule:** If algorithm version increments due to breaking change:
- Delete "Compatible with" field entirely
- Add note: "See previous version of this document (v[old-version]) for compatibility with earlier project versions"

**Backwards Compatible Rule:** If algorithm change is backwards compatible:
- Keep existing "Compatible with" field
- Update "up to" version to include new project version

---

## Discrepancy Detection

**Before ANY version update:**
1. Read AI_AGENT_RULES.md Section "Version Management"
2. Read VersionManagement.md Section 3
3. Compare for consistency
4. If discrepancy: STOP, report, wait for guidance

**What to Check:**
- Category definitions match
- File lists match
- Workflow steps align
- Policy rules consistent
- Version formats match

---

## Implementation Order

1. Create VersionManagement.md (Phase 1)
2. Update AI_AGENT_RULES.md (Phase 2)
3. Update Contributing.md and ProgrammersGuide.md (Phase 3)
4. Update all documentation files (Phase 4)
5. Verify everything (Phase 5)

---

## Key Decisions Made

1. Compatible With format: "up to vX.Y.Z" (not list, not range)
2. Breaking algorithm changes: Delete field, add note about previous version
3. Style guides: Always current, no Compatible With field
4. Revision history: Always add entry, even for version bumps only
5. Discrepancy detection: STOP and ask if documents conflict

---

## Files to Create/Modify

**New Files:**
- Docs/VersionManagement.md

**Files to Modify:**
- Docs/AI_AGENT_RULES.md
- Docs/Contributing.md
- Docs/ProgrammersGuide.md
- Docs/UsersGuide.md
- Docs/InstallationGuide.md
- Docs/ReportInterpretationGuide.md
- Docs/CallsignLookupAlgorithm.md
- Docs/RunS&PAlgorithm.md
- Docs/WPXPrefixLookup.md
- Docs/CLAReportsStyleGuide.md
- Docs/PerformanceProfilingGuide.md (may need category decision)

**Total:** 1 new file, 11 files to modify
