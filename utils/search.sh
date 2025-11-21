#!/bin/bash
# Search patient notes and data

if [ -z "$1" ]; then
    echo "❌ Error: Search term required"
    echo "Usage: ./utils/search.sh SEARCH_TERM [PATIENT_ID]"
    echo "Example: ./utils/search.sh 'laktat' HT001"
    echo "         ./utils/search.sh 'E. coli'"
    exit 1
fi

SEARCH_TERM="$1"
PATIENT_ID="$2"

echo "🔍 Searching for: ${SEARCH_TERM}"
echo ""

if [ -n "$PATIENT_ID" ]; then
    SEARCH_PATH="patients/active/${PATIENT_ID}"
    echo "📂 Searching in patient: ${PATIENT_ID}"
else
    SEARCH_PATH="patients/active"
    echo "📂 Searching all active patients"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Search in notes
echo "📝 Clinical Notes:"
grep -r -i -n --color=always "${SEARCH_TERM}" "${SEARCH_PATH}/*/notes/" 2>/dev/null || echo "   No matches found"
echo ""

# Search in structured data
echo "📊 Structured Data:"
grep -r -i -n --color=always "${SEARCH_TERM}" "${SEARCH_PATH}/*/structured/" 2>/dev/null || echo "   No matches found"
echo ""

# Search in reports
echo "📄 Reports:"
grep -r -i -n --color=always "${SEARCH_TERM}" "${SEARCH_PATH}/*/reports/" 2>/dev/null || echo "   No matches found"
echo ""
