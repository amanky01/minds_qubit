# Agent microservices

Each agent is a separate FastAPI process. The **core** (`backend/`) calls them over HTTP; the frontend never talks to these URLs directly.

## Layout

```text
services/agents/
├── _shared/chat_runtime/   # Gemini, conversations, /v1/execute
├── _template/              # Starting point for new chat agents
├── codecraft/ … techblog/  # Thin main.py per chat agent
└── opportunityalert/       # Proxies Opportunity Crawler subscribe API
```

## Chat agents

**Env** (see `.env.example`):

| Variable | Purpose |
| -------- | ------- |
| `AGENT_ID` | e.g. `codecraft` |
| `PORT` | e.g. `8010` |
| `MONGODB_URL` | MongoDB cluster |
| `AGENT_DB_PREFIX` | Default `mindsqubit_agent_` → DB `mindsqubit_agent_<id>` |
| `GEMINI_API_KEY` | Required for chat |
| `AGENT_SERVICE_API_KEY` | Must match core |

**Endpoints (internal):**

- `GET /health`
- `POST /v1/execute` — body: `{ message, conversation_id? }`
- `GET /v1/conversations?user_id=`

## OpportunityAlert

**Env:** `OPPORTUNITY_CRAWLER_URL`, `AGENT_SERVICE_API_KEY`, `PORT=8017`

**Endpoints:** `POST/PATCH /v1/subscribe`, `POST /v1/unsubscribe` → upstream crawler.

No Gemini, no agent MongoDB.

## Run one agent locally

```bash
pip install -e ../../packages/agent-contract
pip install -r _shared/requirements.txt
cd codecraft
export AGENT_ID=codecraft PORT=8010 GEMINI_API_KEY=... AGENT_SERVICE_API_KEY=...
uvicorn main:app --reload --port 8010
```

Or use `./scripts/start-agent-services.sh` from the repo root.
