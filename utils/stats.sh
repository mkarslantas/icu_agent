#!/bin/bash
# Generate statistics about ICU patients

echo "📊 ICU MONITORING SYSTEM STATISTICS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Count active patients
ACTIVE_COUNT=$(find patients/active -maxdepth 1 -type d | tail -n +2 | wc -l)
echo "👥 Active Patients: ${ACTIVE_COUNT}"

# List active patients
if [ ${ACTIVE_COUNT} -gt 0 ]; then
    echo ""
    echo "Active Patient List:"
    for patient_dir in patients/active/*/; do
        if [ -d "$patient_dir" ]; then
            patient_id=$(basename "$patient_dir")
            note_count=$(find "${patient_dir}notes/" -name "*.txt" 2>/dev/null | wc -l)
            report_count=$(find "${patient_dir}reports/" -name "*.md" 2>/dev/null | wc -l)
            echo "   • ${patient_id}: ${note_count} notes, ${report_count} reports"
        fi
    done
fi

echo ""

# Count discharged patients
DISCHARGED_COUNT=$(find patients/discharged -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l)
echo "🏠 Discharged Patients: ${DISCHARGED_COUNT}"

# Count deceased patients
DECEASED_COUNT=$(find patients/deceased -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l)
echo "💐 Deceased Patients: ${DECEASED_COUNT}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Storage usage
TOTAL_SIZE=$(du -sh patients/ 2>/dev/null | cut -f1)
echo "💾 Storage Usage: ${TOTAL_SIZE}"

# Backup info
BACKUP_COUNT=$(ls -1 backups/*.tar.gz 2>/dev/null | wc -l)
echo "🗄️  Backups Available: ${BACKUP_COUNT}"

echo ""
