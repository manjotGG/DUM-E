# DUM-E
# Product Requirements Document (PRD)

**Product Name:** DUM-E  
**Product Title:** Multi-Equipment Predictive Maintenance & Remaining Useful Life Intelligence Platform  
**Tagline:** Predict Failures. Prevent Downtime.  
**Document Version:** 2.0  
**Date:** 17 November 2026  
**Status:** Development Specification  
**Team:** Power Rangers  
**Institution:** IILM University, Gurugram  
**Course:** Applied Machine Learning Lab (CSE2512P)  
**Allocated Track:** Track 4 — Functional MVP  
**Primary Release:** NASA C-MAPSS Jet Engine RUL Prediction  
**Secondary Release:** NASA Milling Tool Wear Prediction  
**Development Stack:** Python, Scikit-learn, XGBoost, FastAPI, React, Tailwind CSS

---

# 1. Executive Summary

DUM-E is a modular, AI-powered predictive maintenance platform designed to analyze equipment operating conditions, estimate degradation, and support maintenance planning through machine learning.

The platform will initially support two equipment categories:

1. **Jet Engines:** Remaining Useful Life (RUL) prediction using NASA's C-MAPSS turbofan engine degradation dataset.
2. **Milling Machines:** Cutting-tool wear estimation using experimental milling data available through NASA's Prognostics Data Repository.

DUM-E will use independent machine learning models for each equipment category while providing a unified web application for prediction, visualization, analytics, and maintenance insights.

The first development milestone focuses exclusively on the Jet Engine module using the FD001 subset of NASA C-MAPSS.

The system will allow users to select an engine, examine its operating history, visualize sensor measurements, and estimate its remaining operational cycles before simulated failure.

The application will consist of:

- A React-based interactive dashboard.
- A FastAPI backend.
- A machine learning inference engine.
- Reproducible model training pipelines.
- Sensor data visualization.
- Remaining Useful Life predictions.
- Model evaluation and comparison.
- Configurable maintenance priority indicators.
- Modular support for additional equipment models.

DUM-E is intended as an academic and portfolio demonstration. It is not designed or certified for actual aircraft maintenance decisions.

---

# 2. Product Vision

## 2.1 Vision Statement

To develop a modular machine intelligence platform capable of estimating equipment degradation and presenting actionable maintenance insights through accessible machine learning applications.

## 2.2 Mission

DUM-E aims to demonstrate how machine learning can transform historical equipment sensor data into useful predictions about machine health.

The platform will emphasize:

- Predictive analytics.
- Reproducible machine learning.
- Explainable predictions.
- Modular software architecture.
- Data-driven maintenance insights.
- Accessible user experience.

## 2.3 Product Positioning

DUM-E is a research-oriented predictive maintenance prototype.

Unlike a conventional ML notebook, DUM-E will integrate model training, inference, API development, and frontend visualization into a working application.

Unlike a real industrial monitoring system, the initial version will not collect live equipment telemetry or make operational maintenance decisions.

## 2.4 Key Differentiator

The central architectural feature of DUM-E is its modular approach to equipment-specific predictive maintenance.

Different machine types require different data processing methods, prediction targets, and evaluation strategies.

DUM-E will support these differences through independent ML pipelines and a shared application interface.

---

# 3. Problem Statement

Industrial and mechanical systems experience degradation through repeated operation.

Equipment degradation can result in:

- Unexpected failures.
- Unplanned downtime.
- Increased maintenance expenses.
- Reduced equipment availability.
- Inefficient maintenance schedules.
- Operational disruption.

Traditional maintenance approaches commonly include:

### Reactive Maintenance

Equipment is repaired after a failure occurs.

### Preventive Maintenance

Equipment is serviced according to predefined schedules or usage intervals.

### Predictive Maintenance

Equipment condition data is analyzed to estimate degradation and support maintenance decisions.

DUM-E focuses on predictive maintenance.

For the Jet Engine module, the system will estimate Remaining Useful Life based on historical sensor readings and operating conditions.

For the Milling module, the system will estimate cutting-tool wear using experimental machining data.

---

# 4. Product Goals and Success Metrics

## 4.1 Primary Goals

**G-01:** Develop a working Jet Engine RUL prediction model.

**G-02:** Implement a reproducible preprocessing and training pipeline.

**G-03:** Expose the trained model through FastAPI.

**G-04:** Build a functional React dashboard.

**G-05:** Visualize engine operating histories and sensor measurements.

**G-06:** Evaluate predictions using appropriate regression metrics.

**G-07:** Support independent equipment-specific prediction modules.

**G-08:** Document the complete development process.

**G-09:** Complete at least five user tests.

**G-10:** Produce a portfolio-quality project with documented limitations.

## 4.2 Measurable Success Criteria

| Metric | Target |
|---|---|
| Dataset loading | 100% successful for supported FD001 files |
| Model training | Reproducible training pipeline |
| Prediction endpoint | Returns valid RUL estimate |
| Model evaluation | MAE and RMSE reported |
| API validation | Rejects malformed input |
| UI integration | Successful end-to-end prediction |
| Sensor visualization | Displays selected engine history |
| Inference latency | Target below 500 ms after model loading |
| User testing | Minimum five participants |
| Documentation | Setup, training, API and evaluation instructions |
| Model accuracy | Determined experimentally, not predetermined |

The project must not fabricate performance results or claim unsupported prediction accuracy.

---

# 5. Scope Definition

## 5.1 Phase 1 — Jet Engine MVP

The initial release will include:

- NASA C-MAPSS FD001 data ingestion.
- Engine operating history processing.
- RUL target generation.
- Feature engineering.
- Regression model training.
- Model comparison.
- Saved model inference.
- FastAPI endpoints.
- React dashboard.
- Engine selection.
- Sensor visualization.
- RUL prediction.
- Maintenance priority indicator.
- Model performance analytics.
- Basic automated testing.

## 5.2 Phase 2 — Milling Integration

The second release will include:

- NASA Milling Wear data ingestion.
- Experimental sensor data preprocessing.
- Cutting-tool wear prediction.
- Independent milling model.
- Milling prediction API.
- Milling dashboard.
- Shared navigation and analytics.

## 5.3 Phase 3 — Product Enhancement

Optional enhancements:

- SHAP explanations.
- Batch prediction.
- Model uncertainty visualization.
- Prediction history.
- Advanced charts.
- Docker deployment.
- Additional NASA datasets.

## 5.4 Out of Scope

The initial release will not include:

- Live aircraft engine connections.
- Real-time IoT sensor ingestion.
- Actual aircraft maintenance recommendations.
- Automated equipment shutdown.
- Safety-critical decision automation.
- Enterprise user authentication.
- Commercial fleet management.
- Certified Remaining Useful Life predictions.
- Production industrial deployment.

---

# 6. Target Users

## 6.1 Maintenance Engineer

**Objective:** Understand equipment condition and potential degradation.

**Expected actions:**

- Select an engine.
- Inspect sensor readings.
- Request RUL estimation.
- Review maintenance priority.
- Compare operating conditions.

## 6.2 Operations Analyst

**Objective:** Examine equipment health trends.

**Expected actions:**

- Review engine histories.
- Compare predictions.
- Explore degradation patterns.
- Analyze model outputs.

## 6.3 ML Researcher or Student

**Objective:** Study predictive maintenance modeling.

**Expected actions:**

- Examine model evaluation results.
- Compare regression algorithms.
- Review feature engineering methods.
- Understand prediction limitations.

## 6.4 Academic Evaluator

**Objective:** Verify project functionality and ML implementation.

**Expected actions:**

- Run the application.
- Test inference endpoints.
- Review training methodology.
- Inspect evaluation results.
- Verify reproducibility.

---

# 7. Dataset Specifications

## 7.1 Primary Dataset: NASA C-MAPSS

**Full Name:** Commercial Modular Aero-Propulsion System Simulation

**Dataset:** Turbofan Engine Degradation Simulation Data Set

**Source:** NASA Prognostics Center of Excellence

**Initial Subset:** FD001

**Official Dataset Page:**  
https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data

### Dataset Characteristics

FD001 contains:

- 100 training engine trajectories.
- 100 testing engine trajectories.
- One operating-condition regime.
- One fault-mode category.
- Three operational setting variables.
- Twenty-one sensor measurement variables.
- Engine operating cycle information.
- Official RUL labels for test trajectories.

The data is generated using an engine simulation.

It must not be described as sensor data collected from actual aircraft in flight.

## 7.2 Required Dataset Files

The system must support:

**train_FD001.txt**

Contains complete simulated run-to-failure trajectories for training engines.

**test_FD001.txt**

Contains partially observed engine trajectories for testing.

**RUL_FD001.txt**

Contains remaining useful life labels corresponding to the final observed cycle of each test engine.

## 7.3 Dataset Schema

Each training and test row contains 26 fields.

| Field | Description |
|---|---|
| engine_id | Engine identifier |
| cycle | Operational cycle number |
| setting_1 | Operational setting 1 |
| setting_2 | Operational setting 2 |
| setting_3 | Operational setting 3 |
| sensor_1 | Sensor measurement 1 |
| sensor_2 | Sensor measurement 2 |
| ... | ... |
| sensor_21 | Sensor measurement 21 |

The model must not use `engine_id` as an ordinary numerical predictor.

Engine identifiers are used for grouping, history retrieval, validation, and data organization.

## 7.4 RUL Target Generation

For each complete training trajectory:

**RUL = Maximum Cycle for Engine − Current Cycle**

Example:

An engine reaches its simulated failure point at cycle 200.

At cycle 150:

RUL = 200 − 150 = 50 cycles.

At cycle 199:

RUL = 1 cycle.

At cycle 200:

RUL = 0 cycles.

The model may use a capped RUL target during training if experiments demonstrate that this approach is appropriate.

Any RUL capping threshold must be documented.

## 7.5 Test Dataset Handling

NASA's test trajectories do not necessarily continue until failure.

The official RUL file provides remaining cycles at the last observed point of each test trajectory.

The evaluation pipeline must:

1. Read the test trajectories.
2. Identify the last observed cycle for each test engine.
3. Generate the required model features.
4. Predict RUL at that point.
5. Compare predictions against official RUL labels.

If the application displays historical RUL estimates for intermediate test cycles, those values must be identified as model estimates rather than official ground-truth labels.

---

# 8. Machine Learning Requirements

## 8.1 ML Task

**Primary Task:** Supervised Regression

**Input:** Engine operating history and sensor-derived features.

**Output:** Estimated Remaining Useful Life in operational cycles.

## 8.2 Data Preprocessing

The preprocessing module must:

- Load raw FD001 files.
- Assign column names.
- Validate expected column counts.
- Validate engine IDs.
- Validate operational cycles.
- Identify missing values.
- Inspect sensor distributions.
- Identify constant or low-information features.
- Handle invalid numerical values.
- Prepare training features.
- Generate RUL labels.
- Preserve engine grouping.

All fitted preprocessing transformations must be learned from training data only.

## 8.3 Feature Engineering

The initial model will use sensor-based features.

Potential features include:

### Current Sensor Measurements

- Latest sensor values.
- Current operating settings.
- Current operational cycle.

### Rolling Statistics

For selected sensor channels:

- Rolling mean.
- Rolling standard deviation.
- Rolling minimum.
- Rolling maximum.

### Trend Features

- Change from earlier observations.
- Rolling sensor differences.
- Short-window degradation trends.

### History Length

- Number of observed cycles.
- Current cycle index.

Rolling features must be calculated using only observations available at or before the prediction cycle.

No future sensor values may be used.

## 8.4 Validation Strategy

Validation must be performed by engine.

A random row-level split is prohibited because measurements from the same engine are strongly related.

The system must use a group-aware split such that validation engines are separate from training engines.

NASA's official test dataset must remain reserved for final evaluation.

## 8.5 Model Candidates

### Baseline Model

A simple regression baseline will be implemented to establish reference performance.

Possible approaches:

- Constant RUL baseline.
- Linear regression.
- Ridge regression.

### Random Forest Regressor

Used to model nonlinear relationships between sensor measurements and remaining useful life.

### XGBoost Regressor

Used as the primary gradient-boosted regression candidate.

The final model will be selected based on validation results.

## 8.6 Evaluation Metrics

### Mean Absolute Error

Measures average absolute difference between predicted and actual RUL.

MAE = Mean(|Actual RUL − Predicted RUL|)

### Root Mean Squared Error

Penalizes larger prediction errors more heavily.

RMSE = sqrt(Mean((Actual RUL − Predicted RUL)²))

### Additional Analysis

The evaluation report should include:

- Actual versus predicted RUL.
- Prediction error distribution.
- Error by RUL range.
- Model comparison table.
- Feature importance where supported.
- Inference latency.

### Prediction Constraints

RUL predictions must be presented in cycles.

Negative predictions should be handled using a documented nonnegative output policy.

The system must not automatically convert cycles into hours, days, or flight time.

## 8.7 Model Artifact Requirements

Saved model artifacts must include:

- Trained estimator.
- Fitted preprocessing pipeline.
- Required feature names.
- Feature ordering.
- Model version.
- Relevant training configuration.

The application must use the same feature generation logic during training and inference.

---

# 9. System Architecture

## 9.1 Architectural Overview

DUM-E will use a modular full-stack architecture.

### Frontend Layer

React application responsible for:

- Navigation.
- Engine selection.
- Sensor visualization.
- Prediction requests.
- Prediction results.
- Model analytics.

### Backend Layer

FastAPI application responsible for:

- API routing.
- Input validation.
- Dataset history retrieval.
- Model inference.
- Response formatting.
- Error handling.

### Machine Learning Layer

Python modules responsible for:

- Dataset processing.
- Feature engineering.
- Model training.
- Model evaluation.
- Model serialization.

### Data Layer

Local public dataset files and saved model artifacts.

## 9.2 Architecture Flow

```text
                  DUM-E
          React Web Dashboard
                    |
                    v
             FastAPI Backend
                    |
          +---------+---------+
          |                   |
          v                   v
    Jet Engine API       Milling API
          |                   |
          v                   v
    RUL Predictor       Wear Predictor
          |                   |
          v                   v
    C-MAPSS Model       Milling Model
          |                   |
          +---------+---------+
                    |
                    v
         Prediction + Analytics
```

The Jet Engine module will be implemented first.

The Milling module will remain inactive until its own training and evaluation pipeline is ready.

---

# 10. Repository Architecture

The existing repository will be extended rather than replaced.

```text
DUM-E/
│
├── backend/
│   ├── main.py
│   ├── predictor.py
│   ├── schemas.py
│   ├── requirements.txt
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── engines.py
│   │   └── milling.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── engine_predictor.py
│       └── milling_predictor.py
│
├── ml/
│   ├── train.py
│   ├── evaluate.py
│   │
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── inspect_data.py
│   │   ├── preprocess.py
│   │   ├── train.py
│   │   └── evaluate.py
│   │
│   ├── milling/
│   │   ├── __init__.py
│   │   ├── preprocess.py
│   │   └── train.py
│   │
│   └── models/
│       ├── engines/
│       └── milling/
│
├── data/
│   ├── engines/
│   │   └── raw/
│   │       ├── train_FD001.txt
│   │       ├── test_FD001.txt
│   │       └── RUL_FD001.txt
│   │
│   └── milling/
│       └── raw/
│
├── frontend/
│   ├── package.json
│   ├── index.html
│   │
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       │
│       ├── components/
│       │
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── JetEngines.jsx
│       │   ├── Milling.jsx
│       │   └── Analytics.jsx
│       │
│       └── services/
│           └── api.js
│
├── tests/
│   ├── test_api.py
│   └── test_engine_model.py
│
├── docs/
│   └── PRD.md
│
├── README.md
├── .gitignore
└── .env.example
```

## 10.1 Module Responsibilities

**backend/main.py**

Creates the FastAPI application, configures CORS, and registers API routers.

**backend/schemas.py**

Defines shared Pydantic request and response schemas.

**backend/predictor.py**

Provides shared prediction interfaces or model-loading utilities.

**backend/routes/engines.py**

Implements Jet Engine API endpoints.

**backend/services/engine_predictor.py**

Loads the trained RUL model and performs inference.

**ml/engines/inspect_data.py**

Validates and summarizes the NASA dataset.

**ml/engines/preprocess.py**

Implements engine feature engineering and preprocessing.

**ml/engines/train.py**

Trains candidate RUL regression models.

**ml/engines/evaluate.py**

Evaluates trained models and exports metrics.

**frontend/src/pages/JetEngines.jsx**

Provides the Jet Engine monitoring and prediction interface.

---

# 11. Backend API Requirements

## 11.1 GET /health

**Purpose:** Verify application health.

Expected response:

```json
{
  "status": "healthy",
  "engine_model_loaded": true,
  "milling_model_loaded": false
}
```

## 11.2 GET /api/engines

**Purpose:** Return available demonstration engines.

Expected response:

```json
{
  "engines": [
    {
      "engine_id": 1,
      "available_cycles": 31
    }
  ]
}
```

Values are illustrative.

## 11.3 GET /api/engines/{engine_id}/history

**Purpose:** Retrieve a selected engine's available operating history.

The response must contain:

- Engine ID.
- Cycle values.
- Operating settings.
- Sensor measurements.
- Latest available cycle.

The endpoint must not expose unobserved future data.

## 11.4 POST /api/engines/predict

**Purpose:** Predict Remaining Useful Life.

For the first MVP, the API should support selecting a demonstration engine and prediction cycle.

Example request:

```json
{
  "engine_id": 1,
  "cycle": 31
}
```

The backend will retrieve the engine history up to the requested cycle and generate the required model features.

The endpoint must not allow prediction cycles beyond the available observed history.

Example response:

```json
{
  "engine_id": 1,
  "current_cycle": 31,
  "predicted_rul": 86.4,
  "rul_unit": "cycles",
  "maintenance_priority": "Normal",
  "model_version": "1.0.0"
}
```

These values are illustrative.

## 11.5 GET /api/engines/metrics

**Purpose:** Return saved evaluation results.

Example response:

```json
{
  "model_name": "XGBoost Regressor",
  "mae": null,
  "rmse": null,
  "evaluation_status": "pending"
}
```

Actual numerical values must be populated only after evaluation.

## 11.6 POST /api/milling/predict

**Purpose:** Estimate cutting-tool wear.

This endpoint will be implemented in Phase 2 after the milling dataset schema has been validated.

---

# 12. Frontend Requirements

## 12.1 Design Direction

DUM-E should have a modern industrial analytics appearance.

Suggested visual characteristics:

- Dark dashboard theme.
- Clear typography.
- Blue or cyan accents.
- Sensor trend charts.
- Compact metric cards.
- Responsive navigation.
- Clear warning states.
- Minimal visual clutter.

The interface must remain usable on smaller screens.

## 12.2 Dashboard Page

The dashboard must display:

- DUM-E branding.
- Equipment module selection.
- Available models.
- Current prediction summary.
- Recent session predictions.
- Quick navigation to engine analytics.

The application must not invent live fleet statistics.

## 12.3 Jet Engine Page

### Engine Selector

Users can select an engine from the available demonstration dataset.

### Engine Information

Display:

- Engine ID.
- Latest observed cycle.
- Number of available observations.
- Dataset subset.

### Sensor Visualization

Display line charts of selected sensor measurements against operational cycles.

Users should be able to select different sensor channels.

### RUL Prediction Panel

Display:

- Predicted remaining cycles.
- Current observed cycle.
- Maintenance priority.
- Model version.
- Prediction limitations.

### Maintenance Priority

Suggested demonstration thresholds:

- Critical: predicted RUL below 30 cycles.
- Elevated: predicted RUL from 30 to below 60 cycles.
- Normal: predicted RUL of 60 cycles or more.

These thresholds are provisional UI rules, not validated aviation maintenance limits.

They must be configurable and clearly labeled.

## 12.4 Analytics Page

Display:

- Model comparison table.
- MAE.
- RMSE.
- Actual versus predicted RUL plot.
- Prediction error distribution.
- Feature importance.

The page must use saved evaluation outputs rather than fabricated statistics.

## 12.5 Milling Page

Until Phase 2 is complete, the Milling page may display:

"Module under development."

It must not display invented predictions or claim that the model is operational.

---

# 13. User Experience Flows

## 13.1 Primary Prediction Flow

1. User opens DUM-E.
2. User selects Jet Engine Intelligence.
3. Application loads available engine IDs.
4. User selects an engine.
5. Application displays the observed engine history.
6. User selects an available cycle.
7. User clicks Predict Remaining Useful Life.
8. Frontend sends a prediction request.
9. FastAPI retrieves valid historical measurements.
10. The feature engineering pipeline processes the history.
11. The trained model predicts RUL.
12. Backend returns the result.
13. Frontend displays estimated remaining cycles and maintenance priority.

## 13.2 Error Flow

If the model is unavailable:

- Show a model-unavailable message.
- Do not generate placeholder predictions.
- Provide a clear retry or troubleshooting instruction.

If the selected engine is invalid:

- Return a validation error.
- Display an understandable message.

If the selected cycle is unavailable:

- Reject the request.
- Display the available cycle range.

---

# 14. Non-Functional Requirements

## 14.1 Performance

- Target inference latency below 500 milliseconds for supported single-engine requests after model loading.
- Model loading should occur during backend startup.
- Engine history requests should avoid unnecessary repeated file parsing.
- Frontend charts should remain responsive for supported dataset sizes.

## 14.2 Reliability

- Handle missing model files.
- Validate all API inputs.
- Reject invalid engine identifiers.
- Reject unavailable cycles.
- Prevent malformed data from reaching the model.
- Return consistent JSON responses.

## 14.3 Security

- Do not execute uploaded files.
- Restrict CORS to configured frontend origins.
- Validate input types.
- Avoid exposing local filesystem paths in API errors.
- Do not commit credentials or secrets.

## 14.4 Reproducibility

- Document Python dependencies.
- Document dataset sources.
- Use fixed random seeds where appropriate.
- Save training configuration.
- Preserve evaluation outputs.
- Provide commands to reproduce model training.

## 14.5 Maintainability

- Separate backend routes from prediction services.
- Separate training logic from inference.
- Reuse preprocessing functions.
- Keep equipment-specific models independent.
- Use consistent API response formats.

---

# 15. Testing Strategy

## 15.1 Dataset Tests

Verify:

- Correct column count.
- Valid engine identifiers.
- Correct cycle ordering.
- Correct RUL label generation.
- No unexpected missing values.
- Proper official test-label alignment.

## 15.2 ML Tests

Verify:

- No engine overlap between training and validation groups.
- No future-data leakage in rolling features.
- Correct feature ordering.
- Successful model serialization.
- Successful model loading.
- Nonnegative RUL outputs.
- Valid evaluation metrics.

## 15.3 API Tests

Test:

- Health endpoint.
- Available engine listing.
- Valid engine history request.
- Invalid engine identifier.
- Valid prediction request.
- Invalid cycle.
- Missing request fields.
- Model unavailable state.

## 15.4 Frontend Tests

Test:

- Dashboard rendering.
- Engine selection.
- Sensor chart updates.
- Prediction request.
- Loading indicator.
- Prediction display.
- Error messages.
- Responsive layout.

## 15.5 User Acceptance Testing

At least five users must test the application.

Suggested user tasks:

1. Open the dashboard.
2. Select a jet engine.
3. View sensor history.
4. Request an RUL prediction.
5. Interpret the prediction result.

Record:

- Participant identifier.
- Task completion status.
- Time required.
- Problems encountered.
- User feedback.
- Improvements made.

---

# 16. Development Roadmap

## Sprint 1 — Repository and Data Setup

**Estimated time:** 2–3 hours

Tasks:

- Organize repository.
- Create Jet Engine module folders.
- Download NASA FD001.
- Inspect dataset.
- Validate data schema.
- Document dataset characteristics.

**Deliverable:** Verified data-loading pipeline.

## Sprint 2 — ML Training

**Estimated time:** 4–6 hours

Tasks:

- Generate RUL targets.
- Implement preprocessing.
- Create group-aware validation split.
- Train baseline.
- Train Random Forest.
- Train XGBoost.
- Compare models.
- Save selected model.

**Deliverable:** Trained RUL prediction model.

## Sprint 3 — FastAPI Backend

**Estimated time:** 3–4 hours

Tasks:

- Configure FastAPI.
- Implement model loading.
- Create engine listing endpoint.
- Create engine history endpoint.
- Create prediction endpoint.
- Implement request validation.
- Test API responses.

**Deliverable:** Functional RUL inference API.

## Sprint 4 — React Frontend

**Estimated time:** 4–6 hours

Tasks:

- Initialize React application.
- Configure Tailwind CSS.
- Create navigation.
- Build engine selector.
- Build sensor charts.
- Create prediction panel.
- Connect backend endpoints.
- Handle loading and errors.

**Deliverable:** Functional DUM-E Jet Engine dashboard.

## Sprint 5 — Integration and Quality

**Estimated time:** 3–5 hours

Tasks:

- Run end-to-end tests.
- Verify predictions.
- Fix integration bugs.
- Add analytics.
- Measure latency.
- Improve UI.
- Document setup.

**Deliverable:** Demonstrable Jet Engine MVP.

## Sprint 6 — Milling Module

**Estimated time:** 2–3 additional focused days

Tasks:

- Inspect milling data.
- Engineer machining features.
- Train wear regression model.
- Evaluate model.
- Create milling API.
- Build milling dashboard.
- Integrate shared navigation.

**Deliverable:** Dual-equipment predictive maintenance platform.

## Sprint 7 — Academic Submission

Tasks:

- Complete five user tests.
- Prepare IEEE-style report.
- Include dataset citations.
- Complete AI-use declaration.
- Prepare signed contribution table.
- Record project demonstration.
- Finalize GitHub repository.

**Deliverable:** Academic submission package.

All time estimates assume focused development and may change depending on debugging and model experimentation.

---

# 17. Team Responsibilities

## Manjot Singh — Backend and System Integration

Responsibilities:

- FastAPI architecture.
- API development.
- Model loading and inference integration.
- Frontend/backend integration.
- Final system testing.
- Deployment preparation.

## Arnav Sharma — Machine Learning Development

Responsibilities:

- Dataset exploration.
- RUL target generation.
- Feature engineering.
- Model training.
- Hyperparameter experiments.

## Manveer Singh — Frontend Development

Responsibilities:

- React dashboard.
- Tailwind styling.
- Sensor charts.
- Engine selection interface.
- API integration.
- Responsive design.

## Krishna Ghosh — Evaluation and Documentation

Responsibilities:

- Model evaluation.
- Regression metrics.
- API testing.
- User testing.
- Technical documentation.
- Academic report preparation.

All members should contribute through GitHub commits and understand the complete system.

---

# 18. Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Data leakage | Invalid model evaluation | Group-aware splitting and causal feature engineering |
| Poor RUL accuracy | Weak prediction usefulness | Baseline comparison and feature improvement |
| Model overfitting | Poor generalization | Validation and controlled tuning |
| Dataset misunderstanding | Incorrect results | Dataset inspection and documentation |
| API integration errors | Broken application | Contract testing and modular architecture |
| Frontend complexity | Development delays | Build core MVP before enhancements |
| Limited development time | Incomplete submission | Prioritize Jet Engine module |
| Synthetic data limitations | Overstated real-world applicability | Explicitly disclose simulation origin |
| Incomplete user testing | Academic requirement failure | Reserve time for five documented tests |

---

# 19. Academic Requirements

DUM-E is intended for Track 4 — Functional MVP.

The team must confirm approval of the revised topic with the course coordinator.

## M1 — 5 Marks

One-page proposal including:

- Project title.
- Problem statement.
- Selected track.
- Dataset.
- Proposed methodology.
- Team responsibilities.
- Development plan.

## M2 — 10 Marks

Mid-project checkpoint including:

- GitHub repository or working draft.
- Half-page progress note.
- Evidence of implementation.

## M3 — 35 Marks

Final submission including:

- Functional application.
- Runnable package.
- IEEE-style report.
- Model evaluation.
- Testing evidence.
- AI-use declaration.
- Signed contribution table.

All reused datasets, research papers, libraries, and code must be appropriately cited.

---

# 20. Definition of Done

## Jet Engine MVP Completion

The Jet Engine MVP is complete when:

- NASA FD001 loads correctly.
- RUL targets are generated correctly.
- A regression model is trained.
- Model evaluation is documented.
- The model is saved and reloaded successfully.
- FastAPI provides working prediction endpoints.
- React displays engine sensor histories.
- Users can request RUL predictions.
- Predictions come from the actual trained model.
- API errors are handled correctly.
- Local setup instructions are documented.

## Full Platform Completion

The full DUM-E platform is complete when:

- Jet Engine RUL prediction works.
- Milling tool wear prediction works.
- Both models use independent pipelines.
- Both modules are accessible through one dashboard.
- Model metrics are available.
- API and frontend tests pass.
- Five user tests are documented.
- Final report and contribution records are complete.

---

# 21. Future Roadmap

Potential future development includes:

- Additional C-MAPSS subsets (FD002, FD003, FD004).
- LSTM-based RUL prediction.
- Transformer-based sensor sequence modeling.
- Prediction intervals and uncertainty estimation.
- Time-series anomaly detection.
- Fleet-level health comparison.
- PostgreSQL prediction history.
- Real-time sensor ingestion.
- Model drift monitoring.
- Automated retraining pipelines.
- Containerized deployment.
- Maintenance planning workflows.

These enhancements are not required for the initial MVP.

---

# 22. Final Product Deliverables

The final DUM-E project should include:

1. Complete GitHub repository.
2. Documented dataset preparation.
3. Reproducible ML training scripts.
4. Saved trained models.
5. Model evaluation results.
6. Functional FastAPI backend.
7. React dashboard.
8. Engine history visualization.
9. RUL prediction functionality.
10. Milling wear module after Phase 2.
11. Automated tests.
12. User testing evidence.
13. README and setup instructions.
14. IEEE-style academic report.
15. AI-use declaration.
16. Signed contribution table.

---

# 23. Final Product Statement

**DUM-E — AI-Powered Multi-Equipment Predictive Maintenance Platform**

DUM-E is a modular machine learning system that combines Remaining Useful Life estimation, industrial sensor analytics, and cutting-tool wear prediction within a unified full-stack application.

Its initial implementation focuses on NASA C-MAPSS Jet Engine RUL estimation, with subsequent expansion into experimental milling wear analysis.

The platform demonstrates practical skills in:

- Machine learning engineering.
- Time-series feature engineering.
- Regression modeling.
- Predictive maintenance.
- Backend API development.
- Full-stack integration.
- Model evaluation.
- Data visualization.
- Software testing.
- Reproducible ML deployment.

**DUM-E — Predict Failures. Prevent Downtime.**

**End of Product Requirements Document — Version 2.0**