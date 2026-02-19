from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, ToolMessage

from loan_app.state import State
from loan_app.agent import greeting_node, agent_node


# GRAPH
graph = StateGraph(State)

# NODES
graph.add_node("greeting", greeting_node)
graph.add_node("agent", agent_node)

# 1. CONDITIONAL START 
# This handles the entry point logic correctly
def show_greeting(state: State) -> str:
    if not state.get("messages"):
        return "greeting"
    return "agent"

graph.add_conditional_edges(
    START,
    show_greeting,
    {
        "greeting": "greeting",
        "agent": "agent",
    },
)

# 2. FIX THE GREETING EXIT
# Instead of going to 'agent', we go to END. 
# This stops the execution and waits for the user's name.
graph.add_edge("greeting", END) 

# 3. TOOL APPLICATION LOGIC (Internal to the agent loop)
def apply_tool_result(state: State) -> State:
    messages = state.get("messages", [])
    if not messages:
        return state

    last = messages[-1]
    if isinstance(last, ToolMessage):
        # Ensure we don't crash if content isn't a dict
        if isinstance(last.content, dict):
            state.setdefault("loan_data", {}).update(last.content)
    return state

# 4. RE-ACT LOOP LOGIC
def should_continue(state: State) -> str:
    # Update data state before deciding next move
    state = apply_tool_result(state)
    
    messages = state.get("messages", [])
    if not messages:
        return END

    last = messages[-1]

    # If the last message is a ToolMessage, the Agent MUST 
    # run again to interpret that tool result for the user.
    if isinstance(last, ToolMessage):
        return "agent"

    # If it's an AIMessage, the AI has finished its turn.
    if isinstance(last, AIMessage):
        return END

    return "agent"

# 5. AGENT EDGES
graph.add_conditional_edges("agent",
    should_continue,
    {
        "agent": "agent",
        END: END,
    },
)

# COMPILE
app = graph.compile()