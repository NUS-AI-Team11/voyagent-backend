"""
User Preference Agent - collects and parses user travel preferences.
"""

import json
from typing import Dict, Any
from datetime import datetime, date, timedelta

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

        TODO:
            Replace the mock data below with a real LLM call.
            Steps:
              1. Build the prompt using USER_PREFERENCE_EXTRACTION_PROMPT from prompts.py
              2. Call your LLM client with SYSTEM_PROMPT + the formatted prompt
              3. Parse the JSON response the LLM returns
              4. Return the parsed dict — the keys must match the ones below

            The LLM should return a JSON object with these fields:
              destination, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD),
              budget (number), group_size (integer), travel_style (string),
              interests (list), dietary_restrictions (list),
              hotel_preference, transportation_preference, custom_notes
        """
        # ---------------------------------------------------------------------------
        # MOCK DATA — hardcoded so the full pipeline can run end-to-end for testing.
        # Delete this block and replace it with your LLM call when you implement the
        # real agent logic.
        # ---------------------------------------------------------------------------
        preference_data = {
            'destination': 'Tokyo',
            'start_date': date(2025, 5, 1),
            'end_date': date(2025, 5, 7),
            'budget': 5000.0,
            'group_size': 2,
            'travel_style': 'culture',
            'interests': ['history', 'food', 'temples'],
            'dietary_restrictions': [],
            'hotel_preference': 'mid-range',
            'transportation_preference': 'public_transit',
            'custom_notes': user_input,
        }
        # ---------------------------------------------------------------------------
        return preference_data

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

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Convert a value to float with a safe fallback."""
        if value is None or value == "":
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
