"""
FastAPI application: full HTTP surface for the VoyageAgent travel planning backend.
"""

import os
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.schemas_http import (
    AgentsResponse,
    AgentInfoItem,
    HealthResponse,
    PlanRequest,
    PlanResponse,
    VersionResponse,
    WorkflowStepsResponse,
    WorkflowStepItem,
)
from api.serialization import planning_context_to_dict
from orchestrator.workflow import TravelPlanningWorkflow

API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_dotenv()
    yield


app = FastAPI(
    title="VoyageAgent API",
    description="HTTP API for the multi-agent travel planning pipeline (all five agents + orchestrator).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

_cors_origins = os.getenv("CORS_ORIGINS", "").strip()
if _cors_origins:
    origins = [o.strip() for o in _cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _workflow_for_request(fail_fast: bool, print_summary: bool) -> TravelPlanningWorkflow:
    """Build a workflow with per-request orchestration flags."""
    return TravelPlanningWorkflow(fail_fast=fail_fast, print_summary=print_summary)


@lru_cache(maxsize=1)
def _metadata_workflow() -> TravelPlanningWorkflow:
    """Single cached workflow for step/agent metadata endpoints (no run)."""
    return TravelPlanningWorkflow(fail_fast=True, print_summary=False)


@app.get("/", tags=["meta"])
def root() -> dict[str, Any]:
    return {
        "service": "VoyageAgent",
        "docs": "/docs",
        "api": API_PREFIX,
    }


@app.get(f"{API_PREFIX}/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get(f"{API_PREFIX}/version", response_model=VersionResponse, tags=["meta"])
def version() -> VersionResponse:
    return VersionResponse(
        app_name=os.getenv("APP_NAME", "VoyageAgent"),
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        api_version="1.0.0",
    )


@app.get(f"{API_PREFIX}/agents", response_model=AgentsResponse, tags=["agents"])
def list_agents() -> AgentsResponse:
    wf = _metadata_workflow()
    info = wf.get_agent_info()
    items: list[AgentInfoItem] = []
    for idx, (label, _agent, output_field, _required) in enumerate(wf.steps, start=1):
        agent_obj = wf.agents[idx - 1]
        items.append(
            AgentInfoItem(
                name=agent_obj.name,
                description=info.get(agent_obj.name, ""),
                step_index=idx,
                output_field=output_field,
            )
        )
    return AgentsResponse(agents=items)


@app.get(f"{API_PREFIX}/workflow/steps", response_model=WorkflowStepsResponse, tags=["workflow"])
def workflow_steps() -> WorkflowStepsResponse:
    wf = _metadata_workflow()
    steps = [
        WorkflowStepItem(
            step_index=i,
            label=label,
            output_field=output_field,
            required=required,
        )
        for i, (label, _a, output_field, required) in enumerate(wf.steps, start=1)
    ]
    return WorkflowStepsResponse(steps=steps)


@app.post(f"{API_PREFIX}/plan", response_model=PlanResponse, tags=["planning"])
def run_plan(body: PlanRequest) -> PlanResponse:
    """
    Run the full pipeline: User Preference → Spots → Dining → Route/Hotel → Cost → Handbook.
    """
    wf = _workflow_for_request(fail_fast=body.fail_fast, print_summary=body.print_summary)
    context = wf.run(body.user_input.strip())
    payload = planning_context_to_dict(context)
    ok = len(context.errors) == 0
    return PlanResponse(
        ok=ok,
        travel_profile=payload.get("travel_profile"),
        spot_list=payload.get("spot_list"),
        dining_list=payload.get("dining_list"),
        itinerary=payload.get("itinerary"),
        final_handbook=payload.get("final_handbook"),
        final_handbook_summary=payload.get("final_handbook_summary"),
        errors=payload.get("errors") or [],
        warnings=payload.get("warnings") or [],
        metadata=payload.get("metadata") or {},
    )
