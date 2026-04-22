"""
Dining Recommendation Agent - recommends restaurants and dining options.
"""

import json
import logging
import os
from datetime import datetime
from typing import List, Optional, Any, Dict

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - fallback path is tested via mocks
    OpenAI = None  # type: ignore[assignment]

from agents.base_agent import BaseAgent
from agents.dining_recommendation.prompts import (
    DINING_RECOMMENDATION_PROMPT,
    SYSTEM_PROMPT,
)
from models.schemas import DiningList, PlanningContext, Restaurant, TravelProfile

logger = logging.getLogger(__name__)


class DiningRecommendationAgent(BaseAgent):
    """Agent that recommends dining options based on user preferences."""

    def __init__(self):
        super().__init__(
            name="Dining Recommendation Agent",
            description="Recommends restaurants and dining options matching user dietary preferences and budget"
        )
        self._client: Optional["OpenAI"] = None
        self._model = self._get_deepseek_model()

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
                    "destination": travel_profile.destination,
                    "dietary_restrictions": travel_profile.dietary_restrictions,
                    "budget": travel_profile.budget,
                },
                total_count=len(restaurants),
                generated_at=datetime.now(),
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
        try:
            return self._recommend_restaurants_llm(travel_profile)
        except Exception as e:
            logger.warning(f"LLM call failed: {e}, falling back to mock data")

        return self._recommend_restaurants_mock(travel_profile)

    def _recommend_restaurants_llm(self, travel_profile: TravelProfile) -> List[Restaurant]:
        """
        Use an OpenAI-compatible LLM endpoint to recommend restaurants.

        Args:
            travel_profile: user travel information

        Returns:
            list of recommended Restaurant objects
        """
        client = self._create_deepseek_client()
        model = self._model

        start_date = travel_profile.start_date
        end_date = travel_profile.end_date
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        duration_days = (end_date - start_date).days + 1 if start_date and end_date else 7

        user_prompt = DINING_RECOMMENDATION_PROMPT.format(
            destination=travel_profile.destination,
            travel_style=travel_profile.travel_style or "general",
            budget=travel_profile.budget,
            group_size=travel_profile.group_size,
            duration_days=duration_days,
            dietary_restrictions=", ".join(travel_profile.dietary_restrictions) or "none",
        )

        response = self._chat_json(
            client=client,
            model=model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=3000,
        )

        restaurants = []
        restaurant_list = response.get("restaurants", response if isinstance(response, list) else [])

        for r in restaurant_list:
            restaurants.append(
                Restaurant(
                    name=r.get("name", ""),
                    cuisine_type=r.get("cuisine_type", r.get("cuisine", "")),
                    location=r.get("address", r.get("location", "")),
                    price_range=r.get("price_range", "$$"),
                    rating=r.get("rating", 4.0),
                    average_cost_per_person=r.get("average_cost_per_person", 0),
                    opening_hours=r.get("opening_hours", ""),
                    reservations_needed=r.get("reservations_needed", False),
                    accessibility_notes=r.get("special_notes"),
                )
            )

        if not restaurants:
            raise ValueError("LLM returned no restaurant recommendations")

        logger.info("LLM returned %s restaurant recommendations", len(restaurants))
        return restaurants

    def _create_deepseek_client(self) -> OpenAI:
        """
        Backward-compatible name: create an OpenAI-compatible client.
        Resolution order:
        1) DINING_OPENAI_API_KEY
        2) OPENAI_API_KEY
        3) DEEPSEEK_API_KEY
        """
        if self._client is not None:
            return self._client

        if OpenAI is None:
            raise ValueError("openai package is not installed")

        api_key, key_source = self._resolve_api_key()
        if not api_key:
            raise ValueError("No API key configured for dining agent")

        base_url = self._resolve_base_url(key_source)
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        return self._client

    def _get_deepseek_model(self) -> str:
        """
        Backward-compatible name: get configured model for dining agent.
        Resolution order:
        1) DINING_OPENAI_MODEL
        2) OPENAI_MODEL
        3) DEEPSEEK_MODEL
        """
        model = (
            os.getenv("DINING_OPENAI_MODEL", "").strip()
            or os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
            or os.getenv("OPENAI_MODEL", "").strip()
        )
        aliases = {
            "DeepSeek-V3.2": "deepseek-chat",
            "deepseek-v3.2": "deepseek-chat",
        }
        return aliases.get(model, model or "deepseek-chat")

    def _resolve_api_key(self) -> tuple[str, str]:
        """Resolve key and key source label for endpoint routing."""
        candidates = [
            ("DINING_OPENAI_API_KEY", os.getenv("DINING_OPENAI_API_KEY", "").strip()),
            ("DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_API_KEY", "").strip()),
            ("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", "").strip()),
        ]
        for source, key in candidates:
            if key and key not in {"OPENAI_API_KEY", "DEEPSEEK_API_KEY"} and not key.startswith("REPLACE_WITH_"):
                return key, source
        return "", ""

    def _resolve_base_url(self, key_source: str) -> Optional[str]:
        """Choose the appropriate base URL for the selected provider."""
        # Highest priority: explicit dining-specific endpoint, then generic OpenAI-compatible endpoint.
        explicit = (
            os.getenv("DINING_OPENAI_BASE_URL", "").strip()
            or os.getenv("OPENAI_BASE_URL", "").strip()
        )
        if explicit:
            return explicit
        if key_source == "DEEPSEEK_API_KEY":
            return os.getenv("DEEPSEEK_BASE_URL", "").strip() or "https://api.deepseek.com"
        # None means official OpenAI endpoint from SDK default.
        return None

    def _chat_json(
        self,
        client: OpenAI,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 3000,
    ) -> dict:
        """Call DeepSeek and parse its JSON response."""
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM returned empty content")

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse JSON response: %s", exc)
            raise

    def _recommend_restaurants_mock(self, travel_profile: TravelProfile) -> List[Restaurant]:
        """
        Mock implementation for restaurant recommendations.

        Args:
            travel_profile: user travel information

        Returns:
            list of recommended Restaurant objects
        """
        all_restaurants = self._get_restaurant_database(travel_profile.destination)
        filtered = self._filter_by_dietary_restrictions(all_restaurants, travel_profile.dietary_restrictions)
        filtered = self._filter_by_budget(filtered, travel_profile.budget, travel_profile.group_size)
        filtered = self._prioritize_by_travel_style(filtered, travel_profile.travel_style)
        return filtered[:15]

    def _get_restaurant_database(self, destination: str) -> List[Restaurant]:
        """
        Get a comprehensive restaurant database for the destination.
        This serves as a mock LLM response and can be replaced with real LLM call later.
        """
        restaurants_db = {
            "Tokyo": [
                Restaurant(
                    name="Ichiran Ramen Shibuya",
                    cuisine_type="Japanese Ramen",
                    location="Dogenzaka, Shibuya City, Tokyo",
                    price_range="$",
                    rating=4.5,
                    average_cost_per_person=12.0,
                    opening_hours="10:00 - 02:00",
                    reservations_needed=False,
                ),
                Restaurant(
                    name="Tsukiji Outer Market",
                    cuisine_type="Seafood / Street Food",
                    location="Tsukiji, Chuo City, Tokyo",
                    price_range="$$",
                    rating=4.6,
                    average_cost_per_person=25.0,
                    opening_hours="05:00 - 14:00",
                    reservations_needed=False,
                ),
                Restaurant(
                    name="Sukiyabashi Jiro",
                    cuisine_type="High-end Sushi",
                    location="Ginza, Chuo City, Tokyo",
                    price_range="$$$$",
                    rating=4.9,
                    average_cost_per_person=320.0,
                    opening_hours="11:30 - 14:00, 17:00 - 20:30",
                    reservations_needed=True,
                ),
                Restaurant(
                    name="Gonpachi Nishi-Azabu",
                    cuisine_type="Japanese Izakaya",
                    location="Minato City, Tokyo",
                    price_range="$$",
                    rating=4.4,
                    average_cost_per_person=35.0,
                    opening_hours="17:00 - 23:00",
                    reservations_needed=True,
                ),
                Restaurant(
                    name="Nabezo Shibuya",
                    cuisine_type="Hot Pot (Sukiyaki/Shabu)",
                    location="Shibuya City, Tokyo",
                    price_range="$$$",
                    rating=4.3,
                    average_cost_per_person=60.0,
                    opening_hours="11:00 - 23:00",
                    reservations_needed=False,
                ),
                Restaurant(
                    name="Ippudo Ramen",
                    cuisine_type="Tonkotsu Ramen",
                    location="Shinjuku City, Tokyo",
                    price_range="$",
                    rating=4.2,
                    average_cost_per_person=10.0,
                    opening_hours="11:00 - 23:00",
                    reservations_needed=False,
                ),
                Restaurant(
                    name="Kikunoi",
                    cuisine_type="Kaiseki (Japanese Fine Dining)",
                    location="Ginza, Chuo City, Tokyo",
                    price_range="$$$$",
                    rating=4.8,
                    average_cost_per_person=250.0,
                    opening_hours="12:00 - 14:00, 17:00 - 20:00",
                    reservations_needed=True,
                ),
                Restaurant(
                    name="Matsuya Beef Bowl",
                    cuisine_type="Japanese Comfort Food",
                    location="Multiple locations",
                    price_range="$",
                    rating=3.8,
                    average_cost_per_person=8.0,
                    opening_hours="24 hours",
                    reservations_needed=False,
                ),
                Restaurant(
                    name="Okonomiyaki Kiji",
                    cuisine_type="Japanese Savory Pancake",
                    location="Shinjuku City, Tokyo",
                    price_range="$$",
                    rating=4.3,
                    average_cost_per_person=15.0,
                    opening_hours="11:00 - 20:00",
                    reservations_needed=False,
                ),
                Restaurant(
                    name="Gaia",
                    cuisine_type="Italian",
                    location="Shibuya City, Tokyo",
                    price_range="$$$",
                    rating=4.5,
                    average_cost_per_person=45.0,
                    opening_hours="11:30 - 15:00, 17:30 - 23:00",
                    reservations_needed=True,
                ),
                Restaurant(
                    name="New York Grill & Bar",
                    cuisine_type="Western Steak",
                    location="Shinjuku City, Tokyo",
                    price_range="$$$",
                    rating=4.4,
                    average_cost_per_person=80.0,
                    opening_hours="11:30 - 23:00",
                    reservations_needed=True,
                ),
                Restaurant(
                    name="Vegetarian Jiro",
                    cuisine_type="Vegetarian Japanese",
                    location="Harajuku City, Tokyo",
                    price_range="$$",
                    rating=4.1,
                    average_cost_per_person=30.0,
                    opening_hours="11:00 - 21:00",
                    reservations_needed=False,
                ),
                Restaurant(
                    name="Ramen Yokocho",
                    cuisine_type="Japanese Ramen Alley",
                    location="Yurakucho, Chiyoda City, Tokyo",
                    price_range="$",
                    rating=4.0,
                    average_cost_per_person=11.0,
                    opening_hours="10:00 - 23:00",
                    reservations_needed=False,
                ),
                Restaurant(
                    name="Kanda Yabu Soba",
                    cuisine_type="Traditional Soba",
                    location="Chiyoda City, Tokyo",
                    price_range="$$",
                    rating=4.4,
                    average_cost_per_person=18.0,
                    opening_hours="10:00 - 18:00 (Closed Sundays)",
                    reservations_needed=False,
                ),
                Restaurant(
                    name="Hanamaru Udon",
                    cuisine_type="Japanese Udon",
                    location="Multiple locations",
                    price_range="$",
                    rating=3.9,
                    average_cost_per_person=9.0,
                    opening_hours="10:00 - 21:00",
                    reservations_needed=False,
                ),
            ]
        }

        if destination in restaurants_db:
            return restaurants_db[destination]
        return self._build_destination_fallback_restaurants(destination)

    def _build_destination_fallback_restaurants(self, destination: str) -> List[Restaurant]:
        """Generate destination-consistent fallback restaurants when no city dataset exists."""
        city = destination.strip() or "the destination"
        templates: List[Dict[str, Any]] = [
            {"name": f"{city} Hawker Center", "cuisine": "Local Street Food", "price": "$", "cost": 12.0, "rating": 4.4},
            {"name": f"{city} Heritage Kitchen", "cuisine": "Traditional Cuisine", "price": "$$", "cost": 28.0, "rating": 4.5},
            {"name": f"{city} Riverside Grill", "cuisine": "Grill & Seafood", "price": "$$$", "cost": 55.0, "rating": 4.3},
            {"name": f"{city} Vegetarian Table", "cuisine": "Vegetarian / Vegan", "price": "$$", "cost": 24.0, "rating": 4.2},
            {"name": f"{city} Night Market Bites", "cuisine": "Night Market Local Bites", "price": "$", "cost": 10.0, "rating": 4.1},
            {"name": f"{city} Signature Tasting", "cuisine": "Fine Dining", "price": "$$$$", "cost": 120.0, "rating": 4.6},
        ]
        restaurants: List[Restaurant] = []
        for idx, t in enumerate(templates, start=1):
            restaurants.append(
                Restaurant(
                    name=t["name"],
                    cuisine_type=t["cuisine"],
                    location=f"District {idx}, {city}",
                    price_range=t["price"],
                    rating=float(t["rating"]),
                    average_cost_per_person=float(t["cost"]),
                    opening_hours="10:00 - 22:00",
                    reservations_needed=t["price"] in {"$$$", "$$$$"},
                )
            )
        return restaurants

    def _filter_by_dietary_restrictions(self, restaurants: List[Restaurant], restrictions: List[str]) -> List[Restaurant]:
        """Filter restaurants based on dietary restrictions."""
        if not restrictions:
            return restaurants

        restriction_keywords = {
            "vegetarian": ["vegetarian", "vegan", "soba", "udon", "tempura", "tofu"],
            "vegan": ["vegetarian", "vegan"],
            "gluten_free": ["sushi", "seafood", "meat"],
            "halal": ["lamb", "chicken", "beef"],
            "kosher": [],
        }

        filtered = []
        for restaurant in restaurants:
            cuisine_lower = restaurant.cuisine_type.lower()
            is_suitable = False

            for restriction in restrictions:
                keywords = restriction_keywords.get(restriction.lower(), [])
                if keywords and any(kw in cuisine_lower for kw in keywords):
                    is_suitable = True
                    break

            if is_suitable:
                filtered.append(restaurant)

        return filtered if filtered else restaurants

    def _filter_by_budget(self, restaurants: List[Restaurant], budget: float, group_size: int) -> List[Restaurant]:
        """Filter restaurants based on budget per person."""
        if budget <= 0:
            return restaurants

        budget_per_person = budget / max(group_size, 1) / 3
        price_ranges = {
            "$": (0, 20),
            "$$": (20, 50),
            "$$$": (50, 150),
            "$$$$": (150, float("inf")),
        }

        filtered = []
        for restaurant in restaurants:
            min_cost, max_cost = price_ranges.get(restaurant.price_range, (0, float("inf")))
            avg_cost = restaurant.average_cost_per_person or (min_cost + max_cost) / 2
            if avg_cost <= budget_per_person * 1.2:
                filtered.append(restaurant)

        return filtered if filtered else restaurants

    def _prioritize_by_travel_style(self, restaurants: List[Restaurant], travel_style: str) -> List[Restaurant]:
        """Prioritize restaurants based on travel style."""
        if not travel_style:
            return restaurants

        travel_style_lower = travel_style.lower()
        style_priorities = {
            "food": ["sushi", "ramen", "kaiseki", "tempura", "soba", "udon", "izakaya"],
            "luxury": ["$$$$", "fine dining", "kaiseki", "michelin"],
            "budget": ["$", "street food", "market", "ramen"],
            "culture": ["traditional", "soba", "udon", "izakaya", "kaiseki"],
            "adventure": ["street food", "market", "alley", "local"],
            "relaxation": ["$$", "cozy", "izakaya"],
            "shopping": ["$$", "$$$"],
        }

        priority_keywords = style_priorities.get(travel_style_lower, [])
        if not priority_keywords:
            return restaurants

        def relevance_score(restaurant: Restaurant) -> int:
            combined = f"{restaurant.cuisine_type.lower()} {restaurant.name.lower()}"
            score = 0
            for keyword in priority_keywords:
                if keyword in combined:
                    score += 1
            score += restaurant.rating / 10
            return -score

        return sorted(restaurants, key=relevance_score)
