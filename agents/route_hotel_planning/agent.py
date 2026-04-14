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

        while day_number <= num_days:
            day_itinerary = DayItinerary(
                day_number=day_number,
                date=current_date,
                activities=[],
                meals={},
                accommodation=None,
                total_estimated_cost=0.0,
                notes=""
            )

            days.append(day_itinerary)
            current_date += timedelta(days=1)
            day_number += 1

        return days
