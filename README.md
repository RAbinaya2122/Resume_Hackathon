# ResumeAI — Production-Ready AI Resume Screening Platform

A powerful, privacy-first, and fully offline AI platform for resume screening and skill matching. Built with FastAPI and React, it utilizes advanced weighted scoring and NLP techniques to provide explainable match results.

## 🚀 Key Features

- **Bias-Free Evaluation**: Toggle to strip names, gender indicators, locations, and institutions to ensure objective hiring.
- **Explainable Scoring**: Breakdown of matches across Skills (50%), Experience (30%), and Domain (20%).
- **Skill Extraction**: Automated identification of 200+ technical and soft skills from PDF resumes.
- **Career Recommendation Engine**: Actionable learning roadmaps and better-fit domain suggestions for candidates.
- **Fully Offline**: No data leaves your machine. No external paid APIs or cloud dependencies required.

## 🏗️ Architecture

```text
                                     ┌────────────────┐
                                     │  Vite Frontend │
                                     │ (React + TW)   │
                                     └───────┬────────┘
                                             │ REST API
                                     ┌───────▼────────┐
                                     │ FastAPI Backend│
                                     └───────┬────────┘
             ┌───────────────────────────────┼───────────────────────────────┐
     ┌───────▼───────┐               ┌───────▼───────┐               ┌───────▼───────┐
     │  PDF Parser   │               │   Matcher     │               │    History    │
     │ (pdfplumber)  │               │   (Service)   │               │   (SQLite)    │
     └───────────────┘               └───────────────┘               └───────────────┘
```

## 🛠️ Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── main.py          # Entry point & CORS
│   │   ├── routes/          # API Endpoints (resume, history)
│   │   ├── services/        # Matching logic, JD & Resume Parsing
│   │   ├── models/          # DB Schemas & Pydantic Models
│   │   └── utils/           # PDF extraction, Text cleaning, Skill extraction
│   ├── requirements.txt
│   └── resume_screening.db  # Local SQLite database
└── frontend/
    ├── src/
    │   ├── components/      # Reusable UI (ScoreRing, FileDropzone, etc.)
    │   ├── pages/           # View layers (Home, Dashboard, Results)
    │   ├── hooks/           # useScreening state management
    │   └── services/        # Axios API client
    └── tailwind.config.js
```

## 🚦 Local Setup Instructions

### 1. Backend Setup
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```bash
   python -m app.main
   uvicorn app.main:app --reload
   ```
   *The API will be available at `http://localhost:8000`*

### 2. Frontend Setup
1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The application will be available at `http://localhost:5173`*

## 🧪 Matching Algorithm
The platform uses a weighted scoring model to ensure a balanced evaluation:
- **Skill Match (50%)**: Jaccard similarity between resume skills and job requirements.
- **Experience Match (30%)**: Numerical comparison of extracted years vs requirements.
- **Domain Match (20%)**: Classification-based alignment with the target industry.

## 🛡️ Privacy & Bias-Free Mode
When "Bias-Free Evaluation" is enabled, the backend applies heuristic regex filters to the resume text before extraction, redacting:
- Standalone common first names.
- Pronouns and gendered titles.
- University and college names.
- Geographic identifiers (cities, countries).
- Contact details (phones, emails).

---
*Built with ❤️ for privacy-conscious recruiting.*
