import os
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.models import CompareResponse
from app.services.ai_analyzer import generate_insights
from app.services.exporter import export_to_excel, export_to_pdf

router = APIRouter()

@router.get("/api/export/excel/{session_id}")
def export_excel_route(session_id: str):
    session_dir = os.path.join(settings.upload_dir, session_id)
    result_path = os.path.join(session_dir, "compare_result.json")
    
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Compare result not found")
        
    with open(result_path, "r") as f:
        data = json.load(f)
        
    compare_res = CompareResponse(**data)
    output_path = os.path.join(session_dir, "comparison_report.xlsx")
    export_to_excel(compare_res, output_path)
    
    return FileResponse(output_path, filename="comparison_report.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@router.get("/api/export/pdf/{session_id}")
def export_pdf_route(session_id: str):
    session_dir = os.path.join(settings.upload_dir, session_id)
    result_path = os.path.join(session_dir, "compare_result.json")
    
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Compare result not found")
        
    with open(result_path, "r") as f:
        data = json.load(f)
        
    compare_res = CompareResponse(**data)
    analysis = generate_insights(compare_res)
    
    output_path = os.path.join(session_dir, "comparison_report.pdf")
    export_to_pdf(compare_res, analysis, output_path)
    
    return FileResponse(output_path, filename="comparison_report.pdf", media_type="application/pdf")
