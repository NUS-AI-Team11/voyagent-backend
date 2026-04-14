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

        TODO:
            Replace the mock data below with a real LLM call.
            Steps:
              1. Format DINING_RECOMMENDATION_PROMPT with travel_profile fields
                 (destination, dietary_restrictions, budget, group_size, travel_style)
              2. Call your LLM client with SYSTEM_PROMPT + the formatted prompt
              3. Parse the JSON list the LLM returns
              4. Convert each item into a Restaurant object and return the list

            Each Restaurant needs: name, cuisine_type, location, price_range,
            rating, average_cost_per_person, opening_hours.
            price_range uses: $ / $$ / $$$ / $$$$
        """
        # ---------------------------------------------------------------------------
        # MOCK DATA — two placeholder restaurants so the pipeline can run end-to-end.
        # Delete this block and replace it with your LLM call when you implement the
        # real agent logic.
        # ---------------------------------------------------------------------------
        restaurants = [
            Restaurant(
                name="Ichiran Ramen Shibuya",
                cuisine_type="Japanese Ramen",
                location="Dogenzaka, Shibuya City, Tokyo",
                price_range="$$",
                rating=4.5,
                average_cost_per_person=15.0,
                opening_hours="10:00 - 02:00",
                reservations_needed=False,
            ),
            Restaurant(
                name="Tsukiji Outer Market",
                cuisine_type="Seafood / Street Food",
                location="Tsukiji, Chuo City, Tokyo",
                price_range="$$",
                rating=4.6,
                average_cost_per_person=20.0,
                opening_hours="05:00 - 14:00",
                reservations_needed=False,
            ),
        ]
        # ---------------------------------------------------------------------------
        return restaurants
