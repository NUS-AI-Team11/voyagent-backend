"""Quick verifier for Route & Hotel planning output."""

from __future__ import annotations

import json
import random
import sys
from datetime import date
from pathlib import Path

# Allow running this script directly from the repository root or any cwd.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.route_hotel_planning.agent import RouteHotelPlanningAgent
from models.schemas import DiningList, Spot, SpotList, TravelProfile


def build_sample_inputs() -> tuple[TravelProfile, SpotList, DiningList]:
    city_spots = {
        "Tokyo": [
            ("Senso-ji", "Asakusa, Tokyo", "culture", 2.0),
            ("Ueno Park", "Ueno, Tokyo", "park", 1.5),
            ("Tokyo Skytree", "Sumida, Tokyo", "landmark", 1.5),
        ],
        "Paris": [
            ("Louvre Museum", "1st arrondissement, Paris", "museum", 2.0),
            ("Notre-Dame", "Ile de la Cite, Paris", "history", 1.5),
            ("Montmartre Walk", "Montmartre, Paris", "culture", 2.0),
        ],
        "Barcelona": [
            ("Sagrada Familia", "Eixample, Barcelona", "culture", 2.0),
            ("Park Guell", "Gracia, Barcelona", "park", 1.5),
            ("Gothic Quarter", "Ciutat Vella, Barcelona", "history", 1.5),
        ],
        "Seoul": [
            ("Gyeongbokgung", "Jongno-gu, Seoul", "history", 2.0),
            ("Bukchon Hanok Village", "Jongno-gu, Seoul", "culture", 1.5),
            ("N Seoul Tower", "Yongsan-gu, Seoul", "landmark", 1.5),
        ],
    }
    destination = random.choice(list(city_spots.keys()))

    profile = TravelProfile(
        destination=destination,
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 3),
        budget=3000,
        group_size=2,
        travel_style="mix",
    )
    spots = SpotList(
        spots=[
            Spot(name=name, description="", location=location, category=category, duration_hours=duration_hours)
            for name, location, category, duration_hours in city_spots[destination]
        ]
    )
    dining = DiningList()
    return profile, spots, dining


def verify() -> tuple[dict, bool]:
    profile, spots, dining = build_sample_inputs()
    agent = RouteHotelPlanningAgent()
    itinerary = agent.analyze_independently(profile, spots, dining)

    checks = {
        "has_itinerary": itinerary is not None,
        "has_days": bool(itinerary and itinerary.days),
        "day1_has_activities": False,
        "day1_has_accommodation": False,
        "day1_has_hotel_candidates": False,
        "day1_has_route_locations": False,
    }

    day_summaries: list[dict] = []
    if itinerary and itinerary.days:
        for day in itinerary.days:
            accommodation = day.accommodation or {}
            hotel_candidates = accommodation.get("hotel_candidates") or []
            route = [
                {
                    "time": activity.get("time"),
                    "name": activity.get("name"),
                    "location": activity.get("location"),
                    "travel_minutes_from_previous": activity.get("travel_minutes_from_previous", 0),
                }
                for activity in (day.activities or [])
            ]
            day_summaries.append(
                {
                    "day_number": day.day_number,
                    "activity_count": len(day.activities or []),
                    "first_activity": (day.activities or [{}])[0].get("name") if (day.activities or []) else None,
                    "hotel_name": accommodation.get("name"),
                    "hotel_address": accommodation.get("address"),
                    "hotel_candidates": len(hotel_candidates),
                    "route": route,
                }
            )

        day1 = itinerary.days[0]
        day1_accommodation = day1.accommodation or {}
        checks["day1_has_activities"] = len(day1.activities or []) > 0
        checks["day1_has_accommodation"] = bool(day1_accommodation.get("name") and day1_accommodation.get("address"))
        checks["day1_has_hotel_candidates"] = len(day1_accommodation.get("hotel_candidates") or []) > 0
        checks["day1_has_route_locations"] = all(
            bool(item.get("location")) for item in (day_summaries[0].get("route") or [])
        )

    ok = all(checks.values())
    report = {
        "ok": ok,
        "destination": profile.destination,
        "checks": checks,
        "days": day_summaries,
    }
    return report, ok


def main() -> int:
    report, ok = verify()
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

