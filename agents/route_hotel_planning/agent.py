"""
Route & Hotel Planning Agent - plans the full itinerary and hotel arrangement.
"""

from agents.base_agent import BaseAgent
from models.schemas import (
    Itinerary, DayItinerary, TravelProfile, SpotList,
    DiningList, PlanningContext
)
from agents.route_hotel_planning.prompts import (
    SYSTEM_PROMPT,
    ITINERARY_CREATION_PROMPT,
    HOTEL_RECOMMENDATION_PROMPT,
    ROUTE_OPTIMIZATION_PROMPT,
    DAILY_SCHEDULE_PROMPT
)
from typing import List
from datetime import datetime, timedelta


class RouteHotelPlanningAgent(BaseAgent):
    """Agent that plans routes and hotel accommodation."""

    def __init__(self):
        super().__init__(
            name="Route & Hotel Planning Agent",
            description="Plans a complete day-by-day itinerary and hotel arrangement based on spot and restaurant recommendations"
        )

    def process(self, context: PlanningContext) -> PlanningContext:
        """
        Process spot and restaurant recommendations and generate a full itinerary.

        Args:
            context: planning context containing TravelProfile, SpotList, DiningList

        Returns:
            context with itinerary populated
        """
        try:
            if not self.validate_input(context):
                context.add_error("Missing required input")
                return context

            travel_profile = context.travel_profile
            spot_list = context.spot_list
            dining_list = context.dining_list

            days = self._create_daily_itineraries(
                travel_profile,
                spot_list,
                dining_list
            )

            itinerary = Itinerary(
                location=travel_profile.destination,
                start_date=travel_profile.start_date,
                end_date=travel_profile.end_date,
                days=days,
                estimated_total_cost=sum(day.total_estimated_cost for day in days),
                cost_breakdown={
                    'transport': 0.0,
                    'accommodation': 0.0,
                    'food': 0.0,
                    'attractions': 0.0,
                },
                generated_at=datetime.now()
            )

            context.itinerary = itinerary
            self.log_execution(f"Created {len(days)}-day itinerary")

        except Exception as e:
            context.add_error(f"Itinerary planning failed: {str(e)}")
            self.log_execution(f"Error: {str(e)}", level="error")

        return context

    def validate_input(self, context: PlanningContext) -> bool:
        """Validate required input."""
        return (
            context.travel_profile is not None and
            context.spot_list is not None and
            context.dining_list is not None
        )

    def _create_daily_itineraries(
        self,
        travel_profile: TravelProfile,
        spot_list: SpotList,
        dining_list: DiningList
    ) -> List[DayItinerary]:
        """
        Create a detailed itinerary for each day.

        Args:
            travel_profile: user travel information
            spot_list: recommended attractions
            dining_list: recommended restaurants

        Returns:
            list of DayItinerary objects
        """
        days = []
        current_date = travel_profile.start_date
        day_number = 1

        num_days = (travel_profile.end_date - travel_profile.start_date).days + 1

        # TODO:
        #   Replace the skeleton loop below with real itinerary generation.
        #   Steps:
        #     1. Distribute spot_list.spots across the days (e.g. 2-3 spots per day)
        #     2. For each day assign meals from dining_list.restaurants
        #     3. Call LLM with ITINERARY_CREATION_PROMPT to build the activities list
        #        and with HOTEL_RECOMMENDATION_PROMPT to fill accommodation
        #     4. Populate total_estimated_cost by summing entrance fees + meal costs
        #
        #   Each activity dict should look like:
        #     {"time": "09:00", "name": "...", "location": "...", "cost": 0.0, "duration_hours": 2.0}
        #   accommodation dict should look like:
        #     {"name": "...", "address": "...", "cost_per_night": 100.0, "rating": 4.2}

        while day_number <= num_days:
            # -----------------------------------------------------------------------
            # MOCK DATA — empty skeleton so the pipeline can run end-to-end.
            # Fill in activities, meals, and accommodation when you implement the
            # real agent logic.
            # -----------------------------------------------------------------------
            day_itinerary = DayItinerary(
                day_number=day_number,
                date=current_date,
                activities=[
                    # Placeholder — replace with real scheduled activities
                    {"time": "09:00", "name": f"Day {day_number} Morning Activity", "location": "TBD", "cost": 0.0}
                ],
                meals={
                    # Placeholder — replace with real restaurant picks from dining_list
                    "breakfast": "TBD",
                    "lunch": "TBD",
                    "dinner": "TBD",
                },
                accommodation=None,   # Placeholder — replace with hotel from LLM
                total_estimated_cost=0.0,
                notes="Placeholder itinerary — to be replaced by real LLM output"
            )
            # -----------------------------------------------------------------------

            days.append(day_itinerary)
            current_date += timedelta(days=1)
            day_number += 1

        return days
