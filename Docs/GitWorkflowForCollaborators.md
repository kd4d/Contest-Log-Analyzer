# Git Workflow for New Collaborators

This guide is a **short path** from clone to merge. It complements the full standards in `Docs/Contributing.md` and the tooling setup in `Docs/GitWorkflowSetup.md`.

---

## 1. One-time setup

1. **Clone** the repository and open a terminal at the repo root.
2. **Install project tooling** (Python env, dependencies) per `Docs/InstallationGuide.md`.
3. **Configure git workflow helpers** (recommended):
   ```batch
   setup.bat --setup-git
   ```
   Or: `tools\setup_git_workflow.bat`  
   Details: `Docs/GitWorkflowSetup.md` (pre-commit hooks, `git mainlog`, etc.).

---

## 2. Core rules (read once)

| Rule | What it means |
| :--- | :--- |
| **Do not commit directly to `main`** | All work happens on a branch. |
| **`main` is stable** | It should always build and represent a trustworthy state. |
| **Git is the record** | No author/version/date blocks in code for history; use commits and tags. |
| **Angular commit messages** | Required for work that lands on `main` (see below). |

Full policy: `Docs/Contributing.md` (sections 1, 4, 5, and 5 Git Workflow Manual).

---

## 3. Feature branches

### Create a branch from updated `main`

```batch
git checkout main
git pull
git checkout -b feat/short-description
```

### Branch name prefixes (recommended)

| Prefix | Use for |
| :--- | :--- |
| `feat/` | New user-visible behavior or capability |
| `fix/` | Bug fixes |
| `docs/` | Documentation-only changes |
| `refactor/` | Internal restructuring, same behavior |
| `test/` | Tests only |
| `chore/` | Tooling, deps, housekeeping |
| `hotfix/` | Emergency fix from a tag (rare; see Contributing) |

Examples: `feat/report-drawer-overlay`, `fix/cq-zone-mapping`, `docs/install-guide-conda`.

### While you work

- Commit **often** on your branch with small, logical steps.
- On your branch, **WIP** messages are OK (e.g. `wip: try layout tweak`).
- Before sharing or merging, **clean up** history if asked (rebase or squash locally is optional; project prefers preserving branch history via `--no-ff` merges).

### See what differs from `main`

After `setup.bat --setup-git`:

```batch
git branchdiff
```

---

## 4. Commit messages (Angular)

Commits that **end up on `main`** should follow the **Angular** style. Same format is ideal for all commits so merges stay consistent.

### Subject line (required)

```text
<type>(<scope>): short imperative summary
```

- **type**: one of `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`
- **scope**: optional short area, e.g. `(web)`, `(reports)`, `(analyzer)`
- **summary**: imperative, lowercase, under ~50 characters (e.g. `add hour slider to spider movie`)

### Body and footer (when needed)

- Leave a **blank line** after the subject.
- **Body**: what changed and why; wrap near 72 columns.
- **Footer**: only for `BREAKING CHANGE:` or issue references (see `Docs/Contributing.md`).

### Examples

```text
feat(web): add spider propagation mockup script

Adds segmented polar wedges and per-hour radial scaling.
Movie page loads hourly HTML via iframes.

```

```text
fix(reports): correct contest hour clip for IARU start
```

```text
docs: add collaborator git workflow guide
```

Full table of types and SemVer impact: `Docs/Contributing.md`, section 5.

---

## 5. Finishing and integrating

### Update your branch with latest `main` (if others merged)

```batch
git checkout feat/your-branch
git fetch origin
git merge main
```

Resolve conflicts, test, then commit the merge (or use rebase if your team agrees).

### Merge into `main` (typical maintainer flow)

From repo policy (`Docs/Contributing.md`):

```batch
git checkout main
git pull
git merge --no-ff feat/your-branch
```

Your editor opens for the **merge commit message**; use Angular style for the merge summary (e.g. `feat(web): spider propagation mockups and iframe movie`).

### If your team uses pull requests

- Open a PR from `feat/...` into `main`.
- Use the same Angular style for the **PR title** (and description for reviewers).
- Maintainer merges with **Create a merge commit** (or equivalent to `--no-ff`) if that matches project practice.

---

## 6. Useful commands (after git setup)

| Command | Purpose |
| :--- | :--- |
| `git mainlog` | Linear-looking history on `main` |
| `git recent` | Last 20 commits on `main` |
| `git branchdiff` | Commits on current branch not in `main` |
| `git status --untracked-files=all` | List every untracked file |

---

## 7. Related documentation

| Document | Contents |
| :--- | :--- |
| `Docs/GitWorkflowSetup.md` | Pre-commit, aliases, `version.py` hash, troubleshooting |
| `Docs/Contributing.md` | Philosophy, encoding, headers, versioning, full git manual, AI git rules |
| `Docs/VersionManagement.md` | Tags, SemVer, releases |
| `Docs/InstallationGuide.md` | Environment and install |

---

## Summary checklist

1. `git checkout main` and `git pull`
2. `git checkout -b feat/...` or `fix/...`
3. Commit with Angular messages when possible
4. `git branchdiff` before merge
5. Merge to `main` with `git merge --no-ff` (or PR + merge commit)
6. Run tests / checks your team expects before pushing or merging
