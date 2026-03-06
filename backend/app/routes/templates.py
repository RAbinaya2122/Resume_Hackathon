from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, JDTemplateDB
from app.models.schemas import JDTemplate, JDTemplateCreate

router = APIRouter(prefix="/api/templates", tags=["JD Templates"])


@router.post("/", response_model=JDTemplate)
def create_template(template: JDTemplateCreate, db: Session = Depends(get_db)):
    """
    Save a new job description template.
    """
    db_template = JDTemplateDB(
        title=template.title,
        description=template.description,
        about=template.about,
        required_skills=template.required_skills,
        soft_skills=template.soft_skills,
        languages=template.languages,
        projects_keywords=template.projects_keywords,
        required_experience=template.required_experience,
        preferred_domain=template.preferred_domain
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/", response_model=List[JDTemplate])
def list_templates(db: Session = Depends(get_db)):
    """
    List all saved job description templates.
    """
    return db.query(JDTemplateDB).order_by(JDTemplateDB.created_at.desc()).all()


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific JD template.
    """
    db_template = db.query(JDTemplateDB).filter(JDTemplateDB.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found.")
    db.delete(db_template)
    db.commit()
    return {"message": f"Template {template_id} deleted successfully."}
