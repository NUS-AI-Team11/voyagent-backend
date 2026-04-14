"""
Tests for Dining Recommendation Agent.
"""

import pytest
from models.schemas import TravelProfile, DiningList, PlanningContext
from agents.dining_recommendation.agent import DiningRecommendationAgent
from datetime import date


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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
