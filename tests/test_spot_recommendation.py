"""
Tests for Spot Recommendation Agent.
"""

import json

import pytest
from models.schemas import TravelProfile, PlanningContext
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
    assert result.spot_list is not None
    assert result.spot_list.total_count >= 1
    assert len(result.spot_list.spots) == result.spot_list.total_count


def test_process_missing_travel_profile(agent):
    context = PlanningContext()

    result = agent.process(context)

    assert len(result.errors) > 0


def test_validate_input_success(agent, sample_context):
    assert agent.validate_input(sample_context) is True


def test_validate_input_failure(agent):
    context = PlanningContext()

    assert agent.validate_input(context) is False


def test_recommend_spots_uses_openai_when_client_available(agent, sample_context, monkeypatch):
    class FakeChatCompletions:
        @staticmethod
        def create(**kwargs):
            assert kwargs["model"] == agent.model
            return type(
                "FakeResponse",
                (),
                {
                    "choices": [
                        type(
                            "Choice",
                            (),
                            {
                                "message": type(
                                    "Message",
                                    (),
                                    {
                                        "content": json.dumps(
                                            {
                                                "spots": [
                                                    {
                                                        "name": "Louvre Museum",
                                                        "description": "Major art museum in Paris.",
                                                        "location": "Rue de Rivoli, Paris",
                                                        "category": "art",
                                                        "opening_hours": "09:00 - 18:00",
                                                        "entrance_fee": 22.0,
                                                        "rating": 4.8,
                                                        "duration_hours": 3.0,
                                                        "best_season": "year-round",
                                                        "accessibility_notes": "Accessible entrances available.",
                                                    }
                                                ]
                                            }
                                        )
                                    },
                                )()
                            },
                        )()
                    ]
                },
            )()

    fake_client = type(
        "FakeClient",
        (),
        {"chat": type("Chat", (), {"completions": FakeChatCompletions()})()},
    )()
    monkeypatch.setattr(agent, "_get_client", lambda: fake_client)

    spots = agent._recommend_spots(sample_context.travel_profile)

    assert len(spots) == 1
    assert spots[0].name == "Louvre Museum"
    assert spots[0].category == "art"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
