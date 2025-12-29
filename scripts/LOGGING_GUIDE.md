# EDGAR Ingestion Logging Guide

**Purpose:** Understand log messages to distinguish between data availability issues and processing failures

## Log Message Categories

All log messages are prefixed with status tags to make them easy to identify:

### 1. `[DATA_NOT_AVAILABLE]` - Form Doesn't Exist

**Meaning:** The form type doesn't exist in edgar-tools for this ticker.

**Example:**
```
[DATA_NOT_AVAILABLE] No S-1 filing found for AAPL (tried variants: ['S-1', 'S1'])
[STATUS] Form S-1 does not exist in edgar-tools for AAPL - this is expected if the company hasn't filed this form type
[ACTION] Skipping S-1 ingestion for AAPL - no action needed
```

**What This Means:**
- ✅ **Normal behavior** - Some companies don't file certain form types
- ✅ **No data loss** - There was no data to begin with
- ✅ **No action needed** - This is expected

**Common Cases:**
- S-1 (IPO registration) - Only filed when company goes public
- 13D/13G - Only filed when someone acquires 5%+ ownership
- 20-F - Only for foreign companies
- 40-F - Only for Canadian companies

---

### 2. `[PROCESSING_FAILED]` - Extraction/Transformation Failed

**Meaning:** The form exists in edgar-tools but extraction or transformation failed.

**Example:**
```
[PROCESSING_FAILED] No items extracted from filing 0000320193-25-000073 for 10-Q
[STATUS] Filing exists in edgar-tools but extraction failed - data may be lost
[ACTION] Check extraction strategy and form structure - may need to update mappings or add fallback handling
```

**What This Means:**
- ❌ **Problem** - Data exists but couldn't be extracted
- ⚠️ **Data loss risk** - Data may be lost if not fixed
- 🔧 **Action needed** - Review extraction strategy

**Common Causes:**
- Form structure changed
- Extraction mappings don't match actual attributes
- HTML/text parsing patterns don't match format
- Exception during extraction

**What to Do:**
1. Check debug logs for form structure details
2. Review extraction strategy for this form type
3. Update form mappings in `form_config.yaml`
4. Add fallback extraction if needed

---

### 3. `[CHUNKING_FAILED]` - Chunking/Embedding Failed

**Meaning:** Data was extracted but chunking or embedding generation failed.

**Example:**
```
[CHUNKING_FAILED] No sections created from 3 items
[STATUS] Data extraction succeeded but chunking failed - data will be lost
[ACTION] Review transformation and chunking logic
```

**What This Means:**
- ❌ **Problem** - Data extracted but not processed
- ⚠️ **Data loss** - Extracted data won't be stored
- 🔧 **Action needed** - Review chunking logic

**Common Causes:**
- Content too short for chunking
- Transformation logic error
- Embedding generation failure
- Database write error

**What to Do:**
1. Check content length and chunking parameters
2. Review transformation logic
3. Check embedding service connectivity
4. Review database connection

---

### 4. `[FALLBACK_INSPECTION]` - Using Fallback Method

**Meaning:** Primary extraction method didn't work, using fallback inspection.

**Example:**
```
[FALLBACK_INSPECTION] No items found using mappings for TenQ, inspecting object structure...
[EXPLANATION] Fallback inspection means the script doesn't know the exact structure of this form type's data
[EXPLANATION] It will automatically search through all object attributes to find content - data will NOT be lost
[SUCCESS] Fallback inspection found 4 items - data preserved
```

**What This Means:**
- ✅ **Working as designed** - Fallback mechanism activated
- ✅ **No data loss** - Data is preserved via fallback
- ℹ️ **Informational** - May want to update mappings for better performance

**What is Fallback Inspection?**

Fallback inspection is an automatic recovery mechanism that:

1. **When it activates:** When the primary extraction method (using known mappings) doesn't find any content
2. **What it does:** Automatically searches through all object attributes to find content
3. **Data safety:** Data is NOT lost - it's extracted via fallback
4. **Performance:** May be slower than using known mappings

**Example Flow:**
```
Primary Method (StructuredObjectStrategy):
  - Try to extract using known mappings (e.g., "business" → Item 1)
  - If no items found → Activate fallback

Fallback Inspection:
  - Inspect all object attributes
  - Find attributes with content (e.g., "business_description", "business_overview")
  - Extract content from found attributes
  - Data preserved!
```

**When to Update Mappings:**
- If fallback inspection consistently finds the same attributes
- To improve extraction performance
- To ensure consistent section naming

---

### 5. `[SUCCESS]` - Operation Completed Successfully

**Meaning:** Operation completed successfully.

**Example:**
```
[SUCCESS] Extracted 3 items/sections from filing 0000320193-25-000079
[SUCCESS] Found 3 items/sections to process
[SUCCESS] Fallback inspection found 4 items - data preserved
```

**What This Means:**
- ✅ **Everything working** - No action needed

---

## Log Message Format

All log messages follow this format:

```
[CATEGORY] Main message
[STATUS] Current status description
[ACTION] What to do (if needed)
[DEBUG] Technical details (if debug logging enabled)
```

## Quick Reference

| Category | Data Loss Risk | Action Needed | Severity |
|----------|----------------|---------------|----------|
| `[DATA_NOT_AVAILABLE]` | None | None | Info |
| `[PROCESSING_FAILED]` | High | Yes | Error |
| `[CHUNKING_FAILED]` | High | Yes | Error |
| `[FALLBACK_INSPECTION]` | None | Optional | Warning |
| `[SUCCESS]` | None | None | Info |

## Searching Logs

### Find all processing failures:
```bash
grep "\[PROCESSING_FAILED\]" logs/ingest_*.log
```

### Find all data not available:
```bash
grep "\[DATA_NOT_AVAILABLE\]" logs/ingest_*.log
```

### Find all fallback inspections:
```bash
grep "\[FALLBACK_INSPECTION\]" logs/ingest_*.log
```

### Find all chunking failures:
```bash
grep "\[CHUNKING_FAILED\]" logs/ingest_*.log
```

## Example Log Analysis

### Good Run (10-K):
```
[SUCCESS] Extracted 3 items/sections from filing 0000320193-25-000079
[SUCCESS] Found 3 items/sections to process
Creating 3 sections with 30 total chunks...
Successfully ingested filing 0000320193-25-000079
```

### Form Doesn't Exist (S-1):
```
[DATA_NOT_AVAILABLE] No S-1 filing found for AAPL
[STATUS] Form S-1 does not exist in edgar-tools for AAPL
[ACTION] Skipping S-1 ingestion for AAPL - no action needed
```

### Extraction Failed (10-Q):
```
[PROCESSING_FAILED] No items extracted from filing 0000320193-25-000073 for 10-Q
[STATUS] Filing exists in edgar-tools but extraction failed - data may be lost
[ACTION] Check extraction strategy and form structure
```

### Fallback Working (DEF 14A):
```
[FALLBACK_INSPECTION] No items found using mappings for ProxyStatement, inspecting object structure...
[EXPLANATION] Fallback inspection means the script doesn't know the exact structure...
[SUCCESS] Fallback inspection found 5 items - data preserved
```

## Troubleshooting Workflow

1. **Check for `[PROCESSING_FAILED]`** - These need immediate attention
2. **Check for `[CHUNKING_FAILED]`** - These indicate processing issues
3. **Review `[FALLBACK_INSPECTION]`** - Consider updating mappings
4. **Ignore `[DATA_NOT_AVAILABLE]`** - These are normal

## Summary

- **`[DATA_NOT_AVAILABLE]`**: Form doesn't exist - normal, no action needed
- **`[PROCESSING_FAILED]`**: Extraction failed - needs investigation, data may be lost
- **`[CHUNKING_FAILED]`**: Chunking failed - needs investigation, data will be lost
- **`[FALLBACK_INSPECTION]`**: Using fallback - working, data preserved, may want to update mappings
- **`[SUCCESS]`**: Everything working - no action needed

**Fallback Inspection = Automatic Recovery**: When primary method fails, script automatically searches for content. Data is NOT lost, but you may want to update mappings for better performance.

