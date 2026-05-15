from sqlalchemy.orm import Session
from app.modules.property.property_model import Property

def create_property(db: Session, data):
    new_property = Property(**data.dict())
    
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    
    return new_property

def get_all_properties(db: Session):
    return db.query(Property).all()

