# VoyageAgent Architecture

## Overview

VoyageAgent is a multi-agent travel planning backend. The system processes user travel input through a fixed pipeline of specialized agents and returns a structured travel handbook.

## Agent Pipeline

```
User Input (free-form text)
        |
[1] User Preference Agent       -> TravelProfile
        |
[2] Spot Recommendation Agent   -> SpotList
        |
[3] Dining Recommendation Agent -> DiningList
        |
[4] Route & Hotel Planning Agent -> Itinerary
        |
[5] Cost Optimization Agent     -> FinalHandbook
```

Each step reads from and writes to a shared `PlanningContext` object. If a step produces an error, the workflow stops by default (`fail_fast=True`).

## Core Components

| File | Role |
|------|------|
| `agents/base_agent.py` | Abstract base class — handles timing, logging, error capture, and metadata recording. Do not modify. |
| `agents/*/agent.py` | Agent business logic — implement your LLM call inside the stub method marked `# TODO`. |
| `agents/*/prompts.py` | LLM prompt templates — format these and pass them to your LLM client inside `agent.py`. |
| `models/schemas.py` | All shared data models — do not change without team agreement. |
| `orchestrator/workflow.py` | Pipeline runner — no changes needed when implementing agent logic. |

## Shared State: PlanningContext

All agents communicate exclusively through `PlanningContext`. No agent calls another agent directly.

```
PlanningContext
├── travel_profile     set by User Preference Agent
├── spot_list          set by Spot Recommendation Agent
├── dining_list        set by Dining Recommendation Agent
├── itinerary          set by Route & Hotel Planning Agent
├── final_handbook     set by Cost Optimization Agent
├── errors             list of error strings — non-empty stops the pipeline
├── warnings           list of warning strings — pipeline continues
└── metadata           dict — stores user_input, agent_runs, workflow timing
```

## Data Models (models/schemas.py)

| Model | Key Fields |
|-------|------------|
| `TravelProfile` | destination, start_date, end_date, budget, group_size, travel_style, interests |
| `SpotList` | spots: List[Spot], filter_criteria, total_count |
| `DiningList` | restaurants: List[Restaurant], meal_type, filter_criteria, total_count |
| `Itinerary` | location, days: List[DayItinerary], estimated_total_cost |
| `FinalHandbook` | title, itinerary, cost_breakdown, optimization_recommendations |
| `CostBreakdown` | accommodation, transportation, dining, attractions, … (`.total` is computed) |

## How to Implement Your Agent

Each agent has exactly one stub method to fill in. Find the `# TODO:` block in your `agent.py` — it lists the exact steps.

```python
# agents/<your_agent>/agent.py

def _your_stub_method(self, ...) -> ...:
    # 1. Format the prompt from prompts.py using fields from travel_profile / context
    # 2. Call your LLM client (SYSTEM_PROMPT + formatted user prompt)
    # 3. Parse the JSON the LLM returns
    # 4. Construct and return the appropriate schema object(s)
    #
    # Do NOT touch process(), validate_input(), workflow.py, base_agent.py,
    # or models/schemas.py.
    ...
```

The mock data block currently in each stub is only there so the full pipeline can run end-to-end before real LLM logic exists. Delete it once your LLM call is working.

## Workflow Execution Details

`TravelPlanningWorkflow.run(user_input)` in `orchestrator/workflow.py`:

1. Creates a fresh `PlanningContext`; stores `user_input` in `metadata`
2. Calls each agent's `execute()` — which wraps `process()` with error handling and timing
3. After each step, verifies the expected output field is non-None; adds an error if missing
4. Stops early when `context.errors` is non-empty (fail_fast mode)
5. Prints a summary and returns the context

## Quality and Operations

- Unit tests: `tests/test_<agent_name>.py` — run with `pytest tests/ -v`
- CI: `.github/workflows/ci.yml` — runs automatically on push
- Environment: copy `.env.example` → `.env` and fill in API keys
- Dependencies: `requirements.txt`

## Development Rules

- `PlanningContext` is the only cross-agent contract — never pass objects between agents directly
- Keep `models/schemas.py` stable — discuss with the team before changing any field
- Do not modify `orchestrator/workflow.py` or `base_agent.py` to implement agent logic
- Add or update tests in `tests/` when you change agent behavior
