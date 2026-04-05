# Embedded: scripts/download_rbn_data.py

```python
#!/usr/bin/env python3
# scripts/download_rbn_data.py
#
# Download Reverse Beacon Network daily ZIPs (CSV inside) from data.reversebeacon.net,
# optionally filter by skimmer (callsign), spotted station (dx), CW, UTC window, and write a combined CSV.
#
# RBN: callsign = skimmer; dx = station spotted. For GR2HQ as the heard station use --dx GR2HQ (not --skimmer).

from __future__ import annotations

import argparse
import logging
import sys
import zipfile
from pathlib import Path
from typing import List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd

RBN_ZIP_BASE = "https://data.reversebeacon.net/rbn_history"
DEFAULT_DATES = ["20250712", "20250713"]
USER_AGENT = "ContestLogAnalyzer-RBN-Downloader/1.0"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def zip_url(yyyymmdd: str) -> str:
    return f"{RBN_ZIP_BASE}/{yyyymmdd}.zip"


def download_file(url: str, dest: Path, timeout: int = 120) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": USER_AGENT})
    logger.info("Downloading %s -> %s", url, dest)
    with urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    dest.write_bytes(data)
    logger.info("Saved %s bytes", len(data))


def find_csv_name(zf: zipfile.ZipFile) -> str:
    names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
    if not names:
        raise ValueError(f"No CSV in zip: {zf.namelist()[:10]}...")
    if len(names) > 1:
        logger.warning("Multiple CSVs, using first: %s", names)
    return names[0]


def filter_chunk(
    df: pd.DataFrame,
    skimmer: Optional[str],
    dx_spot: Optional[str],
    cw_only: bool,
    time_start: Optional[pd.Timestamp],
    time_end: Optional[pd.Timestamp],
) -> pd.DataFrame:
    if skimmer:
        col = "callsign" if "callsign" in df.columns else None
        if not col:
            raise KeyError("Expected column 'callsign' for skimmer filter")
        mask = df[col].astype(str).str.upper().str.strip() == skimmer.upper().strip()
        df = df.loc[mask].copy()
    if dx_spot:
        col = "dx" if "dx" in df.columns else None
        if not col:
            raise KeyError("Expected column 'dx' for spotted-station filter")
        mask = df[col].astype(str).str.upper().str.strip() == dx_spot.upper().strip()
        df = df.loc[mask].copy()
    if cw_only and "tx_mode" in df.columns:
        df = df.loc[df["tx_mode"].astype(str).str.upper().str.strip() == "CW"].copy()
    elif cw_only:
        logger.warning("No tx_mode column; cw-only filter skipped for this chunk")

    if time_start is not None or time_end is not None:
        date_col = "date" if "date" in df.columns else None
        if not date_col:
            logger.warning("No date column; time window filter skipped")
        else:
            t = pd.to_datetime(df[date_col], utc=True, errors="coerce")
            if time_start is not None:
                df = df.loc[t >= time_start].copy()
                t = pd.to_datetime(df[date_col], utc=True, errors="coerce")
            if time_end is not None:
                df = df.loc[t <= time_end].copy()
    return df


def process_one_zip(
    zip_path: Path,
    skimmer: Optional[str],
    dx_spot: Optional[str],
    cw_only: bool,
    time_start: Optional[pd.Timestamp],
    time_end: Optional[pd.Timestamp],
    chunksize: int,
) -> pd.DataFrame:
    parts: List[pd.DataFrame] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        inner = find_csv_name(zf)
        with zf.open(inner) as raw:
            head = raw.read(8000).decode("utf-8", errors="replace")
            raw.seek(0)
            sep = "," if head.count(",") >= head.count(";") else ";"
            kw = dict(sep=sep, chunksize=chunksize, low_memory=False)
            try:
                reader = pd.read_csv(raw, on_bad_lines="warn", **kw)
            except TypeError:
                raw.seek(0)
                reader = pd.read_csv(raw, error_bad_lines=False, warn_bad_lines=True, **kw)
            for chunk in reader:
                f = filter_chunk(chunk, skimmer, dx_spot, cw_only, time_start, time_end)
                if not f.empty:
                    parts.append(f)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def main() -> None:
    p = argparse.ArgumentParser(description="Download RBN daily ZIPs and optional filtered CSV.")
    p.add_argument(
        "--dates",
        type=str,
        default=",".join(DEFAULT_DATES),
        help="Comma-separated YYYYMMDD (default: 20250712,20250713)",
    )
    p.add_argument(
        "--skimmer",
        type=str,
        default=None,
        help="Skimmer callsign (RBN column: callsign). Optional.",
    )
    p.add_argument(
        "--dx",
        type=str,
        default="GR2HQ",
        help="Spotted station (RBN column: dx). Default GR2HQ. Use empty string to disable.",
    )
    p.add_argument("--cw-only", action="store_true", default=True, help="Keep tx_mode == CW (default: on)")
    p.add_argument("--no-cw-only", action="store_false", dest="cw_only", help="Include all modes")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: <repo>/data/rbn)",
    )
    p.add_argument(
        "--contest-start",
        type=str,
        default="2025-07-12 12:00:00",
        help="UTC start for optional time filter (IARU-style Saturday 12:00)",
    )
    p.add_argument(
        "--contest-end",
        type=str,
        default="2025-07-13 11:59:59",
        help="UTC end for optional time filter",
    )
    p.add_argument("--no-time-filter", action="store_true", help="Keep full UTC days after other filters")
    p.add_argument("--chunksize", type=int, default=200_000, help="CSV chunksize for reading")
    p.add_argument("--skip-download", action="store_true", help="Use existing zips in downloads dir only")
    args = p.parse_args()

    dx_val = args.dx.strip() if args.dx else None
    skimmer_val = args.skimmer.strip() if args.skimmer else None
    if not dx_val and not skimmer_val:
        logger.error("Provide at least one of --dx or --skimmer (or defaults).")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent
    out_dir = args.out_dir or (repo_root / "data" / "rbn")
    dl_dir = out_dir / "downloads"
    dl_dir.mkdir(parents=True, exist_ok=True)

    dates = [d.strip() for d in args.dates.split(",") if d.strip()]
    zip_paths: List[Path] = []

    for d in dates:
        url = zip_url(d)
        dest = dl_dir / f"{d}.zip"
        if not args.skip_download:
            try:
                download_file(url, dest)
            except HTTPError as e:
                logger.error("HTTP error for %s: %s", url, e)
                sys.exit(1)
            except URLError as e:
                logger.error("URL error for %s: %s", url, e)
                sys.exit(1)
        else:
            if not dest.is_file():
                logger.error("Missing %s (cannot --skip-download)", dest)
                sys.exit(1)
        zip_paths.append(dest)

    time_start = None
    time_end = None
    if not args.no_time_filter:
        time_start = pd.Timestamp(args.contest_start, tz="UTC")
        time_end = pd.Timestamp(args.contest_end, tz="UTC")

    all_frames: List[pd.DataFrame] = []
    for zp in zip_paths:
        logger.info("Processing %s", zp)
        df = process_one_zip(zp, skimmer_val, dx_val, args.cw_only, time_start, time_end, args.chunksize)
        if not df.empty:
            df["_source_zip"] = zp.name
            all_frames.append(df)
        else:
            logger.warning("No rows after filter for %s", zp)

    if not all_frames:
        logger.error("No data produced.")
        sys.exit(2)

    combined = pd.concat(all_frames, ignore_index=True)
    tag_parts = []
    if dx_val:
        tag_parts.append(f"dx_{dx_val}")
    if skimmer_val:
        tag_parts.append(f"skim_{skimmer_val}")
    tag = "_".join(tag_parts) if tag_parts else "all"
    stem = f"rbn_{tag}_{'cw' if args.cw_only else 'allmodes'}_{dates[0]}"
    if len(dates) > 1:
        stem += f"_{dates[-1]}"
    out_csv = out_dir / f"{stem}.csv"
    combined.to_csv(out_csv, index=False)
    logger.info("Wrote %s rows -> %s", len(combined), out_csv)
    print(str(out_csv))


if __name__ == "__main__":
    main()
```
