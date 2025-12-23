# Architecture Roadmap

**Version:** 1.5.0
**Date:** 2025-12-20
**Active Release Target:** 0.136.1-Beta

---

## 1. Executive Summary
**Current Status:** **HYBRID ARCHITECTURE (Stabilization In Progress).**
The project has successfully deployed the **Hotfix** (TECH-001) and restored report generation. The **Session Manifest** (ARCH-002) architecture has been partially deployed: the QSO Dashboard (`qso_dashboard`) is fully modernized and reading from `manifest.json`, but the Multiplier Dashboard (`multiplier_dashboard`) currently relies on legacy filesystem scanning. Immediate priority is completing the migration of the Multiplier Dashboard to the Manifest architecture.

---

## 2. Active Development Tracks

### Track A: Reporting Engine Modernization (Visualization)
* **Goal:** Eliminate Matplotlib, standardize branding (3-Line Titles), and enforce "Smart Scoping".
* **Status:**
    * [x] **Phase 1: Presentation Layer** (Branding/Footers) - *Completed.*
    * [x] **Phase 1.1: Smart Scoping** (Redundancy Logic) - *Completed.*
    * [x] **Phase 1.5: Standardization (Plotly)** - *Completed.* (Hotfix Applied).
    * [ ] **Phase 2: Stabilization & Manifest** - *IN PROGRESS.*
        * **Hotfix:** Centralize filename logic. *Completed.*
        * **Manifest (Infrastructure):** `manifest_manager.py` implemented. *Completed.*
        * **Manifest (QSO Dash):** Migrated to Manifest. *Completed.*
        * **Manifest (Mult Dash):** Migration Pending. *IMMEDIATE PRIORITY.*
    * [ ] **Phase 3: Text Report Standardization** - *Pending.*
    * [ ] **Phase 4: Chart Migration** (Butterfly/Propagation) - *Pending.*
    * [ ] **Phase 5: Animation Migration** (WRTC HTML) - *Pending.*

### Track B: Web Dashboard (Architecture)
* **Goal:** Robust, stateless file handling.
* **Status:**
    * [x] **Identity Agnostic Uploads** - *Completed.*
    * [x] **Public Log Archive Fetcher** - *Completed.*
    * [!] **Artifact Discovery** - *HYBRID.*
        * QSO Dashboard: Robust (Manifest-based).
        * Multiplier Dashboard: Fragile (Legacy `os.listdir`).

---

## 3. Feature Backlog & Technical Debt
| ID | Priority | Component | Description | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TECH-001** | **Critical** | `plot_*.py` | **Fix `NameError` Crash.** Restore `is_single_band` logic via utility. | **Completed** |
| **ARCH-002** | **High** | `views.py` | **Session Manifest.** Replace `os.walk` with deterministic JSON manifest. | **In Progress** |
| **DEBT-003** | Medium | `*.py` | **Matplotlib Removal.** Port final static charts to Plotly. | Phase 4 |
| **FEAT-004** | Low | `animations` | **WRTC HTML Animation.** Replace MP4/FFmpeg dependency. | Phase 5 |