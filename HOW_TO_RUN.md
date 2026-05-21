# How to Run the AI Career Platform

## Architecture Overview

The project runs as a full Docker Compose stack:

| Service | Port | Description |
|---|---:|---|
| `frontend` | 3000 | React app served by Nginx |
| `backend` | 8000 | FastAPI backend API |
| `ai_service` | 8001 | FastAPI AI gateway for text generation |
| `ollama` | 11434 | Local model server running inside Docker |
| `db` | 5433 | PostgreSQL database |
| `redis` | 6379 | Redis cache |

The app uses:

- Text generation model: `qwen2.5:7b`
- Embedding model: `nomic-embed-text`

Both models are downloaded into the `ollama_data` Docker volume the first time the stack starts.

---

## Prerequisites

- Docker Desktop installed and running
- Git
- Enough free disk space for the Ollama models

You do not need Ollama installed separately on Windows for the Docker setup.

---

## Option A - Full Docker Setup

### Step 1 - Clone and enter the project

```bash
git clone <repo-url>
cd "CV project"
```

If you already have the project locally, just open a terminal in the project folder.

### Step 2 - Build and start all services

```bash
docker compose up --build
```

On the first run, Docker will:

1. Start PostgreSQL and Redis
2. Start Ollama inside Docker
3. Pull `qwen2.5:7b`
4. Pull `nomic-embed-text`
5. Build the backend, frontend, and AI service images
6. Run database migrations inside the backend container
7. Start the web app

The first run can take a while because the models need to download. Later starts are much faster because the models are kept in the `ollama_data` volume.

### Step 3 - Create the first admin user

Open a new terminal while the containers are running:

```bash
docker exec -it cv_platform_backend python create_admin.py
```

Follow the prompts to enter email, password, and an optional full name.

### Step 4 - Open the app

| URL | What it is |
|---|---|
| http://localhost:3000 | Frontend app |
| http://localhost:8000/docs | Backend API docs |
| http://localhost:8001/docs | AI service API docs |
| http://localhost:11434 | Ollama API |

---

## Option B - Local Development

Use this if you want hot reload for the backend or frontend while still running infrastructure in Docker.

### Step 1 - Start shared services

```bash
docker compose up db redis ollama ollama_init ai_service
```

### Step 2 - Set up the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql://cvuser:cvpassword@localhost:5433/cv_platform
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-me-before-deploy-use-openssl-rand-hex-32
AI_SERVICE_URL=http://localhost:8001
AI_PROVIDER=local
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
EMBEDDING_MODEL=nomic-embed-text
BACKEND_CORS_ORIGINS=http://localhost:3000
```

Run migrations and start the backend:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Step 3 - Set up the frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

The frontend dev server runs at http://localhost:3000.

---

## Stopping the Project

```bash
docker compose down
```

To stop the project and delete database/model volumes:

```bash
docker compose down -v
```

Only use `-v` if you are happy to delete local database data and downloaded Ollama models.

---

## Common Issues

**First startup is slow**

This is normal. The first run downloads `qwen2.5:7b` and `nomic-embed-text`.

**AI service returns 503**

Check that the model initialization container completed successfully:

```bash
docker compose ps
docker compose logs ollama_init
```

**Frontend shows network errors**

In Docker, the frontend proxies `/api` to the backend through Nginx. Confirm the backend is running:

```bash
docker compose logs backend
```

**Migration errors on startup**

Check the backend logs and confirm the database is healthy:

```bash
docker compose logs db
docker compose logs backend
```
