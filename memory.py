"""Simple in-memory session store for conversation context."""

from typing import Optional

# Keyed by session_id; stores lightweight context per session
MEMORY: dict[str, dict] = {
    "default": {}
}


def get_session(session_id: str = "default") -> dict:
    """Retrieve or initialise a session context."""
    if session_id not in MEMORY:
        MEMORY[session_id] = {}
    return MEMORY[session_id]


def set_last_service(service: str, session_id: str = "default") -> None:
    """Persist the most-recently referenced service for a session."""
    get_session(session_id)["last_service"] = service.lower()


def get_last_service(session_id: str = "default") -> Optional[str]:
    """Return the last service mentioned in this session, if any."""
    return get_session(session_id).get("last_service")
