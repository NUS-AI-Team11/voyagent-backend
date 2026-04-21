# Carbon-Aware Agent Workshop (Colab)

Agentic AI carbon-aware scheduler: recommend (region, start time) with lowest carbon intensity within user preferences.

---

## Issues and Solutions

### 1. Wrong or invented ISO timestamps

**Issue:** For inputs like "tomorrow 11:00, I prefer regions SG", the agent called `recommend_best` with a guessed ISO (e.g. `2023-11-10T11:00:00`), causing "No points in window" even when data existed.

**Solution:**
- Expose a single tool **`recommend_best_from_text(text_time)`** that accepts natural-language time (e.g. `"tomorrow 11:00"`).
- The tool internally parses time and runs the recommendation; the LLM never passes raw ISO strings for scheduling.
- System prompt instructs: use `recommend_best_from_text` with the user’s time text; do not invent dates or ISO.

**Files:** `solution/src/run_chat.py` (TOOLS, SYSTEM), `solution/src/tools.py` (`recommend_best_from_text_tool`, `_parse_time_iso`, `_recommend_best`).

---

### 2. `TypeError: 'StructuredTool' object is not callable`

**Issue:** Code called `parse_time_tool(...)` or `recommend_best_tool(...)` from inside another tool. After `@tool`, those names refer to `StructuredTool` instances, which are not callable like functions.

**Solution:** Move core logic into plain functions and keep tools as thin wrappers:
- **`_parse_time_iso(text_time)`** – returns ISO string; used by `parse_time_tool` and `recommend_best_from_text_tool`.
- **`_recommend_best(start_iso)`** – returns recommendation dict; used by `recommend_best_tool` and `recommend_best_from_text_tool`.

**File:** `solution/src/tools.py`.

---

### 3. "No points in window" for "tomorrow" on Colab

**Issue:** Mock data (`data/mock_forecast.json`) only has one date (e.g. 2026-03-11). Colab’s system date may differ, so "tomorrow" can resolve to a date with no forecast points.

**Solution:** In `_parse_time_iso`, after parsing, if the parsed date is not in the forecast’s date set, map it to the **nearest available date** in the dataset (keeping time-of-day). Relative phrases like "tomorrow 10am" then align to the mock data and return a valid recommendation.

**File:** `solution/src/tools.py` (`_parse_time_iso`).

---

### 4. Inconsistent Agent reply format

**Issue:** The final "Agent: ..." line should be one clear sentence (recommendation or "no options" + follow-up), not a 4-line table or varying wording.

**Solution:** In `run_chat.py`, when the last message is a `ToolMessage` from `recommend_best_from_text` or `recommend_best`, the assistant node **does not** call the LLM. It builds the final reply from the tool payload:
- **Success:** One sentence: region, start time (SG), carbon intensity (g), shifted minutes. No markdown bold.
- **Failure:** One sentence stating no options under current preferences and asking whether to expand regions or shift window.

**File:** `solution/src/run_chat.py` (`assistant` in `build_app`).

---

### 5. "Today" or "tomorrow" with no time returns no recommendation (parsed as 00:00)

**Issue:** When the user says "I want to schedule a job today, recommend me the best" (or "tomorrow" with no time), the parser treats the missing time as 00:00. The forecast data usually only has slots during the day (e.g. 09:00–12:00), so the ±shift window around midnight has no points and the agent replies "No points in window" instead of recommending the best slot on that day.

**Solution:** If the time string is exactly "today" or "tomorrow" (no time part), treat it as "best slot on that day": add `_recommend_best_for_day(day_key)` that finds the forecast point with minimum carbon intensity on that date across allowed regions, and call it from `recommend_best_from_text_tool` before parsing a single clock time. Date alignment to the mock forecast is reused so it works with static workshop data.

**File:** `solution/src/tools.py` (`_recommend_best_for_day`, `recommend_best_from_text_tool`).

---

## Colab usage

1. Upload and extract the project zip; set `BASE_DIR` and `OPENAI_API_KEY`.
2. `%cd` to the directory that contains `run_chat.py` (e.g. `.../solution/src`).
3. Reload after editing: `sys.modules.pop("tools", None); sys.modules.pop("run_chat", None); importlib.reload(tools); importlib.reload(run_chat)`.

If you see `ModuleNotFoundError: run_chat` or imports from the wrong `tools.py`, ensure the working directory is the `solution/src` that contains the updated code (e.g. use `find` to locate `run_chat.py` and `cd` there).
