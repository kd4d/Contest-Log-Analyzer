# Architecture Roadmap

**Version:** 1.5.0
**Date:** 2025-12-30
**Status:** Active - Phase 4 (Visual Intelligence)

## Phase 1: Core Analytics Engine [COMPLETED]
* **Goal:** Establish reliable parsing, scoring, and basic reporting.
* **Status:** Stable.
* **Key Components:** `ContestLog`, `CabrilloParser`, `ScoreCalculator`.

## Phase 2: The Data Abstraction Layer (DAL) [COMPLETED]
* **Goal:** Decouple reporting logic from Pandas DataFrames.
* **Status:** Implemented (`0.90.x` series).
* **Outcome:** All reports now consume Dict/List structures via `StationMetrics` objects.

## Phase 3: Workflow Architecture Hardening [COMPLETED]
* **Goal:** Eliminate "Context Drift" and "Hallucinations" in AI development.
* **Status:** Implemented (Workflow v5.0.1).
* **Key Features:**
    * **The V-Model:** Strict separation of Analyst (Session A) and Builder (Session B).
    * **The Trinity:** Workflow + Plan + Source required for execution.
    * **Semantic Rigidity:** Strict naming conventions.

## Phase 4: Visual Intelligence & Strategy [ACTIVE]
* **Goal:** Transform static tables into strategic dashboards (Web UI).
* **Current Focus:** The "Multiplier Strategy Board" (Concept 7).
* **Recent Deliverables:**
    * [x] **Integrated Data Grid:** Hybrid visual/numeric rows for Multiplier Dashboard.
    * [x] **Run/S&P Metrics:** Backend logic to track unique multiplier acquisition method.
    * [x] **Verbose Text Reports:** Expanded text report format for auditability.
* **Backlog:**
    * [ ] **CSS Consolidation:** Move inline dashboard styles to `base.css`.
    * [ ] **Report Unification:** Migrate legacy HTML reports to the new "Card/Grid" design language.
    * [ ] **Rate Analysis:** Implement "QS0 Rate vs. Multiplier Rate" graphs.

## Phase 5: Predictive Analytics [PLANNED]
* **Goal:** Real-time scoring projections and "Path to Victory" modeling.
* **Status:** Pending completion of Phase 4.