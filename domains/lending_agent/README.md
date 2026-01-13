# Lending Agent — Agentic AI Backend (Voice)

This module implements a **production-style lending agent backend** designed for **live phone-call workflows**.
The agent operates as the intelligence layer between **ASR (speech-to-text)** and **TTS (text-to-speech)** services, handling short-turn, real-time conversations and producing structured post-call analytics.

---

## Operating Context

The agent is deployed in a **live telephony environment** with the following interaction flow:

```
Live Phone Call
   → ASR (Speech to Text)
   → Lending Agent Backend (this module)
   → TTS (Text to Speech)
   → Caller
```

ASR and TTS are external services.
This repository focuses exclusively on the **agent intelligence and orchestration layer**.

---

## High-Level Architecture

The lending agent is built using an **agentic workflow pattern**:

1. **Conversation Agent (LangGraph)**
2. **Call Termination Detection**
3. **Post-Call Summarization & Classification**

The agent is optimized for:

* Low latency
* Short, voice-friendly responses
* Deterministic call endings
* Reliable post-call data extraction

---

## Agent Flow

```
Incoming Transcribed Utterance
        ↓
System Prompt Injection
        ↓
LLM Response (short, voice-friendly)
        ↓
Call Status Check (ONGOING / END)
        ↓
If END:
   → Post-Call Summary & Classification
        ↓
Structured JSON Output
```

---

## Key Components

### `app.py`

* Flask-based backend
* LangGraph-driven agent workflow
* Handles conversation state and routing
* Exposes `/chat` API endpoint
* Designed for real-time voice interactions

---

### `prompt.py`

Contains the **compressed system prompt**, including:

* Agent persona
* Conversation flow rules
* Language handling
* Strict JSON termination contract

The prompt is intentionally optimized for:

* Low token usage
* Fast response latency
* Stable ASR → TTS playback

---

## Call Termination Contract

Every agent response **must end** with a JSON object:

```json
{"call_status": "END" or "ONGOING", "language": "<detected_language>"}
```

This contract is used by downstream systems to:

* Control call continuation
* Trigger post-call processing
* Manage ASR/TTS turn-taking

---

## Post-Call Intelligence

When a call ends, the agent performs **post-call summarization** using an LLM.

### Outputs include:

* **Disposition** (Contacted / Not Contacted)
* **Sub-Disposition** (e.g. Not Interested, WIP Call Back, Not Eligible)
* Structured loan-related fields such as:

  * Loan type and amount
  * City and property details
  * Income and employment information
  * Credit and EMI indicators

All extracted fields are returned as **top-level JSON keys** for easy downstream consumption.

---

## Hallucination Control Strategy

To ensure reliable reporting:

* The agent never fabricates loan terms or approvals
* Missing information is explicitly set to `None`
* Default classification rules are applied only when outcomes are unclear
* The agent does not speculate beyond conversation evidence

---

## API Endpoint

### `POST /chat`

#### Request

```json
{
  "user_id": "string",
  "name": "string",
  "message": "string",
  "conversation": [],
  "call_status": "ONGOING"
}
```

#### Response

```json
{
  "agent": "agent response text",
  "call_status": "ONGOING | END",
  "language": "detected_language",
  "summary": "post_call_summary_if_any",
  "conversation": []
}
```

---

## What This Module Demonstrates

* Voice-first agent design
* LangGraph-based agent orchestration
* Deterministic call termination
* Post-call analytics & classification
* Structured data extraction from natural conversations
* Clean separation between conversation and reporting logic

---

## Notes

* External services (ASR, TTS, CRM) are intentionally decoupled
* All identifiers and business references are generic
* The focus is on **architecture, reasoning, and reliability**, not UI or telephony integration

---

## Summary

This lending agent is not a chatbot.
It is a **voice-native, agentic AI backend** built for real call-center environments, combining real-time conversational control with reliable post-call intelligence.

---
