#!/usr/bin/env python
# coding: utf-8

# In[1]:


print("====================================")
print("       FIXORA HOME REPAIR AI")
print("       Safety & Repair Logic")
print("====================================")

print("Module started successfully!")
print("Purpose: Assess repair risks and safety.")


# In[2]:


def assess_repair(fault):
    if fault == "loose_cabinet_handle":
        return {
            "risk": "LOW",
            "decision": "APPROVED_GUIDANCE",
            "message": "Follow approved basic repair instructions."
        }

    elif fault == "dripping_pipe_near_electricity":
        return {
            "risk": "MEDIUM",
            "decision": "RESTRICTED_GUIDANCE",
            "message": "Stay away from wet electrical equipment."
        }

    elif fault == "sparking_switchboard":
        return {
            "risk": "HIGH",
            "decision": "STOP_AND_ESCALATE",
            "message": "Keep away and contact a qualified electrician."
        }

    else:
        return {
            "risk": "UNKNOWN",
            "decision": "STOP_AND_ASSESS",
            "message": "Do not attempt an unverified repair."
        }


result = assess_repair("sparking_switchboard")

print("FIXORA SAFETY REPORT")
print("--------------------")
print("Risk:", result["risk"])
print("Decision:", result["decision"])
print("Message:", result["message"])


# In[3]:


assess_repair("loose_cabinet_handle")


# In[4]:


assess_repair("unknown_fault")


# In[5]:


# FIXORA: Test the safety decision system

test_faults = [
    "loose_cabinet_handle",
    "dripping_pipe_near_electricity",
    "sparking_switchboard",
    "unknown_fault"
]

for fault in test_faults:
    result = assess_repair(fault)

    print("\nFault:", fault)
    print("Risk:", result["risk"])
    print("Decision:", result["decision"])
    print("Safety message:", result["message"])
    print("-" * 40)


# In[6]:


def get_repair_decision(fault):
    result = assess_repair(fault)

    if result["decision"] == "APPROVED_GUIDANCE":
        action = "Show approved basic repair guidance"

    elif result["decision"] == "RESTRICTED_GUIDANCE":
        action = "Show safety precautions; do not proceed near the hazard"

    elif result["decision"] == "STOP_AND_ESCALATE":
        action = "Stop DIY guidance and recommend a qualified professional"

    else:
        action = "Do not show repair steps until the fault is verified"

    return {
        "fault": fault,
        "risk": result["risk"],
        "decision": result["decision"],
        "recommended_action": action
    }


report = get_repair_decision("sparking_switchboard")
print(report)


# In[7]:


import json

repair_knowledge_base = {
    "loose_cabinet_handle": {
        "risk": "LOW",
        "decision": "APPROVED_GUIDANCE",
        "precautions": [
            "Keep fingers clear of pinch points.",
            "Use the correct screwdriver."
        ],
        "repair_guidance": [
            "Check whether the handle screw is loose.",
            "If appropriate, gently tighten it with the correct tool.",
            "Check that the handle is secure."
        ],
        "professional_required": False
    },

    "dripping_pipe_near_electricity": {
        "risk": "HIGH",
        "decision": "STOP_AND_ESCALATE",
        "precautions": [
            "Do not touch wet electrical equipment.",
            "Keep people away from the affected area."
        ],
        "repair_guidance": [],
        "professional_required": True
    },

    "sparking_switchboard": {
        "risk": "HIGH",
        "decision": "STOP_AND_ESCALATE",
        "precautions": [
            "Keep away from the switchboard.",
            "Do not touch it or attempt a repair.",
            "Contact a qualified electrician."
        ],
        "repair_guidance": [],
        "professional_required": True
    }
}

print(json.dumps(repair_knowledge_base, indent=4))


# In[8]:


def get_fault_details(fault):
    details = repair_knowledge_base.get(fault)

    if details is None:
        return {
            "risk": "UNKNOWN",
            "decision": "STOP_AND_ASSESS",
            "precautions": [
                "Do not attempt an unverified repair."
            ],
            "repair_guidance": [],
            "professional_required": True
        }

    return details


fault = "sparking_switchboard"
details = get_fault_details(fault)

print("FAULT:", fault)
print("RISK:", details["risk"])
print("DECISION:", details["decision"])
print("PRECAUTIONS:", details["precautions"])
print("REPAIR GUIDANCE:", details["repair_guidance"])
print("PROFESSIONAL REQUIRED:", details["professional_required"])


# In[9]:


# FIXORA Safety Validation Tests

test_cases = [
    "loose_cabinet_handle",
    "dripping_pipe_near_electricity",
    "sparking_switchboard",
    "unknown_fault"
]

for fault in test_cases:
    result = get_fault_details(fault)

    print("\nFault:", fault)
    print("Risk:", result["risk"])
    print("Decision:", result["decision"])

    if result["risk"] == "HIGH" or result["risk"] == "UNKNOWN":
        assert result["repair_guidance"] == [], \
            "Safety failure: repair guidance should be blocked!"
        print("Safety test: PASSED - DIY repair guidance blocked")
    else:
        print("Safety test: PASSED - Basic guidance permitted")


# In[10]:


def display_fixora_report(fault):
    result = get_fault_details(fault)

    print("=" * 45)
    print("          FIXORA SAFETY REPORT")
    print("=" * 45)
    print("Detected fault:", fault)
    print("Risk level:", result["risk"])
    print("Decision:", result["decision"])
    print("\nSafety precautions:")

    for precaution in result["precautions"]:
        print("-", precaution)

    if result["repair_guidance"]:
        print("\nApproved repair guidance:")
        for step in result["repair_guidance"]:
            print("-", step)
    else:
        print("\nRepair guidance: BLOCKED")
        print("Professional required:",
              result["professional_required"])

    print("=" * 45)


display_fixora_report("sparking_switchboard")


# In[11]:


# ==========================================
# FIXORA - SAFETY & REPAIR LOGIC ENGINE
# Final consolidated prototype
# ==========================================

REPAIR_KNOWLEDGE_BASE = {
    "loose_cabinet_handle": {
        "risk": "LOW",
        "decision": "APPROVED_GUIDANCE",
        "precautions": [
            "Keep fingers clear of pinch points.",
            "Use the correct screwdriver."
        ],
        "repair_guidance": [
            "Check whether the handle screw is loose.",
            "If appropriate, gently tighten it with the correct tool.",
            "Check that the handle is secure."
        ],
        "professional_required": False
    },

    "esp32_led_not_lighting": {
        "risk": "LOW",
        "decision": "APPROVED_GUIDANCE",
        "precautions": [
            "Use only the approved low-voltage prototype.",
            "Disconnect USB power before changing wiring.",
            "Never connect the prototype to household mains."
        ],
        "repair_guidance": [
            "Disconnect USB power.",
            "Check the LED orientation and resistor connections.",
            "Check the program and selected GPIO pin.",
            "Reconnect USB power only after checking the circuit."
        ],
        "professional_required": False
    },

    "disconnected_wire": {
        "risk": "LOW",
        "decision": "APPROVED_GUIDANCE",
        "precautions": [
            "Work strictly on low-voltage (3.3V / 5V) educational circuits.",
            "Turn off the circuit switch or disconnect USB power before touching wiring.",
            "Never perform repairs on household AC mains electricity."
        ],
        "repair_guidance": [
            "Disconnect power from the breadboard circuit.",
            "Identify the unseated jumper wire pinpointed by AI Vision.",
            "Firmly re-insert the jumper wire pin into the correct breadboard terminal row.",
            "Check all connections before turning the switch or power back on."
        ],
        "professional_required": False
    },

    "disconnected_jumper_wire": {
        "risk": "LOW",
        "decision": "APPROVED_GUIDANCE",
        "precautions": [
            "Work strictly on low-voltage (3.3V / 5V) educational circuits.",
            "Turn off the circuit switch or disconnect USB power before touching wiring.",
            "Never perform repairs on household AC mains electricity."
        ],
        "repair_guidance": [
            "Disconnect power from the breadboard circuit.",
            "Identify the unseated jumper wire pinpointed by AI Vision.",
            "Firmly re-insert the jumper wire pin into the correct breadboard terminal row.",
            "Check all connections before turning the switch or power back on."
        ],
        "professional_required": False
    },

    "loose_wire": {
        "risk": "LOW",
        "decision": "APPROVED_GUIDANCE",
        "precautions": [
            "Work strictly on low-voltage DC prototyping circuits.",
            "Turn off power before touching components."
        ],
        "repair_guidance": [
            "Disconnect power from the circuit.",
            "Gently press the loose jumper wire pin into its terminal row.",
            "Verify mechanical stability before testing."
        ],
        "professional_required": False
    },

    "dripping_pipe_near_electricity": {
        "risk": "HIGH",
        "decision": "STOP_AND_ESCALATE",
        "precautions": [
            "Do not touch wet electrical equipment.",
            "Keep people away from the affected area.",
            "Contact appropriate qualified professionals."
        ],
        "repair_guidance": [],
        "professional_required": True
    },

    "sparking_switchboard": {
        "risk": "HIGH",
        "decision": "STOP_AND_ESCALATE",
        "precautions": [
            "Keep away from the switchboard.",
            "Do not touch or attempt to repair it.",
            "Contact a qualified electrician."
        ],
        "repair_guidance": [],
        "professional_required": True
    }
}


def assess_fault(fault_id, hazard_flags=None):
    # Reject invalid inputs
    if not isinstance(fault_id, str) or not fault_id.strip():
        fault_id = ""

    fault_id = fault_id.strip().lower().replace(" ", "_")

    # Treat malformed hazard data as unsafe to assess
    if hazard_flags is not None and not isinstance(hazard_flags, dict):
        return {
            "fault": fault_id or "unknown_fault",
            "risk": "UNKNOWN",
            "decision": "STOP_AND_ASSESS",
            "precautions": [
                "Input could not be safely verified."
            ],
            "repair_guidance": [],
            "professional_required": True
        }

    hazard_flags = hazard_flags or {}

    # Explicit danger indicators always override normal guidance
    dangerous_signals = [
        "sparking",
        "smoke",
        "burning_smell",
        "exposed_mains",
        "water_near_electricity"
    ]

    if any(hazard_flags.get(signal) is True
           for signal in dangerous_signals):
        return {
            "fault": fault_id or "unknown_fault",
            "risk": "HIGH",
            "decision": "STOP_AND_ESCALATE",
            "precautions": [
                "Keep away from the hazard.",
                "Do not touch or attempt a repair.",
                "Contact an appropriate qualified professional."
            ],
            "repair_guidance": [],
            "professional_required": True
        }

    # Unknown faults must never receive repair instructions
    details = REPAIR_KNOWLEDGE_BASE.get(fault_id)

    if details is None:
        return {
            "fault": fault_id or "unknown_fault",
            "risk": "UNKNOWN",
            "decision": "STOP_AND_ASSESS",
            "precautions": [
                "Do not attempt an unverified repair.",
                "Obtain further assessment before proceeding."
            ],
            "repair_guidance": [],
            "professional_required": True
        }

    # Return a fresh report without modifying the knowledge base
    return {
        "fault": fault_id,
        "risk": details["risk"],
        "decision": details["decision"],
        "precautions": details["precautions"].copy(),
        "repair_guidance": details["repair_guidance"].copy(),
        "professional_required": details["professional_required"]
    }


def display_fixora_report(fault_id, hazard_flags=None):
    report = assess_fault(fault_id, hazard_flags)

    print("=" * 45)
    print("          FIXORA SAFETY REPORT")
    print("=" * 45)
    print("Fault:", report["fault"])
    print("Risk:", report["risk"])
    print("Decision:", report["decision"])

    print("\nPrecautions:")
    for item in report["precautions"]:
        print("-", item)

    print("\nRepair guidance:")
    if report["repair_guidance"]:
        for index, item in enumerate(
                report["repair_guidance"], start=1):
            print(f"{index}. {item}")
    else:
        print("BLOCKED - No DIY repair steps provided.")

    print("\nProfessional required:",
          report["professional_required"])
    print("=" * 45)


# First demonstration
display_fixora_report("sparking_switchboard")


# In[12]:


# FIXORA automated safety tests

# 1. A basic repair is recognized
assert assess_fault(
    "loose_cabinet_handle"
)["decision"] == "APPROVED_GUIDANCE"

# 2. A dangerous fault is escalated
report = assess_fault("sparking_switchboard")
assert report["decision"] == "STOP_AND_ESCALATE"
assert report["repair_guidance"] == []

# 3. Unknown faults cannot receive DIY instructions
report = assess_fault("unknown_fault")
assert report["risk"] == "UNKNOWN"
assert report["repair_guidance"] == []

# 4. A danger signal overrides a normally safe fault
report = assess_fault(
    "loose_cabinet_handle",
    {"sparking": True}
)
assert report["decision"] == "STOP_AND_ESCALATE"
assert report["repair_guidance"] == []

# 5. Empty input is handled safely
report = assess_fault("")
assert report["decision"] == "STOP_AND_ASSESS"
assert report["repair_guidance"] == []

# 6. Malformed hazard data is handled safely
report = assess_fault(
    "loose_cabinet_handle",
    ["invalid data"]
)
assert report["repair_guidance"] == []

print("All 6 FIXORA safety tests passed!")


# In[13]:


# Example of the output your teammate can consume

sample_report = assess_fault("sparking_switchboard")

print(sample_report)


# In[ ]:




