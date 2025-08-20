import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# --- 1. Define Colors ---
# Bright colors for UNIQUE QSOs
UNIQUE_COLORS = {
    'Run': '#FF4136',      # Bright Red
    'S&P': '#2ECC40',      # Bright Green
    'Unknown': '#FFDC00'   # Bright Yellow
}

# Muted/darker colors for COMMON QSOs
COMMON_COLORS = {
    'Both Run': '#85144b', # Dark Red/Maroon
    'Both S&P': '#004D40', # Dark Green/Teal
    'Other': '#DAA520'    # Dark Yellow/Gold
}

# --- 2. Create Made-Up Data ---
# Data for a single band group (e.g., 20 Meters)
unique_1_data = {'Run': 40, 'S&P': 25, 'Unknown': 5}
common_data = {'Both Run': 60, 'Both S&P': 80, 'Other': 30}
unique_2_data = {'Run': 20, 'S&P': 55, 'Unknown': 10}

call_1 = "K1ABC"
call_2 = "W1XYZ"

# --- 3. Plot the Bars ---
fig, ax = plt.subplots(figsize=(10, 6))

# Bar for Unique QSOs for Call 1 (on the left)
bottom = 0
for label, count in unique_1_data.items():
    ax.bar(0, count, bottom=bottom, color=UNIQUE_COLORS[label], width=0.8)
    bottom += count

# Stacked Bar for Common QSOs (in the middle)
bottom = 0
for label, count in common_data.items():
    ax.bar(1, count, bottom=bottom, color=COMMON_COLORS[label], width=0.8)
    bottom += count
    
# Bar for Unique QSOs for Call 2 (on the right)
bottom = 0
for label, count in unique_2_data.items():
    ax.bar(2, count, bottom=bottom, color=UNIQUE_COLORS[label], width=0.8)
    bottom += count

# --- 4. Create and Place the Two Separate Legends ---

# Create handles for the LEFT legend (Unique QSOs)
unique_handles = [
    Patch(color=UNIQUE_COLORS['Run'], label='Run'),
    Patch(color=UNIQUE_COLORS['S&P'], label='S&P'),
    Patch(color=UNIQUE_COLORS['Unknown'], label='Unknown')
]
# Place the left legend
leg1 = ax.legend(handles=unique_handles, loc='upper left', title=f'Unique QSOs ({call_1} / {call_2})', fontsize='medium')
# Add the first legend back to the plot so the second one doesn't overwrite it
ax.add_artist(leg1)

# Create handles for the RIGHT legend (Common QSOs)
common_handles = [
    Patch(color=COMMON_COLORS['Both Run'], label='Run (Both)'),
    Patch(color=COMMON_COLORS['Both S&P'], label='S&P (Both)'),
    Patch(color=COMMON_COLORS['Other'], label='Mixed or Unknown')
]
# Place the right legend
ax.legend(handles=common_handles, loc='upper right', title='Common QSOs', fontsize='medium')


# --- 5. Formatting ---
ax.set_xticks([0, 1, 2])
ax.set_xticklabels([f'{call_1}', 'Common', f'{call_2}'], fontsize='large')
ax.set_ylabel('QSO Count', fontsize='large')
ax.set_title('QSO Breakdown Chart Prototype', fontsize='x-large', fontweight='bold')
plt.tight_layout()

# Save the figure
output_filename = "legend_prototype.png"
plt.savefig(output_filename)

print(f"Prototype chart saved to '{output_filename}'")
plt.show()