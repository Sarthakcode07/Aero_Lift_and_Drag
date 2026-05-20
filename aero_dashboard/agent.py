import requests
import time
from typing import List

OLLAMA_MODEL = "mistral"
OLLAMA_API_URL = "http://localhost:11434/api/generate"


def check_ollama_connection() -> bool:
    """Check if Ollama service is running and accessible."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False


def get_ollama_models() -> List[str]:
    """Return a list of available Ollama model names (best-effort).

    Falls back to an empty list if the service is unavailable or the
    response can't be parsed.
    """
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=3)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            models = []
            for k, v in data.items():
                models.append(k)
                if isinstance(v, list):
                    for tag in v:
                        models.append(f"{k}:{tag}")
            return models
        if isinstance(data, list):
            return [str(x) for x in data]
        return []
    except Exception:
        return []


def build_flight_context(
    rho: float,
    velocity: float,
    wing_area: float,
    lift_coefficient: float,
    drag_coefficient: float,
    lift_n: float,
    drag_n: float,
    ld_ratio: float,
) -> str:
    """Format current dashboard values for the AI prompt."""
    return f"""Current flight / aerodynamic data from the dashboard:
- Air density (rho): {rho:.4f} kg/m^3
- Velocity (v): {velocity:.2f} m/s
- Wing area (S): {wing_area:.2f} m^2
- Lift coefficient (Cl): {lift_coefficient:.4f}
- Drag coefficient (Cd): {drag_coefficient:.4f}
- Calculated lift (L): {lift_n:.2f} N
- Calculated drag (D): {drag_n:.2f} N
- Lift-to-drag ratio (L/D): {ld_ratio:.2f}
- Formulas: L = 0.5 * rho * v^2 * S * Cl; D = 0.5 * rho * v^2 * S * Cd"""


def ask_aero_agent(
    question: str,
    flight_context: str,
    conversation_history: str = "",
    model: str | None = None,
) -> str:
    """Send the user question and flight data to Ollama.

    `model` overrides the default `OLLAMA_MODEL` when provided.
    """
    system_instruction = (
        "You are a senior aeronautical engineer with deep expertise in "
        "aerodynamics, aircraft performance, and wing design. Analyse the "
        "provided dashboard data when answering. Be clear, technical, and "
        "practical. Use SI units. If data is missing or unrealistic, note that."
    )

    history_section = ""
    if conversation_history.strip():
        history_section = f"Previous conversation:\n{conversation_history}\n\n"

    prompt = f"""{system_instruction}

{flight_context}

{history_section}User question:
{question}
"""

    model_name = model or OLLAMA_MODEL

    max_retries = 3

    def _try_model_once(model_to_try: str):
        """Attempt to call Ollama with `model_to_try` using retries.

        Returns (success, response_obj_or_None, error_message_or_None).
        """
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    OLLAMA_API_URL,
                    json={"model": model_to_try, "prompt": prompt, "stream": False},
                    timeout=60,
                )

                if response.status_code == 503:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    try:
                        err = response.json()
                    except Exception:
                        err = response.text
                    return False, response, f"503: {err}"

                response.raise_for_status()
                return True, response, None

            except requests.exceptions.ConnectionError:
                return False, None, "connection"
            except requests.exceptions.RequestException as re:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return False, None, str(re)

        return False, None, "unknown"

    success, resp, err = _try_model_once(model_name)
    if success and resp is not None:
        return resp.json().get("response", "No response returned from the model.")

    if err and isinstance(err, str) and err.startswith("503"):
        alternatives = get_ollama_models()
        for alt in alternatives:
            if alt == model_name:
                continue
            success_alt, resp_alt, err_alt = _try_model_once(alt)
            if success_alt and resp_alt is not None:
                return resp_alt.json().get("response", "No response returned from the model.")

    if err == "connection":
        raise ConnectionError(
            "Cannot connect to Ollama. Please ensure Ollama is running at localhost:11434"
        )

    raise RuntimeError(f"Ollama error: {err or 'unknown error'}")
