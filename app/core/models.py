from pydantic import BaseModel
from typing import List, Dict, Optional, Literal

class FileInfo(BaseModel):
    filename: str
    sheets: List[str]
    row_count: int

class UploadResponse(BaseModel):
    session_id: str
    files: List[FileInfo]

class ColumnMapping(BaseModel):
    source_column: str
    target_column: str
    confidence: float
    is_key: bool

class DetectColumnsRequest(BaseModel):
    session_id: str
    sheet_a: str
    sheet_b: str
    file_a: str
    file_b: str

class DetectColumnsResponse(BaseModel):
    mappings: List[ColumnMapping]

class CompareRequest(BaseModel):
    session_id: str
    sheet_a: str
    sheet_b: str
    file_a: str
    file_b: str
    mappings: List[ColumnMapping]
    key_column: str

class CellDiff(BaseModel):
    row_index: str
    column: str
    value_a: Optional[str]
    value_b: Optional[str]
    status: Literal['match', 'mismatch', 'missing_left', 'missing_right']

class CompareResponse(BaseModel):
    session_id: str
    total_rows: int
    matched: int
    mismatched: int
    missing_left: int
    missing_right: int
    accuracy_pct: float
    column_stats: Dict[str, Dict[str, int]]
    row_diffs: List[CellDiff]
    data_type_distribution: Dict[str, int]

class AnalysisResponse(BaseModel):
    summary: str
    anomalies: List[str]
    recommendations: List[str]
    severity: Literal['low', 'medium', 'high']
