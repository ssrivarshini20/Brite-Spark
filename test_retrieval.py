import pytest
from unittest.mock import patch
from datetime import date
from app.services.answer_service import process_question
from app.models.schemas import AskRequest
from app.rag.loader import parse_policy_manual
from app.rag.retriever import Retriever

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
    
    req = AskRequest(question="What is the policy?", claim_date=date(2026, 3, 1))
    resp = process_question(req)
    
    assert resp.status == "answered"
    assert resp.answer == "This is the answer."
    assert len(resp.sources) == 1
    assert resp.sources[0].clause == "§1.1.1"

@patch('app.services.answer_service.retriever.retrieve')
def test_process_question_no_retrieval(mock_retrieve):
    mock_retrieve.return_value = []
    
    req = AskRequest(question="Random question?", claim_date=date(2026, 2, 28))
    resp = process_question(req)
    
    assert resp.status == "unknown"
    assert "I don't know" in resp.answer
    assert len(resp.sources) == 0

def test_amendment_is_parsed_with_effective_date():
    chunks = parse_policy_manual("../data/Amendment No. 2026-01.md")

    assert len(chunks) == 9
    assert chunks[0]["clause"] == "§1.1"
    assert chunks[0]["effective_from"] == "2026-03-01"
    assert chunks[-1]["clause"] == "§5.3"

@patch("app.rag.retriever.embedding_service.embed_text", return_value=[0.1])
def test_retriever_excludes_future_amendments(mock_embed):
    collection = type("Collection", (), {
        "query": lambda self, **kwargs: {
            "metadatas": [[
                {"clause": "§4.3.2", "effective_from": "", "source_text": "old"},
                {"clause": "§2.1", "effective_from": "2026-03-01", "source_text": "new"},
            ]],
            "documents": [["old", "new"]],
            "distances": [[0.1, 0.1]],
        }
    })()
    retriever = Retriever(top_k=2)
    with patch("app.rag.retriever.embedding_service.collection", collection):
        before_effective = retriever.retrieve("report a change", date(2026, 2, 28))
        after_effective = retriever.retrieve("report a change", date(2026, 3, 1))

    assert [chunk["clause"] for chunk in before_effective] == ["§4.3.2"]
    assert [chunk["clause"] for chunk in after_effective] == ["§4.3.2", "§2.1"]
