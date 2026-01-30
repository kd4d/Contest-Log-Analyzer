# Release Notes: v1.0.0-alpha.16

**Release Date:** January 30, 2026  
**Tag:** `v1.0.0-alpha.16`

**Note:** These release notes cover changes on master since `v1.0.0-alpha.15`.

---

## Summary

This release fixes a **regression** where the Multiplier Reports dashboard was slow to open because it re-loaded a log to resolve contest definition for multiplier label formatting. The dashboard now uses persisted metadata (contest definition from JSON and dashboard context) so the fast path does not parse any logs. An optional improvement adds contest name fallback from dashboard context when path extraction fails.

---

## Fixed

### Multiplier Reports Dashboard: Performance Regression
- **Cause:** On the "fast path" (when JSON breakdown and dashboard context were present), the view still created a temporary `LogManager` and called `load_log_batch(log_candidates[:1], ...)` to get the contest definition for `format_multiplier_label`. That parsed one log from disk on every multiplier dashboard load.
- **Fix:** Reuse the contest definition already loaded via `ContestDefinition.from_json(contest_name)` earlier in the same request. Set `contest_def_for_label = contest_def` when on the fast path (no `LogManager`), so no log is loaded for label lookup.
- **Impact:** Multiplier Reports dashboard opens quickly when reports are already generated; no log parsing on the fast path.

---

## Changed

### Contest Name Fallback from Dashboard Context
- When contest name could not be extracted from the report path (e.g. path structure change), the multiplier dashboard now falls back to `dashboard_context.json` (`contest_name` key). Value is normalized (underscores to hyphens, uppercase; CQ-160-* → CQ-160) for `ContestDefinition.from_json()`.
- Ensures contest definition can be resolved without loading a log even when path extraction fails.

---

## Technical Details

### Files Changed
- `web_app/analyzer/views.py` – `multiplier_dashboard`: remove log-load branch for `contest_def_for_label`; use existing `contest_def` on fast path. Add contest name fallback from `dashboard_ctx.get('contest_name')` with normalization.

---

## Known Issues

None in this release.

---

## Migration Notes

No migration required. Existing sessions and reports continue to work; the multiplier dashboard simply loads faster when using the fast path.

---

## Documentation

- Updated version references across documentation to v1.0.0-alpha.16.

---
