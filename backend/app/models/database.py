from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./resume_screening.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ScreeningRecordDB(Base):
    __tablename__ = "screening_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, nullable=False)
    final_score = Column(Float, nullable=False)
    skill_score = Column(Float, nullable=False)
    soft_skill_score = Column(Float, nullable=False, default=0.0)
    language_score = Column(Float, nullable=False, default=0.0)
    project_score = Column(Float, nullable=False, default=0.0)
    experience_score = Column(Float, nullable=False)
    domain_score = Column(Float, nullable=False)
    candidate_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    candidate_domain = Column(String, nullable=True)
    job_domain = Column(String, nullable=True)
    candidate_experience = Column(Float, nullable=True)
    required_experience = Column(Float, nullable=True)
    matched_skills = Column(Text, nullable=True)   # JSON string
    missing_skills = Column(Text, nullable=True)    # JSON string
    experience_gap = Column(Float, nullable=False, default=0.0)
    bias_free_mode = Column(Boolean, default=False)
    learning_roadmap = Column(Text, nullable=True)  # JSON string
    recommended_domains = Column(Text, nullable=True) # JSON string
    top_skills_to_gain = Column(Text, nullable=True) # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


class JDTemplateDB(Base):
    __tablename__ = "jd_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    about = Column(Text, nullable=True)
    required_skills = Column(Text, nullable=True) # Comma separated
    soft_skills = Column(Text, nullable=True) # Comma separated
    languages = Column(Text, nullable=True) # Comma separated
    projects_keywords = Column(Text, nullable=True) # Comma separated
    required_experience = Column(Float, nullable=True, default=0.0)
    preferred_domain = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'candidate' or 'recruiter'
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
