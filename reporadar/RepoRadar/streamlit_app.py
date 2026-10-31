
import json
import sys
from pathlib import Path

import streamlit as st


# The app is in the parent folder; the Python project is in RepoRadar/.
PROJECT_ROOT = Path(__file__).resolve().parent / "RepoRadar"
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from reporadar.dependency import build_dependency_graph
from reporadar.impact import analyze_impact
from reporadar.test_recommender import recommend_tests
from reporadar.hybrid_search import hybrid_search
from reporadar.rag import (
    retrieve_context,
    format_context,
    build_rag_prompt,
)
from reporadar.llm import DEFAULT_MODEL, generate_answer


INDEX_PATH = PROJECT_ROOT / "data" / "index.json"


st.set_page_config(
    page_title="RepoRadar",
    page_icon="🔎",
    layout="wide",
)


@st.cache_data
def load_index(index_path, modified_time):
    """Load the repository index and cache it until the file changes."""
    with open(index_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_index():
    if not INDEX_PATH.exists():
        st.error(f"Repository index not found: {INDEX_PATH}")
        st.info(
            "Generate the index first, then restart or refresh the app."
        )
        return None

    try:
        return load_index(str(INDEX_PATH), INDEX_PATH.stat().st_mtime)
    except (OSError, json.JSONDecodeError) as exc:
        st.error(f"Could not load the repository index: {exc}")
        return None


def main():
    st.title("🔎 RepoRadar")
    st.caption(
        "AI Codebase Investigator — search code, ask questions, "
        "analyze changes, and recommend tests."
    )

    index = get_index()

    if index is None:
        st.stop()

    try:
        forward_graph = build_dependency_graph(index)
    except (KeyError, TypeError, ValueError) as exc:
        st.error(f"Could not build the dependency graph: {exc}")
        st.stop()

    if not forward_graph:
        st.warning("No Python files were found in the repository index.")
        st.stop()

    with st.sidebar:
        st.header("Repository")
        st.write(f"**Indexed Python files:** {len(forward_graph)}")
        st.code(str(INDEX_PATH), language="text")
        st.caption(
            "This app analyzes the files present in the current index."
        )

    ask_tab, impact_tab, tests_tab = st.tabs(
        ["💬 Ask your codebase", "🔗 Change impact", "🧪 Test recommendations"]
    )

    # ---------------------------------------------------------
    # TAB 1: Search and ask questions about the codebase.
    # ---------------------------------------------------------
    with ask_tab:
        st.subheader("Ask your codebase")
        st.write(
            "Search for relevant code and optionally generate an "
            "answer using your locally configured Ollama model."
        )

        with st.form("question_form"):
            question = st.text_area(
                "Your question",
                placeholder=(
                    "Where is authentication implemented? "
                    "Which function validates credentials?"
                ),
            )

            top_k = st.slider(
                "Number of code results",
                min_value=1,
                max_value=10,
                value=5,
            )

            ollama_model = st.text_input(
                "Ollama model",
                value=DEFAULT_MODEL,
                help=(
                    "Use a model installed in Ollama. If model loading runs "
                    "out of memory, try a smaller model."
                ),
            )

            search_only = st.checkbox(
                "Search only (do not call the language model)",
                value=False,
            )

            ask_submitted = st.form_submit_button(
                "Search codebase",
                type="primary",
            )

        if ask_submitted:
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                try:
                    with st.spinner("Searching the repository..."):
                        results = hybrid_search(
                            index,
                            question,
                            top_k=top_k,
                        )

                    st.subheader("Retrieved code evidence")

                    if not results:
                        st.warning(
                            "No relevant code was retrieved. "
                            "Try rephrasing the question."
                        )
                    else:
                        for number, result in enumerate(results, start=1):
                            path = result.get("path", "Unknown file")
                            start = result.get("start_line")
                            end = result.get("end_line")

                            if start is not None and end is not None:
                                location = f"{path}:{start}-{end}"
                            else:
                                location = path

                            with st.expander(
                                f"{number}. {location}",
                                expanded=(number == 1),
                            ):
                                st.caption(
                                    "Search sources: "
                                    + ", ".join(
                                        result.get("source_types", [])
                                    )
                                )
                                st.code(
                                    result.get("text", ""),
                                    language="python",
                                )

                    if not search_only:
                        if not ollama_model.strip():
                            st.warning(
                                "Enter an Ollama model name or select "
                                "Search only."
                            )
                        else:
                            with st.spinner(
                                "Generating an evidence-based answer..."
                            ):
                                context_results = retrieve_context(
                                    index,
                                    question,
                                    top_k=top_k,
                                )
                                context = format_context(context_results)
                                prompt = build_rag_prompt(question, context)

                            try:
                                answer = generate_answer(
                                    prompt,
                                    model=ollama_model.strip(),
                                )
                            except RuntimeError as exc:
                                error_detail = str(exc)
                                if (
                                    "bad_alloc" in error_detail.lower()
                                    or "error loading model"
                                    in error_detail.lower()
                                ):
                                    st.error(
                                        "Ollama could not load this model, "
                                        "likely because it does not have "
                                        "enough available memory."
                                    )
                                    st.info(
                                        "Try a smaller model, for example "
                                        "`ollama pull llama3.2:1b`, then "
                                        "enter `llama3.2:1b` above. You can "
                                        "also enable Search only to use "
                                        "retrieval without Ollama."
                                    )
                                else:
                                    st.error(
                                        "Ollama could not generate an answer."
                                    )

                                with st.expander("Ollama error details"):
                                    st.code(error_detail)
                            else:
                                st.subheader("AI answer")
                                st.write(answer)

                                with st.expander("Inspect the RAG prompt"):
                                    st.text(prompt)

                except Exception as exc:
                    st.error(
                        "The search or answer-generation operation failed."
                    )
                    st.exception(exc)

                    st.info(
                        "For AI answers, check that Ollama is running "
                        "and the configured model is installed. "
                        "You can enable Search only to use retrieval "
                        "without calling the language model."
                    )

    # ---------------------------------------------------------
    # TAB 2: Change-impact analysis.
    # ---------------------------------------------------------
    with impact_tab:
        st.subheader("Change-impact analysis")
        st.write(
            "Select a file to identify other indexed files that "
            "may be affected by a change."
        )

        file_paths = sorted(forward_graph)

        changed_file = st.selectbox(
            "Changed file",
            options=file_paths,
            key="impact_changed_file",
        )

        if st.button("Analyze impact", type="primary"):
            try:
                result = analyze_impact(changed_file, forward_graph)

                first, second, third = st.columns(3)
                first.metric(
                    "Directly affected",
                    len(result["directly_affected"]),
                )
                second.metric(
                    "Transitively affected",
                    len(result["transitively_affected"]),
                )
                third.metric(
                    "Total affected",
                    result["total_affected"],
                )

                st.markdown("#### Directly affected files")
                if result["directly_affected"]:
                    for path in result["directly_affected"]:
                        st.write(f"- `{path}`")
                else:
                    st.write("No direct dependents identified.")

                st.markdown("#### Transitively affected files")
                if result["transitively_affected"]:
                    for path in result["transitively_affected"]:
                        st.write(f"- `{path}`")
                else:
                    st.write("No transitive dependents identified.")

                with st.expander("View impact paths"):
                    if result["impact_paths"]:
                        for path, dependency_path in (
                            result["impact_paths"].items()
                        ):
                            st.code(" -> ".join(dependency_path))
                    else:
                        st.write("No impact paths identified.")

                st.caption(
                    "Results are inferred from static import relationships "
                    "and may not capture every runtime dependency."
                )

            except (KeyError, TypeError, ValueError) as exc:
                st.error(f"Impact analysis failed: {exc}")

    # ---------------------------------------------------------
    # TAB 3: Test recommendations.
    # ---------------------------------------------------------
    with tests_tab:
        st.subheader("Test recommendations")
        st.write(
            "Prioritize tests that import the changed file or "
            "other files identified by impact analysis."
        )

        test_changed_file = st.selectbox(
            "File being changed",
            options=sorted(forward_graph),
            key="test_changed_file",
        )

        if st.button("Recommend tests", type="primary"):
            try:
                impact = analyze_impact(
                    test_changed_file,
                    forward_graph,
                )

                recommendations = recommend_tests(
                    test_changed_file,
                    impact,
                    forward_graph,
                )

                if not recommendations:
                    st.warning(
                        "No relevant tests were identified. "
                        "Consider running the full test suite."
                    )
                else:
                    st.success(
                        f"Found {len(recommendations)} test recommendation(s)."
                    )

                    for number, item in enumerate(
                        recommendations,
                        start=1,
                    ):
                        with st.expander(
                            f"{number}. {item['path']} "
                            f"(priority {item['priority']})",
                            expanded=(number == 1),
                        ):
                            st.write("**Reasons**")
                            for reason in item["reasons"]:
                                st.write(f"- {reason}")

                st.caption(
                    "Recommendations are heuristics, not a guarantee "
                    "that these tests cover every affected behavior."
                )

            except (KeyError, TypeError, ValueError) as exc:
                st.error(f"Test recommendation failed: {exc}")


if __name__ == "__main__":
    main()
