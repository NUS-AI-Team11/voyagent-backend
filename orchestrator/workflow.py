"""
Agent orchestrator - main business logic for the planning pipeline.
"""

import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from models.schemas import PlanningContext
from agents.user_preference.agent import UserPreferenceAgent
from agents.spot_recommendation.agent import SpotRecommendationAgent
from agents.dining_recommendation.agent import DiningRecommendationAgent
from agents.route_hotel_planning.agent import RouteHotelPlanningAgent
from agents.cost_optimization.agent import CostOptimizationAgent


logger = logging.getLogger(__name__)


class TravelPlanningWorkflow:
    """End-to-end travel planning workflow."""

    def __init__(self, fail_fast: bool = True, print_summary: bool = True):
        """Initialize all agents."""
        self.user_preference_agent = UserPreferenceAgent()
        self.spot_recommendation_agent = SpotRecommendationAgent()
        self.dining_recommendation_agent = DiningRecommendationAgent()
        self.route_hotel_planning_agent = RouteHotelPlanningAgent()
        self.cost_optimization_agent = CostOptimizationAgent()
        self.fail_fast = fail_fast
        self.print_summary = print_summary

        self.agents = [
            self.user_preference_agent,
            self.spot_recommendation_agent,
            self.dining_recommendation_agent,
            self.route_hotel_planning_agent,
            self.cost_optimization_agent,
        ]

        self.steps: List[Tuple[str, Any, str, bool]] = [
            ("User Preference", self.user_preference_agent, "travel_profile", True),
            ("Spot Recommendation", self.spot_recommendation_agent, "spot_list", True),
            ("Dining Recommendation", self.dining_recommendation_agent, "dining_list", True),
            ("Route & Hotel Planning", self.route_hotel_planning_agent, "itinerary", True),
            ("Cost Optimization", self.cost_optimization_agent, "final_handbook", True),
        ]

        logger.info("Travel planning workflow initialized with 5 agents.")

    def run(
        self,
        user_input: str,
        *,
        before_step: Optional[Callable[[int, str, str, PlanningContext], None]] = None,
        after_step: Optional[Callable[[int, str, str, PlanningContext], None]] = None,
    ) -> PlanningContext:
        """
        Execute the full travel planning workflow.

        Args:
            user_input: raw user input string
            before_step: optional hook called before each agent step (1-based index, label, output_field, context).
            after_step: optional hook called after each agent step completes.

        Returns:
            PlanningContext containing the complete planning result
        """
        workflow_start = time.perf_counter()
        context = PlanningContext()
        context.metadata["user_input"] = user_input
        context.metadata["workflow_started_at"] = datetime.now().isoformat()
        context.metadata["workflow_steps"] = []

        logger.info("=" * 50)
        logger.info("Starting travel planning workflow")
        logger.info("=" * 50)

        try:
            for index, (label, agent, output_field, required) in enumerate(self.steps, start=1):
                if self.fail_fast and context.errors:
                    logger.error("Stopping workflow due to previous errors.")
                    break

                logger.info(f"\n[Step {index}] Running {label} Agent...")
                if before_step:
                    before_step(index, label, output_field, context)
                context = self._run_step(context, agent, output_field, required)
                if after_step:
                    after_step(index, label, output_field, context)

        except Exception as e:
            context.add_error(f"Workflow execution failed: {str(e)}")
            logger.error(f"Workflow error: {str(e)}", exc_info=True)

        elapsed_ms = round((time.perf_counter() - workflow_start) * 1000, 2)
        context.metadata["workflow_elapsed_ms"] = elapsed_ms
        context.metadata["workflow_finished_at"] = datetime.now().isoformat()

        logger.info("\n" + "=" * 50)
        logger.info("Travel planning workflow complete")
        logger.info(f"Elapsed time: {elapsed_ms} ms")
        logger.info("=" * 50)

        if self.print_summary:
            self._print_summary(context)

        return context

    def _run_step(self, context: PlanningContext, agent: Any, output_field: str, required: bool) -> PlanningContext:
        """Execute one workflow step and validate its expected output."""
        prev_error_count = len(context.errors)

        if hasattr(agent, "execute"):
            context = agent.execute(context)
        else:
            context = agent.process(context)

        step_result = {
            "agent": agent.name,
            "output_field": output_field,
            "has_output": getattr(context, output_field) is not None,
            "new_errors": len(context.errors) - prev_error_count,
        }
        context.metadata["workflow_steps"].append(step_result)

        if required and getattr(context, output_field) is None:
            msg = f"{agent.name}: expected output '{output_field}' is missing"
            context.add_error(msg)
            logger.error(msg)
            return context

        if step_result["new_errors"] > 0:
            logger.error(
                "%s completed with %s new error(s)",
                agent.name,
                step_result["new_errors"],
            )
        else:
            logger.info("Done: %s", agent.name)

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

        if context.metadata.get("workflow_elapsed_ms") is not None:
            print(f"\nWorkflow elapsed: {context.metadata['workflow_elapsed_ms']} ms")

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
