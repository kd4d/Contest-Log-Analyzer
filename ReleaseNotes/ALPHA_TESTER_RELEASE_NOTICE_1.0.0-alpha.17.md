# Alpha Release Notice: v1.0.0-alpha.17

**Release Date:** January 30, 2026  
**Version:** v1.0.0-alpha.17

---

## What's New

This release adds a **Report List** (pull-out drawer) on the main, QSO, and multiplier dashboards. You can open a list of all generated reports from a single control and open any report in the full-screen viewer without hunting for popout buttons. Everything is backward compatible; no action required for existing sessions.

### Report List (Pull-Out Drawer)

- **Where:** On the **left edge** of the screen (main dashboard, QSO dashboard, and multiplier dashboard), **halfway down**, you'll see a small **pull-out arrow** (chevron). Click it to open the report list.
- **What you see:** A sidebar with a hierarchical list of reports, grouped into categories (Single Log Reports, Comparison Reports, Multiplier Reports, QSO / Contest-wide, Miscellaneous, and Bulk Actions). Each report is shown by its **actual filename** (e.g. `rate_sheet_qsos--k3lr`, `qso_rate_plots_20m--k3lr_w3lpl`), so callsign and band info are visible when they're in the filename.
- **What it does:** Click any report to open it in the same full-screen overlay you get from the "popout" buttons on the dashboards. The drawer closes after you pick a report. Use the search box to filter the list, or collapse/expand categories. Press **Escape** or click outside the sidebar to close it.
- **Download All:** The "Bulk Actions" section includes "Download All (.zip)". Clicking it closes the drawer and scrolls to the main "Download All Reports" button so you can trigger the ZIP download as before.

---

## What This Means for You

- **Existing analyses**  
  Nothing changes for sessions you already ran. The new drawer is an additional way to open reports; all existing popout links and buttons still work.

- **Finding reports**  
  If you have many reports (e.g. multiple bands, multiple logs), the drawer gives you one place to see the full list (same as what's in the ZIP) and open any report with one click.

- **No upgrade steps required.** Refresh the app and run or re-run analyses as usual.

---

## Testing Focus

We'd especially like your feedback on:

1. **Discoverability**  
   Do you notice the pull-out arrow on the left? Is its position (halfway down the left edge) easy to find without covering other controls?

2. **Report list**  
   Does the list match what you expect (same reports as in the ZIP)? Are the filename-based labels clear enough to pick the right report (e.g. band/callsign when present)?

3. **Opening reports**  
   When you click a report in the drawer, does it open in the full-screen overlay correctly? Does the drawer close and the correct report show as "active" in the list when you reopen it?

4. **Search and collapse**  
   Does the search filter work as expected? Do category collapse/expand and close (X, scrim, Escape) behave correctly?

5. **Download All**  
   When you click "Download All (.zip)" in the drawer, does it close and focus the main Download All button as intended?

As always, any odd behavior, wrong numbers, or confusing UI is worth reporting—even if it doesn't fit the list above.

---

## Full Details

For complete technical details and file-level changes, see the [Full Release Notes](RELEASE_NOTES_1.0.0-alpha.17.md).

---

**Thank you for testing!** Your feedback helps make Contest Log Analytics better for everyone.
