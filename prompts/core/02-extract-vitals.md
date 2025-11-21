# Extract Vital Signs from Turkish Clinical Notes

## Purpose
Extract and validate vital signs from Turkish clinical notes or structured JSON data.

## Input
Turkish clinical note text or previously parsed JSON

## Output
JSON object with vital signs only:

```json
{
  "vitals": {
    "heart_rate": {"value": <int>, "unit": "bpm"},
    "blood_pressure": {
      "systolic": <int>,
      "diastolic": <int>,
      "map": <int>,
      "unit": "mmHg"
    },
    "respiratory_rate": {"value": <int>, "unit": "/min"},
    "spo2": {"value": <int>, "unit": "%"},
    "temperature": {"value": <number>, "unit": "celsius"},
    "timestamp": "YYYY-MM-DD HH:MM",
    "critical_flags": [
      {"parameter": "<name>", "value": <number>, "threshold": "<description>"}
    ]
  }
}
```

## Critical Thresholds
- HR < 40 or > 180 bpm
- MAP < 65 mmHg
- RR < 8 or > 40 /min
- SpO2 < 90%
- Temp < 35°C or > 40°C

Extract and flag accordingly.
