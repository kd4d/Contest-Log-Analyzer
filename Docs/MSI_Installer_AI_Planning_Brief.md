# Windows MSI Installer: AI Agent Planning Brief

**Purpose:** Hand this document to a **new AI agent instance** to begin **planning** (not necessarily implementing) a Microsoft Windows Installer (MSI) package for **Contest Log Analyzer** (this repository).

**Status:** Planning and requirements capture only. No MSI has been built as of this brief.

**Related project docs:** `Docs/InstallationGuide.md` (Docker primary; conda/developer paths), `Docs/Contributing.md`, `requirements.txt`, `web_app/manage.py`.

---

## 1. Background: What Was Discussed

### 1.1 User question: Can we ship an MSI?

**Answer (from discussion):** Yes, in principle. MSI is a standard Windows deployment format. Suitability depends on what “the package” means for this project.

**Project reality:** The application is primarily a **Python + Django web application** with supporting CLI/report tooling. Current documented installation favors **Docker**; advanced setup uses **conda** and explicit paths. An MSI is therefore not a trivial “export” but a **packaging and deployment design** exercise.

### 1.2 What an MSI must decide (technical)

An MSI typically **lays down files** and may run **custom actions** (scripts, executables). For this stack, planners must resolve:

| Area | Decision needed |
| :--- | :--- |
| **Python runtime** | Embedded/private Python vs. “bring your own” system Python vs. no Python in MSI (launcher only) |
| **Dependencies** | Pre-vendored site-packages vs. post-install `pip` (network, firewall, reproducibility) |
| **Django app** | How to run: `runserver` (dev-like), **waitress**/other WSGI server, or external IIS |
| **Database** | SQLite path, permissions, `migrate` timing (install vs. first run) |
| **Static assets** | `collectstatic` if applicable |
| **Start/stop model** | Windows **Service**, scheduled task, Start Menu shortcut to a local server script, or browser-only shortcut |
| **Data directories** | Per-user vs. per-machine; alignment with existing env vars (`CONTEST_INPUT_DIR`, `CONTEST_REPORTS_DIR`, etc.) |
| **Upgrade / repair / uninstall** | Product codes, version rules, what to preserve (user DB, reports) |
| **Code signing** | Strongly recommended for SmartScreen and enterprise trust; certificate is **human/org** responsibility |

### 1.3 Alternatives mentioned (not MSI)

- **Zip + README + scripts:** Low ceremony; weak for managed IT.
- **Docker:** Already documented; reproducible; not an MSI.
- **PyInstaller / similar:** Better fit for **desktop** executables; Django as a **service** still needs extra design.

### 1.4 User question: Can an AI agent guide and create the installer?

**Answer (from discussion):**

| Capability | Realistic expectation |
| :--- | :--- |
| **Guidance** | Strong: outline decisions, WiX layout, custom action order, debugging from MSI logs. |
| **Authoring source** | Strong: WiX `.wxs`, PowerShell/batch bootstrap, build docs, CI snippets. |
| **Producing `.msi` on agent’s host** | Often **limited**: cloud sandboxes may lack WiX, signing tools, or Windows-specific test VMs. |
| **Final signed, tested MSI** | Requires **human**: local/CI build, clean-machine testing, code signing with org cert. |

**Model:** Treat the AI as a **technical co-author**; the maintainer runs builds, validates installs, and signs releases.

---

## 2. Goals for the Next Agent (Planning Scope)

The next agent should **not** assume requirements are frozen. It should:

1. **Confirm objectives** with the user (audience: home users vs. enterprise; offline install vs. online; service vs. manual start).
2. **Map the repo** to an installable tree (what must ship, what is generated at install vs. build time).
3. **Propose one or two architecture options** (e.g. “embedded Python + WSGI + Start Menu” vs. “MSI + Docker prerequisite”).
4. **Produce a phased plan** (PoC MSI, then signing, then upgrade story).
5. **Identify risks** (UAC, antivirus, long paths, Django `SECRET_KEY`, migrations).

---

## 3. Ideas for Graphics (For Plans, Docs, or Installer UX)

Use these to make plans and reviews easier for humans and future agents.

### 3.1 Architecture / flow (markdown-friendly)

- **Mermaid `flowchart`:** User runs MSI -> Copy files -> (optional) pip/custom action -> migrate DB -> register service OR create shortcuts.
- **Mermaid `sequenceDiagram`:** Installer -> Custom action script -> Python -> `manage.py migrate` -> exit codes.
- **Deployment diagram:** One box “MSI payload,” one “User data directory,” one “Browser localhost,” arrows labeled with ports (e.g. 8000).

### 3.2 Installer UI (if using WiX UI)

- **Banner / dialog bitmap:** Simple project logo + product name (consistent with any existing branding; avoid embedding version strings that drift from `contest_tools/version.py` policy unless intentional).
- **License / README screen:** Short text pointing to MPL 2.0 and `Docs/UsersGuide.md`.

### 3.3 Documentation figures

- **Folder tree diagram:** Install root vs. `%ProgramData%` or `%LOCALAPPDATA%` for DB and reports (once policy is chosen).
- **Before/after:** “Docker workflow” vs. “MSI workflow” one-pager for `InstallationGuide.md` (future).

### 3.4 Optional: Canvas or external tools

- For interactive or polished mockups, a Cursor Canvas or Figma-style wireframe of the WixUI dialog sequence (welcome -> directory -> install -> finish).

**Note:** Project markdown prefers **PDF-safe** text (see `Docs/Contributing.md`); avoid emoji in files that may be converted to PDF.

---

## 4. Implementation Directions (For Planning, Not Prescriptive)

These are **starting points** for the planning agent to validate against the codebase.

### 4.1 Tooling

- **WiX Toolset v3 or v4:** Common choice for open-source-friendly MSI authoring (`candle`/`light` or `wix build`).
- **Heat** or explicit file lists: Harvest application files; exclude `.git`, `__pycache__`, dev-only paths.
- **Optional:** Advanced Installer / InstallShield if the org standardizes on a commercial tool.

### 4.2 Build integration

- Add an `installer/` or `packaging/msi/` directory in-repo with:
  - `.wxs` sources
  - Build script (PowerShell or batch) invoking WiX
  - Version binding strategy (MSI ProductVersion rules vs. SemVer from tags; see `Docs/VersionManagement.md`)

### 4.3 Runtime packaging strategies (pick one in planning)

- **A. Embedded CPython + venv in install dir:** Largest MSI; most self-contained.
- **B. Download bootstrapper:** Small MSI/exe that fetches Python wheelhouse (network dependency).
- **C. Thin MSI:** Installs shortcuts and docs only; documents prerequisite Python (weakest UX).

### 4.4 Django-specific checklist (planning)

- Entry point script: activate venv, `cd` to `web_app`, run chosen server.
- `SECRET_KEY`: generate on first run, store under user or program data (not world-readable shared location without thought).
- `ALLOWED_HOSTS` / CSRF for localhost if applicable.
- Log file location for support.

### 4.5 Testing matrix (planning output)

- Clean Windows 10 and Windows 11 VMs.
- Standard user vs. admin install (per-user vs. per-machine).
- Upgrade from N-1 MSI.
- Uninstall leaves user data intact (if required).

---

## 5. AI Agent Operating Constraints (This Repository)

Before running commands or editing code, the agent should read:

- `Docs/AI_AGENT_RULES.md` (Python paths, “discuss only” rules, etc.)
- `.cursor/rules/project-mandatory.mdc` if using Cursor (full path to Python for scripts/pytest)

**Git:** If the planning phase produces commits, follow `Docs/Contributing.md` and `Docs/GitWorkflowForCollaborators.md` (Angular commits, feature branches).

---

## 6. Open Questions (Product / Maintainer)

The planning agent should surface answers to:

1. Who is the primary audience for the MSI (general amateurs, contest clubs, locked-down enterprise)?
2. Must the app run **without Docker** and **without manual conda**?
3. Is **offline installation** mandatory?
4. Should the web app run as a **Windows service** or only when the user starts it?
5. Where should **logs, SQLite DB, and reports** live (per-user vs. all-users)?
6. Is **code signing** budget/process available?
7. Should MSI version track **git tags** only, or a separate Windows ProductVersion scheme?

---

## 7. Suggested Deliverables from the Planning Agent

1. **Requirements doc** (or section appended to this file): frozen decisions from section 6.
2. **Architecture one-pager** with one mermaid diagram.
3. **Phased roadmap:** PoC -> internal dogfood -> signed release.
4. **File manifest sketch:** directories and exclusions.
5. **Risk register** (short table).

---

## 8. Document control

| Item | Value |
| :--- | :--- |
| **Created for** | New AI agent instance; MSI implementation planning |
| **Source** | Synthesized from maintainer/AI discussions (MSI feasibility, agent capabilities, graphics ideas) |
| **Implementation** | Not started by this brief |

When implementation begins, consider linking this brief from `Docs/InstallationGuide.md` or a new `packaging/README.md`.
