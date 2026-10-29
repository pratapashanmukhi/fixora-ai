"""
Automated Integration Tests for AI Vision (Shanuu) and Safety Logic (Jyothsna).
Verifies that AI Vision diagnosis outputs correctly drive the Safety & Repair Logic engine.
"""

import json
import unittest
from pathlib import Path

from integrate_vision_safety import evaluate_vision_safety, load_ai_vision_diagnosis


class VisionSafetyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).resolve().parents[2]
        cls.sample_file = cls.root_dir / "ai_vision" / "sample_diagnosis.json"
        with open(cls.sample_file, "r", encoding="utf-8") as f:
            cls.samples = json.load(f)

    def test_disconnected_wire_approved_for_low_voltage_guidance(self):
        """Scenario 1: Disconnected Jumper Wire on low-voltage educational circuit."""
        diagnosis = self.samples[0]
        self.assertEqual(diagnosis["fault_type"], "DISCONNECTED_WIRE")

        report = evaluate_vision_safety(diagnosis)

        self.assertEqual(report["risk"], "LOW")
        self.assertEqual(report["decision"], "APPROVED_GUIDANCE")
        self.assertFalse(report["professional_required"])
        self.assertTrue(len(report["repair_guidance"]) > 0)
        self.assertTrue(any("re-insert the jumper wire" in step for step in report["repair_guidance"]))
        self.assertTrue(any("low-voltage" in p.lower() for p in report["precautions"]))

    def test_normal_circuit_intact_requires_no_repairs(self):
        """Scenario 2: Normal circuit loop intact."""
        diagnosis = self.samples[1]
        self.assertFalse(diagnosis["fault_detected"])

        report = evaluate_vision_safety(diagnosis)

        self.assertEqual(report["risk"], "NONE")
        self.assertEqual(report["decision"], "NORMAL_OPERATION")
        self.assertFalse(report["professional_required"])
        self.assertEqual(report["repair_guidance"], [])

    def test_blurry_unknown_image_blocks_diy_guidance(self):
        """Scenario 3: Blurry/unclear image (UNKNOWN status) must block repair steps."""
        diagnosis = self.samples[2]
        self.assertEqual(diagnosis["status"], "UNKNOWN")

        report = evaluate_vision_safety(diagnosis)

        self.assertEqual(report["risk"], "UNKNOWN")
        self.assertEqual(report["decision"], "STOP_AND_ASSESS")
        self.assertTrue(report["professional_required"])
        self.assertEqual(report["repair_guidance"], [])
        self.assertTrue(any("unverified repair" in p.lower() for p in report["precautions"]))

    def test_danger_signal_escalates_even_low_voltage_circuit(self):
        """Scenario 4: Explicit danger signals (e.g. sparking) must block DIY guidance."""
        diagnosis = self.samples[0]
        report = evaluate_vision_safety(diagnosis, hazard_flags={"sparking": True})

        self.assertEqual(report["risk"], "HIGH")
        self.assertEqual(report["decision"], "STOP_AND_ESCALATE")
        self.assertTrue(report["professional_required"])
        self.assertEqual(report["repair_guidance"], [])
        self.assertTrue(any("qualified professional" in p.lower() for p in report["precautions"]))


if __name__ == "__main__":
    unittest.main()
