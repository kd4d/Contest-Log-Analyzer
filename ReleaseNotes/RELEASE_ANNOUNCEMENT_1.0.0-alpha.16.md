# Release Announcement: v1.0.0-alpha.16

**Release Date:** January 30, 2026  
**Version:** `v1.0.0-alpha.16`

---

## Highlights

This release fixes a **performance regression** on the Multiplier Reports dashboard. Opening the dashboard was slow because the app was re-loading a log just to resolve contest labels; it now uses persisted metadata so the dashboard opens quickly when reports are already generated. Contest name can also be taken from the session context when path extraction fails.

---

## What's New

### Multiplier Reports Dashboard: Faster Load
- The Multiplier Reports dashboard no longer parses a log on the "fast path" (when breakdown JSON and dashboard context exist). Contest definition is reused from the JSON definition and session context, so the dashboard should open in a reasonable time.
- If the app can't infer the contest from the report path, it now falls back to the contest name stored in the session, so the multiplier dashboard still works without re-parsing logs.

---

## For More Details

See the [Full Release Notes](RELEASE_NOTES_1.0.0-alpha.16.md) for complete technical details and file changes.

---
