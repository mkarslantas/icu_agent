# Calculate ICU Severity Scores (SOFA, APACHE-II)

## Purpose
Calculate SOFA and APACHE-II scores from structured patient data.

## Input
Structured JSON with patient clinical data (from parser or vitals/labs extraction)

## Reference
Consult `config/scoring-criteria.yaml` for detailed scoring rules.

## Output
JSON with calculated scores:

```json
{
  "scores": {
    "sofa": {
      "components": {
        "respiratory": {
          "pf_ratio": <number>,
          "score": <0-4>,
          "rationale": "<explanation>"
        },
        "coagulation": {
          "platelet": <number>,
          "score": <0-4>,
          "rationale": "<explanation>"
        },
        "hepatic": {
          "bilirubin": <number>,
          "score": <0-4>,
          "rationale": "<explanation>"
        },
        "cardiovascular": {
          "map": <number>,
          "vasopressor": "<drug and dose or none>",
          "score": <0-4>,
          "rationale": "<explanation>"
        },
        "neurological": {
          "gcs": <number>,
          "score": <0-4>,
          "rationale": "<explanation>"
        },
        "renal": {
          "creatinine": <number>,
          "urine_output": <number>,
          "score": <0-4>,
          "rationale": "<explanation>"
        }
      },
      "total_score": <0-24>,
      "mortality_risk": "<percentage range>",
      "severity": "low|moderate|high|very high|critical",
      "date": "YYYY-MM-DD"
    },

    "delta_sofa": {
      "previous_total": <number or null>,
      "current_total": <number>,
      "change": <number or null>,
      "interpretation": "improving|worsening|stable|first_calculation",
      "clinical_significance": "<explanation>"
    },

    "apache_ii": {
      "acute_physiology_score": <0-60>,
      "age_points": <0-6>,
      "chronic_health_points": <0-5>,
      "total_score": <0-71>,
      "predicted_mortality": "<percentage>",
      "note": "Calculated from first 24h data"
    },

    "quick_sofa": {
      "altered_mental_status": <boolean>,
      "sbp_100_or_less": <boolean>,
      "rr_22_or_more": <boolean>,
      "score": <0-3>,
      "interpretation": "<low risk | consider sepsis>"
    }
  },
  "timestamp": "YYYY-MM-DD HH:MM"
}
```

## SOFA Calculation Rules

### Respiratory (P/F Ratio)
- Calculate: PaO2 / FiO2
- ≥400 → 0
- <400 → 1
- <300 → 2
- <200 + MV → 3
- <100 + MV → 4

### Coagulation (Platelets)
- ≥150 → 0
- <150 → 1
- <100 → 2
- <50 → 3
- <20 → 4

### Hepatic (Bilirubin mg/dL)
- <1.2 → 0
- 1.2-1.9 → 1
- 2.0-5.9 → 2
- 6.0-11.9 → 3
- ≥12.0 → 4

### Cardiovascular
- MAP ≥70, no vasopressors → 0
- MAP <70, no vasopressors → 1
- Dopamine ≤5 or dobutamine (any) → 2
- Dopamine >5 OR epi/norepi ≤0.1 → 3
- Dopamine >15 OR epi/norepi >0.1 → 4

### Neurological (GCS)
- GCS 15 → 0
- GCS 13-14 → 1
- GCS 10-12 → 2
- GCS 6-9 → 3
- GCS <6 → 4

### Renal (Creatinine mg/dL or UO mL/day)
- Cr <1.2 → 0
- Cr 1.2-1.9 → 1
- Cr 2.0-3.4 → 2
- Cr 3.5-4.9 OR UO <500 → 3
- Cr ≥5.0 OR UO <200 → 4

## Mortality Risk Interpretation (SOFA)
- 0-6: <10% mortality (low)
- 7-9: 15-20% mortality (moderate)
- 10-12: 40-50% mortality (high)
- 13-14: 50-60% mortality (very high)
- 15-24: >80% mortality (critical)

## Delta SOFA Interpretation
- Increase ≥2 points: Increased mortality risk, escalate care
- Increase ≥3 points: Significant deterioration
- Decrease ≥2 points: Improvement, consider de-escalation
- Change <2 points: Stable trajectory

## Clinical Context
- SOFA should be calculated daily
- Trend is more important than single value
- Use in conjunction with clinical assessment
- Delta SOFA from baseline is prognostic
- SOFA increase ≥2 defines sepsis-induced organ dysfunction

## Special Cases
- If data missing for a component, note it and calculate based on available data
- If on mechanical ventilation but PaO2 unknown, use SpO2/FiO2 ratio × 100 as approximation
- For cardiovascular, use highest vasopressor dose if on multiple agents

Calculate all scores with detailed rationale for each component.
