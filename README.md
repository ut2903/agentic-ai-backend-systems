
# Agentic AI Backend Systems

This repository presents a collection of **production-inspired, agentic AI backends** designed for **real-time voice interactions** in enterprise environments.

The systems here operate as the **intelligence layer** between speech services (ASR/TTS) and downstream business systems, handling conversational control, reasoning, and post-call intelligence.  
This is **not a chatbot repository** — it focuses on **agent orchestration, control, and reliability** in real deployments.

---

## Operating Context: Voice-First Systems

All agents in this repository are designed to run in **live phone-call workflows**:

```

Live Phone Call
→ ASR (Speech to Text)
→ Agent Backend (this repository)
→ TTS (Text to Speech)
→ Caller

```

- ASR and TTS are external services
- The agent backend is channel-agnostic
- The same agents can be reused across voice or text channels

This repository intentionally focuses only on the **agent intelligence layer**.

---

## What This Repository Demonstrates

- Agentic AI system design using **explicit workflows**
- Real-time, short-turn conversational agents
- Deterministic call termination and state control
- Background context loading and prompt mutation
- Post-call summarization and structured classification
- Clean separation between:
  - Conversation
  - Retrieval
  - Reporting
  - Infrastructure

The emphasis is on **engineering trade-offs**, not UI or demos.

---

## LLM Provider Agnostic Design

The agents in this repository are **not tied to any single LLM provider**.

While example implementations may use specific SDKs or hosted models, the architecture supports:

- Cloud-hosted LLMs
- Region-specific or sovereign LLM providers
- Open-source or self-hosted models
- Custom or enterprise inference endpoints

The **agent logic, orchestration, and control flow remain unchanged** regardless of the underlying LLM.

---

## Repository Structure

```

agentic-ai-backend-systems/
│
├── domains/
│   ├── insurance_agent/
│   │   ├── app.py
│   │   ├── prompt.py
│   │   ├── quotation.py
│   │   ├── rag.py
│   │   └── README.md
│   │
│   ├── lending_agent/
│   │   ├── app.py
│   │   ├── prompt.py
│   │   └── README.md
│
├── config/
│
└── README.md

```

Each domain represents a **real-world agent**, optimized for a specific conversational objective while following a common architectural philosophy.

---

## Agent Design Philosophy

### 1. Explicit Agent Workflows
Agents are implemented as **stateful workflows**, not single-prompt calls.  
This enables:
- Conditional routing
- Deterministic endings
- Post-call processing
- Better observability and control

---

### 2. Controlled Context Injection
Authoritative data (e.g., insurance quotations) is:
- Fetched at application startup
- Summarized once
- Injected into the system prompt
- Treated as the **single source of truth**

This prevents hallucination and ensures compliance in regulated conversations.

---

### 3. Strict Output Contracts
All conversational responses end with a **structured JSON block** that communicates:
- Call status (ONGOING / END)
- Detected language

This contract allows downstream systems to reliably manage:
- Turn-taking
- Call flow
- Analytics triggers

---

### 4. Post-Call Intelligence
When a call ends, agents perform structured post-call analysis to produce:
- Call disposition and sub-disposition
- Domain-specific structured fields
- Clean JSON outputs suitable for CRM, reporting, or analytics pipelines

Conversation and reporting are **deliberately separated**.

---

## Included Agents

### Insurance Agent
- Voice-first conversational agent
- Background quotation preload via external API
- Retrieval-augmented knowledge access
- Prompt-level override rules for authoritative data
- Post-call summarization

### Lending Agent
- Voice-optimized lending conversations
- Compressed, latency-aware system prompts
- Deterministic call termination
- Detailed post-call classification and field extraction

Each agent has its own domain-level README describing internal flow and decisions.

---

## What Is Intentionally Excluded

- UI or frontend applications
- Telephony infrastructure
- ASR / TTS implementations
- Authentication and authorization
- Model training or fine-tuning code

These exclusions are deliberate to keep the repository focused on **agent intelligence and orchestration**.

---

## Intended Audience

This repository is intended for:
- Engineers building AI agents for real systems
- Teams exploring agentic workflows beyond chatbots
- Architectural and technical interviews
- Discussions around safe, controllable LLM usage

It reflects **real deployment patterns**, not tutorial examples.

---

## Summary

This repository demonstrates how large language models can be used as **components within larger systems**, rather than standalone chat interfaces.

The focus is on **architecture, control, and reliability** — the qualities that matter most when AI systems interact with real users in real time.
```


