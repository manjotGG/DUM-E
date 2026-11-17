from fastapi import APIRouter, HTTPException, Path, Query, Request, Response
from starlette.concurrency import run_in_threadpool

from backend.services.log_parser import MAX_BYTES, MAX_ROWS, MAX_ENGINES, parse_log
from ml.engines.metadata import SENSOR_METADATA
from ml.engines.preprocess import COLUMNS, WINDOW

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


@router.get("/log-schema")
def log_schema():
    return {"columns": COLUMNS, "sensors": SENSOR_METADATA, "minimum_cycles": WINDOW,
            "maximum_bytes": MAX_BYTES, "maximum_rows": MAX_ROWS, "maximum_engines": MAX_ENGINES,
            "formats": ["csv", "txt", "tsv", "log"], "compatible_dataset": "FD001"}


@router.get("/sample-log")
def sample_log(request: Request):
    service = request.app.state.engines
    prefix = service.prefix(1)
    names = {sensor["key"]: sensor["symbol"] for sensor in SENSOR_METADATA}
    return Response(prefix[COLUMNS].rename(columns=names).to_csv(index=False), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="FD001-sample-engine-1.csv"'})


def analyze_content(content, service):
    try:
        frame = parse_log(content)
    except ValueError as error:
        raise HTTPException(422, str(error)) from None
    predictions = []
    for engine_id, group in frame.groupby("engine_id", sort=True):
        prediction = service.predict_prefix(group, source="upload")
        predictions.append({**prediction, "observations": len(group), "first_cycle": int(group.cycle.min())})
    return {"source": "uploaded log", "rows": len(frame), "engines_analyzed": len(predictions),
            "minimum_cycles": WINDOW, "predictions": predictions,
            "compatibility_note": "This model was trained on FD001: one operating condition and HPC degradation. Logs from other equipment, operating regimes, or units are outside its validated scope.",
            "sensor_metadata": SENSOR_METADATA,
            "histories": [{"engine_id": int(engine_id), "history": group.tail(500)[COLUMNS].to_dict(orient="records"), "chart_truncated": len(group) > 500}
                          for engine_id, group in frame.groupby("engine_id", sort=True)]}


@router.post("/analyze-log", openapi_extra={"requestBody": {"required": True, "content": {
    "application/octet-stream": {"schema": {"type": "string", "format": "binary"}}
}}})
async def analyze_log(request: Request):
    # Stream the raw file body, bounding memory before parsing; no multipart temp files.
    content = bytearray()
    async for chunk in request.stream():
        if len(content) + len(chunk) > MAX_BYTES:
            raise HTTPException(413, "Log is too large. Maximum file size is 10 MB.")
        content.extend(chunk)
    return await run_in_threadpool(analyze_content, bytes(content), request.app.state.engines)


@router.get("/{engine_id}/history")
def history(request: Request, engine_id: int = Path(gt=0), cycle: int | None = Query(default=None, gt=0)):
    return request.app.state.engines.history(engine_id, cycle)
