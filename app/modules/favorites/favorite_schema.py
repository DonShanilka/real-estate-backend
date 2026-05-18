from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    property_id: int