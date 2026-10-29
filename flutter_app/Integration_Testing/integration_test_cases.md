# FIXORA Integration Test Cases

## TC01 – Application Launch

Input:
Launch the FIXORA application.

Expected Result:
FIXORA home screen opens successfully.

Status:
Pending

---

## TC02 – Category Selection

Input:
Select Electrical.

Expected Result:
Camera scan screen opens.

Status:
Pending

---

## TC03 – Camera Scan

Input:
Capture an image of the educational circuit.

Expected Result:
Captured image is passed to the AI diagnosis module.

Status:
Pending

---

## TC04 – AI Diagnosis

Input:
Circuit image.

Expected Result:
AI returns structured diagnosis information.

Status:
Passed (Integrated with AI Vision module via GeminiService)

---

## TC05 – Safety Check

Input:
AI diagnosis.

Expected Result:
Safety module returns the appropriate safety classification.

Status:
Pending

---

## TC06 – Repair Guidance

Input:
Safe repair condition.

Expected Result:
Flutter displays the appropriate repair instructions.

Status:
Pending

---

## TC07 – ESP32 Verification

Input:
User completes the repair.

Expected Result:
ESP32 verifies the circuit condition and returns the
defined verification status.

Status:
Pending

---

## TC08 – Successful Repair

Input:
ESP32 returns VERIFIED.

Expected Result:
Flutter displays REPAIR VERIFIED.

Status:
Pending

---

## TC09 – Failed Repair

Input:
ESP32 returns a failed verification state.

Expected Result:
Flutter informs the user that the repair has not been verified.

Status:
Pending

---

## TC10 – Unsafe Condition

Input:
Safety module returns UNSAFE.

Expected Result:
Flutter blocks DIY repair guidance and displays an
appropriate safety warning.

Status:
Pending
