from fastapi import APIRouter, HTTPException, Path, Query, Request

from backend.schemas import EnginePredictionRequest, EnginePredictionResponse

router = APIRouter(prefix="/api/engines", tags=["Jet engine intelligence"])


@router.get("")
def engines(request: Request):
    return request.app.state.engines.engines()


@router.get("/metrics")
def metrics(request: Request):
    report = request.app.state.engines.metrics
    if report is None:
        raise HTTPException(503, "Evaluation unavailable. Train and evaluate the model first.")
    return report


@router.post("/predict", response_model=EnginePredictionResponse)
def predict(payload: EnginePredictionRequest, request: Request):
    return request.app.state.engines.predict(payload.engine_id, payload.cycle)


@router.get("/{engine_id}/history")
def history(request: Request, engine_id: int = Path(gt=0), cycle: int | None = Query(default=None, gt=0)):
    return request.app.state.engines.history(engine_id, cycle)
