# VoyageAgent

A multi-agent travel planning backend. Uses a pipeline of specialized LLM agents to generate a complete, personalized travel handbook from user input.

## Features

- Multi-agent architecture: 5 dedicated agents, each responsible for a distinct planning stage
- Data-driven: complete data models enabling seamless inter-agent collaboration
- Extensible design: easy to add new agents or extend existing ones
- End-to-end workflow: fully automated from user input to final handbook
- Test coverage: each agent has dedicated unit tests

## Architecture

```
User Input
   |
User Preference Agent      -> extracts user preferences
   |
Spot Recommendation Agent  -> recommends attractions
   |
Dining Recommendation Agent -> recommends restaurants
   |
Route & Hotel Planning Agent -> plans itinerary
   |
Cost Optimization Agent    -> optimizes costs
   |
Final Travel Handbook
```

## Directory Structure

```
voyagent-backend/
├── models/
│   └── schemas.py
├── agents/
│   ├── base_agent.py
│   ├── user_preference/
│   ├── spot_recommendation/
│   ├── dining_recommendation/
│   ├── route_hotel_planning/
│   └── cost_optimization/
├── orchestrator/
│   └── workflow.py
├── tests/
├── .github/workflows/
├── docs/
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

```bash
# Clone the repo
git clone <repo-url>
cd voyagent-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys
```

## Running

```python
from orchestrator.workflow import TravelPlanningWorkflow

workflow = TravelPlanningWorkflow()

user_input = """
I want to visit Paris, departing May 15 and returning May 22.
Budget $5000 for 4 people.
We enjoy culture and food.
"""

context = workflow.run(user_input)
final_handbook = context.final_handbook
print(f"Handbook: {final_handbook.title}")
print(f"Total cost: ${final_handbook.cost_breakdown.total}")
```

## Team

| Member | Module | Branch |
|--------|--------|--------|
| Member 1 | User Preference Agent | feature/agent-user-preference |
| Member 2 | Spot Recommendation Agent | feature/agent-spot |
| Member 3 | Dining Recommendation Agent | feature/agent-dining |
| Member 4 | Route & Hotel Planning Agent | feature/agent-route-hotel |
| Member 5 | Cost Optimization Agent | feature/agent-cost |
| Team Lead | Orchestrator + Schemas | - |

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_user_preference.py -v

# Generate coverage report
pytest tests/ --cov=. --cov-report=html
```

## Agents

### User Preference Agent
Extracts travel preference information (destination, budget, dates, group size, etc.)

### Spot Recommendation Agent
Recommends attractions matching user preferences, including ratings and entrance fees.

### Dining Recommendation Agent
Recommends restaurants matching dietary preferences and budget.

### Route & Hotel Planning Agent
Plans a detailed day-by-day itinerary and hotel arrangement.

### Cost Optimization Agent
Analyzes costs, provides optimization suggestions, and generates the final travel handbook.

## Git Workflow

```bash
# Create a feature branch
git checkout -b feature/agent-xxx

# Develop and commit
git add .
git commit -m "feat: implement xxx"

# Push to remote
git push origin feature/agent-xxx

# Open a PR to dev branch
# Merge to main after review
```

## Configuration

See `.env.example` for required environment variables:

```env
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./data/voyagent.db
```

## Documentation

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Development Notes

- Each agent lives under `agents/<agent_name>/`
- Each agent contains `agent.py` (implementation) and `prompts.py` (LLM prompts)
- All schemas are defined in `models/schemas.py`
- Workflow logic is in `orchestrator/workflow.py`

## CI/CD

GitHub Actions runs tests automatically on push. Config: `.github/workflows/ci.yml`

## License

MIT License

## Contributing

1. Fork this repo
2. Create a feature branch (`git checkout -b feature/xxx`)
3. Commit your changes (`git commit -m 'Add xxx'`)
4. Push to the branch (`git push origin feature/xxx`)
5. Open a Pull Request

## Contact

- Issue reports: GitHub Issues
- Discussion: GitHub Discussions
- Email: team@voyagent.com
