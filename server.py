from fastapi import FastAPI
from pydantic import BaseModel

from loan_app.graph import app as graph_app
from DB.db import save_message, get_session, upsert_session

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
)

app = FastAPI()
SESSIONS = {}

# Helpers: Message Normalization (DB → App)
def normalize_messages(messages):
    """
    Convert DB-stored dict messages into LangChain message objects
    """
    normalized = []

    for m in messages:
        # Already a LangChain message → keep it
        if isinstance(m, (HumanMessage, AIMessage, ToolMessage)):
            normalized.append(m)
            continue

        # DB-stored dict → convert
        if isinstance(m, dict):
            role = m.get("role")
            content = m.get("content")

            if role == "user":
                normalized.append(HumanMessage(content=content))

            elif role == "assistant":
                normalized.append(AIMessage(content=content))

            elif role == "tool":
                normalized.append(
                    ToolMessage(
                        content=content,
                        tool_call_id=m.get("tool_call_id", "legacy"),
                    )
                )

    return normalized


# Helpers: Message Serialization (App → DB)
def serialize_messages(messages):
    """
    Convert LangChain message objects into plain dicts for MongoDB
    """
    serialized = []

    for m in messages:
        if isinstance(m, HumanMessage):
            serialized.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage):
            serialized.append({"role": "assistant", "content": m.content})
        elif isinstance(m, ToolMessage):
            serialized.append({
                "role": "tool",
                "content": m.content,
                "tool_name": m.name,
                "tool_call_id": m.tool_call_id,
            })
        elif isinstance(m, dict):
            serialized.append(m)

    return serialized

# Normalize assistant content for DB
def normalize_content(content):
    if isinstance(content, list):
        return " ".join(
            item.get("text", "") for item in content if isinstance(item, dict)
        )
    return str(content) if content is not None else None

# Request Model
class ChatRequest(BaseModel):
    thread_id: str
    message: str | None = None


# Chat Endpoint
@app.post("/chat")
def chat(req: ChatRequest):

    # LOAD SESSION FROM DB
    db_state = get_session(req.thread_id)

    state = {
        "thread_id": req.thread_id,
        "messages": [],
        "loan_data": {},
        "otp_attempts": 0,
    }

    if db_state:
        state.update(db_state)
        state["messages"] = normalize_messages(db_state.get("messages", []))

    # USER MESSAGE
    if req.message:
        state["messages"].append(HumanMessage(content=req.message))

        # ✅ SAVE USER MESSAGE
        save_message(
            thread_id=req.thread_id,
            role="user",
            content=req.message
        )

    # RUN AGENT
    result = graph_app.invoke(
        state,
        config={
            "configurable": {
                "thread_id": req.thread_id
            }
        }
    )

    for key, value in result.items():
        if value is not None:
            state[key] = value

    # EXTRACT LAST ASSISTANT MESSAGE
    reply = next(
        (m.content for m in reversed(state["messages"]) if isinstance(m, AIMessage)),
        None
    )

    # SAVE ASSISTANT MESSAGE
    if reply:
        save_message(
            thread_id=req.thread_id,
            role="assistant",
            content=normalize_content(reply)
        )

    # SAVE SESSION (SINGLE SOURCE OF TRUTH)
    upsert_session({
        **state,
        "messages": serialize_messages(state["messages"])
    })

    return {"response": reply}