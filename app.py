"""AI Operations Assistant – FastAPI entry point."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from llm import classify_intent, generate_response
from memory import get_last_service, set_last_service
from models import AskRequest, AskResponse, Incident
from services import create_incident, get_service_status, list_incidents
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Operations Assistant", version="1.0.0")


# ---------------------------------------------------------------------------
# Validation error handler – convert Pydantic errors to our schema
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"error": "Question cannot be empty"},
    )


# ---------------------------------------------------------------------------
# POST /ask
# ---------------------------------------------------------------------------

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> Any:
    """
    Main conversational endpoint.

    Flow:
    1. Classify the intent via LLM (with session memory context).
    2. Execute the appropriate tool (service lookup or incident creation).
    3. Generate a natural-language answer via LLM.
    4. Update session memory.
    """
    question = request.question
    session_id = "default"  # Single-session demo; extend with auth headers as needed.

    # --- Intent classification ---
    last_service = get_last_service(session_id)
    intent_data = classify_intent(question, last_service=last_service)

    intent = intent_data.get("intent", "GENERAL_QUESTION")
    # Resolve pronouns: if LLM returned null service, fall back to memory
    service: str | None = intent_data.get("service") or last_service

    logger.info("Intent=%s  Service=%s", intent, service)

    # --- Tool dispatch ---

    if intent == "SERVICE_LOOKUP":
        if not service:
            return AskResponse(answer="Which service would you like to check?")

        info = get_service_status(service)
        if info is None:
            return AskResponse(answer=f"Service '{service}' not found.")

        # Persist for future pronoun resolution
        set_last_service(service, session_id)

        context = f"Service: {service}\nStatus: {info['status']}\nLatency: {info['latency']}"
        answer = generate_response(question, context)
        return AskResponse(answer=answer)

    elif intent == "CREATE_INCIDENT":
        if not service:
            return AskResponse(
                answer="Which service would you like to create an incident for?"
            )

        # Verify service exists before creating an incident
        if get_service_status(service) is None:
            return AskResponse(answer=f"Service '{service}' not found.")

        result = create_incident(service)
        set_last_service(service, session_id)

        return AskResponse(
            answer="Incident created successfully.",
            incident_id=result["incident_id"],
            severity=result["severity"],
        )

    else:
        # GENERAL_QUESTION – let the LLM answer freely
        answer = generate_response(question, context="No specific service data available.")
        return AskResponse(answer=answer)


# ---------------------------------------------------------------------------
# GET /incidents
# ---------------------------------------------------------------------------

@app.get("/incidents", response_model=list[Incident])
async def incidents() -> list[Incident]:
    """Return all incidents created in this session."""
    return list_incidents()
