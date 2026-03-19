"""
WRTC Propagation mockup: 24 hourly bar charts from processed CSV.
One chart per contest hour; 5 band clusters; 16 bars per cluster (8 regions x CW/SSB).
Height = points (2 EU, 5 others). Region order: Europe, Japan, Other Asia, Middle East,
Africa, North America, South America, Oceania. Group by region then mode.
Also generates 24 spider (radar) diagrams (5 per image, two rows) and a spider movie.
"""
import os
import sys
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Contest start for contest-hour derivation (IARU: Sat 12:00 UTC)
CONTEST_START = pd.Timestamp("2025-07-12 12:00:00", tz="UTC")

# Band order for clusters
BANDS = ["80M", "40M", "20M", "15M", "10M"]

# Region order (group by region then mode -> 16 bars per cluster)
REGION_ORDER = [
    "Europe", "Japan", "Other Asia", "Middle East",
    "Africa", "North America", "South America", "Oceania",
]

# Beam heading angles (degrees from North, clockwise) for spider diagram spokes (Eastern GB).
SPIDER_ANGLES = [0, 35, 80, 100, 180, 295, 240, 60]  # same order as REGION_ORDER
# Radial scale: radius = points/3 (data space)
SPIDER_DIVISOR = 3

# CQ zones that contain Japan (assign Japan only if DXCC is Japan)
JAPAN_ZONES = {25, 26}

# CQ zones for Middle East (Continent AS)
MIDDLE_EAST_ZONES = {20, 21, 39}


def assign_region(row):
    cont = row.get("Continent") or ""
    zone = row.get("CQZone")
    try:
        zone = int(zone) if pd.notna(zone) else None
    except (TypeError, ValueError):
        zone = None
    dxcc = (row.get("DXCCName") or "").strip()

    if cont == "EU":
        return "Europe"
    if cont == "NA":
        return "North America"
    if cont == "SA":
        return "South America"
    if cont == "AF":
        return "Africa"
    if cont == "OC":
        return "Oceania"
    if cont == "AS":
        if zone is not None and zone in JAPAN_ZONES and dxcc == "Japan":
            return "Japan"
        if zone is not None and zone in MIDDLE_EAST_ZONES:
            return "Middle East"
        return "Other Asia"
    return "Other Asia"  # fallback


def wrtec_points(region: str) -> int:
    return 2 if region == "Europe" else 5


def _hex_to_rgb(hex_str: str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb) -> str:
    return "#" + "".join(f"{min(255, max(0, int(c))):02x}" for c in rgb)


def lighten_hex(hex_str: str, mix_white: float = 0.35) -> str:
    """Return a lighter shade; mix_white=0.35 blends 35% white."""
    r, g, b = _hex_to_rgb(hex_str)
    r = r * (1 - mix_white) + 255 * mix_white
    g = g * (1 - mix_white) + 255 * mix_white
    b = b * (1 - mix_white) + 255 * mix_white
    return _rgb_to_hex((r, g, b))


def spider_data_by_mode_for_hour(agg, hour):
    """For one contest hour, return per-band (cw_pts[8], ph_pts[8]) for the 8 regions."""
    h = agg[agg["ContestHour"] == hour]
    out = {}
    for band in BANDS:
        cw_pts = [
            h[(h["Band"] == band) & (h["Region"] == r) & (h["Mode"] == "CW")]["Points"].sum()
            for r in REGION_ORDER
        ]
        ph_pts = [
            h[(h["Band"] == band) & (h["Region"] == r) & (h["Mode"] == "PH")]["Points"].sum()
            for r in REGION_ORDER
        ]
        out[band] = (cw_pts, ph_pts)
    return out


def radial_max_for_hour(mode_data):
    """Max total points on any band (both modes) this hour -> radial axis max = that/3 with padding."""
    best = 0
    for band in BANDS:
        cw, ph = mode_data.get(band, ([0] * len(REGION_ORDER), [0] * len(REGION_ORDER)))
        total = sum(cw) + sum(ph)
        if total > best:
            best = total
    return max(100.0 / SPIDER_DIVISOR, best / SPIDER_DIVISOR * 1.05)


# Segmented spider: CW = inner segment, PH = outer segment (stacked bar per spoke). Colors for mode.
SPIDER_CW_COLOR = "#1f77b4"
SPIDER_PH_COLOR = "#ff7f0e"
# Angular half-width of each leg (degrees); total width = 2 * LEG_HALF_WIDTH_DEG (thicker legs)
LEG_HALF_WIDTH_DEG = 15


def _wedge_polygons(cw_r, outer_r, angles_deg):
    """Build r and theta lists for CW wedges and PH ring wedges; use None to separate polygons."""
    cw_r_list, cw_t_list = [], []
    ph_r_list, ph_t_list = [], []
    for i in range(len(angles_deg)):
        tc = angles_deg[i] % 360
        lo = (tc - LEG_HALF_WIDTH_DEG) % 360
        hi = (tc + LEG_HALF_WIDTH_DEG) % 360
        # CW wedge: center -> inner edge -> inner edge -> center (closed)
        cw_r_list.extend([0, cw_r[i], cw_r[i], 0])
        cw_t_list.extend([lo, lo, hi, hi])
        # PH wedge: inner -> outer -> outer -> inner (closed)
        ph_r_list.extend([cw_r[i], outer_r[i], outer_r[i], cw_r[i]])
        ph_t_list.extend([lo, lo, hi, hi])
        if i < len(angles_deg) - 1:
            cw_r_list.append(None)
            cw_t_list.append(None)
            ph_r_list.append(None)
            ph_t_list.append(None)
    return (cw_r_list, cw_t_list), (ph_r_list, ph_t_list)


def make_spider_figure(mode_data, radial_max, year, utc_label, title_suffix="Spider — CW/PH by region (points/3)"):
    """Five polar subplots (2 rows). Each spoke = thick wedge (segmented: CW inner, PH outer). Scale = max points this hour."""
    fig = make_subplots(
        rows=2,
        cols=3,
        specs=[
            [{"type": "polar"}, {"type": "polar"}, {"type": "polar"}],
            [{"type": "polar"}, {"type": "polar"}, None],
        ],
        subplot_titles=BANDS,
        vertical_spacing=0.16,
        horizontal_spacing=0.08,
    )
    for idx, band in enumerate(BANDS):
        row = 1 + (idx // 3)
        col = 1 + (idx % 3)
        cw_pts, ph_pts = mode_data.get(band, ([0] * len(REGION_ORDER), [0] * len(REGION_ORDER)))
        cw_r = [p / SPIDER_DIVISOR for p in cw_pts]
        outer_r = [(c + p) / SPIDER_DIVISOR for c, p in zip(cw_pts, ph_pts)]
        (cw_r_list, cw_t_list), (ph_r_list, ph_t_list) = _wedge_polygons(cw_r, outer_r, SPIDER_ANGLES)
        fig.add_trace(
            go.Scatterpolar(
                r=cw_r_list,
                theta=cw_t_list,
                fill="toself",
                name="CW",
                legendgroup="CW",
                line=dict(color=SPIDER_CW_COLOR, width=1.5),
                fillcolor="rgba(31, 119, 180, 0.5)",
            ),
            row=row,
            col=col,
        )
        fig.add_trace(
            go.Scatterpolar(
                r=ph_r_list,
                theta=ph_t_list,
                fill="toself",
                name="Phone",
                legendgroup="PH",
                line=dict(color=SPIDER_PH_COLOR, width=1.5),
                fillcolor="rgba(255, 127, 14, 0.5)",
            ),
            row=row,
            col=col,
        )
    # Polar layout: 0 at North, clockwise; radial range = this hour's max (longer legs).
    # Inset polar domains so band titles and "Europe" (North) don't overlap; leave top margin for main title.
    # Approximate 2x3 grid: top row y ~[0.56, 1], bottom row y ~[0, 0.44]. Inset from top/bottom.
    polar_domains = [
        dict(x=[0, 0.31], y=[0.58, 0.90]),   # row1 col1: inset top
        dict(x=[0.36, 0.67], y=[0.58, 0.90]),
        dict(x=[0.72, 1.0], y=[0.58, 0.90]),
        dict(x=[0, 0.31], y=[0.06, 0.42]),   # row2: inset bottom
        dict(x=[0.36, 0.67], y=[0.06, 0.42]),
    ]
    for i in range(1, 6):
        polar_key = "polar" if i == 1 else f"polar{i}"
        fig.update_layout({
            polar_key: dict(
                domain=polar_domains[i - 1],
                angularaxis=dict(rotation=90, direction="clockwise", tickvals=SPIDER_ANGLES, ticktext=REGION_ORDER),
                radialaxis=dict(range=[0, radial_max], tickfont=dict(size=9)),
            )
        })
    # Main title in top margin so it doesn't overlap band titles; band titles sit in gap above polar (Europe below).
    fig.update_layout(
        margin=dict(t=150),
        title=dict(
            text=f"{year} WRTC Test Event<br>WRTC Propagation {utc_label} UTC — {title_suffix}<br>GB9WR",
            x=0.5,
            xanchor="center",
            y=0.98,
            yanchor="top",
        ),
        height=700,
        width=1100,
        showlegend=True,
        legend=dict(title=dict(text="Mode"), x=1.02, y=1, xanchor="left"),
    )
    # Move subplot (band) titles up so they sit above the polar and don't overlap "Europe"
    for ann in fig.layout.annotations:
        if hasattr(ann, "text") and ann.text in BANDS:
            ann.yanchor = "bottom"
            ann.y += 0.02
    return fig


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\mbdev\Downloads\GB9WR_processed.csv"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "wrtc_propagation_mockups",
    )

    df = pd.read_csv(csv_path)
    df["Datetime"] = pd.to_datetime(df["Datetime"], utc=True)
    df = df[df["Dupe"] == False].copy()
    year = int(df["Datetime"].iloc[0].year) if len(df) > 0 else 2025
    utc_time_labels = [f"{(12 + i) % 24:02d}:00" for i in range(24)]

    # Contest hour 1..24
    df["ContestHour"] = ((df["Datetime"] - CONTEST_START).dt.total_seconds() / 3600).astype(int) + 1
    df["ContestHour"] = df["ContestHour"].clip(1, 24)

    df["Region"] = df.apply(assign_region, axis=1)
    df["Points"] = df["Region"].map(wrtec_points)

    # Normalize mode
    df["Mode"] = df["Mode"].replace({"SSB": "PH"}).fillna("PH")

    # Aggregate: (ContestHour, Band, Region, Mode) -> sum(Points)
    agg = df.groupby(["ContestHour", "Band", "Region", "Mode"])["Points"].sum().reset_index()
    # Global y-axis max so every hour uses the same scale and none truncate
    max_points = float(agg["Points"].max()) if len(agg) > 0 else 100
    y_max = max(100, max_points * 1.05)

    # Styling: CW = dark, PH = light + outline (Option D); outline = black
    colors_dark = {
        "Europe": "#2ca02c",
        "Japan": "#d62728",
        "Other Asia": "#9467bd",
        "Middle East": "#ff7f0e",
        "Africa": "#8c564b",
        "North America": "#1f77b4",
        "South America": "#bcbd22",
        "Oceania": "#17becf",
    }
    colors_light = {r: lighten_hex(c) for r, c in colors_dark.items()}
    PH_OUTLINE = dict(color="#000000", width=1.5)
    x_cat = BANDS
    shapes = [
        dict(type="line", x0=i - 0.5, x1=i - 0.5, y0=0, y1=1, yref="paper", line=dict(color="black", width=1))
        for i in (1, 2, 3, 4)
    ]

    def data_for_hour(h):
        hour_agg = agg[agg["ContestHour"] == h]
        out = {}
        for _, r in hour_agg.iterrows():
            b, reg, mode, pt = r["Band"], r["Region"], r["Mode"], r["Points"]
            out.setdefault(b, {}).setdefault(reg, {})[mode] = pt
        return out

    def make_traces(data):
        traces = []
        for region in REGION_ORDER:
            for mode in ["CW", "PH"]:
                y_vals = [data.get(band, {}).get(region, {}).get(mode, 0) for band in BANDS]
                is_ph = mode == "PH"
                color = colors_light.get(region, "#b2b2b2") if is_ph else colors_dark.get(region, "#7f7f7f")
                marker = dict(color=color)
                if is_ph:
                    marker["line"] = PH_OUTLINE
                traces.append(
                    go.Bar(
                        x=x_cat,
                        y=y_vals,
                        name=f"{region} {mode}",
                        marker=marker,
                        legendgroup=region,
                    )
                )
        return traces

    layout_common = dict(
        xaxis=dict(title="Band"),
        yaxis=dict(title="Points", range=[0, y_max]),
        barmode="group",
        bargap=0.15,
        bargroupgap=0.02,
        height=550,
        width=1150,
        margin=dict(r=320),
        legend=dict(
            title=dict(
                text="Region / Mode<br><sub>CW = solid dark · PH = light with outline</sub>",
                font=dict(size=10),
            ),
            x=1.01,
            y=1,
            yanchor="top",
            xanchor="left",
            font=dict(size=9),
            itemsizing="constant",
            tracegroupgap=2,
        ),
        shapes=shapes,
    )

    os.makedirs(out_dir, exist_ok=True)

    # 24 individual hourly charts
    for hour in range(1, 25):
        data = data_for_hour(hour)
        fig = go.Figure(data=make_traces(data))
        fig.update_layout(
            layout_common,
        title=dict(
            text=f"{year} WRTC Test Event<br>WRTC Propagation — {utc_time_labels[hour - 1]} UTC<br>GB9WR — Points by band, region, mode",
            x=0.5,
        ),
        )
        out_path = os.path.join(out_dir, f"wrtc_propagation_hour_{hour:02d}.html")
        fig.write_html(out_path)
        print(f"Wrote {out_path}")

    # Movie: NO Plotly slider. Plot only (larger height). Hour slider + Play/Pause in separate HTML block BELOW the plot.
    movie_layout = dict(layout_common)
    movie_layout["margin"] = dict(r=320, b=60)
    movie_layout["height"] = 620
    # GMT hour for frame i: 12, 13, ..., 23, 00, 01, ..., 11
    title_top = f"{year} WRTC Test Event"
    all_traces = [make_traces(data_for_hour(h)) for h in range(1, 25)]
    frames = [
        go.Frame(
            data=all_traces[i],
            name=str(i),
            layout=dict(title=dict(text=f"{title_top}<br>WRTC Propagation — {utc_time_labels[i]} UTC<br>GB9WR — Points by band, region, mode")),
        )
        for i in range(24)
    ]
    fig_movie = go.Figure(data=all_traces[0], frames=frames)
    fig_movie.update_layout(
        movie_layout,
        title=dict(
            text=f"{title_top}<br>WRTC Propagation — {utc_time_labels[0]} UTC<br>GB9WR — Points by band, region, mode",
            x=0.5,
        ),
    )
    movie_path = os.path.join(out_dir, "wrtc_propagation_movie.html")
    html_str = fig_movie.to_html(include_plotlyjs=True)
    # Wrap the plot container in a fixed-height div so the chart has a defined height and controls sit below.
    html_str = html_str.replace("<body>", "<body><div id=\"wrtc-plot-wrapper\" style=\"height:620px; width:100%; min-height:620px;\">")
    # Close the wrapper after the plotly-graph-div's parent (first </div> after plotly div might be the outer one - we need to close after the script that does newPlot).
    # Plotly output is: <div>\n  <div id=.. class=plotly-graph-div></div>\n  <script>...
    # So we have: <body><div id=wrtc-plot-wrapper...>  then original <div> <div plotly...> </div> <script>
    # We need to close wrtc-plot-wrapper after the plot div. So replace the first "</div>" that closes the plotly's parent - that's the one right after plotly-graph-div.
    # Safer: insert closing </div> after the newPlot script block (before our custom block). So find </script> that follows Plotly.newPlot and add </div> after the next </div>.
    # Simpler: the structure is <body><our wrapper><div><div plotly></div><script>... So we need one </div> to close our wrapper. Insert it right before our custom_block.
    controls_block = """
</div>
<div id="wrtc-controls" style="margin: 12px 0 0 5%; font-family: sans-serif; font-size: 14px;">
  <div style="margin-bottom: 8px;">
    <label>GMT hour:</label>
    <input type="range" id="wrtc-hour" min="0" max="23" value="0" style="vertical-align: middle; width: 280px;">
    <span id="wrtc-hour-label" style="margin-left: 8px;">12</span>
  </div>
  <div>
    <label>Seconds per frame (1–3 decimals):</label>
    <input type="number" id="wrtc-sec-per-frame" min="0.1" max="60" step="0.001" value="2" style="width: 5em; margin-left: 6px;">
    <button id="wrtc-play-custom" style="margin-left: 8px;">Play</button>
    <button id="wrtc-pause-custom" style="margin-left: 6px;">Pause</button>
  </div>
</div>
<script>
(function() {
  var gmtLabels = ["12","13","14","15","16","17","18","19","20","21","22","23","00","01","02","03","04","05","06","07","08","09","10","11"];
  function getPlotDiv() { return document.querySelector('.plotly-graph-div'); }
  function goToFrame(i) {
    var gd = getPlotDiv();
    if (gd && window.Plotly) window.Plotly.animate(gd, [String(i)], { frame: { duration: 0 }, mode: 'immediate' });
    var lab = document.getElementById('wrtc-hour-label');
    if (lab) lab.textContent = gmtLabels[i];
  }
  function stopAnimation() {
    var gd = getPlotDiv();
    if (gd && window.Plotly) window.Plotly.animate(gd, [null], { frame: { duration: 0 }, mode: 'immediate' });
  }
  var hourInput = document.getElementById('wrtc-hour');
  if (hourInput) {
    hourInput.addEventListener('input', function() { goToFrame(parseInt(this.value, 10)); });
  }
  document.getElementById('wrtc-pause-custom').onclick = stopAnimation;
  document.getElementById('wrtc-play-custom').onclick = function() {
    var gd = getPlotDiv();
    if (!gd || !window.Plotly) return;
    var sec = parseFloat(document.getElementById('wrtc-sec-per-frame').value);
    if (isNaN(sec) || sec < 0.1) sec = 2;
    window.Plotly.animate(gd, null, {
      frame: { duration: Math.round(sec * 1000), redraw: true },
      transition: { duration: 0 },
      fromcurrent: true,
      mode: 'immediate'
    });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function() { stopAnimation(); goToFrame(0); });
  else { stopAnimation(); goToFrame(0); }
})();
</script>
"""
    if "</body>" in html_str:
        html_str = html_str.replace("</body>", controls_block + "\n</body>")
    with open(movie_path, "w", encoding="utf-8") as f:
        f.write(html_str)
    print(f"Wrote {movie_path}")

    # --- Spider diagrams: 5 polar subplots per hour (2 rows). Segmented by mode (CW inner, PH outer). Per-hour radial scale. ---
    spider_dir = os.path.join(out_dir, "spider")
    os.makedirs(spider_dir, exist_ok=True)

    for hour in range(1, 25):
        mode_data = spider_data_by_mode_for_hour(agg, hour)
        radial_max = radial_max_for_hour(mode_data)
        utc_label = utc_time_labels[hour - 1]
        fig_spider = make_spider_figure(mode_data, radial_max, year, utc_label)
        out_path = os.path.join(spider_dir, f"wrtc_spider_hour_{hour:02d}.html")
        fig_spider.write_html(out_path)
        print(f"Wrote {out_path}")

    # Spider movie: combine the 24 individual plot HTMLs (iframes); no Plotly animation device, just switch which iframe is visible.
    gmt_labels = [f"{(12 + i) % 24:02d}" for i in range(24)]
    iframe_srcs = [f"wrtc_spider_hour_{h:02d}.html" for h in range(1, 25)]
    spider_movie_path = os.path.join(spider_dir, "wrtc_spider_movie.html")
    spider_movie_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>WRTC Spider — Movie (24 hours)</title>
  <style>
    #wrtc-spider-frames {{ position: relative; width: 100%; min-width: 1100px; height: 700px; }}
    #wrtc-spider-frames iframe {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; border: none; }}
    #wrtc-spider-frames iframe:not(.active) {{ visibility: hidden; pointer-events: none; }}
  </style>
</head>
<body>
  <div id="wrtc-spider-frames">
"""
    for i, src in enumerate(iframe_srcs):
        cls = " active" if i == 0 else ""
        spider_movie_html += f'    <iframe id="wrtc-spider-frame-{i}" class="spider-frame{cls}" data-frame="{i}" src="{src}"></iframe>\n'
    spider_movie_html += """  </div>
  <div id="wrtc-spider-controls" style="margin: 12px 0 0 5%; font-family: sans-serif; font-size: 14px;">
    <div style="margin-bottom: 8px;">
      <label>UTC hour:</label>
      <input type="range" id="wrtc-spider-hour" min="0" max="23" value="0" style="vertical-align: middle; width: 280px;">
      <span id="wrtc-spider-hour-label" style="margin-left: 8px;">12</span>
    </div>
    <div>
      <label>Seconds per frame (1–3 decimals):</label>
      <input type="number" id="wrtc-spider-sec-per-frame" min="0.1" max="60" step="0.001" value="2" style="width: 5em; margin-left: 6px;">
      <button id="wrtc-spider-play-custom" style="margin-left: 8px;">Play</button>
      <button id="wrtc-spider-pause-custom" style="margin-left: 6px;">Pause</button>
    </div>
  </div>
  <script>
(function() {
  var gmtLabels = """ + str(gmt_labels) + """;
  var frames = document.querySelectorAll('#wrtc-spider-frames iframe');
  function goToFrame(i) {
    i = Math.max(0, Math.min(23, parseInt(i, 10)));
    for (var k = 0; k < frames.length; k++) {
      frames[k].classList.toggle('active', k === i);
    }
    var lab = document.getElementById('wrtc-spider-hour-label');
    if (lab) lab.textContent = gmtLabels[i];
    document.getElementById('wrtc-spider-hour').value = i;
  }
  var hourInput = document.getElementById('wrtc-spider-hour');
  if (hourInput) {
    hourInput.addEventListener('input', function() { goToFrame(parseInt(this.value, 10)); });
  }
  var playTimer = null;
  document.getElementById('wrtc-spider-pause-custom').onclick = function() {
    if (playTimer) { clearInterval(playTimer); playTimer = null; }
  };
  document.getElementById('wrtc-spider-play-custom').onclick = function() {
    if (playTimer) clearInterval(playTimer);
    var sec = parseFloat(document.getElementById('wrtc-spider-sec-per-frame').value);
    if (isNaN(sec) || sec < 0.1) sec = 2;
    var idx = parseInt(document.getElementById('wrtc-spider-hour').value, 10);
    playTimer = setInterval(function() {
      idx = (idx + 1) % 24;
      goToFrame(idx);
    }, sec * 1000);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function() { goToFrame(0); });
  else goToFrame(0);
})();
  </script>
</body>
</html>
"""
    with open(spider_movie_path, "w", encoding="utf-8") as f:
        f.write(spider_movie_html)
    print(f"Wrote {spider_movie_path}")

    print(f"Done. 24 bar charts + 1 bar movie in {out_dir}; 24 spider images + 1 spider movie in {spider_dir}")


if __name__ == "__main__":
    main()
