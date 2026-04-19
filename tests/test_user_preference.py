"""
Tests for User Preference Agent.
"""

import pytest
from datetime import date
from unittest.mock import Mock
from models.schemas import TravelProfile, PlanningContext
from agents.user_preference.agent import UserPreferenceAgent


@pytest.fixture
def agent():
    return UserPreferenceAgent()


@pytest.fixture
def sample_context():
    context = PlanningContext()
    context.metadata['user_input'] = """
    I want to visit Paris, departing May 15 and returning May 22.
    Budget $5000 for 4 people.
    We enjoy culture and food.
    """
    return context


def test_agent_initialization(agent):
    assert agent.name == "User Preference Agent"
    assert agent.description == "Collects and parses user travel preference information"


def test_process_valid_input(agent, sample_context):
    # Deterministic: avoid relying on LLM when OPENAI_API_KEY is present in the environment.
    agent._client = None
    result = agent.process(sample_context)

    assert result is not None
    assert result.travel_profile is not None
    assert result.travel_profile.destination.lower() == "paris"
    assert result.travel_profile.budget == 5000
    assert result.travel_profile.group_size == 4


def test_process_empty_input(agent):
    context = PlanningContext()
    context.metadata['user_input'] = ''

    result = agent.process(context)

    assert len(result.errors) > 0


def test_validate_required_fields(agent):
    incomplete_data = {
        'destination': 'Paris',
        # other required fields are missing
    }

    missing = agent._validate_required_fields(incomplete_data)

    assert len(missing) > 0
    assert 'budget' in missing


def test_create_travel_profile(agent):
    data = {
        'destination': 'Tokyo',
        'start_date': date(2024, 5, 15),
        'end_date': date(2024, 5, 22),
        'budget': 3000,
        'group_size': 2,
        'travel_style': 'adventure',
        'interests': ['temples', 'food'],
    }

    profile = agent._create_travel_profile(data)

    assert profile.destination == 'Tokyo'
    assert profile.budget == 3000
    assert profile.group_size == 2


def test_extract_preferences_llm_path(agent):
    fake_client = Mock()
    fake_client.chat.completions.create.return_value = Mock(
        choices=[
            Mock(
                message=Mock(
                    content='{"destination":"Seoul","start_date":"2026-06-01","end_date":"2026-06-05","budget":2400,"group_size":2,"travel_style":"food","interests":["food","culture"],"dietary_restrictions":[],"hotel_preference":"comfortable","transportation_preference":"public_transit","custom_notes":"test"}'
                )
            )
        ]
    )
    agent._client = fake_client
    agent._model = "gpt-4o-mini"

    parsed = agent._extract_preferences("Plan a trip to Seoul")

    assert parsed["destination"] == "Seoul"
    assert parsed["budget"] == 2400
    assert parsed["group_size"] == 2
    assert parsed["start_date"] == date(2026, 6, 1)
    assert parsed["end_date"] == date(2026, 6, 5)


def test_extract_preferences_fallback_when_no_client(agent):
    agent._client = None
    parsed = agent._extract_preferences(
        "I want to visit Rome, departing June 10 and returning June 15. Budget $3200 for 3 people. We enjoy culture and food."
    )

    assert parsed["destination"].lower() == "rome"
    assert parsed["budget"] == 3200
    assert parsed["group_size"] == 3
    assert parsed["travel_style"] in {"culture", "food", "general"}


def test_parse_budget_usd_phrase(agent):
    text = (
        "Our total budget is USD 4,200 (excluding flights). "
        "We are 2 adults traveling April 8–April 13, 2026."
    )
    assert agent._parse_budget(text) == 4200.0


def test_safe_float_strips_currency_string(agent):
    assert agent._safe_float("USD 4,200", default=0.0) == 4200.0
    assert agent._safe_float("$1,234.50", default=0.0) == 1234.5


def test_normalize_repairs_budget_from_raw_text(agent):
    raw = "Planning Kyoto. Our total budget is USD 4,200 for 2 adults."
    normalized = agent._normalize_preference_data({"destination": "Kyoto", "budget": "USD 4,200"}, raw)
    assert normalized["budget"] == 4200.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
