from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class ParsedResume(BaseModel):
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    experience_years: float = Field(default=0.0)
    domain: str = Field(default="Unknown")
    raw_text_length: int = Field(default=0)


class JobDescriptionInput(BaseModel):
    text: str
    bias_free: bool = False


class ParsedJobDescription(BaseModel):
    about: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    projects_keywords: List[str] = Field(default_factory=list)
    required_experience: float = Field(default=0.0)
    domain: str = Field(default="Unknown")


class MatchResult(BaseModel):
    filename: str
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    final_score: float
    skill_score: float
    soft_skill_score: float = 0.0
    language_score: float = 0.0
    project_score: float = 0.0
    experience_score: float
    domain_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_gap: float
    domain_match: bool
    candidate_domain: str
    job_domain: str
    candidate_experience: float
    required_experience: float
    bias_free_mode: bool
    learning_roadmap: List[str] = Field(default_factory=list)
    recommended_domains: List[str] = Field(default_factory=list)
    top_skills_to_gain: List[str] = Field(default_factory=list)


class BulkScreenResponse(BaseModel):
    results: List[MatchResult]
    total_processed: int
    failed_count: int = 0


class ScreenRequest(BaseModel):
    job_description: str
    bias_free: bool = False


class ScreeningRecord(BaseModel):
    id: int
    filename: str
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    final_score: float
    domain: str
    matched_skills: List[str]
    missing_skills: List[str]
    bias_free_mode: bool
    created_at: str


class JDTemplateCreate(BaseModel):
    title: str
    description: Optional[str] = None
    about: Optional[str] = None
    required_skills: Optional[str] = None
    soft_skills: Optional[str] = None
    languages: Optional[str] = None
    projects_keywords: Optional[str] = None
    required_experience: float = 0.0
    preferred_domain: Optional[str] = None


class JDTemplate(JDTemplateCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    role: str = "candidate"  # recruiter or candidate


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str


class BulkMailRequest(BaseModel):
    candidates: List[dict]  # [{"name": "...", "email": "..."}]
    subject: str
    message: str
