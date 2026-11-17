# FD001 model card

**Task:** Remaining useful life regression in operating cycles, NASA C-MAPSS FD001.

**Artifact:** `ml/models/engines/model.joblib`, version 1.0.0. Selected XGBoost regressor; training targets capped at 125. The fitted variance filter, standard scaler, estimator, ordered features, and configuration are serialized together.

**Data:** 100 run-to-failure training engines, 20,631 observations. Final evaluation uses 100 separate, partially observed test engines and their official final-cycle RUL labels. NASA generated these trajectories with a turbofan simulation.

**Validation:** Seed 42, engine-aware 80/20 split. Three endpoints at 35%, 55%, and 75% of each held-out trajectory produce 60 validation prefixes. Select by raw, uncapped validation RMSE. No engine appears in both groups. The complete split and source file SHA-256 hashes are in `metrics.json`.

| Candidate | Validation MAE | Validation RMSE |
| --- | ---: | ---: |
| Constant baseline | 35.40 | 42.13 |
| Ridge regression | 26.35 | 32.29 |
| Random Forest | 21.41 | 28.29 |
| Random Forest, cap 125 | 20.24 | 26.64 |
| XGBoost | 23.77 | 30.91 |
| XGBoost, cap 125 | 19.75 | 26.07 |

**Official test:** MAE 12.4972 cycles, RMSE 17.0712 cycles, evaluated on uncapped labels at each engine’s last observation after refitting the winner on all 100 training engines. Median measured end-to-end single-prefix inference approximately 10.83 ms on this machine; latency is hardware dependent.

**Selected estimator:** 550 boosting rounds, depth 4, learning rate 0.035, row/column sampling 0.85, L2 regularization 8, seed 42, 4 CPU threads. Candidate settings live in `ml/engines/train.py` and the saved estimator. Features use trailing windows only. Dropped constant features are learned inside training; no engine ID is supplied to the estimator.

**Output policy:** Clip negative estimates to zero; do not convert cycles to time. Training target capping compresses estimates for engines with long remaining life. Predictions are point estimates without calibrated uncertainty intervals. There is no enforced monotonicity across prediction cycles.

**Limitations:** One operating condition, one fault mode, one subset, one group-validation split. Sensor noise and unknown initial wear limit precision. A relatively good FD001 test score does not establish performance on other subsets or actual hardware. Feature importance reflects the learned model, not causal physical influence. Maintenance colors are configurable demonstration rules. This model is suitable for academic analysis, not aircraft maintenance authorization.

Reproduce with `python -m ml.engines.train`; re-evaluate the saved artifact with `python -m ml.engines.evaluate`. Numerical details and per-engine results in the generated report take precedence over rounded documentation.
