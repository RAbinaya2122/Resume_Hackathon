from app.utils.pdf_parser import extract_text_from_pdf, validate_pdf
from app.utils.text_cleaner import clean_text, strip_bias_indicators, extract_years_of_experience, extract_contact_info
from app.utils.skill_extractor import (
    extract_skills, 
    extract_soft_skills, 
    extract_languages, 
    extract_projects, 
    get_domain_from_skills
)
from app.models.schemas import ParsedResume


def parse_resume(
    filename: str,
    content_type: str,
    file_bytes: bytes,
    bias_free: bool = False,
) -> ParsedResume:
    """
    Full pipeline: validate → extract PDF text → optionally strip bias indicators
    → extract skills, experience, and domain.
    """
    file_size = len(file_bytes)
    validate_pdf(filename, content_type, file_size)

    raw_text = extract_text_from_pdf(file_bytes)
    cleaned = clean_text(raw_text)

    # Extract contact info BEFORE potentially stripping bias indicators
    contact_info = extract_contact_info(raw_text)

    if bias_free:
        cleaned = strip_bias_indicators(cleaned)

    skills = extract_skills(cleaned)
    soft_skills = extract_soft_skills(cleaned)
    languages = extract_languages(cleaned)
    projects = extract_projects(cleaned)
    experience_years = extract_years_of_experience(cleaned)
    domain = get_domain_from_skills(skills)

    return ParsedResume(
        candidate_name=contact_info["name"],
        email=contact_info["email"],
        phone=contact_info["phone"],
        skills=skills,
        soft_skills=soft_skills,
        languages=languages,
        projects=projects,
        experience_years=round(experience_years, 1),
        domain=domain,
        raw_text_length=len(cleaned),
    )
