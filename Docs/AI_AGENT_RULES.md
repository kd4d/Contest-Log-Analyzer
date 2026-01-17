# AI Agent Rules for Git Operations

This document provides specific rules for AI agents (like Cursor/Console AI) when performing git operations on this repository.

---

## Overview

**Primary Principle:** AI assists with git operations, but the user maintains final control over critical operations.

---

## What AI Can Do Directly

### [OK] Commit Message Generation
- Generate Angular-formatted commit messages following strict format
- Suggest appropriate commit types (feat, fix, docs, etc.)
- Format commit messages with proper structure (subject, blank line, body)
- Use multiple `-m` flags or single `-m` with escaped newlines for proper formatting

### [OK] Feature Branch Commits
- Create commits on feature branches
- Use informal messages during development ("wip", "refactor X")
- Commit code changes directly to feature branches

### [OK] Generate Commands
- Suggest git commands for workflows
- Generate merge commands with `--no-ff` flag
- Create command sequences for complex operations

### [OK] Automatic Operations
- Pre-commit hooks automatically update `version.py` git hash
- No manual intervention needed for hash updates

---

## What Requires User Review/Approval

### WARNING: Merges to Main Branch
**Process:**
1. AI generates merge command: `git merge --no-ff feat/branch-name`
2. AI generates merge commit message in Angular format
3. **User reviews** merge message in editor
4. **User saves/closes** editor to complete merge
5. **User pushes** when ready

**Why:** Main branch is sacred - requires human oversight

### WARNING: Creating Tags/Releases
**Process:**
1. AI suggests version number based on commit types
2. AI suggests update to `version.py`
3. **User confirms** version number
4. AI generates commands:
   ```bash
   # Update version.py __version__ to match tag
   # Commit version change
   git tag v1.0.0-beta.5
   git push origin v1.0.0-beta.5
   ```
5. **User reviews** and executes commands
6. **User confirms** tag creation

**Why:** Releases are critical - require explicit approval

### WARNING: Pushing to Remote
**Process:**
1. AI suggests push commands
2. **User executes** push commands manually
3. AI should NOT auto-push without explicit user request

**Why:** Security control - prevents accidental remote changes

### WARNING: Hotfix Operations
**Process:**
1. AI generates hotfix workflow commands
2. **User reviews** each step
3. **User executes** step by step
4. User confirms each critical operation (tag, push)

**Why:** Hotfixes are high-risk - require careful manual review

---

## Character Encoding Rules

### 7-bit ASCII Requirement
**AI agents MUST use 7-bit ASCII (characters 0-127 only) in all non-markdown files.**

**Critical Rule:** When creating or modifying any code files, scripts, or configuration files, AI agents must:
- [OK] Use only 7-bit ASCII characters
- [OK] Replace any non-ASCII characters with ASCII equivalents
- [X] Never use emoji, Unicode symbols, or multi-byte characters in code/scripts

**Files Affected:**
- All source code files (`.py`, `.js`, `.ts`, `.html`, `.css`, etc.)
- All script files (`.ps1`, `.bat`, `.sh`, etc.)
- All configuration files (`.json`, `.yaml`, `.ini`, etc.)
- Documentation source files (`.rst`, `.txt`, etc.)

**Exception:** Markdown files (`.md`) may contain UTF-8 characters, BUT with PDF compatibility restrictions.

**PDF Compatibility Rule for Markdown:**
- **All markdown files MUST be PDF-compatible** (no emoji or Unicode symbols that break LaTeX/PDF conversion)
- **Use plain text alternatives** instead of emoji:
  - [OK] (checkmark) → `[OK]`, `OK`, or `PASS`
  - [X] (cross mark) → `[X]`, `FAIL`, or `ERROR`
  - WARNING: (warning) → `WARNING:` or `WARN:`
  - * (bullet) → `*` or `-`
  - Major Features: (target) → `Major Features:` or `Features:`
  - Enhancements: (sparkles) → `Enhancements:` or `Improvements:`
  - Bug Fixes: (bug) → `Bug Fixes:`
  - Documentation: (books) → `Documentation:`
  - Technical: (wrench) → `Technical:` or `Technical Improvements:`
  - Statistics: (chart) → `Statistics:` or `Metrics:`
  - Migration: (arrows) → `Migration:` or `Migration Notes:`
  - Deployment: (rocket) → `Deployment:` or `Deployment Notes:`
  - Notes: (memo) → `Notes:` or `Commit History:`
- **Rationale:** LaTeX fonts (e.g., lmroman10-regular) used for PDF conversion do not support emoji characters, causing warnings and formatting issues.

**Common Replacements:**
- ✓ (checkmark) → `[OK]`, `OK`, or `PASS`
- ✗ (cross mark) → `[X]`, `FAIL`, or `ERROR`
- ⚠ (warning) → `WARNING:` or `WARN:`
- • (bullet) → `*` or `-`

**Rationale:** PowerShell, batch files, and many other tools can fail to parse files correctly when multi-byte UTF-8 characters are present, leading to cryptic parsing errors. Additionally, PDF conversion tools require plain text alternatives to emoji.

---

## Commit Message Standards

**Standard:** All commits MUST follow strict Angular Conventional Commits format, regardless of branch.

### Angular Format Structure (Mandatory)
```
<type>(<scope>): <short summary>

<body>

<footer> (optional, only for BREAKING CHANGE)
```

**Requirements:**
- **Type:** One of: feat, fix, docs, style, refactor, perf, test, build, ci, chore
- **Scope:** Optional, lowercase, in parentheses (e.g., `(readme)`, `(dashboard)`)
- **Subject:** Imperative, lowercase, < 50 characters
- **Blank line:** MANDATORY between subject and body
- **Body:** Detailed explanation, wrap at 72 characters, bullet points allowed
- **Footer:** Only for BREAKING CHANGE or issue tracking

### For Feature Branch Commits
- **Must follow Angular format strictly**
- Use appropriate type (feat, fix, docs, refactor, etc.)
- Include body with bullet points describing changes
- Example:
  ```
  feat(dashboard): add user dashboard with widgets

  Implements main dashboard view with widget framework.
  Adds real-time data updates and user preferences.
  
  - Created dashboard view component
  - Implemented widget system
  - Added API integration for live data
  ```

### For Merge Commits to Main
- **Must follow Angular format strictly:**
  ```
  feat(dashboard): add user dashboard with widgets

  Implements main dashboard view with widget framework.
  Adds real-time data updates and user preferences.
  
  - Created dashboard view component
  - Implemented widget system
  - Added API integration for live data
  ```
- **Subject:** User-facing feature description
- **Body:** What the feature does (not implementation details)
- **Format:** Lowercase, imperative, < 50 chars for subject

### For Direct Commits to Main (Rare)
- Follow Angular format strictly
- Use appropriate type (fix, docs, chore)
- Include detailed body for significant changes

---

## Version Management

### How Version.py Works
- `contest_tools/version.py` contains `__version__` and `__git_hash__`
- Pre-commit hook automatically updates `__git_hash__` before each commit
- `__version__` should match most recent git tag (manual update before releases)

### Release Workflow: Creating a New Version Tag

**Purpose:** Ensure version consistency across `version.py`, documentation, and git tags when creating a new release.

**When to Use:** Before creating any version tag (alpha, beta, or release).

#### Step-by-Step Process

**1. Pre-Release Checklist**
- [ ] Verify current branch state (`git status`)
- [ ] Ensure all changes are committed on feature branch
- [ ] Review recent commits to determine appropriate version increment
- [ ] Confirm target version number with user (e.g., `v1.0.0-alpha.3`)

**2. Merge Feature Branch into Master**

a. **Ensure feature branch is committed:**
   ```bash
   git status  # Verify no uncommitted changes
   ```

b. **Checkout master and pull latest:**
   ```bash
   git checkout master
   git pull origin master
   ```

c. **Merge feature branch into master:**
   ```bash
   git merge feature/branch-name
   ```

d. **Resolve any merge conflicts** (if present)

e. **Push merged master:**
   ```bash
   git push origin master
   ```

**Note:** All subsequent steps (version bumping, release notes, tagging) happen on master after the merge is complete.

**3. Update Version References**

AI should update all version references in this order:

a. **Update `contest_tools/version.py`:**
   ```python
   __version__ = "1.0.0-alpha.3"  # Match target tag (without 'v' prefix)
   ```

b. **Update `README.md`:**
   - Line 3: `**Version: 1.0.0-alpha.3**`
   - Verify no other version references exist

c. **Check other documentation files:**
   - Search for version strings: `grep -r "1\.0\.0" Docs/ README.md`
   - Update any hardcoded version references found

**4. Create Release Notes and Update CHANGELOG.md**

a. **Create release notes file:**
   - Location: `ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.3.md`
   - Format: Use previous release notes as template
   - Content: Summary of commits since last tag

b. **Update CHANGELOG.md:**
   - Location: `CHANGELOG.md` (project root, alongside README.md)
   - Add new entry at top (reverse chronological order)
   - Format: Use Keep a Changelog format with link to detailed release notes
   - **Note:** CHANGELOG.md is automatically accessible via the web UI hamburger menu (Help & Documentation > Release Notes)
   - Example:
     ```markdown
     ## [1.0.0-alpha.3] - 2026-01-20
     [Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.3.md)
     
     ### Added
     - Feature X
     ### Changed
     - Enhancement Y
     ### Fixed
     - Bug Z
     ```

c. **Generate commit summary:**
   ```bash
   git log --oneline <last-tag>..HEAD
   ```
   - Organize by category (Features, Enhancements, Bug Fixes, Documentation)
   - Include all significant changes

**5. Commit Version Updates**

a. **Stage all version-related changes:**
   ```bash
   git add contest_tools/version.py README.md ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.3.md CHANGELOG.md
   ```

b. **Create commit:**
   ```bash
   git commit -m "chore(release): bump version to 1.0.0-alpha.3 and add release notes"
   ```
   - Use `chore(release):` type for version bumps
   - Include "bump version" in message
   - Mention release notes and CHANGELOG.md if created

**6. Create and Push Tag**

a. **Create annotated tag:**
   ```bash
   git tag -a v1.0.0-alpha.3 -m "Release v1.0.0-alpha.3

   [Summary of major changes]
   
   [Key features/enhancements]
   "
   ```
   - Use `-a` for annotated tag (recommended)
   - Include meaningful tag message
   - Tag name must match version.py (with 'v' prefix)

b. **Verify tag:**
   ```bash
   git tag -l "v1.0.0-alpha.3"
   git show v1.0.0-alpha.3
   ```

c. **Push commits and tag (user executes):**
   ```bash
   git push origin master          # Push version bump commit
   git push origin v1.0.0-alpha.3  # Push tag
   ```

**7. Post-Release Verification**

a. **Verify version consistency:**
   ```bash
   # Check version.py matches tag
   grep "__version__" contest_tools/version.py
   git describe --tags
   
   # Check README matches
   grep "Version:" README.md
   ```

b. **Verify release notes and CHANGELOG.md exist:**
   ```bash
   ls ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.3.md
   ls CHANGELOG.md
   grep -A 5 "## \[1.0.0-alpha.3\]" CHANGELOG.md  # Verify entry exists
   ```

#### AI Agent Responsibilities

- **AI Can Do:**
  - Merge feature branch into master (after user confirmation)
  - Suggest version number based on commit history
  - Update `version.py` and `README.md`
  - Generate release notes from commit history
  - Update CHANGELOG.md with new release entry
  - Create commit message for version bump
  - Generate tag creation command
  - Verify version consistency

- **User Must:**
  - Confirm feature branch is ready for merge
  - Confirm target version number
  - Review release notes content
  - Execute tag push command
  - Verify final state

#### Version Number Guidelines

- **Alpha versions:** `1.0.0-alpha.X` (e.g., `1.0.0-alpha.3`)
- **Beta versions:** `1.0.0-beta.X` (e.g., `1.0.0-beta.5`)
- **Release candidates:** `1.0.0-rc.X` (e.g., `1.0.0-rc.1`)
- **Releases:** `1.0.0`, `1.1.0`, `2.0.0` (SemVer)

#### Quick Reference Commands

**Regular Release:**
```bash
# Merge feature branch into master (do this first)
git checkout master
git pull origin master
git merge feature/branch-name
git push origin master

# Find last tag
git describe --tags --abbrev=0

# List commits since last tag
git log --oneline $(git describe --tags --abbrev=0)..HEAD

# Verify version consistency
grep -r "1\.0\.0-alpha" contest_tools/version.py README.md ReleaseNotes/ CHANGELOG.md

# Create and push tag (after version updates committed on master)
git tag -a v1.0.0-alpha.3 -m "Release v1.0.0-alpha.3"
git push origin master
git push origin v1.0.0-alpha.3
```

**Hotfix Release:**
```bash
# Create hotfix branch from release tag
git checkout v1.0.0
git checkout -b hotfix/1.0.1-description

# After fix and version bump:
git tag -a v1.0.1 -m "Hotfix v1.0.1"
git push origin v1.0.1

# Backport to master
git checkout master
git pull origin master
git merge hotfix/1.0.1-description
git push origin master
```

### Legacy: Simple Tag Creation (Deprecated)

For quick tags without full release process, see "Before Creating a Tag" section below. However, **full release workflow is recommended** for all version tags.

### Before Creating a Tag (Legacy/Quick Method)
1. **User specifies** target version (e.g., `v1.0.0-beta.5`)
2. **AI suggests** updating `version.py`:
   ```python
   __version__ = "1.0.0-beta.5"
   ```
3. **User confirms** version number
4. **AI generates** commit message:
   ```
   chore: bump version to 1.0.0-beta.5
   ```
5. **User commits** version change
6. **User creates** tag: `git tag v1.0.0-beta.5`
7. **User pushes** tag: `git push origin v1.0.0-beta.5`

**Note:** This method does NOT update README.md or create release notes. Use full Release Workflow for proper releases.

### Hotfix Workflow: Emergency Releases

**Purpose:** Handle critical bugs or security vulnerabilities in released versions when master has moved ahead with new features.

**When to Use:** Critical bug in released version (e.g., `v1.0.0`) but master is at higher version (e.g., `v1.1.0-alpha.1`).

#### Step-by-Step Hotfix Process

**1. Pre-Hotfix Checklist**
- [ ] Identify affected release tag (e.g., `v1.0.0`)
- [ ] Confirm bug severity (critical/security/data corruption)
- [ ] Determine patch version (e.g., `v1.0.0` → `v1.0.1`)

**2. Create Hotfix Branch from Release Tag**

a. **Checkout release tag:**
   ```bash
   git checkout v1.0.0
   ```

b. **Create hotfix branch:**
   ```bash
   git checkout -b hotfix/1.0.1-security-patch
   ```

**3. Fix the Bug**

a. **Make minimal fix:**
   - Focus only on fixing the bug
   - Avoid adding new features
   - Test fix thoroughly

b. **Commit fix:**
   ```bash
   git commit -m "fix(security): resolve authentication bypass"
   ```

**4. Update Version References**

a. **Update `contest_tools/version.py`:**
   ```python
   __version__ = "1.0.1"  # Patch increment from fixed release
   ```

b. **Update `README.md`:**
   - Line 3: `**Version: 1.0.1**`

**5. Create Release Notes and Update CHANGELOG.md**

a. **Create release notes file:**
   - Location: `ReleaseNotes/RELEASE_NOTES_1.0.1.md`
   - Format: Same as regular release notes
   - Content: Focus on bug fix, impact, migration if needed
   - Mark as "Hotfix" or "Security" in title

b. **Update CHANGELOG.md:**
   - Add entry at top with `[HOTFIX]` or `[SECURITY]` prefix
   - Example:
     ```markdown
     ## [1.0.1] - 2026-01-20 [HOTFIX]
     [Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.1.md)
     
     ### Fixed
     - Critical security vulnerability in authentication
     ```

**6. Commit Version Updates**

a. **Stage all version-related changes:**
   ```bash
   git add contest_tools/version.py README.md ReleaseNotes/RELEASE_NOTES_1.0.1.md CHANGELOG.md
   ```

b. **Create commit:**
   ```bash
   git commit -m "chore(release): bump version to 1.0.1 for hotfix"
   ```

**7. Tag and Push Hotfix**

a. **Create annotated tag:**
   ```bash
   git tag -a v1.0.1 -m "Hotfix v1.0.1

   Critical security patch for authentication bypass.
   
   [Summary of fix]
   "
   ```

b. **Push hotfix tag (user executes):**
   ```bash
   git push origin v1.0.1
   ```

**8. Backport to Master**

a. **Checkout master:**
   ```bash
   git checkout master
   git pull origin master
   ```

b. **Merge hotfix branch:**
   ```bash
   git merge hotfix/1.0.1-security-patch
   ```

c. **Resolve conflicts** (if master has diverged significantly)

d. **Push merged master (user executes):**
   ```bash
   git push origin master
   ```

**Note:** Master version remains independent (e.g., `v1.1.0-alpha.1`). The fix is backported and will be included in master's next release.

#### Version Numbering for Hotfixes

- **Patch increment from fixed release:** `1.0.0` → `1.0.1`
- **For pre-releases:** `1.0.0-alpha.3` → `1.0.0-alpha.4`
- **Master version:** Independent of hotfix version (reflects master's development state)

#### AI Agent Responsibilities for Hotfixes

- **AI Can Do:**
  - Generate hotfix workflow commands
  - Update `version.py` and `README.md` for hotfix version
  - Generate release notes and CHANGELOG.md entry
  - Create commit message for version bump
  - Generate tag creation command
  - Generate merge commands for backport

- **User Must:**
  - Confirm hotfix is necessary
  - Confirm target version number
  - Review release notes content
  - Execute tag push command
  - Execute master merge push
  - Verify final state

### Rollback Strategy: Reverting Bad Releases

**Purpose:** Handle situations where a release tag needs to be reverted or patched.

#### When to Rollback

- Release tag contains critical bug
- Security vulnerability discovered after release
- Data corruption issue
- Production outage

#### Rollback Options

**Option 1: Create Patch Release (Recommended)**
1. Follow Hotfix Workflow
2. Create patch version with fix (e.g., `v1.0.0` → `v1.0.1`)
3. Deploy patch immediately

**Option 2: Revert Tag and Create New Release**
1. Create revert commit on master:
   ```bash
   git revert <bad-release-commit>
   ```
2. Follow Regular Release Workflow
3. Create new release (e.g., `v1.0.1`)

**Option 3: Delete and Recreate Tag (Not Recommended)**
- Only if tag hasn't been deployed yet
- Warning: Can cause confusion if tag was already pulled

#### Rollback Process

**1. Identify Bad Release**
- Tag: `v1.0.0` (contains bug)

**2. Determine Strategy**
- If fix is ready: Use Hotfix Workflow (create `v1.0.1`)
- If fix needs development: Revert and create new release

**3. Execute Rollback**
- Follow Hotfix Workflow for immediate fix
- Or revert commit and create new release

**4. Update Documentation**
- Update release notes to document rollback
- Update CHANGELOG.md with rollback entry
- Document reason for rollback

**5. Notify Stakeholders**
- Document rollback in release notes
- Include deployment instructions
- Include migration notes if needed

### Untagged Commits
- Version string will be: `"1.0.0-beta.5-3-gabc1234"` (most recent tag + distance + hash)
- Git hash always included: `"1.0.0-beta.5 (commit abc1234)"`
- This works for bug reports - version + hash = exact code state

---

## Workflow Examples

### Example 1: Feature Development
```
User: "Commit these changes with a message about adding the dashboard"

AI:
1. Generates commit message following strict Angular format:
   ```
   feat(dashboard): add user dashboard with widgets

   Implements main dashboard view with widget framework.
   Adds real-time data updates and user preferences.
   
   - Created dashboard view component
   - Implemented widget system
   - Added API integration for live data
   ```
2. Executes: git commit with properly formatted message (using multiple -m flags or single -m with newlines)
3. Confirms: "Committed to feat/dashboard branch"
```

### Example 2: Merge to Main
```
User: "Merge feat/dashboard into main"

AI:
1. Generates: git checkout main && git pull
2. Generates: git merge --no-ff feat/dashboard
3. Opens editor with merge message:
   "feat(dashboard): add user dashboard with widgets
   
   Implements main dashboard view with widget framework."
4. Waits for user to review/edit and save
5. Confirms: "Merge complete. Ready to push?"
6. User: "Push it"
7. AI suggests: git push origin main
8. User executes manually
```

### Example 3: Creating a Release Tag
```
User: "Tag the next beta release"

AI:
1. Checks recent commits for version bump
2. Suggests: "Based on recent commits, suggest v1.0.0-beta.5"
3. User: "Yes"
4. AI updates version.py __version__ = "1.0.0-beta.5"
5. AI generates: git commit -m "chore: bump version to 1.0.0-beta.5"
6. AI suggests commands:
   git tag v1.0.0-beta.5
   git push origin v1.0.0-beta.5
7. User reviews and executes
```

---

## Error Handling

### If Pre-commit Hook Fails
- AI should explain the error
- Do NOT skip hooks without user permission
- Fix the issue (e.g., update version.py manually) before proceeding

### If Merge Conflicts
- AI should detect conflicts
- AI should suggest resolution steps
- **User must resolve** conflicts manually
- AI can help review conflict resolution

### If Version Mismatch
- AI should warn if `version.py` doesn't match recent tag
- AI should suggest updating version before tagging
- User must confirm version number

---

## Safety Checks

Before any critical operation, AI should:
1. [OK] Confirm current branch (`git branch`)
2. [OK] Show recent commits (`git log --oneline -5`)
3. [OK] Warn if on main branch for direct commits
4. [OK] Suggest creating feature branch if not on one
5. [OK] Verify pre-commit hooks are installed

---

## Technical Debt Tracking

### TECHNICAL_DEBT.md Pattern

**AI agents MUST check `TECHNICAL_DEBT.md` at the start of each session.**

**When TECHNICAL_DEBT.md Exists:**
- AI agent **must** read and review technical debt items at session start
- AI agent **should** prioritize work that addresses technical debt
- AI agent **should** update `TECHNICAL_DEBT.md` as items are completed
- AI agent **should** add new items when technical debt is identified

**File Location:** Repository root (`TECHNICAL_DEBT.md`)

**Purpose:** Track technical debt items, architectural improvements, and known issues that need attention.

**Categories:**
- Architecture & Design Debt
- Validation & Testing Debt
- Code Quality Debt
- Documentation Debt
- Performance Debt
- Known Issues
- Future Enhancements

**Agent Behavior:**
1. **Session Start:** Read `TECHNICAL_DEBT.md` (non-blocking but recommended)
2. **During Work:** Check off items as completed, add new items as discovered
3. **Priority:** Address HIGH priority items when relevant to current task

---

## Session Context & Workflow State

### HANDOVER.md Pattern (Optional)

For complex multi-session workflows, a `HANDOVER.md` file may exist at the repository root to maintain workflow state between agent sessions.

**When HANDOVER.md Exists:**
- AI agent **must** check for `HANDOVER.md` at session start
- AI agent **must** read and incorporate workflow state from `HANDOVER.md`
- AI agent **should** update `HANDOVER.md` as work progresses
- AI agent **should** overwrite `HANDOVER.md` when switching sessions

**When HANDOVER.md Does NOT Exist:**
- AI agent proceeds with standard context (git history, documentation, code, user request)
- AI agent does NOT create `HANDOVER.md` unless explicitly requested
- Standard workflow: User request → Agent analyzes code/docs → Agent performs task

**When to Use HANDOVER.md:**
- [OK] Complex multi-session workflows (e.g., version cleanup, major refactoring)
- [OK] Multi-step processes spanning multiple sessions (test → patch → tag → cleanup)
- [OK] Context that spans multiple sessions (current state, next steps, decisions)

**When NOT to Use HANDOVER.md:**
- [X] Simple bug fixes (agent can analyze code directly)
- [X] Single-session tasks (new features, quick fixes)
- [X] Tasks with sufficient context in code/docs/git history

**Agent Behavior:**
1. **Session Start:** Check for `HANDOVER.md` (non-blocking)
2. **If Found:** Read workflow state, incorporate into context
3. **If Not Found:** Proceed with standard context gathering
4. **During Work:** Update `HANDOVER.md` if it exists and workflow state changes
5. **Session End:** Overwrite `HANDOVER.md` with current state if it exists

**File Location:** Repository root (`HANDOVER.md`)

**Git Treatment:** Committed but overwritten (allows backup in git history while maintaining current state)

---

## File Organization Rules

### Discussion Documents Location

**Purpose:** Standardize location for architectural discussions, design decisions, and planning documents.

**Rule:** All discussion documents, architectural analysis documents, implementation plans, and design decision documents **MUST** be placed in the `DevNotes/` directory.

**Examples of Documents That Belong in DevNotes:**
- Architectural discussion documents (e.g., `COMPONENT_ARCHITECTURE_DISCUSSION.md`)
- Refactoring analysis documents (e.g., `DASHBOARD_REFACTORING_DISCUSSION.md`)
- Implementation planning documents (e.g., `PHASE1_SEQUENCING_DECISION.md`)
- Design decision records
- Technical feasibility studies
- Project planning documents

**Examples of Documents That Do NOT Belong in DevNotes:**
- User-facing documentation (goes in `Docs/`)
- Release notes (goes in `ReleaseNotes/` or `RELEASE_NOTES_*.md` at root)
- Code documentation (goes with code files or `Docs/`)
- README files (typically at directory roots where they belong)

**Agent Behavior:**
- When creating new discussion/planning documents, place them in `DevNotes/`
- When moving existing discussion documents, move them to `DevNotes/`
- Use descriptive filenames (e.g., `COMPONENT_ARCHITECTURE_DISCUSSION.md`, not `discussion.md`)

**Directory Structure:**
```
DevNotes/
  ├── LAQP_Implementation_Plan.md
  ├── DASHBOARD_REFACTORING_DISCUSSION.md
  ├── PHASE1_SEQUENCING_DECISION.md
  ├── COMPONENT_ARCHITECTURE_DISCUSSION.md
  └── ... (other discussion/planning documents)
```

---

## Code Architecture Rules

### CRITICAL: Data Aggregation Layer (DAL) Pattern

**AI agents MUST follow the DAL pattern when implementing or modifying reports.**

**Core Principle:** Reports are visualization/formatting layers. Data processing belongs exclusively in aggregators.

#### Rules for Reports (`contest_tools/reports/`)

1. **DO NOT process raw log data in reports.** Use aggregators from `contest_tools.data_aggregators` instead.

2. **DO NOT create pivot tables, groupby operations, or manual time binning in reports.** All data aggregation belongs in aggregators.

3. **DO NOT manually iterate over logs to extract or transform data.** Use aggregator methods that handle all logs consistently.

4. **DO use `master_time_index` from `LogManager`** when passing time_index parameters to aggregators to ensure alignment across logs.

5. **DO use existing aggregator methods** (e.g., `MatrixAggregator.get_stacked_matrix_data()`, `TimeSeriesAggregator.get_time_series_data()`). If new data structures are needed, extend aggregators with new methods rather than processing data in reports.

#### Why This Matters

- **Time Alignment:** Manual time binning in reports causes misalignment across logs, leading to rendering bugs where only some logs appear correctly.
- **Consistency:** Aggregators ensure all logs are processed identically, preventing data structure mismatches.
- **Maintainability:** Centralized data processing logic is easier to test, debug, and extend.
- **Performance:** Aggregators can be cached and reused across multiple reports.

#### Example: Correct Pattern

```python
# CORRECT: Report uses aggregator
def generate(self, output_path: str, **kwargs):
    # Get master_time_index for alignment
    master_index = None
    if self.logs and hasattr(self.logs[0], '_log_manager_ref'):
        log_manager = self.logs[0]._log_manager_ref
        if log_manager:
            master_index = log_manager.master_time_index
    
    # Use aggregator - do NOT process raw data
    matrix_agg = MatrixAggregator(self.logs)
    matrix_data = matrix_agg.get_stacked_matrix_data(bin_size='60min', time_index=master_index)
    
    # Report only formats/visualizes the pre-processed data
    # ... visualization code using matrix_data ...
```

#### Example: Anti-Pattern (DO NOT DO THIS)

```python
# WRONG: Report manually processes data
def generate(self, output_path: str, **kwargs):
    for log in self.logs:
        df = get_valid_dataframe(log)
        # BAD: Manual pivot tables, time binning, etc. in report
        pivot = df.pivot_table(index='Band', columns='Hour', ...)
        # This causes time misalignment and inconsistent data structures!
```

#### Reference Documentation

For detailed information on the DAL pattern and available aggregators, see:
- `Docs/ProgrammersGuide.md` - Section 2: "The Data Aggregation Layer (DAL)"
- Individual aggregator modules in `contest_tools/data_aggregators/`

---

### CRITICAL: Contest-Specific Plugin Architecture

**AI agents MUST respect contest-specific plugins and calculators as the single source of truth.**

**Core Principle:** "Contest-specific weirdness is implemented in code (plugins/aggregators)"

#### Rules for Plugin Architecture

1. **DO NOT bypass contest-specific plugins or calculators.**
   - If a contest defines a `time_series_calculator` (e.g., `wae_calculator`, `naqp_calculator`), use it as the authoritative source for final scores
   - If a contest defines a `scoring_module` (e.g., `arrl_10_scoring`), respect it for point calculation
   - Do NOT create alternative calculation paths that ignore plugins

2. **DO use plugins as single source of truth.**
   - Score calculators (`time_series_calculator`) are authoritative for final scores and cumulative score arrays
   - Scoring modules (`scoring_module`) are authoritative for QSO point calculation
   - Aggregators should use plugin output when available, not recalculate independently

3. **DO validate architectural compliance before proposing solutions.**
   - Before proposing changes, verify: Does this respect plugin architecture?
   - Before creating aggregators, verify: Should this use an existing plugin?
   - Before modifying scoring, verify: Does this respect contest-specific calculators?

4. **DO add validation warnings if multiple calculation paths exist.**
   - If aggregator calculates independently of plugin, add validation check
   - Warn if plugin and aggregator results differ significantly
   - Use plugin as authoritative source, aggregator as validation/fallback only

#### Architecture Decision Framework

When making changes that affect data calculation or contest-specific logic:

**Step 1: Identify Architecture Requirements**
- Does contest have plugin/calculator defined in JSON?
- What is the authoritative source for this calculation?
- Are there existing patterns to follow?

**Step 2: Verify Compliance**
- Does my solution use the plugin/calculator?
- Am I creating alternative paths that bypass architecture?
- Are multiple calculation paths necessary (with validation)?

**Step 3: Validate Consistency**
- If multiple paths exist, add validation checks using `ArchitectureValidator`
- Use plugin as authoritative source
- Warn if results differ significantly (> 1 point tolerance)

**Step 4: Document Decision**
- Document why this approach respects architecture
- Explain if fallback paths are needed
- Note any validation checks added

#### Example: Correct Pattern (Respects Plugin)

```python
# CORRECT: Using calculator as source of truth
if hasattr(log, 'time_series_score_df') and not log.time_series_score_df.empty:
    # Use plugin output as authoritative
    final_score = int(log.time_series_score_df['score'].iloc[-1])
else:
    # Fallback only if plugin unavailable
    final_score = calculate_fallback_score(log)
```

#### Example: Anti-Pattern (Bypasses Plugin)

```python
# WRONG: Bypassing contest-specific calculator
# ScoreStatsAggregator calculates score independently, ignoring time_series_calculator
final_score = total_points * total_mults  # Doesn't use log.time_series_score_df
# This violates plugin architecture!
```

#### Example: Validation Pattern (Multiple Paths with Checks)

```python
# CORRECT: Multiple paths with validation
from contest_tools.utils.architecture_validator import ArchitectureValidator

validator = ArchitectureValidator()
warnings = validator.validate_scoring_consistency(log)
if warnings:
    for warning in warnings:
        logging.warning(f"Architecture validation: {warning}")

# Use plugin as authoritative source
if hasattr(log, 'time_series_score_df'):
    final_score = int(log.time_series_score_df['score'].iloc[-1])
```

#### Plugin Architecture Checklist

Before implementing scoring/data changes:
- [ ] Does contest have `time_series_calculator` or `scoring_module` defined?
- [ ] Is plugin output available (e.g., `log.time_series_score_df`)?
- [ ] Does my solution use plugin as authoritative source?
- [ ] Am I creating an alternative calculation path that bypasses plugins?
- [ ] Should I add validation to detect inconsistencies?

#### Why This Matters

- **Contest-Specific Logic:** Plugins implement contest-specific scoring rules (e.g., WAE, NAQP, WRTC)
- **Single Source of Truth:** Ensures all reports/dashboards show consistent scores
- **Maintainability:** Contest-specific logic is centralized in plugins, not scattered across aggregators
- **Extensibility:** New contests can add plugins without modifying core aggregators

#### Reference Documentation

- `DevNotes/SCORING_ARCHITECTURE_ANALYSIS.md` - Detailed analysis of scoring architecture
- `contest_tools/score_calculators/` - Score calculator implementations
- `contest_tools/contest_specific_annotations/` - Scoring module implementations
- `contest_tools/utils/architecture_validator.py` - Architecture validation utility

---

## Python Script Execution Rules

### CRITICAL: Use Miniforge Python for Script Execution

**AI agents MUST use the miniforge Python executable when running Python scripts in this environment.**

**Rule:** When executing Python scripts, always use the full path to the miniforge Python executable:
- **Correct:** `C:\Users\mbdev\miniforge3\python.exe script.py`
- **Incorrect:** `python script.py` or `python.exe script.py` (these do not work in this environment)

#### Why This Matters

The default `python` command does not resolve correctly in this environment. Using the miniforge Python path ensures:
- Scripts execute with the correct Python interpreter (Python 3.12.10 from conda-forge)
- All dependencies and modules are properly accessible
- Consistent execution environment across all script runs

#### Examples

**Correct Python Script Execution:**
```powershell
# Running a script from test_code directory
C:\Users\mbdev\miniforge3\python.exe test_code/verify_engine.py

# Running a script with arguments
C:\Users\mbdev\miniforge3\python.exe -m pytest tests/

# Running Python one-liners
C:\Users\mbdev\miniforge3\python.exe -c "import sys; print(sys.version)"

# Running scripts that import project modules
C:\Users\mbdev\miniforge3\python.exe main_cli.py --help
```

**Incorrect Python Script Execution (DO NOT USE):**
```powershell
# These will fail or not work correctly
python script.py
python.exe script.py
py script.py
```

#### Agent Behavior

When an AI agent needs to run a Python script:
1. **Always** use `C:\Users\mbdev\miniforge3\python.exe` as the Python interpreter
2. **Never** use `python`, `python.exe`, or `py` without the full path
3. **Preserve** relative paths for script arguments (e.g., `test_code/script.py`)
4. **Use** full path only for the Python executable itself

#### Note on Activation Scripts

The `C:\Users\mbdev\miniforge3\Scripts\custom_activate.bat` script uses `/K` flag which opens an interactive terminal window. For non-interactive script execution, use the Python executable directly rather than trying to activate the environment first.

---

## Summary

**AI's Role:** Generate, suggest, assist, format
**User's Role:** Review, approve, execute, control
**Balance:** AI efficiency + Human oversight = Safe, consistent workflow
