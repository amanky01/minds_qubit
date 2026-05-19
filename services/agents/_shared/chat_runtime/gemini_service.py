from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self, api_key: str, model_name: str) -> None:
        self._model = None
        if not api_key:
            logger.warning("GEMINI_API_KEY not set")
        else:
            try:
                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel(model_name)
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to initialize Gemini: %s", exc)

    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not self._model:
            raise RuntimeError("Gemini API key not configured")

        history = []
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg.get("role") == "user" else "model"
                history.append({"role": role, "parts": [msg.get("content", "")]})

        history.append({"role": "user", "parts": [user_message]})

        generation_config = genai.types.GenerationConfig(
            temperature=config.get("temperature", 0.7) if config else 0.7,
            max_output_tokens=config.get("max_output_tokens", 2048) if config else 2048,
            top_p=config.get("top_p", 0.95) if config else 0.95,
            top_k=config.get("top_k", 40) if config else 40,
        )

        chat = self._model.start_chat(history=history[:-1] if len(history) > 1 else [])
        response = chat.send_message(
            f"{system_prompt}\n\nUser: {user_message}",
            generation_config=generation_config,
        )
        return response.text
