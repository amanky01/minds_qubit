# AI Agents Platform Backend

FastAPI backend for the AI Agents Platform with modular agent architecture.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the backend directory with the following variables:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ai_agents_platform
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
CORS_ORIGINS=http://localhost:3000
OAUTH_REDIRECT_URL=http://localhost:8000/api/v1/auth/oauth
```

3. Make sure MongoDB is running

4. Run the server:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or:
```bash
cd backend
python main.py
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

## Database

MongoDB database: `ai_agents_platform`

Collections:
- `users` - User accounts
- `agents` - Agent metadata (synced from agent files)
- `agent_conversations` - Conversation history
