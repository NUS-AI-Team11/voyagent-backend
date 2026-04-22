"""
Spot Recommendation Agent - recommends attractions based on user preferences.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from agents.llm_quality import run_with_quality_gate
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
        self._timeout_seconds = self._safe_float(os.getenv("SPOT_RECOMMENDATION_TIMEOUT", "45"), default=45.0)
        self._max_retries = max(0, int(self._safe_float(os.getenv("SPOT_RECOMMENDATION_MAX_RETRIES", "2"), default=2.0)))
        self._max_attempts = max(1, int(self._safe_float(os.getenv("SPOT_RECOMMENDATION_MAX_ATTEMPTS", "2"), default=2.0)))
        self._client: Optional["OpenAI"] = None
        self._provider_name = "LLM"

    def process(self, context: PlanningContext) -> PlanningContext:
        """
        Process user preferences and generate a spot recommendation list.

        Args:
            context: planning context containing a TravelProfile

        Returns:
            context with spot_list populated
        """
        try:
            self.log_execution("Starting spot recommendation")
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
                return self._recommend_spots_with_llm(client, travel_profile)
            except Exception as exc:
                self.log_execution(
                    f"{self._provider_name} recommendation failed, falling back to local suggestions: {exc}",
                    level="warning",
                )

        return self._fallback_spots(travel_profile)

    def _recommend_spots_with_llm(self, client: "OpenAI", travel_profile: TravelProfile) -> List[Spot]:
        """Call OpenAI-compatible chat completions API and map result into Spot objects."""
        duration_days = (travel_profile.end_date - travel_profile.start_date).days + 1
        prompt = SPOT_RECOMMENDATION_PROMPT.format(
            destination=travel_profile.destination,
            travel_style=travel_profile.travel_style,
            interests=", ".join(travel_profile.interests) or "general sightseeing",
            group_size=travel_profile.group_size,
            duration_days=duration_days,
        )

        def _generate(feedback: Optional[str]) -> Dict[str, Any]:
            user_content = (
                f"{prompt}\n\n"
                "Return JSON object only with top-level key 'spots'. "
                "Each item requires: name, description, location, category, opening_hours, entrance_fee, "
                "rating, duration_hours, best_season, accessibility_notes."
            )
            if feedback:
                user_content = f"{user_content}\n\n{feedback}"
            content = self._call_model_for_json_content(client, user_content)
            if not content:
                raise ValueError("Model returned empty spot recommendations")
            payload = self._parse_json_content(content)
            if not isinstance(payload, dict):
                raise ValueError("Spot payload is not an object")
            return payload

        def _validate(payload: Dict[str, Any]) -> tuple[bool, str]:
            raw_spots = payload.get("spots", [])
            if not isinstance(raw_spots, list) or len(raw_spots) < 3:
                return False, "need at least 3 spots"
            names = {str(item.get("name") or "").strip().lower() for item in raw_spots if isinstance(item, dict)}
            if len(names) < min(3, len(raw_spots)):
                return False, "spot names are too repetitive"
            return True, "ok"

        payload, report = run_with_quality_gate(
            max_attempts=self._max_attempts,
            generate=_generate,
            validate=_validate,
        )
        self._last_quality_report = {"stage": "spot_recommendation", **report}
        self.log_execution(
            f"spot_quality attempts={report['attempts']} passed={report['passed']} reason={report['final_reason']}",
            level="info",
        )
        raw_spots = payload.get("spots", [])
        return [self._build_spot(item) for item in raw_spots if isinstance(item, dict)]

    # Backward-compatible alias for tests/scripts that may still import old name.
    def _recommend_spots_with_openai(self, client: "OpenAI", travel_profile: TravelProfile) -> List[Spot]:
        return self._recommend_spots_with_llm(client, travel_profile)

    def _get_client(self) -> Optional["OpenAI"]:
        """Create the OpenAI client lazily so tests can run without API dependencies."""
        if self._client is not None:
            return self._client

        # DeepSeek-first priority as requested.
        deepseek_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        spot_key = os.getenv("SPOT_RECOMMENDATION_API_KEY", "").strip()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        api_key = deepseek_key or spot_key or openai_key

        deepseek_base = os.getenv("DEEPSEEK_BASE_URL", "").strip()
        spot_base = os.getenv("SPOT_RECOMMENDATION_BASE_URL", "").strip()
        openai_base = os.getenv("OPENAI_BASE_URL", "").strip()
        base_url = deepseek_base or spot_base or openai_base or None

        if (
            not api_key
            or api_key == "OPENAI_API_KEY"
            or api_key == "DEEPSEEK_API_KEY"
            or api_key.startswith("REPLACE_WITH_")
            or OpenAI is None
        ):
            return None

        if deepseek_key and api_key == deepseek_key:
            self._provider_name = "DeepSeek"
        elif base_url and "deepseek" in base_url.lower():
            self._provider_name = "DeepSeek"
        else:
            self._provider_name = "OpenAI-compatible"

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
            {
                "name": f"{destination} Riverfront Promenade",
                "description": "A waterfront walking route with skyline views and evening ambience.",
                "location": f"Riverside, {destination}",
                "category": "scenic",
                "opening_hours": "All day",
                "entrance_fee": 0.0,
                "rating": 4.4,
                "duration_hours": 1.5,
                "best_season": "year-round",
                "accessibility_notes": "Mostly flat and wheelchair friendly.",
            },
            {
                "name": f"{destination} Cultural Quarter",
                "description": "A compact district with galleries, performance spaces, and local crafts.",
                "location": f"Cultural District, {destination}",
                "category": "culture",
                "opening_hours": "10:00 - 20:00",
                "entrance_fee": 10.0,
                "rating": 4.5,
                "duration_hours": 2.0,
                "best_season": "autumn",
                "accessibility_notes": "Accessible sidewalks and public facilities.",
            },
            {
                "name": f"{destination} Botanical Garden",
                "description": "A peaceful garden area ideal for slow-paced nature exploration.",
                "location": f"Garden Zone, {destination}",
                "category": "nature",
                "opening_hours": "08:00 - 18:00",
                "entrance_fee": 8.0,
                "rating": 4.6,
                "duration_hours": 2.0,
                "best_season": "spring",
                "accessibility_notes": "Main paths are paved and accessible.",
            },
            {
                "name": f"{destination} Local Market Street",
                "description": "A lively market strip for local snacks, crafts, and neighborhood vibe.",
                "location": f"Market Street, {destination}",
                "category": "local_life",
                "opening_hours": "09:00 - 22:00",
                "entrance_fee": 0.0,
                "rating": 4.3,
                "duration_hours": 1.5,
                "best_season": "year-round",
                "accessibility_notes": "Can be crowded during peak evening hours.",
            },
        ]

        recommended_count = min(max((travel_profile.end_date - travel_profile.start_date).days + 3, 6), len(base_spots))
        return [self._build_spot(base_spots[index]) for index in range(recommended_count)]

    def _call_model_for_json_content(self, client: "OpenAI", user_content: str) -> str:
        """
        Call model and return text content; prefer JSON mode but gracefully degrade
        when provider compatibility is partial.
        """
        is_deepseek = self._provider_name.lower().startswith("deepseek")
        # DeepSeek compatibility is generally better without response_format=json_object.
        if is_deepseek:
            self.log_execution("Spot LLM call mode=plain_json provider=DeepSeek", level="info")
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content + "\n\nReturn valid JSON only. No markdown."},
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            return response.choices[0].message.content or ""

        try:
            self.log_execution("Spot LLM call mode=json_object provider=openai_compatible", level="info")
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or ""
        except Exception:
            self.log_execution("Spot LLM call fallback mode=plain_json", level="warning")
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content + "\n\nReturn valid JSON only. No markdown."},
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            return response.choices[0].message.content or ""

    def _parse_json_content(self, content: str) -> Any:
        """Parse JSON response, tolerating markdown code fences."""
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start_obj = text.find("{")
            end_obj = text.rfind("}")
            if start_obj != -1 and end_obj > start_obj:
                return json.loads(text[start_obj : end_obj + 1])
            raise

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
