# VoyageAgent Quick Start

## 1. Setup

```bash
bash init.sh     # macOS/Linux
init.bat         # Windows
```

This creates a virtual environment and installs dependencies automatically.

## 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set your API key:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4
```

## 3. Run

```bash
python main.py
```

Enter your travel requirements in plain text, then type `END` on a new line to submit. The pipeline runs all 5 agents and prints a travel handbook summary.

## 4. Test

```bash
pytest tests/ -v                         # run all 21 tests
pytest tests/test_<agent_name>.py -v    # run one agent's tests
pytest tests/ -v -s                     # show print output
```

All tests should pass before and after your changes.

## 5. Project Map

```
agents/
  base_agent.py              shared abstract base — do not modify
  user_preference/
    agent.py                 implement _extract_preferences() here
    prompts.py               LLM prompt templates
  spot_recommendation/
    agent.py                 implement _recommend_spots() here
    prompts.py
  dining_recommendation/
    agent.py                 implement _recommend_restaurants() here
    prompts.py
  route_hotel_planning/
    agent.py                 implement _create_daily_itineraries() here
    prompts.py
  cost_optimization/
    agent.py                 implement _analyze_costs() here
    prompts.py
models/
  schemas.py                 all shared data models — do not modify
orchestrator/
  workflow.py                pipeline runner — do not modify
tests/
  test_<agent_name>.py       one test file per agent
docs/
  architecture.md            full architecture reference
  QUICK_START.md             this file
```

## 6. Implementing Your Agent

1. Open `agents/<your_agent>/agent.py`
2. Find the `# TODO:` block inside your stub method
3. Follow the steps listed in the comment
4. Delete the mock data block once your LLM call works
5. Run `pytest tests/test_<your_agent>.py -v` to verify nothing broke

The mock data in each stub is only a placeholder so the whole pipeline runs end-to-end before real logic exists. It has no effect on other agents' work.

## 7. Common Commands

```bash
# Activate virtual environment
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate.bat    # Windows

# Install / update dependencies
pip install -r requirements.txt

# Git workflow
git checkout -b feature/agent-<name>
git add .
git commit -m "feat: implement <agent name>"
git push origin feature/agent-<name>
```

## 8. Troubleshooting

- **Import errors**: make sure the virtual environment is activated and run `pip install -r requirements.txt`
- **API key errors**: check that `.env` exists and `OPENAI_API_KEY` is set correctly
- **Test failures**: run `pytest tests/ -v -s` for full output; read the assertion message carefully
- **Pipeline stops at step 1**: the User Preference Agent returned no `travel_profile` — check that `_extract_preferences()` returns all required fields (destination, start_date, end_date, budget, group_size, travel_style)

## 9. References

- Architecture details: `docs/architecture.md`
- Project proposal: `docs/PROPOSAL.md`
- Course requirements: `docs/AAS_Practice_Module_Requirements.md`
