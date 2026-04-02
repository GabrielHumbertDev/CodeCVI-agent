# AI Career Platform — Project Report v1

---

## 1. Project Overview

The **AI Career Platform** is a full-stack web application that uses artificial intelligence to help job seekers tailor their CVs, generate cover letters, track job applications, and receive personalised coaching tips — all running entirely locally on the user's machine at no cost.

The system is powered by **Ollama** running the **qwen2.5:7b** language model locally (free, no API key required), meaning no data is sent to third-party AI services.

The platform also includes a full **Admin Management System** allowing administrators to control user access, approve registrations, manage account lifecycle, and maintain an audit trail of all admin actions.

---

## 2. What the Application Does

### Core User Features

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

### Admin Features

| Feature | Description |
|---------|-------------|
| **User Approval** | New registrations are held as `pending_approval` until an admin approves them. |
| **User Listing** | View all users with filters by status, role, and search by name or email. |
| **Approve User** | Activate a pending user so they can log in and use the platform. |
| **Pause User** | Temporarily suspend a user's access with an optional reason. |
| **Resume User** | Restore access for a paused user. |
| **Disable User** | Permanently block a user from accessing the platform. |
| **Edit User** | Update a user's name, email, or role. |
| **Soft Delete** | Remove a user from the platform without destroying database records. |
| **Admin Audit Log** | Every admin action is recorded with the acting admin, target user, action type, and timestamp. |
| **Self-Lock Protection** | Admins cannot delete, disable, or pause their own account. |

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
- **Axios** — HTTP client with automatic JWT injection and status-aware interceptor
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
- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`

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

## 6. Admin Management System

Added after the initial 21 phases as a separate extension. Built in 11 controlled phases with Git checkpoints at each stage.

### 6.1 Admin Design

#### User Roles
| Role | Description |
|------|-------------|
| `user` | Standard platform user |
| `admin` | Full administrative access |

#### User Lifecycle Statuses
| Status | Description |
|--------|-------------|
| `pending_approval` | Newly registered — cannot log in until approved by admin |
| `active` | Full access to the platform |
| `paused` | Temporarily suspended — blocked from logging in |
| `disabled` | Permanently blocked from the platform |

#### User Model Fields Added
| Field | Purpose |
|-------|---------|
| `role` | `user` or `admin` |
| `status` | Current lifecycle status |
| `approved_at` | Timestamp of admin approval |
| `approved_by` | UUID of the admin who approved |
| `paused_at` | Timestamp of most recent pause |
| `pause_reason` | Optional reason given when pausing |
| `is_deleted` | Soft delete flag |
| `last_login_at` | Timestamp of last successful login |

### 6.2 Admin Build Phases

#### Admin Phase 1 — Planning
Inspected existing user model, auth flow, JWT logic, route protection, schemas, services, and frontend auth context. Mapped all integration points before making any changes.
- Git tag: `admin-phase-1-planning`

#### Admin Phase 2 — Database Model Extension
- Added `role`, `status`, `approved_at`, `approved_by`, `paused_at`, `pause_reason`, `is_deleted`, `last_login_at` to the `users` table
- Created Alembic migration (`a1b2c3d4e5f6`)
- Existing users defaulted to `active` status — no disruption
- Added `AdminUserOut`, `AdminUserEdit`, `AdminPauseRequest` schemas
- Git tag: `admin-phase-2-db-model`

#### Admin Phase 3 — Registration & Login Behaviour
- New registrations default to `pending_approval`
- Login checks `status` and returns specific messages per status
- `get_current_user` checks `status` and `is_deleted` on every request
- `last_login_at` updated on every successful login
- Created `backend/create_admin.py` seed script for first admin setup
- Git tag: `admin-phase-3-auth-status`

#### Admin Phase 4 — Role-Based Access Control
- `require_admin` dependency added to `deps.py`
- Chains off `get_current_user` — returns `403 Admin access required` for non-admins
- Any endpoint just needs `Depends(require_admin)` to be protected
- Git tag: `admin-phase-4-rbac`

#### Admin Phase 5 — Admin API Endpoints
- Built `admin_service.py` with all business logic and status transition rules
- Built `admin.py` router with all endpoints
- Registered `/admin` prefix in main router
- Git tag: `admin-phase-5-api`

#### Admin Phase 6 — Audit Logging
- All admin actions logged via existing `log_action()` service
- No new tables needed — reused `audit_logs`
- Actions logged: approve, pause, resume, disable, edit, delete
- Each log includes acting admin ID and target user ID
- Git tag: `admin-phase-6-audit`

#### Admin Phase 7 — Admin Frontend Page
- Created `frontend/src/api/admin.ts` — all admin API calls
- Created `frontend/src/pages/Admin.tsx` — full user management UI
- Features: status tabs, search, approve/pause/resume/disable/edit/delete buttons
- Pause modal with optional reason input
- Edit modal for name, email, role
- Git tag: `admin-phase-7-frontend`

#### Admin Phase 8 — Route Protection & Navigation
- Extended `AuthContext` to store full user object (role, status) after login
- Updated `Login.tsx` to call `GET /auth/me` after token and store user
- Created `AdminRoute.tsx` — redirects non-admins away from `/admin`
- Updated `Navbar.tsx` — shows purple Admin link only for admins
- Shows logged-in user name and `(admin)` badge in navbar
- Git tag: `admin-phase-8-route-guard`

#### Admin Phase 9 — Status-Aware UX
- `Register.tsx` — shows "pending approval" screen after registration instead of redirecting silently
- `AccountStatus.tsx` — friendly status page for pending/paused/disabled accounts
- Axios response interceptor — catches mid-session 403 restriction and redirects to `/account-status`
- Login page already shows specific backend messages per status
- Git tag: `admin-phase-9-user-status-ui`

#### Admin Phase 10 — Testing & Hardening
All 11 lifecycle scenarios tested and confirmed:
- Registration creates `pending_approval` user ✅
- Pending user cannot log in ✅
- Admin can approve user ✅
- Approved user can log in ✅
- Admin can pause user with reason ✅
- Paused user cannot log in ✅
- Non-admin cannot access admin endpoints ✅
- Resume and soft-delete work correctly ✅
- Soft-deleted user is invisible and cannot log in ✅
- Admin cannot delete themselves ✅
- Git tag: `admin-phase-10-hardening`

#### Admin Phase 11 — Documentation
- Full project report updated as `PROJECT_REPORT_v1.md`
- Git tag: `admin-phase-11-docs`

### 6.3 Admin API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/users` | List all users (filter by status, role, search) |
| `GET` | `/admin/users/{id}` | Get single user detail |
| `PUT` | `/admin/users/{id}` | Edit user name, email, or role |
| `POST` | `/admin/users/{id}/approve` | Approve pending user |
| `POST` | `/admin/users/{id}/pause` | Pause active user |
| `POST` | `/admin/users/{id}/resume` | Resume paused user |
| `POST` | `/admin/users/{id}/disable` | Disable user |
| `DELETE` | `/admin/users/{id}` | Soft delete user |

All endpoints require `Authorization: Bearer <admin_token>`.

### 6.4 Admin Files Added/Modified

| File | Type | Change |
|------|------|--------|
| `backend/app/models/user.py` | Modified | Added role, status, lifecycle fields |
| `backend/app/schemas/user.py` | Modified | Added admin schemas |
| `backend/app/services/user_service.py` | Modified | Status-aware user creation and login |
| `backend/app/services/admin_service.py` | New | All admin business logic |
| `backend/app/api/v1/auth.py` | Modified | Status checks in login |
| `backend/app/api/v1/deps.py` | Modified | Status check + `require_admin` |
| `backend/app/api/v1/admin.py` | New | Admin API router |
| `backend/app/api/v1/router.py` | Modified | Registered `/admin` router |
| `backend/alembic/versions/a1b2c3d4e5f6_*.py` | New | Migration for new user fields |
| `backend/create_admin.py` | New | First admin seed script |
| `frontend/src/api/admin.ts` | New | Admin API client |
| `frontend/src/pages/Admin.tsx` | New | Admin management UI |
| `frontend/src/pages/AccountStatus.tsx` | New | Status page for restricted accounts |
| `frontend/src/pages/Register.tsx` | Modified | Pending approval screen after registration |
| `frontend/src/pages/Login.tsx` | Modified | Fetches and stores user object after login |
| `frontend/src/components/AuthContext.tsx` | Modified | Stores user object with role |
| `frontend/src/components/AdminRoute.tsx` | New | Admin-only route guard |
| `frontend/src/components/Navbar.tsx` | Modified | Admin link + user info display |
| `frontend/src/api/client.ts` | Modified | 403 interceptor for mid-session restriction |

---

## 7. Database Tables

| Table | Description |
|-------|-------------|
| `users` | User accounts with role, status, and lifecycle fields |
| `cvs` | Uploaded CV files and parsed JSON data |
| `cv_versions` | AI-tailored versions of CVs |
| `jobs` | Job descriptions |
| `applications` | Job application tracking |
| `cover_letters` | Generated cover letters |
| `audit_logs` | GDPR + admin action audit trail |

**Database GUI:** pgAdmin 4 — https://www.pgadmin.org/download/

---

## 8. Credentials & Configuration

### Database
| Setting | Value |
|---------|-------|
| Host | `127.0.0.1` |
| Port | `5432` |
| Database name | `cv_platform` |
| Username | `cvuser` |
| Password | `cvpass2025` |

### Admin Accounts
| Email | Password | Role | Notes |
|-------|----------|------|-------|
| `admin@cvplatform.com` | `Admin1234` | admin | Primary admin account |
| `test21@test.com` | `Test1234` | admin | Promoted during testing |

### Regular User Accounts (created during testing)
| Email | Password | Status | Notes |
|-------|----------|--------|-------|
| `gabriel@test.com` | — | active | Early test account |
| `plainuser@test.com` | `Test1234` | active | Phase 10 test account |

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

## 9. How to Run the Full Application

Open **4 separate terminal windows** and run one command in each.

### Terminal 1 — Ollama (AI Engine)
```powershell
ollama serve
```
> Must be started first. Runs on port 11434.

### Terminal 2 — AI Microservice
```powershell
cd "d:\FYP 2025\privete projects\CV project\ai_service"
.venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Terminal 3 — FastAPI Backend
```powershell
cd "d:\FYP 2025\privete projects\CV project\backend"
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
> Must use `backend\.venv` — not `ai_service\.venv`.

### Terminal 4 — React Frontend
```powershell
cd "d:\FYP 2025\privete projects\CV project\frontend"
npm start
```
> Opens at http://localhost:3000

### Startup Order
```
1. ollama serve          (wait for "Listening on 127.0.0.1:11434")
2. AI microservice       (wait for "Application startup complete")
3. FastAPI backend       (wait for "Application startup complete")
4. React frontend        (wait for "Compiled successfully")
```

### Verify Everything is Running
| Check | URL |
|-------|-----|
| Frontend | http://localhost:3000 |
| API health | http://localhost:8000/api/v1/health |
| API docs | http://localhost:8000/docs |
| AI service health | http://localhost:8001/health |

---

## 10. First-Time Admin Setup

If starting fresh on a new machine, create the first admin:

```powershell
cd "d:\FYP 2025\privete projects\CV project\backend"
.venv\Scripts\activate
python create_admin.py
```

To promote an existing user to admin:

```powershell
python create_admin.py --promote email@example.com
```

---

## 11. Login & Access

### As Admin
- Go to http://localhost:3000/login
- Email: `admin@cvplatform.com` / Password: `Admin1234`
- Purple **Admin** link appears in navbar
- Navigate to http://localhost:3000/admin for user management

### As Regular User
- Register at http://localhost:3000/register
- Wait for admin approval
- Log in once approved

### View Database (pgAdmin 4)
1. Open pgAdmin 4
2. Connect: host `127.0.0.1`, port `5432`, user `cvuser`, password `cvpass2025`
3. Navigate: **CV Platform → Databases → cv_platform → Schemas → public → Tables**
4. Right-click any table → **View/Edit Data → All Rows**

---

*Report version: v1 — Updated April 2026*
