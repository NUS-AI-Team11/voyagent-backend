
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import os, json
import re

from langchain_core.tools import tool
from zoneinfo import ZoneInfo
from dateutil import parser as dparser

from memory import (load_profile, save_profile)

DATA_FP = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "mock_forecast.json")

def snap_15(dt: datetime) -> datetime:
    dt = dt.replace(second=0, microsecond=0)
    minute = (dt.minute // 15) * 15
    return dt.replace(minute=minute)

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

@tool("parse_time", return_direct=False)
def parse_time_tool(text_time: str) -> str:
    """Parse user time to ISO string in Asia/Singapore, snapped to 15 minutes."""
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
        return snap_15(dt.replace(tzinfo=SG_TZ)).isoformat()

    dt = dparser.parse(text_time, default=now).replace(tzinfo=SG_TZ)
    return snap_15(dt).isoformat()
    # fallback: normal parsing (e.g., '4 Mar 2026 10am', '10am')
    dt = dparser.parse(text, default=now_sg)
    return ensure_sg(dt)

@tool("recommend_best", return_direct=False)
def recommend_best_tool(start_iso: str) -> dict:
    """Given ISO start time (SG), pick best (region, ts) in +/- shift window."""
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
        return {"ok": False, "reason": "No points in window", "start_iso": start_iso}

    g, ts, region = best
    return {"ok": True, "region": region, "start_time_sg": ts.isoformat(), "g": g, "allowed_shift_minutes": shift}

    g, ts, region = best
    return {
        "ok": True,
        "region": region,
        "start_time_sg": ts.isoformat(),
        "g": g,
        "desired_time_sg": desired.isoformat(),
        "window_start_sg": window_start.isoformat(),
        "window_end_sg": window_end.isoformat(),
        "allowed_shift_minutes": shift_min,
        "regions_allowed": regions,
    }