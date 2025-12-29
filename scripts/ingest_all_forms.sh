#!/bin/bash
TICKER=$1

if [ -z "$TICKER" ]; then
    echo "Usage: ./ingest_all_forms.sh <TICKER>"
    exit 1
fi

echo "Ingesting all forms for $TICKER..."

python ingest_edgar_data.py --ticker $TICKER --form-type 10-K --force
python ingest_edgar_data.py --ticker $TICKER --form-type 10-Q --force
python ingest_edgar_data.py --ticker $TICKER --form-type 8-K --force
python ingest_edgar_data.py --ticker $TICKER --form-type DEF 14A --force

echo "Done!"