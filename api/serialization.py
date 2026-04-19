"""
JSON-safe serialization for PlanningContext and nested dataclass models.
"""

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from typing import Any

from api.narrative import itinerary_dict_to_narrative
from models.schemas import CostBreakdown, PlanningContext


def to_jsonable(obj: Any) -> Any:
    """Recursively convert dataclasses and dates to JSON-serializable structures."""
    if obj is None:
        return None
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if is_dataclass(obj) and not isinstance(obj, type):
        data = asdict(obj)
        if isinstance(obj, CostBreakdown):
            data["total"] = obj.total
        return {k: to_jsonable(v) for k, v in data.items()}
    return obj


def planning_context_to_dict(context: PlanningContext) -> dict[str, Any]:
    """Serialize a full PlanningContext for API responses."""
    result: dict[str, Any] = {
        "travel_profile": to_jsonable(context.travel_profile),
        "spot_list": to_jsonable(context.spot_list),
        "dining_list": to_jsonable(context.dining_list),
        "itinerary": to_jsonable(context.itinerary),
        "final_handbook": to_jsonable(context.final_handbook),
        "errors": list(context.errors),
        "warnings": list(context.warnings),
        "metadata": to_jsonable(context.metadata),
    }
    if context.final_handbook is not None:
        fh = context.final_handbook
        result["final_handbook_summary"] = {
            "title": fh.title,
            "destination": fh.destination,
            "budget": fh.budget,
            "total_cost": fh.cost_breakdown.total,
            "budget_remaining": fh.budget_remaining,
            "is_within_budget": fh.is_within_budget,
        }
    itin = result.get("itinerary")
    if itin:
        narrative = itinerary_dict_to_narrative(itin)
        if narrative:
            result["itinerary_narrative"] = narrative
    return result
