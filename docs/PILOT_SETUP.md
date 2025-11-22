# Real Hospital Pilot Setup Guide

This guide provides step-by-step instructions for deploying the ICU Agent Multi-Agent System in a real hospital environment for pilot testing.

---

## 📋 Pre-Deployment Checklist

### Environment Requirements

- [ ] Python 3.10+ installed
- [ ] 4GB+ RAM available
- [ ] 2GB+ disk space
- [ ] Internet connection for Claude API
- [ ] Terminal access
- [ ] Text editor (vim, nano, or VS Code)

### Data Requirements

- [ ] 5+ patients identified for pilot
- [ ] Minimum 1 week of historical clinical notes (Turkish)
- [ ] Notes in UTF-8 text format
- [ ] Patient consent obtained (if required)
- [ ] Data anonymization completed (if required)
- [ ] IRB/Ethics approval (if required)

### Personnel Requirements

- [ ] ICU physician champion identified
- [ ] Technical support person assigned
- [ ] Training session scheduled
- [ ] Feedback collection mechanism established

---

## 🚀 Phase 1: Installation & Setup (Day 1)

### Step 1: Install System

```bash
# Clone repository (or copy to server)
cd /opt
git clone <repository-url> icu-agent
cd icu-agent

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install package
pip install -e .

# Verify installation
icu-agent --version
python -c "import agents; print('✓ Import successful')"
```

### Step 2: Configure API Key

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env

# Add your Anthropic API key:
# ANTHROPIC_API_KEY=your_api_key_here
```

**Security Note:** Keep `.env` file secure. Never commit to version control.

### Step 3: Test Basic Functionality

```bash
# Test with example patient
icu-agent process-patient -p HT001 -d 2025-11-20

# Verify report generated
ls -la state/HT001/2025-11-20/

# View report
icu-agent report -p HT001 -d 2025-11-20
```

**Expected:** All phases should complete successfully. Report should be in Turkish.

---

## 📁 Phase 2: Data Preparation (Days 1-2)

### Step 1: Create Patient Directories

```bash
# Create directory structure for pilot patients
mkdir -p patients/active/{PILOT001,PILOT002,PILOT003,PILOT004,PILOT005}
mkdir -p patients/active/PILOT001/{notes,demographics}
# Repeat for each patient...
```

### Step 2: Prepare Clinical Notes

**File Naming Convention:**
- `YYYY-MM-DD.txt` or
- `YYYY-MM-DD-dayX.txt`

**Example:**
```bash
patients/active/PILOT001/notes/
├── 2025-11-14.txt
├── 2025-11-15.txt
├── 2025-11-16.txt
├── 2025-11-17.txt
└── 2025-11-18.txt
```

**Note Format Requirements:**
- UTF-8 encoding (critical for Turkish characters)
- Plain text format
- Turkish clinical notes (voice transcription format supported)
- One note per day
- Minimum 200 characters per note

**Verification:**
```bash
# Check encoding
file -i patients/active/PILOT001/notes/2025-11-18.txt
# Should show: charset=utf-8

# Check for Turkish characters
grep -i "hasta\|üç\|değer" patients/active/PILOT001/notes/*.txt
```

### Step 3: Create Demographics (Optional)

Create `demographics.yaml` for each patient:

```yaml
# patients/active/PILOT001/demographics/demographics.yaml
patient_id: PILOT001
age: 65
gender: M
admission_date: 2025-11-10
diagnosis: Septic shock
weight_kg: 75
height_cm: 175
```

---

## 🧪 Phase 3: Initial Testing (Day 2-3)

### Step 1: Process First Patient Manually

```bash
# Process single patient with verbose output
icu-agent process-patient -p PILOT001 -d 2025-11-18 -r -v

# Check for errors in logs
tail -f logs/icu-agent.log
```

### Step 2: Validate Output Quality

**Checklist for Manual Review:**

- [ ] **Parsing Accuracy**
  - All vital signs extracted correctly
  - Lab values match original note
  - Turkish numbers converted accurately
  - Trends identified correctly

- [ ] **SOFA Score**
  - Score is reasonable (0-24 range)
  - Component breakdown makes sense
  - Delta SOFA calculated if history exists

- [ ] **Critical Values**
  - True critical values identified
  - No false positives
  - Severity categorization appropriate

- [ ] **Report Quality**
  - All sections present
  - Turkish language correct
  - Recommendations specific (not generic)
  - Medical terminology appropriate
  - Formatting readable

### Step 3: Physician Review Session

**First Review Meeting (30-60 minutes):**

1. **Show System Output**
   - Demonstrate report generation
   - Walk through all sections
   - Explain SOFA score breakdown

2. **Collect Feedback**
   - Accuracy of data extraction
   - Clinical utility of recommendations
   - Missing information
   - Formatting preferences

3. **Identify Issues**
   - Parsing errors to fix
   - Missing parameters
   - Incorrect interpretations

4. **Document Feedback**
```bash
# Create feedback file
cat > feedback/day1_review.md << 'EOF'
# Physician Review - Day 1

Date: 2025-11-18
Reviewer: Dr. [Name]
Patients Reviewed: PILOT001

## Accuracy
- Vital signs: ✓ Correct
- Lab values: ⚠ Lactate trend missed
- SOFA score: ✓ Accurate

## Clinical Utility
- Recommendations: Good but too conservative
- Missing: Weaning criteria mention

## Issues Found
1. Lactate trend not detected in Turkish text
2. Vasopressor dose conversion incorrect

EOF
```

---

## 📅 Phase 4: Daily Workflow (Days 3-7)

### Step 1: Morning Round Processing

Create a daily script:

```bash
#!/bin/bash
# scripts/daily_round.sh

# Morning round processing
echo "Starting morning round..."
date

# Process all patients with today's notes
icu-agent process-batch --all --priority

# Generate summary
echo "Morning round complete"
echo "Check: state/batch_summaries/batch_summary_$(date +%Y-%m-%d).md"
```

Make executable:
```bash
chmod +x scripts/daily_round.sh
```

Run daily:
```bash
./scripts/daily_round.sh
```

### Step 2: Review Workflow

**Daily Review Process (15-20 minutes):**

1. **Run Morning Round**
   ```bash
   ./scripts/daily_round.sh
   ```

2. **Review Critical Alerts**
   ```bash
   # Check for critical alerts
   icu-monitor
   # Press Ctrl+C to exit
   ```

3. **Spot-Check Random Patient**
   ```bash
   # Pick random patient
   icu-agent report -p PILOT00X
   ```

4. **Log Any Issues**
   - Keep issue log in `feedback/daily_issues.md`
   - Note parsing errors
   - Note incorrect recommendations
   - Note missing data

### Step 3: Weekly Metrics Collection

```bash
# View system stats
icu-agent stats

# Expected metrics to track:
# - Total patients processed
# - Success rate (target: >90%)
# - Average processing time (target: <120s)
# - Critical alerts count
```

---

## 📊 Phase 5: Data Collection (Throughout Pilot)

### Metrics to Track

Create a tracking spreadsheet with:

| Date | Patients | Success Rate | Avg Time | Parse Accuracy | Physician Acceptance | Issues |
|------|----------|--------------|----------|----------------|---------------------|--------|
| Day 1 | 5 | 100% | 95s | 90% | 80% | 2 |
| Day 2 | 5 | 100% | 87s | 95% | 85% | 1 |
| ... | | | | | | |

### Acceptance Rate Calculation

After each review, ask physician:
- Would you use this report in clinical decision-making? (Yes/No)
- Confidence level: 1-5 (5 = very confident)

**Target:** >80% "Yes" responses with average confidence >3.5

### Issue Tracking

Categorize issues:
- **Critical:** Incorrect clinical data (stop pilot)
- **High:** Missing important data
- **Medium:** Formatting/language issues
- **Low:** Minor improvements

---

## ✅ Phase 6: Success Criteria Evaluation (Day 20)

### Quantitative Criteria

- [ ] **20 consecutive days** of use completed
- [ ] **Parse accuracy** >90% (manual spot-checks)
- [ ] **Physician acceptance** >80%
- [ ] **Review time** <5 minutes per patient
- [ ] **System uptime** >95%
- [ ] **SOFA calculation** 100% accurate
- [ ] **Zero patient safety incidents**

### Qualitative Criteria

- [ ] Physicians find recommendations useful
- [ ] Reports integrate into workflow naturally
- [ ] Time savings demonstrated
- [ ] Clinical decision support valued

### Go/No-Go Decision

**Proceed to Expanded Pilot if:**
- All quantitative criteria met
- No critical safety issues
- Physician satisfaction high
- Clear clinical benefit demonstrated

**Iterate/Improve if:**
- Some criteria missed but fixable
- Physician feedback positive but needs refinement

**Stop if:**
- Multiple critical criteria missed
- Safety concerns raised
- Low physician acceptance (<60%)
- No clear clinical benefit

---

## 🔧 Troubleshooting Guide

### Common Issues

#### Issue: Parse accuracy low

**Symptoms:** Data extracted incorrectly from notes

**Solutions:**
1. Check Turkish encoding (must be UTF-8)
2. Review prompt in `prompts/core/01-parse-note.md`
3. Add specific examples to prompt
4. Check for unusual number formats

#### Issue: Slow processing (>120s)

**Symptoms:** Workflow takes too long

**Solutions:**
1. Check API latency: `time curl https://api.anthropic.com/v1/messages`
2. Reduce max_tokens in config if needed
3. Use parallel processing for batches
4. Check system resources (CPU, memory)

#### Issue: Report in wrong language

**Symptoms:** Report not in Turkish or mixed languages

**Solutions:**
1. Check prompt: `prompts/reports/30-daily-report.md`
2. Verify Turkish examples present
3. Add more Turkish medical terminology
4. Check encoding (UTF-8 required)

#### Issue: SOFA score seems wrong

**Symptoms:** SOFA calculation doesn't match manual calculation

**Solutions:**
1. Review scoring criteria: `config/scoring-criteria.yaml`
2. Check each component in state files
3. Verify lab values extracted correctly
4. Compare with manual calculation step-by-step

---

## 📝 Documentation Requirements

### Files to Maintain

1. **Daily Log** (`logs/pilot_daily.md`)
   - Patients processed
   - Issues encountered
   - Time spent
   - Physician feedback

2. **Issue Tracker** (`feedback/issues.md`)
   - Issue description
   - Severity
   - Date found
   - Status (open/resolved)
   - Resolution

3. **Acceptance Log** (`feedback/acceptance.md`)
   - Patient ID
   - Date
   - Accept/Reject
   - Confidence (1-5)
   - Comments

### Weekly Report Template

```markdown
# Week X Pilot Report

**Period:** [Start Date] - [End Date]

## Summary
- Patients processed: X
- Total notes: X
- Success rate: X%
- Average processing time: Xs

## Achievements
- [Achievement 1]
- [Achievement 2]

## Challenges
- [Challenge 1 and how addressed]
- [Challenge 2 and plan]

## Physician Feedback
- Acceptance rate: X%
- Key comments: [Summary]

## Metrics
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Parse accuracy | >90% | X% | ✓/✗ |
| Acceptance rate | >80% | X% | ✓/✗ |
| Review time | <5 min | X min | ✓/✗ |

## Next Week Plan
- [Plan items]
```

---

## 🎓 Training Materials

### Physician Training (1 hour session)

**Agenda:**
1. System overview (15 min)
2. Report walkthrough (20 min)
3. Hands-on demo (15 min)
4. Q&A (10 min)

**Key Points to Cover:**
- System capabilities and limitations
- How to interpret reports
- SOFA score meaning
- Critical alert system
- How to provide feedback

### Technical Training (30 min)

**For technical support person:**
1. How to run daily processing
2. How to check logs
3. Basic troubleshooting
4. How to restart if needed
5. Who to contact for issues

---

## 🔒 Data Privacy & Security

### Patient Data Protection

- [ ] All patient data anonymized/de-identified
- [ ] No PHI in logs
- [ ] `.env` file secured (API keys)
- [ ] Access controls configured
- [ ] Audit trail enabled

### API Key Security

```bash
# Verify .env is not in git
git check-ignore .env
# Should show: .env

# Set restrictive permissions
chmod 600 .env

# Verify
ls -l .env
# Should show: -rw------- (only owner can read/write)
```

---

## 📞 Support & Escalation

### Daily Support

**Minor issues:**
- Check logs: `tail -f logs/icu-agent.log`
- Restart system if needed
- Document in issue tracker

**Major issues:**
- Stop processing immediately
- Notify project lead
- Document incident
- Wait for resolution

### Contact Information

```markdown
Project Lead: [Name, Email, Phone]
Technical Support: [Name, Email, Phone]
Clinical Lead: [Name, Email, Phone]
Emergency: [Protocol]
```

---

## 🎯 Success Stories Template

Document successful cases:

```markdown
# Success Story: PILOT001

**Date:** 2025-11-20

## Scenario
Patient showing subtle deterioration not immediately obvious in routine check.

## System Contribution
- Detected lactate trending upward (2.1 → 2.8 → 3.2)
- Flagged increasing vasopressor requirement
- Calculated delta SOFA: +2 points

## Clinical Impact
- Prompted earlier sepsis protocol escalation
- Additional antibiotics added 4 hours earlier than planned
- Patient stabilized

## Physician Feedback
"The trend analysis helped me see the deterioration pattern I might have missed during a busy shift."

## Outcome
✓ Clinical benefit demonstrated
✓ Physician satisfaction high
✓ System reliability confirmed
```

---

## 📈 Continuous Improvement

### Feedback Integration

**Weekly:**
- Review all feedback
- Identify common patterns
- Prioritize improvements

**Monthly:**
- Update prompts based on feedback
- Refine reference ranges if needed
- Add new features if requested

### System Optimization

**Monitor:**
- Processing times (trend over time)
- Parse accuracy (by parameter type)
- Critical alert precision/recall
- Physician acceptance (by section)

**Optimize:**
- Prompts (iterative refinement)
- Reference ranges (hospital-specific)
- Report format (physician preferences)

---

## ✨ Next Steps After Successful Pilot

1. **Expand to More Patients**
   - Add additional patients gradually
   - Maintain same quality standards

2. **Integrate into Workflow**
   - Automate morning round processing
   - Set up automatic notifications
   - Create EHR integration (if feasible)

3. **Train Additional Users**
   - Expand to more physicians
   - Include residents/fellows
   - Document best practices

4. **Publish Results**
   - Prepare case studies
   - Write pilot report
   - Consider academic publication

---

**Good luck with your pilot! 🚀**

For questions or support, refer to project documentation or contact the development team.
