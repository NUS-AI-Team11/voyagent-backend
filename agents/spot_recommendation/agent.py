"""
Spot Recommendation Agent - recommends attractions based on user preferences.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from models.schemas import SpotList, Spot, TravelProfile, PlanningContext
from agents.spot_recommendation.prompts import (
    SYSTEM_PROMPT,
    SPOT_RECOMMENDATION_PROMPT,
)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency during early setup
    def load_dotenv(*args: Any, **kwargs: Any) -> bool:
        return False

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled by fallback path
    OpenAI = None  # type: ignore[assignment]


class SpotRecommendationAgent(BaseAgent):
    """Agent that recommends attractions based on user travel preferences."""

    def __init__(self):
        super().__init__(
            name="Spot Recommendation Agent",
            description="Recommends attractions matching user travel preferences"
        )
        load_dotenv()
        self.model = (
            os.getenv("SPOT_RECOMMENDATION_MODEL", "").strip()
            or os.getenv("DEEPSEEK_MODEL", "").strip()
            or os.getenv("OPENAI_MODEL", "deepseek-chat").strip()
            or "deepseek-chat"
        )
        self._timeout_seconds = self._safe_float(os.getenv("SPOT_RECOMMENDATION_TIMEOUT", "20"), default=20.0)
        self._max_retries = max(0, int(self._safe_float(os.getenv("SPOT_RECOMMENDATION_MAX_RETRIES", "1"), default=1.0)))
        self._client: Optional["OpenAI"] = None

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
        client = self._get_client()

        if client is not None:
            try:
                return self._recommend_spots_with_openai(client, travel_profile)
            except Exception as exc:
                self.log_execution(
                    f"OpenAI recommendation failed, falling back to local suggestions: {exc}",
                    level="warning",
                )

        return self._fallback_spots(travel_profile)

    def _recommend_spots_with_openai(self, client: "OpenAI", travel_profile: TravelProfile) -> List[Spot]:
        """Call OpenAI-compatible chat completions API and map result into Spot objects."""
        duration_days = (travel_profile.end_date - travel_profile.start_date).days + 1
        prompt = SPOT_RECOMMENDATION_PROMPT.format(
            destination=travel_profile.destination,
            travel_style=travel_profile.travel_style,
            interests=", ".join(travel_profile.interests) or "general sightseeing",
            group_size=travel_profile.group_size,
            duration_days=duration_days,
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"{prompt}\n\n"
                        "Return JSON object only with top-level key 'spots'. "
                        "Each item requires: name, description, location, category, opening_hours, entrance_fee, "
                        "rating, duration_hours, best_season, accessibility_notes."
                    ),
                },
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Model returned empty spot recommendations")
        payload = json.loads(content)
        raw_spots = payload.get("spots", [])

        if not raw_spots:
            raise ValueError("OpenAI returned no spot recommendations")

        return [self._build_spot(item) for item in raw_spots]

    def _get_client(self) -> Optional["OpenAI"]:
        """Create the OpenAI client lazily so tests can run without API dependencies."""
        if self._client is not None:
            return self._client

        api_key = (
            os.getenv("SPOT_RECOMMENDATION_API_KEY", "").strip()
            or os.getenv("DEEPSEEK_API_KEY", "").strip()
            or os.getenv("OPENAI_API_KEY", "").strip()
        )
        base_url = (
            os.getenv("SPOT_RECOMMENDATION_BASE_URL", "").strip()
            or os.getenv("DEEPSEEK_BASE_URL", "").strip()
            or os.getenv("OPENAI_BASE_URL", "").strip()
            or None
        )
        if (
            not api_key
            or api_key == "OPENAI_API_KEY"
            or api_key == "DEEPSEEK_API_KEY"
            or api_key.startswith("REPLACE_WITH_")
            or OpenAI is None
        ):
            return None

        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=self._timeout_seconds,
            max_retries=self._max_retries,
        )
        return self._client

    def _build_spot(self, item: Dict[str, Any]) -> Spot:
        """Normalize one structured model result into the shared Spot schema."""
        return Spot(
            name=str(item.get("name") or "Unnamed attraction"),
            description=str(item.get("description") or "Recommended attraction"),
            location=str(item.get("location") or "Location unavailable"),
            category=str(item.get("category") or "general"),
            opening_hours=self._optional_string(item.get("opening_hours")),
            entrance_fee=self._safe_float(item.get("entrance_fee")),
            rating=self._safe_float(item.get("rating"), default=4.0),
            duration_hours=self._safe_float(item.get("duration_hours"), default=2.0),
            best_season=self._optional_string(item.get("best_season")),
            accessibility_notes=self._optional_string(item.get("accessibility_notes")),
        )

    def _fallback_spots(self, travel_profile: TravelProfile) -> List[Spot]:
        """Provide deterministic recommendations when API access is unavailable."""
        destination = travel_profile.destination.strip() or "the destination"
        interest_text = ", ".join(travel_profile.interests) if travel_profile.interests else "general sightseeing"
        base_spots = [
            {
                "name": f"{destination} Historic Center",
                "description": f"A walkable area that highlights the city's culture and matches interests in {interest_text}.",
                "location": f"Central {destination}",
                "category": "history" if "history" in travel_profile.interests else "culture",
                "opening_hours": "All day",
                "entrance_fee": 0.0,
                "rating": 4.6,
                "duration_hours": 2.0,
                "best_season": "spring or autumn",
                "accessibility_notes": "Mostly accessible, but some streets may be uneven.",
            },
            {
                "name": f"{destination} Signature Museum",
                "description": "A flagship museum or gallery well-suited to first-time visitors.",
                "location": f"Museum District, {destination}",
                "category": "art" if "art" in travel_profile.interests or "museums" in travel_profile.interests else "culture",
                "opening_hours": "10:00 - 18:00",
                "entrance_fee": 18.0,
                "rating": 4.7,
                "duration_hours": 2.5,
                "best_season": "year-round",
                "accessibility_notes": "Indoor venue with accessible entrances.",
            },
            {
                "name": f"{destination} Scenic Park",
                "description": "A relaxed outdoor stop for views, strolling, and a slower-paced break.",
                "location": f"Park Zone, {destination}",
                "category": "nature",
                "opening_hours": "08:00 - 20:00",
                "entrance_fee": 0.0,
                "rating": 4.5,
                "duration_hours": 1.5,
                "best_season": "spring",
                "accessibility_notes": "Paved paths available in main areas.",
            },
        ]

        recommended_count = min(max((travel_profile.end_date - travel_profile.start_date).days + 4, 6), 10)
        spots = [self._build_spot(base_spots[index % len(base_spots)]) for index in range(recommended_count)]

        for index, spot in enumerate(spots, start=1):
            if index > len(base_spots):
                spot.name = f"{spot.name} #{index}"

        return spots

    def _spot_response_schema(self) -> Dict[str, Any]:
        """JSON schema used to keep the model output stable and parseable."""
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "spots": {
                    "type": "array",
                    "minItems": 6,
                    "maxItems": 15,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "location": {"type": "string"},
                            "category": {"type": "string"},
                            "opening_hours": {"type": "string"},
                            "entrance_fee": {"type": "number"},
                            "rating": {"type": "number"},
                            "duration_hours": {"type": "number"},
                            "best_season": {"type": "string"},
                            "accessibility_notes": {"type": "string"},
                        },
                        "required": [
                            "name",
                            "description",
                            "location",
                            "category",
                            "opening_hours",
                            "entrance_fee",
                            "rating",
                            "duration_hours",
                            "best_season",
                            "accessibility_notes",
                        ],
                    },
                }
            },
            "required": ["spots"],
        }

    def _optional_string(self, value: Any) -> Optional[str]:
        """Convert empty-like values to None while preserving useful text."""
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Convert model output to float safely."""
        if value in (None, ""):
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
