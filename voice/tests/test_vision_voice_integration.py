"""
Automated Integration Tests for AI Vision (Shanuu) and Voice Interaction (Vyshu).
Verifies that the AI Vision diagnosis payload directly powers the Voice Assistant prompt context.
"""

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from voice.voice_assistant_ai import generate_ai_response, _diagnosis_context


class FakeModel:
    def __init__(self, response_text="Check wire connection after powering off switch."):
        self.response_text = response_text
        self.prompts = []

    def start_chat(self, history):
        class FakeChat:
            def __init__(self, model):
                self.model = model

            def send_message(self, prompt):
                self.model.prompts.append(prompt)
                return SimpleNamespace(text=self.model.response_text)

        return FakeChat(self)


class VisionVoiceIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).resolve().parents[2]
        cls.sample_file = cls.root_dir / "ai_vision" / "sample_diagnosis.json"
        with open(cls.sample_file, "r", encoding="utf-8") as f:
            cls.samples = json.load(f)

    def test_vision_scenario_1_fault_detected_powers_voice_context(self):
        """Scenario 1: Disconnected Jumper Wire (Primary Review-II Setup)."""
        diagnosis = self.samples[0]
        self.assertEqual(diagnosis["status"], "SUCCESS")
        self.assertTrue(diagnosis["fault_detected"])
        self.assertEqual(diagnosis["fault_type"], "DISCONNECTED_WIRE")

        # Format context for Voice assistant
        context = _diagnosis_context(diagnosis, diagnosis_source="ai_vision")

        # Verify Vision fields exist inside Voice context
        self.assertIn("Diagnosis source: AI Vision result", context)
        self.assertIn("Status: SUCCESS", context)
        self.assertIn("Fault detected: True", context)
        self.assertIn("Fault type: DISCONNECTED_WIRE", context)
        self.assertIn("Jumper wire connection between switch and breadboard", context)
        self.assertIn("92%", context)
        self.assertIn("Bounding box", context)

        # Verify Voice model receives Vision context when answering user question
        fake_model = FakeModel()
        reply = generate_ai_response(
            "What should I do to fix this circuit?",
            diagnosis,
            conversation_history=[],
            model=fake_model,
            diagnosis_source="ai_vision",
        )

        self.assertIn("Check wire connection after powering off switch", reply)
        self.assertTrue(len(fake_model.prompts) > 0)
        self.assertIn("DISCONNECTED_WIRE", fake_model.prompts[0])
        self.assertIn("AI Vision result", fake_model.prompts[0])

    def test_vision_scenario_2_normal_circuit_powers_voice_context(self):
        """Scenario 2: Normal Circuit (No Fault Detected)."""
        diagnosis = self.samples[1]
        self.assertEqual(diagnosis["status"], "SUCCESS")
        self.assertFalse(diagnosis["fault_detected"])
        self.assertEqual(diagnosis["fault_type"], "NONE")

        context = _diagnosis_context(diagnosis, diagnosis_source="ai_vision")
        self.assertIn("Fault detected: False", context)
        self.assertIn("Fault type: NONE", context)
        self.assertIn("Circuit loop intact", context)

    def test_vision_scenario_3_unclear_image_powers_voice_context(self):
        """Scenario 3: Blurry / Obscured Image (UNKNOWN Status)."""
        diagnosis = self.samples[2]
        self.assertEqual(diagnosis["status"], "UNKNOWN")
        self.assertFalse(diagnosis["fault_detected"])

        context = _diagnosis_context(diagnosis, diagnosis_source="ai_vision")
        self.assertIn("Status: UNKNOWN", context)
        self.assertIn("Unclear / Obscured", context)


if __name__ == "__main__":
    unittest.main()
