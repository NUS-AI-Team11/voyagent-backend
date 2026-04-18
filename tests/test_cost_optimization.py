"""
Tests for Cost Optimization Agent.
"""

import pytest
from unittest.mock import patch, MagicMock
from models.schemas import (
    TravelProfile, Itinerary, DayItinerary, PlanningContext, CostBreakdown
)
from agents.cost_optimization.agent import CostOptimizationAgent
from datetime import date


# ── fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def agent():
    """Create agent with mocked OpenAI client for testing."""
    instance = CostOptimizationAgent()
    instance._client = MagicMock()
    return instance


@pytest.fixture
def five_day_context():
    """Realistic 5-day Rome itinerary mimicking Route & Hotel Planning Agent output."""
    days = [
        DayItinerary(
            day_number=1, date=date(2024, 8, 1),
            activities=[
                {"name": "Colosseum", "category": "attractions", "cost": 25},
                {"name": "Roman Forum", "category": "history", "cost": 16},
                {"name": "Trattoria lunch", "category": "dining", "cost": 30},
                {"name": "Pizza dinner", "category": "dining", "cost": 40},
                {"name": "Metro day pass", "category": "transportation", "cost": 8},
            ],
            accommodation={"name": "Hotel Roma Centro", "cost_per_night": 180},
        ),
        DayItinerary(
            day_number=2, date=date(2024, 8, 2),
            activities=[
                {"name": "Vatican Museums", "category": "culture", "cost": 35},
                {"name": "St Peter's Basilica", "category": "culture", "cost": 0},
                {"name": "Lunch near Vatican", "category": "dining", "cost": 25},
                {"name": "Trastevere dinner", "category": "dining", "cost": 50},
                {"name": "Bus tickets", "category": "transportation", "cost": 5},
            ],
            accommodation={"name": "Hotel Roma Centro", "cost_per_night": 180},
        ),
        DayItinerary(
            day_number=3, date=date(2024, 8, 3),
            activities=[
                {"name": "Borghese Gallery", "category": "attractions", "cost": 20},
                {"name": "Piazza Navona stroll", "category": "sightseeing", "cost": 0},
                {"name": "Street food lunch", "category": "dining", "cost": 15},
                {"name": "Upscale dinner", "category": "dining", "cost": 90},
                {"name": "Souvenir shopping", "category": "shopping", "cost": 80},
                {"name": "Taxi", "category": "transportation", "cost": 20},
            ],
            accommodation={"name": "Hotel Roma Centro", "cost_per_night": 180},
        ),
        DayItinerary(
            day_number=4, date=date(2024, 8, 4),
            activities=[
                {"name": "Day trip to Tivoli", "category": "nature", "cost": 30},
                {"name": "Train to Tivoli", "category": "transportation", "cost": 12},
                {"name": "Lunch in Tivoli", "category": "dining", "cost": 20},
                {"name": "Dinner back in Rome", "category": "dining", "cost": 45},
                {"name": "Leather goods shopping", "category": "shopping", "cost": 120},
            ],
            accommodation={"name": "Hotel Roma Centro", "cost_per_night": 180},
        ),
        DayItinerary(
            day_number=5, date=date(2024, 8, 5),
            activities=[
                {"name": "Palatine Hill", "category": "history", "cost": 16},
                {"name": "Gelato & espresso", "category": "dining", "cost": 12},
                {"name": "Final lunch", "category": "dining", "cost": 28},
                {"name": "Airport transfer", "category": "transportation", "cost": 45},
                {"name": "Last-minute gifts", "category": "shopping", "cost": 60},
            ],
            accommodation=None,
        ),
    ]
    context = PlanningContext()
    context.travel_profile = TravelProfile(
        destination="Rome",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 5),
        budget=1500,
        group_size=2,
        travel_style="cultural",
        interests=["history", "food", "art"],
    )
    context.itinerary = Itinerary(
        location="Rome",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 5),
        days=days,
    )
    return context


def _make_profile(budget: float) -> TravelProfile:
    return TravelProfile(
        destination="Rome",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 7),
        budget=budget,
        group_size=2,
        travel_style="cultural",
    )


def _make_context(budget: float, days=None) -> PlanningContext:
    context = PlanningContext()
    context.travel_profile = _make_profile(budget)
    context.itinerary = Itinerary(
        location="Rome",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 7),
        days=days or [],
    )
    return context


@pytest.fixture
def sample_context():
    return _make_context(budget=5000)


# ── basic sanity ─────────────────────────────────────────────────────────────

def test_agent_initialization(agent):
    assert agent.name == "Cost Optimization Agent"


def test_validate_input_success(agent, sample_context):
    assert agent.validate_input(sample_context) is True


def test_validate_input_missing_itinerary(agent, sample_context):
    sample_context.itinerary = None
    assert agent.validate_input(sample_context) is False


def test_validate_input_missing_profile(agent, sample_context):
    sample_context.travel_profile = None
    assert agent.validate_input(sample_context) is False


# ── _analyze_costs ───────────────────────────────────────────────────────────

def test_analyze_costs_empty_itinerary(agent, sample_context):
    breakdown = agent._analyze_costs(sample_context.itinerary)
    assert breakdown.total == 0.0


def test_analyze_costs_accumulates_accommodation(agent):
    days = [
        DayItinerary(day_number=1, date=date(2024, 8, 1), activities=[],
                     accommodation={"name": "Hotel A", "cost_per_night": 100}),
        DayItinerary(day_number=2, date=date(2024, 8, 2), activities=[],
                     accommodation={"name": "Hotel B", "cost_per_night": 150}),
    ]
    itinerary = Itinerary(location="Rome", start_date=date(2024, 8, 1),
                          end_date=date(2024, 8, 2), days=days)
    breakdown = agent._analyze_costs(itinerary)
    assert breakdown.accommodation == 250.0


def test_analyze_costs_maps_categories(agent):
    days = [
        DayItinerary(day_number=1, date=date(2024, 8, 1), activities=[
            {"name": "Lunch", "category": "dining", "cost": 40},
            {"name": "Metro", "category": "transportation", "cost": 10},
            {"name": "Museum", "category": "culture", "cost": 20},
            {"name": "Souvenir", "category": "shopping", "cost": 30},
        ], accommodation=None),
    ]
    itinerary = Itinerary(location="Rome", start_date=date(2024, 8, 1),
                          end_date=date(2024, 8, 1), days=days)
    breakdown = agent._analyze_costs(itinerary)
    assert breakdown.dining == 40.0
    assert breakdown.transportation == 10.0
    assert breakdown.attractions == 20.0
    assert breakdown.shopping == 30.0


def test_analyze_costs_unknown_category_goes_to_misc(agent):
    days = [
        DayItinerary(day_number=1, date=date(2024, 8, 1), activities=[
            {"name": "Weird thing", "category": "mystery", "cost": 55},
        ], accommodation=None),
    ]
    itinerary = Itinerary(location="Rome", start_date=date(2024, 8, 1),
                          end_date=date(2024, 8, 1), days=days)
    breakdown = agent._analyze_costs(itinerary)
    assert breakdown.miscellaneous == 55.0


def test_analyze_costs_contingency_is_5_percent(agent):
    days = [
        DayItinerary(day_number=1, date=date(2024, 8, 1), activities=[
            {"name": "Dinner", "category": "dining", "cost": 200},
        ], accommodation=None),
    ]
    itinerary = Itinerary(location="Rome", start_date=date(2024, 8, 1),
                          end_date=date(2024, 8, 1), days=days)
    breakdown = agent._analyze_costs(itinerary)
    assert breakdown.contingency == pytest.approx(10.0, abs=0.01)


# ── _generate_recommendations ────────────────────────────────────────────────

def test_no_recommendations_within_budget(agent):
    breakdown = CostBreakdown(accommodation=500, dining=200)
    recs = agent._generate_recommendations(breakdown, budget=10000,
                                           travel_profile=_make_profile(10000))
    assert recs == []


def test_recommendations_capped_at_3(agent):
    breakdown = CostBreakdown(
        accommodation=3000, dining=1000, shopping=500,
        transportation=400, attractions=300, miscellaneous=200,
    )
    with patch.object(agent, "_fetch_suggestions", return_value={}):
        recs = agent._generate_recommendations(breakdown, budget=100,
                                               travel_profile=_make_profile(100))
    assert len(recs) <= 3


def test_recommendations_sorted_by_savings_descending(agent):
    breakdown = CostBreakdown(
        accommodation=3000, dining=1000, shopping=500,
        transportation=400, attractions=300, miscellaneous=200,
    )
    with patch.object(agent, "_fetch_suggestions", return_value={}):
        recs = agent._generate_recommendations(breakdown, budget=100,
                                               travel_profile=_make_profile(100))
    savings = [r.potential_savings for r in recs]
    assert savings == sorted(savings, reverse=True)


def test_recommendations_use_llm_suggestion(agent):
    breakdown = CostBreakdown(accommodation=3000)
    llm_text = "Book a family-run B&B near the Colosseum instead of a central hotel."
    with patch.object(agent, "_fetch_suggestions",
                      return_value={"accommodation": llm_text}):
        recs = agent._generate_recommendations(breakdown, budget=0,
                                               travel_profile=_make_profile(0))
    assert recs[0].suggestion == llm_text


def test_recommendations_fallback_when_llm_fails(agent):
    breakdown = CostBreakdown(accommodation=3000)
    with patch.object(agent, "_fetch_suggestions", return_value={}):
        recs = agent._generate_recommendations(breakdown, budget=0,
                                               travel_profile=_make_profile(0))
    # Falls back to generic text — should not raise
    assert len(recs) == 1
    assert "accommodation" in recs[0].suggestion.lower()


def test_recommendations_skip_zero_categories(agent):
    breakdown = CostBreakdown(accommodation=5000)
    with patch.object(agent, "_fetch_suggestions", return_value={}):
        recs = agent._generate_recommendations(breakdown, budget=0,
                                               travel_profile=_make_profile(0))
    assert all(r.category == "accommodation" for r in recs)


# ── _fetch_suggestions (LLM integration) ─────────────────────────────────────

def _mock_openai_response(content: str):
    """Build a minimal mock matching openai.ChatCompletion structure."""
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


def test_fetch_suggestions_parses_array(agent):
    payload = json_payload = (
        '[{"category": "accommodation", "suggestion": "Try a hostel near Trastevere."}]'
    )
    agent._client.chat.completions.create = MagicMock(
        return_value=_mock_openai_response(payload)
    )
    result = agent._fetch_suggestions(
        [{"category": "accommodation", "amount": 1000, "potential_savings": 300, "confidence": 0.3}],
        CostBreakdown(accommodation=1000),
        budget=500,
        travel_profile=_make_profile(500),
    )
    assert result["accommodation"] == "Try a hostel near Trastevere."


def test_fetch_suggestions_parses_wrapped_object(agent):
    payload = '{"suggestions": [{"category": "dining", "suggestion": "Eat at trattorias."}]}'
    agent._client.chat.completions.create = MagicMock(
        return_value=_mock_openai_response(payload)
    )
    result = agent._fetch_suggestions(
        [{"category": "dining", "amount": 500, "potential_savings": 100, "confidence": 0.2}],
        CostBreakdown(dining=500),
        budget=200,
        travel_profile=_make_profile(200),
    )
    assert result["dining"] == "Eat at trattorias."


def test_fetch_suggestions_returns_empty_on_api_error(agent):
    agent._client.chat.completions.create = MagicMock(side_effect=Exception("API down"))
    result = agent._fetch_suggestions(
        [{"category": "shopping", "amount": 200, "potential_savings": 80, "confidence": 0.4}],
        CostBreakdown(shopping=200),
        budget=100,
        travel_profile=_make_profile(100),
    )
    assert result == {}


# ── end-to-end process ────────────────────────────────────────────────────────

def test_process_creates_final_handbook(agent, sample_context):
    with patch.object(agent, "_fetch_suggestions", return_value={}):
        result = agent.process(sample_context)
    assert result.final_handbook is not None
    assert result.final_handbook.destination == "Rome"


def test_process_adds_warning_when_over_budget(agent):
    days = [
        DayItinerary(day_number=1, date=date(2024, 8, 1), activities=[
            {"name": "Dinner", "category": "dining", "cost": 9999},
        ], accommodation=None),
    ]
    ctx = _make_context(budget=100, days=days)
    with patch.object(agent, "_fetch_suggestions", return_value={}):
        result = agent.process(ctx)
    assert any("exceeds budget" in w for w in result.warnings)


def test_process_no_warning_within_budget(agent):
    ctx = _make_context(budget=999999)
    with patch.object(agent, "_fetch_suggestions", return_value={}):
        result = agent.process(ctx)
    assert not any("exceeds budget" in w for w in result.warnings)


# ── 5-day end-to-end ─────────────────────────────────────────────────────────

def test_five_day_cost_breakdown_totals(agent, five_day_context):
    breakdown = agent._analyze_costs(five_day_context.itinerary)
    # 4 nights × 180 = 720
    assert breakdown.accommodation == 720.0
    # dining: 30+40+25+50+15+90+20+45+12+28 = 355
    assert breakdown.dining == 355.0
    # attractions/culture/history/sightseeing/nature → attractions bucket
    # 25+16+35+20+30+16 = 142
    assert breakdown.attractions == 142.0
    # shopping: 80+120+60 = 260
    assert breakdown.shopping == 260.0
    # transportation: 8+5+20+12+45 = 90
    assert breakdown.transportation == 90.0
    # contingency = (720+355+142+260+90) * 0.05
    expected_contingency = round((720 + 355 + 142 + 260 + 90) * 0.05, 2)
    assert breakdown.contingency == expected_contingency


def test_five_day_over_budget_gets_recommendations(agent, five_day_context):
    # budget=1500, total will be ~1567+contingency → over budget
    with patch.object(agent, "_fetch_suggestions", return_value={
        "accommodation": "Stay in a guesthouse in Trastevere instead of central hotel.",
        "shopping": "Skip the leather market and buy gifts at local supermarkets.",
        "dining": "Eat at local mercati instead of tourist-facing restaurants.",
    }):
        result = agent.process(five_day_context)

    recs = result.final_handbook.optimization_recommendations
    assert len(recs) > 0
    assert len(recs) <= 3
    assert any(r.category == "accommodation" for r in recs)


def test_five_day_recommendations_use_llm_text(agent, five_day_context):
    llm_suggestions = {
        "accommodation": "Stay in a guesthouse in Trastevere instead of central hotel.",
        "shopping": "Skip the leather market and buy gifts at local supermarkets.",
        "dining": "Eat at local mercati instead of tourist-facing restaurants.",
    }
    with patch.object(agent, "_fetch_suggestions", return_value=llm_suggestions):
        result = agent.process(five_day_context)

    recs = result.final_handbook.optimization_recommendations
    for rec in recs:
        if rec.category in llm_suggestions:
            assert rec.suggestion == llm_suggestions[rec.category]


def test_five_day_warning_emitted(agent, five_day_context):
    with patch.object(agent, "_fetch_suggestions", return_value={}):
        result = agent.process(five_day_context)
    assert any("exceeds budget" in w for w in result.warnings)


def test_five_day_handbook_budget_remaining(agent, five_day_context):
    with patch.object(agent, "_fetch_suggestions", return_value={}):
        result = agent.process(five_day_context)
    hb = result.final_handbook
    assert hb.budget_remaining == pytest.approx(hb.budget - hb.cost_breakdown.total, abs=0.01)
    assert not hb.is_within_budget


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
