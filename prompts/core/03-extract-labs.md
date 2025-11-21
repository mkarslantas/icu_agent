# Extract Laboratory Values from Turkish Clinical Notes

## Purpose
Extract and validate laboratory values from Turkish clinical notes.

## Input
Turkish clinical note text or previously parsed JSON

## Output
JSON with all laboratory values:

```json
{
  "labs": {
    "hematology": {
      "wbc": {"value": <number>, "unit": "K/µL"},
      "hemoglobin": {"value": <number>, "unit": "g/dL"},
      "platelet": {"value": <number>, "unit": "K/µL"}
    },
    "chemistry": {
      "sodium": {"value": <number>, "unit": "mEq/L"},
      "potassium": {"value": <number>, "unit": "mEq/L"},
      "chloride": {"value": <number>, "unit": "mEq/L"},
      "bicarbonate": {"value": <number>, "unit": "mEq/L"},
      "bun": {"value": <number>, "unit": "mg/dL"},
      "creatinine": {"value": <number>, "unit": "mg/dL"},
      "glucose": {"value": <number>, "unit": "mg/dL"}
    },
    "inflammatory_markers": {
      "crp": {"value": <number>, "unit": "mg/L"},
      "procalcitonin": {"value": <number>, "unit": "ng/mL"}
    },
    "blood_gas": {
      "ph": <number>,
      "pco2": {"value": <number>, "unit": "mmHg"},
      "po2": {"value": <number>, "unit": "mmHg"},
      "hco3": {"value": <number>, "unit": "mEq/L"},
      "lactate": {"value": <number>, "unit": "mmol/L"}
    },
    "coagulation": {
      "pt": {"value": <number>, "unit": "seconds"},
      "inr": <number>,
      "aptt": {"value": <number>, "unit": "seconds"}
    },
    "timestamp": "YYYY-MM-DD HH:MM",
    "critical_values": []
  }
}
```

## Critical Lab Values
- K+ < 2.5 or > 6.5 mEq/L
- Glucose < 40 or > 400 mg/dL
- Lactate > 4 mmol/L
- Hgb < 7 g/dL
- Platelet < 20 K/µL
- pH < 7.2 or > 7.6

Extract all values, convert Turkish numbers, flag critical values.
