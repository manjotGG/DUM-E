# DUM-E

**Predict failures. Prevent downtime.** A working predictive maintenance application with a React dashboard, FastAPI inference service, and a reproducible NASA C-MAPSS FD001 learning pipeline.

The UI reads the supplied dataset and requests predictions from the saved trained model. Sensor charts, engine selection, prediction cycles, metrics, downloads, and session history are connected to the backend. C-MAPSS contains NASA-generated simulated degradation trajectories; it is not telemetry collected from aircraft in flight.

## Run locally

Requires Python 3.10+ and Node 20.19+ or 22.12+ (tested with Python 3.10.11 and Node 24). On macOS, XGBoost also needs `brew install libomp`. Linux needs the OpenMP runtime (`libgomp1` on Debian/Ubuntu).

From the repository root:

```bash
bash scripts/setup.sh
bash scripts/start.sh
```

Open **http://127.0.0.1:8000** for the dashboard and **http://127.0.0.1:8000/docs** for interactive API documentation. FastAPI serves the built React app and API on the same origin. Stop with Ctrl+C. The setup installs dependencies and builds the frontend; a model is already included. If artifacts are absent, setup trains them.

For the environment already prepared in this workspace, only `bash scripts/start.sh` is needed.

## Dataset

The supplied `CMAPSSData/` contains all four C-MAPSS subsets. This release deliberately trains and serves **FD001 only**, as specified in [architecture.md](architecture.md).

| File | Purpose | Rows / engines |
| --- | --- | --- |
| `train_FD001.txt` | Complete training trajectories | 20,631 / 100 |
| `test_FD001.txt` | Partially observed test trajectories | 13,096 / 100 |
| `RUL_FD001.txt` | Official RUL at each test engine’s final observation | 100 labels |

Data discovery checks `data/engines/raw/`, then `CMAPSSData/`, then a sibling `CMAPSSData/`. Override with `CMAPSS_DATA_DIR`. Files remain in place; no generated replacements are used. Validation rejects wrong column counts, missing/nonfinite values, noninteger IDs, duplicate or unordered cycles, and misaligned labels.

## Training and evaluation

```bash
.venv/bin/python -m ml.engines.inspect_data
.venv/bin/python -m ml.engines.train
.venv/bin/python -m ml.engines.evaluate
```

The seeded pipeline reserves 20 complete training engines for validation. Three censored prefixes (35%, 55%, 75% of each held-out trajectory) provide 60 validation points. Candidate selection uses uncapped validation RMSE. The selected pipeline is refit on all 100 training engines, then evaluated once against the official, uncapped test RUL labels at each test engine’s final observed cycle. Test labels are never used for model selection.

Features include cycle, operating settings, 14 informative sensor channels, trailing 5/15-cycle means, trailing standard deviations, and 15-cycle changes. Every feature is causal and engine-local. Engine IDs are not predictors. Variance filtering and scaling are fitted within each training split and saved with the estimator.

Measured on the supplied files:

| Selected model | Official test MAE | Official test RMSE |
| --- | --- | --- |
| XGBoost, training RUL capped at 125 cycles | 12.50 cycles | 17.07 cycles |

Median feature generation plus inference was approximately 11 ms over 10 requests on this machine. Timing varies by hardware. The cap affects training targets; official evaluation labels remain uncapped. Outputs are clipped at zero and reported in cycles only. The application does not convert them to time. All candidate scores, per-engine test predictions, residual bins, error by RUL range, feature importances, seed, engine splits, and file hashes are saved in `ml/models/engines/metrics.json`. The full estimator and fitted preprocessing are in `model.joblib`. Only load trusted, locally generated artifacts.

Restart the backend after retraining so it loads the new artifact and report.

## API

| Method | Endpoint | Behavior |
| --- | --- | --- |
| GET | `/health` | Model and dataset readiness |
| GET | `/api/engines` | 100 test engine IDs, observed cycle counts, sensor channels |
| GET | `/api/engines/{id}/history?cycle=20` | Observations through the requested cycle only; optional cycle |
| POST | `/api/engines/predict` | `{"engine_id":1,"cycle":31}`; cycle optional, defaults to latest |
| GET | `/api/engines/metrics` | Saved training and evaluation results |
| POST | `/api/milling/predict` | Explicit 501 until milling is implemented |

```bash
curl -X POST http://127.0.0.1:8000/api/engines/predict \
  -H 'Content-Type: application/json' \
  -d '{"engine_id":1,"cycle":31}'
```

Engine 1 at cycle 31 produces approximately **125.67 cycles** with this artifact. The response includes model version, inference time, demo maintenance priority, and the configured thresholds. IDs are scoped to the test split. Cycles beyond observed history are rejected, and early-cycle estimates use only the available prefix. The inference service never reads the RUL labels; they appear only in evaluation analytics.

## Development and configuration

Run the backend in one terminal and Vite in another:

```bash
.venv/bin/python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
npm --prefix frontend run dev
```

Open http://127.0.0.1:5173; Vite proxies `/api`, `/health`, `/docs`, and `/openapi.json` to FastAPI. For a separately hosted frontend, set `VITE_API_BASE_URL` before building and explicitly configure `CORS_ORIGINS` in the backend.

Environment variables in [.env.example](.env.example) are optional. Load a configuration file with `uvicorn backend.main:app --env-file .env`. The start script uses shell environment variables; it does not load `.env` automatically.

| Variable | Default |
| --- | --- |
| `CMAPSS_DATA_DIR` | Automatic dataset discovery |
| `ENGINE_MODEL_DIR` | `ml/models/engines` |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` |
| `CRITICAL_RUL` | 30 cycles |
| `ELEVATED_RUL` | 60 cycles |

Priority is Critical below 30, Elevated from 30 to below 60, and Normal from 60 upward. These configurable UI rules are not validated maintenance thresholds. Session predictions remain in memory until refresh. Missing data/model errors are displayed and never replaced with made-up predictions.

## Verification

```bash
make test
cd frontend
npx playwright install chromium
npm run test:e2e
```

Python tests cover schema checks, target generation, label alignment, causal features, group separation, serialization, prediction/report agreement, inference latency, API validation, CORS, missing resources, and built frontend serving. Browser tests use the running API and actual model on desktop and mobile; they cover engine/sensor/cycle changes, prediction agreement, CSV/evaluation downloads, analytics, loading/errors, and session history. The browser test runner starts FastAPI if needed.

Dependency inputs are pinned in `backend/requirements.txt`, the complete Python environment in `backend/requirements.lock.txt`, and the JavaScript tree in `frontend/package-lock.json`. See [verification.md](docs/verification.md) for verification results and dependency audit limitations.

## Project layout

- `ml/engines/`: ingestion, feature generation, group validation, training, final evaluation.
- `ml/models/engines/`: saved pipeline and measured evaluation report.
- `backend/`: FastAPI routes, strict request schemas, cached dataset and loaded model service.
- `frontend/`: responsive React/Tailwind dashboard and Recharts visualizations.
- `tests/`, `frontend/e2e/`: model/API tests and browser integration tests.
- `scripts/`: repeatable setup and start commands.
- `docs/`: pipeline explanation, model card, verification and acceptance-test template.

## Release scope

The **Jet Engine MVP** is implemented. Milling remains inactive because no milling dataset was supplied. FD002–FD004 modeling, telemetry ingestion, uncertainty intervals, and certified maintenance guidance are outside this release. The five human acceptance tests and academic submission signatures must be completed by real participants; [user-testing.md](docs/user-testing.md) provides the protocol and blank records.

The original PRD mistakenly stored in `backend/requirements.txt` has been preserved in [docs/original-requirements.md](docs/original-requirements.md).

Dataset citation: A. Saxena, K. Goebel, D. Simon, and N. Eklund, “Damage Propagation Modeling for Aircraft Engine Run-to-Failure Simulation,” PHM 2008. See the supplied `CMAPSSData/readme.txt` and paper. [NASA dataset page](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data).
