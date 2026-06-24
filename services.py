"""Service data, tool implementations, and business logic."""

from typing import Optional
from models import Incident

# Mock service registry
SERVICES: dict[str, dict[str, str]] = {
    "payment": {"status": "Healthy", "latency": "120ms"},
    "auth": {"status": "Degraded", "latency": "700ms"},
    "database": {"status": "Down", "latency": "N/A"},
}

# In-memory incident store
INCIDENTS: list[Incident] = []

# Severity mapping based on service status
SEVERITY_MAP: dict[str, str] = {
    "Healthy": "Low",
    "Degraded": "Medium",
    "Down": "Critical",
}

_incident_counter = 1000


def get_service_status(service_name: str) -> Optional[dict[str, str]]:
    """
    Retrieve mock status for a named service.

    Returns None if the service is not found.
    """
    return SERVICES.get(service_name.lower())


def create_incident(service_name: str) -> dict[str, str]:
    """
    Create and store an incident for the given service.

    Severity is derived from the current service status.
    Returns the incident_id and severity.
    """
    global _incident_counter
    _incident_counter += 1

    service_info = get_service_status(service_name)
    status = service_info["status"] if service_info else "Unknown"
    severity = SEVERITY_MAP.get(status, "Medium")

    incident = Incident(
        id=f"INC-{_incident_counter}",
        service=service_name.lower(),
        severity=severity,
    )
    INCIDENTS.append(incident)

    return {"incident_id": incident.id, "severity": severity}


def list_incidents() -> list[Incident]:
    """Return all stored incidents."""
    return INCIDENTS
