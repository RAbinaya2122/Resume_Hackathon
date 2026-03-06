import os
import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.models.database import get_db, ScreeningRecordDB
from app.services.resume_parser import parse_resume
from app.utils.auth_utils import decode_access_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/api/candidate", tags=["Candidate"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

UPLOAD_DIR = "uploaded_resumes"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def get_current_candidate(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or payload.get("role") != "candidate":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or not a candidate",
        )
    return payload

@router.post("/upload-resume")
async def candidate_upload_resume(
    file: UploadFile = File(...),
    candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """
    Candidate upload portal:
    1. Accept PDF only.
    2. Store uploaded file.
    3. Trigger existing resume parsing pipeline.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    file_path = os.path.join(UPLOAD_DIR, f"{candidate['sub']}_{file.filename}")
    
    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read file bytes for parsing
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            
        # Step 3: Trigger existing pipeline
        # Note: We're using a dummy job description if one isn't provided, 
        # but the request says just "trigger existing resume parsing pipeline"
        # and "extract text / continue skill extraction".
        # We can just call parse_resume which is the core part of the pipeline.
        
        parsed_result = await parse_resume(
            filename=file.filename,
            content_type=file.content_type,
            file_bytes=file_bytes,
            bias_free=False
        )
        
        return {
            "status": "success",
            "message": "Resume uploaded and processed successfully.",
            "data": parsed_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {str(e)}")
