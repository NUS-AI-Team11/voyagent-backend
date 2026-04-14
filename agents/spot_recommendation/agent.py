"""
Spot Recommendation Agent - recommends attractions based on user preferences.
"""

from agents.base_agent import BaseAgent
from models.schemas import SpotList, Spot, TravelProfile, PlanningContext
from agents.spot_recommendation.prompts import (
    SYSTEM_PROMPT,
    SPOT_RECOMMENDATION_PROMPT,
    SPOT_FILTERING_PROMPT,
    SPOT_RANKING_PROMPT
)
from typing import List
from datetime import datetime


class SpotRecommendationAgent(BaseAgent):
    """Agent that recommends attractions based on user travel preferences."""

    def __init__(self):
        super().__init__(
            name="Spot Recommendation Agent",
            description="Recommends attractions matching user travel preferences"
        )

    def process(self, context: PlanningContext) -> PlanningContext:
        """
        Process user preferences and generate a spot recommendation list.

        Args:
            context: planning context containing a TravelProfile

        Returns:
            context with spot_list populated
        """
        try:
            if not context.travel_profile:
                context.add_error("Missing travel profile")
                return context

            if not self.validate_input(context):
                context.add_error("Input validation failed")
                return context

            travel_profile = context.travel_profile

            spots = self._recommend_spots(travel_profile)

            spot_list = SpotList(
                spots=spots,
                filter_criteria={
                    'destination': travel_profile.destination,
                    'travel_style': travel_profile.travel_style,
                    'interests': travel_profile.interests
                },
                total_count=len(spots),
                generated_at=datetime.now()
            )

            context.spot_list = spot_list
            self.log_execution(f"Recommended {len(spots)} spots")

        except Exception as e:
            context.add_error(f"Spot recommendation failed: {str(e)}")
            self.log_execution(f"Error: {str(e)}", level="error")

        return context

    def validate_input(self, context: PlanningContext) -> bool:
        """Validate required input."""
        return context.travel_profile is not None

    def _recommend_spots(self, travel_profile: TravelProfile) -> List[Spot]:
        """
        Generate a list of recommended attractions based on user preferences.

        Args:
            travel_profile: user travel information

        Returns:
            list of recommended Spot objects
        """
        # Real implementation would call an LLM or query a database.
        spots = []
        return spots
