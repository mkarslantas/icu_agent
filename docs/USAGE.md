# Usage Guide

## Daily Workflow

### Morning Rounds Workflow

```bash
# 1. Add today's clinical note
vim patients/active/HT001/notes/$(date +%Y-%m-%d).txt
# [Paste ccNote transcript or type note]

# 2. Parse the note
claude-code "Parse patients/active/HT001/notes/$(date +%Y-%m-%d).txt using prompts/core/01-parse-note.md and save structured output to patients/active/HT001/structured/$(date +%Y-%m-%d).json"

# 3. Calculate SOFA score
claude-code "Using structured data from patients/active/HT001/structured/$(date +%Y-%m-%d).json, calculate SOFA score using prompts/analysis/13-calculate-scores.md"

# 4. Generate daily assessment
claude-code "Generate comprehensive daily assessment report in Turkish for patient HT001 using today's data and previous 2 days data. Use prompt prompts/reports/30-daily-report.md"

# 5. View the report
cat patients/active/HT001/reports/daily/$(date +%Y-%m-%d)_assessment.md
```

### Quick Daily Tasks

```bash
# Quick parse and report (combined)
PATIENT="HT001"
DATE=$(date +%Y-%m-%d)

# Parse note
claude-code "Parse patients/active/${PATIENT}/notes/${DATE}.txt using prompts/core/01-parse-note.md. Save to patients/active/${PATIENT}/structured/${DATE}.json"

# Generate report
claude-code "Generate daily assessment for ${PATIENT} from ${DATE} structured data using prompts/reports/30-daily-report.md. Save to patients/active/${PATIENT}/reports/daily/${DATE}_assessment.md"
```

## Common Tasks

### Adding a New Patient

```bash
# Create patient structure
./utils/new-patient.sh HT003

# Edit demographics
vim patients/active/HT003/demographics.yaml

# Edit admission data
vim patients/active/HT003/admission.yaml

# Add admission note
vim patients/active/HT003/notes/2025-11-21-admission.txt
```

### Processing Clinical Notes

#### Simple Parse

```bash
claude-code "Parse this Turkish clinical note using prompts/core/01-parse-note.md: [paste note text]"
```

#### Parse from File

```bash
claude-code "Read and parse patients/active/HT001/notes/2025-11-20-day5.txt using prompts/core/01-parse-note.md. Return structured JSON only."
```

### Generating Reports

#### Daily Assessment

```bash
claude-code "Generate comprehensive Turkish daily assessment for patient HT001 using data from structured/2025-11-21.json and previous 2 days. Use prompt prompts/reports/30-daily-report.md. Save to reports/daily/2025-11-21_assessment.md"
```

#### Weekly Summary

```bash
claude-code "Analyze 7 days of data for patient HT001 (2025-11-15 to 2025-11-21) and generate weekly summary using prompts/reports/31-weekly-summary.md"
```

#### Trend Analysis

```bash
claude-code "Perform 7-day trend analysis for HT001 using structured data from past week. Use prompt prompts/analysis/11-trend-analysis.md. Generate Turkish markdown report."
```

### Clinical Recommendations

#### Vasopressor Management

```bash
claude-code "Analyze hemodynamics for HT001 from today's structured data. Provide vasopressor management recommendations in Turkish using prompts/recommendations/20-vasopressor-mgmt.md"
```

#### Ventilator Weaning

```bash
claude-code "Evaluate weaning readiness for HT001 based on respiratory data in structured/2025-11-21.json. Use prompts/recommendations/21-ventilator-weaning.md for Turkish recommendations"
```

#### Antibiotic Stewardship

```bash
claude-code "Review infection data and antibiotic therapy for HT001. Provide stewardship recommendations using prompts/recommendations/22-antibiotic-steward.md. Output in Turkish"
```

### Calculating Scores

#### SOFA Score

```bash
claude-code "Calculate SOFA score from structured data in patients/active/HT001/structured/2025-11-21.json using prompts/analysis/13-calculate-scores.md. Include delta SOFA if previous available."
```

#### APACHE-II (Admission)

```bash
claude-code "Calculate APACHE-II score from admission data in patients/active/HT001/admission.yaml using scoring criteria in config/scoring-criteria.yaml"
```

## Searching and Analysis

### Search Patient Notes

```bash
# Search specific patient
./utils/search.sh "laktat" HT001

# Search all patients
./utils/search.sh "E. coli"

# Search for vasopressor changes
./utils/search.sh "noradrenalin azaldı"
```

### System Statistics

```bash
# View system stats
./utils/stats.sh

# Output:
# Active Patients: 3
# Discharged Patients: 1
# Storage Usage: 15M
```

## Data Management

### Backup

```bash
# Manual backup
./utils/backup.sh

# Backup with note
./utils/backup.sh  # Creates timestamped backup in backups/

# Restore from backup
tar -xzf backups/20251121_140530.tar.gz -C backups/
# Then copy desired files back
```

### Moving Patient to Discharged

```bash
PATIENT="HT001"

# Move to discharged
mv patients/active/${PATIENT} patients/discharged/

# Update status file
echo "Discharged: $(date)" > patients/discharged/${PATIENT}/status.txt
```

### Archiving Old Data

```bash
# Archive patients from >90 days ago
find patients/discharged -type d -mtime +90 -exec tar -czf archived-{}.tar.gz {} \;
```

## Advanced Usage

### Batch Processing Multiple Patients

```bash
#!/bin/bash
# Process all active patients

for patient_dir in patients/active/*/; do
    patient_id=$(basename "$patient_dir")
    echo "Processing ${patient_id}..."

    # Find today's note
    today=$(date +%Y-%m-%d)
    note_file="${patient_dir}notes/${today}.txt"

    if [ -f "$note_file" ]; then
        # Parse and generate report
        claude-code "Process ${note_file} and generate daily report for ${patient_id}"
    else
        echo "  No note found for today"
    fi
done
```

### Custom Report Generation

```bash
# Create custom prompt for specific analysis
cat > /tmp/custom_analysis.md << 'EOF'
Analyze the following patient data and provide:
1. Risk of AKI progression
2. Renal recovery likelihood
3. RRT indication assessment

Output in Turkish markdown.
EOF

claude-code "Using /tmp/custom_analysis.md, analyze HT001's renal function from structured data"
```

### Exporting Data

```bash
# Export structured data to CSV (if you have jq)
jq -r '.patient_info, .hemodynamics, .renal' patients/active/HT001/structured/2025-11-21.json > export.csv
```

## Tips and Best Practices

### Efficient Note-Taking

1. **Use consistent format** - Follow template in `templates/daily-note.txt`
2. **Include trends** - Always mention if values increased/decreased
3. **Be specific** - "nokta on beş" clearer than "düşük doz"
4. **Reference previous** - "önceki değer iki nokta bir idi"

### Prompt Usage

1. **Be specific** - Reference exact file paths
2. **State desired output** - "Return JSON only" or "Generate Turkish report"
3. **Include context** - Mention previous data if needed for trends
4. **Save outputs** - Always specify where to save results

### Data Quality

1. **Review parsed data** - Check structured JSON for accuracy
2. **Verify critical values** - Double-check flagged values
3. **Validate trends** - Ensure trend detection makes sense
4. **Update demographics** - Keep patient info current

### Performance

1. **Use example data** - Test prompts with HT001 first
2. **Batch similar tasks** - Process multiple patients together
3. **Cache frequently used** - Save commonly accessed reports
4. **Clean old logs** - Periodically remove old backup logs

## Troubleshooting

### Issue: Parser misses values

**Solution**: Ensure numbers written as Turkish words:
- Use "nokta" for decimal: "bir nokta beş" not "1.5"
- Use "yüzde" for percent: "yüzde doksan" not "90%"

### Issue: Trends not detected

**Solution**: Include comparison phrases:
- "önceki değer ... idi"
- "azaldı" / "arttı"
- Explicit previous values

### Issue: Report recommendations too vague

**Solution**: Ensure structured data includes:
- Previous day data for comparison
- Complete vital signs
- All relevant labs

### Issue: Critical values not flagged

**Solution**: Check reference ranges in `config/reference-ranges.yaml`

## Example Workflows

### Complete New Patient Workflow

```bash
# Day 1: Admission
./utils/new-patient.sh HT004
vim patients/active/HT004/demographics.yaml  # Fill in
vim patients/active/HT004/admission.yaml     # Fill in
vim patients/active/HT004/notes/2025-11-21-admission.txt  # Admission note

# Parse admission note
claude-code "Parse admission note and save structured data"

# Calculate admission APACHE-II
claude-code "Calculate APACHE-II from admission data"

# Day 2-N: Daily notes
vim patients/active/HT004/notes/$(date +%Y-%m-%d).txt
claude-code "Parse note → Calculate SOFA → Generate daily report"

# Day 7: Weekly summary
claude-code "Generate 7-day weekly summary for HT004"

# Discharge: Move patient
mv patients/active/HT004 patients/discharged/
claude-code "Generate discharge summary for HT004"
```

## Quick Reference Card

```bash
# Daily essentials
./utils/new-patient.sh ID         # New patient
./utils/stats.sh                  # System stats
./utils/search.sh TERM [ID]       # Search
./utils/backup.sh                 # Backup

# Processing
# 1. Add note: vim patients/active/ID/notes/DATE.txt
# 2. Parse: claude-code "Parse using prompts/core/01-parse-note.md"
# 3. Report: claude-code "Generate using prompts/reports/30-daily-report.md"

# Recommendations
# prompts/recommendations/20-vasopressor-mgmt.md
# prompts/recommendations/21-ventilator-weaning.md
# prompts/recommendations/22-antibiotic-steward.md
```

## Next Steps

- Review [CLINICAL_GUIDELINES.md](CLINICAL_GUIDELINES.md) for clinical protocols
- Check [SCORING_SYSTEMS.md](SCORING_SYSTEMS.md) for score interpretation
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

Happy monitoring! 🏥
