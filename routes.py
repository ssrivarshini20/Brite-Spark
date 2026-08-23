from fastapi import APIRouter
from app.models.schemas import AskRequest, AskResponse
from app.services.answer_service import process_question

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    return process_question(request)
