import time
import threading
import requests
import json
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI
import os

# =========================
# LLM for quotation summarization
# =========================

llm_quote_summary = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    max_tokens=400
)

# =========================
# Dummy quotation API
# =========================

def fetch_dummy_quotation():
    """
    Simulates an external quotation API.
    This replaces real insurer integrations.
    """
    time.sleep(1)  # simulate network delay

    return {
        "insurer": "InsurerA",
        "premium": 12456,
        "idv": "₹4.2L – ₹4.5L",
        "add_ons": ["Zero Dep", "Engine Protect"],
        "cashless_garages": 3200
    }


# =========================
# Quotation summarization
# =========================

def summarize_quotation(quotation_json: dict) -> str:
    """
    Converts raw quotation JSON into a compact,
    agent-consumable summary.
    """
    prompt = f"""
You are given raw insurance quotation data.
Summarize it into a short, factual, structured text.

IMPORTANT:
- Preserve exact numbers
- Do NOT infer or modify values
- Do NOT add recommendations

Quotation JSON:
{json.dumps(quotation_json, indent=2)}
"""

    response = llm_quote_summary.invoke(
        [HumanMessage(content=prompt)]
    )

    return response.content.strip()


# =========================
# Background quotation loader
# =========================

def start_quotation_loader(shared_state: dict):
    """
    Runs at app startup.
    Fetches quotation, summarizes it,
    and stores it in shared_state.
    """

    def _loader():
        try:
            raw_quote = fetch_dummy_quotation()
            summary = summarize_quotation(raw_quote)

            shared_state["quotation_summary"] = summary
            print("✅ Quotation summary loaded into system state")

        except Exception as e:
            print("❌ Quotation loader failed:", str(e))
            shared_state["quotation_summary"] = None

    thread = threading.Thread(target=_loader, daemon=True)
    thread.start()
