# Logging Implementation Guide

## Overview

Comprehensive logging has been implemented for both backend and frontend to enable clear understanding of execution flow and facilitate debugging and investigation.

## Backend Logging

### Log Files

Logs are written to `backend/logs/` directory:

1. **`ui_backend_YYYYMMDD.log`**: All application logs (INFO level and above)
2. **`errors_YYYYMMDD.log`**: Error logs only (ERROR level)
3. **`access_YYYYMMDD.log`**: HTTP request/response logs

### Log Format

```
YYYY-MM-DD HH:mm:ss.SSS | LEVEL     | module:function:line | message
```

Example:
```
2025-12-28 10:15:23.456 | INFO     | api.graph:get_graph:45 | Getting graph for ticker: AAPL
```

### What Gets Logged

#### Application Lifecycle
- Application startup/shutdown
- Configuration loading
- Neo4j connection initialization

#### HTTP Requests/Responses
- Request method, path, query parameters
- Client IP address
- Response status code
- Response time (in seconds)
- Error responses with details

#### API Endpoints
- Ticker submissions
- Graph data requests
- Node expansion requests
- Node details requests
- Parameters passed to endpoints

#### Neo4j Queries
- Query execution start
- Cypher queries (full query text)
- Query parameters
- Result counts
- Query execution time
- Errors with stack traces

#### Performance Metrics
- Query execution times
- Endpoint response times
- Data processing times

### Configuration

Set in `backend/.env`:
```env
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
LOG_DIR=logs            # Log directory (relative to backend/)
```

### Log Rotation

- Files rotate at 100MB
- Logs retained for 30 days
- Old logs compressed (zip format)
- Thread-safe logging (enqueue=True)

## Frontend Logging

### Log Storage

Frontend logs are stored in:
1. **Browser Console**: Real-time logging
2. **Browser localStorage**: Persistent storage (last 1000 entries)
3. **Downloadable files**: Can be exported as text files

### Log Format

```json
{
  "timestamp": "2025-12-28T10:15:23.456Z",
  "level": "info",
  "message": "Ticker submitted",
  "data": { "ticker": "AAPL" }
}
```

### What Gets Logged

#### Application Lifecycle
- Application initialization
- Environment configuration
- API base URL

#### User Interactions
- Ticker symbol submission
- Node clicks
- Node expansion requests
- Filter changes

#### API Communication
- All API requests (method, URL, parameters)
- API responses (status, data length)
- API errors (full error details, stack traces)

#### Graph Operations
- Graph data received
- Layout application
- Graph updates after expansion
- Filter application

### Accessing Logs

#### Browser Console
All logs are printed to browser console in real-time.

#### Download Logs
Logs are automatically downloaded every 100 log entries, or manually:

```javascript
// In browser console
import { logger } from './utils/logger';
logger.downloadLogs();
```

#### View Logs Programmatically
```javascript
import { logger } from './utils/logger';
const logs = logger.getLogs();
console.log(logs);
```

### Configuration

Set in `frontend/.env`:
```env
VITE_LOG_LEVEL=info              # debug, info, warn, error
VITE_ENABLE_FILE_LOGGING=true    # Enable localStorage logging
```

## Log Levels

### Backend
- **DEBUG**: Detailed diagnostic information (queries, parameters, intermediate results)
- **INFO**: General informational messages (operations, results, performance)
- **WARNING**: Warning messages (missing data, non-critical issues)
- **ERROR**: Error messages with stack traces

### Frontend
- **debug**: Detailed diagnostic information
- **info**: General informational messages
- **warn**: Warning messages
- **error**: Error messages with stack traces

## Example Log Scenarios

### Scenario 1: User Loads Graph

**Backend Logs:**
```
2025-12-28 10:15:23.456 | INFO | api.graph:get_graph:45 | Getting graph for ticker: AAPL
2025-12-28 10:15:23.789 | DEBUG | services.neo4j_service:get_company_graph:95 | Executing get_company_graph query for ticker: AAPL
2025-12-28 10:15:23.790 | DEBUG | services.neo4j_service:get_company_graph:100 | Query: MATCH (c:Company {ticker: $ticker})...
2025-12-28 10:15:24.123 | DEBUG | services.neo4j_service:get_company_graph:107 | Query returned 5 results in 0.333s
2025-12-28 10:15:24.124 | INFO | services.neo4j_service:get_company_graph:155 | get_company_graph completed for AAPL: 5 nodes, 4 edges in 0.334s
2025-12-28 10:15:24.125 | INFO | api.graph:get_graph:67 | Graph retrieved for ticker AAPL: 5 nodes, 4 edges in 0.669s
```

**Frontend Logs:**
```
[2025-12-28T10:15:23.456Z] INFO: Ticker submitted {"ticker":"AAPL"}
[2025-12-28T10:15:23.789Z] DEBUG: API Request: GET /api/graph/AAPL
[2025-12-28T10:15:24.123Z] DEBUG: API Response: GET /api/graph/AAPL {"status":200,"dataLength":1234}
[2025-12-28T10:15:24.124Z] INFO: Graph data received {"nodeCount":5,"edgeCount":4}
```

### Scenario 2: Error Occurrence

**Backend Logs:**
```
2025-12-28 10:20:15.456 | ERROR | services.neo4j_service:get_company_graph:145 | Error getting graph for ticker INVALID after 0.123s: No data found
Traceback (most recent call last):
  File "services/neo4j_service.py", line 140, in get_company_graph
    ...
```

**Frontend Logs:**
```
[2025-12-28T10:20:15.456Z] ERROR: API Error: GET /api/graph/INVALID {"status":404,"data":{"detail":"No data found for ticker: INVALID"}}
[2025-12-28T10:20:15.457Z] ERROR: Failed to load graph {"ticker":"INVALID","error":"No data found for ticker: INVALID"}
```

## Debugging Tips

1. **Enable DEBUG Logging**: Set `LOG_LEVEL=DEBUG` in backend `.env` for detailed query logs
2. **Check Error Logs**: Always check `errors_*.log` first for error details
3. **Review Access Logs**: Check `access_*.log` for HTTP request/response details
4. **Performance Analysis**: Look for slow queries (check execution times in logs)
5. **Trace User Actions**: Frontend logs show complete user interaction flow
6. **API Debugging**: Both backend and frontend logs show API communication

## Log File Management

### Backend
- Logs automatically rotate at 100MB
- Old logs compressed and retained for 30 days
- Manual cleanup: Delete old log files from `backend/logs/`

### Frontend
- Logs kept in memory (last 1000 entries)
- localStorage storage (limited by browser, ~5-10MB)
- Manual cleanup: `logger.clearLogs()` in browser console

## Best Practices

1. **Production**: Set `LOG_LEVEL=INFO` to reduce log volume
2. **Development**: Use `LOG_LEVEL=DEBUG` for detailed debugging
3. **Investigation**: Check both backend and frontend logs for complete picture
4. **Performance**: Monitor query execution times in logs
5. **Errors**: Always check error logs first, then trace back through info logs

## Troubleshooting Logging Issues

### Backend Logs Not Created
- Check `backend/logs/` directory exists and is writable
- Verify `LOG_DIR` environment variable
- Check file permissions

### Frontend Logs Not Working
- Check browser console for errors
- Verify localStorage is available (not in private/incognito mode)
- Check `VITE_ENABLE_FILE_LOGGING` is set

### Logs Too Verbose
- Increase log level (INFO instead of DEBUG)
- Check log rotation settings
- Clean up old log files

### Missing Log Information
- Enable DEBUG level logging
- Check that logging is initialized properly
- Verify logger is imported correctly

