import pytest
from unittest.mock import patch
from app.services.answer_service import process_question
from app.models.schemas import AskRequest

@patch('app.services.answer_service.retriever.retrieve')
@patch('app.services.answer_service.generator.generate_answer')
def test_process_question_answered(mock_generate, mock_retrieve):
    mock_retrieve.return_value = [
        {"clause": "§1.1.1", "section": "Part 1 - Scope", "source_text": "**1.1.1** Policy text."}
    ]
    mock_generate.return_value = {
        "status": "answered",
        "answer": "This is the answer.",
        "relevant_clauses": ["§1.1.1"]
    }
    
    req = AskRequest(question="What is the policy?")
    resp = process_question(req)
    
    assert resp.status == "answered"
    assert resp.answer == "This is the answer."
    assert len(resp.sources) == 1
    assert resp.sources[0].clause == "§1.1.1"

@patch('app.services.answer_service.retriever.retrieve')
def test_process_question_no_retrieval(mock_retrieve):
    mock_retrieve.return_value = []
    
    req = AskRequest(question="Random question?")
    resp = process_question(req)
    
    assert resp.status == "unknown"
    assert "I don't know" in resp.answer
    assert len(resp.sources) == 0
