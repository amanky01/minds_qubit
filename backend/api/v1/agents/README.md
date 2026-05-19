# Agents API layout

Routes are split so each agent type can grow independently.

```text
api/v1/agents/
  router.py              # mounts sub-routers (entry point for api/v1/router.py)
  integrations.py        # list of per-agent integration routers
  common.py              # shared helpers (quota check, response mapping)
  catalog/               # public catalog (list, categories, get by id)
  chat/                  # generic chat: execute + conversations
  opportunityalert/      # subscribe / update / unsubscribe
  schemas/
    catalog.py
    chat.py
```

## Adding a chat agent

No new API folder needed. Chat agents use:

- `POST /api/v1/agents/{agent_id}/execute`
- `GET /api/v1/agents/{agent_id}/conversations`

Register the agent in `services/agent_catalog.py` and deploy its microservice.

## Adding an integration agent (custom API)

1. Create `api/v1/agents/<agent_id>/` with:
   - `router.py` — FastAPI routes (use `APIRouter(prefix="/<agent_id>")`)
   - `schemas.py` — request/response models
   - `service.py` — calls `agent_gateway.proxy_integration(...)`
   - `__init__.py` — export `router`
2. Append the router to `INTEGRATION_ROUTERS` in `integrations.py`.
3. Add metadata to `services/agent_catalog.py` and deploy the microservice.

Example:

```python
# integrations.py
from api.v1.agents.myagent import router as myagent_router

INTEGRATION_ROUTERS = [
    opportunityalert_router,
    myagent_router,
]
```

URLs stay under `/api/v1/agents/<agent_id>/...` so the frontend gateway contract is stable.
