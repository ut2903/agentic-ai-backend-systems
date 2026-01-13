import os

# =========================
# Azure OpenAI Configuration
# =========================

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")


# =========================
# Application Settings
# =========================

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "English")
MAX_RESPONSE_TOKENS = int(os.getenv("MAX_RESPONSE_TOKENS", "90"))


# =========================
# Vector / Retrieval Settings
# =========================

VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")
VECTOR_DB_API_KEY = os.getenv("VECTOR_DB_API_KEY")
VECTOR_COLLECTION_NAME = os.getenv("VECTOR_COLLECTION_NAME", "agent_docs")


# =========================
# Runtime Flags
# =========================

ENABLE_RAG = os.getenv("ENABLE_RAG", "true").lower() == "true"
ENABLE_QUOTATION_PRELOAD = os.getenv("ENABLE_QUOTATION_PRELOAD", "true").lower() == "true"
