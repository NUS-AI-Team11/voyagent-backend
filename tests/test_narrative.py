"""Unit tests for handbook-style narrative helpers."""

from api.narrative import itinerary_dict_to_narrative


def test_itinerary_dict_to_narrative_basic():
    d = {
        "location": "Kyoto",
        "days": [
            {
                "day_number": 1,
                "date": "2026-04-01",
                "activities": [{"time": "09:00", "name": "Silver Pavilion", "location": "Higashiyama"}],
                "meals": {"lunch": "Shojin lunch spot"},
            }
        ],
    }
    s = itinerary_dict_to_narrative(d)
    assert s
    assert "Kyoto" in s
    assert "Silver Pavilion" in s
    assert "Shojin" in s


def test_itinerary_dict_to_narrative_empty():
    assert itinerary_dict_to_narrative(None) is None
    assert itinerary_dict_to_narrative({}) is None
    assert itinerary_dict_to_narrative({"days": []}) is None
