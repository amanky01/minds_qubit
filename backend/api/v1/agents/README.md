# Agents API layout

All agent traffic goes through a **single generic proxy**. The catalog exposes which agents are live.

```text
api/v1/agents/
  router.py              # list + mount proxy + catalog
  proxy/router.py        # /{agent_id}/proxy/{path}  (GET, POST, PATCH, PUT, DELETE)
  catalog/               # GET /agents, /categories, /{agent_id}
  common.py              # quota check, response mapping
  schemas/
    catalog.py           # AgentResponse (includes is_live)
```

## Generic proxy

Authenticated clients call:

```http
POST /api/v1/agents/{agent_id}/proxy/v1/execute
PATCH /api/v1/agents/opportunityalert/proxy/v1/subscribe
GET /api/v1/agents/codecraft/proxy/v1/conversations?user_id=...
```

Core forwards to `{agent.service_url}/{path}` with service headers (`X-Service-Key`, `X-User-Id`, etc.).

- **503** if `is_live` is false on the agent in [`agent_catalog.py`](../../../services/agent_catalog.py)
- **Quota** checked before POST / PATCH / PUT; usage recorded after successful POST

## `is_live` flag

Set `is_live=True` in `AGENT_CATALOG` when the microservice is ready for users. Only live agents accept proxy calls (UI should gate non-live agents as "Coming soon").

## Adding an agent

1. Deploy microservice under `services/agents/<id>/` with the HTTP routes it needs.
2. Add entry to `services/agent_catalog.py` with `service_url` and `is_live=True` when ready.
3. Add `AGENT_<ID>_URL` to core `.env`.
4. Frontend: entry in `agentUIConfig.tsx` for visuals / UI type (chat form vs subscription form).

No per-agent core router folder is required — the proxy handles all agents uniformly.

## Examples

| Agent | Proxy path | Upstream |
|-------|------------|----------|
| codecraft | `POST .../proxy/v1/execute` | `{CODECRAFT_URL}/v1/execute` |
| opportunityalert | `POST .../proxy/v1/subscribe` | `{OPP_URL}/v1/subscribe` |
