### Insurance Agent — Agentic AI Backend

This module implements a **production-style insurance agent backend** built using an agentic AI architecture.
The agent is designed to conduct structured insurance conversations while remaining grounded in **authoritative quotation data** fetched at startup.

The implementation demonstrates how **LLMs, retrieval, and background processes** can be orchestrated together in a controlled, non-hallucinatory system.

---

## High-Level Design

The insurance agent follows a **three-layer design**:

1. **Agent Orchestration (LangGraph)**
2. **Retrieval-Augmented Context (RAG)**
3. **Preloaded Quotation Intelligence**

Rather than computing or inferring insurance quotes during conversation, the agent relies on **pre-fetched quotation data**, ensuring deterministic and compliant responses.

---

## Architecture Flow

```
Application Startup
        │
        ├── Background Thread
        │     └── Fetch quotation data (dummy external API)
        │     └── Summarize quotation using LLM
        │     └── Store QUOTATION_SUMMARY in shared state
        │
        ▼
System Prompt Construction
        ├── Static agent rules (prompt.py)
        ├── Runtime context (time, user name)
        └── Injected QUOTATION_SUMMARY (single source of truth)
        │
        ▼
User Conversation
        ├── LangGraph-based agent loop
        ├── Optional RAG for policy / knowledge queries
        └── Structured call termination & summarization
```

---

## Real-Time Voice Integration

This agent is designed to operate within a **live phone call environment**.

The overall interaction flow is:

Live Call → ASR → Agent Backend → TTS → Caller

- Incoming user speech is transcribed by an external **Automatic Speech Recognition (ASR)** service.
- The transcribed text is passed to this agent backend via the `/chat` API.
- The agent processes the input using its internal state, quotation context, and retrieval logic.
- The agent’s text response is returned to an external **Text-to-Speech (TTS)** service.
- The synthesized audio is played back to the caller in real time.

ASR and TTS are intentionally kept **outside** the agent backend to ensure:
- Clean separation of concerns
- Backend reusability across voice and text channels
- Independent scaling and optimization of speech services

This repository focuses exclusively on the **agent intelligence layer** that sits between ASR and TTS.

---
## Key Components

### `app.py`

* FastAPI-based backend
* LangGraph-driven agent workflow
* Handles conversation state and routing
* Injects quotation summary dynamically into the system prompt
* Exposes `/chat` endpoint for agent interaction

---

### `prompt.py`

Contains the **static system prompt**, including:

* Agent persona
* Conversation rules
* Output format constraints
* Anti-hallucination instructions

This file does **not** contain any dynamic or runtime data.

---

### `quotation.py`

Implements **startup-time quotation intelligence**:

* Runs a background thread at application startup
* Calls a simulated external quotation API
* Summarizes raw quotation JSON using an LLM
* Stores a clean `QUOTATION_SUMMARY` in shared state

This summary is later injected into the system prompt and treated as the **single source of truth** during the conversation.

---

### `rag.py`

Implements **retrieval-augmented context**:

* Vector-based document retrieval
* Supplies policy or informational context when needed
* Does not override quotation data
* Complements, rather than replaces, deterministic information

---

## Hallucination Control Strategy

To prevent hallucinations and inconsistent insurance information:

* Quotation data is fetched **before** any user interaction
* The summarized quotation is injected into the system prompt
* The agent is explicitly instructed to **override all general knowledge** using quotation data when present
* Quotes are **never generated dynamically** during the conversation

This pattern ensures predictable and compliant responses.

---

## API Endpoint

### POST `/chat`

**Request Payload**

```json
{
  "user_id": "string",
  "name": "string",
  "message": "string",
  "conversation": [],
  "session_id": "string",
  "call_status": "ONGOING"
}
```

**Response Payload**

```json
{
  "session_id": "string",
  "agent": "response text",
  "call_status": "ONGOING | END",
  "language": "detected_language",
  "summary": "final_call_summary_if_any"
}
```

---

## What This Module Demonstrates

* Agentic AI design using LangGraph
* Background task orchestration
* Prompt mutation with authoritative data
* Safe use of LLMs for summarization (not decision-making)
* Clear separation between static rules and dynamic context
* Production-style FastAPI backend patterns

---

## Notes

* External APIs are simulated to avoid proprietary exposure
* All identifiers and domain references are intentionally generic
* This module is designed to showcase **architecture and reasoning**, not business-specific details

---

## Summary

This insurance agent is not a chatbot.
It is an **agentic backend system** that demonstrates how LLMs can be safely integrated into regulated workflows using controlled context injection, background intelligence loading, and explicit override rules.

---
