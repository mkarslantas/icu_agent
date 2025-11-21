# Extract Treatment Plan from Turkish Clinical Notes

## Purpose
Extract treatment plan and clinical decision-making from Turkish notes.

## Input
Turkish clinical note text

## Output
JSON with structured treatment plan:

```json
{
  "treatment_plan": {
    "cardiovascular": {
      "vasopressor_plan": "<plan>",
      "fluid_management": "<plan>",
      "targets": {"map": <number>}
    },
    "respiratory": {
      "ventilator_changes": "<plan>",
      "weaning_plan": "<plan>",
      "oxygenation_targets": {"spo2": <number>, "fio2": <number>}
    },
    "renal": {
      "fluid_balance_goal": "<plan>",
      "diuretic_plan": "<plan>"
    },
    "infectious_disease": {
      "antibiotic_plan": "<plan>",
      "duration": "<days>",
      "de_escalation_strategy": "<plan>",
      "culture_plan": "<plan>"
    },
    "nutrition": {
      "route": "enteral|parenteral|oral|NPO",
      "plan": "<details>"
    },
    "actions": [
      {
        "action": "<specific action>",
        "timing": "immediately|today|tomorrow|this_week",
        "rationale": "<clinical reasoning>"
      }
    ],
    "goals": [
      "<clinical goal 1>",
      "<clinical goal 2>"
    ]
  }
}
```

## Extract
- Specific interventions planned
- Timing of actions
- Clinical reasoning/rationale
- Weaning plans
- De-escalation strategies
- Follow-up plans

Turkish keywords:
- "Plan:" or "Planlama:"
- "devam" → continue
- "azaltmaya devam" → continue to decrease
- "başlanabilir" → can be started
- "re-evaluate" → reassess
- "takip" → follow-up
