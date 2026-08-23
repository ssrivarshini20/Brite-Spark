import json
import re
from google import genai
from google.genai import types
from app.config import settings
from typing import List, Dict, Any
from datetime import date

class Generator:
    def __init__(self):
        self.client = genai.Client(api_key=settings.LLM_API_KEY)
        self.model_name = settings.LLM_MODEL
        
    def generate_answer(self, question: str, retrieved_chunks: List[Dict[str, Any]], claim_date: date | None = None) -> Dict[str, Any]:
        # Construct the context
        context_str = ""
        for i, chunk in enumerate(retrieved_chunks):
            context_str += f"--- Clause {chunk['clause']} ---\n"
            if chunk.get("is_amendment") == "true":
                context_str += f"Source effective from: {chunk.get('effective_from')} (amendment; applies only on/after this date)\n"
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
9. Evaluate the evidence for the claim date supplied below. Do not apply an amendment before its effective date.
10. Amendment text changes the cited provision; for a date on/after its effective date, apply the amendment instead of the superseded wording in the consolidated manual. For a date before its effective date, ignore the amendment.

Output your response as a JSON object with the following schema:
{
  "status": "answered" | "unknown" | "conflict",
  "reasoning": "Brief explanation of how the evidence supports the answer or why it is unknown/conflicting.",
  "answer": "Plain language answer (if answered) OR explanation of missing info (if unknown) OR explanation of conflict (if conflict).",
  "next_step": "Appropriate next step (e.g. 'Please refer this matter to a supervisor' or contact info if specified). If unknown/conflict, MUST provide a next step if reasonable.",
  "relevant_clauses": ["§1.1.1", ...] (List of exactly matching clause strings that support the answer or represent the conflict. If unknown, leave empty.)
}"""

        date_text = claim_date.isoformat() if claim_date else "not supplied"
        user_prompt = f"""Claim date: {date_text}
    Question: {question}

Retrieved Evidence:
{context_str}

Please evaluate the evidence and generate the JSON response according to the rules."""

        try:
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
        except Exception:
            return {
                "status": "unknown",
                "answer": "I found relevant policy text, but the answer service is not configured with a valid language-model API key.",
                "relevant_clauses": [],
                "next_step": "Set a valid LLM_API_KEY in the project .env file and restart the backend."
            }
        
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
