from pydantic import BaseModel, ConfigDict, Field


class EnginePredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    engine_id: int = Field(gt=0)
    cycle: int | None = Field(default=None, gt=0)


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
