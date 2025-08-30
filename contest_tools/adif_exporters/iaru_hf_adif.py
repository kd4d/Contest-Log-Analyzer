# Contest Log Analyzer/contest_tools/adif_exporters/iaru_hf_adif.py
#
# Author: Gemini AI
# Date: 2025-08-30
# Version: 0.55.5-Beta
#
# Purpose: Provides a contest-specific ADIF exporter for the IARU HF
#          World Championship contest. It generates an ADIF file compatible
#          with N1MM Logger+ by writing specific tags and omitting the <ITUZ>
#          tag for HQ and Official station contacts.

import pandas as pd
import numpy as np
import os
import logging
from typing import Dict, Any, Set, List

from ..contest_log import ContestLog

def export_log(log: ContestLog, output_filepath: str):
    """
    Generates a contest-specific ADIF file for an IARU HF Championship log.
    """
    df_full = log.get_processed_data()
    if df_full.empty:
        logging.warning(f"No QSOs to export. ADIF file '{output_filepath}' will not be created.")
        return

    # Use a copy to avoid modifying the original DataFrame
    df_to_export = df_full.copy()
    
    # --- State tracking for new multipliers ---
    seen_zones_per_band: Dict[str, Set[str]] = {}
    seen_hq_officials_per_band: Dict[str, Set[str]] = {}

    def adif_format(tag: str, value: Any) -> str:
        """Helper to format a single ADIF tag."""
        if pd.isna(value) or value == '':
            return ''
        val_str = str(value)
        return f"<{tag}:{len(val_str)}>{val_str} "

    # --- Generate ADIF Content ---
    adif_records: List[str] = []
    adif_records.append("ADIF Export from Contest-Log-Analyzer\n")
    adif_records.append(f"<PROGRAMID:22>Contest-Log-Analyzer\n")
    adif_records.append(f"<PROGRAMVERSION:11>0.55.5-Beta\n")
    adif_records.append("<EOH>\n\n")

    for _, row in df_to_export.iterrows():
        record_parts: List[str] = []
        
        # --- Standard Fields ---
        record_parts.append(adif_format('CALL', row.get('Call')))
        if pd.notna(row.get('Datetime')):
            record_parts.append(f"<QSO_DATE:8>{row['Datetime'].strftime('%Y%m%d')} ")
            record_parts.append(f"<TIME_ON:6>{row['Datetime'].strftime('%H%M%S')} ")
        if pd.notna(row.get('Band')):
            record_parts.append(adif_format('BAND', str(row.get('Band')).lower()))
        record_parts.append(adif_format('MODE', row.get('Mode')))
        record_parts.append(adif_format('RST_RCVD', row.get('RST') or row.get('RS')))
        record_parts.append(adif_format('RST_SENT', row.get('SentRST') or row.get('SentRS')))
        record_parts.append(adif_format('CONTEST_ID', log.get_metadata().get('ContestName')))
        record_parts.append(adif_format('STATION_CALLSIGN', log.get_metadata().get('MyCall')))
        
        # --- IARU Contest-Specific Multiplier Logic ---
        band = row.get('Band')
        if band:
            # Initialize tracking sets for the band if they don't exist
            seen_zones_per_band.setdefault(band, set())
            seen_hq_officials_per_band.setdefault(band, set())

            mult_zone = row.get('Mult_Zone')
            mult_hq = row.get('Mult_HQ')
            mult_official = row.get('Mult_Official')

            # Case 1: Zone Multiplier
            if pd.notna(mult_zone):
                is_new = mult_zone not in seen_zones_per_band[band]
                if is_new: seen_zones_per_band[band].add(mult_zone)
                
                record_parts.append(adif_format('ITUZ', mult_zone))
                if is_new: record_parts.append('<APP_N1MM_MULT1:1>1 ')
                record_parts.append(adif_format('APP_CLA_MULT_ZONE', mult_zone))
                if is_new: record_parts.append('<APP_CLA_MULT_ZONE_ISNEWMULT:1>1 ')

            # Case 2: HQ Multiplier
            elif pd.notna(mult_hq):
                is_new = mult_hq not in seen_hq_officials_per_band[band]
                if is_new: seen_hq_officials_per_band[band].add(mult_hq)
                
                record_parts.append(adif_format('APP_N1MM_HQ', mult_hq))
                if is_new: record_parts.append('<APP_N1MM_MULT2:1>1 ')
                record_parts.append(adif_format('APP_CLA_MULT_HQ', mult_hq))
                if is_new: record_parts.append('<APP_CLA_MULT_HQ_ISNEWMULT:1>1 ')
            
            # Case 3: Official Multiplier
            elif pd.notna(mult_official):
                is_new = mult_official not in seen_hq_officials_per_band[band]
                if is_new: seen_hq_officials_per_band[band].add(mult_official)

                record_parts.append(adif_format('APP_N1MM_HQ', mult_official))
                if is_new: record_parts.append('<APP_N1MM_MULT2:1>1 ')
                record_parts.append(adif_format('APP_CLA_MULT_OFFICIAL', mult_official))
                if is_new: record_parts.append('<APP_CLA_MULT_OFFICIAL_ISNEWMULT:1>1 ')

        # --- Standard APP_CLA Fields ---
        record_parts.append(adif_format('APP_CLA_QSO_POINTS', row.get('QSOPoints')))
        if row.get('Run') == 'Run':
            record_parts.append('<APP_CLA_ISRUNQSO:1>1 ')
            
        adif_records.append("".join(record_parts).strip() + " <EOR>\n")

    # --- Write to File ---
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.writelines(adif_records)
        logging.info(f"Custom IARU ADIF log saved to: {output_filepath}")
    except Exception as e:
        logging.error(f"Error exporting custom IARU ADIF log to '{output_filepath}': {e}")
        raise