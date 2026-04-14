"""
User Preference Agent - collects and parses user travel preferences.
"""

import json
from typing import Dict, Any
from datetime import datetime, date

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
        # In a real implementation this would call the LLM to parse user input.
        preference_data = {
            'destination': self._extract_field(user_input, 'destination'),
            'start_date': self._extract_field(user_input, 'start_date'),
            'end_date': self._extract_field(user_input, 'end_date'),
            'budget': self._extract_field(user_input, 'budget'),
            'group_size': self._extract_field(user_input, 'group_size'),
            'travel_style': self._extract_field(user_input, 'travel_style'),
            'interests': self._extract_field(user_input, 'interests', default=[]),
            'dietary_restrictions': self._extract_field(user_input, 'dietary_restrictions', default=[]),
            'hotel_preference': self._extract_field(user_input, 'hotel_preference'),
            'transportation_preference': self._extract_field(user_input, 'transportation_preference'),
            'custom_notes': self._extract_field(user_input, 'custom_notes'),
        }

        return preference_data

    def _extract_field(self, text: str, field_name: str, default: Any = None) -> Any:
        """
        Extract a specific field from text.

        Args:
            text: input text
            field_name: field to extract
            default: fallback value

        Returns:
            extracted value or default
        """
        # Simplified stub; real implementation would use LLM.
        return default

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
            destination=preference_data.get('destination', ''),
            start_date=preference_data.get('start_date') or date.today(),
            end_date=preference_data.get('end_date') or date.today(),
            budget=float(preference_data.get('budget', 0)),
            group_size=int(preference_data.get('group_size', 1)),
            travel_style=preference_data.get('travel_style', ''),
            interests=preference_data.get('interests', []),
            dietary_restrictions=preference_data.get('dietary_restrictions', []),
            hotel_preference=preference_data.get('hotel_preference'),
            transportation_preference=preference_data.get('transportation_preference'),
            custom_notes=preference_data.get('custom_notes'),
        )
