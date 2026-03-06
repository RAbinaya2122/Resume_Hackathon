import json
import asyncio
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from typing import List, Optional
from app.models.schemas import ParsedResume, MatchResult, BulkScreenResponse, ParsedJobDescription
from app.models.database import get_db, ScreeningRecordDB, JDTemplateDB
from app.services.resume_parser import parse_resume
from app.services.jd_parser import parse_job_description
from app.services.matcher import (
    calculate_skill_score,
    calculate_experience_score,
    calculate_domain_score,
    calculate_soft_skills_score,
    calculate_language_score,
    calculate_project_score,
    compute_final_score,
    generate_learning_roadmap,
    get_domain_recommendations,
    get_top_skills_to_gain,
)

router = APIRouter(prefix="/api/resume", tags=["Resume"])


def _process_single_resume_sync(
    file_bytes: bytes,
    filename: str,
    content_type: str,
    parsed_jd: ParsedJobDescription,
    bias_free: bool
):
    """
    Synchronous helper to process a single resume. 
    Can be safely offloaded to a thread pool.
    """
    # 1. Parse resume
    parsed_resume = parse_resume(
        filename=filename,
        content_type=content_type,
        file_bytes=file_bytes,
        bias_free=bias_free,
    )

    # 2. Compute sub-scores
    skill_score, matched_skills, missing_skills = calculate_skill_score(
        parsed_resume.skills, parsed_jd.required_skills
    )
    soft_skill_score, matched_soft, missing_soft = calculate_soft_skills_score(
        parsed_resume.soft_skills, parsed_jd.soft_skills
    )
    lang_score, matched_langs, missing_langs = calculate_language_score(
        parsed_resume.languages, parsed_jd.languages
    )
    proj_score = calculate_project_score(
        parsed_resume.projects, parsed_jd.projects_keywords
    )
    exp_score, exp_gap = calculate_experience_score(
        parsed_resume.experience_years, parsed_jd.required_experience
    )
    domain_score, domain_match = calculate_domain_score(
        parsed_resume.domain, parsed_jd.domain
    )

    # 3. Final weighted score
    final_score = compute_final_score(
        skill_score, exp_score, domain_score, soft_skill_score, lang_score, proj_score
    )

    # 4. Recommendations (combine technical and soft skills for roadmap)
    all_missing = missing_skills + missing_soft
    roadmap = generate_learning_roadmap(all_missing)
    recommended_domains = get_domain_recommendations(parsed_resume.domain, final_score)
    top_skills = get_top_skills_to_gain(all_missing, parsed_resume.skills)

    # 5. Prepare MatchResult
    match_result = MatchResult(
        filename=filename,
        candidate_name=parsed_resume.candidate_name,
        email=parsed_resume.email,
        phone=parsed_resume.phone,
        final_score=final_score,
        skill_score=round(skill_score * 100, 2),
        soft_skill_score=round(soft_skill_score * 100, 2),
        language_score=round(lang_score * 100, 2),
        project_score=round(proj_score * 100, 2),
        experience_score=round(exp_score * 100, 2),
        domain_score=round(domain_score * 100, 2),
        matched_skills=matched_skills + matched_soft,
        missing_skills=missing_skills + missing_soft,
        experience_gap=exp_gap,
        domain_match=domain_match,
        candidate_domain=parsed_resume.domain,
        job_domain=parsed_jd.domain,
        candidate_experience=parsed_resume.experience_years,
        required_experience=parsed_jd.required_experience,
        bias_free_mode=bias_free,
        learning_roadmap=roadmap,
        recommended_domains=recommended_domains,
        top_skills_to_gain=top_skills,
    )

    # 6. Prepare DB Record (unbound to session)
    record = ScreeningRecordDB(
        filename=filename,
        candidate_name=parsed_resume.candidate_name,
        email=parsed_resume.email,
        phone=parsed_resume.phone,
        final_score=final_score,
        skill_score=round(skill_score * 100, 2),
        soft_skill_score=round(soft_skill_score * 100, 2),
        language_score=round(lang_score * 100, 2),
        project_score=round(proj_score * 100, 2),
        experience_score=round(exp_score * 100, 2),
        domain_score=round(domain_score * 100, 2),
        candidate_domain=parsed_resume.domain,
        job_domain=parsed_jd.domain,
        candidate_experience=parsed_resume.experience_years,
        required_experience=parsed_jd.required_experience,
        matched_skills=json.dumps(matched_skills + matched_soft),
        missing_skills=json.dumps(missing_skills + missing_soft),
        experience_gap=exp_gap,
        bias_free_mode=bias_free,
        learning_roadmap=json.dumps(roadmap),
        recommended_domains=json.dumps(recommended_domains),
        top_skills_to_gain=json.dumps(top_skills),
    )

    return match_result, record


@router.post("/parse", response_model=ParsedResume)
async def upload_and_parse_resume(
    file: UploadFile = File(...),
    bias_free: bool = Form(False),
):
    """
    Offload PDF parsing to a thread pool to avoid blocking.
    """
    try:
        file_bytes = await file.read()
        result = await run_in_threadpool(
            parse_resume,
            filename=file.filename or "unknown.pdf",
            content_type=file.content_type or "",
            file_bytes=file_bytes,
            bias_free=bias_free,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal processing error: {str(e)}")


@router.post("/screen", response_model=MatchResult)
async def screen_resume(
    file: Optional[UploadFile] = File(None),
    resume_url: Optional[str] = Form(None),
    template_id: Optional[int] = Form(None),
    job_description: str = Form(""),
    about: str = Form(""),
    required_skills: str = Form(""),
    soft_skills: str = Form(""),
    languages: str = Form(""),
    projects_keywords: str = Form(""),
    required_experience: float = Form(0.0),
    preferred_domain: str = Form(""),
    bias_free: bool = Form(False),
    db: Session = Depends(get_db),
):
    """
    Full screening pipeline. Supports physical file upload or a resume URL.
    """
    # 1. Handle File Source
    file_bytes = None
    filename = "downloaded_resume.pdf"
    content_type = "application/pdf"

    if file:
        file_bytes = await file.read()
        filename = file.filename or filename
        content_type = file.content_type or content_type
    elif resume_url:
        try:
            # Handle Google Drive Links automatically
            if "drive.google.com" in resume_url:
                import re
                file_id_match = re.search(r'[-\w]{25,}', resume_url)
                if file_id_match:
                    resume_url = f"https://drive.google.com/uc?id={file_id_match.group()}&export=download"
            
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(resume_url, follow_redirects=True, timeout=30.0)
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail="Failed to download resume from URL")
                file_bytes = resp.content
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error downloading URL: {str(e)}")
    
    if not file_bytes:
        raise HTTPException(status_code=422, detail="Please provide either a 'file' or a 'resume_url'")
    # 2. Get Parsed JD
    if template_id:
        template = db.query(JDTemplateDB).filter(JDTemplateDB.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="JD Template not found")
        
        parsed_jd = ParsedJobDescription(
            about=template.about or "",
            required_skills=[s.strip() for s in template.required_skills.split(",")] if template.required_skills and template.required_skills.strip() else [],
            soft_skills=[s.strip() for s in template.soft_skills.split(",")] if template.soft_skills and template.soft_skills.strip() else [],
            languages=[s.strip() for s in template.languages.split(",")] if template.languages and template.languages.strip() else [],
            projects_keywords=[s.strip() for s in template.projects_keywords.split(",")] if template.projects_keywords and template.projects_keywords.strip() else [],
            required_experience=template.required_experience or 0.0,
            domain=template.preferred_domain or "Unknown"
        )
    elif required_skills or soft_skills or languages or projects_keywords or required_experience or preferred_domain:
        parsed_jd = ParsedJobDescription(
            about=about,
            required_skills=[s.strip() for s in required_skills.split(",")] if required_skills and required_skills.strip() else [],
            soft_skills=[s.strip() for s in soft_skills.split(",")] if soft_skills and soft_skills.strip() else [],
            languages=[s.strip() for s in languages.split(",")] if languages and languages.strip() else [],
            projects_keywords=[s.strip() for s in projects_keywords.split(",")] if projects_keywords and projects_keywords.strip() else [],
            required_experience=required_experience,
            domain=preferred_domain or "Unknown"
        )
    else:
        if not job_description.strip():
            raise HTTPException(status_code=422, detail="Please provide template_id, structured fields, or a raw job description.")
        parsed_jd = await run_in_threadpool(parse_job_description, job_description)

    try:
        match_result, record = await run_in_threadpool(
            _process_single_resume_sync,
            file_bytes,
            filename,
            content_type,
            parsed_jd,
            bias_free
        )

        db.add(record)
        db.commit()
        db.refresh(record)
        return match_result

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal processing error: {str(e)}")


@router.post("/bulk-screen", response_model=BulkScreenResponse)
async def bulk_screen_resumes(
    files: List[UploadFile] = File(...),
    job_description: str = Form(""),
    about: str = Form(""),
    required_skills: str = Form(""),
    soft_skills: str = Form(""),
    languages: str = Form(""),
    projects_keywords: str = Form(""),
    required_experience: float = Form(0.0),
    preferred_domain: str = Form(""),
    template_id: Optional[int] = Form(None),
    bias_free: bool = Form(False),
    db: Session = Depends(get_db),
):
    """
    Bulk screening using parallel thread offloading with asyncio.gather.
    """
    if template_id:
        template = db.query(JDTemplateDB).filter(JDTemplateDB.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        parsed_jd = ParsedJobDescription(
            about=template.about or "",
            required_skills=[s.strip() for s in template.required_skills.split(",")] if template.required_skills and template.required_skills.strip() else [],
            soft_skills=[s.strip() for s in template.soft_skills.split(",")] if template.soft_skills and template.soft_skills.strip() else [],
            languages=[s.strip() for s in template.languages.split(",")] if template.languages and template.languages.strip() else [],
            projects_keywords=[s.strip() for s in template.projects_keywords.split(",")] if template.projects_keywords and template.projects_keywords.strip() else [],
            required_experience=template.required_experience or 0.0,
            domain=template.preferred_domain or "Unknown"
        )
    elif required_skills or soft_skills or languages or projects_keywords or required_experience or preferred_domain:
        parsed_jd = ParsedJobDescription(
            about=about,
            required_skills=[s.strip() for s in required_skills.split(",")] if required_skills else [],
            soft_skills=[s.strip() for s in soft_skills.split(",")] if soft_skills else [],
            languages=[s.strip() for s in languages.split(",")] if languages else [],
            projects_keywords=[s.strip() for s in projects_keywords.split(",")] if projects_keywords else [],
            required_experience=required_experience,
            domain=preferred_domain or "Unknown"
        )
    else:
        if not job_description.strip():
            raise HTTPException(status_code=422, detail="Please provide either structured fields or a raw job description.")
        parsed_jd = await run_in_threadpool(parse_job_description, job_description)

    print(f"Parallel Bulk Screen: Received {len(files)} files. Using semaphore limit: 3")
    
    # We use a semaphore to prevent spawning too many heavy threads at once (especially OCR)
    semaphore = asyncio.Semaphore(3)
    
    async def worker(file: UploadFile):
        async with semaphore:
            try:
                filename = file.filename or "unknown.pdf"
                content_type = file.content_type or ""
                print(f"Processing candidate file: {filename}")
                file_bytes = await file.read()
                
                if not file_bytes:
                    return None
                    
                # Offload heavy CPU/OCR work to ThreadPool
                return await run_in_threadpool(
                    _process_single_resume_sync,
                    file_bytes,
                    filename,
                    content_type,
                    parsed_jd,
                    bias_free
                )
            except Exception as e:
                print(f"Error in parallel worker for {file.filename}: {e}")
                return None
            finally:
                await file.close()

    # Create tasks and run in parallel
    tasks = [worker(f) for f in files]
    processed_items = await asyncio.gather(*tasks)
    
    results = []
    failed_count = 0
    # Commit records to DB sequentially in the main thread to avoid session conflicts
    for item in processed_items:
        if item:
            match_res, record = item
            results.append(match_res)
            db.add(record)
        else:
            failed_count += 1
    
    db.commit()

    # Rank results by final_score descending
    results.sort(key=lambda x: x.final_score, reverse=True)

    return BulkScreenResponse(
        results=results,
        total_processed=len(results),
        failed_count=failed_count
    )
