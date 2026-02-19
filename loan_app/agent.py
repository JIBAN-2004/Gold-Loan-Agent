import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from loan_app.state import State

from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# PROMPT
from loan_app.prompts import SYSTEM_PROMPT

# STATE
class LoanState(dict):
    """
    State container for the loan ReAct agent
    """
    messages: list
    loan_data: dict


# TOOLS
from tools.full_name import full_name_tool
from tools.Phone_number import phone_number_tool
from tools.Phone_otp import send_otp_tool, verify_otp_tool
from tools.Father_name import father_name_tool
from tools.Loan_amount import loan_amount_tool
from tools.Loan_type import loan_type_tool
from tools.metals_price import metals_price_tool

AGENT_TOOLS = [
    full_name_tool,
    phone_number_tool,
    send_otp_tool,
    verify_otp_tool,
    father_name_tool,
    loan_amount_tool,
    loan_type_tool,
    metals_price_tool,
]

# LLM
#llm = ChatGroq(
#    model="llama-3.1-8b-instant", #model="groq/compound", model="groq/compound-mini"
#    temperature=0
#)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",   # Gemini 3.0+ defaults to 1.0
    temperature=1.0,   
).bind_tools(AGENT_TOOLS)


# GREETING NODE
def greeting_node(state: LoanState) -> LoanState:
    if state.get("messages"):
        return state

    # Instead of an AIMessage, we inject a "dummy" HumanMessage 
    # that triggers the agent to respond with a greeting.
    state["messages"] = [
        # This tells the LLM: "The user just joined, greet them and ask for their name"
        HumanMessage(content="[User joined the chat. Greet them and ask for their full name.]")
    ]
    return state


# REACT AGENT NODE
react_agent = create_react_agent(
    model=llm,
    tools=AGENT_TOOLS,
    prompt=SYSTEM_PROMPT,
)

agent_node = react_agent
