import pandas as pd
import os
from app.core.models import FileInfo

def parse_file(file_path: str, sheet_name: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path, dtype=str)
    else:
        return pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)

def get_sheet_names(file_path: str) -> list[str]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return ["Sheet1"]
    else:
        xls = pd.ExcelFile(file_path)
        return xls.sheet_names

def get_file_info(file_path: str, filename: str) -> FileInfo:
    sheets = get_sheet_names(file_path)
    df = parse_file(file_path, sheets[0])
    row_count = len(df)
    return FileInfo(filename=filename, sheets=sheets, row_count=row_count)
