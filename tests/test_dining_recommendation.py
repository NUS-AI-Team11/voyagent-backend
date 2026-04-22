"""
Tests for Dining Recommendation Agent.
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch

from agents.dining_recommendation.agent import DiningRecommendationAgent
from models.schemas import PlanningContext, TravelProfile


@pytest.fixture
def agent():
    return DiningRecommendationAgent()


@pytest.fixture
def sample_context():
    context = PlanningContext()
    context.travel_profile = TravelProfile(
        destination='Tokyo',
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 7),
        budget=4000,
        group_size=2,
        travel_style='food',
        dietary_restrictions=['vegetarian']
    )
    return context


def test_agent_initialization(agent):
    assert agent.name == "Dining Recommendation Agent"


def test_process_valid_input(agent, sample_context):
    result = agent.process(sample_context)

    assert result is not None


def test_process_missing_travel_profile(agent):
    context = PlanningContext()

    result = agent.process(context)

    assert len(result.errors) > 0


def test_get_deepseek_model_normalizes_version_name(agent, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_MODEL", "DeepSeek-V3.2")

    assert agent._get_deepseek_model() == "deepseek-chat"


def test_recommend_restaurants_llm_uses_deepseek_response(agent):
    profile = TravelProfile(
        destination="Tokyo",
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 7),
        budget=4000,
        group_size=2,
        travel_style="food",
        dietary_restrictions=["vegetarian"],
    )
    fake_client = Mock()
    fake_client.chat.completions.create.return_value = Mock(
        choices=[
            Mock(
                message=Mock(
                    content='{"restaurants":[{"name":"Test Dining","cuisine":"Japanese","address":"Tokyo Station","price_range":"$$","rating":4.5,"average_cost_per_person":25,"opening_hours":"10:00 - 22:00","reservations_needed":false,"special_notes":"Vegetarian options available"}]}'
                )
            )
        ]
    )

    with patch.object(agent, "_create_deepseek_client", return_value=fake_client):
        restaurants = agent._recommend_restaurants_llm(profile)

    assert len(restaurants) == 1
    assert restaurants[0].name == "Test Dining"
    assert restaurants[0].cuisine_type == "Japanese"


def test_resolve_api_key_prefers_deepseek_key(agent, monkeypatch):
    monkeypatch.delenv("DINING_OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-deepseek-test")

    key, source = agent._resolve_api_key()
    assert key == "sk-deepseek-test"
    assert source == "DEEPSEEK_API_KEY"


def test_mock_recommendation_for_non_tokyo_uses_destination_name(agent):
    profile = TravelProfile(
        destination="Singapore",
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 3),
        budget=3000,
        group_size=2,
        travel_style="food",
        dietary_restrictions=[],
    )
    restaurants = agent._recommend_restaurants_mock(profile)
    assert restaurants
    assert any("Singapore" in (r.location or "") or "Singapore" in (r.name or "") for r in restaurants)


def test_normalize_cost_per_person_clamps_outlier(agent):
    profile = TravelProfile(
        destination="Bangkok",
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 4),
        budget=1200,
        group_size=1,
        travel_style="budget",
    )
    normalized = agent._normalize_cost_per_person(
        raw_cost="18850",
        price_range="$$",
        travel_profile=profile,
    )
    assert normalized < 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
