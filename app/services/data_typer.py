import pandas as pd
import numpy as np

def detect_and_convert(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    converted_df = df.copy()
    type_map = {}
    
    for col in converted_df.columns:
        series = converted_df[col].dropna()
        if len(series) == 0:
            type_map[col] = 'text'
            continue
            
        str_series = series.astype(str)
        
        # Check for currency
        if str_series.str.contains(r'[$€£¥]').any():
            clean_series = str_series.str.replace(r'[^\d.-]', '', regex=True)
            try:
                converted_df[col] = pd.to_numeric(clean_series)
                type_map[col] = 'currency'
                continue
            except ValueError:
                pass
                
        # Check for date
        date_formats = ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y']
        is_date = False
        for fmt in date_formats:
            try:
                parsed_dates = pd.to_datetime(series, format=fmt, errors='coerce')
                if parsed_dates.notna().sum() > len(series) * 0.5:
                    converted_df[col] = parsed_dates
                    type_map[col] = 'date'
                    is_date = True
                    break
            except Exception:
                continue
                
        if is_date:
            continue
            
        # Check for numeric
        try:
            num_series = pd.to_numeric(series, errors='coerce')
            if num_series.notna().sum() > len(series) * 0.5:
                converted_df[col] = num_series
                type_map[col] = 'number'
                continue
        except Exception:
            pass
            
        # Default to text
        converted_df[col] = str_series
        type_map[col] = 'text'
        
    return converted_df, type_map
