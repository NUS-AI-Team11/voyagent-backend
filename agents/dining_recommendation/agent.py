"""
Dining Recommendation Agent - recommends restaurants and dining options.
"""

from agents.base_agent import BaseAgent
from models.schemas import DiningList, Restaurant, TravelProfile, PlanningContext
from agents.dining_recommendation.prompts import (
    SYSTEM_PROMPT,
    DINING_RECOMMENDATION_PROMPT,
    MEAL_PLAN_PROMPT,
    BUDGET_DINING_PROMPT
)
from typing import List
from datetime import datetime


class DiningRecommendationAgent(BaseAgent):
    """Agent that recommends dining options based on user preferences."""

    def __init__(self):
        super().__init__(
            name="Dining Recommendation Agent",
            description="Recommends restaurants and dining options matching user dietary preferences and budget"
        )

    def process(self, context: PlanningContext) -> PlanningContext:
        """
        Process user preferences and generate a dining recommendation list.

        Args:
            context: planning context containing a TravelProfile

        Returns:
            context with dining_list populated
        """
        try:
            if not context.travel_profile:
                context.add_error("Missing travel profile")
                return context

            if not self.validate_input(context):
                context.add_error("Input validation failed")
                return context

            travel_profile = context.travel_profile

            restaurants = self._recommend_restaurants(travel_profile)

            dining_list = DiningList(
                restaurants=restaurants,
                meal_type="all",
                filter_criteria={
                    'destination': travel_profile.destination,
                    'dietary_restrictions': travel_profile.dietary_restrictions,
                    'budget': travel_profile.budget
                },
                total_count=len(restaurants),
                generated_at=datetime.now()
            )

            context.dining_list = dining_list
            self.log_execution(f"Recommended {len(restaurants)} restaurants")

        except Exception as e:
            context.add_error(f"Dining recommendation failed: {str(e)}")
            self.log_execution(f"Error: {str(e)}", level="error")

        return context

    def validate_input(self, context: PlanningContext) -> bool:
        """Validate required input."""
        return context.travel_profile is not None

    def _recommend_restaurants(self, travel_profile: TravelProfile) -> List[Restaurant]:
        """
        Generate a list of recommended restaurants based on user preferences.

        Args:
            travel_profile: user travel information

        Returns:
            list of recommended Restaurant objects
        """
        # Real implementation would call an LLM or query a database.
        restaurants = []
        return restaurants
