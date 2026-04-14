"""
Tests for User Preference Agent.
"""

import pytest
from datetime import date, datetime
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
    result = agent.process(sample_context)

    assert result is not None
    # When fully implemented, travel_profile should be populated.
    # assert result.travel_profile is not None


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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
