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


def get_single_property(db: Session, property_id: int):
    return db.query(Property).filter(Property.id == property_id).first()


def update_property(db: Session, property_id: int, data):
    property = db.query(Property).filter(Property.id == property_id).first()
    
    if not property:
        return None
    
    update_data = data.dict(exclude_unset=True)

    allowed_fields = [
        "title",
        "description",
        "price",
        "property_type",
        "status",
        "bedrooms",
        "bathrooms",
        "area_size",
        "address",
        "city",
        "district",
        "country",
        "latitude",
        "longitude",
        "image_url",
        "video_url"
    ]

    for key, value in update_data.items():
        if key in allowed_fields:
            setattr(property, key, value)
            
    db.commit()
    db.refresh(property)
    
    return property


def delete_property(db: Session, property_id: int):
    property = db.query(Property).filter(Property.id == property_id).first()
    
    if not property:
        return None
    
    db.delete(property)
    db.commit()
    
    return True