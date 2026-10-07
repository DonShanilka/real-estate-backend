from sqlalchemy.orm import Session

from app.modules.property.property_model import Property


class PricePredictionRepository:
    @staticmethod
    def get_historical_listings(db: Session, limit: int = 2_000) -> list[Property]:
        """Use recorded property prices as supervised training labels."""
        return (
            db.query(Property)
            .filter(Property.price.isnot(None), Property.price > 0)
            .order_by(Property.created_at.desc(), Property.id.desc())
            .limit(limit)
            .all()
        )
