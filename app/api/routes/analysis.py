import os
import json
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.core.models import CompareResponse, AnalysisResponse
from app.services.ai_analyzer import generate_insights

router = APIRouter()

@router.get("/api/analysis/{session_id}", response_model=AnalysisResponse)
def get_analysis(session_id: str):
    session_dir = os.path.join(settings.upload_dir, session_id)
    result_path = os.path.join(session_dir, "compare_result.json")
    
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Compare result not found")
        
    with open(result_path, "r") as f:
        data = json.load(f)
        
    compare_res = CompareResponse(**data)
    analysis = generate_insights(compare_res)
    
    return analysis
