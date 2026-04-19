"""
User Preference Agent - collects and parses user travel preferences.
"""

import json
import os
import re
from typing import Dict, Any, List
from datetime import datetime, date

from openai import OpenAI

from agents.base_agent import BaseAgent
from models.schemas import TravelProfile, PlanningContext
from agents.user_preference.prompts import (
    SYSTEM_PROMPT,
    USER_PREFERENCE_EXTRACTION_PROMPT,
    CLARIFICATION_PROMPT,
    PROFILE_SUMMARY_PROMPT
)


class UserPreferenceAgent(BaseAgent):
    """Agent that collects and parses user travel preferences."""

    def __init__(self):
        super().__init__(
            name="User Preference Agent",
            description="Collects and parses user travel preference information"
        )
        self.required_fields = [
            'destination', 'start_date', 'end_date',
            'budget', 'group_size', 'travel_style'
        ]
        self._client = self._create_openai_client()
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"

    def process(self, context: PlanningContext) -> PlanningContext:
        """
        Process user input and produce a TravelProfile.

        Args:
            context: planning context containing raw user input in metadata

        Returns:
            context with travel_profile populated
        """
        try:
            user_input = context.metadata.get('user_input', '')

            if not user_input:
                context.add_error("User input is empty")
                return context

            preference_data = self._extract_preferences(user_input)

            missing_fields = self._validate_required_fields(preference_data)
            if missing_fields:
                context.add_warning(f"Missing fields: {', '.join(missing_fields)}")
                context.add_error(
                    f"Unable to build travel profile because required fields are missing: {', '.join(missing_fields)}"
                )
                return context

            travel_profile = self._create_travel_profile(preference_data)
            context.travel_profile = travel_profile

            self.log_execution(f"Parsed user preferences: {travel_profile.destination}")

        except Exception as e:
            context.add_error(f"User preference processing failed: {str(e)}")
            self.log_execution(f"Error: {str(e)}", level="error")

        return context

    def _extract_preferences(self, user_input: str) -> Dict[str, Any]:
        """
        Extract preference information from user input.

        Args:
            user_input: raw user input text

        Returns:
            extracted preference data dict

        """
        try:
            if self._client:
                llm_data = self._extract_preferences_llm(user_input)
                return self._normalize_preference_data(llm_data, user_input)
        except Exception as exc:
            self.log_execution(f"LLM extraction failed, using fallback parser: {exc}", level="warning")

        fallback_data = self._extract_preferences_fallback(user_input)
        return self._normalize_preference_data(fallback_data, user_input)

    def _create_openai_client(self) -> Any:
        """Create OpenAI client when API key is available."""
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or api_key == "OPENAI_API_KEY":
            return None
        return OpenAI(api_key=api_key)

    def _extract_preferences_llm(self, user_input: str) -> Dict[str, Any]:
        """Extract preferences through an LLM call."""
        if not self._client:
            raise ValueError("OPENAI_API_KEY not configured")

        prompt = USER_PREFERENCE_EXTRACTION_PROMPT.format(user_input=user_input)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM returned empty response")
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("LLM response is not a JSON object")
        return parsed

    def _extract_preferences_fallback(self, user_input: str) -> Dict[str, Any]:
        """Heuristic parser used when LLM is unavailable."""
        return {
            "destination": self._parse_destination(user_input),
            "start_date": self._parse_date_from_text(user_input, "depart"),
            "end_date": self._parse_date_from_text(user_input, "return"),
            "budget": self._parse_budget(user_input),
            "group_size": self._parse_group_size(user_input),
            "travel_style": self._parse_travel_style(user_input),
            "interests": self._parse_interests(user_input),
            "dietary_restrictions": self._parse_dietary_restrictions(user_input),
            "hotel_preference": self._parse_hotel_preference(user_input),
            "transportation_preference": self._parse_transport_preference(user_input),
            "custom_notes": user_input,
        }

    def _normalize_preference_data(self, preference_data: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Normalize parsed preference data into schema-friendly values."""
        normalized = dict(preference_data or {})
        normalized["destination"] = str(normalized.get("destination") or "").strip()
        normalized["start_date"] = self._parse_date_value(normalized.get("start_date"))
        normalized["end_date"] = self._parse_date_value(normalized.get("end_date"))
        normalized["budget"] = self._safe_float(normalized.get("budget"), default=0.0)
        normalized["group_size"] = self._safe_int(normalized.get("group_size"), default=1)
        normalized["travel_style"] = str(normalized.get("travel_style") or "").strip().lower()
        normalized["interests"] = self._normalize_list(normalized.get("interests"))
        normalized["dietary_restrictions"] = self._normalize_list(normalized.get("dietary_restrictions"))
        normalized["hotel_preference"] = self._normalize_optional_string(normalized.get("hotel_preference"))
        normalized["transportation_preference"] = self._normalize_optional_string(
            normalized.get("transportation_preference")
        )
        normalized["custom_notes"] = self._normalize_optional_string(normalized.get("custom_notes")) or user_input

        # If LLM returned budget as a string like "USD 4,200" or omitted it, repair from raw text.
        bud = self._safe_float(normalized.get("budget"), default=0.0)
        if bud <= 0:
            text_budget = self._parse_budget(user_input)
            if text_budget > 0:
                normalized["budget"] = text_budget

        return normalized

    def _validate_required_fields(self, preference_data: Dict[str, Any]) -> list:
        """
        Check which required fields are missing.

        Args:
            preference_data: extracted preference data

        Returns:
            list of missing field names
        """
        missing = []
        for field in self.required_fields:
            if not preference_data.get(field):
                missing.append(field)
        return missing

    def _create_travel_profile(self, preference_data: Dict[str, Any]) -> TravelProfile:
        """
        Build a TravelProfile from extracted data.

        Args:
            preference_data: extracted preference data

        Returns:
            TravelProfile object
        """
        return TravelProfile(
            destination=str(preference_data.get('destination') or ''),
            start_date=preference_data.get('start_date') or date.today(),
            end_date=preference_data.get('end_date') or date.today(),
            budget=self._safe_float(preference_data.get('budget'), default=0.0),
            group_size=self._safe_int(preference_data.get('group_size'), default=1),
            travel_style=str(preference_data.get('travel_style') or ''),
            interests=preference_data.get('interests', []),
            dietary_restrictions=preference_data.get('dietary_restrictions', []),
            hotel_preference=preference_data.get('hotel_preference'),
            transportation_preference=preference_data.get('transportation_preference'),
            custom_notes=preference_data.get('custom_notes'),
        )

    def _normalize_list(self, value: Any) -> List[str]:
        """Normalize list-like values into a clean list of strings."""
        if value is None:
            return []
        if isinstance(value, list):
            items = value
        elif isinstance(value, str):
            items = re.split(r"[,\n;/]+", value)
        else:
            return []
        return [str(item).strip().lower() for item in items if str(item).strip()]

    def _normalize_optional_string(self, value: Any) -> Any:
        """Convert value to stripped string or None."""
        if value is None:
            return None
        text = str(value).strip()
        return text if text else None

    def _parse_date_value(self, value: Any) -> Any:
        """Parse date values from date/datetime/string input."""
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if not value:
            return None

        text = str(value).strip()
        try:
            return datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            pass
        try:
            parsed = datetime.strptime(text, "%B %d")
            return parsed.replace(year=date.today().year).date()
        except ValueError:
            return None

    def _parse_destination(self, user_input: str) -> str:
        """Extract destination from free text with simple patterns."""
        patterns = [
            r"\bvisit\s+([A-Za-z\s]+?)(?:,|\.|\n|$)",
            r"\btrip to\s+([A-Za-z\s]+?)(?:,|\.|\n|$)",
            r"\bto\s+([A-Za-z\s]+?)(?:,|\.|\n|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                value = re.sub(r"\s+", " ", value)
                if value:
                    return value
        return ""

    def _parse_date_from_text(self, user_input: str, marker: str) -> Any:
        """Extract month-day date around a marker word."""
        pattern = rf"{marker}[a-z]*\s+(?:on\s+)?([A-Za-z]+)\s+(\d{{1,2}})"
        match = re.search(pattern, user_input, re.IGNORECASE)
        if not match:
            return None
        month, day = match.group(1), match.group(2)
        try:
            parsed = datetime.strptime(f"{month} {day}", "%B %d")
            return parsed.replace(year=date.today().year).date()
        except ValueError:
            return None

    def _parse_budget(self, user_input: str) -> float:
        """Extract first currency-like number as budget."""
        patterns = [
            # "total budget is USD 4,200" / "budget of EUR 3.500,50" (European decimals less common)
            r"(?:budget|total\s+budget)\s+is\s+(?:USD|EUR|GBP)\s*([0-9][0-9,\.]*)",
            r"(?:budget|total)\s+(?:is\s+)?(?:USD|EUR|GBP)\s*([0-9][0-9,\.]*)",
            r"(?:budget|total)\D*\$?\s*([0-9][0-9,]*(?:\.\d+)?)",
            r"\$\s*([0-9][0-9,]*(?:\.\d+)?)",
            r"(?<![A-Za-z])(?:USD|EUR|GBP)\s*([0-9][0-9,\.]*)",
        ]
        for pat in patterns:
            match = re.search(pat, user_input, re.IGNORECASE)
            if match:
                raw = match.group(1).replace(",", "")
                val = self._safe_float(raw, default=0.0)
                if val > 0:
                    return val
        return 0.0

    def _parse_group_size(self, user_input: str) -> int:
        """Extract group size from common phrases."""
        patterns = [
            r"for\s+(\d+)\s+people",
            r"group\s+of\s+(\d+)",
            r"(\d+)\s+traveler",
        ]
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return self._safe_int(match.group(1), default=1)
        return 1

    def _parse_travel_style(self, user_input: str) -> str:
        """Infer travel style from explicit keywords."""
        styles = ["adventure", "relaxation", "culture", "shopping", "food", "family", "luxury", "budget"]
        lower = user_input.lower()
        for style in styles:
            if style in lower:
                return style
        return "general"

    def _parse_interests(self, user_input: str) -> List[str]:
        """Extract coarse interests from common keywords."""
        keywords = ["culture", "food", "history", "nature", "art", "shopping", "nightlife", "temples", "museum"]
        lower = user_input.lower()
        return [word for word in keywords if word in lower]

    def _parse_dietary_restrictions(self, user_input: str) -> List[str]:
        """Extract dietary restriction keywords."""
        keywords = ["vegetarian", "vegan", "halal", "kosher", "gluten-free", "gluten free"]
        lower = user_input.lower()
        found = [word.replace(" ", "_") for word in keywords if word in lower]
        return list(dict.fromkeys(found))

    def _parse_hotel_preference(self, user_input: str) -> Any:
        """Extract coarse hotel preference."""
        lower = user_input.lower()
        if "luxury" in lower:
            return "luxury"
        if "budget" in lower:
            return "budget"
        if "comfortable" in lower or "mid-range" in lower:
            return "comfortable"
        return None

    def _parse_transport_preference(self, user_input: str) -> Any:
        """Extract transportation preference."""
        lower = user_input.lower()
        if "public transit" in lower or "public transport" in lower:
            return "public_transit"
        if "self-drive" in lower or "self drive" in lower or "car rental" in lower:
            return "self_drive"
        if "flight" in lower or "flights" in lower:
            return "flights"
        return None

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Convert a value to float with a safe fallback."""
        if value is None or value == "":
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            s = value.strip()
            s = re.sub(r"(?i)^\s*(usd|eur|gbp|\$)\s*", "", s)
            s = re.sub(r"(?i)\s*(usd|eur|gbp)\s*$", "", s)
            s = s.replace(",", "").strip()
            if not s:
                return default
            try:
                return float(s)
            except ValueError:
                return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _safe_int(self, value: Any, default: int = 1) -> int:
        """Convert a value to int with a safe fallback."""
        if value is None or value == "":
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
