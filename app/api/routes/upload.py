import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File
from typing import List
from app.core.config import settings
from app.core.models import UploadResponse
from app.services.excel_parser import get_file_info

router = APIRouter()

@router.post("/api/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(settings.upload_dir, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    file_infos = []
    
    for file in files:
        file_path = os.path.join(session_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_info = get_file_info(file_path, file.filename)
        file_infos.append(file_info)
        
    return UploadResponse(session_id=session_id, files=file_infos)

@router.get("/api/sheets/{session_id}", response_model=UploadResponse)
def get_sheets(session_id: str):
    session_dir = os.path.join(settings.upload_dir, session_id)
    if not os.path.exists(session_dir):
        return UploadResponse(session_id=session_id, files=[])
        
    file_infos = []
    for filename in os.listdir(session_dir):
        file_path = os.path.join(session_dir, filename)
        if os.path.isfile(file_path) and not filename.endswith('.json'):
            file_info = get_file_info(file_path, filename)
            file_infos.append(file_info)
            
    return UploadResponse(session_id=session_id, files=file_infos)
