[README.md](https://github.com/user-attachments/files/34212893/README.md)
# RepoRadar — AI Codebase Investigator

RepoRadar is an AI-powered codebase investigation tool designed to help developers understand unfamiliar Python projects. It combines code parsing, dependency analysis, hybrid retrieval, and optional local LLM generation to find relevant code and explain how files relate to one another.

## Problem Statement

Understanding an unfamiliar codebase can take significant time. Developers need to locate relevant functions, trace dependencies, identify files that may be affected by a change, and find appropriate tests.

RepoRadar aims to make these tasks faster by combining static code analysis with retrieval-based AI assistance.

## Features

- **Repository scanning:** Discover Python files for indexing.
- **AST-based code analysis:** Extract structured information from Python source code.
- **Dependency analysis:** Build relationships between files using local import statements.
- **Keyword search:** Find code using relevant words and identifiers.
- **Semantic search:** Retrieve code based on the meaning of a question.
- **Hybrid search:** Combine keyword and semantic results using Reciprocal Rank Fusion (RRF).
- **RAG pipeline:** Retrieve relevant code and construct a grounded prompt for an LLM.
- **Local LLM integration:** Generate answers through Ollama when the required model is available.
- **Change-impact analysis:** Identify files that may be affected by a change.
- **Test recommendations:** Rank potentially relevant tests using dependency relationships and heuristics.
- **Retrieval evaluation:** Measure retrieval quality using metrics such as Hit Rate@K, Recall@K, and Mean Reciprocal Rank (MRR).
- **Streamlit interface:** Explore code search, impact analysis, and test recommendations through a web interface.

## Technology Stack

- Python
- Abstract Syntax Trees (AST)
- Sentence Transformers
- Vector embeddings and semantic retrieval
- Hybrid information retrieval and Reciprocal Rank Fusion
- Retrieval-Augmented Generation (RAG)
- Ollama for local LLM inference
- Streamlit
- Pytest

## Architecture

```text
Python Repository
       |
       v
Repository Scanner
       |
       v
File Index and AST Parser
       |
       +----------------------+
       |                      |
       v                      v
Keyword Search        Semantic Search
       |                      |
       +----------+-----------+
                  |
                  v
             Hybrid Search
                  |
                  v
          Relevant Code Chunks
                  |
                  v
             RAG Prompt
                  |
                  v
          Local Ollama LLM
                  |
                  v
        Evidence-Based Answer

Additional analysis:
Dependency Graph -> Change Impact -> Test Recommendations

Evaluation:
Retrieval Metrics + Citation Path Consistency Checks
```

## Project Structure

```text
RepoRadar/
├── src/
│   └── reporadar/
│       ├── scanner.py
│       ├── indexer.py
│       ├── parser.py
│       ├── dependencies.py
│       ├── search.py
│       ├── chunker.py
│       ├── embeddings.py
│       ├── semantic_search.py
│       ├── hybrid_search.py
│       ├── rag.py
│       ├── llm.py
│       ├── impact.py
│       ├── test_recommender.py
│       ├── evaluation.py
│       └── reliability.py
├── tests/
├── data/
├── streamlit_app.py
├── demo_semantic_search.py
├── demo_hybrid_search.py
├── demo_rag.py
├── demo_impact.py
├── demo_real_impact.py
├── demo_test_recommendations.py
├── demo_evaluation.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

### 1. Prerequisites

- Python 3.11 or a compatible Python version supported by the project's dependencies
- pip
- Ollama and a supported local model for AI-generated answers

### 2. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd RepoRadar
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If script activation is restricted, use the virtual environment's Python executable directly instead.

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure the local language model

Install Ollama, then download the model used by the application:

```bash
ollama pull llama3.2
```

Ensure Ollama is running before requesting AI-generated answers. Code retrieval and search-only functionality should be tested separately from LLM generation.

### 6. Launch the interface

From the project root:

```bash
python -m streamlit run streamlit_app.py
```

Open the local URL printed in the terminal.

The application expects a compatible repository index at `data/index.json`. Generate or refresh this index using the project's indexing workflow before analyzing a different repository.

## Running Tests

Run the complete test suite:

```bash
python -m pytest -v
```

Run an individual test module when debugging a feature:

```bash
python -m pytest tests/test_impact.py -v
```

## Evaluation

RepoRadar includes a retrieval evaluation workflow with metrics such as:

- **Hit Rate@K:** Whether at least one expected relevant file appears among the top K results.
- **Recall@K:** The proportion of expected relevant files retrieved in the top K.
- **Mean Reciprocal Rank (MRR):** How highly the first relevant result is ranked.

Evaluation results depend on the dataset, test questions, expected files, and retrieval configuration. Report measured results from your actual evaluation run rather than assuming a particular accuracy.

## Reliability and Limitations

- Static import analysis may miss dynamic imports, runtime dependencies, and indirect relationships.
- Test recommendations are heuristic suggestions, not guarantees of complete test coverage.
- Retrieval quality depends on the index, chunking strategy, embedding model, and search configuration.
- LLM answers can still be incorrect or incomplete. Retrieved code should be checked before acting on recommendations.
- Citation-path consistency checks do not establish that every claim in an answer is factually correct.
- Local model availability and performance depend on the user's machine and model configuration.

## Future Improvements

- Support additional programming languages.
- Improve symbol-level dependency tracking.
- Add stronger evaluation datasets and answer-quality checks.
- Improve ranking and test recommendation methods.
- Add repository-level configuration and automated index refresh.
- Explore an optional hosted LLM backend.

## Learning Outcomes

This project demonstrates practical experience with Python tooling, AST parsing, embeddings, semantic and hybrid retrieval, RAG, local LLM integration, graph-based impact analysis, automated testing, and retrieval evaluation.

## License

Choose and add an appropriate open-source license before distributing the project.
