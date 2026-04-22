"""
Shared helpers for LLM candidate validation and retry loops.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Tuple


ValidationResult = Tuple[bool, str]
GenerateFn = Callable[[Optional[str]], Any]
ValidateFn = Callable[[Any], ValidationResult]


def run_with_quality_gate(
    *,
    max_attempts: int,
    generate: GenerateFn,
    validate: ValidateFn,
) -> tuple[Any, dict[str, Any]]:
    """
    Generate model output with validation + bounded retries.

    Returns:
      - best_output: last output (or first passing output)
      - report: metadata for observability
    """
    attempts = max(1, int(max_attempts))
    last_output: Any = None
    last_reason = "not_attempted"
    checks: list[dict[str, Any]] = []

    feedback: Optional[str] = None
    for idx in range(1, attempts + 1):
        output = generate(feedback)
        last_output = output
        ok, reason = validate(output)
        checks.append({"attempt": idx, "ok": ok, "reason": reason})
        if ok:
            return output, {
                "attempts": idx,
                "passed": True,
                "checks": checks,
                "final_reason": reason,
            }
        last_reason = reason
        feedback = f"Previous output failed validation: {reason}. Regenerate a corrected response."

    return last_output, {
        "attempts": attempts,
        "passed": False,
        "checks": checks,
        "final_reason": last_reason,
    }

