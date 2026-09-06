# RoboLab

RoboLab is an Android-first engineering workspace for turning natural-language robotics ideas into structured projects, circuits, firmware and verification results.

## 48-agent engineering core

RoboLab now has a registry of 48 specialist model roles covering architecture, requirements, electronics, power, embedded firmware, Arduino, ESP32, STM32, Raspberry Pi, Python, Flutter, robotics, control, navigation, CAD, simulation, PCB, communications, security, reliability, testing, compilation, debugging and independent verification. Each slot can use the shared `AI_MODEL` or an optional `ROBOLAB_MODEL_<ROLE>` override.

The pipeline runs specialists concurrently, isolates individual failures, then sends the usable reports to a dedicated consensus synthesis stage. Outputs are explicitly marked as generated analysis; the system does not claim physical tests, simulations or successful compilation without external evidence.

## Premium / Pro beta

The Pro layer is wired into the backend and Android workspace. Current Pro capabilities include:

- Full 48-agent engineering review
- Consensus synthesis and specialist reports
- Advanced circuit/power-path validation
- Firmware review and debugging analysis
- CAD-ready mechanical specifications
- Simulation-ready test planning
- Project JSON export endpoint
- Priority-generation configuration

The beta can run with Pro enabled for everyone by setting `ROBOLAB_DEFAULT_PLAN=pro`. When real per-user authentication and billing are connected, change the default back to `free` and issue entitlements server-side.

Pricing configured for the beta product: **₹99/month** or **₹799/year**.

## Deployment

### Render backend

A `render.yaml` blueprint and production `Dockerfile` are included. The backend starts with:

`uvicorn main:app --app-dir backend --host 0.0.0.0 --port $PORT`

Required secret:

- `AI_API_KEY` — your provider key, stored only in Render environment settings

Important non-secret configuration:

- `AI_BASE_URL` — OpenAI-compatible API base URL
- `AI_MODEL` — shared fallback model
- `ROBOLAB_DEFAULT_PLAN=pro` for the free beta experience
- `ROBOLAB_AGENT_CONCURRENCY=8` as the safe starting concurrency

Health endpoints:

- `/healthz` — liveness
- `/readyz` — readiness/provider configuration
- `/api/status` — fleet and deployment status
- `/api/v1/plans` — public plan catalogue

### Android release

The GitHub Actions workflow validates Python and Flutter, creates the Android platform files when they are absent, runs Flutter analysis/tests, and builds both APK and AAB artifacts.

Add a GitHub Actions secret named `ROBOLAB_API_URL` containing the deployed backend origin before running the Android release workflow. The Android app reads it through the `ROBOLAB_API_URL` Dart define and automatically falls back to its local engine if the remote service is unavailable.

For Google Play production publishing, add a real Android signing key to the release pipeline before publishing the AAB. The workflow intentionally builds release artifacts but does not contain private signing material.

## Local development

Backend:

`pip install -r backend/requirements.txt`

`uvicorn main:app --app-dir backend --reload --port 8000`

Flutter:

`flutter pub get`

`flutter run`

For a deployed backend:

`flutter run --dart-define=ROBOLAB_API_URL=https://YOUR-BACKEND.example`

Never commit `.env` files, provider keys, Android keystores, or billing secrets.
