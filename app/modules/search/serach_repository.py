from sqlalchemy.orm import Session
from app.modules.property.property_model import Property

class SearchRepository:

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

        # Sorting
        if filters.sort == "price_asc":
            query = query.order_by(Property.price.asc())

        elif filters.sort == "price_desc":
            query = query.order_by(Property.price.desc())

        else:
            query = query.order_by(Property.created_at.desc())

        # Pagination
        offset = (filters.page - 1) * filters.limit

        total = query.count()

        properties = query.offset(offset).limit(filters.limit).all()

        return {
            "total": total,
            "page": filters.page,
            "limit": filters.limit,
            "data": properties
        }