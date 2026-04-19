"""
Human-readable text derived from structured planning payloads (for UI / handbook cards).
"""

from typing import Any, Dict, List, Optional


def _as_str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def itinerary_dict_to_narrative(itinerary: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Turn a serialized Itinerary dict into plain paragraphs for handbook-style display.
    """
    if not itinerary or not isinstance(itinerary, dict):
        return None
    days: List[Dict[str, Any]] = itinerary.get("days") or []
    if not days:
        return None

    blocks: list[str] = []
    loc = _as_str(itinerary.get("location"))
    if loc:
        blocks.append(f"Here is your day-by-day plan for {loc}.")
    else:
        blocks.append("Here is your day-by-day plan.")

    for day in days:
        dn = day.get("day_number")
        dt = _as_str(day.get("date"))
        head = f"Day {dn}" + (f" ({dt})" if dt else "")
        lines: list[str] = [head]

        for act in day.get("activities") or []:
            if not isinstance(act, dict):
                continue
            t = _as_str(act.get("time"))
            name = _as_str(act.get("name"))
            place = _as_str(act.get("location"))
            if not name:
                continue
            slot = f"{t} — {name}" if t else name
            if place and place.upper() != "TBD":
                slot = f"{slot} at {place}"
            lines.append(f"• {slot}")

        meals = day.get("meals") or {}
        if isinstance(meals, dict) and meals:
            parts: list[str] = []
            for key in ("breakfast", "lunch", "dinner"):
                if key in meals:
                    val = _as_str(meals.get(key))
                    if val and val.upper() != "TBD":
                        parts.append(f"{key.capitalize()}: {val}")
            if parts:
                lines.append("Meals: " + "; ".join(parts) + ".")

        acc = day.get("accommodation")
        if isinstance(acc, dict):
            hotel = _as_str(acc.get("name"))
            if hotel and hotel.upper() != "TBD":
                addr = _as_str(acc.get("address"))
                lines.append(f"Stay: {hotel}" + (f" ({addr})" if addr else "") + ".")

        notes = _as_str(day.get("notes"))
        if notes and notes.upper() != "TBD":
            lines.append(notes)

        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)
