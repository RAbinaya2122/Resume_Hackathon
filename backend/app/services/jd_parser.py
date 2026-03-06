from app.utils.text_cleaner import clean_text, extract_years_of_experience
from app.utils.skill_extractor import extract_skills, get_domain_from_skills
from app.models.schemas import ParsedJobDescription


def parse_job_description(text: str) -> ParsedJobDescription:
    """
    Parse a job description text to extract:
    - Required skills
    - Required experience years
    - Domain classification
    """
    cleaned = clean_text(text)
    skills = extract_skills(cleaned)
    experience_years = extract_years_of_experience(cleaned)
    domain = get_domain_from_skills(skills)

    return ParsedJobDescription(
        required_skills=skills,
        required_experience=round(experience_years, 1),
        domain=domain,
    )
