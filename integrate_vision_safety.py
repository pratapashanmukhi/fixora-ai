"""
FIXORA: AI Vision and Safety Logic Integration Bridge
Connects Module 1 (AI Vision - Shanuu) with Module 4 (Safety & Repair Logic - Jyothsna)
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from safety_logic.FIXORA_Safety_Logic import assess_fault


def load_ai_vision_diagnosis(index: int = 0) -> dict:
    """Loads the official AI Vision diagnosis output from ai_vision/sample_diagnosis.json."""
    sample_file = root_dir / "ai_vision" / "sample_diagnosis.json"
    if not sample_file.exists():
        raise FileNotFoundError(f"AI Vision sample file not found at: {sample_file}")

    with open(sample_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list) and len(data) > index:
        diagnosis = data[index]
    elif isinstance(data, dict):
        diagnosis = data
    else:
        raise ValueError("Invalid format in sample_diagnosis.json")

    return diagnosis


def evaluate_vision_safety(diagnosis: dict, hazard_flags: dict = None) -> dict:
    """
    Evaluates an AI Vision diagnosis through the Safety & Repair Logic engine.
    """
    status = diagnosis.get("status", "UNKNOWN").upper()
    fault_detected = diagnosis.get("fault_detected", False)
    fault_type = diagnosis.get("fault_type", "UNKNOWN")

    # If the image was blurry or unverified by AI Vision, safety rules require STOP_AND_ASSESS
    if status == "UNKNOWN" or not fault_detected:
        if status == "SUCCESS" and not fault_detected:
            # Intact circuit
            return {
                "fault": "circuit_intact",
                "risk": "NONE",
                "decision": "NORMAL_OPERATION",
                "precautions": ["Circuit is complete and intact. No repairs needed."],
                "repair_guidance": [],
                "professional_required": False,
                "ai_vision_diagnosis": diagnosis,
            }
        else:
            fault_id = "unknown_fault"
    else:
        # Normalize AI Vision fault_type (e.g. 'DISCONNECTED_WIRE' -> 'disconnected_wire')
        fault_id = fault_type.strip().lower()

    # Run through Jyothsna's assess_fault engine
    safety_report = assess_fault(fault_id, hazard_flags=hazard_flags)
    safety_report["ai_vision_diagnosis"] = diagnosis
    return safety_report


def display_integrated_report(diagnosis_index: int = 0, hazard_flags: dict = None):
    diagnosis = load_ai_vision_diagnosis(index=diagnosis_index)
    report = evaluate_vision_safety(diagnosis, hazard_flags=hazard_flags)

    print("=" * 60)
    print(" FIXORA: AI VISION -> SAFETY & REPAIR LOGIC INTEGRATION")
    print("=" * 60)
    print("1. [AI Vision Module Output]")
    print(f"   - Status:         {diagnosis.get('status')}")
    print(f"   - Fault Detected: {diagnosis.get('fault_detected')}")
    print(f"   - Fault Type:     {diagnosis.get('fault_type')}")
    print(f"   - Location:       {diagnosis.get('location')}")
    print(f"   - Possible Cause: {diagnosis.get('possible_cause')}")
    print(f"   - Confidence:     {float(diagnosis.get('confidence', 0)):.0%}")
    print("-" * 60)
    print("2. [Safety Engine Evaluation (Jyothsna)]")
    print(f"   - Safety Decision: {report['decision']}")
    print(f"   - Risk Level:      {report['risk']}")
    print(f"   - Pro Required:    {report['professional_required']}")
    print("\n   Precautions:")
    for p in report["precautions"]:
        print(f"   - {p}")

    print("\n   Approved Repair Guidance:")
    if report["repair_guidance"]:
        for idx, step in enumerate(report["repair_guidance"], start=1):
            print(f"   {idx}. {step}")
    else:
        print("   [BLOCKED] DIY repair guidance is not permitted for this condition.")
    print("=" * 60)
    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run FIXORA AI Vision & Safety Logic Integration")
    parser.add_argument(
        "--scenario",
        type=int,
        default=0,
        help="0: Disconnected Wire, 1: Normal Circuit, 2: Blurry Image",
    )
    parser.add_argument(
        "--danger",
        action="store_true",
        help="Simulate a danger signal (e.g., sparking or burning smell)",
    )
    args = parser.parse_args()

    hazards = {"sparking": True} if args.danger else None
    display_integrated_report(diagnosis_index=args.scenario, hazard_flags=hazards)
