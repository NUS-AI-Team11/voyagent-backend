# VoyageAgent HTTP API

Base URL: `/api/v1` (when served at server root). OpenAPI UI: `/docs`, ReDoc: `/redoc`.

## Meta

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service links (`api` prefix, `docs`). |
| GET | `/api/v1/health` | Liveness probe: `{ "status": "ok" }`. |
| GET | `/api/v1/version` | `{ app_name, app_version, api_version }` from env (`APP_NAME`, `APP_VERSION`). |

## Workflow (all agents)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/agents` | Lists all five agents: name, description, `step_index`, `output_field`. |
| GET | `/api/v1/workflow/steps` | Ordered pipeline steps (`travel_profile` → … → `final_handbook`) and logical `pipeline` keys. |

## Planning (full pipeline)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/plan` | Runs **User Preference → Spot → Dining → Route/Hotel → Cost** and returns the full structured result. |
| POST | `/api/v1/plan/stream` | Same pipeline; **Server-Sent Events** (`text/event-stream`). Each line is `data: {json}` (double newline between events). |

### `POST /api/v1/plan`

**Request body (JSON)**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `user_input` | string | required | Free-form travel requirements (same semantics as CLI). |
| `fail_fast` | boolean | `true` | Stop after the first workflow error. |
| `print_summary` | boolean | `false` | If `true`, also prints the CLI-style summary to **server** stdout. |

**Response (JSON)** — `ok` is `true` when `errors` is empty.

| Field | Description |
|-------|-------------|
| `travel_profile` | Output of User Preference Agent (nullable if failed early). |
| `spot_list` | Spot Recommendation Agent. |
| `dining_list` | Dining Recommendation Agent. |
| `itinerary` | Route & Hotel Planning Agent. |
| `final_handbook` | Cost Optimization Agent (full handbook). |
| `final_handbook_summary` | Short summary when handbook exists (budget, totals, `is_within_budget`). |
| `itinerary_narrative` | When `itinerary` exists, a plain-language multi-paragraph summary of `days` (for handbook UIs). |
| `errors`, `warnings` | Lists of strings. |
| `metadata` | Includes `workflow_elapsed_ms`, `workflow_steps`, `agent_runs`, etc. |

### `POST /api/v1/plan/stream`

Same request body as `POST /api/v1/plan`. Response is **not** JSON — it is **SSE**: repeated `data: <event_json>\n\n`.

Event `type` values:

| `type` | Fields | Meaning |
|--------|--------|---------|
| `step_running` | `step_index`, `label`, `output_field` | A pipeline step is starting (1-based index). |
| `step_done` | `step_index`, `label`, `output_field`, `error_count` | That step finished. |
| `complete` | `result` | Full `PlanResponse` object (same shape as non-streaming `/plan`). |
| `error` | `message` | Unrecoverable server-side failure before `complete`. |

## CORS

Optional: set `CORS_ORIGINS` to a comma-separated list of allowed origins (e.g. `http://localhost:5173`).

## Run the server

From the project root:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
