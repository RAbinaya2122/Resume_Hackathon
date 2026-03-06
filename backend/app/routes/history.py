import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db, ScreeningRecordDB
from app.models.schemas import ScreeningRecord, MatchResult

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("/", response_model=List[ScreeningRecord])
def get_screening_history(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve past screening records, newest first.
    """
    records = (
        db.query(ScreeningRecordDB)
        .order_by(ScreeningRecordDB.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for r in records:
        result.append(ScreeningRecord(
            id=r.id,
            filename=r.filename,
            candidate_name=r.candidate_name,
            email=r.email,
            phone=r.phone,
            final_score=r.final_score,
            domain=r.candidate_domain or "Unknown",
            matched_skills=json.loads(r.matched_skills or "[]"),
            missing_skills=json.loads(r.missing_skills or "[]"),
            bias_free_mode=r.bias_free_mode or False,
            created_at=r.created_at.isoformat() if r.created_at else "",
        ))
    return result


@router.get("/{record_id}", response_model=MatchResult)
def get_screening_record_detail(record_id: int, db: Session = Depends(get_db)):
    """
    Get the full analysis details of a specific past screening.
    """
    r = db.query(ScreeningRecordDB).filter(ScreeningRecordDB.id == record_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Record not found.")

    return MatchResult(
        filename=r.filename,
        candidate_name=r.candidate_name,
        email=r.email,
        phone=r.phone,
        final_score=r.final_score,
        skill_score=r.skill_score,
        experience_score=r.experience_score,
        domain_score=r.domain_score,
        matched_skills=json.loads(r.matched_skills or "[]"),
        missing_skills=json.loads(r.missing_skills or "[]"),
        experience_gap=r.experience_gap,
        domain_match=True if r.candidate_domain == r.job_domain else False,
        candidate_domain=r.candidate_domain or "Unknown",
        job_domain=r.job_domain or "Unknown",
        candidate_experience=r.candidate_experience or 0.0,
        required_experience=r.required_experience or 0.0,
        bias_free_mode=r.bias_free_mode or False,
        learning_roadmap=json.loads(r.learning_roadmap or "[]"),
        recommended_domains=json.loads(r.recommended_domains or "[]"),
        top_skills_to_gain=json.loads(r.top_skills_to_gain or "[]"),
    )


@router.delete("/{record_id}")
def delete_screening_record(record_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific screening record by ID.
    """
    record = db.query(ScreeningRecordDB).filter(ScreeningRecordDB.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    db.delete(record)
    db.commit()
    return {"message": f"Record {record_id} deleted successfully."}


@router.delete("/")
def clear_all_records(db: Session = Depends(get_db)):
    """
    Delete ALL screening records.
    """
    db.query(ScreeningRecordDB).delete()
    db.commit()
    return {"message": "All records cleared successfully."}
