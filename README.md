# CodeCVI Agent

CodeCVI Agent is an AI-assisted CV and job-application platform. It helps users upload CVs, compare them against job descriptions, understand match gaps, generate tailored CV versions, and create cover letters for specific roles.

The project uses a local-first AI setup with Ollama and Qwen 2.5, packaged through Docker Compose so the app can run without manually starting Ollama on the host machine.

## Features

- User registration and login
- Admin approval and user management
- CV upload and parsing for PDF/DOCX files
- Job description storage
- CV-to-job match scoring
- Match breakdown by skills, experience, education, and summary
- Recommended edits before rewriting the CV
- AI-generated tailored CV versions
- Unsupported-claim validation warnings for tailored CVs
- AI-generated cover letters
- DOCX/PDF export for tailored CVs
- Application tracking
- Analytics dashboard
- GDPR export/delete flows
- Full Docker setup with PostgreSQL, Redis, FastAPI, React, Ollama, and Qwen 2.5

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Tailwind CSS, Nginx |
| Backend | FastAPI, SQLAlchemy, Alembic |
| AI service | FastAPI, httpx |
| AI runtime | Ollama |
| Generation model | `qwen2.5:7b` |
| Embedding model | `nomic-embed-text` |
| Database | PostgreSQL |
| Cache | Redis |
| Deployment | Docker Compose |

## Main Workflow

The guided workflow is available at:

```text
http://localhost:3000/workflow
```

It walks the user through:

1. Uploading or selecting a CV
2. Pasting or selecting a job description
3. Getting a match score
4. Reviewing missing or weak areas
5. Generating an improved CV version
6. Generating a tailored cover letter
7. Downloading the tailored CV as DOCX/PDF

The primary navigation is intentionally focused:

- Dashboard
- Workflow
- CVs
- Jobs
- Applications
- Search
- History
- Analytics
- Privacy

The older standalone tools for match scoring, tailoring, cover letters, and coaching are still available as direct routes from the History page under "Advanced direct tools". They are kept for testing and fallback while the Workflow page becomes the main user journey.

## Running The App With Docker

### Prerequisites

- Docker Desktop
- Git
- Enough disk space for the Ollama models

You do not need Ollama installed separately on Windows for the full Docker setup.

### Start The Stack

From the project root:

```powershell
docker compose up -d
```

On the first run, Docker pulls:

- `qwen2.5:7b`
- `nomic-embed-text`

This can take several minutes. Later runs are faster because the models are stored in the `ollama_data` Docker volume.

### Check Services

```powershell
docker compose ps
```

Expected services:

- `frontend`
- `backend`
- `ai_service`
- `ollama`
- `db`
- `redis`

### Open The App

| URL | Purpose |
|---|---|
| http://localhost:3000 | Main app |
| http://localhost:8000/docs | Backend API docs |
| http://localhost:8001/docs | AI service API docs |
| http://localhost:11434 | Ollama API |

### Create An Admin User

With the stack running:

```powershell
docker compose exec backend python create_admin.py
```

Follow the prompts to enter an email, password, and optional full name.

## Health Checks

Backend:

```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/health -UseBasicParsing
```

AI service through backend:

```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/health/ai -UseBasicParsing
```

The AI health check should return an `OK` response from Qwen.

## Development Notes

The frontend calls the backend through a relative API path:

```text
/api/v1
```

In Docker, Nginx proxies `/api` to the backend service. This keeps the browser-facing app portable across local and deployed environments.

The backend and AI service call Ollama through Docker networking:

```text
http://ollama:11434
```

## Useful Commands

Start:

```powershell
docker compose up -d
```

Stop:

```powershell
docker compose down
```

View logs:

```powershell
docker compose logs -f backend
docker compose logs -f ai_service
docker compose logs -f ollama
```

Rebuild:

```powershell
docker compose build
```

Delete containers and volumes:

```powershell
docker compose down -v
```

Only use `-v` if you are happy to delete local database data and downloaded Ollama models.

## Project Status

This is an active MVP. The core application flow works, and the next recommended improvements are:

- AI-powered job description parsing
- Stronger hybrid match scoring using keywords and embeddings
- Candidate profile support
- Better CV and cover letter export templates
- More detailed before/after change review
- Deployment-ready secrets and environment configuration

## Copyright

Copyright (c) 2026 Gabriel Humbert. All rights reserved.
