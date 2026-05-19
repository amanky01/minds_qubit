# MindsQubit Frontend

Next.js app for the MindsQubit platform. All API calls go to the **core gateway** (`NEXT_PUBLIC_API_BASE_URL`), never to agent microservices directly.

## Features

- Agent catalog (loaded from `GET /api/v1/agents`)
- Per-agent chat UI (`/agent/[id]`)
- OpportunityAlert subscription UI (`/agent/opportunityalert`)
- JWT auth (login, register, OAuth callback)
- Category filtering on the home page
- **Dashboard** (`/dashboard`) — plan limits and per-agent usage (`GET /api/v1/quota/me`)
- **Logged-in home** — `/` shows a welcome hero and agents grid for authenticated users; guests see the full marketing page (About section included)

## Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:3000`. Ensure **core** (`:8000`) and **agent services** (`:8010–8017`) are running — see [../README.md](../README.md).

## Environment

| Variable | Example |
| -------- | ------- |
| `NEXT_PUBLIC_API_BASE_URL` | `http://127.0.0.1:8000/` |

Trailing slash is optional; see `src/network/config/config.js`.

## Project structure

```text
frontend/src/
├── components/       # Header, AgentCard, OpportunityAlertSubscription, …
├── config/
│   └── agentUIConfig.tsx   # Per-agent visuals; uiType: chat | subscription
├── contexts/
│   └── AuthContext.tsx
├── network/
│   ├── config/config.js
│   └── core/axiosInstance.js   # JWT + refresh
├── pages/
│   ├── index.tsx
│   ├── dashboard.tsx
│   ├── login.tsx
│   ├── agent/[id].tsx
│   └── auth/callback.tsx
├── services/
│   ├── agentService.ts
│   ├── authService.ts
│   └── quotaService.ts
└── styles/
```

## Customizing an agent UI

1. Add entry in `src/config/agentUIConfig.tsx` (banner, colors, `uiType`).
2. For non-chat agents, set `uiType: "subscription"` and wire API methods in `agentService.ts`.
3. Agent metadata (name, description) comes from the core API — no static list required.

## API integration

See [API_SETUP.md](./API_SETUP.md).

## Related docs

- [../Architecture.md](../Architecture.md)
- [../backend/README.md](../backend/README.md)
