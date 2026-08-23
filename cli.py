import argparse
from app.models.schemas import AskRequest
from app.services.answer_service import process_question
from dotenv import load_dotenv

load_dotenv()

def main():
    print("-" * 50)
    print("Grounded Policy Assistant CLI")
    print("-" * 50)
    
    while True:
        try:
            question = input("\nAsk a question (or type 'quit' to exit):\n> ")
            if question.lower() in ['quit', 'exit', 'q']:
                break
                
            if not question.strip():
                continue
                
            request = AskRequest(question=question)
            response = process_question(request)
            
            print("\n" + "=" * 50)
            if response.status == "answered":
                print("ANSWER")
                print("-" * 50)
                print(response.answer)
                print("\nEVIDENCE")
                print("-" * 50)
                for source in response.sources:
                    print(f"Clause: {source.clause}")
                    if source.section:
                        print(f"Section: {source.section}")
                    print(f"\"{source.text}\"\n")
            elif response.status == "unknown":
                print("🔴 I DON'T KNOW")
                print("-" * 50)
                print(response.answer)
                if response.next_step:
                    print(f"\nNext step:\n{response.next_step}")
            elif response.status == "conflict":
                print("🟠 POLICY CONFLICT")
                print("-" * 50)
                print(response.answer)
                print("\nCONFLICTING PROVISIONS")
                print("-" * 50)
                for source in response.sources:
                    print(f"Clause: {source.clause}")
                    print(f"\"{source.text}\"\n")
                if response.next_step:
                    print(f"\nNext step:\n{response.next_step}")
            print("=" * 50)
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
