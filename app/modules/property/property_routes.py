from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.modules.property.property_service import (
    create_property,
    get_all_properties,
    get_single_property,
    update_property,
    delete_property,
    get_property_delete_blockers,
)

router = APIRouter(
    prefix="/properties",
    tags=["Properties"]
)


# DATABASE DEPENDENCY
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# CREATE PROPERTY
@router.post("/saveProperty")
async def create_property_route(

    title: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),

    property_type: str = Form(None),
    status: str = Form("AVAILABLE"),

    bedrooms: int = Form(None),
    bathrooms: int = Form(None),
    area_size: float = Form(None),

    address: str = Form(None),
    city: str = Form(None),
    district: str = Form(None),
    country: str = Form(None),

    latitude: float = Form(None),
    longitude: float = Form(None),

    owner_id: int = Form(...),

    image: UploadFile = File(...),
    video: UploadFile = File(...),

    db: Session = Depends(get_db),
):

    property_data = await create_property(
        db=db,

        title=title,
        description=description,
        price=price,

        property_type=property_type,
        status=status,

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

        image=image,
        video=video,
    )

    return {
        "success": True,
        "message": "Property created successfully",
        "data": property_data,
    }


# GET ALL PROPERTIES
@router.get("/getAllProperty")
def get_all_properties_route(
    db: Session = Depends(get_db)
):

    properties = get_all_properties(db)

    return {
        "success": True,
        "count": len(properties),
        "data": properties,
    }


# GET SINGLE PROPERTY
@router.get("/getById/{property_id}")
def get_single_property_route(
    property_id: int,
    db: Session = Depends(get_db),
):

    property_data = get_single_property(
        db,
        property_id
    )

    if not property_data:

        raise HTTPException(
            status_code=404,
            detail="Property not found"
        )

    return {
        "success": True,
        "data": property_data,
    }


# UPDATE PROPERTY
@router.put("/updateProperty/{property_id}")
async def update_property_route(

    property_id: int,

    title: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),

    property_type: str = Form(None),
    status: str = Form(None),

    bedrooms: int = Form(None),
    bathrooms: int = Form(None),
    area_size: float = Form(None),

    address: str = Form(None),
    city: str = Form(None),
    district: str = Form(None),
    country: str = Form(None),

    latitude: float = Form(None),
    longitude: float = Form(None),

    image: UploadFile = File(None),
    video: UploadFile = File(None),

    db: Session = Depends(get_db),
):

    property_data = await update_property(
        db=db,

        property_id=property_id,

        title=title,
        description=description,
        price=price,

        property_type=property_type,
        status=status,

        bedrooms=bedrooms,
        bathrooms=bathrooms,
        area_size=area_size,

        address=address,
        city=city,
        district=district,
        country=country,

        latitude=latitude,
        longitude=longitude,

        image=image,
        video=video,
    )

    if not property_data:

        raise HTTPException(
            status_code=404,
            detail="Property not found"
        )

    return {
        "success": True,
        "message": "Property updated successfully",
        "data": property_data,
    }


# DELETE PROPERTY
@router.delete("/deleteProperty/{property_id}")
def delete_property_route(
    property_id: int,
    db: Session = Depends(get_db),
):

    blockers = get_property_delete_blockers(db, property_id)
    active_references = {name: count for name, count in blockers.items() if count}
    if active_references:
        details = ", ".join(
            f"{count} {name}" for name, count in active_references.items()
        )
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete property {property_id}: it is still referenced by {details}. Resolve these records first; booking history is preserved.",
        )

    try:
        deleted = delete_property(
            db,
            property_id
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this property because it has related reviews, bookings, or favorites. Remove those records first.",
        ) from exc

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Property not found"
        )

    return {
        "success": True,
        "message": "Property deleted successfully",
    }