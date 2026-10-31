
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_MODEL = "llama3.2:1b"
DEFAULT_API_URL = "http://localhost:11434/api/generate"


def generate_answer(
    prompt: str,
    model: str = DEFAULT_MODEL,
    api_url: str = DEFAULT_API_URL,
    timeout: int = 180,
) -> str:
    """Send a prompt to a local Ollama model and return its answer."""

    if not prompt or not prompt.strip():
        raise ValueError("Prompt must not be empty")

    if not model or not model.strip():
        raise ValueError("Model name must not be empty")

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    request = Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))

    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        if detail:
            detail = f" {detail[:500]}"
        raise RuntimeError(
            f"Ollama returned HTTP error {exc.code}.{detail}"
        ) from exc

    except URLError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure Ollama is "
            "installed and running at the configured API URL."
        ) from exc

    except TimeoutError as exc:
        raise RuntimeError(
            "The LLM request timed out. Try again or use a smaller model."
        ) from exc

    answer = result.get("response", "").strip()

    if not answer:
        raise RuntimeError("The model returned an empty answer")

    return answer
