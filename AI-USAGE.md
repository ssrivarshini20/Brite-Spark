# AI Usage Disclosure

In the development of this hackathon project, AI assistance (specifically Google's advanced coding agent models) was utilized in the following ways:

- **Code Scaffolding**: AI was used to generate the boilerplate structure for the FastAPI backend and the React/Vite frontend.
- **RAG Architecture & Parsing**: The regex logic to parse the `policy-manual.md` into explicit clauses (e.g., matching `**1.1.1**`) was co-developed with AI.
- **Prompt Engineering**: The structured system prompt in `generator.py` that enforces JSON output and strict grounding rules was iteratively refined with AI assistance.
- **UI Design**: The Tailwind CSS layout, including the responsive search bar and the styling of the "Answered", "I don't know", and "Conflict" states, was heavily assisted by AI to meet the "premium aesthetic" requirements of the prompt.
- **Documentation**: The foundation of the `README.md` and `DECISIONS.md` was drafted by AI and reviewed/edited for accuracy.
- **Test Generation**: The `test_questions.yaml` file and Pytest scaffolding were generated with AI assistance based on the contents of the policy manual.

All core logic, architecture decisions, and conflict-detection mechanisms were driven by the prompt's explicit requirements and guided by human oversight.
