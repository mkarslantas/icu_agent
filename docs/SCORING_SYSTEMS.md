# ICU Scoring Systems

Detailed explanation of severity scoring systems used in this monitoring system.

## SOFA Score (Sequential Organ Failure Assessment)

### Overview
- **Purpose**: Assess degree of organ dysfunction over time
- **Range**: 0-24 points (6 organ systems × 0-4 points each)
- **Frequency**: Calculate daily
- **Use**: Trend tracking, prognostication, sepsis definition

### Components

#### 1. Respiratory (P/F Ratio)

| P/F Ratio (mmHg) | Mechanical Ventilation | Score |
|------------------|------------------------|-------|
| ≥400             | No                     | 0     |
| <400             | No                     | 1     |
| <300             | No                     | 2     |
| <200             | **Yes**                | 3     |
| <100             | **Yes**                | 4     |

**Calculation**: PaO2 / FiO2
- PaO2 from ABG (mmHg)
- FiO2 as decimal (0.40 = 40%)

**Example**: PaO2 = 92 mmHg, FiO2 = 40% (0.40)
- P/F = 92 / 0.40 = 230 → Score 2 (if not ventilated) or 3 (if ventilated)

#### 2. Coagulation (Platelets)

| Platelet Count (K/µL) | Score |
|-----------------------|-------|
| ≥150                  | 0     |
| <150                  | 1     |
| <100                  | 2     |
| <50                   | 3     |
| <20                   | 4     |

#### 3. Hepatic (Bilirubin)

| Bilirubin (mg/dL) | Score |
|-------------------|-------|
| <1.2              | 0     |
| 1.2-1.9           | 1     |
| 2.0-5.9           | 2     |
| 6.0-11.9          | 3     |
| ≥12.0             | 4     |

#### 4. Cardiovascular

| MAP / Vasopressor                               | Score |
|-------------------------------------------------|-------|
| MAP ≥70 mmHg                                    | 0     |
| MAP <70 mmHg                                    | 1     |
| Dopamine ≤5 or dobutamine (any dose)            | 2     |
| Dopamine >5 OR epi/norepi ≤0.1 mcg/kg/min      | 3     |
| Dopamine >15 OR epi/norepi >0.1 mcg/kg/min     | 4     |

**Notes:**
- Doses in mcg/kg/min
- Use HIGHEST scoring vasopressor if multiple agents

#### 5. Neurological (GCS)

| GCS           | Score |
|---------------|-------|
| 15            | 0     |
| 13-14         | 1     |
| 10-12         | 2     |
| 6-9           | 3     |
| <6            | 4     |

#### 6. Renal

| Creatinine (mg/dL) OR Urine Output | Score |
|------------------------------------|-------|
| <1.2                               | 0     |
| 1.2-1.9                            | 1     |
| 2.0-3.4                            | 2     |
| 3.5-4.9 OR UO <500 mL/day          | 3     |
| ≥5.0 OR UO <200 mL/day             | 4     |

### SOFA Score Interpretation

| Total Score | Mortality Risk | Severity     |
|-------------|----------------|--------------|
| 0-6         | <10%           | Low          |
| 7-9         | 15-20%         | Moderate     |
| 10-12       | 40-50%         | High         |
| 13-14       | 50-60%         | Very High    |
| 15-24       | >80%           | Critical     |

### Delta SOFA

**Definition**: Change in SOFA score from baseline (admission or previous)

**Interpretation**:
- **Increase ≥2 points**: Worsening, increased mortality risk
  - Action: Escalate interventions, reassess treatment
- **Increase ≥3 points**: Significant deterioration
  - Action: Consider goals of care discussion
- **Decrease ≥2 points**: Improvement
  - Action: Consider de-escalation when appropriate
- **Change <2 points**: Stable trajectory

**Clinical Use**:
- Defines sepsis: Infection + SOFA increase ≥2 points
- More prognostic than single value
- Track daily to monitor response to therapy

### Example SOFA Calculation

**Patient**: 68M, septic shock, Day 5

**Data**:
- PaO2 92 mmHg, FiO2 40%, on ventilator → P/F = 230
- Platelets 95 K/µL
- Bilirubin 0.8 mg/dL
- MAP 80 mmHg on norepinephrine 0.15 mcg/kg/min
- GCS 15
- Creatinine 1.8 mg/dL

**Calculation**:
- Respiratory: P/F 230 + ventilated = **3 points**
- Coagulation: Plt 95 = **2 points**
- Hepatic: Bili 0.8 = **0 points**
- Cardiovascular: NE 0.15 (>0.1) = **4 points**
- Neurological: GCS 15 = **0 points**
- Renal: Cr 1.8 = **1 point**

**Total SOFA**: 3 + 2 + 0 + 4 + 0 + 1 = **10 points** → 40-50% mortality risk (High severity)

---

## APACHE-II Score

### Overview
- **Purpose**: Predict ICU mortality at admission
- **Range**: 0-71 points
- **Timing**: First 24 hours of ICU admission (WORST values)
- **Use**: Severity assessment, quality benchmarking, research
- **Note**: Do NOT recalculate during ICU stay

### Components

#### 1. Acute Physiology Score (0-60 points)

12 physiologic variables, each 0-4 points based on deviation from normal.

**Variables**:
1. Temperature (°C)
2. Mean Arterial Pressure (mmHg)
3. Heart Rate (bpm)
4. Respiratory Rate (/min)
5. Oxygenation (A-a gradient if FiO2≥50%, otherwise PaO2)
6. Arterial pH
7. Serum Sodium (mEq/L)
8. Serum Potassium (mEq/L)
9. Serum Creatinine (mg/dL) - **Double points if acute renal failure**
10. Hematocrit (%)
11. White Blood Count (K/µL)
12. Glasgow Coma Scale (15 minus actual GCS)

#### 2. Age Points (0-6 points)

| Age (years) | Points |
|-------------|--------|
| <44         | 0      |
| 45-54       | 2      |
| 55-64       | 3      |
| 65-74       | 5      |
| ≥75         | 6      |

#### 3. Chronic Health Points (0-5 points)

**If patient has severe organ insufficiency or immunocompromised:**
- Nonoperative or emergency postoperative: **5 points**
- Elective postoperative: **2 points**
- No chronic health problems: **0 points**

**Qualifying conditions**:
- Severe organ insufficiency: Cirrhosis (biopsy-proven), NYHA Class IV CHF, severe COPD, chronic dialysis
- Immunocompromised: High-dose steroids, chemotherapy, radiation, immunosuppression, AIDS

### APACHE-II Interpretation

| Score  | Predicted Mortality |
|--------|---------------------|
| 0-4    | 4%                  |
| 5-9    | 8%                  |
| 10-14  | 15%                 |
| 15-19  | 25%                 |
| 20-24  | 40%                 |
| 25-29  | 55%                 |
| 30-34  | 75%                 |
| ≥35    | >85%                |

### Example APACHE-II Calculation

**Patient**: Same 68M patient, admission data

**Acute Physiology** (using worst first 24h values):
- Temperature 38.8°C → 1 point
- MAP 68 mmHg → 2 points
- HR 115 bpm → 2 points
- RR 24/min → 1 point
- PaO2 88 mmHg (FiO2 <50%) → 1 point
- pH 7.28 → 3 points
- Na 138 mEq/L → 0 points
- K 4.2 mEq/L → 0 points
- Cr 2.4 mg/dL (acute!) → 3 × 2 = 6 points
- Hct 31% → 2 points
- WBC 18.5 K/µL → 2 points
- GCS 13 → 15-13 = 2 points

**Subtotal**: 1+2+2+1+1+3+0+0+6+2+2+2 = **22 points**

**Age**: 68 years → **5 points**

**Chronic Health**: DM, HTN, CKD Stage 3, emergency admission → **5 points**

**Total APACHE-II**: 22 + 5 + 5 = **32 points** → ~75% predicted mortality

---

## Quick SOFA (qSOFA)

### Overview
- **Purpose**: Rapid bedside screening for sepsis risk
- **Range**: 0-3 points
- **Use**: Triage, early identification (NOT for diagnosis)

### Criteria

| Criterion                              | Points |
|----------------------------------------|--------|
| Altered mental status (GCS <15)        | 1      |
| Systolic blood pressure ≤100 mmHg      | 1      |
| Respiratory rate ≥22/min               | 1      |

### Interpretation
- **qSOFA ≥2**: Higher risk for poor outcomes
  - Action: Consider sepsis, perform full SOFA assessment
  - Initiate sepsis workup and treatment

- **qSOFA <2**: Lower risk (but does NOT rule out sepsis)

**Note**: qSOFA is for SCREENING only. Full SOFA score and clinical judgment required for diagnosis and management.

---

## Clinical Use Guidelines

### When to Calculate

**SOFA**:
- ✅ Daily in all ICU patients
- ✅ At any clinical change
- ✅ Admission baseline

**APACHE-II**:
- ✅ Once at ICU admission (first 24h)
- ❌ Not daily (use SOFA for trends)

**qSOFA**:
- ✅ Emergency department
- ✅ Ward patients with suspected infection
- ❌ Not useful in ICU (use full SOFA)

### Limitations

**SOFA**:
- Not validated for discharge decisions
- Single value less useful than trend
- Influenced by aggressive treatment

**APACHE-II**:
- Population-level accuracy, not individual
- May over/underestimate in specific populations
- Doesn't account for ICU interventions

**Both**:
- Decision support tools, NOT treatment mandates
- Clinical judgment supersedes scores
- Local validation recommended

### Tips for Accurate Scoring

1. **Use worst values** (for APACHE-II first 24h)
2. **Complete data**: Missing values affect accuracy
3. **Check units**: mg/dL vs mmol/L, °C vs °F
4. **Consistent timing**: Same time each day for SOFA
5. **Document baseline**: Especially for delta SOFA
6. **Clinical context**: Scores inform, don't dictate

---

## Automated Calculation

This system calculates scores automatically using:
- `prompts/analysis/13-calculate-scores.md`
- `config/scoring-criteria.yaml` (full criteria)

Provides:
- Component-by-component scoring
- Rationale for each score
- Mortality risk interpretation
- Delta SOFA with trending

See [USAGE.md](USAGE.md) for calculation examples.
