from sqlalchemy import Column, ForeignKey, Integer, String
from app.core.database import Base


class GoogleIdentity(Base):
    __tablename__ = "google_identities"

    id = Column(Integer, primary_key=True, index=True)
    google_sub = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
