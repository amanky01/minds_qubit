# AI Agents Platform Backend

FastAPI backend for the AI Agents Platform with modular agent architecture.

## Setup

1. Install dependencies (includes **motor** for MongoDB). **Use a virtual environment** — required on macOS/Homebrew Python (`externally-managed-environment`; global `pip install` is blocked). Use **Python 3.10–3.12** (not 3.14): `pydantic-core` has prebuilt wheels for those versions; 3.14 triggers a Rust build that fails on Render.
```bash
cd backend
python3.10 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Always start the app with **that same environment** (activated shell, or `backend/.venv/bin/python` / `backend/.venv/bin/uvicorn`). If you still see `No module named 'motor'`, you are not using the venv’s Python.

2. Copy `.env.example` to `.env` in the backend directory and set variables. All config is read from env (see `core/config.py`). Example:
```bash
cp .env.example .env
# Edit .env with your values
```
Optional env vars: `ENV_FILE` (default `.env`), `MONGODB_URL`, `DATABASE_NAME`, `JWT_*`, `GEMINI_API_KEY`, `GEMINI_MODEL` (default `gemini-1.5-flash`), `GOOGLE_*`, `GITHUB_*`, `CORS_ORIGINS`, `OAUTH_REDIRECT_URL`, `HOST`, `PORT`.

3. Make sure MongoDB is running

4. Run the server (from `backend`, with venv active **or** use paths below):
```bash
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Without activating the venv:
```bash
cd backend
.venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Or:
```bash
.venv/bin/python main.py
```

## Architecture

- **Core**: Configuration, database, security, dependencies
- **API**: REST API endpoints (auth and agents)
- **Agents**: Modular agent files (each agent is a separate file)
- **Models**: MongoDB data models
- **Services**: Business logic (Gemini service, agent executor)

## Adding a New Agent

1. Create a new file in `agents/` directory (e.g., `agents/myagent.py`)
2. Inherit from `BaseAgent` and implement required methods
3. Restart the server - the agent will be automatically discovered and registered

## API Endpoints

### Agents
- `GET /api/v1/agents` - List all agents (public)
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `GET /api/v1/agents/categories` - Get all categories
- `POST /api/v1/agents/{agent_id}/execute` - Execute agent (requires auth)
- `GET /api/v1/agents/{agent_id}/conversations` - Get conversation history (requires auth)

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user (requires auth)

## Deploy on Render

Render **does not** read `render.yaml` for services you create in the dashboard (that file is only for [Blueprints](https://render.com/docs/blueprint-spec)). Configure everything in the service **Settings** and **Environment**:

| Setting | Value |
|--------|--------|
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Environment → PYTHON_VERSION** | `3.10.18` |

Also commit `backend/runtime.txt` (`python-3.10.18`). If the build log still shows `python3.14`, set **PYTHON_VERSION** in the dashboard (that overrides the default). Then **Manual Deploy → Clear build cache & deploy**.

## Database

MongoDB database: `ai_agents_platform`

Collections:
- `users` - User accounts
- `agents` - Agent metadata (synced from agent files)
- `agent_conversations` - Conversation history
