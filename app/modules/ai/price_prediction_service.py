from sqlalchemy.orm import Session

from app.modules.ai.price_prediction_repository import PricePredictionRepository
from app.modules.ai.training.price_prediction_model import (
    predict_price,
    train_price_model,
)


class PricePredictionService:
    @staticmethod
    def predict(db: Session, property_data: dict) -> dict:
        history = PricePredictionRepository.get_historical_listings(db)
        model = train_price_model(history)
        prediction = predict_price(model, property_data)
        prediction["request"] = {
            "city": property_data.get("city"),
            "district": property_data.get("district"),
            "country": property_data.get("country", "Sri Lanka"),
            "property_type": property_data.get("property_type"),
            "bedrooms": property_data.get("bedrooms"),
            "bathrooms": property_data.get("bathrooms"),
            "house_area_sqft": property_data.get("house_area_sqft"),
            "land_area_perches": property_data.get("land_area_perches"),
        }
        return prediction
