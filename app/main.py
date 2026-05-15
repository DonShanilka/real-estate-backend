from fastapi import FastAPI

from app.core.database import (
    engine,
    Base
)

from app.modules.auth.auth_routes import (
    router as auth_router
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)

@app.get("/")
def root():
    return {
        "message": "Real Estate API Running"
    }