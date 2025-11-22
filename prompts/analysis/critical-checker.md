# Critical Value Checker

## Purpose
Identify and categorize critical clinical values that require immediate attention.

## Input
- Vital signs data
- Laboratory values
- Reference ranges and thresholds

## Critical Thresholds

### Life-Threatening (Immediate Intervention Required)
- MAP < 65 mmHg
- GCS < 8
- pH < 7.2 or > 7.6
- K+ < 2.5 or > 6.5 mEq/L

### Critical (Urgent Attention)
- Lactate > 4 mmol/L
- SpO2 < 90%
- Glucose < 40 or > 400 mg/dL
- Hemoglobin < 7 g/dL
- Platelet < 20 K/µL
- HR < 40 or > 180 bpm

### Urgent (Monitor Closely)
- Urine output < 0.5 mL/kg/hr
- Temperature < 35°C or > 40°C
- Respiratory rate < 8 or > 40 /min

## Output Format

Return JSON only:

```json
{
  "critical_analysis": {
    "life_threatening": [
      {
        "parameter": "MAP",
        "value": 58,
        "unit": "mmHg",
        "threshold": "< 65 mmHg",
        "severity": "life-threatening",
        "action": "Increase vasopressor immediately"
      }
    ],
    "critical": [
      {
        "parameter": "Lactate",
        "value": 4.5,
        "unit": "mmol/L",
        "threshold": "> 4 mmol/L",
        "severity": "critical",
        "action": "Assess tissue perfusion, consider fluid resuscitation"
      }
    ],
    "urgent": [],
    "summary": {
      "total_critical_values": 2,
      "highest_severity": "life-threatening",
      "requires_immediate_action": true
    }
  }
}
```

## Instructions
1. Compare each parameter against thresholds
2. Categorize by severity
3. Provide specific actionable recommendations
4. Prioritize by severity (life-threatening first)
5. Return ONLY JSON, no explanations
