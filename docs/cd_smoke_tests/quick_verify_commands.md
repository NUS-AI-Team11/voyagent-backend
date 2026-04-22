# CD Smoke Test Inputs

Use these commands after each deployment to verify your service quickly.

Replace the base URL with your deployed endpoint:

```bash
export BASE_URL="http://<your-server-ip-or-domain>"
```

PowerShell:

```powershell
$env:BASE_URL = "http://<your-server-ip-or-domain>"
```

## 1) Meta endpoints

```bash
curl "$BASE_URL/"
curl "$BASE_URL/api/v1/health"
curl "$BASE_URL/api/v1/version"
curl "$BASE_URL/api/v1/agents"
curl "$BASE_URL/api/v1/workflow/steps"
```

Expected:
- `/api/v1/health` returns `{"status":"ok"}`.
- `/api/v1/agents` returns 5 agents.
- `/api/v1/workflow/steps` returns ordered pipeline steps.

## 2) Plan endpoint (non-streaming)

```bash
curl -X POST "$BASE_URL/api/v1/plan" \
  -H "Content-Type: application/json" \
  --data @docs/cd_smoke_tests/payload_plan_basic.json
```

```bash
curl -X POST "$BASE_URL/api/v1/plan" \
  -H "Content-Type: application/json" \
  --data @docs/cd_smoke_tests/payload_plan_family.json
```

```bash
curl -X POST "$BASE_URL/api/v1/plan" \
  -H "Content-Type: application/json" \
  --data @docs/cd_smoke_tests/payload_plan_budget.json
```

Expected:
- Response contains `ok`, `errors`, and `metadata`.
- Usually `ok=true` and `errors=[]` when upstream model/API keys are valid.

## 3) Plan stream endpoint (SSE)

```bash
curl -N -X POST "$BASE_URL/api/v1/plan/stream" \
  -H "Content-Type: application/json" \
  --data @docs/cd_smoke_tests/payload_plan_basic.json
```

Expected event sequence:
- `step_running`
- `step_done` (repeated for steps)
- `complete` with full planning result

## 4) Failure-case input (optional)

Send an empty payload to confirm validation is active:

```bash
curl -X POST "$BASE_URL/api/v1/plan" \
  -H "Content-Type: application/json" \
  --data "{}"
```

Expected:
- HTTP `422 Unprocessable Entity`.
