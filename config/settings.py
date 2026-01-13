import os

# =========================
# LLM Provider Configuration
# =========================
# This repository is intentionally provider-agnostic.
# Any LLM backend (cloud-hosted or self-hosted) can be used
# as long as it exposes a chat-style inference interface.

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
# Examples: openai, sarvam, mistral, llama, custom

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT")
LLM_API_VERSION = os.getenv("LLM_API_VERSION")
LLM_DEPLOYMENT_NAME = os.getenv("LLM_DEPLOYMENT_NAME")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

MAX_RESPONSE_TOKENS = int(os.getenv("MAX_RESPONSE_TOKENS", "90"))

# =========================
# Runtime Defaults
# =========================

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "English")

# =========================
# Retrieval / Knowledge Settings
# =========================

VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "qdrant")
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")
VECTOR_DB_API_KEY = os.getenv("VECTOR_DB_API_KEY")
VECTOR_COLLECTION_NAME = os.getenv("VECTOR_COLLECTION_NAME", "agent_docs")

ENABLE_RAG = os.getenv("ENABLE_RAG", "true").lower() == "true"

# =========================
# Domain-Specific Flags
# =========================

ENABLE_QUOTATION_PRELOAD = (
    os.getenv("ENABLE_QUOTATION_PRELOAD", "true").lower() == "true"
)
