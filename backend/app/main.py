from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.database import init_db
from app.routes.resume import router as resume_router
from app.routes.history import router as history_router
from app.routes.templates import router as templates_router
from app.routes.auth import router as auth_router
from app.routes.recruiter import router as recruiter_router
from app.routes.candidate import router as candidate_router
from app.routes.team import router as team_router

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="AI Resume Screening & Skill Matching API",
    description=(
        "A fully offline, explainable AI resume screening platform. "
        "Upload PDF resumes, parse job descriptions, and compute weighted match scores "
        "with full explainability and bias-free evaluation support."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS: allow origins
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(resume_router)
app.include_router(history_router)
app.include_router(templates_router)
app.include_router(auth_router)
app.include_router(recruiter_router)
app.include_router(candidate_router)
app.include_router(team_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "service": "AI Resume Screening & Skill Matching API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
