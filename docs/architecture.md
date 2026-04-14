# VoyageAgent Architecture

## Overview

VoyageAgent is a multi-agent travel planning backend. The system processes user travel input through a fixed pipeline of specialized agents and returns a structured travel handbook.

## Agent Pipeline

1. User Preference Agent
2. Spot Recommendation Agent
3. Dining Recommendation Agent
4. Route and Hotel Planning Agent
5. Cost Optimization Agent

Each step reads and updates a shared `PlanningContext` object.

## Core Components

- `agents/base_agent.py`: shared abstract interface and validation hooks.
- `agents/*/agent.py`: agent-specific processing logic.
- `agents/*/prompts.py`: prompt templates for LLM integration.
- `models/schemas.py`: shared data models.
- `orchestrator/workflow.py`: end-to-end pipeline orchestration.

## Data Flow

Input text -> `TravelProfile` -> `SpotList` + `DiningList` -> `Itinerary` -> `FinalHandbook`

All intermediate state is stored in `PlanningContext`, including:

- `travel_profile`
- `spot_list`
- `dining_list`
- `itinerary`
- `final_handbook`
- `errors`
- `warnings`
- `metadata`

## Responsibilities by Agent

- User Preference: parse constraints and preferences.
- Spot Recommendation: suggest points of interest.
- Dining Recommendation: suggest meal options under constraints.
- Route and Hotel Planning: create day plans and stay strategy.
- Cost Optimization: estimate costs and provide optimization actions.

## Quality and Operations

- Unit tests under `tests/`.
- CI workflow under `.github/workflows/ci.yml`.
- Environment template in `.env.example`.
- Dependency management in `requirements.txt`.

## Development Notes

- Keep models stable and explicit.
- Keep agent boundaries strict.
- Use `PlanningContext` as the only cross-agent contract.
- Add tests when extending schemas or workflow behavior.
