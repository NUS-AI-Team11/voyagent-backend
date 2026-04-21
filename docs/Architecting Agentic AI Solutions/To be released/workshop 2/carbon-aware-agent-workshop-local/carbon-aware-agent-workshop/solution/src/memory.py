import os, json

MEM_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "memory")
os.makedirs(MEM_DIR, exist_ok=True)
PROFILE_FP = os.path.join(MEM_DIR, "profile.json")

DEFAULT_PROFILE = {
    "regions_allowed": ["SG", "EU_WEST", "US_WEST"],
    "allowed_shift_minutes": 60
}

def _read_json(fp, default):
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                pass
    return default

def _write_json(fp, data):
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_profile():
    return _read_json(PROFILE_FP, DEFAULT_PROFILE.copy())

def save_profile(p):
    _write_json(PROFILE_FP, p)

def get_pref(name, default=None):
    p = load_profile()
    return p.get(name, default)

def set_pref(name, value):
    p = load_profile()
    p[name] = value
    save_profile(p)
    return p

def set_regions(regions):
    return set_pref("regions_allowed", regions)

def get_regions():
    return get_pref("regions_allowed", DEFAULT_PROFILE["regions_allowed"])

def set_allowed_shift(minutes):
    return set_pref("allowed_shift_minutes", int(minutes))

def get_allowed_shift():
    return int(get_pref("allowed_shift_minutes", DEFAULT_PROFILE["allowed_shift_minutes"]))
