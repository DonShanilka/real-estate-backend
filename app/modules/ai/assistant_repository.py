from sqlalchemy.orm import Session

from app.modules.property.property_model import Property, PropertyStatus


class PropertyAssistantRepository:
    @staticmethod
    def get_available_properties(db: Session, limit: int = 500) -> list[Property]:
        return (
            db.query(Property)
            .filter(Property.status == PropertyStatus.AVAILABLE)
            .order_by(Property.created_at.desc(), Property.id.desc())
            .limit(limit)
            .all()
        )
