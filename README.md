# VoyageAgent

A multi-agent travel planning backend. Processes free-form user input through a pipeline of 5 specialized LLM agents and produces a complete, personalized travel handbook.

## Architecture

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

All agents share a single `PlanningContext` object. Each agent reads its inputs from the context and writes its output back. See [docs/architecture.md](docs/architecture.md) for full details.

## Quick Start

```bash
# 1. Setup
bash init.sh          # macOS/Linux
init.bat              # Windows

# 2. Configure
cp .env.example .env
# Edit .env and set OPENAI_API_KEY

# 3. Run
python main.py

# 4. Test
pytest tests/ -v
```

See [docs/QUICK_START.md](docs/QUICK_START.md) for step-by-step instructions and troubleshooting.

## Directory Structure

```
voyagent-backend/
├── agents/
│   ├── base_agent.py           shared base class (do not modify)
│   ├── user_preference/        agent.py + prompts.py
│   ├── spot_recommendation/
│   ├── dining_recommendation/
│   ├── route_hotel_planning/
│   └── cost_optimization/
├── models/
│   └── schemas.py              shared data models (do not modify)
├── orchestrator/
│   └── workflow.py             pipeline runner (do not modify)
├── tests/
├── docs/
│   ├── architecture.md
│   └── QUICK_START.md
├── .env.example
└── requirements.txt
```

## Implementing an Agent

Each agent has one stub method with a `# TODO:` block. Fill in that method:

1. Format the prompt from `prompts.py` using fields from `context.travel_profile` (or other context fields)
2. Call your LLM client
3. Parse the response and return the appropriate schema object

The mock data already in each stub keeps the full pipeline runnable until real logic is added. Delete it once your LLM call works.

Do not modify `base_agent.py`, `orchestrator/workflow.py`, or `models/schemas.py`.

## Testing

```bash
pytest tests/ -v                        # all 21 tests
pytest tests/test_<agent_name>.py -v   # one agent
pytest tests/ --cov=. --cov-report=html
```

## Team

| Member | Agent | Branch |
|--------|-------|--------|
| Member 1 | User Preference | `feature/agent-user-preference` |
| Member 2 | Spot Recommendation | `feature/agent-spot` |
| Member 3 | Dining Recommendation | `feature/agent-dining` |
| Member 4 | Route & Hotel Planning | `feature/agent-route-hotel` |
| Member 5 | Cost Optimization | `feature/agent-cost` |

## CI/CD

GitHub Actions runs `pytest tests/ -v` on every push. Config: `.github/workflows/ci.yml`

## License

MIT License
