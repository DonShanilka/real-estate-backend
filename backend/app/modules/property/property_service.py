from sqlalchemy.orm import Session

from app.modules.bookings.booking_model import Booking
from app.modules.favorites.favorite_model import Favorite
from app.modules.property.property_model import Property, PropertyType, PropertyStatus
from app.modules.review.review_model import Review
from app.core.upload_file import upload_file


# CREATE PROPERTY
async def create_property(
    db: Session,

    title: str,
    description: str,
    price: float,

    property_type: str,
    status: str,

    bedrooms: int,
    bathrooms: int,
    area_size: float,

    address: str,
    city: str,
    district: str,
    country: str,

    latitude: float,
    longitude: float,

    owner_id: int,

    image,
    video,
):

    # convert ENUM safely
    property_type_enum = PropertyType(property_type) if property_type else PropertyType.HOUSE
    status_enum = PropertyStatus(status) if status else PropertyStatus.AVAILABLE

    # upload files to Backblaze
    image_url = await upload_file(image, "property-images")
    video_url = await upload_file(video, "property-videos")

    new_property = Property(
        title=title,
        description=description,
        price=price,

        property_type=property_type_enum,
        status=status_enum,

        bedrooms=bedrooms,
        bathrooms=bathrooms,
        area_size=area_size,

        address=address,
        city=city,
        district=district,
        country=country,

        latitude=latitude,
        longitude=longitude,

        owner_id=owner_id,

        image_url=image_url,
        video_url=video_url,
    )

    db.add(new_property)
    db.commit()
    db.refresh(new_property)

    return new_property


# Update Property
async def update_property(
    db: Session,
    property_id: int,

    title=None,
    description=None,
    price=None,

    property_type=None,
    status=None,

    bedrooms=None,
    bathrooms=None,
    area_size=None,

    address=None,
    city=None,
    district=None,
    country=None,

    latitude=None,
    longitude=None,

    image=None,
    video=None,
):

    property = (
        db.query(Property)
        .filter(Property.id == property_id)
        .first()
    )

    if not property:
        return None

    # normal fields
    if title: property.title = title
    if description: property.description = description
    if price: property.price = price

    if property_type:
        property.property_type = PropertyType(property_type)

    if status:
        property.status = PropertyStatus(status)

    if bedrooms is not None: property.bedrooms = bedrooms
    if bathrooms is not None: property.bathrooms = bathrooms
    if area_size is not None: property.area_size = area_size

    if address: property.address = address
    if city: property.city = city
    if district: property.district = district
    if country: property.country = country

    if latitude is not None: property.latitude = latitude
    if longitude is not None: property.longitude = longitude

    # upload new files
    if image:
        property.image_url = await upload_file(image, "property-images")

    if video:
        property.video_url = await upload_file(video, "property-videos")

    db.commit()
    db.refresh(property)

    return property


# GET ALL
def get_all_properties(db: Session):

    return db.query(Property).all()


# GET SINGLE
def get_single_property(
    db: Session,
    property_id: int
):

    return (
        db.query(Property)
        .filter(Property.id == property_id)
        .first()
    )


# DELETE PROPERTY
def get_property_delete_blockers(db: Session, property_id: int):
    return {
        "reviews": db.query(Review).filter(Review.property_id == property_id).count(),
        "bookings": db.query(Booking).filter(Booking.property_id == property_id).count(),
        "favorites": db.query(Favorite).filter(Favorite.property_id == property_id).count(),
    }


def delete_property(
    db: Session,
    property_id: int
):

    property = (
        db.query(Property)
        .filter(Property.id == property_id)
        .first()
    )

    if not property:
        return None

    db.delete(property)

    db.commit()

    return True