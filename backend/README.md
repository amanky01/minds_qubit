# MindsQubit Core API (Gateway)

FastAPI **core**: authentication, quotas, agent catalog, and HTTP routing to agent microservices in [`../services/agents/`](../services/agents/).

**MongoDB:** connects to **`mindsqubit_core` only** — not `mindsqubit_agent_*` (those belong to chat agent services).

## Setup

1. **Virtualenv** (Python 3.10–3.12 recommended):

```bash
cd backend
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Environment:**

```bash
cp .env.example .env
# Set: JWT_SECRET_KEY, AGENT_SERVICE_API_KEY, AGENT_*_URL for each agent
```

3. **Start agent microservices** (from repo root, before or with core):

```bash
export GEMINI_API_KEY=your_key
export AGENT_SERVICE_API_KEY=dev_agent_service_key   # same value in backend/.env
./scripts/start-agent-services.sh
```

4. **MongoDB** running locally (or set `MONGODB_URL`).

5. **Run core:**

```bash
cd backend && source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Docker (full stack): `docker compose up` from repo root.

## Architecture (this service)

| Module | Role |
| ------ | ---- |
| `api/v1/` | HTTP routes (auth, agents, quota) |
| `api/v1/agents/` | Modular agents API — see [`api/v1/agents/README.md`](api/v1/agents/README.md) |
| `services/agent_catalog.py` | Agent metadata + service URLs |
| `services/agent_gateway.py` | HTTP client to agent microservices |
| `services/quota_service.py` | Limits and usage logs |
| `core/database.py` | `db_manager.central` → `mindsqubit_core` |
| `models/` | Pydantic shapes for central collections |

## API endpoints

### Agents

| Method | Path | Auth |
| ------ | ---- | ---- |
| GET | `/api/v1/agents` | Public (includes `is_live`) |
| GET | `/api/v1/agents/categories` | Public |
| GET | `/api/v1/agents/{agent_id}` | Public |
| GET/POST/PATCH/PUT/DELETE | `/api/v1/agents/{agent_id}/proxy/{path}` | Bearer (live agents only) |

### Auth

| Method | Path |
| ------ | ---- |
| POST | `/api/v1/auth/register` |
| POST | `/api/v1/auth/login` |
| POST | `/api/v1/auth/refresh` |
| GET | `/api/v1/auth/me` |
| GET | `/api/v1/auth/oauth/google` |
| GET | `/api/v1/auth/oauth/github` |

### Quota

| Method | Path |
| ------ | ---- |
| GET | `/api/v1/quota/me` |

## Database (`mindsqubit_core`)

| Collection | Purpose |
| ---------- | ------- |
| `users` | Accounts |
| `subscription_plans` | Plan limits |
| `user_quotas` | Usage counters |
| `usage_logs` | Audit trail |
| `agent_registry` | Synced agent metadata |

See [../Schema.md](../Schema.md).

## Adding an agent

1. Create `services/agents/<id>/` (copy `codecraft` or `_template`) — see [services/agents/README.md](../services/agents/README.md).
2. Add to `services/agent_catalog.py` and `AGENT_<ID>_URL` in `.env`.
3. Register in `docker-compose.yml` and `scripts/start-agent-services.sh`.
4. Set `is_live=True` in `agent_catalog.py` when the service is ready for users.
5. Core routes all agent calls via the generic proxy — see [api/v1/agents/README.md](api/v1/agents/README.md).
6. Restart core to sync `agent_registry`.

## Deploy on Render (core only)

| Setting | Value |
| ------- | ----- |
| Root Directory | `backend` |
| Build | `pip install -r requirements.txt` |
| Start | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| PYTHON_VERSION | `3.10.18` |

Deploy each agent service separately with its own Render service URL, then set `AGENT_*_URL` on the core service to those public URLs (or use private networking).

See also [../Architecture.md](../Architecture.md).
