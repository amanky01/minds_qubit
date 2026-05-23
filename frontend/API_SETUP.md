# Frontend API setup (MindsQubit core)

The frontend talks only to the **core API** at `NEXT_PUBLIC_API_BASE_URL` (default `http://127.0.0.1:8000/`).

## Environment

```bash
# frontend/.env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/
```

## HTTP client

`src/network/core/axiosInstance.js`:

- Attaches `Authorization: Bearer <access_token>` from `localStorage`
- On **401**, refreshes via `POST /api/v1/auth/refresh` and retries once

## Services

| File | Purpose |
| ---- | ------- |
| `src/services/authService.ts` | Register, login, logout, me, token storage |
| `src/services/agentService.ts` | List agents, generic proxy, OpportunityAlert helpers |

### Example: list agents

```typescript
import { agentService } from "@/services/agentService";

const agents = await agentService.getAllAgents();
// each agent has is_live — only opportunityalert is true today
```

### Example: generic proxy (authenticated)

```typescript
import { agentService } from "@/services/agentService";

// Chat (when agent is live)
const data = await agentService.proxyAgent(
  "codecraft",
  "POST",
  "v1/execute",
  { message: "Hello", conversation_id: null }
);

// OpportunityAlert subscribe
await agentService.proxyAgent("opportunityalert", "POST", "v1/subscribe", {
  email: "you@example.com",
  notification_categories: ["daily_digest"],
  opportunity_types: ["internship", "job"],
});
```

### Example: OpportunityAlert helpers

```typescript
await agentService.subscribeOpportunityAlert({
  email: "you@example.com",
  notification_categories: ["daily_digest"],
  opportunity_types: ["internship", "job"],
});
```

## Core endpoints used by the app

| Feature | Endpoint |
| ------- | -------- |
| Register / login | `POST /api/v1/auth/register`, `login` |
| Current user | `GET /api/v1/auth/me` |
| Agents list | `GET /api/v1/agents` (`is_live` per agent) |
| Any agent action | `{METHOD} /api/v1/agents/{id}/proxy/{path}` |
| Quota dashboard | `GET /api/v1/quota/me` |

Full API docs when core is running: `http://localhost:8000/docs`

## Coming soon agents

Agents with `is_live: false` show a Coming soon UI. The proxy returns **503** if called anyway.

## Troubleshooting

| Issue | Check |
| ----- | ----- |
| Network error | Core running on `8000`? `NEXT_PUBLIC_API_BASE_URL` correct? |
| 503 on agent actions | Agent `is_live`? Microservice running? `AGENT_*_URL` in core `.env`? |
| 401 | Log in again; refresh token in `localStorage` |
| CORS | `CORS_ORIGINS` in `backend/.env` includes frontend origin |

## Related

- [README.md](./README.md)
- [../backend/README.md](../backend/README.md)
