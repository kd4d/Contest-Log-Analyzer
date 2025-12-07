# Architecture Roadmap: The Unified Engine Migration

**Version:** 1.6.0 (Draft)
**Date:** 2025-12-06
**Status:** Active - Strategic Re-sequencing

---

## 1. The Strategic Vision
**Goal:** Create a single analysis engine that powers both a Command-Line Interface (CLI) and a future Web Interface (Django).
**Core Constraint:** "Write Once, Render Everywhere." Logic must not be duplicated between CLI and Web.

## 2. Architectural Decision Records (ADRs)

### ADR-001: Data Abstraction Layer (DAL)
* **Decision:** All business logic must be extracted into `data_aggregators/`.
* **Constraint:** Aggregators must return **Pure Python Primitives**.

### ADR-002: Unified Visualization (Plotly + Jinja2)
* **Decision:** Replace Matplotlib with **Plotly**. Use **Jinja2** for HTML generation.

### ADR-007: Shared Presentation Layer [NEW]
* **Decision:** The Django Web App must NOT have its own template directory.
* **Mechanism:** It must point to the existing `contest_tools/templates`.
* **Reason:** Ensures CLI HTML reports and Web Views are bit-for-bit identical.

---

## 3. Master Transition Timeline

### **Phase 1: Data Decoupling (COMPLETE)**
* **Status:** Complete. DAL is operational.

### **Phase 1.5: Stabilization (IN PROGRESS)**
* **Goal:** Synchronize documentation and fix "Phantom Dependencies."
* **Critical Task:** Remove `celery` and `redis` from `InstallationGuide.md` (Detected as unused).
* **Critical Task:** Remove deprecated `multipliers_by_hour` from `ReportInterpretationGuide.md`.

### **Phase 2: Visualization Standardization (PRIORITY)**
* **Goal:** Replace Matplotlib with Plotly/Jinja2.
* **Constraint:** Must be completed BEFORE Web Foundation to ensure charts work in browsers.
* **Tasks:**
    * [ ] Create `plotly_style_manager.py`.
    * [ ] Convert `chart_point_contribution.py` (Tracer Bullet).
    * [ ] Convert remaining plots.

### **Phase 3: The Web Foundation (Simplified)**
* **Goal:** Initialize Django *Synchronously*.
* **Constraint:** **NO Celery/Redis yet.** The initial deployment must be a simple monolithic app to reduce complexity.
* **Tasks:**
    * Initialize Django Project.
    * Mount `contest_tools` as an app.
    * Wire up Views to Aggregators.

### **Phase 4: Advanced Features**
* **Goal:** Async Processing & Persistence.
* **Tasks:**
    * Introduce Celery/Redis (Only if processing time > 30s).
    * User Authentication.