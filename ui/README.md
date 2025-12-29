# Neo4j EDGAR Graph Visualization UI

A web-based UI application for visualizing and exploring Neo4j EDGAR graph database data. Built with React Flow for interactive graph visualization and FastAPI for the backend API.

## Overview

This application allows users to:
- Enter a ticker symbol to visualize the complete graph structure
- Explore nodes (Company, Filing, Section, Chunk) and their relationships
- View detailed properties of nodes in a side panel
- Expand nodes progressively to load related data
- Filter graph by form type, fiscal year, and node types
- View chunk content in an expandable viewer

## Architecture

The application consists of two main components:

1. **Backend (FastAPI)**: REST API server that queries Neo4j database
2. **Frontend (React + React Flow)**: Interactive graph visualization UI

```
ui/
├── backend/          # FastAPI backend
│   ├── app.py       # Main application
│   ├── api/         # API routes
│   ├── services/    # Business logic (Neo4j queries)
│   └── models/      # Pydantic models
└── frontend/        # React application
    └── src/
        ├── components/  # React components
        ├── services/    # API client
        ├── types/       # TypeScript types
        └── utils/       # Utility functions
```

## Prerequisites

- **Python 3.12+** (for backend)
- **Node.js 18+** (for frontend)
- **Neo4j** running locally on `bolt://localhost:7687`
- **Neo4j credentials** configured (same as scripts folder)

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd ui/backend
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Copy `.env.example` to `.env` (if it exists) or create `.env` file
   - Set the following variables:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
BACKEND_PORT=8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd ui/frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start Backend

1. Activate virtual environment (if using one):
```bash
cd ui/backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Start the FastAPI server:
```bash
uvicorn app:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Start Frontend

1. In a new terminal, navigate to frontend directory:
```bash
cd ui/frontend
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage Guide

### Basic Usage

1. **Enter Ticker Symbol**: Type a ticker symbol (e.g., AAPL) in the input field and click "Load Graph"
2. **View Graph**: The graph will display Company node connected to Filing nodes
3. **Click Nodes**: Click any node to view its detailed properties in the right panel
4. **Expand Nodes**: Double-click Filing nodes to expand and load Sections (future enhancement)
5. **Filter Graph**: Use the left filter panel to filter by form type, fiscal year, or node types

### Graph Visualization Features

- **Node Types**:
  - **Company** (Blue circle): Company information
  - **Filing** (Yellow rectangle): SEC filings (10-K, 10-Q, etc.)
  - **Section** (Green rectangle): Filing sections (Item 7, Item 1A, etc.)
  - **Chunk** (Pink circle): Content chunks with embeddings

- **Interactions**:
  - **Drag nodes**: Click and drag nodes to reposition them
  - **Zoom**: Use mouse wheel or controls to zoom in/out
  - **Pan**: Click and drag canvas background to pan
  - **Node details**: Click any node to view properties

### Node Details Panel

The right panel shows:
- **Node Type**: Labels and type information
- **Properties**: Grouped by category (Basic, Dates, Metadata, Other)
- **Content**: For Chunk nodes, shows full content (expandable if long)
- **Relationships**: List of incoming and outgoing relationships

### Filter Panel

The left panel provides filters:
- **Form Type**: Filter by form type (10-K, 10-Q, 8-K, etc.)
- **Fiscal Year**: Filter by fiscal year
- **Node Types**: Show/hide specific node types

## API Endpoints

### Graph Endpoints

- `GET /api/graph/{ticker}` - Get graph data for a ticker
- `GET /api/graph/{ticker}/expand/{node_id}?node_type={type}` - Expand a node
- `GET /api/graph/node/{node_id}?labels={labels}` - Get node details
- `GET /api/graph/node/{node_id}/relationships?labels={labels}` - Get node relationships

### Ticker Endpoints

- `GET /api/ticker/{ticker}/info` - Get company information
- `GET /api/ticker/{ticker}/filings?form_type={type}` - Get filings list
- `GET /api/ticker/{ticker}/stats` - Get graph statistics

See `http://localhost:8000/docs` for interactive API documentation.

## Logging

The application includes comprehensive logging for debugging and investigation.

### Backend Logging

Backend logs are written to files in `backend/logs/` directory:

- **`ui_backend_YYYYMMDD.log`**: All logs (INFO level and above)
- **`errors_YYYYMMDD.log`**: Error logs only
- **`access_YYYYMMDD.log`**: HTTP request/response logs

**Log Format:**
```
YYYY-MM-DD HH:mm:ss.SSS | LEVEL     | module:function:line | message
```

**What is Logged:**
- Application startup/shutdown
- All HTTP requests (method, path, query params, client IP)
- HTTP responses (status code, response time)
- API endpoint calls (ticker, node_id, parameters)
- Neo4j query execution (queries, parameters, results, timing)
- Errors with full stack traces
- Performance metrics (query execution times)

**Configuration:**
Set environment variables in `.env`:
```env
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
LOG_DIR=logs            # Log directory (relative to backend/)
```

**Example Log Entries:**
```
2025-12-28 10:15:23.456 | INFO     | api.graph:get_graph:45 | Getting graph for ticker: AAPL
2025-12-28 10:15:23.789 | DEBUG    | services.neo4j_service:get_company_graph:95 | Query: MATCH (c:Company {ticker: $ticker})...
2025-12-28 10:15:24.123 | INFO     | services.neo4j_service:get_company_graph:145 | get_company_graph completed for AAPL: 5 nodes, 4 edges in 0.334s
2025-12-28 10:15:24.124 | INFO     | api.graph:get_graph:67 | Graph retrieved for ticker AAPL: 5 nodes, 4 edges in 0.668s
```

### Frontend Logging

Frontend logs are stored in browser localStorage and can be downloaded.

**What is Logged:**
- Application initialization
- API requests (method, URL, parameters)
- API responses (status, data length)
- API errors (full error details)
- User interactions (ticker submission, node clicks, node expansion)
- Filter changes
- Graph updates

**Accessing Logs:**

1. **Browser Console**: All logs are printed to browser console
2. **Download Logs**: Logs are automatically downloaded every 100 log entries, or manually:
   ```javascript
   // In browser console
   import { logger } from './utils/logger';
   logger.downloadLogs();
   ```

**Configuration:**
Set environment variables in `.env` (frontend):
```env
VITE_LOG_LEVEL=info        # debug, info, warn, error
VITE_ENABLE_FILE_LOGGING=true  # Enable localStorage logging
```

**Example Log Entries:**
```
[2025-12-28T10:15:23.456Z] INFO: Ticker submitted {"ticker":"AAPL"}
[2025-12-28T10:15:23.789Z] DEBUG: API Request: GET /api/graph/AAPL
[2025-12-28T10:15:24.123Z] INFO: Graph data received {"nodeCount":5,"edgeCount":4}
```

### Log Analysis Tips

1. **Performance Issues**: Look for slow queries in backend logs (check execution times)
2. **API Errors**: Check both backend error logs and frontend console for API failures
3. **Missing Data**: Check Neo4j query logs to see what data was returned
4. **User Actions**: Frontend logs show user interactions and what data was requested
5. **Request Flow**: Access logs show complete request/response cycle with timing

### Log File Locations

- **Backend**: `ui/backend/logs/`
- **Frontend**: Browser localStorage (downloadable) + browser console

### Log Rotation

- Backend logs rotate at 100MB
- Logs are retained for 30 days
- Old logs are compressed (zip)
- Frontend logs keep last 1000 entries in memory

## Troubleshooting

### Backend Issues

**Connection Error to Neo4j**
- Verify Neo4j is running: `docker ps` or check Neo4j service
- Check connection URI matches your setup (default: `bolt://localhost:7687`)
- Verify credentials in `.env` file
- Test connection: `cypher-shell -u neo4j -p password`

**Import Errors**
- Ensure `scripts/utils/neo4j_client.py` exists (used by backend)
- Check Python path includes scripts directory
- Verify all dependencies installed: `pip install -r requirements.txt`

**Port Already in Use**
- Change `BACKEND_PORT` in `.env` or use different port: `uvicorn app:app --port 8001`

### Frontend Issues

**Cannot Connect to Backend**
- Verify backend is running on `http://localhost:8000`
- Check browser console for CORS errors
- Verify `VITE_API_BASE_URL` in `.env` (if set) matches backend URL
- Check Vite proxy configuration in `vite.config.ts`

**Graph Not Loading**
- Check browser console for errors
- Verify ticker symbol exists in Neo4j database
- Check backend logs for query errors
- Ensure data was ingested using scripts in `scripts/` folder

**Node Details Not Showing**
- Check browser console for API errors
- Verify node ID format matches Neo4j schema
- Check backend logs for query execution

### Common Issues

**No Data for Ticker**
- Ensure data was ingested: `python scripts/ingest_edgar_data.py --ticker AAPL`
- Verify ticker symbol is uppercase
- Check Neo4j database has data: `MATCH (c:Company) RETURN c LIMIT 5`

**Graph Layout Issues**
- Refresh page to recalculate layout
- Clear browser cache
- Check for console errors

**Performance Issues**
- Large graphs may take time to load
- Consider filtering by form type or fiscal year
- Check Neo4j query performance
- Review backend logs for slow queries (check execution times)
- Check frontend logs for API call timing

**Debugging with Logs**
- Enable DEBUG logging: Set `LOG_LEVEL=DEBUG` in backend `.env`
- Check `backend/logs/errors_*.log` for error details
- Check `backend/logs/access_*.log` for HTTP request/response details
- Review frontend browser console for client-side errors
- Download frontend logs for detailed investigation

## Development

### Backend Development

- Backend uses FastAPI with auto-reload enabled
- API changes are reflected immediately
- Check `http://localhost:8000/docs` for API documentation
- Logs are printed to console

### Frontend Development

- Frontend uses Vite with hot module replacement
- Changes are reflected immediately in browser
- TypeScript errors shown in console
- React Flow documentation: https://reactflow.dev

### Adding New Features

1. **Backend**: Add new endpoints in `backend/api/` and service methods in `backend/services/`
2. **Frontend**: Add new components in `frontend/src/components/` and update `App.tsx`
3. **Types**: Update TypeScript types in `frontend/src/types/graph.ts` and Pydantic models in `backend/models/`

## Project Structure

```
ui/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── api/
│   │   ├── graph.py          # Graph API endpoints
│   │   └── ticker.py         # Ticker API endpoints
│   ├── services/
│   │   └── neo4j_service.py  # Neo4j query service
│   ├── models/
│   │   └── graph.py          # Pydantic models
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── GraphCanvas.tsx    # React Flow canvas
│   │   │   ├── NodeTypes.tsx      # Custom node components
│   │   │   ├── NodeDetails.tsx    # Node details panel
│   │   │   ├── TickerInput.tsx    # Ticker input form
│   │   │   └── FilterPanel.tsx   # Filter panel
│   │   ├── services/
│   │   │   └── api.ts            # API client
│   │   ├── types/
│   │   │   └── graph.ts           # TypeScript types
│   │   ├── utils/
│   │   │   └── graphLayout.ts     # Layout algorithms
│   │   ├── App.tsx               # Main app component
│   │   └── main.tsx              # Entry point
│   ├── package.json              # Node dependencies
│   └── vite.config.ts            # Vite configuration
└── README.md                     # This file
```

## Dependencies

### Backend
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `neo4j`: Neo4j Python driver
- `pydantic`: Data validation
- `python-dotenv`: Environment variables

### Frontend
- `react`: UI library
- `reactflow`: Graph visualization
- `axios`: HTTP client
- `typescript`: Type safety
- `vite`: Build tool

## License

See parent directory LICENSE file.

## Support

For issues or questions:
- Check troubleshooting section above
- Review Neo4j schema documentation in `docs/`
- Check scripts README: `scripts/README.md`
- Review API documentation at `http://localhost:8000/docs`

## Future Enhancements

- [ ] Double-click to expand nodes
- [ ] Search functionality
- [ ] Export graph as image
- [ ] Save/load graph views
- [ ] Advanced filtering options
- [ ] Relationship path visualization
- [ ] Vector similarity search UI
- [ ] Timeline view for filings

