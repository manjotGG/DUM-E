# Connected pipeline

```mermaid
flowchart LR
    A[Supplied FD001 training files] --> B[Strict schema validation]
    B --> C[Causal per-engine features]
    C --> D[80 training / 20 validation engines]
    D --> E[Fit candidate preprocessing and estimators]
    E --> F[Select by uncapped validation RMSE]
    F --> G[Refit on all 100 training engines]
    G --> H[Saved pipeline and feature order]
    H --> I[Final official test evaluation]
    I --> J[metrics.json]
    H --> K[FastAPI startup model cache]
    L[Observed test histories] --> M[FastAPI dataset cache]
    M --> N[Prefix through selected cycle]
    N --> C2[Same causal feature function]
    C2 --> K
    K --> O[Nonnegative RUL in cycles]
    O --> P[React prediction panel]
    M --> Q[React sensor charts]
    J --> R[React model analytics]
```

`ml.engines.preprocess.make_features` is the single feature implementation. Transformations are fitted inside the candidate pipeline on training engines only. Validation uses whole held-out engines and three prefix endpoints per engine. Official test labels are accessed only by inspection/evaluation, not the runtime prediction service.

The model is selected before final test evaluation. Repeating training with the same file hashes, versions, and seed reproduces the experiment, subject to platform floating-point differences. A single fixed validation split is a limitation: the reported test score is not a cross-validation confidence interval.

FastAPI loads the trusted model and parses test trajectories once at startup. It uses a supplied history prefix for inference, so requests cannot inspect unobserved cycles. The built React app is mounted after API routes on the same origin. There are no mock API paths, generated telemetry streams, or random fallback predictions.

The UI aborts obsolete requests when engine or cycle selection changes. A prediction result is cleared whenever its inputs change. Session history records completed requests only and is lost on refresh. CSV export includes exactly the selected engine’s observed prefix.
