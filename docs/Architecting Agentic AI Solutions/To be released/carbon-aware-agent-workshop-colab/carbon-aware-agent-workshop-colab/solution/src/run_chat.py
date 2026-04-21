
from typing import List, Any, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from datetime import date

from config import OPENAI_MODEL, USE_LLM
from tools import (
    get_profile_tool,
    update_prefs_tool,
    recommend_best_from_text_tool,
)

SYSTEM = f"""
You are a single-agent carbon-aware scheduler.

Goal:
Recommend the best (region, start time) around the user's desired time within allowed shift and allowed regions.
"Best" means smallest carbon intensity g.

Rules:
- Always call get_profile first if you don't know regions/shift.
- If the user mentions any desired time in natural language (e.g. "tomorrow 11:00", "next Tue 3pm", "11 Mar 2026 10am"), ALWAYS call recommend_best_from_text using the user's time text (do not invent dates or ISO strings).
- Keep responses concise. Include: region, start_time (SG), g, shifted minutes.

"""

# Prepare LLM bound with tools
TOOLS = [
    get_profile_tool,
    update_prefs_tool,
    recommend_best_from_text_tool,
]

def build_app():
    if not USE_LLM:
        raise SystemExit("OPENAI_API_KEY missing. Add it to .env to run the chat agent.")
    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.4).bind_tools(TOOLS)

    graph = StateGraph(MessagesState)

    def assistant(state: MessagesState):
        # Ensure a single system message anchors behavior
        msgs = state["messages"]
        if not msgs or not isinstance(msgs[0], SystemMessage):
            msgs = [SystemMessage(content=SYSTEM)] + msgs
        resp = llm.invoke(msgs)
        return {"messages": [resp]}

    tool_node = ToolNode(TOOLS)

    graph.add_node("assistant", assistant)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("assistant")
    graph.add_conditional_edges("assistant", tools_condition)  # -> "tools" when tool_calls present, else END
    graph.add_edge("tools", "assistant")
    graph.add_edge("assistant", END)

    return graph.compile()

def chat():
    app = build_app()
    print("Agent ready. Try: 'I want to schedule a job', 'tomorrow 10am', 'I prefer regions SG, EU_WEST', 'remember allowed shift 90 minutes'.")
    state: Dict[str, Any] = {"messages": [SystemMessage(content=SYSTEM)]}
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye")
            break
        if not user:
            continue
        if user.lower() in {"exit", "quit"}:
            print("Bye")
            break
        state["messages"].append(HumanMessage(content=user))
        # Run graph until it reaches END (no more tool calls)
        result = app.invoke(state)
        print(result["messages"]);
        # Extract last AI message for display
        last_ai = None
        for m in result["messages"][::-1]:
            if isinstance(m, AIMessage) and m.content:
                last_ai = m
                break
        if last_ai:
            print(f"\nAgent: {last_ai.content}")
        state = result  # continue conversation with updated state

if __name__ == "__main__":
    chat()
