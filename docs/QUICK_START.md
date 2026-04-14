# VoyageAgent Quick Start

## 1. Setup

```bash
bash init.sh          # macOS/Linux
init.bat              # Windows
```

## 2. Configure Environment

Edit `.env` and set:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4
```

## 3. Run and Test

```bash
python main.py
pytest tests/ -v
pytest tests/test_<agent_name>.py -v
```

## 4. Project Map

```text
agents/
  user_preference/
  spot_recommendation/
  dining_recommendation/
  route_hotel_planning/
  cost_optimization/
models/schemas.py
orchestrator/workflow.py
tests/
```

## 5. Common Commands

```bash
source venv/bin/activate          # macOS/Linux
venv\\Scripts\\activate.bat         # Windows
pip install -r requirements.txt

# Git flow
git checkout -b feature/agent-<name>
git add .
git commit -m "feat: describe your change"
git push origin feature/agent-<name>
```

## 6. Troubleshooting

- Module import errors: reinstall dependencies with `pip install -r requirements.txt`.
- API key errors: check `.env` and `OPENAI_API_KEY`.
- Test failures: run `pytest tests/ -v -s` for full output.
- Environment issues: ensure the virtual environment is activated.

## 7. References

- Architecture: `docs/architecture.md`
- Project proposal: `docs/PROPOSAL.md`
- Course requirements: `docs/AAS_Practice_Module_Requirements.md`
