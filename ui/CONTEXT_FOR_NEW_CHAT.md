# Context for New Chat - EDGAR Graph UI Debugging

> **⚠️ IMPORTANT**: For detailed debugging context on the current right panel issue, see `DEBUGGING_CONTEXT.md`

## Project Overview
Building a graph visualization UI for EDGAR financial data using React Flow. The graph shows Company → Filings → Sections → Chunks relationships.

## Current Issues

### 🔴 **CRITICAL: Right Panel Not Showing** (Active Issue)
- **Status**: API calls work, but panel doesn't appear
- **Evidence**: Backend logs show successful API calls when nodes clicked
- **See**: `DEBUGGING_CONTEXT.md` for full investigation details

### 1. **Edge Visibility Issue**
- **Problem**: Edges/connectors don't show up until zooming in
- **Status**: Partially addressed - increased opacity and added explicit styling, but may still need investigation
- **Files Modified**: 
  - `frontend/src/components/graph/GraphCanvas.tsx` - Added edge styling with opacity: 1
  - `frontend/src/components/graph/CustomEdges.tsx` - Increased opacity to 1

### 2. **Right Panel Not Showing**
- **Problem**: When nodes are clicked, right panel with properties doesn't appear
- **Status**: Partially addressed - fixed panel state management, but may still have issues
- **Files Modified**:
  - `frontend/src/hooks/usePanelState.ts` - Fixed width calculation and initial state
  - `frontend/src/components/layout/AppLayout.css` - Added transform handling
  - `frontend/src/App.tsx` - Enhanced node click handler

### 3. **Complete Graph Loading**
- **Status**: ✅ FIXED - Backend now loads complete graph (Company → Filings → Sections → Chunks) in one query
- **Files Modified**:
  - `backend/services/neo4j_service.py` - Added `get_complete_graph()` method
  - `backend/api/graph.py` - Updated endpoint to use complete graph

## Recent Changes Made

### Backend Changes
1. **Complete Graph Loading** (`backend/services/neo4j_service.py`):
   - Added `get_complete_graph()` method that loads all levels in one query
   - Returns Company + Filings + Sections + Chunks with all edges

2. **API Endpoint** (`backend/api/graph.py`):
   - `/api/graph/{ticker}` now uses `get_complete_graph()` instead of `get_company_graph()`

### Frontend Changes

1. **Graph Canvas** (`frontend/src/components/graph/GraphCanvas.tsx`):
   - Added comprehensive logging for edge creation and rendering
   - Increased edge opacity to 1.0 for better visibility
   - Added explicit edge styling (strokeWidth: 3, opacity: 1)
   - Added arrow markers to edges
   - Reduced minZoom from 0.1 to 0.05
   - Added edge configuration options

2. **Panel State Management** (`frontend/src/hooks/usePanelState.ts`):
   - Fixed `getRightPanelWidth()` to only check `collapsed` status
   - Changed initial right panel state to `visible: true` (but `collapsed: true`)
   - Added logging for width calculations and state changes

3. **Node Selection** (`frontend/src/hooks/useNodeSelection.ts`):
   - Enhanced to accept optional `graphNode` parameter
   - Uses graph node properties as immediate fallback
   - Merges properties from graph node and API response
   - Added comprehensive logging

4. **App Component** (`frontend/src/App.tsx`):
   - Updated `handleNodeClick()` to find and pass graph node
   - Added logging for node click flow

5. **Right Panel** (`frontend/src/components/layout/RightPanel.tsx`):
   - Added logging for state changes

6. **App Layout** (`frontend/src/components/layout/AppLayout.tsx`):
   - Added logging for layout state
   - Fixed missing logger import (was causing breaking error)

7. **Custom Edges** (`frontend/src/components/graph/CustomEdges.tsx`):
   - Increased opacity to 1
   - Added logging for edge rendering (first few edges only)

## Key Files and Locations

### Backend
- `Research/edgar-graphdb/ui/backend/services/neo4j_service.py` - Graph data service
- `Research/edgar-graphdb/ui/backend/api/graph.py` - Graph API endpoints
- `Research/edgar-graphdb/ui/backend/logs/` - Backend logs

### Frontend
- `Research/edgar-graphdb/ui/frontend/src/App.tsx` - Main app component
- `Research/edgar-graphdb/ui/frontend/src/components/graph/GraphCanvas.tsx` - React Flow canvas
- `Research/edgar-graphdb/ui/frontend/src/components/graph/CustomEdges.tsx` - Edge rendering
- `Research/edgar-graphdb/ui/frontend/src/components/graph/CustomNodes.tsx` - Node rendering
- `Research/edgar-graphdb/ui/frontend/src/components/layout/AppLayout.tsx` - Layout component
- `Research/edgar-graphdb/ui/frontend/src/components/layout/RightPanel.tsx` - Right panel component
- `Research/edgar-graphdb/ui/frontend/src/components/details/NodeDetailsPanel.tsx` - Node details display
- `Research/edgar-graphdb/ui/frontend/src/hooks/usePanelState.ts` - Panel state management
- `Research/edgar-graphdb/ui/frontend/src/hooks/useNodeSelection.ts` - Node selection logic
- `Research/edgar-graphdb/ui/frontend/src/hooks/useGraphData.ts` - Graph data management

## Logging Added

Comprehensive logging has been added throughout to help debug:
- Edge creation and rendering
- Node click events
- Panel state changes
- Width calculations
- Node selection flow
- API calls and responses

**Check browser console (F12 → Console) for logs**

## Current State

### What Works
- ✅ Complete graph loads with all levels (Company → Filings → Sections → Chunks)
- ✅ All nodes display correctly
- ✅ Backend API is working (check logs in `backend/logs/`)
- ✅ Logging is in place for debugging

### What Needs Investigation
1. **Edge Visibility**: Edges may not be visible at certain zoom levels
   - Check React Flow edge rendering
   - Verify edge styles are applied correctly
   - Check if edges are being filtered out

2. **Right Panel**: May not be showing when nodes are clicked
   - Check panel width calculation
   - Verify CSS transforms
   - Check if panel content is rendering
   - Verify node details are being fetched

## Debugging Steps

1. **Check Browser Console**:
   - Look for errors
   - Check logging output for:
     - "React Flow edges created" - confirms edges are created
     - "Node clicked in GraphCanvas" - confirms clicks work
     - "Right panel expanded" - confirms panel expansion
     - "Right panel width calculated" - shows width calculation

2. **Check Network Tab**:
   - Verify API calls are successful
   - Check `/api/graph/{ticker}` returns complete graph
   - Check `/api/graph/node/{nodeId}` returns node details

3. **Check React DevTools**:
   - Inspect component state
   - Check if edges are in React Flow state
   - Verify panel state values

4. **Visual Inspection**:
   - Check if edges appear when zooming in
   - Check if right panel appears (even if empty)
   - Check browser console for errors

## Reference Images
- `Research/debug/jsonsea-ref1.png` - Reference for how graph should look
- `Research/edgar-graphdb/ui/debug/LoadConsoleError.png` - Error screenshot (if available)

## Next Steps for Debugging

1. **For Edge Visibility**:
   - Check React Flow documentation for edge visibility at different zoom levels
   - Verify edge styles are not being overridden
   - Check if there's a minimum zoom threshold for edges
   - Consider adding edge visibility toggle or force rendering

2. **For Right Panel**:
   - Verify panel is actually rendering (check DOM)
   - Check CSS transforms are working
   - Verify panel width is > 0 when expanded
   - Check if content is being passed to panel
   - Verify node details API is returning data

3. **General**:
   - Review browser console logs
   - Check for React errors
   - Verify all imports are correct
   - Check for TypeScript errors

## Important Notes

- The logger import was missing in `AppLayout.tsx` - this was fixed and caused a breaking error
- All logging uses the logger utility from `frontend/src/utils/logger.ts`
- Panel state starts with `visible: true` but `collapsed: true` to allow content rendering
- Graph node properties are used as fallback if API call fails

## API Endpoints

- `GET /api/graph/{ticker}` - Get complete graph (all levels)
- `GET /api/graph/node/{nodeId}?labels=...` - Get node details
- `GET /api/ticker/{ticker}/stats` - Get graph statistics

## Environment

- Frontend: React + TypeScript + Vite + React Flow
- Backend: FastAPI + Neo4j
- Logs: Browser console (frontend), `backend/logs/` (backend)

