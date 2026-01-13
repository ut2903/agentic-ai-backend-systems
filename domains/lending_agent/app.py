import os
import re
import json
import time
from datetime import datetime
from uuid import uuid4

from flask import Flask, request, jsonify
from flask_cors import CORS

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from .prompt import SYSTEM_PROMPT


# =========================
# LLM Configuration
# =========================
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    max_tokens=90
)


# =========================
# Flask App
# =========================
app = Flask(__name__)
CORS(app)


# =========================
# LangGraph State
# =========================
class State(TypedDict):
    conversation: list
    call_status: str
    language: str
    summary: str


# =========================
# Helpers
# =========================
def get_system_message(name: str):
    hour = datetime.now().hour
    return SystemMessage(
        content=(
            SYSTEM_PROMPT
            .replace("Name", name)
            .replace("{current_hour}", str(hour))
        )
    )


def llm_call(state: State):
    conversation = state["conversation"]

    start = time.time()
    response = llm.invoke(conversation)
    print(f"Lending LLM latency: {time.time() - start:.2f}s")

    conversation.append(AIMessage(content=response.content))

    match = re.search(r'\{.*"call_status".*\}', response.content)
    call_status = "ONGOING"
    language = None

    if match:
        try:
            payload = json.loads(match.group())
            call_status = payload.get("call_status", "ONGOING")
            language = payload.get("language")
        except Exception:
            pass

    return {
        "conversation": conversation,
        "call_status": call_status,
        "language": language,
        "summary": None
    }


def summarize_conversation(state: State):
    conversation = state["conversation"]

    summary_prompt = """
You are an assistant that summarizes call conversations for reporting.

Important Definitions:
1. Disposition: Contacted / Not Contacted

2. Sub Disposition (choose exactly one):
Wrong Number
Short Hang up
Call Disconnected
Language Barrier
Not Interested
Already Applied
Interested in Other Products
WIP Call Back
Not Eligible
WIP Follow up for Documents

Rules:
- Assign exactly one Sub Disposition.
- Short Hang Up: call ends immediately after agent greeting, no customer response.
- Default to "WIP Call Back" if outcome is unclear and none of the negative conditions apply.

Extract the following fields as top-level JSON keys:
{
'Disposition',
'SubDisposition',
'LoanType',
'LoanAmount',
'CurrentCity',
'CurrentCityPinCode',
'PropertyCity',
'PropertyPinCode',
'WithinMuncipalLimits',
'PropertyStage',
'PropetyType',
'OccupationStatus',
'MonthlySalary',
'MonthlyBonus',
'TotalMonthlyIncome',
'SalaryCreditMode',
'BusinessType',
'ProfessionalCertificateAvailable',
'BusinessRegistrationAvailable',
'ITR/CACertificate',
'Profit',
'CIBILScore',
'ExistingEMIs',
'EMIBounce',
'Co-Applicant',
'Co-ApplicantIncome',
'OutstandingLoanAmt',
'TopUpAmt',
'CurrentLender',
'CurrentInterestRate',
'CurrentTenure'
}

If a field is not present, set it to None.
Return ONLY valid JSON. No explanation. No markdown.
"""

    convo = "\n".join(
        f"{'Agent' if isinstance(m, AIMessage) else 'User'}: {m.content}"
        for m in conversation
        if not isinstance(m, SystemMessage)
    )

    response = llm.invoke([HumanMessage(content=summary_prompt + convo)])

    summary_text = response.content.strip()
    summary_text = re.sub(r"^```json\s*|\s*```$", "", summary_text)

    match = re.search(r"\{[\s\S]*\}", summary_text)
    summary_json = match.group() if match else "{}"

    return {
        "conversation": conversation,
        "call_status": "END",
        "language": state.get("language"),
        "summary": summary_json
    }


# =========================
# LangGraph Workflow
# =========================
workflow = StateGraph(State)

workflow.add_node("llm_call", llm_call)
workflow.add_node("summarize_conversation", summarize_conversation)

workflow.set_entry_point("llm_call")

workflow.add_conditional_edges(
    "llm_call",
    lambda s: s["call_status"],
    {
        "END": "summarize_conversation",
        "ONGOING": END
    }
)

workflow.add_edge("summarize_conversation", END)

graph_app = workflow.compile()


# =========================
# API Endpoint
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    user_id = data.get("user_id")
    user_name = data.get("name", "Customer")
    user_message = data.get("message")
    conversation = data.get("conversation", [])
    call_status = data.get("call_status", "ONGOING")

    if not user_id or not user_message:
        return jsonify({"error": "Missing user_id or message"}), 400

    if not conversation:
        conversation = [get_system_message(user_name)]

    conversation.append(HumanMessage(content=user_message))

    state = {
        "conversation": conversation,
        "call_status": call_status,
        "language": None,
        "summary": None
    }

    result = graph_app.invoke(state)

    last_agent_msg = next(
        (m for m in reversed(result["conversation"]) if isinstance(m, AIMessage)),
        None
    )

    agent_text = last_agent_msg.content if last_agent_msg else ""
    agent_text = re.sub(r'\{.*"call_status".*\}$', '', agent_text).strip()

    return jsonify({
        "agent": agent_text,
        "call_status": result.get("call_status"),
        "language": result.get("language"),
        "summary": result.get("summary"),
        "conversation": result.get("conversation")
    })
