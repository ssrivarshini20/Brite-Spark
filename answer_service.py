from app.models.schemas import AskRequest, AskResponse, SourceClause
from app.rag.retriever import retriever
from app.rag.generator import generator

def process_question(request: AskRequest) -> AskResponse:
    if not request.question or not request.question.strip():
        return AskResponse(
            status="unknown",
            answer="Please ask a valid question.",
            sources=[]
        )
        
    retrieved_chunks = retriever.retrieve(request.question)
    
    if not retrieved_chunks:
        return AskResponse(
            status="unknown",
            answer="I don't know. The policy manual does not provide enough information to answer this question.",
            sources=[],
            next_step="Please consult a supervisor or check if the question relates to the Household Support Program."
        )
        
    generation_result = generator.generate_answer(request.question, retrieved_chunks)
    
    # Map back to SourceClause objects based on relevant_clauses returned by LLM
    sources = []
    
    if generation_result.get("status") in ["answered", "conflict"] and generation_result.get("relevant_clauses"):
        for clause_id in generation_result["relevant_clauses"]:
            # Find the original chunk
            chunk = next((c for c in retrieved_chunks if c["clause"] == clause_id), None)
            if chunk:
                sources.append(SourceClause(
                    clause=chunk["clause"],
                    section=chunk["section"],
                    text=chunk["source_text"]
                ))
                
    # Format next step based on status if not provided by LLM
    next_step = generation_result.get("next_step")
    if generation_result.get("status") == "unknown" and not next_step:
        next_step = "Please refer this matter to the appropriate policy authority."
        
    return AskResponse(
        status=generation_result.get("status", "unknown"),
        answer=generation_result.get("answer", "I don't know."),
        sources=sources,
        next_step=next_step
    )
