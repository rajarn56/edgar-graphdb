# Troubleshooting Guide

This document collects troubleshooting information, fixes, and debugging techniques for the EDGAR Graph Database scripts.

## Table of Contents

1. [Neo4j Session Commit Error](#neo4j-session-commit-error)
2. [Cypher MERGE Syntax Error](#cypher-merge-syntax-error)
3. [Date Parsing Error](#date-parsing-error)
4. [Mock Data Instead of Real EDGAR Data](#mock-data-instead-of-real-edgar-data)
5. [Debug Logging](#debug-logging)
6. [Common Issues](#common-issues)

---

## Neo4j Session Commit Error

### Issue

**Error Message:**
```
'Session' object has no attribute 'commit'
```

**Symptoms:**
- All write operations fail (constraints, indexes, vector indexes, fulltext indexes)
- Error occurs in `utils.neo4j_client.execute_write()` method
- Script fails during schema setup

**Date Fixed:** 2025-12-28

### Root Cause

The Neo4j Python driver's `Session` object does not have a `commit()` method. The driver uses **auto-commit transactions** - transactions are automatically committed when:

1. The result is consumed (by iterating over it or calling `.single()`)
2. The session context exits (when the `with` block ends)

The code was incorrectly trying to call `session.commit()` after executing queries, which doesn't exist in the Neo4j Python driver API.

### Solution

**Fixed in:** `scripts/utils/neo4j_client.py`

**Changes Made:**
1. Removed `session.commit()` calls from `execute_write()` method (line ~168)
2. Removed `session.commit()` call from `execute_transaction()` method (line ~244)
3. Added comments explaining that Neo4j auto-commits transactions

**Code Before:**
```python
with self.session() as session:
    result = session.run(query, parameters)
    records = [dict(record) for record in result]
    session.commit()  # ❌ This doesn't exist!
    return records
```

**Code After:**
```python
with self.session() as session:
    result = session.run(query, parameters)
    records = [dict(record) for record in result]
    # Note: Neo4j Python driver auto-commits transactions when session context exits
    # No explicit commit() call needed
    return records
```

### Verification

After the fix:
- Schema setup script runs successfully
- All constraints, indexes, and vector indexes are created
- No errors in logs

### Related Files

- `scripts/utils/neo4j_client.py` - Fixed methods: `execute_write()`, `execute_transaction()`
- `scripts/setup_schema.py` - Uses the fixed client methods

---

## Cypher MERGE Syntax Error

### Issue

**Error Message:**
```
Invalid input 'ON': expected an expression, ',', 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'WITH' or <EOF> (line 10, column 5 (offset: 279))
"    ON CREATE SET c.created_at = datetime()"
     ^
```

**Symptoms:**
- Data ingestion script fails when creating Company, Filing, Section, or Period nodes
- Error occurs in `ingest_edgar_data.py` during node creation
- Script fails immediately after attempting to create company node
- Error log shows syntax error in Cypher query

**Date Fixed:** 2025-12-28

### Root Cause

In Cypher, when using `MERGE` statements, you cannot place a `SET` clause before `ON CREATE SET`. The correct syntax requires `ON CREATE SET` and `ON MATCH SET` to come immediately after `MERGE`, before any standalone `SET` clause.

The code was incorrectly structured as:
```cypher
MERGE (c:Company {cik: $cik})
SET c.name = $name, ...  // ❌ SET before ON CREATE SET is invalid
ON CREATE SET c.created_at = datetime()
```

This violates Cypher syntax rules where `ON CREATE SET` and `ON MATCH SET` must directly follow `MERGE`.

### Solution

**Fixed in:** `scripts/ingest_edgar_data.py`

**Functions Fixed:**
1. `create_company_node()` - Line 43-63
2. `create_filing_node()` - Line 62-96
3. `create_section_node()` - Line 149-192
4. Period node creation in `create_filing_node()` - Line 102-138

**Code Before:**
```python
query = """
MERGE (c:Company {cik: $cik})
SET c.name = $name,
    c.ticker = $ticker,
    c.updated_at = datetime()
ON CREATE SET c.created_at = datetime()
RETURN c.cik AS cik
"""
```

**Code After:**
```python
query = """
MERGE (c:Company {cik: $cik})
ON CREATE SET c.created_at = datetime(),
    c.name = $name,
    c.ticker = $ticker,
    c.updated_at = datetime()
ON MATCH SET c.name = $name,
    c.ticker = $ticker,
    c.updated_at = datetime()
RETURN c.cik AS cik
"""
```

**Key Changes:**
- Moved all property assignments into `ON CREATE SET` and `ON MATCH SET` clauses
- `ON CREATE SET` handles properties when node is first created
- `ON MATCH SET` handles properties when node already exists
- Ensures `created_at` is only set on creation, while other properties update on both create and match

### Verification

After the fix:
- Ingestion script runs successfully
- Company, Filing, Section, and Period nodes are created correctly
- No Cypher syntax errors in logs
- Data ingestion completes successfully

### Related Files

- `scripts/ingest_edgar_data.py` - Fixed all MERGE queries with incorrect SET/ON CREATE SET ordering
- `scripts/logs/errors_20251228.log` - Contains original error logs

---

## Date Parsing Error

### Issue

**Error Message:**
```
Text cannot be parsed to a Date
""
 ^
error: data exception - invalid date, time, or datetime format
```

**Symptoms:**
- Ingestion script fails when creating Filing or Period nodes
- Error occurs in `create_filing_node()` or Period node creation
- Error message shows empty string `""` being passed to `date()` function
- Script fails immediately after successfully creating company node

**Date Fixed:** 2025-12-28

### Root Cause

When EDGAR data is retrieved, some date fields (`filing_date`, `period_end_date`, `period_start`, `period_end`) may be empty strings `""` or `None` if the data source doesn't provide them. The code was attempting to pass these empty strings directly to Neo4j's `date()` function, which cannot parse empty strings and throws a syntax error.

The issue occurred in:
1. `create_filing_node()` - when setting `filing_date` and `period_end_date`
2. Period node creation - when setting `period_start` and `period_end`

### Solution

**Fixed in:** `scripts/ingest_edgar_data.py`

**Functions Fixed:**
1. `create_filing_node()` - Line 69-146
2. Period node creation in `create_filing_node()` - Line 126-154

**Code Before:**
```python
filing_date = filing_props.get("filing_date") or ""
period_end_date = filing_props.get("period_end_date") or ""

query = """
MERGE (f:Filing {accession_number: $accession_number})
SET f.filing_date = date($filing_date),  # ❌ Fails if $filing_date is ""
    f.period_end_date = date($period_end_date)  # ❌ Fails if empty
"""
```

**Code After:**
```python
# Normalize empty strings to None
filing_date = filing_props.get("filing_date")
period_end_date = filing_props.get("period_end_date")
filing_date = filing_date.strip() if filing_date and filing_date.strip() else None
period_end_date = period_end_date.strip() if period_end_date and period_end_date.strip() else None

query = """
MERGE (f:Filing {accession_number: $accession_number})
ON CREATE SET 
    f.filing_date = CASE WHEN $filing_date IS NOT NULL AND $filing_date <> '' 
                         THEN date($filing_date) ELSE null END,
    f.period_end_date = CASE WHEN $period_end_date IS NOT NULL AND $period_end_date <> '' 
                              THEN date($period_end_date) ELSE null END
"""
```

**Key Changes:**
- Added validation to normalize empty strings to `None`
- Used `CASE WHEN` in Cypher to conditionally parse dates only when they're not empty
- Set dates to `null` in Neo4j when values are empty (instead of trying to parse empty strings)
- Applied same fix to Period node creation for `period_start` and `period_end`

### Verification

After the fix:
- Ingestion script runs successfully even when date fields are empty
- Filing and Period nodes are created with `null` dates when data is unavailable
- No date parsing errors in logs
- Data ingestion completes successfully

### Related Files

- `scripts/ingest_edgar_data.py` - Fixed date handling in `create_filing_node()` and Period node creation
- `scripts/utils/edgar_client.py` - May return empty date strings from EDGAR data
- `scripts/utils/data_transformer.py` - Transforms EDGAR data which may have empty dates
- `scripts/logs/errors_20251228.log` - Contains original error logs

---

## Mock Data Instead of Real EDGAR Data

### Issue

**Warning Messages:**
```
WARNING | utils.edgar_client:_initialize_client:41 | Could not import edgar-tools library. Using mock implementation.
WARNING | utils.edgar_client:_initialize_client:42 | Please install edgar-tools: pip install edgar-tools
WARNING | utils.edgar_client:_mock_filing_data:246 | Using mock filing data for AAPL 10-K (edgar-tools not available)
WARNING | utils.edgar_client:_mock_company_data:233 | Using mock company data for AAPL (edgar-tools not available)
```

**Symptoms:**
- Ingestion script runs successfully but uses mock/test data instead of real SEC EDGAR data
- Logs show warnings about edgar-tools library not being available
- Data ingested contains placeholder/mock values (e.g., "AAPL Inc." instead of "Apple Inc.")
- Mock data structure matches expected format but contains fake content

**Date Identified:** 2025-12-28

### Root Cause

The `EdgarClient` class in `utils/edgar_client.py` attempts to import the `edgar-tools` library to fetch real SEC EDGAR data. If the library is not installed or cannot be imported, it falls back to a mock implementation that generates test data.

The client tries to import several possible module names:
- `edgar_tools`
- `edgar_tools.client`
- `sec_edgar`
- `sec_edgar.client`
- `edgar`

If none of these are found, it logs a warning and uses mock data instead of failing.

### Solution

**Install the edgartools Library:**

The project uses `edgartools` library (https://github.com/dgunning/edgartools) for fetching SEC EDGAR data.

**Step 1: Install edgartools**
```bash
pip install edgartools
```

Or update from requirements.txt:
```bash
pip install -r requirements.txt
```

**Step 2: Set Your SEC EDGAR Identity**

The SEC requires you to identify yourself when accessing EDGAR data. Set your email address as an environment variable:

```bash
# In your .env file (recommended)
EDGAR_IDENTITY=your.email@example.com

# Or export in shell
export EDGAR_IDENTITY=your.email@example.com
```

**Important:** Use a valid email address. The SEC uses this to identify who is accessing their data.

**Step 3: Verify Installation**

1. Check if library is installed:
   ```bash
   python -c "import edgar; print('edgartools installed')"
   ```

2. Check logs after installation:
   - Should see: `Successfully imported edgartools library`
   - Should see: `Set EDGAR identity: your.email@example.com`
   - Should NOT see: `Could not import edgartools library. Using mock implementation.`

3. Re-run ingestion:
   ```bash
   python ingest_edgar_data.py --ticker AAPL
   ```

4. Verify real data:
   - Company name should be "Apple Inc." (not "AAPL Inc.")
   - CIK should be correct (0000320193 for Apple)
   - Filing data should contain actual SEC filing content
   - Logs should show: `Fetched company data for AAPL: Apple Inc.`
   - Logs should show: `Fetched filing data for AAPL 10-K: <accession_number>`

### Current Workaround

If you cannot install an EDGAR tools library immediately:
- Mock data allows testing the ingestion pipeline end-to-end
- Mock data structure matches expected schema format
- You can verify Neo4j schema, embeddings, and graph structure work correctly
- Replace with real data once EDGAR library is installed

### Related Files

- `scripts/utils/edgar_client.py` - Contains the EDGAR client implementation with edgartools integration and mock data fallback
- `scripts/requirements.txt` - Lists edgartools library dependency
- `scripts/logs/ingest_20251228.log` - Contains warnings about mock data usage
- `scripts/README.md` - Setup instructions including EDGAR_IDENTITY configuration

### Additional Notes

The mock implementation generates realistic-looking data structures but with placeholder content. This is intentional to allow testing without requiring external dependencies. However, for production use, you must install and configure a real EDGAR data fetching library.

---

## Debug Logging

### Overview

Debug logging is available for troubleshooting Neo4j client operations. It's disabled by default and can be enabled via environment variable.

### Enabling Debug Logging

Set the `NEO4J_DEBUG_LOGGING` environment variable to enable:

```bash
# In .env file
NEO4J_DEBUG_LOGGING=true

# Or via command line
export NEO4J_DEBUG_LOGGING=true
python setup_schema.py
```

**Accepted values:** `true`, `1`, `yes` (case-insensitive)

### Debug Log Location

When enabled, debug logs are written to:
```
scripts/logs/debug.log
```

### Debug Log Format

Debug logs are written in NDJSON format (one JSON object per line):

```json
{
  "sessionId": "neo4j-client",
  "runId": "attempt-0",
  "location": "neo4j_client.py:execute_write",
  "message": "Session object type check",
  "data": {
    "session_type": "<class 'neo4j._sync.work.session.Session'>",
    "has_commit": false,
    "session_methods": ["close", "run", "last_bookmark", ...]
  },
  "timestamp": 1733456789000
}
```

### What Gets Logged

When debug logging is enabled, the following information is captured:

1. **Session Object Type Check** (before query execution)
   - Session object type
   - Whether session has `commit()` method
   - Available session methods

2. **After Query Execution**
   - Number of records returned
   - Whether commit method exists (for verification)

3. **Transaction Operations**
   - Number of queries in transaction
   - Transaction results count

### Use Cases

Debug logging is useful for:
- Troubleshooting session-related issues
- Verifying transaction behavior
- Understanding Neo4j driver API usage
- Debugging connection problems

### Performance Impact

Debug logging has minimal performance impact when disabled (default). When enabled:
- Small overhead from file I/O operations
- Logs are written asynchronously (non-blocking)
- Errors in logging don't affect main execution

---

## Common Issues

### Neo4j Connection Issues

**Symptoms:**
- Connection timeout errors
- "Failed to connect to Neo4j" messages

**Solutions:**
1. Verify Neo4j is running: `docker ps` or check Neo4j service
2. Check connection URI matches your setup (default: `bolt://localhost:7687`)
3. Verify credentials in `.env` file
4. Test connection: `cypher-shell -u neo4j -p password`

### Schema Creation Issues

**Symptoms:**
- Constraints/indexes fail to create
- "Already exists" errors (non-fatal, can be ignored)

**Solutions:**
1. Ensure Neo4j version supports vector indexes (5.11+)
2. Check user has CREATE INDEX permissions
3. Verify schema design matches Neo4j version capabilities
4. Check logs for specific error messages

### Vector Index Issues

**Symptoms:**
- Vector indexes fail to create
- "Vector index not supported" warnings

**Solutions:**
1. Ensure Neo4j version 5.11+ (vector indexes require newer versions)
2. Check Neo4j plugins are installed (if needed)
3. Verify embedding dimensions match index configuration (default: 1536)
4. Vector indexes may not be supported in older Neo4j versions (will log warning)

### Environment Variable Issues

**Symptoms:**
- Configuration not loading
- Default values being used unexpectedly

**Solutions:**
1. Ensure `.env` file exists in `scripts/` directory
2. Verify `.env` file format (KEY=VALUE, no spaces around `=`)
3. Check environment variables are loaded: `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('NEO4J_URI'))"`
4. Restart script after changing `.env` file

---

## Contributing Troubleshooting Information

When documenting new issues:

1. **Issue Title** - Clear, descriptive title
2. **Error Message** - Exact error text
3. **Symptoms** - What behavior indicates the issue
4. **Root Cause** - Technical explanation
5. **Solution** - Step-by-step fix with code examples
6. **Verification** - How to confirm the fix works
7. **Related Files** - Files affected by the issue/fix

---

## Additional Resources

- [Neo4j Python Driver Documentation](https://neo4j.com/docs/python-manual/current/)
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- Schema Design: `docs/neo4j-edgar-schema-design-v2.md`
- Scripts README: `scripts/README.md`

