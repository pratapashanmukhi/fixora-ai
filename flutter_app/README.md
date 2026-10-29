# FIXORA – Flutter App & Integration

## Module

Flutter App & Integration

## Responsibility

This module is responsible for developing the FIXORA mobile application
and integrating the AI Vision, Safety Logic, Voice, ESP32 and Firebase
modules into a single user-facing application.

## Objective

The Flutter application provides the main interface through which a user
can:

1. Select a repair category.
2. Capture an image of the faulty setup.
3. Receive an AI-based diagnosis.
4. View the safety assessment.
5. Follow repair instructions.
6. Verify the repair using the ESP32 hardware.
7. Receive a final repair verification result.

## Main Workflow

Home
→ Category Selection
→ Camera Scan
→ AI Diagnosis
→ Safety Check
→ Repair Guidance
→ ESP32 Verification
→ Repair Verified

## Primary Demonstration

The primary demonstration is an electrical low-voltage educational
circuit using the ESP32 prototype.

The intended demonstration is:

Circuit Fault
→ Camera Scan
→ AI Diagnosis
→ Safety Check
→ Repair Guidance
→ User Repairs Circuit
→ ESP32 Verification
→ Repair Verified

## Flutter Responsibilities

- User interface development
- Screen navigation
- Camera interface
- AI diagnosis integration
- Safety result presentation
- Repair guidance presentation
- Voice interface integration
- ESP32 communication integration
- Firebase integration
- Error handling
- End-to-end testing

## Integration Dependencies

The Flutter application depends on the following project modules:

### AI Vision
Provides image analysis and structured diagnosis information.

### Safety
Provides safety classification and repair restrictions.

### Voice
Provides speech-to-text and text-to-speech functionality.

### ESP32
Provides physical circuit verification.

### Backend
Provides Firebase-based session and repair information storage.

## Status

Flutter UI prototype and module integration are developed progressively
as the other project modules become available.

## Security

API keys, authentication tokens, passwords and private credentials must
not be committed to the GitHub repository.
