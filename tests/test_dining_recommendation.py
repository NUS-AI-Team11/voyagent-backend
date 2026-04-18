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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
