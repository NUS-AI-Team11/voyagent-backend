"""
Route & Hotel Planning Agent - plans the full itinerary and hotel arrangement.
"""

import os
import json
import re
from pathlib import Path
import urllib.request
import urllib.error
from dotenv import load_dotenv
from agents.base_agent import BaseAgent
from models.schemas import (
    Itinerary, DayItinerary, TravelProfile, SpotList,
    DiningList, PlanningContext
)
from agents.route_hotel_planning.prompts import (
    SYSTEM_PROMPT,
    ITINERARY_CREATION_PROMPT,
    HOTEL_RECOMMENDATION_PROMPT,
    ROUTE_OPTIMIZATION_PROMPT,
    DAILY_SCHEDULE_PROMPT
)
from typing import List, Optional, Any, Dict
from datetime import datetime, timedelta


class RouteHotelPlanningAgent(BaseAgent):
    """Agent that plans routes and hotel accommodation."""

    @staticmethod
    def _safe_int(raw_value: Any, default: int, minimum: int = 1) -> int:
        """Safely parse integer config values from environment or runtime updates."""
        try:
            parsed = int(str(raw_value).strip())
        except (TypeError, ValueError):
            return max(minimum, int(default))
        return max(minimum, parsed)

    @staticmethod
    def _safe_float(raw_value: Any, default: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        """Safely parse float config values and clamp to bounds."""
        try:
            parsed = float(str(raw_value).strip())
        except (TypeError, ValueError):
            parsed = float(default)
        return max(minimum, min(maximum, parsed))

    @staticmethod
    def _normalize_api_mode(raw_value: Any, default: str = "auto") -> str:
        """Normalize api_mode into allowed values: auto | forced | off."""
        normalized = str(raw_value or default).strip().lower()
        return normalized if normalized in {"auto", "forced", "off"} else default

    def __init__(self):
        env_path = Path(__file__).resolve().parents[2] / ".env"
        load_dotenv(dotenv_path=env_path, override=False)

        super().__init__(
            name="Route & Hotel Planning Agent",
            description="Plans a complete day-by-day itinerary and hotel arrangement based on spot and restaurant recommendations"
        )
        # Agent-scoped key only: do not read OPENAI_API_KEY here.
        self.route_hotel_api_key = os.getenv("ROUTE_HOTEL_OPENAI_API_KEY", "")
        self.route_hotel_model = os.getenv("ROUTE_HOTEL_OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
        self._api_config: Dict[str, Any] = {
            "api_key": self.route_hotel_api_key,
            "model": self.route_hotel_model,
            "base_url": os.getenv("ROUTE_HOTEL_OPENAI_BASE_URL", "https://api.openai.com/v1/responses"),
            "timeout_seconds": self._safe_int(os.getenv("ROUTE_HOTEL_OPENAI_TIMEOUT", "20"), default=20),
            "temperature": self._safe_float(os.getenv("ROUTE_HOTEL_OPENAI_TEMPERATURE", "0.2"), default=0.2),
            # auto: try API then fallback, forced: API only, off: deterministic only
            "api_mode": self._normalize_api_mode(os.getenv("ROUTE_HOTEL_API_MODE", "auto"), default="auto"),
        }

    def get_api_config(self, include_secret: bool = False) -> Dict[str, Any]:
        """Return current agent-scoped API configuration for external callers."""
        config = dict(self._api_config)
        if not include_secret and config.get("api_key"):
            config["api_key"] = "***"
        return config

    def configure_api(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        temperature: Optional[float] = None,
        api_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update agent-scoped API config at runtime without mutating global env."""
        if api_key is not None:
            self._api_config["api_key"] = str(api_key).strip()
        if model is not None:
            self._api_config["model"] = str(model).strip() or self._api_config["model"]
        if base_url is not None:
            self._api_config["base_url"] = str(base_url).strip() or self._api_config["base_url"]
        if timeout_seconds is not None:
            self._api_config["timeout_seconds"] = self._safe_int(timeout_seconds, default=self._api_config.get("timeout_seconds", 20))
        if temperature is not None:
            self._api_config["temperature"] = self._safe_float(
                temperature,
                default=self._api_config.get("temperature", 0.2),
            )
        if api_mode is not None:
            self._api_config["api_mode"] = self._normalize_api_mode(api_mode, default=self._api_config.get("api_mode", "auto"))

        # Keep legacy attributes in sync for backwards compatibility.
        self.route_hotel_api_key = self._api_config.get("api_key", "")
        self.route_hotel_model = self._api_config.get("model", self.route_hotel_model)
        return self.get_api_config(include_secret=False)

    def reset_api_config(self) -> Dict[str, Any]:
        """Reset runtime API config from environment values."""
        self._api_config = {
            "api_key": os.getenv("ROUTE_HOTEL_OPENAI_API_KEY", ""),
            "model": os.getenv("ROUTE_HOTEL_OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini")),
            "base_url": os.getenv("ROUTE_HOTEL_OPENAI_BASE_URL", "https://api.openai.com/v1/responses"),
            "timeout_seconds": self._safe_int(os.getenv("ROUTE_HOTEL_OPENAI_TIMEOUT", "20"), default=20),
            "temperature": self._safe_float(os.getenv("ROUTE_HOTEL_OPENAI_TEMPERATURE", "0.2"), default=0.2),
            "api_mode": self._normalize_api_mode(os.getenv("ROUTE_HOTEL_API_MODE", "auto"), default="auto"),
        }
        self.route_hotel_api_key = self._api_config["api_key"]
        self.route_hotel_model = self._api_config["model"]
        return self.get_api_config(include_secret=False)

    def is_api_enabled(self) -> bool:
        """Whether external API calls are allowed for this agent instance."""
        mode = str(self._api_config.get("api_mode") or "auto").lower()
        if mode == "off":
            return False
        return bool(self._api_config.get("api_key"))

    def analyze_independently(
        self,
        travel_profile: TravelProfile,
        spot_list: Optional[SpotList] = None,
        dining_list: Optional[DiningList] = None,
    ) -> Itinerary:
        """Standalone itinerary analysis API for direct use outside shared workflow context."""
        if travel_profile is None:
            raise ValueError("travel_profile is required")

        spot_list = spot_list or SpotList()
        dining_list = dining_list or DiningList()
        days = self._create_daily_itineraries(travel_profile, spot_list, dining_list)

        return Itinerary(
            location=travel_profile.destination,
            start_date=travel_profile.start_date,
            end_date=travel_profile.end_date,
            days=days,
            estimated_total_cost=sum(day.total_estimated_cost for day in days),
            cost_breakdown={
                "transport": 0.0,
                "accommodation": 0.0,
                "food": 0.0,
                "attractions": 0.0,
            },
            generated_at=datetime.now(),
        )

    def fetch_agent_api_response(
        self,
        user_prompt: str,
        system_prompt: str = SYSTEM_PROMPT,
        temperature: Optional[float] = None,
    ) -> Optional[dict]:
        """Dedicated API retrieval interface using this agent's isolated credentials/config."""
        if not self.is_api_enabled():
            return None

        request_temperature = self._api_config.get("temperature", 0.2) if temperature is None else float(temperature)
        body = {
            "model": self._api_config.get("model", self.route_hotel_model),
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": max(0.0, min(1.0, request_temperature)),
        }

        request = urllib.request.Request(
            url=self._api_config.get("base_url", "https://api.openai.com/v1/responses"),
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_config.get('api_key', '')}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=int(self._api_config.get("timeout_seconds", 20))) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            self.log_execution(f"Route-hotel API request failed: {str(exc)}", level="warning")
            return None

    def process(self, context: PlanningContext) -> PlanningContext:
        """
        Process spot and restaurant recommendations and generate a full itinerary.

        Args:
            context: planning context containing TravelProfile, SpotList, DiningList

        Returns:
            context with itinerary populated
        """
        try:
            if not self.validate_input(context):
                context.add_error("Missing required input")
                return context

            context.itinerary = self.analyze_independently(
                travel_profile=context.travel_profile,
                spot_list=context.spot_list,
                dining_list=context.dining_list,
            )
            self.log_execution(f"Created {len(context.itinerary.days)}-day itinerary")

        except Exception as e:
            context.add_error(f"Itinerary planning failed: {str(e)}")
            self.log_execution(f"Error: {str(e)}", level="error")

        return context

    def validate_input(self, context: PlanningContext) -> bool:
        """Validate required input."""
        return (
            context.travel_profile is not None and
            context.spot_list is not None and
            context.dining_list is not None
        )

    def _create_daily_itineraries(
        self,
        travel_profile: TravelProfile,
        spot_list: SpotList,
        dining_list: DiningList
    ) -> List[DayItinerary]:
        """
        Create a detailed itinerary for each day.

        Args:
            travel_profile: user travel information
            spot_list: recommended attractions
            dining_list: recommended restaurants

        Returns:
            list of DayItinerary objects
        """
        days = []
        current_date = travel_profile.start_date
        day_number = 1

        num_days = max(1, (travel_profile.end_date - travel_profile.start_date).days + 1)
        spots = spot_list.spots or []
        restaurants = dining_list.restaurants or []

        # Evenly distribute attractions across days while preserving recommendation order.
        base_spots_per_day = len(spots) // num_days if num_days > 0 else 0
        extra_spots = len(spots) % num_days if num_days > 0 else 0
        spot_cursor = 0

        while day_number <= num_days:
            day_index = day_number - 1
            spots_for_today = base_spots_per_day + (1 if day_index < extra_spots else 0)
            daily_spots = spots[spot_cursor: spot_cursor + spots_for_today]
            spot_cursor += spots_for_today

            optimized_daily_spots = self._order_spots_nearest_neighbor(daily_spots)
            activities, activity_cost = self._build_dynamic_activities(
                ordered_spots=optimized_daily_spots,
                destination=travel_profile.destination,
            )

            if not activities:
                activities.append({
                    "time": "10:00",
                    "name": "Leisure walk and local exploration",
                    "location": travel_profile.destination,
                    "cost": 0.0,
                    "duration_hours": 2.0,
                })

            meals = {"breakfast": "TBD", "lunch": "TBD", "dinner": "TBD"}
            meal_cost = 0.0
            meal_keys = ["breakfast", "lunch", "dinner"]
            selected_restaurants = []

            if restaurants:
                for offset, meal_key in enumerate(meal_keys):
                    restaurant = restaurants[(day_index * len(meal_keys) + offset) % len(restaurants)]
                    selected_restaurants.append(restaurant)
                    meals[meal_key] = restaurant.name
                    avg_cost = float(restaurant.average_cost_per_person or 0.0)
                    meal_cost += avg_cost * max(1, travel_profile.group_size)

            accommodation_addresses = self._resolve_accommodation_addresses(
                activities=activities,
                selected_restaurants=selected_restaurants,
                destination=travel_profile.destination,
            )
            nightly_hotel_cost = round(max(80.0, travel_profile.budget * 0.35 / num_days), 2)
            hotel_candidates = self._fetch_hotel_candidates_via_api(
                destination=travel_profile.destination,
                addresses=accommodation_addresses,
                base_nightly_cost=nightly_hotel_cost,
                group_size=max(1, int(travel_profile.group_size or 1)),
            )
            if not hotel_candidates:
                hotel_candidates = self._build_hotel_candidates(
                    addresses=accommodation_addresses,
                    base_nightly_cost=nightly_hotel_cost,
                    destination=travel_profile.destination,
                )
                self.log_execution(
                    f"hotel_source=fallback day={day_number} candidates={len(hotel_candidates)}",
                    level="info",
                )
            else:
                self.log_execution(
                    f"hotel_source=api day={day_number} candidates={len(hotel_candidates)}",
                    level="info",
                )
            primary_hotel = hotel_candidates[0]
            accommodation = {
                "name": primary_hotel["name"],
                "address": primary_hotel["address"],
                "addresses": accommodation_addresses,
                "cost_per_night": primary_hotel["cost_per_night"],
                "rating": primary_hotel["rating"],
                "hotel_candidates": hotel_candidates,
            }

            day_total_cost = round(activity_cost + meal_cost + nightly_hotel_cost, 2)
            day_itinerary = DayItinerary(
                day_number=day_number,
                date=current_date,
                activities=activities,
                meals=meals,
                accommodation=accommodation,
                total_estimated_cost=day_total_cost,
                notes="Plan grouped by proximity with balanced daily pace",
            )

            days.append(day_itinerary)
            current_date += timedelta(days=1)
            day_number += 1

        return days

    def _order_spots_nearest_neighbor(self, spots: List[object]) -> List[object]:
        """Order spots using a greedy nearest-neighbor route heuristic from text locations."""
        if len(spots) <= 1:
            return list(spots)

        remaining = list(spots[1:])
        ordered = [spots[0]]

        while remaining:
            current_location = str(getattr(ordered[-1], "location", "") or "")
            next_index = min(
                range(len(remaining)),
                key=lambda idx: self._location_distance(current_location, str(getattr(remaining[idx], "location", "") or "")),
            )
            ordered.append(remaining.pop(next_index))

        return ordered

    def _build_dynamic_activities(self, ordered_spots: List[object], destination: str) -> tuple[List[dict], float]:
        """Build activity blocks with dynamic time slots, travel buffer, and lunch-window adjustment."""
        if not ordered_spots:
            return [
                {
                    "time": "10:00",
                    "name": "Leisure walk and local exploration",
                    "location": destination,
                    "cost": 0.0,
                    "duration_hours": 2.0,
                }
            ], 0.0

        activities: List[dict] = []
        activity_cost = 0.0
        current_minutes = self._parse_time_hhmm("09:00")
        lunch_taken = False
        prev_location: Optional[str] = None

        for spot in ordered_spots:
            spot_location = str(getattr(spot, "location", "") or destination)
            transit_minutes = 0
            if prev_location:
                transit_minutes = self._estimate_transit_minutes(prev_location, spot_location)
                current_minutes += transit_minutes

            current_minutes, lunch_taken = self._apply_lunch_window(current_minutes, lunch_taken)

            open_start, open_end = self._parse_opening_hours(getattr(spot, "opening_hours", None))
            if open_start is not None and current_minutes < open_start:
                current_minutes = open_start

            entrance_fee = float(getattr(spot, "entrance_fee", 0.0) or 0.0)
            duration_hours = float(getattr(spot, "duration_hours", 2.0) or 2.0)
            duration_minutes = max(30, int(round(duration_hours * 60)))

            activity = {
                "time": self._format_time_hhmm(current_minutes),
                "name": getattr(spot, "name", "Attraction"),
                "location": spot_location,
                "cost": entrance_fee,
                "duration_hours": duration_hours,
                "travel_minutes_from_previous": transit_minutes,
            }
            if open_end is not None and current_minutes > open_end:
                activity["time_window_note"] = "Scheduled after typical closing time"

            activities.append(activity)
            activity_cost += entrance_fee
            current_minutes += duration_minutes
            prev_location = spot_location

        return activities, activity_cost

    def _location_distance(self, source: str, target: str) -> float:
        """Estimate text-based location distance for heuristic ordering when no coordinates are available."""
        s = source.strip().lower()
        t = target.strip().lower()
        if not s or not t:
            return 1.0
        if s == t:
            return 0.0

        s_area = s.split(",")[0].strip()
        t_area = t.split(",")[0].strip()
        if s_area and t_area and s_area == t_area:
            return 0.25

        s_tokens = set(re.findall(r"[a-z0-9]+", s))
        t_tokens = set(re.findall(r"[a-z0-9]+", t))
        if not s_tokens or not t_tokens:
            return 1.0

        overlap = len(s_tokens.intersection(t_tokens))
        union = len(s_tokens.union(t_tokens))
        jaccard = overlap / union if union else 0.0
        return round(1.0 - jaccard, 4)

    def _estimate_transit_minutes(self, source: str, target: str) -> int:
        """Estimate transfer time from text similarity; bounded to practical city travel ranges."""
        distance_score = self._location_distance(source, target)
        if distance_score <= 0.1:
            return 10
        if distance_score <= 0.35:
            return 18
        if distance_score <= 0.6:
            return 28
        return 40

    def _apply_lunch_window(self, current_minutes: int, lunch_taken: bool) -> tuple[int, bool]:
        """Insert a one-hour lunch break once when schedule reaches lunchtime."""
        if lunch_taken:
            return current_minutes, lunch_taken

        lunch_start = self._parse_time_hhmm("12:00")
        lunch_end = self._parse_time_hhmm("14:00")
        if lunch_start <= current_minutes <= lunch_end:
            return current_minutes + 60, True
        return current_minutes, lunch_taken

    def _parse_opening_hours(self, opening_hours: Optional[str]) -> tuple[Optional[int], Optional[int]]:
        """Parse a simple HH:MM-HH:MM opening-hours string into minutes from midnight."""
        if not opening_hours:
            return None, None

        match = re.search(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", str(opening_hours))
        if not match:
            return None, None

        start = self._parse_time_hhmm(match.group(1))
        end = self._parse_time_hhmm(match.group(2))
        if end <= start:
            return start, None
        return start, end

    def _parse_time_hhmm(self, value: str) -> int:
        """Parse HH:MM into absolute minutes from midnight."""
        hour_text, minute_text = value.split(":", 1)
        hour = max(0, min(23, int(hour_text)))
        minute = max(0, min(59, int(minute_text)))
        return hour * 60 + minute

    def _format_time_hhmm(self, minutes: int) -> str:
        """Format absolute minutes into HH:MM (24-hour)."""
        normalized = max(0, minutes) % (24 * 60)
        hour = normalized // 60
        minute = normalized % 60
        return f"{hour:02d}:{minute:02d}"

    def _resolve_accommodation_addresses(
        self,
        activities: List[dict],
        selected_restaurants: List[object],
        destination: str,
    ) -> List[str]:
        """Collect multiple practical hotel area candidates from activities, dining, and city center."""
        addresses: List[str] = []

        if activities:
            for activity in activities:
                activity_location = activity.get("location")
                if activity_location:
                    addresses.append(str(activity_location))

        if selected_restaurants:
            for restaurant in selected_restaurants:
                restaurant_location = getattr(restaurant, "location", None)
                if restaurant_location:
                    addresses.append(str(restaurant_location))

        # Keep order but remove duplicates and empty values.
        normalized: List[str] = []
        seen = set()
        for addr in addresses:
            key = addr.strip()
            if not key or key in seen:
                continue
            seen.add(key)
            normalized.append(key)

        if not normalized:
            normalized.append(f"City Center, {destination}")

        return normalized

    def _build_hotel_candidates(
        self,
        addresses: List[str],
        base_nightly_cost: float,
        destination: str,
    ) -> List[dict]:
        """Build and rank deterministic hotel recommendations from location candidates."""
        cost_factors = [0.92, 1.0, 1.15]
        rating_offsets = [0.15, 0.25, 0.35]

        candidates = []
        for index, address in enumerate(addresses[:3]):
            area_label = address.split(",")[0].strip() if address else destination
            candidates.append(
                {
                    "name": f"{area_label} Stay {index + 1}",
                    "address": address,
                    "cost_per_night": round(base_nightly_cost * cost_factors[index], 2),
                    "rating": round(min(4.9, 4.0 + rating_offsets[index]), 1),
                }
            )

        if not candidates:
            candidates.append(
                {
                    "name": f"{destination} Central Stay 1",
                    "address": f"City Center, {destination}",
                    "cost_per_night": round(base_nightly_cost, 2),
                    "rating": 4.2,
                }
            )

        for index, candidate in enumerate(candidates):
            candidate["_score"] = self._score_hotel_candidate(
                candidate=candidate,
                candidate_index=index,
                target_cost=base_nightly_cost,
            )

        candidates.sort(
            key=lambda item: (
                item.get("_score", 0.0),
                item.get("rating", 0.0),
            ),
            reverse=True,
        )

        for candidate in candidates:
            candidate.pop("_score", None)

        return candidates

    def _fetch_hotel_candidates_via_api(
        self,
        destination: str,
        addresses: List[str],
        base_nightly_cost: float,
        group_size: int,
    ) -> Optional[List[dict]]:
        """Fetch hotel candidates from OpenAI Responses API; return None on any failure."""
        if not self.is_api_enabled():
            return None

        address_text = "\n".join(f"- {addr}" for addr in addresses[:6]) or f"- City Center, {destination}"
        prompt = (
            f"{HOTEL_RECOMMENDATION_PROMPT}\n\n"
            f"Destination: {destination}\n"
            f"Group size: {group_size}\n"
            f"Target nightly budget: {base_nightly_cost}\n"
            f"Preferred areas:\n{address_text}\n\n"
            "Return ONLY JSON array with 3 hotel objects."
            " Each item must include: name, address, cost_per_night, rating."
            " No markdown, no explanation."
        )

        payload = self.fetch_agent_api_response(user_prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.2)
        if not payload:
            if str(self._api_config.get("api_mode") or "auto").lower() == "forced":
                self.log_execution("Hotel API required but unavailable in forced mode", level="warning")
            return None

        output_text = self._extract_responses_output_text(payload)
        if not output_text:
            self.log_execution("Hotel API returned empty output text, using fallback", level="warning")
            return None

        parsed = self._parse_json_block(output_text)
        if not isinstance(parsed, list):
            self.log_execution("Hotel API output is not a JSON list, using fallback", level="warning")
            return None

        normalized = self._normalize_api_hotel_candidates(
            parsed=parsed,
            fallback_addresses=addresses,
            base_nightly_cost=base_nightly_cost,
            destination=destination,
        )
        return normalized or None

    def _extract_responses_output_text(self, payload: dict) -> str:
        """Extract plain text from Responses API payload."""
        text = payload.get("output_text")
        if isinstance(text, str) and text.strip():
            return text

        chunks = []
        for item in payload.get("output", []) or []:
            for content in item.get("content", []) or []:
                value = content.get("text")
                if isinstance(value, str):
                    chunks.append(value)
        return "\n".join(chunks).strip()

    def _parse_json_block(self, text: str) -> Any:
        """Parse raw JSON or first JSON block in mixed text."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        start_obj = text.find("{")
        start_arr = text.find("[")
        starts = [idx for idx in [start_obj, start_arr] if idx != -1]
        if not starts:
            return None

        start = min(starts)
        for end in range(len(text), start, -1):
            candidate = text[start:end]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        return None

    def _normalize_api_hotel_candidates(
        self,
        parsed: List[dict],
        fallback_addresses: List[str],
        base_nightly_cost: float,
        destination: str,
    ) -> List[dict]:
        """Normalize API candidates into stable schema and keep top 3 unique addresses."""
        candidates: List[dict] = []
        used_addresses = set()

        for index, item in enumerate(parsed):
            if not isinstance(item, dict):
                continue

            fallback_address = fallback_addresses[index] if index < len(fallback_addresses) else f"City Center, {destination}"
            address = str(item.get("address") or fallback_address).strip()
            if not address or address in used_addresses:
                continue
            used_addresses.add(address)

            area_label = address.split(",")[0].strip() if "," in address else address
            name = str(item.get("name") or f"{area_label} Stay {len(candidates) + 1}").strip()

            try:
                cost = float(item.get("cost_per_night"))
            except (TypeError, ValueError):
                cost = round(base_nightly_cost * (1.0 + (0.08 * len(candidates))), 2)

            try:
                rating = float(item.get("rating"))
            except (TypeError, ValueError):
                rating = 4.2
            rating = round(min(5.0, max(3.0, rating)), 1)

            candidates.append(
                {
                    "name": name,
                    "address": address,
                    "cost_per_night": round(max(50.0, cost), 2),
                    "rating": rating,
                }
            )

            if len(candidates) >= 3:
                break

        return candidates

    def _score_hotel_candidate(self, candidate: dict, candidate_index: int, target_cost: float) -> float:
        """Score candidate by price fitness and location priority for stable ranking."""
        nightly_cost = float(candidate.get("cost_per_night") or 0.0)
        target = max(1.0, float(target_cost or 0.0))
        price_delta_ratio = abs(nightly_cost - target) / target
        budget_fit_score = max(0.0, 1.0 - price_delta_ratio)

        location_priority_score = max(0.0, 1.0 - (candidate_index * 0.25))
        address = str(candidate.get("address") or "").lower()
        if "city center" in address:
            location_priority_score = max(0.0, location_priority_score - 0.1)

        rating_score = min(1.0, max(0.0, float(candidate.get("rating") or 0.0) / 5.0))

        return round((budget_fit_score * 0.7) + (location_priority_score * 0.2) + (rating_score * 0.1), 4)

    def _resolve_accommodation_address(self, activities: List[dict], selected_restaurants: List[object], destination: str) -> str:
        """Backwards-compatible single best address based on first candidate."""
        return self._resolve_accommodation_addresses(activities, selected_restaurants, destination)[0]
