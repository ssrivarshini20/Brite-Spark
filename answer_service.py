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
    if request.claim_date is None:
        return AskResponse(
            status="unknown",
            answer="Please provide the claim date so I can apply the policy version in force at that time.",
            sources=[]
        )
    if retriever.get_collection_size() == 0:
        return AskResponse(
            status="unknown",
            answer="Configuration Error: The policy database is currently empty. Please run the ingestion script.",
            sources=[],
            next_step="Run `python scripts/ingest_policy.py` to index the policy manual."
        )

    retrieved_chunks = retriever.retrieve(request.question, request.claim_date)
    
    print(f"\n--- DEBUG INFO ---")
    print(f"Question: {request.question}")
    print(f"Retrieved {len(retrieved_chunks)} chunks.")
    for c in retrieved_chunks:
        dist = c.get('distance')
        dist_str = f"{dist:.4f}" if isinstance(dist, (float, int)) else "N/A"
        print(f"  - {c['clause']} (distance: {dist_str})")
    
    if not retrieved_chunks:
        print("Final status: UNKNOWN (Low quality / No retrieval)")
        print("------------------\n")
        return AskResponse(
            status="unknown",
            answer="I don't know. The policy manual does not provide enough information to answer this question.",
            sources=[],
            next_step="Please consult a supervisor or check if the question relates to the Household Support Program."
        )
    generation_result = generator.generate_answer(request.question, retrieved_chunks, request.claim_date)
    
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
        
    final_status = generation_result.get("status", "unknown")
    print(f"Grounding decision: {final_status.upper()}")
    print(f"Final status: {final_status.upper()}")
    print("------------------\n")

    return AskResponse(
        status=final_status,
        answer=generation_result.get("answer", "I don't know."),
        sources=sources,
        next_step=next_step
    )
