from fastapi import FastAPI

from app.core.database import (
    engine,
    Base
)

# Import routers
from app.modules.auth.auth_routes import router as auth_router
from app.modules.users.user_routes import router as user_router
from app.modules.property.property_routes import router as property_router

# Import models
from app.modules.users.user_model import User

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Real Estate API",
    version="1.0.0"
)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(property_router)

# Root route
@app.get("/")
def root():
    return {
        "success": True,
        "message": "Real Estate API Running"
    }