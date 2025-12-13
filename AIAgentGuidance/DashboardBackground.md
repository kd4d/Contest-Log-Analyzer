Here is a detailed breakdown of the strategic, architectural, and user experience decisions that culminated in the current `mockup_dashboard.html` prototype.

### 1. The Strategic Pivot: "Strategy First"
The initial roadmap called for building log fetchers (Phase 4), but we halted that to prioritize the **Analytics Refactor**.
* **The Core Insight:** In competitive contesting, score separation at the top tier often comes from *how* stations operate (Run vs. Search & Pounce), not just *what* they work.
* **The Decision:** We shifted the UI focus from a simple "Score Summary" to a **"Strategy Board."** Instead of burying operating metrics in sub-reports, we elevated **"Run %"** and **"Run QSOs"** to the primary table. This allows a user to instantly see *style* differences (e.g., "Station A won by maintaining a 75% Run rate") without clicking anything.

### 2. The Interaction Model: "The Arena" vs. "The Cockpit"
We explicitly rejected a traditional "Dashboard" design (gauges, sparklines, widgets) in favor of a **"Top-Down" Hierarchy**.
* **The Problem:** Comparison involves dense data. Trying to show rate graphs for three different logs simultaneously on one screen creates cognitive overload.
* **The Solution:**
    1.  **The Arena (Top Table):** A high-level comparative scalar view. It answers "Who won?" and "What was their strategy?"
    2.  **The War Room (The Triptych):** Three specific entry points for deep-dive investigation.
* **Why this works:** It respects the user's attention. Users typically scan the scalars to form a hypothesis (e.g., "Did K1LZ win on rate or multipliers?"), then click a specific report to verify it.

### 3. The Drill-Down Architecture (The Triptych)
The middle section of the mockup groups analysis into three distinct "Cards," replacing a generic list of files.
* **Hourly Breakdown (Animation):** Answers "Where did the flow go?" regarding geography and time.
* **QSO Reports (Plots):** Answers "Who held the frequency?" regarding rate and dominance.
* **Multiplier Reports (Text):** Answers "Did I miss the easy ones?" regarding efficiency.
* **Labeling Refinement:** We moved from abstract labels ("Flow & Time") to concrete, descriptive labels (**"Hourly Breakdown"**, **"QSO Reports"**, **"Multiplier Reports"**) at your specific request to ensure clarity for end-users.

### 4. The Technical Enabler: Session-Scoped Persistence
The most critical backend decision supporting this frontend was the move from **Ephemeral I/O** to **Session-Scoped Persistence**.
* **The Constraint:** The original "Zero Persistence" model deleted files immediately after generation. This meant thumbnails and links in the dashboard would point to non-existent files (404 Errors).
* **The Fix:** We adopted a session-based storage model (`media/sessions/<key>/`) with a "Lazy Cleanup" policy. This ensures that when a user clicks "Hourly Breakdown," the interactive HTML animation is actually there to be served.

### 5. Visual & UX Tactics
* **Thumbnails vs. Icons:** We acknowledged that generating real image thumbnails for text files is technically expensive (requires Selenium/Pillow). We compromised by using **Bootstrap Icons** as semantic placeholders (`bi-film`, `bi-table`) while allowing for a real image thumbnail for the plots (`qso_rate_plots_all.png`).
* **New Tab Navigation:** We decided that complex interactive reports (like the Plotly animation) deserve maximum screen real estate. Therefore, all drill-down links use `target="_blank"` to open in a new tab rather than an iFrame or modal.

### Summary
The `mockup_dashboard.html` is not just a layout; it is the visual manifestation of the **"Strategy First"** doctrine. It prioritizes comparative scalars to frame the narrative, then uses persistent session storage to deliver rich, interactive deep-dives on demand.