Here is the finalized Architectural Decision Record and Roadmap, summarizing our discussion and defining the path to the Beta release.

---

# Architectural Decision Record: The "HTML-First" Strategy

**Date:** 2025-12-30
**Status:** Approved for Execution
**Scope:** Contest Log Analytics (CLA) - Beta Release

## 1. Executive Summary

We have resolved a critical architectural conflict between "Visual Fidelity" and "Server Complexity." Previous attempts to replicate complex dashboard widgets (specifically the Multiplier "Integrated Data Grid") using server-side Python libraries failed to match the quality of the HTML/CSS implementation.

**The Decision:** We are shifting from a **Server-Side Generation** model to a **Client-Side Capture** model.

* **Philosophy:** The browser-rendered HTML dashboard is the "Master Source of Truth."
* **Execution:** We will leverage the user's browser engine to render visuals and generate static images on-demand, eliminating the need for heavy server-side infrastructure (like Headless Chrome).

---

## 2. The "Twin Context" Architecture

To support both online users and offline (air-gapped) analysis, we have defined two distinct execution contexts for the same report artifacts.

### Context A: The Live Dashboard (Online/Server)

* **Environment:** The user is connected to the Django server.
* **Asset Loading:** The dashboard templates **link** to static assets (e.g., `<script src="/static/js/html2canvas.js">`).
* **Benefit:** Efficient caching; prevents bloating the page load with redundant code.

### Context B: The Downloaded Artifact (Offline/Air-Gapped)

* **Environment:** The user downloads a ZIP file and opens a report (`.html`) on a machine with no internet or server connection.
* **Asset Loading:** The report generators (Python) **inline** (embed) the necessary JavaScript libraries directly into the HTML file during creation.
* **Benefit:** The file is 100% self-contained. "Capture" buttons and interactive charts function perfectly without external dependencies.

---

## 3. Component Strategy: Closing the "Capture Gap"

We identified a functional gap between Plotly-based charts and HTML-based widgets regarding image export.

### A. Charts (Rate Sheets, Difference Plots, Animation)

* **Technology:** **Plotly.js** (Client-side vector rendering).
* **Download Mechanism:** We rely on Plotly's native **"Camera Icon"** (Download plot as a png) located in the interactive modebar.
* **Action:** No custom buttons or code required.

### B. Widgets (The Multiplier Grid)

* **Technology:** **Django Templates + CSS Grid** (Concept 7).
* **The Gap:** This is raw HTML; it has no built-in "save as image" feature.
* **The Solution:** We will inject **`html2canvas.js`**.
* **Download Mechanism:** We will add a custom **"Capture Image"** button to the widget header. When clicked, the browser snapshots the DOM element and downloads a PNG.
* **Scope:** This logic applies *only* to the Multiplier Breakdown widget.

---

## 4. Deliverable Definition (The Bulk Download ZIP)

The contents of the "Download All" ZIP file are strictly defined to minimize redundancy while maintaining auditability.

| Artifact Type | Format | Status | Notes |
| --- | --- | --- | --- |
| **Text Reports** | `.txt` | **Included** | The primary audit trail and data source. |
| **Interactive Reports** | `.html` | **Included** | Self-contained Plotly files (Rates, Diffs, Animation). |
| **Visual Widgets** | `.html` | **Included** | The standalone Multiplier Grid report. |
| **Widget Image** | `.png` | **Excluded** | Users generate this on-demand via the "Capture" button. |
| **Legacy Visuals** | `.png` | **Transitional** | Legacy reports (WRTC) will still appear until refactored. |

---

## 5. Technical Debt & Scope Boundaries

To accelerate the Beta release, we explicitly accept the following constraints:

1. **Mobile Support:** **Out of Scope.** The data density (3-column comparison) targets desktop/tablet viewports. No responsive stacking logic will be implemented.
2. **Legacy Dependencies:** **Frozen.** `kaleido` and `ffmpeg` remain in the container to support un-ported legacy reports (WRTC), but no new features will use them.
3. **Contest Support:** **CQ WW Only.** Other contests are supported via "Bulk Download" but may not render correctly in the interactive dashboard until specific strategies are built.
4. **CSS Fragmentation:** **Accepted.** Styles for the Multiplier Dashboard remain in the template for now. Consolidation into `styles.css` is a post-Beta task.

---

## 6. Execution Plan

### Phase 1: Immediate Beta Readiness (The Next Session)

1. **Asset Integration:** Add `html2canvas.js` to the project's `static/js/` directory.
2. **Dashboard Update:** Modify `multiplier_dashboard.html` to include the library and the "Capture" button logic.
3. **Generator Update:** Modify `html_multiplier_breakdown.py` to **inline** the JS library for the offline version.

### Phase 2: Follow-On Work (Post-Beta)

1. **Debt Paydown:** Remove `kaleido` and `ffmpeg` dependencies; port WRTC reports to Plotly.
2. **Contest Expansion:** Create `DashboardStrategy` classes for NAQP and ARRL DX.
3. **UI Polish:** Consolidate CSS and standardize "Card" layouts across all reports.

---

**Next Action:** I will issue the standardized prompt for **Generate Builder Execution Kit**.

Generate Builder Execution Kit