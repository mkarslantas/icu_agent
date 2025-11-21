# Clinical Guidelines Reference

Quick reference for evidence-based ICU protocols implemented in this system.

## Sepsis & Septic Shock

Based on **Surviving Sepsis Campaign 2021**

### Hour-1 Bundle
1. Measure lactate (remeasure if >2 mmol/L)
2. Obtain blood cultures before antibiotics
3. Administer broad-spectrum antibiotics within 1 hour
4. Give 30 mL/kg crystalloid for hypotension or lactate ≥4
5. Apply vasopressors if hypotensive (target MAP ≥65)

### Key Recommendations
- **Norepinephrine**: First-line vasopressor
- **Hydrocortisone**: 200 mg/day if inadequate response to fluids/vasopressors
- **Source control**: Within 12 hours if possible
- **Antibiotic duration**: 7-10 days typically
- **De-escalation**: Based on cultures and clinical improvement

See: `knowledge-base/protocols/sepsis-management.md`

## Mechanical Ventilation

### ARDSnet Protocol (Low Tidal Volume)
- **Tidal volume**: 6 mL/kg predicted body weight
- **Plateau pressure**: ≤30 cmH2O
- **PEEP/FiO2 table**: Evidence-based combinations
- **pH goal**: 7.30-7.45 (permissive hypercapnia acceptable)

### Weaning Protocol
**Daily Screening Criteria:**
- P/F ratio ≥150-200
- PEEP ≤5-8 cmH2O, FiO2 ≤40-50%
- Hemodynamically stable (minimal vasopressors)
- GCS ≥13, able to follow commands

**Spontaneous Breathing Trial:**
- Method: PS 5-8 + PEEP 5 OR T-piece
- Duration: 30-120 minutes
- Monitor: RR, SpO2, HR, BP, work of breathing

See: `config/weaning-protocols.yaml`

## Antibiotic Stewardship

### De-Escalation Principles
1. **Culture-directed**: Narrow spectrum based on susceptibility
2. **Shortest effective duration**: Typically 5-7 days
3. **PCT-guided**: Consider stopping if PCT <0.5 or ↓80%
4. **Source control**: Essential for success

### Common ICU Infections

**HAP/VAP:**
- Empiric: Anti-pseudomonal β-lactam + anti-MRSA
- Duration: 7 days standard
- De-escalate at 48-72h based on cultures

**Urosepsis:**
- Empiric: Ceftriaxone or pip-tazo
- Duration: 7-14 days
- Source control: Remove/change catheter

**Intra-abdominal:**
- Source control MANDATORY
- Duration: 4-7 days post-source control

See: `config/antibiotic-guidelines.yaml`

## Hemodynamic Management

### Vasopressor Selection

**First-line: Norepinephrine**
- Dose: 0.05-0.5 mcg/kg/min
- Target: MAP ≥65 mmHg

**Second-line: Vasopressin**
- Dose: 0.03-0.04 units/min (fixed)
- Add if high-dose norepinephrine
- Allows NE dose reduction

**Inotrope: Dobutamine**
- Indication: Myocardial dysfunction with low CO
- Dose: 2.5-20 mcg/kg/min
- Use WITH norepinephrine (not alone)

See: `knowledge-base/drug-database/vasopressors.yaml`

## Renal Management

### AKI Staging (KDIGO)

**Stage 1:**
- Cr 1.5-1.9× baseline OR
- UO <0.5 mL/kg/hr for 6-12h

**Stage 2:**
- Cr 2.0-2.9× baseline OR
- UO <0.5 mL/kg/hr for ≥12h

**Stage 3:**
- Cr ≥3× baseline OR Cr ≥4.0 OR
- UO <0.3 mL/kg/hr for ≥24h OR anuria ≥12h
- Initiation of RRT

### Fluid Management
- **Resuscitation**: 30 mL/kg within 3h for septic shock
- **De-resuscitation**: Negative balance after stabilization
- **Diuretics**: After adequate resuscitation if fluid overload

## Glucose Control

### Target
- **ICU target**: 140-180 mg/dL
- Avoid hypoglycemia (<70 mg/dL)

### Protocol
- Insulin infusion for persistent hyperglycemia
- Monitor q1-2h during insulin infusion
- Transition to subcutaneous when stable and eating

## DVT Prophylaxis

### Pharmacologic
- **Enoxaparin**: 40 mg SC daily
- **Heparin**: 5000 units SC q8-12h
- Hold if active bleeding or severe thrombocytopenia (<50K)

### Mechanical
- Sequential compression devices
- Use if pharmacologic contraindicated

## Stress Ulcer Prophylaxis

### Indications
- Mechanical ventilation >48h
- Coagulopathy
- High-dose corticosteroids
- Severe sepsis

### Agents
- **PPI**: Pantoprazole 40 mg IV/PO daily
- **H2 blocker**: Famotidine 20 mg IV/PO q12h

## Sedation & Analgesia

### Approach
- **Pain first**: Treat pain before sedation
- **Light sedation**: Target RASS -2 to 0
- **Daily awakening trials**: Unless contraindicated
- **Delirium screening**: CAM-ICU daily

### Agents
- **Analgesia**: Fentanyl, morphine
- **Sedation**: Propofol (short-term), dexmedetomidine
- **Avoid**: Benzodiazepines (increase delirium risk)

## Nutrition

### Timing
- **Enteral**: Start within 24-48h if tolerated
- **Parenteral**: If enteral not feasible after 7 days

### Goals
- **Calories**: 25-30 kcal/kg/day
- **Protein**: 1.5-2 g/kg/day

### Route
- Prefer enteral over parenteral
- Post-pyloric if gastric intolerance

## Code Status & Goals of Care

### Documentation
- Discuss with patient/family early
- Document code status clearly
- Revisit if clinical change

### Prognostication
- Use SOFA/APACHE as adjuncts
- Avoid single prognostic tool
- Consider trajectory, not just single point

## References

### Guidelines
- Surviving Sepsis Campaign 2021
- ARDSnet Protocols
- IDSA HAP/VAP Guidelines 2016
- KDIGO AKI Guidelines 2012
- SCCM Pain, Agitation, Delirium Guidelines 2018

### Evidence Base
All recommendations based on current evidence and expert consensus. Local protocols may differ - always follow institutional guidelines when they conflict.

## Clinical Pearls

1. **Early antibiotics** - Most critical in sepsis (<1 hour)
2. **Source control** - No amount of antibiotics works without it
3. **MAP target** - ≥65 mmHg, but individualize (may need higher in chronic HTN)
4. **Sedation breaks** - Reduces delirium and vent days
5. **Weaning daily** - Don't delay if criteria met
6. **De-escalation** - Narrow antibiotics at 48-72h
7. **Trends matter** - Single values less important than trajectory

---

**Disclaimer**: These are general guidelines. Clinical decisions must be individualized based on patient-specific factors, institutional protocols, and physician judgment. This is decision support, not prescriptive treatment.
