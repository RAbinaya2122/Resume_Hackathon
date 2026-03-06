from typing import List, Tuple
from app.utils.skill_extractor import get_domain_from_skills


# Learning roadmap: maps skill → list of recommended resources/steps
SKILL_ROADMAP = {
    "machine learning": ["Learn Python basics", "Study statistics & linear algebra", "Complete Coursera ML course by Andrew Ng", "Build 3 ML projects on Kaggle"],
    "deep learning": ["Master machine learning fundamentals", "Study neural networks (3Blue1Brown series)", "TensorFlow/PyTorch tutorials", "Implement CNNs & RNNs from scratch"],
    "docker": ["Linux fundamentals", "Containerization concepts", "Docker official get-started guide", "Docker Compose for multi-container apps"],
    "kubernetes": ["Docker proficiency first", "CKAD practice labs (killer.sh)", "Deploy a microservice on Minikube", "Study Kubernetes architecture patterns"],
    "react": ["JavaScript ES6+ foundations", "React official docs tutorial", "State management with Redux/Zustand", "Build a full-stack React app"],
    "typescript": ["Strong JavaScript fundamentals", "TypeScript handbook (typescriptlang.org)", "Add types to an existing JS project", "Advanced types: generics, conditional types"],
    "aws": ["Cloud computing fundamentals", "AWS Cloud Practitioner certification", "Deploy a web app on EC2 + S3 + RDS", "AWS Solutions Architect Associate course"],
    "fastapi": ["Python async programming", "FastAPI official documentation", "Build a REST API with auth & DB", "Deploy with Docker + NGINX",],
    "postgresql": ["Relational database concepts", "PostgreSQL official tutorial", "Indexing and query optimization", "PgAdmin hands-on lab"],
    "nlp": ["Python & text processing basics", "NLTK / spaCy tutorial", "Hugging Face transformers course", "Build a text classifier or summarizer"],
    "graphql": ["REST API fundamentals", "GraphQL official learn guide", "Implement schema + resolvers in Python/Node", "GraphQL performance optimization"],
    "cybersecurity": ["Networking fundamentals (CompTIA Net+)", "Linux command line proficiency", "Try Hack Me / Hack The Box beginner paths", "CompTIA Security+ certification"],
    "data engineering": ["SQL mastery", "Python pandas & PySpark basics", "Apache Airflow for workflows", "Build an ETL pipeline end-to-end"],
    "terraform": ["Cloud provider basics (AWS/GCP/Azure)", "HCL syntax — Terraform docs", "Deploy infrastructure to AWS with Terraform", "Terraform state management & modules"],
}

# Better-fit domain recommendations by score range and current domain
DOMAIN_RECOMMENDATIONS = {
    "Data Science / ML": ["Data Engineering", "Backend Engineering", "AI Research"],
    "Backend Engineering": ["Full Stack Engineering", "DevOps / Cloud Engineering", "Data Engineering"],
    "Frontend Engineering": ["Full Stack Engineering", "Mobile Development", "UI/UX Design"],
    "Full Stack Engineering": ["Backend Engineering", "Frontend Engineering", "DevOps / Cloud Engineering"],
    "DevOps / Cloud Engineering": ["Backend Engineering", "Data Engineering", "Site Reliability Engineering"],
    "Mobile Development": ["Frontend Engineering", "Full Stack Engineering", "IoT Development"],
    "Cybersecurity": ["Backend Engineering", "DevOps / Cloud Engineering", "Cloud Security"],
    "Data Engineering": ["Data Science / ML", "Backend Engineering", "Analytics Engineering"],
    "Product Management": ["Project Management", "Business Analysis", "Agile Coaching"],
    "General / Other": ["Frontend Engineering", "Backend Engineering", "Data Science / ML"],
}


def calculate_skill_score(candidate_skills: List[str], required_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    """
    Calculate skill match score using Jaccard-like overlap scoring.
    Returns: (score_0_to_1, matched_skills, missing_skills)
    """
    if not required_skills:
        # Return all candidate skills as "matched" if no requirement specified
        return 1.0, [str(s) for s in candidate_skills if s], []

    candidate_set = {str(s).lower().strip() for s in candidate_skills if s}
    required_set = {str(s).lower().strip() for s in required_skills if s}

    matched = candidate_set & required_set
    missing = required_set - candidate_set

    score = len(matched) / len(required_set) if required_set else 1.0
    score = min(score, 1.0)

    return score, sorted(list(matched)), sorted(list(missing))


def calculate_experience_score(candidate_years: float, required_years: float) -> Tuple[float, float]:
    """
    Calculate experience match score.
    Returns: (score_0_to_1, experience_gap)
    """
    # Ensure inputs are numbers
    c_years = float(candidate_years or 0.0)
    r_years = float(required_years or 0.0)

    if r_years <= 0:
        return 1.0, 0.0

    gap = max(0.0, r_years - c_years)

    if c_years >= r_years:
        score = 1.0
    else:
        score = c_years / r_years

    return min(score, 1.0), gap


def calculate_domain_score(candidate_domain: str, job_domain: str) -> Tuple[float, bool]:
    """
    Calculate domain alignment score.
    Exact match = 1.0, related domains = 0.5, no match = 0.0
    """
    if not candidate_domain or not job_domain:
        return 0.5, False

    cd = str(candidate_domain).lower().strip()
    jd = str(job_domain).lower().strip()

    if cd == jd:
        return 1.0, True

    if cd in jd or jd in cd:
        return 0.75, True

    related_groups = [
        {"backend engineering", "full stack engineering", "data engineering"},
        {"frontend engineering", "full stack engineering", "mobile development"},
        {"data science / ml", "data engineering", "ai research"},
        {"devops / cloud engineering", "site reliability engineering", "backend engineering"},
    ]
    for group in related_groups:
        if cd in group and jd in group:
            return 0.5, False

    return 0.0, False


def calculate_soft_skills_score(candidate_soft_skills: List[str], required_soft_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    """Calculate soft skill match score."""
    if not required_soft_skills:
        return 1.0, [str(s) for s in candidate_soft_skills if s], []
    
    candidate_set = {str(s).lower().strip() for s in candidate_soft_skills if s}
    required_set = {str(s).lower().strip() for s in required_soft_skills if s}
    
    matched = candidate_set & required_set
    missing = required_set - candidate_set
    
    score = len(matched) / len(required_set) if required_set else 1.0
    return min(score, 1.0), sorted(list(matched)), sorted(list(missing))


def calculate_language_score(candidate_languages: List[str], required_languages: List[str]) -> Tuple[float, List[str], List[str]]:
    """Calculate language match score."""
    if not required_languages:
        return 1.0, [str(s) for s in candidate_languages if s], []
    
    candidate_set = {str(s).lower().strip() for s in candidate_languages if s}
    required_set = {str(s).lower().strip() for s in required_languages if s}
    
    matched = candidate_set & required_set
    missing = required_set - candidate_set
    
    score = len(matched) / len(required_set) if required_set else 1.0
    return min(score, 1.0), sorted(list(matched)), sorted(list(missing))


def calculate_project_score(candidate_projects: List[str], required_keywords: List[str]) -> float:
    """Calculate project alignment score based on keywords."""
    if not required_keywords:
        return 1.0
    
    # Cast elements to strings and filter None
    c_projects = [str(p) for p in candidate_projects if p]
    r_keywords = [str(k) for k in required_keywords if k]
    
    if not r_keywords:
        return 1.0

    all_projects_text = " ".join(c_projects).lower()
    matched_count = 0
    for kw in r_keywords:
        if kw.lower().strip() in all_projects_text:
            matched_count += 1
            
    score = matched_count / len(r_keywords) if r_keywords else 1.0
    return min(score, 1.0)


def compute_final_score(
    skill_score: float,
    experience_score: float,
    domain_score: float,
    soft_skills_score: float = 0.0,
    language_score: float = 0.0,
    project_score: float = 0.0,
) -> float:
    """
    Weighted final score (Total 1.0):
    0.4 * Tech, 0.15 * Exp, 0.1 * Domain, 0.15 * Soft, 0.1 * Lang, 0.1 * Proj
    """
    final = (
        (0.4 * (skill_score or 0.0)) + 
        (0.15 * (experience_score or 0.0)) + 
        (0.1 * (domain_score or 0.0)) + 
        (0.15 * (soft_skills_score or 0.0)) + 
        (0.1 * (language_score or 0.0)) + 
        (0.1 * (project_score or 0.0))
    )
    return round(final * 100, 2)


def generate_learning_roadmap(missing_skills: List[str]) -> List[str]:
    """Generate actionable learning steps."""
    roadmap = []
    # Filter None and convert to string
    safe_missing = [str(s) for s in missing_skills if s]
    
    for skill in safe_missing[:5]:
        steps = SKILL_ROADMAP.get(skill.lower())
        if steps:
            roadmap.append(f"📚 {skill.title()}: {steps[0]}")
        else:
            roadmap.append(f"📚 Study {skill.title()} — find courses on Coursera, Udemy, or official docs")
    return roadmap


def get_domain_recommendations(candidate_domain: str, final_score: float) -> List[str]:
    """Recommend 3 alternative domains."""
    if (final_score or 0.0) >= 60:
        return []
    
    domain_key = str(candidate_domain or "General / Other")
    recs = DOMAIN_RECOMMENDATIONS.get(domain_key, ["Software Engineering", "Data Analysis", "Cloud Computing"])
    return recs[:3]


def get_top_skills_to_gain(missing_skills: List[str], candidate_skills: List[str]) -> List[str]:
    """Return top 5 high-value missing skills."""
    # Filter None and convert to string
    safe_missing = [str(s) for s in missing_skills if s]
    
    priority_skills = [s for s in safe_missing if s.lower() in SKILL_ROADMAP]
    other_skills = [s for s in safe_missing if s.lower() not in SKILL_ROADMAP]
    combined = priority_skills + other_skills
    return combined[:5]
