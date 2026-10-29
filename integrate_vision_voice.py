"""
FIXORA: AI Vision and Voice Interaction Integration Bridge
Connects Module 1 (AI Vision - Shanuu) with Module 2 (Voice Interaction - Vyshu)
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from voice.voice_assistant_ai import main as voice_main, generate_ai_response


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


def run_integrated_vision_voice(text_mode: bool = True, scenario_index: int = 0):
    """
    Feeds the AI Vision diagnosis into Vyshu's Voice Assistant.
    """
    diagnosis = load_ai_vision_diagnosis(index=scenario_index)

    print("=" * 60)
    print(" FIXORA: AI VISION -> VOICE INTERACTION INTEGRATION")
    print("=" * 60)
    print("1. [AI Vision Module] Loaded Circuit Diagnosis:")
    print(f"   - Status:         {diagnosis.get('status')}")
    print(f"   - Fault Detected: {diagnosis.get('fault_detected')}")
    print(f"   - Fault Type:     {diagnosis.get('fault_type')}")
    print(f"   - Location:       {diagnosis.get('location')}")
    print(f"   - Possible Cause: {diagnosis.get('possible_cause')}")
    print(f"   - Confidence:     {float(diagnosis.get('confidence', 0)):.0%}")
    if "bounding_box" in diagnosis:
        print(f"   - Bounding Box:   {diagnosis.get('bounding_box')}")
    print("-" * 60)
    print("2. [Voice Module] Starting Voice Assistant with Vision Context...")
    print("=" * 60)

    # Launch Vyshu's voice assistant passing Shanuu's vision diagnosis
    voice_main(
        diagnosis=diagnosis,
        diagnosis_source="ai_vision",
        input_mode="text" if text_mode else "auto",
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run FIXORA AI Vision and Voice Integration")
    parser.add_argument("--voice", action="store_true", help="Use microphone instead of text")
    parser.add_argument(
        "--scenario",
        type=int,
        default=0,
        help="0: Disconnected Wire, 1: Normal Circuit, 2: Blurry Image",
    )
    args = parser.parse_args()

    run_integrated_vision_voice(text_mode=not args.voice, scenario_index=args.scenario)
