from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.modules.property.property_model import Property


class SearchRepository:

    FEATURE_TERMS = {
        "parking": ("parking", "garage"),
        "swimming pool": ("swimming pool", "pool"),
        "garden": ("garden", "yard"),
        "furnished": ("furnished", "furniture"),
        "balcony": ("balcony", "balconies"),
        "elevator": ("elevator", "lift"),
        "security": ("security",),
        "sea view": ("sea view", "ocean view"),
        "pet friendly": ("pet friendly", "pet-friendly", "allows pets"),
    }

    @staticmethod
    def get_natural_search_candidates(db: Session, limit: int = 500):
        """Return a bounded set of actual listings to rank against user intent."""
        return (
            db.query(Property)
            .order_by(Property.created_at.desc(), Property.id.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def search_nearby(db: Session, latitude: float, longitude: float, radius_km: float, limit: int):
        # Haversine great-circle distance in kilometers; SQL filtering avoids loading
        # unrelated properties into application memory.
        distance_km = 6371.0088 * 2 * func.asin(
            func.sqrt(
                func.pow(func.sin(func.radians(Property.latitude - latitude) / 2), 2)
                + func.cos(func.radians(latitude))
                * func.cos(func.radians(Property.latitude))
                * func.pow(func.sin(func.radians(Property.longitude - longitude) / 2), 2)
            )
        )

        rows = (
            db.query(Property, distance_km.label("distance_km"))
            .filter(
                Property.latitude.isnot(None),
                Property.longitude.isnot(None),
                Property.latitude.between(-90, 90),
                Property.longitude.between(-180, 180),
                distance_km <= radius_km,
            )
            .order_by(distance_km.asc())
            .limit(limit)
            .all()
        )

        return [
            {"property": property_, "distance_km": round(float(distance), 2)}
            for property_, distance in rows
        ]

    @staticmethod
    def search_properties(db: Session, filters):

        query = db.query(Property)

        if filters.keyword:
            query = query.filter(
                Property.title.ilike(f"%{filters.keyword}%")
            )

        if filters.city:
            query = query.filter(
                Property.city == filters.city
            )

        if filters.district:
            query = query.filter(
                Property.district == filters.district
            )

        if filters.property_type:
            query = query.filter(
                Property.property_type == filters.property_type
            )

        if filters.min_price:
            query = query.filter(
                Property.price >= filters.min_price
            )

        if filters.max_price:
            query = query.filter(
                Property.price <= filters.max_price
            )

        if filters.bedrooms:
            query = query.filter(
                Property.bedrooms >= filters.bedrooms
            )

        if filters.bathrooms:
            query = query.filter(
                Property.bathrooms >= filters.bathrooms
            )

        if filters.min_area:
            query = query.filter(
                Property.area_size >= filters.min_area
            )

        if filters.max_area:
            query = query.filter(
                Property.area_size <= filters.max_area
            )

        # Sorting
        if filters.sort == "price_asc":
            query = query.order_by(Property.price.asc())

        elif filters.sort == "price_desc":
            query = query.order_by(Property.price.desc())

        else:
            query = query.order_by(Property.created_at.desc())

        # Pagination
        total = query.count()

        offset = (filters.page - 1) * filters.limit

        properties = (
            query
            .offset(offset)
            .limit(filters.limit)
            .all()
        )

        return {
            "success": True,
            "total": total,
            "page": filters.page,
            "limit": filters.limit,
            "data": properties
        }

    @staticmethod
    def search_natural_filters(db: Session, filters: dict):
        query = db.query(Property)

        if filters.get("city"):
            query = query.filter(Property.city.ilike(filters["city"]))
        if filters.get("property_type"):
            query = query.filter(Property.property_type == filters["property_type"])
        if filters.get("bedrooms") is not None:
            query = query.filter(Property.bedrooms >= filters["bedrooms"])
        if filters.get("bathrooms") is not None:
            query = query.filter(Property.bathrooms >= filters["bathrooms"])
        if filters.get("min_price") is not None:
            query = query.filter(Property.price >= filters["min_price"])
        if filters.get("max_price") is not None:
            query = query.filter(Property.price <= filters["max_price"])

        searchable_text = (
            Property.title,
            Property.description,
            Property.address,
        )
        for feature in filters.get("features", []):
            terms = SearchRepository.FEATURE_TERMS.get(feature, (feature,))
            query = query.filter(
                or_(*[
                    column.ilike(f"%{term}%")
                    for column in searchable_text
                    for term in terms
                ])
            )

        return query.order_by(Property.created_at.desc()).all()