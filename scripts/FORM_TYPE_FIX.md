# Form Type Argument Fix

**Date:** 2025-12-28  
**Issue:** DEF 14A form type with space causing argument parsing error  
**Status:** ✅ Fixed

---

## Problem Identified

The `ingest_all_forms.sh` script was failing when trying to ingest DEF 14A because:

1. **Shell Script Issue:** Form type `DEF 14A` (with space) was not quoted
2. **Argument Splitting:** Bash split `DEF 14A` into two separate arguments: `DEF` and `14A`
3. **Python Received Wrong Value:** Python script received only `DEF` as form-type, causing edgartools lookup to fail

### Example of the Problem

**Before (Broken):**
```bash
python ingest_edgar_data.py --ticker $TICKER --form-type DEF 14A --force
```

This was interpreted as:
- `--form-type DEF`
- `14A` (extra positional argument)
- `--force`

**After (Fixed):**
```bash
python ingest_edgar_data.py --ticker "$TICKER" --form-type "DEF 14A" --force
```

This correctly passes:
- `--form-type "DEF 14A"` (single argument with space)

---

## Changes Made

### 1. Fixed Shell Script Quoting

**File:** `scripts/ingest_all_forms.sh`

**Changes:**
- Added quotes around all form types: `"10-K"`, `"10-Q"`, `"8-K"`, `"DEF 14A"`
- Added quotes around `$TICKER` variable for safety
- Ensures proper argument passing to Python script

**Before:**
```bash
python ingest_edgar_data.py --ticker $TICKER --form-type DEF 14A --force
```

**After:**
```bash
python ingest_edgar_data.py --ticker "$TICKER" --form-type "DEF 14A" --force
```

### 2. Enhanced Form Type Normalization

**File:** `scripts/utils/edgar_client.py`

**Changes:**
- Added form type normalization logic
- Handles both `"DEF 14A"` and `"DEF14A"` formats
- Tries alternative format if first attempt fails
- Better error logging for debugging

**New Logic:**
```python
# Normalize form type for edgartools (handle spaces and variations)
normalized_form_type = form_type
if form_type.upper() == "DEF 14A" or form_type.upper() == "DEF14A":
    normalized_form_type = "DEF 14A"  # Standard SEC format
    logger.debug(f"Normalized form type: {form_type} -> {normalized_form_type}")

# Try alternative format if first attempt fails
if not filing and normalized_form_type == "DEF 14A":
    logger.debug(f"Trying alternative form type format: DEF14A")
    try:
        filings = company.get_filings(form="DEF14A")
        filing = filings[0] if len(filings) > 0 else None
        if filing:
            normalized_form_type = "DEF14A"
            logger.info(f"Found filing using alternative form type: DEF14A")
    except Exception as e:
        logger.debug(f"Alternative form type failed: {e}")
```

---

## Testing

### Test the Fix

1. **Test Shell Script:**
   ```bash
   cd /Users/rnellapalle/learn-poc/fingpt-phase2/Research/edgar-graphdb/scripts
   ./ingest_all_forms.sh AAPL
   ```

2. **Test Individual Form:**
   ```bash
   python ingest_edgar_data.py --ticker AAPL --form-type "DEF 14A" --force
   ```

3. **Verify Logs:**
   - Check `logs/ingest_20251228.log` for DEF 14A ingestion
   - Should see: `Form Type: DEF 14A`
   - Should see: `Fetched filing data for AAPL DEF 14A: ...`
   - Should see sections extracted successfully

### Expected Results

After the fix:
- ✅ Shell script passes `"DEF 14A"` correctly to Python
- ✅ Python receives complete form type string
- ✅ edgartools finds DEF 14A filings
- ✅ Sections are extracted successfully
- ✅ Ingestion completes without errors

---

## Related Issues

This fix addresses:
1. **Shell Script Argument Parsing:** Quotes prevent space splitting
2. **Form Type Variations:** Handles both `"DEF 14A"` and `"DEF14A"` formats
3. **Error Handling:** Better logging for debugging form type issues

---

## Best Practices

### For Shell Scripts with Spaces

Always quote arguments that may contain spaces:

```bash
# ✅ Good - Quotes preserve spaces
python script.py --form-type "DEF 14A"

# ❌ Bad - Spaces cause argument splitting
python script.py --form-type DEF 14A
```

### For Form Types

1. **Use Standard SEC Format:** `"DEF 14A"` (with space) is the official SEC format
2. **Quote in Shell Scripts:** Always quote form types in bash scripts
3. **Normalize in Code:** Handle variations (`DEF14A`, `DEF-14A`, etc.) in Python code

---

## Files Modified

1. **`scripts/ingest_all_forms.sh`**
   - Added quotes around all form types
   - Added quotes around `$TICKER` variable

2. **`scripts/utils/edgar_client.py`**
   - Added form type normalization logic
   - Added fallback to alternative format
   - Enhanced error logging

---

**Fix Status:** ✅ Complete  
**Testing Status:** ⏳ Ready for user verification

