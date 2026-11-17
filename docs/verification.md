# Verification record

## Upload and usability update — 18 November 2026

- Production frontend build passed, with the upload and performance workspaces loaded on demand.
- **52 Python tests passed**, including 25 new upload tests. Coverage includes symbol/canonical CSV headers, raw NASA whitespace logs, TSV, multiple arbitrary engine IDs, later-starting cycle histories, exact agreement with existing model predictions, minimum history, malformed columns, missing/nonfinite/extreme values, cycle gaps, duplicates, byte limits, and unavailable-model behavior. Upload inference works independently of the built-in dataset cache.
- **14 desktop/mobile browser tests passed** in 17.5 seconds. New checks cover choosing a real sample file, actual upload-to-model prediction, named sensor charts, prediction export, short-log error and correction, stale-result clearing, performance matrix calculations, artifact-location guidance, and mobile layout.
- Visually inspected the desktop upload workspace and mobile performance report. A final mobile presentation adjustment presents the performance matrix as readable stacked rows rather than requiring a horizontal swipe.
- The model was loaded and inspected: XGBRegressor, 74 ordered features, version 1.0.0, 227,031-byte Joblib artifact. No retraining or artificial predictions were introduced.
- No new Python or JavaScript dependencies were required. The earlier dependency audit below has not been rerun during this update.

Development verification on 17 November 2026 used the supplied FD001 files, Python 3.10.11, Node 24.7.0, the saved XGBoost artifact, and a local FastAPI server serving the production frontend.

## Completed checks

- Python model/API suite: 27 tests passed. Covers dataset validation, causal features and future mutation checks, engine-aware split, official-label alignment, artifact reload, exact agreement between API and saved evaluation, nonnegative estimates, invalid inputs, observed history bounds, missing resources, configurable thresholds, CORS, inactive milling, and frontend serving.
- Frontend production build: passed. Engine and analytics workspaces are loaded on demand; initial JavaScript approximately 243 kB before gzip, with the chart bundle loaded separately.
- Browser suite: **8 tests passed** in 10.2 seconds across desktop Chromium at 1440 px and mobile Chromium using an iPhone 13 viewport. The primary flow requests the actual API and compares the rendered result with a direct request for the same engine/cycle. Browser tests also exercise sensor/cycle/engine changes, downloads, saved analytics, session history, request loading, error recovery, and mobile navigation. See `frontend/e2e/product.spec.js` for the scenarios.
- Desktop overview and mobile engine prediction screenshots were visually inspected. Charts, selectors, prediction results, and operating condition cards render within the viewport. Automated layout checks reject horizontal page overflow.
- Official test evaluation: MAE 12.4972 cycles, RMSE 17.0712 cycles, 100 engine endpoints. Pipeline median inference approximately 10.83 ms; API latency also checked below 500 ms after startup.

## Dependency checks and limitations

`npm audit --omit=dev` reported **zero runtime dependency findings**. The complete audit reported four linked high-severity development findings through `picomatch`, `fdir`, `tinyglobby`, and Vite, associated with GHSA-fc5q-39xc-vjpf. The registry’s latest `picomatch` at verification was 4.0.7 and the advisory covered that version. No patched upgrade was available in that dependency line. The static production frontend contains no Vite development server. Recheck before exposing a development server beyond localhost or changing dependencies.

The Python suite emits a dependency deprecation warning about FastAPI/Starlette’s httpx TestClient integration; the suite passes. Training Ridge on this platform produced NumPy BLAS runtime warnings despite finite predictions and valid validation scores; the selected runtime estimator is XGBoost. No warning was suppressed.

Browser tests cover automated acceptance scenarios, not five human participants. Human feedback remains pending in `docs/user-testing.md`. Milling has no supplied data, is visibly inactive, and its API returns 501. No external hosting or safety-critical deployment has been performed.
