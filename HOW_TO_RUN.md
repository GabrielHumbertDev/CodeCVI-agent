# How to Run the AI Career Platform

## Architecture Overview

The project has four services that work together:

| Service | Port | Description |
|---|---|---|
| `db` | 5433 | PostgreSQL database |
| `redis` | 6379 | Redis cache |
| `ai_service` | 8001 | FastAPI AI service (calls Ollama) |
| `backend` | 8000 | FastAPI backend API |
| `frontend` | 3000 | React frontend (served via Nginx) |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Ollama](https://ollama.com/) installed on your host machine
- Git

---

## Option A — Docker (Recommended, runs everything together)

### Step 1 — Start Ollama and pull the AI model

Ollama must be running on your host machine **before** starting Docker. The containers will connect to it via `host.docker.internal:11434`.

```bash
# Pull the model (only needed once, ~4 GB download)
ollama pull qwen2.5:7b

# Start Ollama (if not already running as a service)
ollama serve
```

### Step 2 — Clone and enter the project

```bash
git clone <repo-url>
cd "CV project"
```

### Step 3 — Build and start all services

```bash
docker compose up --build
```

This will:
1. Build images for `backend`, `frontend`, and `ai_service`
2. Start PostgreSQL and Redis
3. Run `alembic upgrade head` (database migrations) automatically inside the backend container
4. Start all five services

Wait until you see the backend log: `Application startup complete.`

### Step 4 — Create the first admin user

Open a new terminal while the containers are running:

```bash
docker exec -it cv_platform_backend python create_admin.py
```

Follow the prompts — enter email, password, and an optional full name.

### Step 5 — Open the app

| URL | What it is |
|---|---|
| http://localhost:3000 | Frontend (main app) |
| http://localhost:8000/docs | Backend API (Swagger UI) |
| http://localhost:8001/docs | AI Service API |

---

## Option B — Local Development (run services manually)

Use this if you want hot-reload on the backend or frontend without rebuilding Docker images.

### Step 1 — Start infrastructure via Docker

```bash
docker compose up db redis ai_service
```

This starts only PostgreSQL, Redis, and the AI service in Docker.

### Step 2 — Set up the backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create a .env file
```

Create `backend/.env` with:

```env
DATABASE_URL=postgresql://cvuser:cvpassword@localhost:5433/cv_platform
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-me-before-deploy-use-openssl-rand-hex-32
AI_SERVICE_URL=http://localhost:8001
AI_PROVIDER=local
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

### Step 3 — Run database migrations

```bash
# Still inside backend/ with venv active
alembic upgrade head
```

### Step 4 — Start the backend server

```bash
uvicorn app.main:app --reload --port 8000
```

### Step 5 — Create the first admin user

In a new terminal (with venv active, from the `backend/` folder):

```bash
python create_admin.py
```

To promote an existing user to admin instead:

```bash
python create_admin.py --promote admin@example.com
```

### Step 6 — Set up the frontend

```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Start the dev server
npm start
```

The frontend dev server runs at http://localhost:3000 and proxies API calls to http://localhost:8000.

---

## Stopping the Project

```bash
# Stop all containers (keeps data)
docker compose down

# Stop and delete all data (database volume)
docker compose down -v
```

---

## Common Issues

**Backend can't connect to the database**
Make sure the `db` container is healthy before the backend starts. With Docker Compose this is handled automatically via `depends_on` health checks. For local dev, confirm PostgreSQL is running on port 5433.

**AI service returns 503**
Ollama is not running or the model is not pulled. Run `ollama serve` on your host and confirm `ollama pull qwen2.5:7b` completed.

**Frontend shows network errors**
The backend must be reachable at port 8000. For local dev, confirm `uvicorn` is running. For Docker, confirm all containers are up with `docker compose ps`.

**Migration errors on startup**
If you see `alembic upgrade head` failing, check `DATABASE_URL` in your `.env` (local dev) or that the `db` container is healthy (Docker).
