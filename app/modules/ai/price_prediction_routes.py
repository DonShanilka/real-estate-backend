from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.ai.models.price_prediction_schema import PricePredictionRequest
from app.modules.ai.price_prediction_service import PricePredictionService
from app.modules.ai.training.price_prediction_model import MIN_TRAINING_ROWS
from app.modules.ai.price_prediction_repository import PricePredictionRepository


router = APIRouter(prefix="/price-prediction", tags=["AI Price Prediction"])


@router.post("/predict")
def predict_property_price(
    request: PricePredictionRequest,
    db: Session = Depends(get_db),
):
    """Estimate a listing price from the database's historical asking prices."""
    try:
        return PricePredictionService.predict(db, request.model_dump())
    except ValueError as exc:
        usable_rows = len(PricePredictionRepository.get_historical_listings(db))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": str(exc),
                "usable_training_records": usable_rows,
                "minimum_training_records": MIN_TRAINING_ROWS,
                "next_step": "Add more properties with accurate asking prices, then try again.",
            },
        ) from exc
