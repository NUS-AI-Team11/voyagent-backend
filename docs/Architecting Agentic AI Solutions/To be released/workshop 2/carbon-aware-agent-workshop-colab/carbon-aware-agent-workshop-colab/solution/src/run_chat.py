
from typing import List, Any, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from datetime import date
import json

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
- For the final answer:
  - If a recommendation is available: respond with a single short paragraph recommending the best region and start time in SG, and include g and shifted minutes.
  - If no recommendation is available: say there are no available options under current preferences and ask whether to expand allowed regions or shift window.

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
        # If a recommendation tool just returned, produce a deterministic final response.
        msgs = state["messages"]
        if msgs and isinstance(msgs[-1], ToolMessage) and msgs[-1].name in {
            "recommend_best_from_text",
            "recommend_best",
        }:
            try:
                payload = json.loads(msgs[-1].content or "{}")
            except Exception:
                payload = {}

            if payload.get("ok") is True:
                region = payload.get("region", "")
                start_time_sg_full = (payload.get("start_time_sg", "") or "").replace("T", " ")
                date_part = start_time_sg_full[:10] if len(start_time_sg_full) >= 10 else ""
                time_part = start_time_sg_full[11:16] if len(start_time_sg_full) >= 16 else start_time_sg_full[:5]
                g = payload.get("g", "")
                shifted = payload.get("shifted_minutes", "")
                text = (
                    f"I recommend scheduling your job in the {region} region at {time_part} SG"
                    + (f" on {date_part}" if date_part else "")
                    + f". The carbon intensity is {g}g, shifted by {shifted} minutes."
                )
                return {"messages": [AIMessage(content=text)]}

            # Tool returned no available points (or unknown structure)
            desired = (payload.get("desired_time_sg", "") or "").replace("T", " ")[:16]
            regions = payload.get("regions_allowed", None)
            # Prefer the workshop-style message.
            text = (
                f"There are no available options under your current preferences"
                + (f" around {desired} SG" if desired else "")
                + (f" in the {', '.join(regions)} region(s)" if isinstance(regions, list) and regions else "")
                + ". Would you like to expand your preferences to include other regions or allow a larger time shift?"
            )
            return {"messages": [AIMessage(content=text)]}

        # Ensure a single system message anchors behavior
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
