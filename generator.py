import json
import re
from google import genai
from google.genai import types
from app.config import settings
from typing import List, Dict, Any

class Generator:
    def __init__(self):
        self.client = genai.Client(api_key=settings.LLM_API_KEY) if settings.LLM_API_KEY and settings.LLM_API_KEY != "your_gemini_api_key_here" else None
        self.model_name = settings.LLM_MODEL
        
    def generate_answer(self, question: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.client is None:
            return {
                "status": "unknown",
                "answer": "A Gemini API key is required to generate an answer.",
                "relevant_clauses": [],
                "next_step": "Set LLM_API_KEY in the project .env file and restart the backend.",
            }

        # Construct the context
        context_str = ""
        for i, chunk in enumerate(retrieved_chunks):
            context_str += f"--- Clause {chunk['clause']} ---\n"
            context_str += f"{chunk['source_text']}\n\n"
            
        system_prompt = """You are a policy assistant for the Calder County Household Support Program.
You may answer ONLY from the supplied policy evidence.

Rules:
1. Do not use outside knowledge.
2. Do not invent policy requirements.
3. Do not infer unsupported rules.
4. Every factual policy claim must be supported by retrieved evidence.
5. If the evidence does not establish the answer, or if there is an apparent gap in the policy where a rule should exist but doesn't, you must refuse to answer.
6. If relevant provisions conflict and the policy does not establish which controls, report the conflict instead of choosing one.
7. Keep answers concise and understandable.
8. Never fabricate citations.

Output your response as a JSON object with the following schema:
{
  "status": "answered" | "unknown" | "conflict",
  "reasoning": "Brief explanation of how the evidence supports the answer or why it is unknown/conflicting.",
  "answer": "Plain language answer (if answered) OR explanation of missing info (if unknown) OR explanation of conflict (if conflict).",
  "next_step": "Appropriate next step (e.g. 'Please refer this matter to a supervisor' or contact info if specified). If unknown/conflict, MUST provide a next step if reasonable.",
  "relevant_clauses": ["§1.1.1", ...] (List of exactly matching clause strings that support the answer or represent the conflict. If unknown, leave empty.)
}"""

        user_prompt = f"""Question: {question}

Retrieved Evidence:
{context_str}

Please evaluate the evidence and generate the JSON response according to the rules."""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Content(role="user", parts=[types.Part.from_text(text=system_prompt + "\n\n" + user_prompt)])
            ],
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
            )
        )
        
        try:
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            # Fallback for unexpected format
            match = re.search(r'```json(.*?)```', response.text, re.DOTALL)
            if match:
                return json.loads(match.group(1).strip())
            return {
                "status": "unknown",
                "answer": "An error occurred while generating the response.",
                "relevant_clauses": [],
                "next_step": "Please try again."
            }

generator = Generator()
