# Troubleshooting Guide

This document collects troubleshooting information, fixes, and debugging techniques for the EDGAR Graph Database scripts.

## Table of Contents

1. [Neo4j Session Commit Error](#neo4j-session-commit-error)
2. [Debug Logging](#debug-logging)
3. [Common Issues](#common-issues)

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

