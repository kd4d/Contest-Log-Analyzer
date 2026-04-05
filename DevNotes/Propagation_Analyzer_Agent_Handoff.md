# Propagation Analyzer – Discussion Summary (Agent Handoff)

This document summarizes design discussions for adding a **propagation analyzer** to Contest Log Analytics. It is intended to onboard a new AI or developer session without re-reading the full thread.

## Goal

Add a capability that is **not a contest score run**: analyze **propagation / band openings** from:

- **One or more Cabrillo logs**, and/or  
- **One or more RBN (Reverse Beacon Network) raw CSV files** (e.g. from [RBN raw data](https://www.reversebeacon.net/raw_data/)), possibly zipped and large (often far beyond Excel row limits).

The feature should reuse **log upload** and **public log fetch** patterns where applicable, and produce **tabular and graphical** views of propagation-oriented data.

## Core data semantics

### Combining multiple Cabrillo logs

- Logs may have **different sent callsigns** (`CALLSIGN:` / `MyCall` per file). The existing multi-log path must support combining them for propagation views (unlike contest scoring, which cares about per-station score).
- **Dupe checking** for this mode should be **extended** so a duplicate is defined with respect to **both** the transmitting station and the contacted station (conceptually `(MyCall, Call, Band, Mode)` and time bucket as needed), not only the worked `Call` as in today’s contest dupe logic inside a single log.

### RBN CSV

- Treat as a **separate ingest path** with a dedicated parser mapping RBN columns to an internal schema compatible with propagation aggregates (timestamp, frequency/band, mode, spotted call, skimmer/reporter identity, SNR, etc.). **Exact column headers** should be verified against a sample file from the archive during implementation.

### Geography (cty.dat)

- Reuse **`CtyLookup`** ([`contest_tools/core_annotations/get_cty.py`](contest_tools/core_annotations/get_cty.py)) and **`process_dataframe_for_cty_data`** patterns so **Call** (and where relevant **MyCall**) resolve to DXCC / continent / zones for maps and continent breakdowns.
- **`CtyManager`** continues to resolve which `CTY.DAT` to use (or custom upload), consistent with the main app.

## Architectural touchpoints (existing code)

| Area | Role |
|------|------|
| [`contest_tools/cabrillo_parser.py`](contest_tools/cabrillo_parser.py) | `parse_qso_common_fields()` extracts HF/VHF QSO common fields; full QSO lines need contest-specific **exchange** rules today. |
| [`contest_tools/contest_log.py`](contest_tools/contest_log.py) | `_check_dupes()` uses `dupe_check_scope` and `(Call, Mode)` per band (or all-band call set)—**not** MyCall-aware; propagation will need a **separate or extended** rule for combined logs. |
| [`contest_tools/log_manager.py`](contest_tools/log_manager.py) | Batch validation: **unique header callsigns**, **same CONTEST name**, **same year**, **same event id** across files. Propagation workflows may need **relaxed or alternate** validation (open decision). |
| [`contest_tools/data_aggregators/propagation_aggregator.py`](contest_tools/data_aggregators/propagation_aggregator.py) | Existing **WRTC** hourly propagation-by-continent aggregation: `MyCall → Mode → Band → Continent → count` for one selected hour—useful precedent for **nested JSON** feeding charts. |
| [`contest_tools/report_generator.py`](contest_tools/report_generator.py) / reports registry | New propagation reports would register similarly to other reports, with contest definition `included_reports` / `excluded_reports` as appropriate. |

## Methods to display propagation data (discussion-level)

These are candidate **UI + data** patterns to discuss and prioritize—not a committed backlog.

### Tabular

- **Time-binned tables**: rows = hour (or finer), columns = band or mode; cells = QSO count, spot count, or unique calls.
- **Path / entity tables**: counts or rates by **continent**, **DXCC**, or **prefix** for sent vs received side (depending on Cabrillo vs RBN).
- **RBN-specific**: SNR quantiles, spot counts per skimmer, per spotted station.

### Graphical

- **Heatmaps**: time (x) × band (y), intensity = activity or opening strength (from Cabrillo QSO density or RBN spot density).
- **Hourly continent snapshot**: same spirit as current WRTC propagation report—**stacked or grouped bars** by continent and band for a chosen hour or animated over hours using `master_time_index`-style alignment.
- **Line charts**: cumulative spots or QSOs over time; rates (QSOs or spots per hour).
- **Maps** (if lat/lon available from CTY): optional **great-circle** or simplified geographic views; treat as stretch if scope is tight.

### Implementation note

- **Large RBN files**: require **chunked reads** (e.g. pandas `read_csv` in chunks) or similar; avoid loading full days into memory without streaming.

## Open decisions (for product / next agent)

1. **Cabrillo strictness**: Require a **dedicated `CONTEST:` tag** and one flexible parser for propagation-only logs, vs **relax** batch rules to allow mixed contest headers and normalize to common fields only. (User choice was not finalized in-thread.)
2. **Entry point**: Dedicated **Propagation Analyzer** page/flow vs a **mode toggle** on the existing upload screen.
3. **Mixed inputs in one session**: Allow **both** RBN CSV and Cabrillo in one combined dataset vs **separate** modes for v1.
4. **Exact dupe rule**: Confirm time granularity (e.g. same calendar minute vs full datetime) for `(MyCall, Call, Band, Mode)`.

## Suggested first implementation slice

1. Internal **schema** for “propagation events” (unified from Cabrillo rows and RBN rows).  
2. **Cabrillo path**: minimal contest definition + parser that reliably fills time, band, mode, MyCall, Call; **combined-log** dupe pass after `concat`.  
3. **RBN path**: parser + chunking + same schema.  
4. One **table** + one **chart** (e.g. heatmap or hourly bars) wired through the existing session/report pipeline.

## References

- RBN raw downloads: `https://www.reversebeacon.net/raw_data/`  
- Programmers’ guide sections on **custom dupe checkers** and report hooks: [`Docs/ProgrammersGuide.md`](Docs/ProgrammersGuide.md) (custom dupe execution order is documented there).

---

*Generated for agent continuity; update this file as decisions are locked.*
