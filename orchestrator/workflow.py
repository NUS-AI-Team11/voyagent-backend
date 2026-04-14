"""
Agent orchestrator - main business logic for the planning pipeline.
"""

import logging
from typing import Dict, Any

from models.schemas import PlanningContext
from agents.user_preference.agent import UserPreferenceAgent
from agents.spot_recommendation.agent import SpotRecommendationAgent
from agents.dining_recommendation.agent import DiningRecommendationAgent
from agents.route_hotel_planning.agent import RouteHotelPlanningAgent
from agents.cost_optimization.agent import CostOptimizationAgent


logger = logging.getLogger(__name__)


class TravelPlanningWorkflow:
    """End-to-end travel planning workflow."""

    def __init__(self):
        """Initialize all agents."""
        self.user_preference_agent = UserPreferenceAgent()
        self.spot_recommendation_agent = SpotRecommendationAgent()
        self.dining_recommendation_agent = DiningRecommendationAgent()
        self.route_hotel_planning_agent = RouteHotelPlanningAgent()
        self.cost_optimization_agent = CostOptimizationAgent()

        self.agents = [
            self.user_preference_agent,
            self.spot_recommendation_agent,
            self.dining_recommendation_agent,
            self.route_hotel_planning_agent,
            self.cost_optimization_agent,
        ]

        logger.info("Travel planning workflow initialized with 5 agents.")

    def run(self, user_input: str) -> PlanningContext:
        """
        Execute the full travel planning workflow.

        Args:
            user_input: raw user input string

        Returns:
            PlanningContext containing the complete planning result
        """
        context = PlanningContext()
        context.metadata['user_input'] = user_input

        logger.info("=" * 50)
        logger.info("Starting travel planning workflow")
        logger.info("=" * 50)

        try:
            logger.info("\n[Step 1] Running User Preference Agent...")
            context = self.user_preference_agent.process(context)
            if not context.travel_profile:
                logger.error("Failed to parse user preferences. Cannot continue.")
                return context
            logger.info(f"Done: {context.travel_profile.destination}")

            logger.info("\n[Step 2] Running Spot Recommendation Agent...")
            context = self.spot_recommendation_agent.process(context)
            if context.spot_list:
                logger.info(f"Done: recommended {context.spot_list.total_count} spots")

            logger.info("\n[Step 3] Running Dining Recommendation Agent...")
            context = self.dining_recommendation_agent.process(context)
            if context.dining_list:
                logger.info(f"Done: recommended {context.dining_list.total_count} restaurants")

            logger.info("\n[Step 4] Running Route & Hotel Planning Agent...")
            context = self.route_hotel_planning_agent.process(context)
            if context.itinerary:
                logger.info(f"Done: generated {len(context.itinerary.days)}-day itinerary")

            logger.info("\n[Step 5] Running Cost Optimization Agent...")
            context = self.cost_optimization_agent.process(context)
            if context.final_handbook:
                logger.info("Done: final handbook generated")

            self._print_summary(context)

        except Exception as e:
            context.add_error(f"Workflow execution failed: {str(e)}")
            logger.error(f"Workflow error: {str(e)}", exc_info=True)

        logger.info("\n" + "=" * 50)
        logger.info("Travel planning workflow complete")
        logger.info("=" * 50)

        return context

    def _print_summary(self, context: PlanningContext) -> None:
        """Print an execution summary."""
        print("\n" + "=" * 60)
        print("Travel Planning Summary")
        print("=" * 60)

        if context.errors:
            print("\nErrors:")
            for error in context.errors:
                print(f"  - {error}")

        if context.warnings:
            print("\nWarnings:")
            for warning in context.warnings:
                print(f"  - {warning}")

        if context.final_handbook:
            handbook = context.final_handbook
            print(f"\nHandbook: {handbook.title}")
            print(f"   - Destination: {handbook.destination}")
            print(f"   - Budget: ${handbook.budget}")
            print(f"   - Total cost: ${handbook.cost_breakdown.total:.2f}")
            print(f"   - Remaining budget: ${handbook.budget_remaining:.2f}")

            if handbook.optimization_recommendations:
                print(f"\nOptimization suggestions ({len(handbook.optimization_recommendations)}):")
                for rec in handbook.optimization_recommendations[:3]:
                    print(f"   - {rec.category}: {rec.suggestion}")
                    print(f"     Potential savings: ${rec.potential_savings:.2f}")

        print("\n" + "=" * 60 + "\n")

    def get_agent_info(self) -> Dict[str, str]:
        """Return name and description for all agents."""
        return {agent.name: agent.description for agent in self.agents}


def main():
    """Example usage."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    workflow = TravelPlanningWorkflow()

    user_input = """
    I want to plan a 5-day trip to Paris.
    Departure date is June 15, 2024, return date is June 20.
    There are 4 of us, total budget is $4000.
    We enjoy exploring historical and cultural sites, and we love food.
    We are all vegetarian.
    We prefer comfortable but not overly luxurious hotels.
    """

    context = workflow.run(user_input)
    return context


if __name__ == "__main__":
    main()
