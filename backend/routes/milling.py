from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/milling", tags=["Milling (inactive)"])


@router.post("/predict")
def predict():
    raise HTTPException(501, "Milling is under development. A validated milling dataset and trained model are required.")
