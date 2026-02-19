from typing import TypedDict, Annotated, Optional, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class State(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    remaining_steps: int

    current_step: str
    loan_data: dict
    retries: dict
    greeted: bool
    otp_sent: bool
    otp_verified: bool
    otp_attempts: int
