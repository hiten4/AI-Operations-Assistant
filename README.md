# AI Operations Assistant

A production-style AI-powered operations assistant built with **FastAPI** and **Groq (LLaMA 3)**.

## Features

| Capability | Detail |
|---|---|
| Service status queries | Check health of `payment`, `auth`, `database` |
| Incident creation | Auto-assigns severity based on service status |
| Conversation memory | Resolves pronouns ("it", "that service") using session context |
| Intent routing | LLM classifies every query into `SERVICE_LOOKUP / CREATE_INCIDENT / GENERAL_QUESTION` |
| Validation | Rejects blank/whitespace questions with a clear error |
| Error handling | Unknown services, missing service names, LLM failures all handled gracefully |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Groq API key

```bash
export GROQ_API_KEY="gsk_..."
```

Or create a `.env` file:

```
GROQ_API_KEY=gsk_...
```

### 3. Run

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## API Reference

### POST /ask

**Request**

```json
{ "question": "What is the status of auth service?" }
```

**Response**

```json
{ "answer": "Auth service is degraded with latency 700ms." }
```

**Incident creation response**

```json
{
  "answer": "Incident created successfully.",
  "incident_id": "INC-1001",
  "severity": "Critical"
}
```

### GET /incidents

Returns all incidents created in the current session.

```json
[
  { "id": "INC-1001", "service": "database", "severity": "Critical", "status": "Open" }
]
```

---

## Demo Scenarios

### Scenario 1 – Service lookup

```bash
curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the status of auth service?"}'
```

### Scenario 2 – Incident creation

```bash
curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Database is down. Create an incident."}'
```

### Scenario 3 – Memory (pronoun resolution)

```bash
# Turn 1
curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Check payment service"}'

# Turn 2 – "it" resolves to "payment"
curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Create an incident for it"}'
```

---

## Project Structure

```
project/
├── app.py          # FastAPI app, routes, orchestration
├── models.py       # Pydantic request/response/incident models
├── services.py     # Mock service data, tool implementations
├── memory.py       # In-memory session store
├── llm.py          # Groq SDK: intent classification + response generation
├── requirements.txt
└── README.md
```

---

## Configuration

| Env Var | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | *(required)* | Your Groq API key |
| `GROQ_MODEL` | `llama3-8b-8192` | Override the LLM model |

---

## Mock Services

| Service | Status | Latency |
|---|---|---|
| payment | Healthy | 120ms |
| auth | Degraded | 700ms |
| database | Down | N/A |

## Severity Mapping

| Service Status | Incident Severity |
|---|---|
| Healthy | Low |
| Degraded | Medium |
| Down | Critical |
