from sqlalchemy.orm import Session

from app.modules.ai.assistant_repository import PropertyAssistantRepository
from app.modules.ai.inference.property_assistant import answer_property_question


class PropertyAssistantService:
    @staticmethod
    def ask(db: Session, question: str) -> dict:
        properties = PropertyAssistantRepository.get_available_properties(db)
        response = answer_property_question(question, properties)
        response["retrieved_count"] = len(properties)
        return response
