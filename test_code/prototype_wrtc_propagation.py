# test_code/prototype_wrtc_propagation.py
#
# Version: 1.0.0-Beta
# Date: 2025-10-12
#
# Purpose: A standalone script to generate a visual prototype for one frame
#          of the proposed WRTC propagation animation. It creates a side-by-side
#          butterfly chart comparing two logs' hourly QSO data, broken down by
#          band, continent, and mode.

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

# --- Hardcoded Sample Data for One Hour ---
DATA = {
    'K1ABC': {
        'CW': {
            '80M': {'NA': 20, 'EU': 5},
            '40M': {'NA': 15, 'EU': 25, 'AS': 2},
            '20M': {'EU': 30, 'AS': 10, 'AF': 3, 'OC': 1},
            '15M': {'SA': 8, 'AF': 5},
            '10M': {'SA': 12, 'Unknown': 1}
        },
        'PH': {
            '80M': {'NA': 18},
            '40M': {'NA': 22, 'EU': 8},
            '20M': {'NA': 10, 'EU': 15, 'SA': 5},
            '15M': {'SA': 15},
            '10M': {}
        }
    },
    'W1XYZ': {
        'CW': {
            '80M': {'NA': 25, 'EU': 2},
            '40M': {'NA': 18, 'EU': 28},
            '20M': {'EU': 25, 'AS': 12, 'AF': 5},
            '15M': {'SA': 6, 'AF': 8, 'OC': 2},
            '10M': {'SA': 10}
        },
        'PH': {
            '80M': {'NA': 20},
            '40M': {'NA': 19, 'EU': 12},
            '20M': {'NA': 15, 'EU': 18, 'SA': 3},
            '15M': {'SA': 12, 'AF': 2},
            '10M': {}
        }
    }
}

BANDS = ['80M', '40M', '20M', '15M', '10M']
CONTINENTS = ['NA', 'EU', 'AS', 'SA', 'AF', 'OC', 'Unknown']
MODES = ['CW', 'PH']
CALLS = ['K1ABC', 'W1XYZ']

# --- Color Mapping for Continents ---
COLORS = plt.get_cmap('viridis', len(CONTINENTS))
CONTINENT_COLORS = {cont: COLORS(i) for i, cont in enumerate(CONTINENTS)}

def create_propagation_chart():
    """Generates and saves the side-by-side butterfly chart."""
    fig = plt.figure(figsize=(20, 11)) # Increased height slightly for better spacing

    # --- Main 3-Row GridSpec Layout (Title, Plots, Legend) ---
    gs_main = gridspec.GridSpec(
        3, 1,
        figure=fig,
        height_ratios=[1, 10, 1.5],
        top=0.93,      # Reduce top margin to move layout up
        bottom=0.12,   # Reduce bottom margin to move layout down
        hspace=0.3
    )

    # --- Create zones for title, plots, and legend ---
    ax_title = fig.add_subplot(gs_main[0])
    ax_legend = fig.add_subplot(gs_main[2])
    ax_title.axis('off')
    ax_legend.axis('off')

    # --- Nested GridSpec for the two butterfly plots ---
    gs_plots = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_main[1], wspace=0.1)
    ax_cw = fig.add_subplot(gs_plots[0, 0])
    ax_ph = fig.add_subplot(gs_plots[0, 1], sharey=ax_cw)
    axes = [ax_cw, ax_ph]
    plt.setp(ax_ph.get_yticklabels(), visible=False) # Hide y-axis labels on right plot

    max_qso_rate = 0
    # Pre-calculate the maximum QSO rate across all modes to sync x-axis
    for mode in MODES:
        for band in BANDS:
            for call in CALLS:
                max_qso_rate = max(max_qso_rate, sum(DATA.get(call, {}).get(mode, {}).get(band, {}).values()))
    
    # Round up to the nearest 10 for a clean axis limit
    axis_limit = (max_qso_rate // 10 + 1) * 10

    # Reverse the band order for plotting to ensure 80M is on top
    bands_for_plotting = list(reversed(BANDS))

    for i, mode in enumerate(MODES):
        ax = axes[i]
        ax.set_title(mode, fontsize=16, fontweight='bold')

        # Plot bars for each band
        for j, band in enumerate(bands_for_plotting):
            # --- Plot Log 1 (Top / Positive) ---
            left_pos = 0
            for continent in CONTINENTS:
                qso_count = DATA[CALLS[0]].get(mode, {}).get(band, {}).get(continent, 0)
                if qso_count > 0:
                    ax.barh(j, qso_count, left=left_pos, color=CONTINENT_COLORS[continent], edgecolor='white', height=0.8)
                    left_pos += qso_count

            # --- Plot Log 2 (Bottom / Negative) ---
            left_neg = 0
            for continent in CONTINENTS:
                qso_count = DATA[CALLS[1]].get(mode, {}).get(band, {}).get(continent, 0)
                if qso_count > 0:
                    ax.barh(j, -qso_count, left=left_neg, color=CONTINENT_COLORS[continent], edgecolor='white', height=0.8)
                    left_neg -= qso_count

        # --- Formatting for each subplot ---
        ax.axvline(0, color='black', linewidth=1.5)
        ax.set_yticks(np.arange(len(bands_for_plotting)))
        ax.set_yticklabels(bands_for_plotting, fontsize=12)
        ax.set_xlim(-axis_limit, axis_limit)
        ax.grid(axis='x', linestyle='--', alpha=0.6)

        # Add callsign labels
        ax.text(0.02, 1.02, CALLS[0], transform=ax.transAxes, ha='left', fontsize=12, fontweight='bold')
        ax.text(0.98, 1.02, CALLS[1], transform=ax.transAxes, ha='right', fontsize=12, fontweight='bold')
        ax.set_xlabel("QSO Count for the Hour")


    # --- Overall Figure Title and Legend ---
    year = "2025"
    contest_name = "WRTC"
    event_id = "JUL" # Placeholder
    title_line1 = "WRTC Propagation by Continent (Hourly Snapshot)"
    title_line2 = f"{year} {event_id} {contest_name} - {CALLS[0]} vs. {CALLS[1]}".strip().replace("  ", " ")
    ax_title.text(0.5, 0.5, f"{title_line1}\n{title_line2}", ha='center', va='center', fontsize=22, fontweight='bold', wrap=True)
    
    legend_patches = [plt.Rectangle((0,0),1,1, color=CONTINENT_COLORS[c], label=c) for c in CONTINENTS]
    ax_legend.legend(handles=legend_patches, loc='center', ncol=len(CONTINENTS), title="Continents", fontsize='large', frameon=False)

    # --- Save and Show Plot (Protocol 2.3.4) ---
    output_filename = 'wrtc_propagation_prototype.png'
    try:
        plt.savefig(output_filename)
        print(f"Prototype chart saved to: {output_filename}")
        plt.show()
    except Exception as e:
        print(f"Error saving or showing plot: {e}")

if __name__ == '__main__':
    create_propagation_chart()