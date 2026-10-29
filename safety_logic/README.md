
# FIXORA — Safety & Repair Logic Module

## Purpose
Evaluates diagnosed household faults and returns risk levels, safety precautions, repair guidance, and escalation decisions.

## Technology
- Python
- Jupyter Notebook
- Python module: FIXORA_Safety_Logic.py

## Main function
`assess_fault(fault_id, hazard_flags=None)`

## Input
- `fault_id`: Identifier for the diagnosed fault.
- `hazard_flags`: Optional dictionary of hazard indicators.

Example:
`assess_fault("sparking_switchboard")`

## Output
- Fault identifier
- Risk level
- Safety decision
- Safety precautions
- Approved repair guidance
- Whether a professional is required

## Safety behavior
- Recognized low-risk faults may receive approved basic guidance.
- Dangerous conditions block DIY repair instructions.
- Unknown faults receive no DIY repair instructions.
- The system depends on accurate inputs and needs further validation before real-world use.

## Integration
The AI Vision module should provide agreed fault identifiers. The Flutter interface should display the returned risk, precautions, decision, and permitted guidance.
