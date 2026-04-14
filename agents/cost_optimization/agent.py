"""
Cost Optimization Agent - analyzes and optimizes itinerary costs.
"""

from agents.base_agent import BaseAgent
from models.schemas import (
    Itinerary, FinalHandbook, CostBreakdown, PlanningContext,
    OptimizationRecommendation
)
from agents.cost_optimization.prompts import (
    SYSTEM_PROMPT,
    COST_ANALYSIS_PROMPT,
    OPTIMIZATION_RECOMMENDATION_PROMPT,
    BUDGET_ALLOCATION_PROMPT,
    ALTERNATIVE_ITINERARY_PROMPT,
    FINAL_HANDBOOK_PROMPT
)
from datetime import datetime


class CostOptimizationAgent(BaseAgent):
    """Agent that analyzes and optimizes itinerary costs."""

    def __init__(self):
        super().__init__(
            name="Cost Optimization Agent",
            description="Analyzes itinerary costs and provides optimization suggestions to stay within budget"
        )

    def process(self, context: PlanningContext) -> PlanningContext:
        """
        Analyze costs and generate the final handbook.

        Args:
            context: planning context containing an Itinerary

        Returns:
            context with final_handbook populated
        """
        try:
            if not self.validate_input(context):
                context.add_error("Missing required input")
                return context

            itinerary = context.itinerary
            travel_profile = context.travel_profile

            cost_breakdown = self._analyze_costs(itinerary)

            recommendations = self._generate_recommendations(
                cost_breakdown,
                travel_profile.budget,
                itinerary
            )

            if cost_breakdown.total > travel_profile.budget:
                context.add_warning(
                    f"Total cost {cost_breakdown.total} exceeds budget {travel_profile.budget}"
                )

            final_handbook = FinalHandbook(
                title=f"{travel_profile.destination} Travel Handbook",
                destination=travel_profile.destination,
                itinerary=itinerary,
                cost_breakdown=cost_breakdown,
                budget=travel_profile.budget,
                budget_remaining=travel_profile.budget - cost_breakdown.total,
                optimization_recommendations=recommendations,
                generated_at=datetime.now()
            )

            context.final_handbook = final_handbook
            self.log_execution(f"Cost analysis complete. Total cost: {cost_breakdown.total}")

        except Exception as e:
            context.add_error(f"Cost optimization failed: {str(e)}")
            self.log_execution(f"Error: {str(e)}", level="error")

        return context

    def validate_input(self, context: PlanningContext) -> bool:
        """Validate required input."""
        return (
            context.itinerary is not None and
            context.travel_profile is not None
        )

    def _analyze_costs(self, itinerary: Itinerary) -> CostBreakdown:
        """
        Analyze the cost structure of the itinerary.

        Args:
            itinerary: full itinerary

        Returns:
            CostBreakdown object

        TODO:
            Replace the mock data below with real cost analysis.
            Steps:
              1. Loop through itinerary.days
              2. For each day, read activity costs from day.activities (each dict has a "cost" key)
              3. Read accommodation cost from day.accommodation["cost_per_night"] if present
              4. Optionally call LLM with COST_ANALYSIS_PROMPT for a more detailed breakdown
              5. Sum up by category and populate a real CostBreakdown object

            CostBreakdown fields: accommodation, transportation, dining,
            attractions, shopping, miscellaneous, contingency (all floats).
            cost_breakdown.total is computed automatically as the sum of all fields.
        """
        # ---------------------------------------------------------------------------
        # MOCK DATA — placeholder costs so the pipeline produces a non-empty handbook.
        # Delete this block and replace it with real cost aggregation logic when you
        # implement the real agent logic.
        # ---------------------------------------------------------------------------
        cost_breakdown = CostBreakdown(
            accommodation=700.0,
            transportation=200.0,
            dining=420.0,
            attractions=150.0,
            shopping=200.0,
            miscellaneous=80.0,
            contingency=100.0,
        )
        # ---------------------------------------------------------------------------
        return cost_breakdown

    def _generate_recommendations(
        self,
        cost_breakdown: CostBreakdown,
        budget: float,
        itinerary: Itinerary
    ) -> list:
        """
        Generate optimization recommendations based on cost analysis.

        Args:
            cost_breakdown: cost breakdown
            budget: user budget
            itinerary: full itinerary

        Returns:
            list of OptimizationRecommendation objects
        """
        recommendations = []

        overage = cost_breakdown.total - budget

        if overage > 0:
            recommend = OptimizationRecommendation(
                category="accommodation",
                suggestion="Consider downgrading hotel tier",
                potential_savings=overage * 0.3,
                confidence=0.7
            )
            recommendations.append(recommend)

        return recommendations
