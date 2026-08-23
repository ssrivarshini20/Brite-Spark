# Grounded Policy Assistant

A robust, production-ready RAG application that answers policy questions strictly based on the provided Calder County Household Support Program manual. 

It explicitly detects policy conflicts and refuses to answer questions that are not supported by the evidence or that fall into apparent gaps.

## Architecture

The system is designed with a modular separation of concerns:
- **Retrieval Layer**: Loads Markdown, chunks by clause (`**§X.Y.Z**`), embeds using `sentence-transformers`, and stores in a local ChromaDB instance.
- **Generation Layer**: Uses an LLM (`google-genai` by default) to reason over the retrieved clauses, outputting a structured JSON evaluation (is it answered, unknown, or a conflict?) and producing the final grounded answer.
- **API Layer**: Exposes a clean `POST /api/ask` endpoint using FastAPI.
- **UI Layer**: A modern, single-page React frontend using Vite and Tailwind CSS.
- **CLI Fallback**: A command-line interface that reuses the core logic for terminal-only execution.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, ChromaDB, SentenceTransformers, Google GenAI SDK.
- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons, Axios.

## Prerequisites
- Node.js (v18+)
- Python (3.11+)

## Installation

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# Activate venv (Windows: .venv\Scripts\activate | Unix: source .venv/bin/activate)
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory based on `.env.example`:
```env
LLM_API_KEY=your_api_key_here
LLM_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_PATH=./data/chroma
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

## Running the Application

### 1. Ingest Policy
First, ingest the policy manual into ChromaDB:
```bash
# From project root
python scripts/ingest_policy.py
```
The ingestion includes `data/Amendment No. 2026-01.md`. Questions sent to the API may include an ISO `claim_date` (for example, `2026-02-28`); the frontend supplies today’s date by default.

### 2. Run Backend
```bash
# From project root
cd backend
# Make sure venv is activated
uvicorn app.main:app --reload
```

### 3. Run Frontend
```bash
# In a new terminal
cd frontend
npm run dev
```

### 4. Run CLI Fallback
If you don't want to use the web UI, you can run the CLI tool:
```bash
# From project root
python -m backend.app.cli
```

## Running Tests
Run the test suite via pytest:
```bash
cd backend
pytest ../tests/
```

## Known Limitations
- The embedding model `all-MiniLM-L6-v2` is small and fast, which is great for local development, but might not capture complex semantic nuance as well as larger commercial embeddings.
- RAG systems are sensitive to chunk sizes; the current clause-level chunking is highly accurate for this specific document but might need modification if the policy manual formatting changes drastically.
