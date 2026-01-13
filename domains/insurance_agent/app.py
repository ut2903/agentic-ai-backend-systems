from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .rag import rag_node


from datetime import datetime
from uuid import uuid4
import re, json, time, os

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from .prompt import SYSTEM_PROMPT

# =========================
# Azure OpenAI Configuration 
# =========================
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    max_tokens=90
)

llm_summary = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    max_tokens=512
)

# =========================
# FastAPI App
# =========================
app = FastAPI(title="Insurance Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        content=SYSTEM_PROMPT.replace("Name", name).replace("{current_hour}", str(hour))
    )


def llm_call(state: State):
    conversation = state["conversation"]

    start_time = time.time()
    response = llm.invoke(conversation)
    print(f"LLM latency: {time.time() - start_time:.2f}s")

    conversation.append(AIMessage(content=response.content))

    match = re.search(
        r'\{.*"call_status"\s*:\s*"(END|ONGOING)".*("language"\s*:\s*"[^"]+")?.*\}',
        response.content
    )

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
        "language": language
    }


def summarize_conversation(state: State):
    conversation = state["conversation"]

    summary_prompt = ("""
You are an assistant that summarizes insurance call conversations for reporting.
Summarize the call by extracting these fields as top-level JSON keys (set to null if not found):

{
  "Disposition": "Contacted / Not Contacted",
  "SubDisposition": "Interested / Not Interested / Call Disconnected / Wrong Number / Short Hang up / Language Barrier / Callback Requested / Already Insured / Just Exploring / Technical Issue / Other",
  "UserName": "",
  "BikeRegistrationNumber": "",
  "BikeMakeModel": "",
  "PolicyExpiryDate": "",
  "CoverType": "Comprehensive / Third-Party / Not Decided",
  "AddOnsDiscussed": "",
  "NomineeDetailsProvided": true/false/null,
  "KYCDetailsProvided": true/false/null,
  "WantsExpertConnection": true/false/null,
  "ObjectionsOrSpecialScenarios": "",
  "TechnicalIssues": "",
  "Language": "",
  "Summary": "Short summary of the call"
}
If a field is not present, set it to None.
Return ONLY a valid JSON object with these fields as top-level keys, no explanation, no markdown, and no extra text.
"""
    )

    convo = "\n".join(
        f"{'Agent' if isinstance(m, AIMessage) else 'User'}: {m.content}"
        for m in conversation
        if not isinstance(m, SystemMessage)
    )

    response = llm_summary.invoke(
        [HumanMessage(content=summary_prompt + convo)]
    )

    summary_text = response.content.strip()
    summary_text = re.sub(r"^```json\s*|\s*```$", "", summary_text)

    match = re.search(r"\{[\s\S]*\}", summary_text)
    summary_out = match.group() if match else "{}"

    return {
        "conversation": conversation,
        "call_status": "END",
        "summary": summary_out
    }


# =========================
# LangGraph Workflow
# =========================
workflow = StateGraph(State)

workflow.add_node("llm_call", llm_call)
workflow.add_node("summarize_conversation", summarize_conversation)

workflow.add_node("rag_node", rag_node)
workflow.add_edge("rag_node", "llm_call_postrag")


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
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    user_id = data.get("user_id")
    user_name = data.get("name", "Customer")
    user_message = data.get("message")
    client_call_status = data.get("call_status", "ONGOING")

    if not user_id or not user_message:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing user_id or message"}
        )

    session_id = data.get("session_id") or str(uuid4())
    conversation = data.get("conversation")

    if not conversation:
        conversation = [get_system_message(user_name)]

    conversation.append(HumanMessage(content=user_message))

    state = {
        "conversation": conversation,
        "call_status": client_call_status,
        "language": None,
        "summary": ""
    }

    if client_call_status == "END":
        result = summarize_conversation(state)
    else:
        result = graph_app.invoke(state)

    last_agent_msg = next(
        (m for m in reversed(result["conversation"]) if isinstance(m, AIMessage)),
        None
    )

    agent_text = last_agent_msg.content if last_agent_msg else ""
    agent_text = re.sub(
        r'\{.*"call_status".*\}$',
        '',
        agent_text
    ).strip()

    return {
        "session_id": session_id,
        "agent": agent_text,
        "call_status": result.get("call_status"),
        "language": result.get("language"),
        "summary": result.get("summary")
    }
