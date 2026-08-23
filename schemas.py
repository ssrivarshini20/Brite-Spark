from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class AskRequest(BaseModel):
    question: str
    claim_date: Optional[date] = None

class SourceClause(BaseModel):
    clause: str
    section: Optional[str] = None
    text: str

class AskResponse(BaseModel):
    status: str # "answered", "unknown", "conflict"
    answer: str
    sources: List[SourceClause]
    next_step: Optional[str] = None
