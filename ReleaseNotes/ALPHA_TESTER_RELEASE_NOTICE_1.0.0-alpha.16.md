# Alpha Release Notice: v1.0.0-alpha.16

**Release Date:** January 30, 2026  
**Version:** v1.0.0-alpha.16

---

## What's New

This release adds **QSO and Points** options for rate reports and dashboards, **CQ WPX** public log support, **Points** views for cumulative difference plots, and a **performance fix** for the Multiplier Reports dashboard. Everything is backward compatible; no action required for existing sessions.

### Rate Sheets: QSO and Points

**Points-based contests (e.g. CQ WW, ARRL DX)** now get two rate report variants:

- **Rate Detail tab (QSO Dashboard)**  
  When comparing multiple logs, the "Select Log" dropdown now includes **Comparison (QSOs)** and **Comparison (Points)**. Pick the one you want to view; both use the same hourly comparison layout, one in QSO counts and one in points.

- **Single-log rate sheets**  
  For one-log analyses, rate sheets still appear in the Rate Detail tab. Under the hood they use the same QSO/Points naming so future options stay consistent.

- **Downloaded reports**  
  In your session report folder you'll see files like `rate_sheet_qsos--CALL.txt` and `rate_sheet_points--CALL.txt` (single log), and `rate_sheet_comparison_qsos--CALL1_CALL2.txt` / `rate_sheet_comparison_points--CALL1_CALL2.txt` when comparing logs.

### Cumulative Difference: QSOs and Points

- On **points-based contests**, the **Rate Differential** card (Pairwise Strategy tab) now has a **QSOs | Points** toggle.
- **QSOs** shows the cumulative QSO difference between the two logs (existing behavior).
- **Points** shows the cumulative *points* difference—useful to see when one station pulled ahead in score rather than raw QSO count.
- Try switching between the two and confirm the plot and "Open in new tab" link update correctly.

### CQ WPX Support

- **Public log fetcher**  
  You can now pull CQ WPX logs from the web app. On the home page, choose **CQ WPX** in the contest list, then pick **Year** and **Mode** (CW or SSB). The app fetches from the CQ WPX public log archive; the rest of the flow is the same as for CQ WW.

- **Dashboard for WPX**  
  After analyzing WPX logs, the main dashboard (QSO rates, strategy, rate detail, etc.) works as for other contests. The **Multiplier Reports** card is **hidden** for WPX because WPX uses prefix multipliers, not the same country/zone reports as CQ WW/ARRL DX.

- **Multiplier dashboard link for WPX**  
  If you open the Multiplier Dashboard directly for a WPX session (e.g. from an old bookmark), you'll see a clear **"Not available for this contest"** message instead of an empty or confusing screen.

### Multiplier Reports Dashboard: Faster Load

- **Performance fix**  
  Opening the Multiplier Reports dashboard was previously slow because the app was re-loading a log just to resolve contest labels. That work now uses persisted metadata (contest definition from JSON and dashboard context), so the dashboard should open quickly when reports are already generated.

- **Contest name fallback**  
  If the app can't infer the contest from the report path, it now falls back to the contest name stored in the session, so the multiplier dashboard still works correctly without re-parsing logs.

---

## What This Means for You

- **Existing analyses**  
  Nothing changes for sessions you already ran. Old rate sheet and comparison filenames are still found and displayed.

- **New analyses (points-based contests)**  
  You'll see extra options: Comparison (QSOs) / Comparison (Points) in Rate Detail, and the QSOs | Points toggle in Rate Differential. Downloaded reports will include both `_qsos` and `_points` files when applicable.

- **CQ WPX**  
  If you run WPX, you can use the new contest option to fetch logs and run full analyses; expect no Multiplier Reports card on the main dashboard and a "Not available" page if you hit the multiplier dashboard URL for WPX.

- **Multiplier Reports**  
  The Multiplier Reports dashboard should open much faster; no action required.

**No upgrade steps required.** Refresh the app and run or re-run analyses as usual.

---

## Testing Focus

We'd especially like your feedback on:

1. **Rate Detail tab**  
   For a multi-log, points-based contest: do **Comparison (QSOs)** and **Comparison (Points)** both load and match what you expect? Does the dropdown default and switching between options behave correctly?

2. **Rate Differential (Pairwise Strategy)**  
   For a points-based, two-log comparison: does the **QSOs | Points** toggle update the plot and the "open in new tab" link? Do the two views look consistent (same time range, different metric)?

3. **CQ WPX**  
   If you try WPX: does log fetch and analysis complete? Is the main dashboard useful, and is the absence of the Multiplier Reports card (and the "Not available" message when opening that dashboard) clear and correct?

4. **Multiplier Reports dashboard**  
   Does the Multiplier Reports dashboard open in a reasonable time? Do multiplier labels and tabs still display correctly for your contest?

5. **Single-log and non–points-based contests**  
   Confirm that single-log rate sheets and non–points-based contests (e.g. WPX, or contests without points scoring) still behave as before, with no errors or missing reports.

As always, any odd behavior, wrong numbers, or confusing UI is worth reporting—even if it doesn't fit the list above.

---

## Full Details

For complete technical details and file-level changes, see the [Full Release Notes](RELEASE_NOTES_1.0.0-alpha.16.md).

---

**Thank you for testing!** Your feedback helps make Contest Log Analytics better for everyone.
