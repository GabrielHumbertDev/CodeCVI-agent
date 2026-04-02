# AI Career Platform — Project Report

---

## 1. Project Overview

The **AI Career Platform** is a full-stack web application that uses artificial intelligence to help job seekers tailor their CVs, generate cover letters, track job applications, and receive personalised coaching tips — all running entirely locally on the user's machine at no cost.

The system is powered by **Ollama** running the **qwen2.5:7b** language model locally (free, no API key required), meaning no data is sent to third-party AI services.

---

## 2. What the Application Does

### Core Features

| Feature | Description |
|---------|-------------|
| **CV Upload & Parsing** | Upload PDF or DOCX CVs. The system automatically parses them into structured JSON (name, skills, experience, education, summary). |
| **Job Management** | Store job descriptions for roles you want to apply to. |
| **AI CV Tailoring** | Rewrite your CV using AI to match a specific job description, emphasising relevant skills and experience. |
| **Cover Letter Generation** | Generate personalised cover letters using AI based on your CV and the job description. |
| **Match Scoring** | Score how well your CV matches a job description (0–100%) with category breakdowns (skills, experience, education, summary), top strengths, and critical gaps. |
| **Application Tracker** | Track job applications through a status pipeline: Draft → Applied → Interview → Offer / Rejected / Withdrawn. |
| **Readiness Checker** | Before applying, check a 5-point checklist: match score, tailored CV, cover letter, application status. |
| **PDF/DOCX Export** | Download tailored CVs as PDF or DOCX files. |
| **Semantic Search** | Find the best matching jobs for a CV (or best CVs for a job) using AI-generated embeddings and cosine similarity. |
| **Playwright Job Form Detection** | Visit a job application URL and automatically detect form fields, suggesting CV data to pre-fill them. |
| **Coaching Tips** | Receive actionable, priority-ranked improvement tips based on keyword gaps between your CV and the job description. |
| **Analytics Dashboard** | View your average match score, best performing CV version, application counts, and activity over the last 30 days. |
| **Application Funnel** | Visual breakdown of applications by status with conversion rates (application rate, interview rate, offer rate). |
| **Score Trend** | Track how your match score improves across tailored CV versions for the same job. |
| **GDPR Compliance** | Full GDPR implementation: data export (Art. 15), right to erasure (Art. 17), consent management, and personal audit log. |

---

## 3. Technology Stack

### Backend
- **Python 3.10** — primary language
- **FastAPI** — REST API framework (port 8000)
- **SQLAlchemy** — ORM for database models
- **Alembic** — database migration tool
- **PostgreSQL 15** — relational database (port 5432)
- **Pydantic v2** — data validation and serialisation
- **python-docx** — DOCX file parsing and export
- **reportlab** — PDF export
- **Playwright** — browser automation for job form detection
- **numpy** — cosine similarity for semantic search

### AI Service
- **Python** microservice (port 8001)
- **Ollama** — local LLM runtime (port 11434)
- **qwen2.5:7b** — language model for tailoring and cover letters
- **nomic-embed-text** — embedding model (768 dimensions) for semantic search

### Frontend
- **React 19** with **TypeScript**
- **Create React App**
- **Tailwind CSS** — styling
- **React Router v7** — client-side routing
- **Axios** — HTTP client with automatic JWT injection
- **TanStack Query** — server state management

### Database Management
- **pgAdmin 4** — GUI for PostgreSQL (download: https://www.pgadmin.org/download/)

---

## 4. System Architecture

```
┌─────────────────┐     HTTP      ┌──────────────────┐     SQL      ┌──────────────┐
│  React Frontend │ ────────────► │  FastAPI Backend  │ ──────────► │  PostgreSQL  │
│  localhost:3000 │               │  localhost:8000   │             │  port 5432   │
└─────────────────┘               └──────────────────┘             └──────────────┘
                                           │
                                           │ HTTP
                                           ▼
                                  ┌──────────────────┐     HTTP     ┌──────────────┐
                                  │   AI Microservice │ ──────────► │    Ollama    │
                                  │  localhost:8001   │             │  port 11434  │
                                  └──────────────────┘             └──────────────┘
```

---

## 5. Build History — Phase by Phase

### Phase 0a — Project Scaffold
Set up the project folder structure, Git repository, Python virtual environments for backend and AI service, PostgreSQL database (`cv_platform`), and database user (`cvuser`).

### Phase 0b — Database & Alembic
Configured SQLAlchemy with PostgreSQL, set up Alembic for migrations, created the base model class.

### Phase 1 — User Authentication
- User registration and login endpoints
- JWT token generation and validation
- Password hashing with bcrypt
- `GET /auth/register`, `POST /auth/login`, `GET /auth/me`

### Phase 2 — CV Upload & Parsing
- File upload endpoint accepting PDF and DOCX
- DOCX parsing with python-docx
- Structured JSON extraction: name, email, phone, summary, skills, experience, education
- `POST /cvs/upload`, `GET /cvs`, `DELETE /cvs/{id}`

### Phase 3 — Job Management
- CRUD for job descriptions
- `POST /jobs`, `GET /jobs`, `DELETE /jobs/{id}`

### Phase 4 — Ollama AI Service
- Standalone FastAPI microservice wrapping Ollama
- `POST /generate` endpoint proxying to qwen2.5:7b
- Health check endpoint

### Phase 5 — CV Tailoring
- AI-powered CV rewriting against a job description
- Stores tailored versions with version numbers
- `POST /tailor`, `GET /tailor/{cv_id}/versions`

### Phase 6 — Cover Letter Generator
- AI-generated cover letters from CV data and job description
- `POST /cover-letters`, `GET /cover-letters/job/{job_id}`

### Phase 7 — Basic Match Scoring
- Keyword extraction from job descriptions
- Initial match score as percentage of matched keywords

### Phase 8 — Frontend Scaffold
- Initial React app setup with Tailwind CSS
- Basic navbar and page routing

### Phase 9–12 — AI Service Refinement
- Improved prompt engineering for tailoring and cover letters
- Better CV section extraction
- Retry logic on AI failures

### Phase 13 — AI Output Validation
- Pydantic schemas for validating AI JSON output (`TailoredCVOutput`, `CoverLetterOutput`)
- Retry loop with corrective prompt note on validation failure (max 2 retries)
- Fixed `null` phone/email fields from AI output

### Phase 14 — Rich Match Reports
- Complete rewrite of match engine
- Category breakdown: skills, experience, education, summary
- Grade system: Excellent (≥80%), Good (≥60%), Fair (≥40%), Poor (<40%)
- Top strengths and critical gaps ranked by keyword frequency
- Plain-English explanation of match result

### Phase 15 — Application Tracker
- Full CRUD for job applications
- Status state machine: draft → applied → interview → offer / rejected / withdrawn
- Auto-sets `applied_at` timestamp when status changes to "applied"
- `POST /applications`, `GET /applications`, `PUT /applications/{id}`, `DELETE /applications/{id}`

### Phase 16 — Readiness Checker
- Pre-application checklist per application
- Checks: match score ≥60%, tailored CV exists, cover letter exists, status not draft, job description present
- `GET /applications/{id}/readiness`

### Phase 17 — PDF/DOCX Export
- Export any tailored CV version as a formatted DOCX (python-docx) or PDF (reportlab)
- `GET /export/versions/{version_id}/docx`
- `GET /export/versions/{version_id}/pdf`

### Phase 18 — Semantic Search (RAG-Ready)
- nomic-embed-text model via Ollama for 768-dimension embeddings
- Embeddings stored as JSONB in PostgreSQL (pgvector-free workaround)
- Cosine similarity computed with numpy
- `POST /search/jobs-for-cv`, `POST /search/cvs-for-job`
- `POST /search/embed-cv/{cv_id}`, `POST /search/embed-job/{job_id}`

### Phase 19 — Playwright Job Form Detection
- Visit a job application URL with a headless Chromium browser
- Detect visible form fields (name, email, phone, address, LinkedIn, etc.)
- Suggest CV data to pre-fill each field
- Capture screenshot of the page
- Windows-compatible: sync Playwright in ThreadPoolExecutor
- `POST /apply`

### Phase 20 — GDPR Compliance
- Audit logging for all sensitive actions (CV upload, delete, tailor, login)
- `GET /gdpr/export` — full personal data export (Art. 15)
- `POST /gdpr/consent` — record/withdraw consent
- `GET /gdpr/audit-log` — personal audit trail
- `DELETE /gdpr/me` — account erasure requiring password + confirmation phrase (Art. 17)

### Phase 21 — Coaching & Analytics
- Gap-based coaching tips grouped by CV section with high/medium priority
- Analytics dashboard (totals, avg match score, best CV version, recent activity)
- Application funnel with conversion rates
- Score trend across tailored versions of a CV
- `GET /analytics/dashboard`, `GET /analytics/funnel`
- `GET /analytics/score-trend/{cv_id}`, `POST /analytics/coaching`

### Frontend — All 14 Pages
- Login / Register with JWT auth
- Protected routes (redirect to /login if not authenticated)
- Dashboard, CVs, Jobs, Match, Tailor, Cover Letters, Applications
- Search, Coaching, Analytics, Privacy/GDPR pages
- Global Axios instance with automatic Bearer token injection

---

## 6. Database Tables

| Table | Description |
|-------|-------------|
| `users` | Registered user accounts |
| `cvs` | Uploaded CV files and parsed JSON data |
| `cv_versions` | AI-tailored versions of CVs |
| `jobs` | Job descriptions |
| `applications` | Job application tracking |
| `cover_letters` | Generated cover letters |
| `audit_logs` | GDPR audit trail |

**Database GUI:** pgAdmin 4 — https://www.pgadmin.org/download/

---

## 7. Credentials & Configuration

### Database
| Setting | Value |
|---------|-------|
| Host | `127.0.0.1` |
| Port | `5432` |
| Database name | `cv_platform` |
| Username | `cvuser` |
| Password | `cvpass2025` |

### Application User Accounts (created during testing)
| Email | Password | Notes |
|-------|----------|-------|
| `test21@test.com` | `Test1234` | Test account created during Phase 21 testing |

### Services
| Service | URL | Notes |
|---------|-----|-------|
| Frontend | http://localhost:3000 | React app |
| Backend API | http://localhost:8000 | FastAPI |
| API Docs (Swagger) | http://localhost:8000/docs | Interactive API explorer |
| AI Microservice | http://localhost:8001 | Ollama wrapper |
| Ollama | http://localhost:11434 | Local LLM runtime |

### AI Models Required
| Model | Purpose | Install command |
|-------|---------|-----------------|
| `qwen2.5:7b` | CV tailoring, cover letters | `ollama pull qwen2.5:7b` |
| `nomic-embed-text` | Semantic search embeddings | `ollama pull nomic-embed-text` |

---

## 8. How to Run the Full Application

Open **4 separate terminal windows** and run one command in each.

---

### Terminal 1 — Ollama (AI Engine)
```powershell
ollama serve
```
> Must be started first. Runs on port 11434.

---

### Terminal 2 — AI Microservice
```powershell
cd "d:\FYP 2025\privete projects\CV project\ai_service"
.venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8001
```
> Wraps Ollama for the backend. Runs on port 8001.

---

### Terminal 3 — FastAPI Backend
```powershell
cd "d:\FYP 2025\privete projects\CV project\backend"
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
> Main API server. Runs on port 8000.  
> **Important:** Must use the `backend\.venv`, not the `ai_service\.venv`.

---

### Terminal 4 — React Frontend
```powershell
cd "d:\FYP 2025\privete projects\CV project\frontend"
npm start
```
> Opens automatically at http://localhost:3000

---

### Startup Order
```
1. ollama serve          (wait for "Listening on 127.0.0.1:11434")
2. AI microservice       (wait for "Application startup complete")
3. FastAPI backend       (wait for "Application startup complete")
4. React frontend        (wait for "Compiled successfully")
```

---

### Verify Everything is Running
| Check | URL |
|-------|-----|
| Frontend | http://localhost:3000 |
| API health | http://localhost:8000/api/v1/health |
| API docs | http://localhost:8000/docs |
| AI service health | http://localhost:8001/health |

---

### Login
Go to http://localhost:3000/login and use:
- **Email:** `test21@test.com`
- **Password:** `Test1234`

Or register a new account at http://localhost:3000/register

---

### View Database (pgAdmin 4)
1. Open pgAdmin 4
2. Connect to **CV Platform** server (host: `127.0.0.1`, port: `5432`, user: `cvuser`, password: `cvpass2025`)
3. Navigate to: **CV Platform → Databases → cv_platform → Schemas → public → Tables**
4. Right-click any table → **View/Edit Data → All Rows**

---

*Report generated: April 2026*
