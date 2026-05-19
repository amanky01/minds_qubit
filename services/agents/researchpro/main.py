import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))

from chat_runtime.app import create_chat_app
from chat_runtime.configs import RESEARCHPRO

app = create_chat_app(RESEARCHPRO)

if __name__ == "__main__":
    import uvicorn
    from chat_runtime.settings import Settings

    s = Settings(AGENT_ID="researchpro")
    uvicorn.run("main:app", host=s.HOST, port=s.PORT, reload=True)
