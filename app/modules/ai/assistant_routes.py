from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.ai.models.property_assistant_schema import PropertyAssistantRequest
from app.modules.ai.assistant_service import PropertyAssistantService


router = APIRouter(prefix="/assistant", tags=["Property Assistant"])


@router.post("/property")
def ask_property_assistant(
    request: PropertyAssistantRequest,
    db: Session = Depends(get_db),
):
    """Ask a natural-language question about properties in the database."""
    return PropertyAssistantService.ask(db, request.question)
