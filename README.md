# MindsQubit

Multi-agent AI platform: **Next.js** frontend, **FastAPI core** (gateway), and **one microservice per agent**.

## Architecture (modular)

| Layer | Folder | Role |
| ----- | ------ | ---- |
| Frontend | `frontend/` | UI; calls core only (`/api/v1/*`) |
| Core API | `backend/` | Auth, quotas, agent catalog; **MongoDB: `mindsqubit_core` only** |
| Agent services | `services/agents/` | Chat (Gemini + own DB) or integrations (e.g. OpportunityAlert) |
| Contract | `packages/agent-contract/` | Shared HTTP schemas between core and agents |

```text
Browser → Core (8000) → Agent services (8010–8017)
              ↓
         mindsqubit_core
```

Details: [Architecture.md](./Architecture.md) · DB schema: [Schema.md](./Schema.md)

## Quick start

**Prerequisites:** MongoDB, Python 3.10–3.12, Node.js, `GEMINI_API_KEY` for chat agents.

```bash
# 1. Core
cd backend && cp .env.example .env && pip install -r requirements.txt
# Edit .env (JWT_SECRET_KEY, AGENT_*_URL for each agent)

# 2. Agent services (from repo root)
export GEMINI_API_KEY=your_key
./scripts/start-agent-services.sh

# 3. Core server
cd backend && uvicorn main:app --reload

# 4. Frontend
cd frontend && cp .env.example .env && npm install && npm run dev
```

Or: `docker compose up` (set `GEMINI_API_KEY` in the environment).

## Agents

| Id | Type | Port |
| ---- | ---- | ---- |
| codecraft, dataviz, contentcreator, designmaster, languagetutor, researchpro, techblog | chat | 8010–8016 |
| opportunityalert | email subscriptions → [Opportunity Crawler](https://opportunity-crawler.onrender.com/docs) | 8017 |

## Documentation

| Doc | Contents |
| --- | -------- |
| [Architecture.md](./Architecture.md) | System design, auth, quotas, microservices |
| [Schema.md](./Schema.md) | `mindsqubit_core` collections only |
| [backend/README.md](./backend/README.md) | Core API setup & deploy |
| [services/agents/README.md](./services/agents/README.md) | Agent microservices |
| [frontend/README.md](./frontend/README.md) | Frontend setup |
| [frontend/API_SETUP.md](./frontend/API_SETUP.md) | Frontend ↔ core API |

## Add a new agent

1. Copy `services/agents/codecraft/` or `_template/`
2. Register in `backend/services/agent_catalog.py` and `AGENT_<ID>_URL` in `backend/.env`
3. Add to `docker-compose.yml` and `scripts/start-agent-services.sh`
4. Optional: `frontend/src/config/agentUIConfig.tsx` for custom UI
