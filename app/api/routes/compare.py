import os
import json
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.core.models import DetectColumnsRequest, DetectColumnsResponse, CompareRequest, CompareResponse
from app.services.excel_parser import parse_file
from app.services.column_mapper import detect_column_mappings
from app.services.data_typer import detect_and_convert
from app.services.comparator import compare_dataframes

router = APIRouter()

@router.post("/api/detect-columns", response_model=DetectColumnsResponse)
def detect_columns(req: DetectColumnsRequest):
    session_dir = os.path.join(settings.upload_dir, req.session_id)
    file_a_path = os.path.join(session_dir, req.file_a)
    file_b_path = os.path.join(session_dir, req.file_b)
    
    if not os.path.exists(file_a_path) or not os.path.exists(file_b_path):
        raise HTTPException(status_code=404, detail="Files not found")
        
    df_a = parse_file(file_a_path, req.sheet_a)
    df_b = parse_file(file_b_path, req.sheet_b)
    
    cols_a = list(df_a.columns)
    cols_b = list(df_b.columns)
    
    mappings = detect_column_mappings(cols_a, cols_b)
    return DetectColumnsResponse(mappings=mappings)

@router.post("/api/compare", response_model=CompareResponse)
def compare_files(req: CompareRequest):
    session_dir = os.path.join(settings.upload_dir, req.session_id)
    file_a_path = os.path.join(session_dir, req.file_a)
    file_b_path = os.path.join(session_dir, req.file_b)
    
    if not os.path.exists(file_a_path) or not os.path.exists(file_b_path):
        raise HTTPException(status_code=404, detail="Files not found")
        
    df_a = parse_file(file_a_path, req.sheet_a)
    df_b = parse_file(file_b_path, req.sheet_b)
    
    df_a, types_a = detect_and_convert(df_a)
    df_b, types_b = detect_and_convert(df_b)
    
    compare_res = compare_dataframes(df_a, df_b, req.mappings, req.key_column, req.session_id)
    
    result_path = os.path.join(session_dir, "compare_result.json")
    with open(result_path, "w") as f:
        json.dump(compare_res.model_dump(), f)
        
    return compare_res
