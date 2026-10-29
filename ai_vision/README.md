# FIXORA — AI Vision & Diagnosis Module

**Tagline:** *SEE IT. UNDERSTAND IT. FIX IT SAFELY.*  
**Project:** FIXORA Home Repair Assistant  
**Module Lead:** Shanmukhi Pratapa (AI Vision Lead)  

---

## 1. Module Structure

```text
ai_vision/
├── README.md                      # Module documentation & quickstart
├── prompts.txt                    # System prompt and JSON contract for Gemini Vision
├── sample_diagnosis.json          # Valid JSON test payloads for all diagnostic states
├── integration_information.md     # Person's final Input/Output format and integration guide
└── gemini_code/
    └── gemini_service.dart        # Core Dart service, BoundingBox & DiagnosisResult models
```

---

## 2. Key Components

- **[`gemini_code/gemini_service.dart`](gemini_code/gemini_service.dart)**: Complete implementation of `GeminiService` (REST client with `x-goog-api-key` header, automatic retry with exponential backoff), `BoundingBox`, and `DiagnosisResult` domain models.
- **[`integration_information.md`](integration_information.md)**: Person's finalized Input/Output format, JSON schemas, and step-by-step integration guide for Likhita's Flutter app (`flutter_app/`).
- **[`prompts.txt`](prompts.txt)**: Multimodal system prompt ensuring Gemini 3.8 Flash inspects low-voltage circuits, locks out AC mains, and returns structured JSON with bounding boxes.
- **[`sample_diagnosis.json`](sample_diagnosis.json)**: Standard sample payloads for fault-detected, normal-circuit, and blurry-image states.

---

## 3. Quick Reference: Final Input & Output

### Input Method
```dart
Future<DiagnosisResult> analyzeCircuitImage(
  Uint8List imageBytes, {
  String mimeType = 'image/jpeg',
})
```

### Output JSON Contract
```json
{
  "status": "SUCCESS",
  "fault_detected": true,
  "fault_type": "DISCONNECTED_WIRE",
  "location": "Jumper wire connection between switch and breadboard terminal",
  "possible_cause": "The jumper wire appears disconnected or unseated, resulting in an open circuit.",
  "confidence": 0.92,
  "bounding_box": {
    "ymin": 0.35,
    "xmin": 0.42,
    "ymax": 0.58,
    "xmax": 0.65
  }
}
```

---

## 4. Running Unit Tests

```bash
dart test test/ai_vision_test.dart
```

---

## 5. Integration Information

For complete details on the person's final input/output specifications and the step-by-step Flutter integration guide, refer to **[`integration_information.md`](integration_information.md)**.
