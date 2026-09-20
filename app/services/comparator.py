import pandas as pd
import numpy as np
from typing import List
from app.core.models import CompareResponse, ColumnMapping, CellDiff

def compare_dataframes(df_a: pd.DataFrame, df_b: pd.DataFrame, mappings: List[ColumnMapping], key_column: str, session_id: str) -> CompareResponse:
    rename_dict = {m.target_column: m.source_column for m in mappings}
    df_b = df_b.rename(columns=rename_dict)
    
    mapped_cols = [m.source_column for m in mappings]
    if key_column not in mapped_cols:
        mapped_cols.append(key_column)
        
    cols_a = [c for c in mapped_cols if c in df_a.columns]
    cols_b = [c for c in mapped_cols if c in df_b.columns]
    
    df_a = df_a[cols_a].copy()
    df_b = df_b[cols_b].copy()
    
    df_a[key_column] = df_a[key_column].astype(str)
    df_b[key_column] = df_b[key_column].astype(str)
    
    merged = pd.merge(df_a, df_b, on=key_column, how='outer', suffixes=('_A', '_B'), indicator=True)
    
    row_diffs = []
    matched = 0
    mismatched = 0
    missing_left = 0
    missing_right = 0
    
    column_stats = {col: {'matched': 0, 'mismatched': 0, 'missing_left': 0, 'missing_right': 0} for col in mapped_cols if col != key_column}
    
    for idx, row in merged.iterrows():
        row_key = str(row[key_column])
        _merge_val = row['_merge']
        
        if _merge_val == 'left_only':
            missing_right += 1
            for col in mapped_cols:
                if col == key_column:
                    continue
                val_a = row.get(f"{col}_A", row.get(col))
                row_diffs.append(CellDiff(row_index=row_key, column=col, value_a=str(val_a) if pd.notna(val_a) else None, value_b=None, status='missing_right'))
                column_stats[col]['missing_right'] += 1
        elif _merge_val == 'right_only':
            missing_left += 1
            for col in mapped_cols:
                if col == key_column:
                    continue
                val_b = row.get(f"{col}_B", row.get(col))
                row_diffs.append(CellDiff(row_index=row_key, column=col, value_a=None, value_b=str(val_b) if pd.notna(val_b) else None, status='missing_left'))
                column_stats[col]['missing_left'] += 1
        else:
            row_has_mismatch = False
            for col in mapped_cols:
                if col == key_column:
                    continue
                val_a = row.get(f"{col}_A")
                val_b = row.get(f"{col}_B")
                
                is_na_a = pd.isna(val_a)
                is_na_b = pd.isna(val_b)
                
                if is_na_a and is_na_b:
                    status = 'match'
                elif is_na_a or is_na_b or str(val_a) != str(val_b):
                    status = 'mismatch'
                    row_has_mismatch = True
                else:
                    status = 'match'
                    
                if status == 'mismatch':
                    row_diffs.append(CellDiff(row_index=row_key, column=col, value_a=str(val_a) if not is_na_a else None, value_b=str(val_b) if not is_na_b else None, status='mismatch'))
                    column_stats[col]['mismatched'] += 1
                else:
                    column_stats[col]['matched'] += 1
                    
            if row_has_mismatch:
                mismatched += 1
            else:
                matched += 1
                
    total_rows = len(merged)
    accuracy_pct = (matched / total_rows * 100) if total_rows > 0 else 100.0
    
    data_type_distribution = {'Text': len(mapped_cols), 'Number': 0, 'Currency': 0, 'Date': 0}
    
    return CompareResponse(
        session_id=session_id,
        total_rows=total_rows,
        matched=matched,
        mismatched=mismatched,
        missing_left=missing_left,
        missing_right=missing_right,
        accuracy_pct=accuracy_pct,
        column_stats=column_stats,
        row_diffs=row_diffs,
        data_type_distribution=data_type_distribution
    )
