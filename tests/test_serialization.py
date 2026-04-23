from datetime import date, datetime

from api.serialization import planning_context_to_dict, to_jsonable
from models.schemas import (
    CostBreakdown,
    DayItinerary,
    FinalHandbook,
    Itinerary,
    OptimizationRecommendation,
    PlanningContext,
)


def test_to_jsonable_cost_breakdown_includes_total_and_dates_are_iso():
    cb = CostBreakdown(accommodation=100.0, dining=50.5)
    dt = datetime(2026, 4, 22, 12, 0, 1)
    d = date(2026, 4, 22)

    payload = {
        "cb": cb,
        "dt": dt,
        "d": d,
        "items": [cb, {"when": d}],
    }

    out = to_jsonable(payload)
    assert out["dt"] == dt.isoformat()
    assert out["d"] == d.isoformat()
    assert out["cb"]["accommodation"] == 100.0
    assert out["cb"]["dining"] == 50.5
    assert out["cb"]["total"] == cb.total
    assert out["items"][0]["total"] == cb.total
    assert out["items"][1]["when"] == d.isoformat()


def test_planning_context_to_dict_adds_handbook_summary_and_itinerary_narrative():
    itin = Itinerary(
        location="Seoul",
        start_date=date(2026, 8, 12),
        end_date=date(2026, 8, 16),
        days=[
            DayItinerary(
                day_number=1,
                date=date(2026, 8, 12),
                activities=[{"time": "09:00", "name": "Gyeongbokgung Palace", "location": "Jongno-gu"}],
                meals={"lunch": "Gwangjang Market"},
                accommodation={"name": "Hotel Test", "address": "Seoul"},
            )
        ],
        estimated_total_cost=123.0,
    )

    cb = CostBreakdown(accommodation=200.0, transportation=80.0, dining=60.0)
    fh = FinalHandbook(
        title="Seoul 5D",
        destination="Seoul",
        itinerary=itin,
        cost_breakdown=cb,
        budget=500.0,
        budget_remaining=160.0,
        optimization_recommendations=[
            OptimizationRecommendation(category="Transport", suggestion="Use T-money", potential_savings=10.0, confidence=0.8)
        ],
    )

    ctx = PlanningContext(itinerary=itin, final_handbook=fh)
    out = planning_context_to_dict(ctx)

    assert out["final_handbook_summary"]["title"] == "Seoul 5D"
    assert out["final_handbook_summary"]["destination"] == "Seoul"
    assert out["final_handbook_summary"]["budget"] == 500.0
    assert out["final_handbook_summary"]["total_cost"] == cb.total
    assert out["final_handbook_summary"]["budget_remaining"] == 160.0
    assert out["final_handbook_summary"]["is_within_budget"] is True

    assert "itinerary_narrative" in out
    narrative = out["itinerary_narrative"]
    assert isinstance(narrative, str)
    assert "Seoul" in narrative
    assert "Day 1" in narrative
    assert "Gyeongbokgung Palace" in narrative
