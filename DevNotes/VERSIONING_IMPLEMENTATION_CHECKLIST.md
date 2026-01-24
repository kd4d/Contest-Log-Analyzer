# Versioning Policy Implementation Checklist

**Date:** 2026-01-24  
**Status:** Implementation Guide  
**Category:** Policy Implementation  
**Use With:** `DevNotes/VERSIONING_POLICY_IMPLEMENTATION_HANDOFF.md`

---

## Implementation Checklist

Use this checklist to track progress through the implementation phases.

### Phase 1: Create VersionManagement.md

- [ ] Create `Docs/VersionManagement.md`
- [ ] Add Section 1: Project Versioning Strategy
- [ ] Add Section 2: Release Workflow (summary with reference)
- [ ] Add Section 3: Documentation Versioning Policy
  - [ ] Category definitions (A, B, C, D)
  - [ ] Versioning rules per category
  - [ ] Compatible With field management
  - [ ] Revision history standards
  - [ ] Documentation Index format
- [ ] Add Section 4: Maintenance Procedures
- [ ] Add Section 5: AI Agent Requirements
  - [ ] Discrepancy detection mechanism
  - [ ] Detection checklist
  - [ ] Reporting format
- [ ] Add Section 6: Quick Reference
- [ ] Add Section 7: Examples
- [ ] Verify all policy decisions are included
- [ ] Verify format matches project standards

### Phase 2: Update AI_AGENT_RULES.md

- [ ] Add discrepancy detection at start of "Version Management" section
  - [ ] Prominent warning with ⚠️
  - [ ] Detection checklist
  - [ ] Reporting format
  - [ ] STOP instruction
- [ ] Update "Release Workflow" section
  - [ ] Add Step 0: Document Consistency Check
  - [ ] Update Step 3: Add documentation update procedures
  - [ ] Reference VersionManagement.md Section 3
  - [ ] Include quick reference for categories
- [ ] Update "Update Version References" subsection
  - [ ] Add documentation update steps
  - [ ] Reference policy categories
  - [ ] Include verification checklist
- [ ] Add to "Error Handling" section
  - [ ] Document discrepancy handling
- [ ] Verify all references are correct
- [ ] Verify workflow is clear and actionable

### Phase 3: Update Supporting Documentation

- [ ] Update `Docs/Contributing.md`
  - [ ] Add reference to VersionManagement.md in versioning section
  - [ ] Keep SemVer overview
  - [ ] Verify reference is correct
- [ ] Update `Docs/ProgrammersGuide.md`
  - [ ] Add "Documentation Index" section
  - [ ] List all maintained documentation
  - [ ] Include category information
  - [ ] Reference VersionManagement.md
  - [ ] Verify all files are listed
  - [ ] Verify no broken links

### Phase 4: Update Documentation Files

#### Category A: User-Facing Documentation

- [ ] `UsersGuide.md`
  - [ ] Update version: 1.0.0-alpha.4 → 1.0.0-alpha.10
  - [ ] Update "Last Updated": 2026-01-24
  - [ ] Add "Category: User Guide"
  - [ ] Add revision history entry
- [ ] `InstallationGuide.md`
  - [ ] Update version: 1.0.0-alpha.3 → 1.0.0-alpha.10
  - [ ] Update "Last Updated": 2026-01-24
  - [ ] Add "Category: User Guide"
  - [ ] Add revision history entry
- [ ] `ReportInterpretationGuide.md`
  - [ ] Update version: 0.160.0-Beta → 1.0.0-alpha.10
  - [ ] Update "Last Updated": 2026-01-24
  - [ ] Add "Category: User Guide"
  - [ ] Add revision history entry

#### Category B: Programmer Reference

- [ ] `ProgrammersGuide.md`
  - [ ] Update version: 0.160.0-Beta → 1.0.0-alpha.10
  - [ ] Update "Last Updated": 2026-01-24
  - [ ] Add "Category: Programmer Reference"
  - [ ] Add revision history entry
  - [ ] Add Documentation Index section (from Phase 3)

#### Category C: Algorithm Specifications

- [ ] `CallsignLookupAlgorithm.md`
  - [ ] Keep version: 0.90.11-Beta
  - [ ] Add "Category: Algorithm Spec"
  - [ ] Add "Compatible with: up to v1.0.0-alpha.10"
  - [ ] Update "Last Updated": 2026-01-24
  - [ ] Add revision history entry for Compatible With update
- [ ] `RunS&PAlgorithm.md`
  - [ ] Keep version: 0.47.4-Beta
  - [ ] Add "Category: Algorithm Spec"
  - [ ] Add "Compatible with: up to v1.0.0-alpha.10"
  - [ ] Update "Last Updated": 2026-01-24
  - [ ] Add revision history entry for Compatible With update
- [ ] `WPXPrefixLookup.md`
  - [ ] Keep version: 0.70.0-Beta
  - [ ] Add "Category: Algorithm Spec"
  - [ ] Add "Compatible with: up to v1.0.0-alpha.10"
  - [ ] Update "Last Updated": 2026-01-24
  - [ ] Add revision history entry for Compatible With update

#### Category D: Style Guides

- [ ] `CLAReportsStyleGuide.md`
  - [ ] Keep version: 1.4.0
  - [ ] Add "Category: Style Guide"
  - [ ] Update "Last Updated": 2026-01-24 (if needed)
  - [ ] Verify no "Compatible With" field

#### Other Files (May Need Decision)

- [ ] `PerformanceProfilingGuide.md`
  - [ ] Determine category (likely Category A or B)
  - [ ] Update accordingly

### Phase 5: Verification and Testing

- [ ] Verify VersionManagement.md completeness
  - [ ] All sections present
  - [ ] All policy decisions included
  - [ ] Examples are correct
- [ ] Verify AI_AGENT_RULES.md updates
  - [ ] Discrepancy detection is prominent
  - [ ] Workflow references are correct
  - [ ] All steps are clear
- [ ] Verify all documentation files
  - [ ] All versions correct per category
  - [ ] All metadata standardized
  - [ ] All Compatible With fields use range format
  - [ ] All revision history entries added
  - [ ] Format consistent across all files
- [ ] Verify cross-references
  - [ ] No broken links
  - [ ] All references point to correct sections
- [ ] Verify Documentation Index
  - [ ] All files listed
  - [ ] Categories correct
  - [ ] Versions match actual files
- [ ] Final consistency check
  - [ ] AI_AGENT_RULES.md and VersionManagement.md are consistent
  - [ ] All files follow the policy
  - [ ] No discrepancies detected

---

## Current Project Version

**Project Version:** `1.0.0-alpha.10`  
**Source:** `contest_tools/version.py` line 53  
**Date:** 2026-01-24

---

## File Status Before Implementation

### Category A (Should be 1.0.0-alpha.10)
- `UsersGuide.md`: 1.0.0-alpha.4 ❌
- `InstallationGuide.md`: 1.0.0-alpha.3 ❌
- `ReportInterpretationGuide.md`: 0.160.0-Beta ❌

### Category B (Should be 1.0.0-alpha.10)
- `ProgrammersGuide.md`: 0.160.0-Beta ❌

### Category C (Independent, need Compatible With)
- `CallsignLookupAlgorithm.md`: 0.90.11-Beta ✅ (needs Compatible With)
- `RunS&PAlgorithm.md`: 0.47.4-Beta ✅ (needs Compatible With)
- `WPXPrefixLookup.md`: 0.70.0-Beta ✅ (needs Compatible With)

### Category D (Independent, no Compatible With)
- `CLAReportsStyleGuide.md`: 1.4.0 ✅ (needs Category metadata)

### Unknown Category
- `PerformanceProfilingGuide.md`: 1.0 (needs category determination)

---

## Key Policy Points to Remember

1. **Category A & B:** Match project version, update on every release
2. **Category C:** Independent versioning, update "Compatible With" on every release (range format: "up to vX.Y.Z")
3. **Category D:** Independent versioning, no "Compatible With" field
4. **Compatible With Format:** "up to v1.0.0-alpha.10" (not a list, not a range like "v0.0.0 - v1.0.0-alpha.10")
5. **Breaking Algorithm Changes:** Delete "Compatible With" field, add note about previous version
6. **Revision History:** Always add entry for version bumps, even if no content changes
7. **Discrepancy Detection:** STOP and ask if AI_AGENT_RULES.md and VersionManagement.md conflict

---

## Testing the Implementation

After implementation, verify:

1. **VersionManagement.md exists and is complete**
2. **AI_AGENT_RULES.md has discrepancy detection**
3. **All Category A & B files match project version**
4. **All Category C files have "Compatible With" field**
5. **All files have standardized metadata**
6. **Documentation Index is complete**
7. **No broken cross-references**
8. **Discrepancy detection mechanism is clear**

---

## Notes for Implementation

- Work systematically through each phase
- Verify each file before moving to next
- Use the examples in VersionManagement.md as templates
- If unsure about any decision, refer to the handoff document
- Remember: This is for AI agents, so be explicit and clear
