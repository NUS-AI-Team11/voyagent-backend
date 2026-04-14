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

        TODO:
            Replace the mock data below with a real LLM call.
            Steps:
              1. Format SPOT_RECOMMENDATION_PROMPT with travel_profile fields
                 (destination, travel_style, interests, group_size, start_date, end_date)
              2. Call your LLM client with SYSTEM_PROMPT + the formatted prompt
              3. Parse the JSON list the LLM returns
              4. Convert each item into a Spot object and return the list

            Each Spot needs: name, description, location, category,
            opening_hours, entrance_fee, rating, duration_hours.
            Optional: best_season, accessibility_notes.
        """
        # ---------------------------------------------------------------------------
        # MOCK DATA — one placeholder spot so the pipeline can run end-to-end.
        # Delete this block and replace it with your LLM call when you implement the
        # real agent logic.
        # ---------------------------------------------------------------------------
        spots = [
            Spot(
                name="Senso-ji Temple",
                description="Tokyo's oldest Buddhist temple in Asakusa.",
                location="2-3-1 Asakusa, Taito City, Tokyo",
                category="culture",
                opening_hours="06:00 - 17:00",
                entrance_fee=0.0,
                rating=4.8,
                duration_hours=2.0,
                best_season="spring",
                accessibility_notes="Wheelchair accessible main hall",
            ),
            Spot(
                name="Shinjuku Gyoen National Garden",
                description="Large park famous for cherry blossoms.",
                location="11 Naito-cho, Shinjuku City, Tokyo",
                category="nature",
                opening_hours="09:00 - 16:30",
                entrance_fee=5.0,
                rating=4.7,
                duration_hours=2.5,
            ),
        ]
        # ---------------------------------------------------------------------------
        return spots
