from pydantic import BaseModel, ConfigDict, Field


class EnginePredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    engine_id: int = Field(gt=0)
    cycle: int | None = Field(default=None, gt=0)


class SensorContribution(BaseModel):
    key: str
    symbol: str
    name: str
    unit: str
    contribution_cycles: float
    reading: float
    recent_change: float
    observed_window: int


class PredictionExplanation(BaseModel):
    available: bool
    summary: str
    method: str | None = None
    baseline_cycles: float | None = None
    raw_prediction_cycles: float | None = None
    sensor_contributions: list[SensorContribution] = Field(default_factory=list)
    other_contributions: dict[str, float] = Field(default_factory=dict)


class EnginePredictionResponse(BaseModel):
    engine_id: int
    current_cycle: int
    predicted_rul: float
    rul_unit: str = "cycles"
    maintenance_priority: str
    model_version: str
    model_name: str
    inference_ms: float
    dataset: str = "NASA C-MAPSS FD001 · test trajectories"
    thresholds: dict[str, float]
    limitation: str
    source: str = "dataset"
    explanation: PredictionExplanation
