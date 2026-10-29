import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from voice.stt_code.stt_service import STTService, sr
from voice.voice_assistant_ai import generate_ai_response, main


DIAGNOSIS = {
    "status": "SUCCESS",
    "fault_detected": True,
    "fault_type": "DISCONNECTED_WIRE",
    "location": "Breadboard row 4",
    "possible_cause": "A jumper appears disconnected.",
    "confidence": 0.82,
    "bounding_box": [10, 20, 30, 40],
}


class FakeChat:
    def __init__(self, model):
        self.model = model

    def send_message(self, prompt):
        self.model.prompts.append(prompt)
        if self.model.error:
            raise self.model.error
        return SimpleNamespace(text=self.model.response_text)


class FakeModel:
    def __init__(self, response_text="Check the jumper after power is disconnected.", error=None):
        self.response_text = response_text
        self.error = error
        self.histories = []
        self.prompts = []

    def start_chat(self, history):
        self.histories.append(history)
        return FakeChat(self)


class FakeTTS:
    def __init__(self):
        self.messages = []

    def speak(self, text):
        self.messages.append(text)


class FakeUnavailableSTT:
    available = False

    def listen(self):
        raise AssertionError("unavailable microphone should use text input")


class VoiceAssistantTests(unittest.TestCase):
    def test_empty_speech_is_returned_as_empty_text(self):
        service = STTService()
        with patch("voice.stt_code.stt_service.sr.Microphone") as microphone:
            microphone.return_value.__enter__.return_value = object()
            with patch.object(service.recognizer, "adjust_for_ambient_noise"):
                with patch.object(service.recognizer, "listen", return_value=object()):
                    with patch.object(
                        service.recognizer,
                        "recognize_google",
                        side_effect=sr.UnknownValueError(),
                    ):
                        self.assertEqual(service.listen(), "")

    def test_microphone_open_failure_marks_stt_unavailable(self):
        service = STTService()
        with patch(
            "voice.stt_code.stt_service.sr.Microphone",
            side_effect=OSError("no microphone"),
        ):
            self.assertEqual(service.listen(), "")
        self.assertFalse(service.available)

    def test_text_input_uses_gemini_and_keeps_session_history(self):
        answers = iter(("What might be wrong?", "How certain is that?", "exit"))
        model = FakeModel()
        tts = FakeTTS()

        main(
            diagnosis=DIAGNOSIS,
            diagnosis_source="mock",
            input_mode="text",
            input_fn=lambda _prompt: next(answers),
            tts_service=tts,
            model=model,
        )

        self.assertEqual(model.histories[0], [])
        self.assertEqual(len(model.histories[1]), 2)
        self.assertEqual(model.histories[1][0], {"role": "user", "parts": ["What might be wrong?"]})
        self.assertIn("MOCK", model.prompts[0])
        self.assertIn("not an actual AI Vision result", model.prompts[0])
        self.assertIn("Bounding box: [10, 20, 30, 40]", model.prompts[0])
        self.assertIn("Never touch live wiring", tts.messages[1])

    def test_unavailable_microphone_switches_to_text(self):
        answers = iter(("Explain the diagnosis", "exit"))
        tts = FakeTTS()
        main(
            diagnosis=DIAGNOSIS,
            input_fn=lambda _prompt: next(answers),
            stt_service=FakeUnavailableSTT(),
            tts_service=tts,
            model=FakeModel(),
        )
        self.assertTrue(any("Microphone unavailable" in message for message in tts.messages))

    def test_missing_api_key_returns_safe_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            answer = generate_ai_response("What does this mean?", DIAGNOSIS, [])
        self.assertIn("Gemini is unavailable", answer)
        self.assertIn("Never touch live wiring", answer)

    def test_diagnosis_context_and_explicit_vision_source(self):
        model = FakeModel()
        generate_ai_response(
            "What is the possible cause?",
            DIAGNOSIS,
            [],
            model=model,
            diagnosis_source="ai_vision",
        )
        prompt = model.prompts[0]
        for field in ("SUCCESS", "DISCONNECTED_WIRE", "Breadboard row 4", "82%", "AI Vision result"):
            self.assertIn(field, prompt)

    def test_network_and_invalid_model_responses_are_handled(self):
        failed = generate_ai_response(
            "Explain this", DIAGNOSIS, [], model=FakeModel(error=ConnectionError())
        )
        invalid = generate_ai_response(
            "Explain this", DIAGNOSIS, [], model=FakeModel(response_text=None)
        )
        self.assertIn("could not get a reliable answer", failed)
        self.assertIn("could not get a reliable answer", invalid)
        self.assertIn("Never touch live wiring", failed)

    def test_unsafe_model_claim_is_replaced_with_safe_fallback(self):
        answer = generate_ai_response(
            "Is it safe now?",
            DIAGNOSIS,
            [],
            model=FakeModel(response_text="The circuit is safe to touch now."),
        )
        self.assertNotIn("safe to touch", answer)
        self.assertIn("could not get a reliable answer", answer)

    def test_mains_question_is_refused_without_calling_model(self):
        model = FakeModel()
        answer = generate_ai_response("How do I repair a wall socket?", DIAGNOSIS, [], model=model)
        self.assertIn("licensed electrician", answer)
        self.assertEqual(model.prompts, [])


if __name__ == "__main__":
    unittest.main()