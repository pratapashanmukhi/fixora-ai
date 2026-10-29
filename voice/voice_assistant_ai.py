"""FIXORA voice assistant with optional Gemini responses and diagnosis context."""

import argparse
import os
import re
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from google import genai
from dotenv import load_dotenv

from .stt_code.stt_service import STTService
from .tts_code.tts_service import TTSService

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL_NAME = "gemini-2.0-flash"
EXIT_COMMANDS = {"exit", "quit", "stop", "bye", "goodbye"}
SAFETY_REMINDER = (
    "Only work with disconnected, low-voltage educational circuits. "
    "Never touch live wiring; an image cannot confirm that a circuit is safe."
)
_MAINS_TERMS = (
    "mains", "230v", "240v", "220v ac", "wall socket", "household wiring",
    "household", "wall outlet", "breaker panel", "breaker box", "120v", "110v",
    "240 volt", "120 volt", "110 volt", "live wire", "neutral wire", "phase wire",
    "high voltage",
)
_UNSAFE_ANSWER = re.compile(
    r"\b(?:safe to (?:touch|handle|work on)|(?:touch|work on) (?:the )?"
    r"(?:live|energized)|(?:the )?(?:circuit|wiring|image|it|this) "
    r"(?:is|looks|seems|appears) (?:completely )?safe|guaranteed safe)\b",
    re.IGNORECASE,
)


def _init_gemini(api_key: str | None = None) -> Any | None:
    """Create the Gemini model lazily so text-only use needs no API key."""
    key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key.lower() in {"your_gemini_api_key_here", "replace_me"}:
        return None
    try:
        return _GeminiModel(genai.Client(api_key=key))
    except Exception as error:
        print(f"[FIXORA] Gemini could not be initialized: {error}")
        return None


class _GeminiModel:
    def __init__(self, client: Any):
        self.client = client

    def start_chat(self, history: list[dict[str, Any]]) -> Any:
        return self.client.chats.create(model=MODEL_NAME, history=history)


def _diagnosis_context(
    diagnosis: Mapping[str, Any] | None,
    diagnosis_source: str | None = None,
) -> str:
    if not isinstance(diagnosis, Mapping):
        return "No circuit diagnosis was provided."

    source = diagnosis_source or str(diagnosis.get("source", "unspecified"))
    source_key = source.strip().lower().replace(" ", "_")
    if source_key in {"mock", "sample", "mock_data", "sample_data"}:
        source_label = "MOCK / sample data; this is not an actual AI Vision result"
    elif source_key in {"ai_vision", "vision", "actual_ai_vision"}:
        source_label = "AI Vision result; this is not a safety verification"
    else:
        source_label = "Unspecified source; do not assume this is an AI Vision result"

    try:
        confidence = float(diagnosis.get("confidence", 0))
        confidence_text = (
            f"{confidence:.0%}" if 0 <= confidence <= 1 else "invalid / unspecified"
        )
    except (TypeError, ValueError):
        confidence_text = "invalid / unspecified"

    fields = (
        ("Status", diagnosis.get("status", "UNKNOWN")),
        ("Fault detected", diagnosis.get("fault_detected", "unspecified")),
        ("Fault type", diagnosis.get("fault_type", "UNKNOWN")),
        ("Location", diagnosis.get("location", "Not specified")),
        ("Possible cause", diagnosis.get("possible_cause", "Not available")),
        ("Confidence", confidence_text),
    )
    lines = [f"Diagnosis source: {source_label}"]
    lines.extend(f"{label}: {value}" for label, value in fields)
    if "bounding_box" in diagnosis:
        lines.append(f"Bounding box: {diagnosis['bounding_box']}")
    return "\n".join(lines)


def _fallback_response(question: str, reason: str) -> str:
    if any(term in question.lower() for term in _MAINS_TERMS):
        answer = (
            "I can only help with low-voltage educational circuits, not household or "
            "mains wiring. Please contact a licensed electrician for that work."
        )
    else:
        answer = reason
    return f"{answer} {SAFETY_REMINDER}"


def _normalized_history(
    conversation_history: Sequence[Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    normalized = []
    for turn in conversation_history or ():
        role = turn.get("role")
        text = turn.get("text")
        if role == "assistant":
            role = "model"
        if role in {"user", "model"} and isinstance(text, str) and text.strip():
            normalized.append({"role": role, "parts": [text.strip()]})
    return normalized


def generate_ai_response(
    question: str,
    diagnosis: Mapping[str, Any] | None,
    conversation_history: Sequence[Mapping[str, Any]] | None,
    model: Any | None = None,
    diagnosis_source: str | None = None,
) -> str:
    """Answer one question with the session diagnosis and preceding turns."""
    question = question.strip() if isinstance(question, str) else ""
    if not question:
        return _fallback_response(
            "", "I did not receive a question. Please enter it again."
        )
    if any(term in question.lower() for term in _MAINS_TERMS):
        return _fallback_response(question, "")

    model = model if model is not None else _init_gemini()
    if model is None:
        return _fallback_response(
            question,
            "Gemini is unavailable, so I cannot reliably interpret the diagnosis. "
            "Check GEMINI_API_KEY and your network, or try again later.",
        )

    prompt = (
        "You are FIXORA, a voice assistant for low-voltage educational circuits.\n"
        f"Session diagnosis:\n{_diagnosis_context(diagnosis, diagnosis_source)}\n\n"
        f"User question: {question}\n\n"
        "Give concise, uncertain guidance for 2-4 spoken sentences. Never claim a "
        "circuit is safe based on an image. Never instruct anyone to touch live or "
        "energized wiring. Limit guidance to low-voltage educational circuits with "
        "power disconnected. Do not provide household mains repair instructions. "
        "Treat mock/sample diagnoses as illustrative data, not actual AI Vision results."
    )
    try:
        chat = model.start_chat(history=_normalized_history(conversation_history))
        response = chat.send_message(prompt)
        answer = getattr(response, "text", None)
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Gemini returned an empty or invalid response")
        answer = answer.strip()
        unsafe_match = _UNSAFE_ANSWER.search(answer)
        if unsafe_match and not re.search(
            r"\b(?:not|never|don't|do not|cannot|can't)\s+$",
            answer[max(0, unsafe_match.start() - 20):unsafe_match.start()],
            re.IGNORECASE,
        ):
            raise ValueError("Gemini response did not meet the safety requirements")
        return f"{answer} {SAFETY_REMINDER}"
    except Exception:
        return _fallback_response(
            question,
            "I could not get a reliable answer from Gemini. Check your network and "
            "try again, or consult a qualified instructor.",
        )


def _greeting(diagnosis: Mapping[str, Any] | None) -> str:
    if not isinstance(diagnosis, Mapping):
        return (
            "Hello, I am FIXORA. Describe your low-voltage educational circuit "
            "question. I do not have a diagnosis for this session yet."
        )
    if diagnosis.get("status") in {"UNKNOWN", "ERROR"}:
        return (
            "The diagnosis is unclear or unavailable. Do not treat it as verified; "
            "you can describe your question or provide a clearer diagnosis."
        )
    if diagnosis.get("fault_detected"):
        return (
            "I have a circuit diagnosis for context, but it does not verify safety. "
            "Please ask about your low-voltage educational circuit."
        )
    return (
        "I have a circuit diagnosis for context, but an image cannot verify safety. "
        "Please ask about your low-voltage educational circuit."
    )


def main(
    diagnosis: Mapping[str, Any] | None = None,
    *,
    input_mode: str = "auto",
    input_fn: Callable[[str], str] = input,
    stt_service: Any | None = None,
    tts_service: Any | None = None,
    model: Any | None = None,
    diagnosis_source: str | None = None,
) -> None:
    """Run a session using voice when possible, with an explicit text fallback."""
    if input_mode not in {"auto", "voice", "text"}:
        raise ValueError("input_mode must be 'auto', 'voice', or 'text'")

    stt = stt_service if stt_service is not None else STTService()
    tts = tts_service if tts_service is not None else TTSService()
    history: list[dict[str, str]] = []
    tts.speak(_greeting(diagnosis))
    if input_mode == "auto" and not getattr(stt, "available", True):
        tts.speak("Microphone unavailable. Switching to text input.")

    while True:
        use_text = input_mode == "text" or not getattr(stt, "available", True)
        if use_text:
            try:
                question = input_fn("FIXORA question (type exit to quit): ").strip()
            except (EOFError, KeyboardInterrupt):
                question = "exit"
        else:
            question = stt.listen()
            if not getattr(stt, "available", True):
                tts.speak("Microphone unavailable. Switching to text input.")
                input_mode = "text"
                continue
            if not question:
                tts.speak("I could not understand that. Please try again or use text input.")
                continue

        if not question:
            tts.speak("Please enter a question, or type exit to quit.")
            continue
        if question.lower() in EXIT_COMMANDS:
            tts.speak("Thank you for using FIXORA. Stay safe.")
            return

        answer = generate_ai_response(
            question,
            diagnosis,
            history,
            model=model,
            diagnosis_source=diagnosis_source,
        )
        tts.speak(answer)
        history.extend(
            ({"role": "user", "text": question}, {"role": "model", "text": answer})
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FIXORA voice interaction assistant")
    parser.add_argument(
        "--text", action="store_true", help="use text input instead of the microphone"
    )
    args = parser.parse_args()
    sample_diagnosis = {
        "status": "SUCCESS",
        "fault_detected": True,
        "fault_type": "DISCONNECTED_WIRE",
        "location": "Jumper wire connection between switch and breadboard",
        "possible_cause": "The jumper wire appears disconnected.",
        "confidence": 0.92,
        "source": "mock",
    }
    main(
        diagnosis=sample_diagnosis,
        diagnosis_source="mock",
        input_mode="text" if args.text else "auto",
    )