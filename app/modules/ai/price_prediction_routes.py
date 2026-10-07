from fastapi import APIRouter, HTTPException, status

from app.modules.ai.models.price_prediction_schema import PricePredictionRequest
from app.modules.ai.price_prediction_service import PricePredictionService

router = APIRouter(prefix="/price-prediction", tags=["AI Price Prediction"])


@router.get("/status")
def price_model_status():
    """Report the training dataset size and whether the model can be trained."""
    return PricePredictionService.training_status()


@router.post("/predict")
def predict_property_price(request: PricePredictionRequest):
    """Estimate a market price from the historical CSV dataset."""
    try:
        return PricePredictionService.predict(request.model_dump())
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": str(exc)},
        ) from exc
