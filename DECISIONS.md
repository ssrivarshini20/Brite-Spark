# Architectural and Design Decisions

## Tech Stack Choices
- **Backend (FastAPI)**: Chosen for its speed, simplicity, and ease of defining strict schemas with Pydantic. Python is the de facto standard for RAG applications.
- **Frontend (React + Vite + Tailwind)**: Chosen to meet the requirement for a "production-quality but hackathon-sized application." Tailwind provides rapid, beautiful styling matching modern aesthetics without writing bloated CSS.
- **Database (ChromaDB)**: Selected as a robust, fully local vector database. It removes the need for external cloud infrastructure (like Pinecone) or complex local setups (like Postgres with pgvector).
- **LLM/Embeddings**: Used a local SentenceTransformer (`all-MiniLM-L6-v2`) for embeddings to keep vector searches entirely offline and fast. Google GenAI (Gemini) was selected as the configurable LLM provider due to its strong reasoning capabilities required for grounding and conflict detection.

## RAG Design and Grounding
- **Chunking Strategy**: The policy manual is highly structured. Rather than arbitrary character-based chunking, I wrote a custom parser that chunks the document by *explicit clauses* (e.g., `**1.1.1**`). This preserves exact boundaries, section metadata, and clause numbers naturally, solving the citation requirement natively.
- **Grounding Logic**: The system does not directly prompt the LLM to just "answer". Instead, the LLM is instructed to output a JSON object containing its reasoning, status (`answered`, `unknown`, `conflict`), and the exact clause numbers it relied upon. The backend then maps these clause numbers back to the retrieved source chunks. This guarantees that every citation displayed to the user is a genuine clause retrieved from the database, preventing hallucinated citations.

## Refusal ("I don't know") Threshold
- **Where the line is set**: The LLM is strictly instructed that if the retrieved evidence does not contain the explicit rule, or if there is an apparent gap (such as the missing rule for full-time student absence, which is referenced in §3.2.3 but never defined), it *must* refuse to answer. 
- **Why**: In a county benefits office, a confident hallucinated answer can cause a resident to lose their livelihood. The threshold for refusal is set to "explicit presence in the text." If it requires inferring a rule from general knowledge, it is rejected.

## Conflict Handling
- I identified the genuine internal inconsistency: §4.3.2 requires reporting changes within 10 days, but §9.1.4 states no overpayment is established if reported within 30 days. 
- Instead of silently picking one or merging them into "between 10 and 30 days", the system explicitly surfaces the conflict and instructs the user to escalate to a supervisor.

## Hackathon Constraints
- **What was NOT built**: Authentication, user accounts, chat history/memory, and multi-document ingestion. These were omitted to focus entirely on the core grounding, retrieval, and UI polish constraints of the problem.
- **Day 2 requirement preparation**: The codebase separates `retriever.py`, `generator.py`, and `answer_service.py`. If Day 2 requires changing the embedding model, adding a reranker, or switching to an Agentic workflow, those components can be swapped without touching the API routes or the frontend.
