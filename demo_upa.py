#!/usr/bin/env python
"""
Run User Preference Agent in isolation.
"""

import argparse
import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime

from agents.user_preference.agent import UserPreferenceAgent
from models.schemas import PlanningContext


def _json_default(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _read_user_input(cli_text: str | None) -> str:
    if cli_text:
        return cli_text

    print("Enter travel requirements (type END on a new line to submit):")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run User Preference Agent only.")
    parser.add_argument(
        "--input",
        dest="user_input",
        default=None,
        help="Single-line travel requirement text. If omitted, interactive multi-line mode is used.",
    )
    args = parser.parse_args()

    user_input = _read_user_input(args.user_input)
    if not user_input:
        print("No input provided.")
        return 1

    context = PlanningContext()
    context.metadata["user_input"] = user_input

    result = UserPreferenceAgent().execute(context)

    output = {
        "errors": result.errors,
        "warnings": result.warnings,
        "travel_profile": asdict(result.travel_profile) if result.travel_profile else None,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
