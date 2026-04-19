"""
Tests for Route & Hotel Planning Agent.
"""

import pytest
import urllib.request
from models.schemas import TravelProfile, SpotList, Spot, DiningList, PlanningContext
from agents.route_hotel_planning.agent import RouteHotelPlanningAgent
from datetime import date


@pytest.fixture
def agent():
    return RouteHotelPlanningAgent()


@pytest.fixture
def sample_context():
    context = PlanningContext()
    context.travel_profile = TravelProfile(
        destination='Barcelona',
        start_date=date(2024, 7, 1),
        end_date=date(2024, 7, 5),
        budget=6000,
        group_size=3,
        travel_style='mix'
    )
    context.spot_list = SpotList()
    context.dining_list = DiningList()
    return context


def test_agent_initialization(agent):
    assert agent.name == "Route & Hotel Planning Agent"


def test_process_valid_input(agent, sample_context):
    result = agent.process(sample_context)

    assert result is not None


def test_analyze_independently_returns_itinerary(agent, sample_context):
    itinerary = agent.analyze_independently(
        travel_profile=sample_context.travel_profile,
        spot_list=sample_context.spot_list,
        dining_list=sample_context.dining_list,
    )

    assert itinerary is not None
    assert itinerary.location == sample_context.travel_profile.destination
    assert len(itinerary.days) == 5


def test_validate_input_success(agent, sample_context):
    assert agent.validate_input(sample_context) is True


def test_validate_input_missing_spot_list(agent, sample_context):
    sample_context.spot_list = None

    assert agent.validate_input(sample_context) is False


def test_independent_api_config_interface(agent):
    updated = agent.configure_api(
        api_key="test-key",
        model="gpt-test",
        base_url="https://example.com/v1/responses",
        timeout_seconds=9,
        temperature=0.4,
        api_mode="off",
    )

    assert updated["api_key"] == "***"
    assert updated["model"] == "gpt-test"
    assert updated["api_mode"] == "off"
    assert agent.is_api_enabled() is False

    with_secret = agent.get_api_config(include_secret=True)
    assert with_secret["api_key"] == "test-key"

    reset = agent.reset_api_config()
    assert "api_key" in reset
    assert "model" in reset


def test_fetch_agent_api_response_success_with_mock(agent, monkeypatch):
    agent.configure_api(api_key="test-key", base_url="https://example.com/v1/responses", api_mode="auto")

    class DummyResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"output_text": "[]"}'

    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: DummyResponse())

    payload = agent.fetch_agent_api_response(user_prompt="hello")
    assert isinstance(payload, dict)
    assert payload.get("output_text") == "[]"


def test_fetch_agent_api_response_off_mode_skips_http(agent, monkeypatch):
    agent.configure_api(api_key="test-key", api_mode="off")

    called = {"value": False}

    def _should_not_call(*args, **kwargs):
        called["value"] = True
        raise AssertionError("urlopen should not be called when api_mode=off")

    monkeypatch.setattr(urllib.request, "urlopen", _should_not_call)

    payload = agent.fetch_agent_api_response(user_prompt="hello")
    assert payload is None
    assert called["value"] is False


def test_hotel_api_auto_mode_returns_none_on_api_failure(agent, monkeypatch):
    agent.configure_api(api_key="test-key", api_mode="auto")
    monkeypatch.setattr(agent, "fetch_agent_api_response", lambda **kwargs: None)

    result = agent._fetch_hotel_candidates_via_api(
        destination="Tokyo",
        addresses=["Asakusa, Tokyo"],
        base_nightly_cost=180.0,
        group_size=2,
    )
    assert result is None


def test_hotel_api_forced_mode_logs_warning_when_api_unavailable(agent, monkeypatch):
    agent.configure_api(api_key="test-key", api_mode="forced")
    monkeypatch.setattr(agent, "fetch_agent_api_response", lambda **kwargs: None)

    logs = []
    monkeypatch.setattr(agent, "log_execution", lambda message, level="info": logs.append((message, level)))

    result = agent._fetch_hotel_candidates_via_api(
        destination="Tokyo",
        addresses=["Asakusa, Tokyo"],
        base_nightly_cost=180.0,
        group_size=2,
    )
    assert result is None
    assert any(level == "warning" and "forced mode" in message for message, level in logs)


def test_agent_isolation_does_not_read_global_openai_api_key(monkeypatch):
    monkeypatch.setenv("ROUTE_HOTEL_OPENAI_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "global-key-should-not-be-used")

    isolated_agent = RouteHotelPlanningAgent()
    assert isolated_agent.get_api_config(include_secret=True)["api_key"] == ""
    assert isolated_agent.is_api_enabled() is False


def test_process_without_route_hotel_api_key_still_generates_itinerary(sample_context, monkeypatch):
    monkeypatch.setenv("ROUTE_HOTEL_OPENAI_API_KEY", "")
    isolated_agent = RouteHotelPlanningAgent()

    result = isolated_agent.process(sample_context)
    assert result.itinerary is not None
    assert len(result.itinerary.days) > 0
    assert result.itinerary.days[0].accommodation.get("hotel_candidates")


def test_itinerary_contains_accommodation_address(agent, sample_context):
    result = agent.process(sample_context)

    assert result.itinerary is not None
    assert len(result.itinerary.days) > 0
    first_day = result.itinerary.days[0]
    assert first_day.accommodation is not None
    assert first_day.accommodation.get("address")
    assert isinstance(first_day.accommodation.get("addresses"), list)
    assert len(first_day.accommodation.get("addresses")) > 0


def test_itinerary_contains_multiple_hotel_candidates(agent, sample_context):
    result = agent.process(sample_context)

    first_day = result.itinerary.days[0]
    hotel_candidates = first_day.accommodation.get("hotel_candidates")

    assert isinstance(hotel_candidates, list)
    assert len(hotel_candidates) >= 1
    assert hotel_candidates[0].get("name") == first_day.accommodation.get("name")
    assert hotel_candidates[0].get("address") == first_day.accommodation.get("address")
    assert hotel_candidates[0].get("cost_per_night") == first_day.accommodation.get("cost_per_night")


def test_hotel_candidates_ranked_by_budget_fit(agent):
    candidates = agent._build_hotel_candidates(
        addresses=["A District", "B District", "City Center, Test City"],
        base_nightly_cost=200.0,
        destination="Test City",
    )

    assert candidates[0]["cost_per_night"] == 200.0


def test_resolve_accommodation_addresses_does_not_always_include_city_center(agent):
    addresses = agent._resolve_accommodation_addresses(
        activities=[{"location": "Asakusa, Tokyo"}],
        selected_restaurants=[],
        destination="Tokyo",
    )

    assert "Asakusa, Tokyo" in addresses
    assert "City Center, Tokyo" not in addresses


def test_order_spots_nearest_neighbor_prefers_same_area(agent):
    spots = [
        Spot(name="A1", description="", location="X District, Test City", category="culture"),
        Spot(name="B", description="", location="Y District, Test City", category="culture"),
        Spot(name="A2", description="", location="X District, Test City", category="culture"),
    ]

    ordered = agent._order_spots_nearest_neighbor(spots)
    assert [spot.name for spot in ordered] == ["A1", "A2", "B"]


def test_build_dynamic_activities_applies_opening_hours_and_transit(agent):
    spots = [
        Spot(
            name="Late Opening Museum",
            description="",
            location="Museum Quarter, Test City",
            category="art",
            opening_hours="11:00-18:00",
            duration_hours=1.5,
        ),
        Spot(
            name="Old Town Walk",
            description="",
            location="Old Town, Test City",
            category="history",
            duration_hours=2.0,
        ),
    ]

    activities, _ = agent._build_dynamic_activities(spots, destination="Test City")
    assert activities[0]["time"] == "11:00"
    assert activities[0]["travel_minutes_from_previous"] == 0
    assert activities[1]["travel_minutes_from_previous"] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
