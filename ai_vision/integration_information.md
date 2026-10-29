# AI Vision & Diagnosis Module — Final Input/Output Format & Integration Information

**Project:** FIXORA — AI-Powered Home Repair Assistant  
**Module:** AI Vision & Diagnosis  
**Contributor (Person):** Shanmukhi Pratapa (AI Vision Lead)  
**Integration Partner:** Likhita (Flutter Application Lead) & FIXORA Team  
**Model:** Google Gemini Vision (`gemini-3.8-flash`) via Google AI Studio REST API  

---

## 1. Overview & Purpose

The **AI Vision & Diagnosis** module is the visual intelligence engine of FIXORA. When a user captures an image of a low-voltage educational circuit (ESP32, solderless breadboard, switch, 220-ohm resistor, 5V LED, jumper wires), this module:
1. Encodes the image bytes and dispatches a multimodal request to Google Gemini Vision (`gemini-3.8-flash`).
2. Enforces structured JSON output via API-level schema constraints.
3. Automatically retries transient network rate limits (HTTP 429) or server errors (HTTP 503) using exponential backoff.
4. Returns a strongly typed `DiagnosisResult` domain model with fault identification, component location, possible cause, confidence score, and normalized bounding box coordinates for camera UI overlay.

---

## 2. Person's Final Input Format

### A. Method Signature (Application Entry Point)
```dart
Future<DiagnosisResult> analyzeCircuitImage(
  Uint8List imageBytes, {
  String mimeType = 'image/jpeg',
})
```

### B. Input Parameter Specifications
| Parameter | Type | Required | Description |
|---|---|---|---|
| `imageBytes` | `Uint8List` | Yes | Raw image bytes captured from Flutter's camera controller (`await file.readAsBytes()`) or image picker. Cannot be empty. |
| `mimeType` | `String` | Optional | MIME type of the image (`'image/jpeg'` or `'image/png'`). Defaults to `'image/jpeg'`. |

### C. Recommended Image Capture Guidelines
- **Resolution:** 720p to 1080p (recommended: 1024x768 to 1920x1080).
- **Framing:** The solderless breadboard, switch, ESP32, and wire terminals should fill at least 60% of the viewfinder.
- **Lighting:** Adequate, even illumination without strong glare on metallic jumper wire pins.

### D. Outgoing HTTP REST Request Payload (to Gemini 3.8 Flash)
- **Endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent`
- **Headers:**
  - `Content-Type: application/json`
  - `x-goog-api-key: <GEMINI_API_KEY>`
- **Payload Structure:**
  ```json
  {
    "contents": [
      {
        "parts": [
          { "text": "<System Prompt from prompts.txt>" },
          {
            "inline_data": {
              "mime_type": "image/jpeg",
              "data": "<Base64 Encoded Image String>"
            }
          }
        ]
      }
    ],
    "generationConfig": {
      "response_mime_type": "application/json",
      "temperature": 0.1
    }
  }
  ```

---

## 3. Person's Final Output Format

### A. Standard 6-Field JSON Contract (+ Bounding Box)
The AI Vision module parses and validates the Gemini response into this exact JSON contract:

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

### B. Field Specifications & Allowed Values
| Field Name | Type | Allowed Values | Description |
|---|---|---|---|
| `status` | `String` | `"SUCCESS"`, `"UNKNOWN"`, `"ERROR"` | Overall diagnostic execution state. |
| `fault_detected` | `bool` | `true`, `false` | Indicates whether a visible wiring fault was detected. |
| `fault_type` | `String` | `"NONE"`, `"DISCONNECTED_WIRE"`, `"LOOSE_WIRE"`, `"WRONG_CONNECTION"`, `"UNKNOWN"` | Standardized electrical fault classification. |
| `location` | `String` | Plain text | Specific terminal, breadboard row, or component connection point. |
| `possible_cause` | `String` | Plain text | Concise root cause explanation for the user. |
| `confidence` | `double` | `0.0` to `1.0` | Model confidence score (clamped between 0.0 and 1.0). |
| `bounding_box` | `Map` (optional) | `{ "ymin": float, "xmin": float, "ymax": float, "xmax": float }` | Normalized coordinates (`0.0` to `1.0`) for camera UI highlight box. |

### C. Sample Payloads for Each Diagnostic State

#### 1. Fault Detected State (Primary Scenario: Disconnected Jumper Wire)
```json
{
  "status": "SUCCESS",
  "fault_detected": true,
  "fault_type": "DISCONNECTED_WIRE",
  "location": "Jumper wire connection between switch and breadboard",
  "possible_cause": "The jumper wire appears disconnected from the breadboard, creating an open circuit.",
  "confidence": 0.92,
  "bounding_box": {
    "ymin": 0.35,
    "xmin": 0.42,
    "ymax": 0.58,
    "xmax": 0.65
  }
}
```

#### 2. Normal Closed Circuit State (No Fault)
```json
{
  "status": "SUCCESS",
  "fault_detected": false,
  "fault_type": "NONE",
  "location": "Circuit loop intact",
  "possible_cause": "All visible jumper wire connections between ESP32, switch, 220-ohm resistor, and LED appear properly seated with no visible open connection.",
  "confidence": 0.95
}
```

#### 3. Blurry or Unclear Image State
```json
{
  "status": "UNKNOWN",
  "fault_detected": false,
  "fault_type": "UNKNOWN",
  "location": "Unclear / Obscured",
  "possible_cause": "The captured image is blurry, poorly illuminated, or does not clearly display the breadboard terminals.",
  "confidence": 0.0
}
```

#### 4. Network / Timeout Error State
```json
{
  "status": "ERROR",
  "fault_detected": false,
  "fault_type": "UNKNOWN",
  "location": "System Error",
  "possible_cause": "Request timed out after multiple attempts.",
  "confidence": 0.0
}
```

---

## 4. Integration Guide for Likhita's Flutter App (`flutter_app/`)

### Step 1: Add Dependencies in `flutter_app/pubspec.yaml`
Ensure `http` is declared under dependencies:
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0
```

### Step 2: Implement `flutter_app/lib/services/gemini_service.dart`
Connect `flutter_app/lib/services/gemini_service.dart` to the AI Vision module using this ready-to-use adapter:

```dart
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import '../../../ai_vision/gemini_code/gemini_service.dart' as ai;
import '../models/diagnosis.dart';

class GeminiService {
  final ai.GeminiService _service;

  GeminiService({String? apiKey, http.Client? client})
      : _service = ai.GeminiService(
          apiKey: apiKey,
          httpClient: client,
          maxRetries: 2,
        );

  /// Analyzes circuit image and maps to the app's Diagnosis model.
  Future<Diagnosis> diagnoseCircuit(Uint8List imageBytes) async {
    final ai.DiagnosisResult result = await _service.analyzeCircuitImage(imageBytes);

    // Map AI Vision result to the Flutter app's Diagnosis domain model
    return Diagnosis(
      faultDetected: result.faultDetected,
      faultType: result.faultType,
      location: result.location,
      possibleCause: result.possibleCause,
      confidence: result.confidence >= 0.8
          ? 'High'
          : result.confidence >= 0.5
              ? 'Medium'
              : 'Low',
      safetyRisk: result.faultDetected
          ? 'Low-Voltage Educational Setup (Turn off switch before fixing)'
          : 'None / Normal Operation',
    );
  }
}
```

### Step 3: Wire into `CameraScreen` & `DiagnosisScreen`
In `flutter_app/lib/screens/camera_screen.dart`:
```dart
// After capturing image:
final Uint8List imageBytes = await capturedFile.readAsBytes();
final geminiService = GeminiService();
final diagnosis = await geminiService.diagnoseCircuit(imageBytes);

Navigator.push(
  context,
  MaterialPageRoute(
    builder: (_) => DiagnosisScreen(diagnosis: diagnosis, imageBytes: imageBytes),
  ),
);
```

In `flutter_app/lib/screens/diagnosis_screen.dart`:
Consume the dynamic `diagnosis.faultType`, `diagnosis.location`, `diagnosis.possibleCause`, and `diagnosis.confidence`.

### Step 4: Run Application with Compile-Time API Key
```bash
flutter run --dart-define=GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

---

## 5. Summary of Module Structure

```text
ai_vision/
├── README.md                      # Module overview & quick reference
├── prompts.txt                    # System prompt & schema boundaries
├── sample_diagnosis.json          # Verified sample payloads
├── integration_information.md     # This comprehensive I/O & integration document
└── gemini_code/
    └── gemini_service.dart        # Core Dart implementation (GeminiService + BoundingBox + DiagnosisResult)
```

---
*Document verified and prepared for FIXORA Core Team integration.*
