"""
Tests for Route & Hotel Planning Agent.
"""

import pytest
from models.schemas import TravelProfile, SpotList, DiningList, PlanningContext
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


def test_validate_input_success(agent, sample_context):
    assert agent.validate_input(sample_context) is True


def test_validate_input_missing_spot_list(agent, sample_context):
    sample_context.spot_list = None

    assert agent.validate_input(sample_context) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
