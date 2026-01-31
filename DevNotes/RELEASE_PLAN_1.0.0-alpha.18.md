# Release Plan: Current State to v1.0.0-alpha.18 on Master

**Target release:** v1.0.0-alpha.18  
**Last tag:** v1.0.0-alpha.17  
**Branch:** feature/1.0.0-alpha.18  

**Reference:** Release workflow in `Docs/AI_AGENT_RULES.md` (drafts on feature branch, commit, merge, bump, tag).

---

## Current State (as of plan creation)

- **Branch:** feature/1.0.0-alpha.18
- **Uncommitted on feature branch:**
  - Modified: `CHANGELOG.md` (draft [1.0.0-alpha.18] entry added)
  - Modified: `Docs/AI_AGENT_RULES.md`, `Docs/VersionManagement.md`, `Docs/AI_AGENT_CHECKLISTS.md` (workflow: drafts on feature branch, then merge, then bump)
  - Untracked: `ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.18.md`, `ReleaseNotes/RELEASE_ANNOUNCEMENT_1.0.0-alpha.18.md`
- **Already committed on feature branch:** All code and analyzer changes for alpha.18 (Rate Chart, Rate Differential, cumulative difference fixes, contest definitions, diagnostic removal, etc.)

---

## Steps to Next Alpha Release on Master

### On feature/1.0.0-alpha.18

**Step 1. Commit workflow documentation updates**

- Stage: `Docs/AI_AGENT_RULES.md`, `Docs/VersionManagement.md`, `Docs/AI_AGENT_CHECKLISTS.md`
- Commit: e.g. `docs(release): release workflow - drafts on feature branch, then merge, then bump`
- Ensures release process changes are part of the release.

**Step 2. Commit draft release notes, announcement, and CHANGELOG**

- Stage: `ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.18.md`, `ReleaseNotes/RELEASE_ANNOUNCEMENT_1.0.0-alpha.18.md`, `CHANGELOG.md`
- Commit: e.g. `docs(release): add draft release notes and CHANGELOG for v1.0.0-alpha.18`
- Verify: `git status` shows no uncommitted changes.

**Step 3. Merge feature branch into master (first commit on master)**

- Checkout master: `git checkout master`
- Pull latest: `git pull origin master`
- Merge: `git merge --no-ff feature/1.0.0-alpha.18 -m "Merge branch 'feature/1.0.0-alpha.18' - Rate Chart, Rate Differential, cumulative difference fixes, release workflow"`
- Push: `git push origin master`

### On master (after merge)

**Step 4. Review and finalize release materials; update version references; Category E in-app help thorough check; VPS update instructions**

- Optional: On master, run `git log --oneline v1.0.0-alpha.17..HEAD` and, if any master-only commits exist, update the merged release notes/announcement.
- Update `contest_tools/version.py`: set `__version__ = "1.0.0-alpha.18"`.
- Update `README.md`: line 3 to `**Version: 1.0.0-alpha.18**`.
- Update Docs per Category A/B/C (`Docs/VersionManagement.md` Section 3):
  - Category A: `UsersGuide.md`, `InstallationGuide.md`, `ReportInterpretationGuide.md` (version, Last Updated, revision history).
  - Category B: `ProgrammersGuide.md`, `PerformanceProfilingGuide.md` (same).
  - Category C: `CallsignLookupAlgorithm.md`, `RunS&PAlgorithm.md`, `WPXPrefixLookup.md` (Compatible with "up to v1.0.0-alpha.18", Last Updated, revision history).
- **Category E (In-App Help):** Thorough check of in-app documentation/help per `Docs/VersionManagement.md` Section 3 Category E. Artifacts: `web_app/analyzer/templates/analyzer/help_dashboard.html`, `help_reports.html`, `help_release_notes.html`, `about.html`. Verify: (1) Every help entry point has up-to-date content; (2) Each template describes current UI (e.g. Rate Differential, Report List, Rate Chart); (3) No stale or removed feature references; (4) In-app links and anchors work. Update templates as needed.
- **VPS update instructions (Step 8):** Create `ReleaseNotes/VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.18.md` with the four or five script commands for the VPS (see Step 8 below). Include in the version bump commit (Step 5).

**Step 5. Commit version updates (second commit on master)**

- Stage all: `contest_tools/version.py`, `README.md`, `ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.18.md`, `ReleaseNotes/RELEASE_ANNOUNCEMENT_1.0.0-alpha.18.md`, `CHANGELOG.md`, `ReleaseNotes/VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.18.md`, the Docs files from Step 4, and any modified in-app help templates (Category E).
- Commit: `chore(release): bump version to 1.0.0-alpha.18 and add release notes`
- Push: `git push origin master`

**Step 6. Create and push tag**

- Create tag: `git tag -a v1.0.0-alpha.18 -m "Release v1.0.0-alpha.18"`
- Push tag: `git push origin v1.0.0-alpha.18`

**Step 7. Post-release verification**

- Confirm `contest_tools/version.py` and `README.md` show 1.0.0-alpha.18.
- Confirm `git describe --tags` shows v1.0.0-alpha.18.
- Confirm ReleaseNotes and CHANGELOG are correct in the repo and (if applicable) in the web UI.

**Step 8. Provide user summary of VPS update steps**

- Create `ReleaseNotes/VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.18.md` with the four or five script commands to run on the VPS server (use a previous release file as template):
  1. `cd` to installation directory (e.g. `/docker/Contest-Log-Analyzer`)
  2. `git fetch --tags origin`
  3. `git checkout v1.0.0-alpha.18`
  4. `docker compose up --build -d`
  5. (Optional) Verify: `docker compose ps` and/or `docker compose logs web`
- Include the file in the version bump commit (Step 5) if created during Step 4, or create and commit it after the tag as a follow-up commit.
- Provide the user with the summary (e.g. link in release announcement to the VPS update instructions file).

---

## Quick command summary (after Steps 1–2 are committed on feature branch)

```powershell
# Step 3: Merge to master
git checkout master
git pull origin master
git merge --no-ff feature/1.0.0-alpha.18 -m "Merge branch 'feature/1.0.0-alpha.18' - Rate Chart, Rate Differential, cumulative difference fixes, release workflow"
git push origin master

# Step 4: Edit version.py, README.md, Docs (Category A/B/C), Category E in-app help thorough check

# Step 5: Version bump commit (include in-app help templates and VPS update instructions if created in Step 4)
git add contest_tools/version.py README.md ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.18.md ReleaseNotes/RELEASE_ANNOUNCEMENT_1.0.0-alpha.18.md CHANGELOG.md ReleaseNotes/VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.18.md
git add Docs/UsersGuide.md Docs/InstallationGuide.md Docs/ReportInterpretationGuide.md
git add Docs/ProgrammersGuide.md Docs/PerformanceProfilingGuide.md
git add Docs/CallsignLookupAlgorithm.md Docs/RunS&PAlgorithm.md Docs/WPXPrefixLookup.md
# If Category E templates were updated: git add web_app/analyzer/templates/analyzer/help_dashboard.html help_reports.html help_release_notes.html about.html
git commit -m "chore(release): bump version to 1.0.0-alpha.18 and add release notes"
git push origin master

# Step 6: Tag
git tag -a v1.0.0-alpha.18 -m "Release v1.0.0-alpha.18"
git push origin v1.0.0-alpha.18
```

---

## Checklist

- [ ] Step 1: Workflow docs committed on feature/1.0.0-alpha.18
- [ ] Step 2: Draft release notes, announcement, CHANGELOG committed on feature/1.0.0-alpha.18
- [ ] Step 3: Merged feature/1.0.0-alpha.18 into master, pushed
- [ ] Step 4: version.py, README, Docs (A/B/C) updated on master; Category E in-app help thorough check done; drafts reviewed/updated if needed
- [ ] Step 5: Version bump commit created and pushed on master
- [ ] Step 6: Tag v1.0.0-alpha.18 created and pushed
- [ ] Step 7: Post-release verification done
- [ ] Step 8: VPS update instructions created (ReleaseNotes/VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.18.md), included in version bump or committed after tag; user provided with summary (link or commands)
