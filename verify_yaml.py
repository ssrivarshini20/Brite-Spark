import sys
import os
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from app.services.answer_service import process_question
from app.models.schemas import AskRequest

def main():
    with open('tests/test_questions.yaml', 'r') as f:
        data = yaml.safe_load(f)
        
    all_passed = True
    for q in data['questions']:
        expected = q['expected_behavior']
        resp = process_question(AskRequest(question=q['question'], claim_date=q.get('claim_date', '2026-02-28')))
        actual = resp.status
        
        print(f"Q: {q['question']}")
        print(f"Expected: {expected} -> Actual: {actual}")
        print(f"Answer: {resp.answer}")
        print("-" * 40)
        
        if expected != actual:
            all_passed = False
            
    if all_passed:
        print("ALL TESTS PASSED SUCCESSFULLY!")
    else:
        print("SOME TESTS FAILED!")

if __name__ == '__main__':
    main()
