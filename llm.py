"""LLM integration via Groq SDK for intent classification and response generation."""

import json
import logging
import os
from typing import Optional

from groq import Groq

logger = logging.getLogger(__name__)

# Initialise Groq client (reads GROQ_API_KEY from environment)
_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

# Model to use; override via GROQ_MODEL env var
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama3-8b-8192")

_INTENT_SYSTEM_PROMPT = """
You are an AI operations assistant that classifies user queries into structured intents.

Available intents:
- SERVICE_LOOKUP  : User wants to know the health/status of a service.
- CREATE_INCIDENT : User wants to create an incident for a service.
- GENERAL_QUESTION: Anything else.

Known services: payment, auth, database.

If the query refers to "it" or a pronoun, the caller will resolve the service; output null for service.

Respond ONLY with valid JSON, no markdown, no extra text.

Schema:
{
  "intent": "SERVICE_LOOKUP" | "CREATE_INCIDENT" | "GENERAL_QUESTION",
  "service": "<service_name_lower_case_or_null>"
}
""".strip()


def classify_intent(question: str, last_service: Optional[str] = None) -> dict:
    """
    Use the LLM to classify the user's question into a structured intent.

    Falls back to GENERAL_QUESTION on any failure.
    """
    context = f'Last mentioned service: "{last_service}".' if last_service else ""
    user_prompt = f"{context}\n\nUser question: {question}".strip()

    try:
        response = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": _INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_tokens=150,
        )
        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)
        return parsed
    except json.JSONDecodeError as exc:
        logger.warning("LLM returned non-JSON intent: %s", exc)
    except Exception as exc:
        logger.error("LLM classify_intent failed: %s", exc)

    return {"intent": "GENERAL_QUESTION", "service": None}


_RESPONSE_SYSTEM_PROMPT = """
You are a concise AI operations assistant.
Answer the user's question in one or two sentences using the data provided.
Do not mention JSON or internal structures.
""".strip()


def generate_response(question: str, context: str) -> str:
    """
    Ask the LLM to produce a human-friendly response given question + context data.

    Returns a fallback string if the call fails.
    """
    user_prompt = f"Question: {question}\n\nContext data:\n{context}"

    try:
        response = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": _RESPONSE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.error("LLM generate_response failed: %s", exc)
        return "Unable to process request right now."
