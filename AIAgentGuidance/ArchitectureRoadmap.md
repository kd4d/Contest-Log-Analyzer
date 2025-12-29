# Architecture Roadmap

**Version:** 2.1.0
**Date:** 2025-12-29

## Phase 1: Core Analysis Engine (Complete)
* **Status:** Stable.
* **Key Components:** `LogManager`, `ContestLog`, `cabrillo_parser.py`.
* **Outcome:** Robust parsing and data normalization for major contests.

## Phase 2: Data Abstraction Layer (DAL) (Complete)
* **Status:** Stable.
* **Key Components:** `TimeSeriesAggregator`, `MatrixAggregator`, `MultiplierStatsAggregator`.
* **Outcome:** Decoupled reporting logic from data storage ("Pure Python Primitives" contract).

## Phase 3: The Web Pathfinder (Active - Critical Pivot)
* **Status:** **IN PROGRESS (High Alert)**.
* **Goal:** Replace "Document-Based" (Iframe) architecture with "Component-Based" (JSON Injection) architecture to solve layout thrashing.
* **Completed:**
    * **Pilot:** `chart_qso_breakdown` and `plot_cumulative_difference` successfully migrated to JSON injection.
    * **Frontend:** `qso_dashboard.html` updated to consume JSON via `fetch()` and `Plotly.newPlot()`.
    * **Fixes:** Layout margins corrected (Backend authority restored); Data serialization hardened (`.tolist()` enforcement).
* **Pending (Immediate):**
    * **Rollout:** Migrate `plot_qso_rate.py`, `plot_point_rate.py`, and `chart_point_contribution.py` to the JSON pattern.
    * **Cleanup:** Refactor `view_report` to consume JSON (Phase 4).

## Phase 4: Full Web Maturity (Planned)
* **Goal:** Eliminate legacy artifacts (`.html` files) and standardize all viewers.
* **Tasks:**
    * Rewrite `view_report` to use the shared Javascript rendering engine.
    * Deprecate HTML file generation in Python.
    * Migrate Animation report (complex) to a dedicated component.