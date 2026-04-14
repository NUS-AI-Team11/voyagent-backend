"""
Tests for Spot Recommendation Agent.
"""

import pytest
from models.schemas import TravelProfile, SpotList, PlanningContext
from agents.spot_recommendation.agent import SpotRecommendationAgent
from datetime import date


@pytest.fixture
def agent():
    return SpotRecommendationAgent()


@pytest.fixture
def sample_context():
    context = PlanningContext()
    context.travel_profile = TravelProfile(
        destination='Paris',
        start_date=date(2024, 5, 15),
        end_date=date(2024, 5, 22),
        budget=5000,
        group_size=4,
        travel_style='culture',
        interests=['history', 'art', 'museums']
    )
    return context


def test_agent_initialization(agent):
    assert agent.name == "Spot Recommendation Agent"
    assert agent.description == "Recommends attractions matching user travel preferences"


def test_process_valid_input(agent, sample_context):
    result = agent.process(sample_context)

    assert result is not None
    # When fully implemented, spot_list should be populated.
    # assert result.spot_list is not None


def test_process_missing_travel_profile(agent):
    context = PlanningContext()

    result = agent.process(context)

    assert len(result.errors) > 0


def test_validate_input_success(agent, sample_context):
    assert agent.validate_input(sample_context) is True


def test_validate_input_failure(agent):
    context = PlanningContext()

    assert agent.validate_input(context) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
