import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import upload, compare, analysis, export

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.upload_dir, exist_ok=True)
    yield

app = FastAPI(title="NexSheetMind API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["Upload"])
app.include_router(compare.router, tags=["Compare"])
app.include_router(analysis.router, tags=["Analysis"])
app.include_router(export.router, tags=["Export"])

@app.get("/")
def root():
    return {"message": "Welcome to NexSheetMind API"}
