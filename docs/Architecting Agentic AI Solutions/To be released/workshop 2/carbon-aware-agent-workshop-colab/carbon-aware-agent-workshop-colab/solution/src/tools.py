
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import os, json
import re

from langchain_core.tools import tool
from zoneinfo import ZoneInfo
from dateutil import parser as dparser

from memory import (load_profile, save_profile)

DATA_FP = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "mock_forecast.json")

def load_forecast():
    with open(DATA_FP, "r", encoding="utf-8") as f:
        return json.load(f)

@tool("get_profile", return_direct=False)
def get_profile_tool() -> dict:
    """Return current persistent preferences: regions_allowed, allowed_shift_minutes."""
    return load_profile()


@tool("update_prefs", return_direct=False)
def update_prefs_tool(regions_allowed: Optional[str] = None, allowed_shift_minutes: Optional[int] = None) -> dict:
    """Update persistent preferences. 
    - regions_allowed: optional comma-separated regions like 'SG,EU_WEST'
    - allowed_shift_minutes: optional integer shift window
    Returns the updated profile.
    Use this tool whenever the user says 'I prefer...' or 'remember...' about regions/shift, or otherwise expresses a clear preference update.
    """
    p = load_profile()
    if regions_allowed:
        regions = [r.strip().upper() for r in regions_allowed.split(",") if r.strip()]
        if regions:
            p["regions_allowed"] = regions
    if allowed_shift_minutes is not None:
        p["allowed_shift_minutes"] = int(allowed_shift_minutes)
    save_profile(p)
    return p


SG_TZ = ZoneInfo("Asia/Singapore")
_REL = re.compile(r"^\s*(today|tomorrow)\s*(.*)\s*$", re.IGNORECASE)

def snap_15(dt: datetime) -> datetime:
    dt = dt.replace(second=0, microsecond=0)
    return dt.replace(minute=(dt.minute // 15) * 15)

def _parse_time_iso(text_time: str) -> str:
    """Parse user time to ISO string in Asia/Singapore, snapped to 15 minutes.

    Kept as a plain function so other tools can call it internally.
    """
    now = datetime.now(tz=SG_TZ)

    m = _REL.match(text_time.strip())
    if m:
        day_word = m.group(1).lower()
        rest = m.group(2).strip() or "00:00"
        base = now + timedelta(days=1 if day_word == "tomorrow" else 0)
        base = base.replace(hour=0, minute=0, second=0, microsecond=0)
        dt = dparser.parse(rest, default=base).replace(
            year=base.year, month=base.month, day=base.day
        )
        dt = dt.replace(tzinfo=SG_TZ)
    else:
        dt = dparser.parse(text_time, default=now).replace(tzinfo=SG_TZ)

    # Align parsed date to available mock forecast dates (workshop data is static).
    # If the runtime clock doesn't match the mock dataset's year, relative phrases like "tomorrow"
    # would otherwise point to dates that have no forecast points.
    try:
        data = load_forecast()
        avail = []
        for entries in data.values():
            for e in entries:
                ts = datetime.fromisoformat(e["ts"])
                avail.append(ts.date())
        avail_dates = sorted(set(avail))
        if avail_dates:
            parsed_date = dt.date()
            if parsed_date not in avail_dates:
                nearest = min(avail_dates, key=lambda d: abs((d - parsed_date).days))
                dt = dt.replace(year=nearest.year, month=nearest.month, day=nearest.day)
    except Exception:
        pass

    return snap_15(dt).isoformat()

@tool("parse_time", return_direct=False)
def parse_time_tool(text_time: str) -> str:
    """Parse user time to ISO string in Asia/Singapore, snapped to 15 minutes."""
    return _parse_time_iso(text_time)

def _recommend_best_for_day(day_key: str) -> dict:
    """Best (region, start time) on the given day ('today' or 'tomorrow') across all forecast points that day."""
    now = datetime.now(tz=SG_TZ)
    target_date = (now + timedelta(days=1 if day_key == "tomorrow" else 0)).date()
    p = load_profile()
    regions = p.get("regions_allowed", ["US_WEST"])
    shift = int(p.get("allowed_shift_minutes", 60))
    data = load_forecast()
    # Align to forecast dates if needed (same as _parse_time_iso)
    avail_dates = sorted(set(datetime.fromisoformat(e["ts"]).date() for entries in data.values() for e in entries))
    if avail_dates and target_date not in avail_dates:
        target_date = min(avail_dates, key=lambda d: abs((d - target_date).days))
    best = None  # (g, ts, region)
    for r in regions:
        for e in data.get(r.upper(), []):
            ts = datetime.fromisoformat(e["ts"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=SG_TZ)
            if ts.date() == target_date:
                cand = (int(e["g"]), ts, r.upper())
                if best is None or cand < best:
                    best = cand
    if best is None:
        return {
            "ok": False,
            "reason": "No points on that day",
            "start_iso": "",
            "desired_time_sg": datetime(target_date.year, target_date.month, target_date.day, tzinfo=SG_TZ).isoformat(),
            "window_start_sg": "",
            "window_end_sg": "",
            "allowed_shift_minutes": shift,
            "regions_allowed": [r.upper() for r in regions],
        }
    g, ts, region = best
    return {
        "ok": True,
        "region": region,
        "start_time_sg": ts.isoformat(),
        "g": g,
        "desired_time_sg": ts.isoformat(),
        "window_start_sg": "",
        "window_end_sg": "",
        "allowed_shift_minutes": shift,
        "regions_allowed": [r.upper() for r in regions],
        "shifted_minutes": 0,
    }


@tool("recommend_best_from_text", return_direct=False)
def recommend_best_from_text_tool(text_time: str) -> dict:
    """Recommend best (region, start time) from a natural-language time string (e.g. 'tomorrow 11:00', or just 'today' / 'tomorrow' for best slot on that day)."""
    raw = text_time.strip().lower()
    if raw in ("today", "tomorrow"):
        return _recommend_best_for_day(raw)
    start_iso = _parse_time_iso(text_time)
    return _recommend_best(start_iso)

def _recommend_best(start_iso: str) -> dict:
    """Given ISO start time (SG), pick best (region, ts) in +/- shift window.

    Kept as a plain function so other tools can call it internally.
    """
    p = load_profile()
    regions = p.get("regions_allowed", ["US_WEST"])
    shift = int(p.get("allowed_shift_minutes", 60))

    desired = datetime.fromisoformat(start_iso)  # already SG-aware from parse_time
    win_start = desired - timedelta(minutes=shift)
    win_end = desired + timedelta(minutes=shift)

    data = load_forecast()

    best = None  # (g, ts, region)
    for r in regions:
        for e in data.get(r.upper(), []):
            ts = datetime.fromisoformat(e["ts"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=SG_TZ)
            if win_start <= ts <= win_end:
                cand = (int(e["g"]), ts, r.upper())
                if best is None or cand < best:
                    best = cand

    if best is None:
        return {
            "ok": False,
            "reason": "No points in window",
            "start_iso": start_iso,
            "desired_time_sg": desired.isoformat(),
            "window_start_sg": win_start.isoformat(),
            "window_end_sg": win_end.isoformat(),
            "allowed_shift_minutes": shift,
            "regions_allowed": [r.upper() for r in regions],
        }

    g, ts, region = best
    return {
        "ok": True,
        "region": region,
        "start_time_sg": ts.isoformat(),
        "g": g,
        "desired_time_sg": desired.isoformat(),
        "window_start_sg": win_start.isoformat(),
        "window_end_sg": win_end.isoformat(),
        "allowed_shift_minutes": shift,
        "regions_allowed": [r.upper() for r in regions],
        "shifted_minutes": int(round((ts - desired).total_seconds() / 60.0)),
    }

@tool("recommend_best", return_direct=False)
def recommend_best_tool(start_iso: str) -> dict:
    """Given ISO start time (SG), pick best (region, ts) in +/- shift window."""
    return _recommend_best(start_iso)