"""
Cost Optimization Agent - analyzes and optimizes itinerary costs.
"""

import json
import os
from openai import OpenAI
from agents.base_agent import BaseAgent
from models.schemas import (
    Itinerary, FinalHandbook, CostBreakdown, PlanningContext,
    OptimizationRecommendation, TravelProfile
)
from agents.cost_optimization.prompts import (
    SYSTEM_PROMPT,
    OPTIMIZATION_RECOMMENDATION_PROMPT,
)
from datetime import datetime


class CostOptimizationAgent(BaseAgent):
    """Agent that analyzes and optimizes itinerary costs."""

    def __init__(self):
        super().__init__(
            name="Cost Optimization Agent",
            description="Analyzes itinerary costs and provides optimization suggestions to stay within budget"
        )
        # Lazy init: do not require OPENAI_API_KEY when this agent is only inspected
        # (e.g. metadata endpoints that list workflow steps/agents).
        self._client = None

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
                travel_profile
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

    # Mapping from activity category strings to CostBreakdown field names.
    _CATEGORY_MAP = {
        "dining": "dining",
        "food": "dining",
        "restaurant": "dining",
        "meal": "dining",
        "transport": "transportation",
        "transportation": "transportation",
        "transit": "transportation",
        "attraction": "attractions",
        "attractions": "attractions",
        "sightseeing": "attractions",
        "culture": "attractions",
        "nature": "attractions",
        "history": "attractions",
        "shopping": "shopping",
        "accommodation": "accommodation",
        "hotel": "accommodation",
    }

    # Compression rate per category: how much of that spend can realistically be cut.
    _COMPRESSION_RATES = {
        "accommodation": 0.30,
        "dining": 0.20,
        "shopping": 0.40,
        "attractions": 0.15,
        "transportation": 0.20,
        "miscellaneous": 0.50,
    }

    def _analyze_costs(self, itinerary: Itinerary) -> CostBreakdown:
        """
        Analyze the cost structure of the itinerary.

        Iterates over every day, maps each activity's category to a
        CostBreakdown field, and accumulates accommodation from
        day.accommodation["cost_per_night"].  Uncategorised costs fall
        into miscellaneous.  A 5 % contingency is added on top.

        Args:
            itinerary: full itinerary

        Returns:
            CostBreakdown object with real accumulated costs
        """
        totals = {
            "accommodation": 0.0,
            "transportation": 0.0,
            "dining": 0.0,
            "attractions": 0.0,
            "shopping": 0.0,
            "miscellaneous": 0.0,
        }

        for day in itinerary.days:
            # Accommodation cost for the night
            if day.accommodation:
                cost_per_night = day.accommodation.get("cost_per_night", 0.0)
                totals["accommodation"] += float(cost_per_night or 0.0)

            # Activity costs — map category → bucket
            for activity in day.activities:
                cost = float(activity.get("cost", 0.0) or 0.0)
                if cost == 0.0:
                    continue
                raw_category = str(activity.get("category", "")).lower().strip()
                bucket = self._CATEGORY_MAP.get(raw_category, "miscellaneous")
                totals[bucket] += cost

        subtotal = sum(totals.values())
        contingency = round(subtotal * 0.05, 2)

        return CostBreakdown(
            accommodation=round(totals["accommodation"], 2),
            transportation=round(totals["transportation"], 2),
            dining=round(totals["dining"], 2),
            attractions=round(totals["attractions"], 2),
            shopping=round(totals["shopping"], 2),
            miscellaneous=round(totals["miscellaneous"], 2),
            contingency=contingency,
        )

    def _generate_recommendations(
        self,
        cost_breakdown: CostBreakdown,
        budget: float,
        travel_profile: TravelProfile
    ) -> list:
        """
        Generate optimization recommendations based on cost analysis.

        Rules compute potential_savings; LLM generates the suggestion text.
        Returns up to 3 recommendations sorted by potential_savings descending.

        Args:
            cost_breakdown: computed cost breakdown
            budget: user's total budget
            travel_profile: user travel profile (destination, travel_style, etc.)

        Returns:
            list of OptimizationRecommendation objects
        """
        if cost_breakdown.total <= budget:
            return []

        # Build candidates: one per category with non-zero spend
        candidates = []
        for category, rate in self._COMPRESSION_RATES.items():
            amount = getattr(cost_breakdown, category, 0.0)
            if amount <= 0:
                continue
            candidates.append({
                "category": category,
                "amount": amount,
                "potential_savings": round(amount * rate, 2),
                "confidence": round(rate, 2),
            })

        # Keep top 3 by potential_savings before calling LLM
        candidates.sort(key=lambda c: c["potential_savings"], reverse=True)
        top = candidates[:3]

        suggestions = self._fetch_suggestions(top, cost_breakdown, budget, travel_profile)

        return [
            OptimizationRecommendation(
                category=c["category"],
                suggestion=suggestions.get(c["category"], f"Reduce {c['category']} spending"),
                potential_savings=c["potential_savings"],
                confidence=c["confidence"],
            )
            for c in top
        ]

    def _fetch_suggestions(
        self,
        candidates: list,
        cost_breakdown: CostBreakdown,
        budget: float,
        travel_profile: TravelProfile
    ) -> dict:
        """
        Call OpenAI to generate destination-specific suggestion text.

        Returns a dict mapping category → suggestion string.
        Falls back to generic text on any error.
        """
        category_lines = "\n".join(
            f"- {c['category']}: ${c['amount']:.2f} spend, save ~${c['potential_savings']:.2f}"
            for c in candidates
        )

        user_prompt = OPTIMIZATION_RECOMMENDATION_PROMPT.format(
            destination=travel_profile.destination,
            travel_style=travel_profile.travel_style,
            budget=budget,
            total_cost=cost_breakdown.total,
            overage=round(cost_breakdown.total - budget, 2),
            category_lines=category_lines,
        )

        try:
            client = self._get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.4,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
            # LLM returns {"suggestions": [...]} or a bare array — handle both
            parsed = json.loads(raw)
            items = parsed if isinstance(parsed, list) else parsed.get("suggestions", parsed.get("items", []))
            return {item["category"]: item["suggestion"] for item in items if "category" in item}
        except Exception as e:
            self.log_execution(f"LLM suggestion fetch failed: {e}", level="warning")
            return {}

    def _get_openai_client(self) -> OpenAI:
        """Build OpenAI client only when LLM suggestions are actually requested."""
        if self._client is not None:
            return self._client
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        self._client = OpenAI(api_key=api_key)
        return self._client
