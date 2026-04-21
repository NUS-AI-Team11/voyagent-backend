# Single-Agent Carbon-Aware Scheduler — **Autonomous Chat (ToolNode)**

Build a *single agent* that recommends the **best region + start time** for a batch job around a desired time, within an **allowed shift** window. The agent is fully **autonomous**:
- Asks for the start time if you didn’t provide one (natural language accepted: “tomorrow 10am”).
- **Decides which tools to call** via LLM tool-calling.
- **Updates memory** (preferences) when you say things like “I prefer regions SG, EU_WEST” or “remember allowed shift 90 minutes”.

## Preferences (persisted in `memory/profile.json`)
- `regions_allowed`: e.g., `["SG","EU_WEST","US_WEST"]`
- `allowed_shift_minutes`: e.g., `60`

## Project layout (streamlined)
```
solution/
  src/
    config.py
    memory.py
    tools_agent.py
    run_chat.py        # <- Autonomous chat using LangGraph ToolNode
data/
  mock_forecast.json   # Deterministic 15-min forecasts for SG/EU_WEST/US_WEST
memory/
  profile.json         # Preferences (persisted)
```
---

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env   # add OPENAI_API_KEY
```

## Run the autonomous chat
```bash
python solution/src/run_chat.py
```
Sample interaction:
```
You: I want to schedule a job
Agent: Sure — what time would you like to start? You can say things like “tomorrow 10am”.
You: tomorrow 10am
Agent: Recommended: EU_WEST at 2025-09-13T10:45 (gCO2e/kWh 210). Shift: +45 min within allowed 60.
```

Preference updates (no regex, LLM decides to call the tool):
```
You: I prefer regions SG, EU_WEST
You: remember allowed shift 90 minutes
```

## Under the hood
- `run_chat.py` builds a LangGraph with two nodes:
  - **assistant** (LLM bound to tools)
  - **tools** (`ToolNode`) — executes tool calls automatically
- Loop continues until the model stops requesting tools.

## Notes
- Times are snapped to 15-minute slots.
