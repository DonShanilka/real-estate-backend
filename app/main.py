from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import ( engine, Base)

from app.modules.auth.auth_routes import router as auth_router
from app.modules.users.user_routes import router as user_router
from app.modules.property.property_routes import router as property_router
from app.modules.search.search_routes import router as search_router
from app.modules.recommendations.recommendation_routes import router as recommendation_router
from app.modules.favorites.favorite_routes import router as favorites_router
from app.modules.review.review_routes import router as review_router
from app.modules.bookings.booking_routes import router as booking_router
from app.modules.chat.chat_routes import router as chat_router
from app.modules.chat.websocket_routes import router as websocket_router

from app.modules.users.user_model import User

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Real Estate API",
    version="1.0.0"
)


# CORS CONFIGURATION
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# INCLUDE ROUTERS
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(property_router)
app.include_router(search_router)
app.include_router(recommendation_router)
app.include_router(favorites_router)
app.include_router(review_router)
app.include_router(booking_router)
app.include_router(chat_router)
app.include_router(websocket_router)


# ROOT ROUTE
@app.get("/")
def root():
    return {
        "success": True,
        "message": "Real Estate API Running"
    }