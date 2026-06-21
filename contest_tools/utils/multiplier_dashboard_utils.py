# contest_tools/utils/multiplier_dashboard_utils.py
#
# Purpose: Shared layout and chart-scaling logic for the multiplier dashboard
#          and the offline html_multiplier_breakdown report.
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)

from typing import Any, Dict, List, Optional, Tuple

from ..contest_definitions import ContestDefinition


def determine_breakdown_dimension(contest_def: ContestDefinition) -> Tuple[str, bool]:
    """Return (dimension, is_mode_dimension) from contest definition."""
    valid_bands = contest_def.valid_bands
    valid_modes = contest_def.valid_modes
    is_single_band = len(valid_bands) == 1
    is_multi_mode = len(valid_modes) > 1
    is_mode_dimension = is_single_band and is_multi_mode
    dimension = 'mode' if is_mode_dimension else 'band'
    return dimension, is_mode_dimension


def split_breakdown_dimension_blocks(
    breakdown_data: Optional[Dict[str, Any]],
    is_mode_dimension: bool,
) -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
    """Split band/mode blocks into low/high layout groups (matches dashboard)."""
    low_bands_data: List[Dict] = []
    high_bands_data: List[Dict] = []
    low_modes_data: List[Dict] = []
    high_modes_data: List[Dict] = []

    if not breakdown_data:
        return low_bands_data, high_bands_data, low_modes_data, high_modes_data

    if is_mode_dimension and 'modes' in breakdown_data:
        for i, block in enumerate(breakdown_data['modes']):
            if i < 3:
                low_modes_data.append(block)
            else:
                high_modes_data.append(block)
    elif 'bands' in breakdown_data:
        low_bands = ['160M', '80M', '40M']
        for block in breakdown_data['bands']:
            if block['label'] in low_bands:
                low_bands_data.append(block)
            else:
                high_bands_data.append(block)

    return low_bands_data, high_bands_data, low_modes_data, high_modes_data


def count_applicable_multiplier_rules(
    contest_def: Optional[ContestDefinition],
    location_type: Optional[str] = None,
    breakdown_data: Optional[Dict[str, Any]] = None,
) -> int:
    """Count multiplier rule types applicable to this session (for tab visibility)."""
    applicable_count = 0
    if contest_def:
        for rule in contest_def.multiplier_rules:
            applies_to = rule.get('applies_to')
            if not applies_to or applies_to == location_type:
                applicable_count += 1

    if applicable_count == 0 and breakdown_data and 'totals' in breakdown_data:
        seen_names = set()
        for row in breakdown_data['totals']:
            mult_name = row.get('label', '')
            if mult_name and mult_name != 'TOTAL' and mult_name not in seen_names:
                seen_names.add(mult_name)
                applicable_count += 1

    return applicable_count


def extract_multiplier_names(breakdown_data: Optional[Dict[str, Any]]) -> List[str]:
    """Multiplier type labels from breakdown totals (excluding TOTAL row)."""
    names: List[str] = []
    if not breakdown_data or 'totals' not in breakdown_data:
        return names
    for row in breakdown_data['totals']:
        mult_name = row.get('label', '')
        if mult_name and mult_name != 'TOTAL' and mult_name not in names:
            names.append(mult_name)
    return names


def compute_spectrum_global_max(
    breakdown_data: Optional[Dict[str, Any]],
    multiplier_names: List[str],
    is_mode_dimension: bool,
) -> Dict[str, int]:
    """
    Y-axis maxima for Band/Mode Spectrum charts.

    Uses per-dimension-block rows only (not contest-wide totals rows), so bar
    heights are normalized against the highest per-band/per-mode unique count.
    """
    global_max: Dict[str, int] = {'total': 1}
    for mult_name in multiplier_names:
        mult_key = mult_name.lower().replace(' ', '_')
        global_max[mult_key] = 1

    if not breakdown_data:
        return global_max

    dimension_key = 'modes' if is_mode_dimension else 'bands'
    if dimension_key not in breakdown_data:
        return global_max

    for block in breakdown_data[dimension_key]:
        for row in block.get('rows', []):
            row_max = 0
            for stat in row.get('stations', []):
                val = (
                    stat.get('unique_run', 0)
                    + stat.get('unique_sp', 0)
                    + stat.get('unique_unk', 0)
                )
                if val > row_max:
                    row_max = val

            row_label = row.get('label', '')
            if row_label == 'TOTAL' or row_label == block.get('label', ''):
                if row_max > global_max['total']:
                    global_max['total'] = row_max
            else:
                for mult_name in multiplier_names:
                    if mult_name in row_label:
                        mult_key = mult_name.lower().replace(' ', '_')
                        if row_max > global_max[mult_key]:
                            global_max[mult_key] = row_max

    return global_max


def get_sweepstakes_breakdown_extras(
    breakdown_data: Optional[Dict[str, Any]],
    contest_name: Optional[str],
    root_input_dir: Optional[str] = None,
) -> Tuple[bool, Optional[int], bool]:
    """
    Return (is_sweepstakes, fixed_multiplier_max, all_logs_same_mult_count).
    """
    is_sweepstakes = bool(contest_name and contest_name.startswith('ARRL-SS'))
    fixed_multiplier_max = None
    all_logs_same_mult_count = False

    if not is_sweepstakes or not breakdown_data or 'totals' not in breakdown_data:
        return is_sweepstakes, fixed_multiplier_max, all_logs_same_mult_count

    total_row = next(
        (row for row in breakdown_data['totals'] if row.get('label') == 'TOTAL'),
        None,
    )
    if total_row and total_row.get('stations'):
        mult_counts = [stat.get('count', 0) for stat in total_row['stations']]
        if mult_counts:
            all_logs_same_mult_count = len(set(mult_counts)) == 1

        try:
            import os
            root_input = root_input_dir or os.environ.get(
                'CONTEST_INPUT_DIR', '/app/CONTEST_LOGS_REPORTS'
            )
            data_dir = os.path.join(root_input, 'data')
            from contest_tools.contest_specific_annotations.arrl_ss_multiplier_resolver import (
                SectionAliasLookup,
            )
            alias_lookup = SectionAliasLookup(data_dir)
            fixed_multiplier_max = alias_lookup.get_total_multiplier_count()
        except Exception:
            fixed_multiplier_max = None

    return is_sweepstakes, fixed_multiplier_max, all_logs_same_mult_count


def build_multiplier_breakdown_chart_context(
    breakdown_data: Optional[Dict[str, Any]],
    contest_def: Optional[ContestDefinition],
    is_mode_dimension: bool,
    location_type: Optional[str] = None,
    contest_name: Optional[str] = None,
    root_input_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build chart/layout context shared by the web dashboard and HTML breakdown report.
    """
    multiplier_names = extract_multiplier_names(breakdown_data)
    multiplier_count = count_applicable_multiplier_rules(
        contest_def, location_type, breakdown_data
    )
    global_max = compute_spectrum_global_max(
        breakdown_data, multiplier_names, is_mode_dimension
    )
    low_bands_data, high_bands_data, low_modes_data, high_modes_data = (
        split_breakdown_dimension_blocks(breakdown_data, is_mode_dimension)
    )
    is_sweepstakes, fixed_multiplier_max, all_logs_same_mult_count = (
        get_sweepstakes_breakdown_extras(breakdown_data, contest_name, root_input_dir)
    )

    return {
        'multiplier_names': multiplier_names,
        'multiplier_count': multiplier_count,
        'global_max': global_max,
        'low_bands_data': low_bands_data,
        'high_bands_data': high_bands_data,
        'low_modes_data': low_modes_data,
        'high_modes_data': high_modes_data,
        'is_mode_dimension': is_mode_dimension,
        'is_sweepstakes': is_sweepstakes,
        'fixed_multiplier_max': fixed_multiplier_max,
        'all_logs_same_mult_count': all_logs_same_mult_count,
    }
