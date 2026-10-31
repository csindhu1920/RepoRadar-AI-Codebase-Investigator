
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Keep native numerical-library thread pools small alongside local models.
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

from reporadar.rag import (
    retrieve_context,
    format_context,
    build_rag_prompt,
)
from reporadar.llm import generate_answer


def main():
    index_path = PROJECT_ROOT / "data" / "index.json"

    with index_path.open("r", encoding="utf-8") as file:
        index = json.load(file)

    question = "What does the login function do?"

    # Step 1: Retrieve relevant code.
    results = retrieve_context(index, question, top_k=5)

    # Step 2: Format retrieved code as evidence.
    context = format_context(results)

    # Step 3: Build the prompt for the LLM.
    prompt = build_rag_prompt(question, context)

    print("\nUSER QUESTION")
    print(question)

    print("\nRETRIEVED EVIDENCE")
    print(context)

    print("\nGENERATING ANSWER WITH THE LLM...")

    # Step 4: Generate the final answer.
    try:
        answer = generate_answer(prompt)
    except (RuntimeError, ValueError) as exc:
        print(f"\nCould not generate an answer: {exc}")
        return

    print("\nREP0RADAR ANSWER")
    print(answer)


if __name__ == "__main__":
    main()
