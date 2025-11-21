# Critical Values Alert System

## Purpose
Identify and prioritize critical laboratory and vital sign values requiring immediate attention.

## Input
Structured patient data (vitals + labs)

## Output
JSON array of critical alerts:

```json
{
  "critical_alerts": [
    {
      "parameter": "<parameter name>",
      "value": <number>,
      "unit": "<unit>",
      "threshold": "<threshold description>",
      "severity": "urgent|critical|life-threatening",
      "action_required": "<specific action>",
      "timing": "immediate|within_1_hour|within_4_hours"
    }
  ],
  "alert_count": {
    "life_threatening": <int>,
    "critical": <int>,
    "urgent": <int>
  }
}
```

## Critical Thresholds (Life-Threatening)
- MAP < 65 mmHg
- GCS < 8
- pH < 7.2 or > 7.6
- K+ < 2.5 or > 6.5 mEq/L

## Critical Thresholds (Critical)
- Lactate > 4 mmol/L
- SpO2 < 90%
- Glucose < 40 or > 400 mg/dL
- Hgb < 7 g/dL
- Platelet < 20 K/µL

## Critical Thresholds (Urgent)
- Urine output < 0.5 mL/kg/hr
- Temperature < 35°C or > 40°C
- HR < 40 or > 180 bpm

Prioritize by severity, provide specific actions.
