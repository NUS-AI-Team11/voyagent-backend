"""
Pydantic request/response models for the HTTP API layer.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    """Body for POST /api/v1/plan."""

    user_input: str = Field(..., min_length=1, description="Free-form travel requirements (same as CLI input).")
    fail_fast: bool = Field(True, description="Stop the pipeline when the first error is recorded.")
    print_summary: bool = Field(
        False,
        description="If true, also print the CLI-style summary to server stdout (usually false for API).",
    )


class PlanResponse(BaseModel):
    """Full planning result."""

    ok: bool = Field(..., description="True when there are no blocking errors in context.errors.")
    travel_profile: Optional[Dict[str, Any]] = None
    spot_list: Optional[Dict[str, Any]] = None
    dining_list: Optional[Dict[str, Any]] = None
    itinerary: Optional[Dict[str, Any]] = None
    final_handbook: Optional[Dict[str, Any]] = None
    final_handbook_summary: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str = "ok"


class VersionResponse(BaseModel):
    app_name: str
    app_version: str
    api_version: str


class AgentInfoItem(BaseModel):
    name: str
    description: str
    step_index: int
    output_field: str


class AgentsResponse(BaseModel):
    agents: List[AgentInfoItem]


class WorkflowStepItem(BaseModel):
    step_index: int
    label: str
    output_field: str
    required: bool


class WorkflowStepsResponse(BaseModel):
    steps: List[WorkflowStepItem]
    pipeline: List[str] = Field(
        default_factory=lambda: [
            "user_preference",
            "spot_recommendation",
            "dining_recommendation",
            "route_hotel_planning",
            "cost_optimization",
        ],
        description="Logical agent keys in execution order.",
    )
