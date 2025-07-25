# Contest Log Analyzer/contest_tools/reports/plot_venn_diagrams.py
#
# Purpose: A plot report that generates a comparative Venn diagram of QSO overlap,
#          with unique regions subdivided by Run/S&P/Unknown.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-25
# Version: 0.15.0-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# --- Revision History ---
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).

## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.

## [0.14.0-Beta] - 2025-07-24
### Changed
# - Updated to handle and display the new "Unknown" classification.
# - The unique (non-overlapping) areas are now visually split into
#   proportional Run, S&P, and Unknown sections.
# - Refined label positioning, font sizes, and plot boundaries for better readability.
# - Combined 'S&P' and 'Unknown' categories into a single yellow segment.

## [0.12.0-Beta] - 2025-07-23
# - Initial release of the QSO Overlap Venn Diagram report using Shapely
#   for area-proportional diagrams.

from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

# This report requires the 'shapely' library.
try:
    from shapely.geometry import Point, Polygon, LineString
    from shapely.ops import split as shapely_split
except ImportError:
    print("Warning: 'shapely' library not found. The 'venn_diagrams' report will be unavailable.")
    Point = None 

from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a Venn diagram for each band, showing the overlap of
    worked callsigns between two logs, with unique regions split by Run/S&P/Unknown.
    """
    @property
    def report_id(self) -> str:
        return "venn_diagrams"

    @property
    def report_name(self) -> str:
        return "QSO Overlap Venn Diagrams"

    @property
    def report_type(self) -> str:
        return "chart"

    # --- Numerical methods for area-proportional diagrams ---
    def _calculate_intersection_area(self, r1, r2, d):
        if d >= r1 + r2: return 0
        if d <= abs(r1 - r2): return np.pi * min(r1, r2)**2
        term1 = r1**2 * np.arccos((d**2 + r1**2 - r2**2) / (2 * d * r1))
        term2 = r2**2 * np.arccos((d**2 + r2**2 - r1**2) / (2 * d * r2))
        term3 = 0.5 * np.sqrt((-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2))
        return term1 + term2 - term3

    def _find_distance_for_intersection(self, r1, r2, target_area, tol=1e-6, max_iter=100):
        min_d, max_d = abs(r1 - r2), r1 + r2
        if target_area <= 0: return max_d
        if target_area >= np.pi * min(r1, r2)**2: return min_d
        low, high = min_d, max_d
        for _ in range(max_iter):
            d = (low + high) / 2
            current_area = self._calculate_intersection_area(r1, r2, d)
            if abs(current_area - target_area) < tol: return d
            if current_area < target_area: high = d
            else: low = d
        return d

    def _plot_polygon(self, ax, poly, **kwargs):
        if poly.is_empty: return
        if poly.geom_type == 'MultiPolygon':
            for p in poly.geoms:
                ax.add_patch(patches.Polygon(list(p.exterior.coords), closed=True, **kwargs))
        else:
            ax.add_patch(patches.Polygon(list(poly.exterior.coords), closed=True, **kwargs))

    def _generate_single_diagram(self, output_path: str, band_filter: str, **kwargs):
        """
        Helper function to generate a single Venn diagram for a specific band.
        """
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        # --- Data Preparation ---
        df1_full = log1.get_processed_data()[log1.get_processed_data()['Dupe'] == False]
        df2_full = log2.get_processed_data()[log2.get_processed_data()['Dupe'] == False]

        df1_band = df1_full if band_filter == 'All Bands' else df1_full[df1_full['Band'] == band_filter]
        df2_band = df2_full if band_filter == 'All Bands' else df2_full[df2_full['Band'] == band_filter]

        calls1 = set(df1_band['Call'].unique())
        calls2 = set(df2_band['Call'].unique())

        if not calls1 and not calls2:
            print(f"  - Skipping Venn diagram for {band_filter}: No QSOs for either log.")
            return None

        # --- Calculate Subset Sizes and Proportions ---
        common_qso = len(calls1.intersection(calls2))
        k1_only_calls = calls1.difference(calls2)
        k2_only_calls = calls2.difference(calls1)
        
        k1_unique_df = df1_band[df1_band['Call'].isin(k1_only_calls)]
        k2_unique_df = df2_band[df2_band['Call'].isin(k2_only_calls)]

        k1_only_run = (k1_unique_df['Run'] == 'Run').sum()
        k1_only_snp = (k1_unique_df['Run'] == 'S&P').sum()
        k1_only_unk = (k1_unique_df['Run'] == 'Unknown').sum()
        
        k2_only_run = (k2_unique_df['Run'] == 'Run').sum()
        k2_only_snp = (k2_unique_df['Run'] == 'S&P').sum()
        k2_only_unk = (k2_unique_df['Run'] == 'Unknown').sum()
        
        # --- Calculate Proportional Geometry ---
        scale_factor = 0.005
        area_a = len(calls1) * scale_factor
        area_b = len(calls2) * scale_factor
        area_intersect_target = common_qso * scale_factor
        
        r1 = np.sqrt(area_a / np.pi) if area_a > 0 else 0
        r2 = np.sqrt(area_b / np.pi) if area_b > 0 else 0
        distance = self._find_distance_for_intersection(r1, r2, area_intersect_target)

        center1, center2 = Point(-distance/2, 0), Point(distance/2, 0)
        circle_a, circle_b = center1.buffer(r1), center2.buffer(r2)

        # --- Derive Geometric Regions ---
        intersection_poly = circle_a.intersection(circle_b)
        crescent1 = circle_a.difference(circle_b)
        crescent2 = circle_b.difference(circle_a)

        # --- Plotting ---
        fig, ax = plt.subplots(figsize=(12, 9))
        ax.set_aspect('equal')
        ax.axis('off')

        # Draw Intersection
        self._plot_polygon(ax, intersection_poly, facecolor='#B0B0B0', edgecolor='black', alpha=0.8, zorder=2)
        if not intersection_poly.is_empty:
            label_pos = intersection_poly.centroid.coords[0]
            ax.text(label_pos[0], label_pos[1], f"Common\n{common_qso}", ha='center', va='center', color='white', fontsize=17, weight='bold', zorder=3)

        # --- Draw Split Crescents ---
        for crescent, run, snp, unk in [(crescent1, k1_only_run, k1_only_snp, k1_only_unk), 
                                        (crescent2, k2_only_run, k2_only_snp, k2_only_unk)]:
            if crescent.is_empty: continue
            total_unique = run + snp + unk
            if total_unique == 0: continue

            run_prop = run / total_unique
            
            if run_prop == 1.0: # All Run
                self._plot_polygon(ax, crescent, facecolor='#d62728', alpha=0.6, zorder=1) # Red
            elif run_prop == 0.0: # All S&P/Unknown
                self._plot_polygon(ax, crescent, facecolor='gold', alpha=0.6, zorder=1) # Yellow
            else: # Mixed, needs splitting
                bounds = crescent.bounds
                is_vertical = (bounds[2] - bounds[0]) > (bounds[3] - bounds[1])
                
                try:
                    if is_vertical:
                        split_coord = bounds[0] + (bounds[2] - bounds[0]) * run_prop
                        split_line = LineString([(split_coord, bounds[1] - 1), (split_coord, bounds[3] + 1)])
                    else:
                        split_coord = bounds[1] + (bounds[3] - bounds[1]) * run_prop
                        split_line = LineString([(bounds[0] - 1, split_coord), (bounds[2] + 1, split_coord)])

                    split_result = shapely_split(crescent, split_line)
                    
                    if len(split_result.geoms) == 2:
                        p1, p2 = split_result.geoms
                        run_poly, other_poly = (p1, p2) if (p1.centroid.x < split_coord if is_vertical else p1.centroid.y < split_coord) else (p2, p1)
                        
                        self._plot_polygon(ax, run_poly, facecolor='#d62728', alpha=0.6, zorder=1) # Red
                        self._plot_polygon(ax, other_poly, facecolor='gold', alpha=0.6, zorder=1) # Yellow
                    else: 
                        self._plot_polygon(ax, crescent, facecolor='grey', alpha=0.5, zorder=1)
                except: 
                    self._plot_polygon(ax, crescent, facecolor='grey', alpha=0.5, zorder=1)

        # --- Add Detailed, Color-Coded Labels Outside Circles ---
        line_height = max(r1, r2) * 0.28
        gold_color = '#DAA520' # Goldenrod
        
        y_start1 = center1.y + line_height * 2.5
        ax.text(center1.x - r1 - 0.15, y_start1, f"{call1}", ha='right', va='center', fontsize=17, weight='bold', color='black')
        ax.text(center1.x - r1 - 0.15, y_start1 - line_height, f"Total: {len(calls1)}", ha='right', va='center', fontsize=14, color='black')
        ax.text(center1.x - r1 - 0.15, y_start1 - line_height * 2.5, f"Unique: {len(k1_only_calls)}", ha='right', va='center', fontsize=14, color='black')
        ax.text(center1.x - r1 - 0.15, y_start1 - line_height * 3.5, f"Run: {k1_only_run}", ha='right', va='center', fontsize=14, weight='bold', color='#d62728')
        ax.text(center1.x - r1 - 0.15, y_start1 - line_height * 4.5, f"S&P: {k1_only_snp}", ha='right', va='center', fontsize=14, weight='bold', color=gold_color)
        ax.text(center1.x - r1 - 0.15, y_start1 - line_height * 5.5, f"Unknown: {k1_only_unk}", ha='right', va='center', fontsize=14, weight='bold', color=gold_color)

        y_start2 = center2.y + line_height * 2.5
        ax.text(center2.x + r2 + 0.15, y_start2, f"{call2}", ha='left', va='center', fontsize=17, weight='bold', color='black')
        ax.text(center2.x + r2 + 0.15, y_start2 - line_height, f"Total: {len(calls2)}", ha='left', va='center', fontsize=14, color='black')
        ax.text(center2.x + r2 + 0.15, y_start2 - line_height * 2.5, f"Unique: {len(k2_only_calls)}", ha='left', va='center', fontsize=14, color='black')
        ax.text(center2.x + r2 + 0.15, y_start2 - line_height * 3.5, f"Run: {k2_only_run}", ha='left', va='center', fontsize=14, weight='bold', color='#d62728')
        ax.text(center2.x + r2 + 0.15, y_start2 - line_height * 4.5, f"S&P: {k2_only_snp}", ha='left', va='center', fontsize=14, weight='bold', color=gold_color)
        ax.text(center2.x + r2 + 0.15, y_start2 - line_height * 5.5, f"Unknown: {k2_only_unk}", ha='left', va='center', fontsize=14, weight='bold', color=gold_color)

        # --- Formatting and Saving ---
        contest_name = log1.get_metadata().get('ContestName', '')
        year = log1.get_processed_data()['Date'].iloc[0].split('-')[0]
        band_text = band_filter.replace('M', ' Meters') if band_filter != "All Bands" else "All Bands"

        plt.title(f"{year} {contest_name}\nQSO Overlap Analysis - {band_text}", fontsize=16, fontweight='bold')
        fig.text(0.5, 0.02, "Circle and intersection areas are proportional to QSO counts", ha='center', va='bottom', fontsize=10, color='gray')
        
        min_x = center1.x - r1
        max_x = center2.x + r2
        min_y = -max(r1, r2)
        max_y = max(r1, r2)
        
        x_range = max_x - min_x
        y_range = max_y - min_y
        ax.set_xlim(min_x - x_range * 0.5, max_x + x_range * 0.5)
        ax.set_ylim(min_y - y_range * 0.5, max_y + y_range * 0.5)

        os.makedirs(output_path, exist_ok=True)
        filename_band = band_filter.lower().replace('m', '')
        filename = f"{self.report_id}_{filename_band}_{call1}_vs_{call2}.png"
        filepath = os.path.join(output_path, filename)
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()

        return filepath

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all Venn diagrams.
        """
        if Point is None:
            return "Error: 'shapely' library is not installed. Cannot generate Venn diagrams."
        if len(self.logs) != 2:
            return "Error: The Venn Diagram report requires exactly two logs."

        bands_to_plot = ['All Bands', '160M', '80M', '40M', '20M', '15M', '10M']
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = os.path.join(output_path, band) if band != "All Bands" else output_path
                filepath = self._generate_single_diagram(
                    output_path=save_path,
                    band_filter=band,
                    **kwargs
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate Venn diagram for {band}: {e}")

        if not created_files:
            return "No Venn diagrams were generated."

        return "Venn diagrams saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])
