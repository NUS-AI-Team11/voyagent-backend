"""
Tests for Cost Optimization Agent.
"""

import pytest
from models.schemas import TravelProfile, Itinerary, DayItinerary, PlanningContext
from agents.cost_optimization.agent import CostOptimizationAgent
from datetime import date


@pytest.fixture
def agent():
    return CostOptimizationAgent()


@pytest.fixture
def sample_context():
    context = PlanningContext()
    context.travel_profile = TravelProfile(
        destination='Rome',
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 7),
        budget=5000,
        group_size=2,
        travel_style='cultural'
    )
    context.itinerary = Itinerary(
        location='Rome',
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 7),
        days=[]
    )
    return context


def test_agent_initialization(agent):
    assert agent.name == "Cost Optimization Agent"


def test_process_valid_input(agent, sample_context):
    result = agent.process(sample_context)

    assert result is not None


def test_validate_input_success(agent, sample_context):
    assert agent.validate_input(sample_context) is True


def test_validate_input_missing_itinerary(agent, sample_context):
    sample_context.itinerary = None

    assert agent.validate_input(sample_context) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
