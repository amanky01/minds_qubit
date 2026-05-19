#!/usr/bin/env bash
# Start all agent microservices locally (requires MongoDB + GEMINI_API_KEY in env).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="${ROOT}/services/agents/_shared:${PYTHONPATH:-}"
export AGENT_SERVICE_API_KEY="${AGENT_SERVICE_API_KEY:-dev_agent_service_key}"
export MONGODB_URL="${MONGODB_URL:-mongodb://localhost:27017}"
export GEMINI_API_KEY="${GEMINI_API_KEY:?Set GEMINI_API_KEY}"

pip install -q -e "${ROOT}/packages/agent-contract"
pip install -q -r "${ROOT}/services/agents/_shared/requirements.txt"
pip install -q -r "${ROOT}/services/agents/opportunityalert/requirements.txt"

agents=(codecraft:8010 dataviz:8011 contentcreator:8012 designmaster:8013 languagetutor:8014 researchpro:8015 techblog:8016)
for entry in "${agents[@]}"; do
  id="${entry%%:*}"
  port="${entry##*:}"
  (
    cd "${ROOT}/services/agents/${id}"
    export AGENT_ID="$id" PORT="$port"
    uvicorn main:app --host 0.0.0.0 --port "$port" &
  )
done

(
  cd "${ROOT}/services/agents/opportunityalert"
  export PORT=8017
  uvicorn main:app --host 0.0.0.0 --port 8017 &
)

echo "Agent services started on ports 8010-8017"
