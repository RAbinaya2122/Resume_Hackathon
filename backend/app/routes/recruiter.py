import httpx
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.models.schemas import BulkMailRequest
from app.utils.auth_utils import decode_access_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/api/recruiter", tags=["Recruiter"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_recruiter(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or payload.get("role") != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or not a recruiter",
        )
    return payload

@router.post("/send-bulk-mail")
async def send_bulk_mail(
    request: BulkMailRequest,
    recruiter = Depends(get_current_recruiter)
):
    """
    Send bulk email to selected candidates via n8n webhook.
    """
    url = "https://abinaya2122.app.n8n.cloud/webhook/bulkmail"
    
    # Body format requested:
    # {
    #  "people": [
    #    {"name": "", "email": ""}
    #  ],
    #  "subject": "",
    #  "message": ""
    # }
    
    body = {
        "people": request.candidates,
        "subject": request.subject,
        "message": request.message
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, timeout=30.0)
            
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Webhook error: {response.text}"
            )
            
        return {"status": "success", "message": "Bulk email request sent to n8n."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send bulk mail: {str(e)}")
