# Architecture Roadmap

**Version:** 1.4.0
**Date:** 2025-12-20
**Active Release Target:** 0.133.0-Beta

---

## 1. Executive Summary
**Current Status:** **CRITICAL STABILIZATION REQUIRED.**
The project is mid-transition in a major "Visualization Standardization" overhaul. Phase 1.5 (Standardization) was partially executed but introduced a regression (`NameError` crash) in the Plotly reporting engine. The immediate priority is applying the **Hotfix** to restore report generation, followed by implementing the **Session Manifest** architecture to decouple the Web Dashboard from filename predictions (fixing 404 errors).

---

## 2. Active Development Tracks

### Track A: Reporting Engine Modernization (Visualization)
* **Goal:** Eliminate Matplotlib, standardize branding (3-Line Titles), and enforce "Smart Scoping".
* **Status:**
    * [x] **Phase 1: Presentation Layer** (Branding/Footers) - *Completed.*
    * [x] **Phase 1.1: Smart Scoping** (Redundancy Logic) - *Completed.*
    * [!] **Phase 1.5: Standardization (Plotly)** - *REGRESSED.*
        * *Issue:* Refactoring removed `is_single_band` variable needed for filename generation.
        * *Result:* Reports crash on generation. 404s in Dashboard.
    * [ ] **Phase 2: Stabilization & Manifest** - *IMMEDIATE PRIORITY.*
        * **Hotfix:** Centralize filename logic in `_report_utils.build_filename`.
        * **Manifest:** Implement `manifest_manager.py` to index artifacts and prevent 404s.
    * [ ] **Phase 3: Text Report Standardization** - *Pending.*
    * [ ] **Phase 4: Chart Migration** (Butterfly/Propagation) - *Pending.*
    * [ ] **Phase 5: Animation Migration** (WRTC HTML) - *Pending.*

### Track B: Web Dashboard (Architecture)
* **Goal:** Robust, stateless file handling.
* **Status:**
    * [x] **Identity Agnostic Uploads** - *Completed.*
    * [x] **Public Log Archive Fetcher** - *Completed.*
    * [!] **Artifact Discovery** - *FRAGILE.* Currently relies on `os.walk` and filename prediction. Must move to **Session Manifest** (Track A, Phase 2).

---

## 3. Feature Backlog & Technical Debt
| ID | Priority | Component | Description | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TECH-001** | **Critical** | `plot_*.py` | **Fix `NameError` Crash.** Restore `is_single_band` logic via utility. | **Ready** |
| **ARCH-002** | **High** | `views.py` | **Session Manifest.** Replace `os.walk` with deterministic JSON manifest. | **Planned** |
| **DEBT-003** | Medium | `*.py` | **Matplotlib Removal.** Port final static charts to Plotly. | Phase 4 |
| **FEAT-004** | Low | `animations` | **WRTC HTML Animation.** Replace MP4/FFmpeg dependency. | Phase 5 |