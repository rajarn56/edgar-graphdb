#!/bin/bash
# Ingest all EDGAR form types for a ticker
# Usage: ./ingest_all_forms.sh <TICKER> [category]
# Categories: all, periodic, proxy, registration, ownership, investment, foreign, other

TICKER=$1
CATEGORY=${2:-"all"}  # Default to "all" if not specified

if [ -z "$TICKER" ]; then
    echo "Usage: ./ingest_all_forms.sh <TICKER> [category]"
    echo ""
    echo "Categories:"
    echo "  all          - All form types (default)"
    echo "  periodic     - Periodic reports (10-K, 10-Q, 8-K)"
    echo "  proxy        - Proxy & governance (DEF 14A, DEF 14C)"
    echo "  registration - Registration statements (S-1, S-3, S-4, 10)"
    echo "  ownership    - Ownership & insider trading (3, 4, 5, 13D, 13G)"
    echo "  investment   - Investment & benefit plans (13F, N-CSR, 11-K)"
    echo "  foreign      - Foreign issuers (20-F, 40-F)"
    echo "  other        - Other forms (144, 424B)"
    exit 1
fi

echo "=========================================="
echo "Ingesting EDGAR forms for $TICKER"
echo "Category: $CATEGORY"
echo "=========================================="

# Define form arrays by category
PERIODIC_FORMS=("10-K" "10-Q" "8-K")
PROXY_FORMS=("DEF 14A" "DEF 14C")
REGISTRATION_FORMS=("S-1" "S-3" "S-4" "10")
OWNERSHIP_FORMS=("3" "4" "5" "13D" "13G")
INVESTMENT_FORMS=("13F" "N-CSR" "11-K")
FOREIGN_FORMS=("20-F" "40-F")
OTHER_FORMS=("144" "424B")

# Combine all forms
ALL_FORMS=(
  "${PERIODIC_FORMS[@]}"
  "${PROXY_FORMS[@]}"
  "${REGISTRATION_FORMS[@]}"
  "${OWNERSHIP_FORMS[@]}"
  "${INVESTMENT_FORMS[@]}"
  "${FOREIGN_FORMS[@]}"
  "${OTHER_FORMS[@]}"
)

# Select forms to ingest based on category
case "$CATEGORY" in
  "all")
    FORMS_TO_INGEST=("${ALL_FORMS[@]}")
    ;;
  "periodic")
    FORMS_TO_INGEST=("${PERIODIC_FORMS[@]}")
    ;;
  "proxy")
    FORMS_TO_INGEST=("${PROXY_FORMS[@]}")
    ;;
  "registration")
    FORMS_TO_INGEST=("${REGISTRATION_FORMS[@]}")
    ;;
  "ownership")
    FORMS_TO_INGEST=("${OWNERSHIP_FORMS[@]}")
    ;;
  "investment")
    FORMS_TO_INGEST=("${INVESTMENT_FORMS[@]}")
    ;;
  "foreign")
    FORMS_TO_INGEST=("${FOREIGN_FORMS[@]}")
    ;;
  "other")
    FORMS_TO_INGEST=("${OTHER_FORMS[@]}")
    ;;
  *)
    echo "Warning: Unknown category '$CATEGORY', using 'all'"
    FORMS_TO_INGEST=("${ALL_FORMS[@]}")
    ;;
esac

# Counters for success/failure tracking
SUCCESS_COUNT=0
FAILURE_COUNT=0
FAILED_FORMS=()

# Ingest each form
for FORM in "${FORMS_TO_INGEST[@]}"; do
  echo ""
  echo "----------------------------------------"
  echo "Ingesting $FORM for $TICKER..."
  echo "----------------------------------------"
  
  if python ingest_edgar_data.py --ticker "$TICKER" --form-type "$FORM" --force; then
    echo "✅ Successfully ingested $FORM"
    ((SUCCESS_COUNT++))
  else
    echo "❌ Failed to ingest $FORM"
    ((FAILURE_COUNT++))
    FAILED_FORMS+=("$FORM")
  fi
done

# Summary
echo ""
echo "=========================================="
echo "Ingestion Summary"
echo "=========================================="
echo "Total forms attempted: ${#FORMS_TO_INGEST[@]}"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $FAILURE_COUNT"

if [ $FAILURE_COUNT -gt 0 ]; then
  echo ""
  echo "Failed forms:"
  for FORM in "${FAILED_FORMS[@]}"; do
    echo "  - $FORM"
  done
  echo ""
  echo "Note: Some forms may not be available for this ticker or may require"
  echo "      additional extraction strategy implementation."
fi

echo ""
echo "Done!"