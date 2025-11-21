#!/bin/bash
# Create new patient directory structure and templates

# Check if patient ID provided
if [ -z "$1" ]; then
    echo "❌ Error: Patient ID required"
    echo "Usage: ./utils/new-patient.sh PATIENT_ID"
    echo "Example: ./utils/new-patient.sh HT002"
    exit 1
fi

PATIENT_ID="$1"
PATIENT_DIR="patients/active/${PATIENT_ID}"

# Check if patient already exists
if [ -d "$PATIENT_DIR" ]; then
    echo "⚠️  Warning: Patient ${PATIENT_ID} already exists!"
    echo "Directory: ${PATIENT_DIR}"
    exit 1
fi

# Create directory structure
echo "📁 Creating directory structure for patient ${PATIENT_ID}..."
mkdir -p "${PATIENT_DIR}/notes"
mkdir -p "${PATIENT_DIR}/structured"
mkdir -p "${PATIENT_DIR}/scores"
mkdir -p "${PATIENT_DIR}/trends"
mkdir -p "${PATIENT_DIR}/reports/daily"
mkdir -p "${PATIENT_DIR}/reports/weekly"
mkdir -p "${PATIENT_DIR}/reports/special"

# Copy and customize templates
echo "📄 Creating template files..."

# Demographics
sed "s/PATIENT_ID/${PATIENT_ID}/g" templates/new-patient.yaml > "${PATIENT_DIR}/demographics.yaml"

# Admission (create empty template)
cat > "${PATIENT_DIR}/admission.yaml" << 'EOF'
# ICU Admission Data
admission:
  date: "YYYY-MM-DD"
  time: "HH:MM"
  admission_source: "Emergency Department|Ward|Transfer"
  admission_type: "Emergency|Elective"

chief_complaint: ""

primary_diagnosis:
  diagnosis: ""
  icd10: ""
  secondary_diagnoses: []

admission_vitals:
  heart_rate:
  blood_pressure:
    systolic:
    diastolic:
    map:
  respiratory_rate:
  spo2:
  temperature:

admission_severity:
  initial_sofa:
  initial_apache_ii:

initial_interventions:
  fluid_resuscitation:
    type: ""
    volume_ml:

  vasopressors: []

  antibiotics: []

initial_plan: []

goals_of_care:
  code_status: "Full code|DNR|DNI"
  documented: true

notes: []
EOF

# Create README for patient
cat > "${PATIENT_DIR}/README.md" << EOF
# Patient ${PATIENT_ID}

## Directory Structure

- \`notes/\` - Clinical notes (Turkish text)
- \`structured/\` - Parsed JSON data
- \`scores/\` - Calculated SOFA/APACHE scores
- \`trends/\` - Trend analysis data
- \`reports/\` - Generated assessment reports
  - \`daily/\` - Daily assessment reports
  - \`weekly/\` - Weekly summaries
  - \`special/\` - Special reports (discharge, mortality review)

## Usage

### 1. Fill in patient information
Edit \`demographics.yaml\` and \`admission.yaml\` with patient data.

### 2. Add clinical notes
Create daily notes in \`notes/\` directory:
\`\`\`bash
vim notes/YYYY-MM-DD.txt
\`\`\`

### 3. Process notes
Use the parsing prompt to create structured data:
\`\`\`bash
# Example: Process today's note
claude-code "Parse patients/active/${PATIENT_ID}/notes/YYYY-MM-DD.txt using prompts/core/01-parse-note.md"
\`\`\`

### 4. Generate reports
\`\`\`bash
# Daily assessment
claude-code "Generate daily assessment for ${PATIENT_ID} using prompts/reports/30-daily-report.md"

# Weekly summary
claude-code "Generate weekly summary for ${PATIENT_ID} using prompts/reports/31-weekly-summary.md"
\`\`\`

## Quick Reference

- Admission Date: [Fill in]
- Diagnosis: [Fill in]
- Current Status: Active
EOF

echo ""
echo "✅ Patient ${PATIENT_ID} created successfully!"
echo ""
echo "📂 Directory: ${PATIENT_DIR}"
echo ""
echo "📝 Next steps:"
echo "   1. Edit demographics: ${PATIENT_DIR}/demographics.yaml"
echo "   2. Edit admission data: ${PATIENT_DIR}/admission.yaml"
echo "   3. Add clinical notes: ${PATIENT_DIR}/notes/YYYY-MM-DD.txt"
echo ""
echo "📖 See ${PATIENT_DIR}/README.md for usage instructions"
echo ""
