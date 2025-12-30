# EDGAR Graph Visualization UI - Frontend

A modern React-based frontend application for visualizing and exploring Neo4j EDGAR graph database data. Built with React Flow for interactive graph visualization.

## Overview

This frontend application provides an elegant three-panel interface for exploring graph data:
- **Left Panel**: Filter controls for form type, fiscal year, and node types
- **Center Panel**: Interactive graph visualization using React Flow
- **Right Panel**: Detailed node information including properties and chunk content

## Features

- **Interactive Graph Visualization**: Drag, zoom, and pan through graph nodes
- **Node Expansion**: Double-click nodes to expand and load related data
- **Node Details**: Click nodes to view detailed properties and relationships
- **Chunk Content Display**: Full content viewer for chunk nodes with search functionality
- **Filtering**: Filter by form type, fiscal year, and node types
- **Collapsible Panels**: Side panels can be collapsed to maximize graph view
- **Comprehensive Logging**: File-based logging for debugging and investigation

## Prerequisites

- **Node.js 18+** and npm
- **Backend API** running on `http://localhost:8000` (configurable)

## Installation

1. Navigate to the frontend directory:
```bash
cd ui/frontend
```

2. Install dependencies:
```bash
npm install
```

## Configuration

Create a `.env` file in the frontend directory (optional):

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_LOG_LEVEL=info
VITE_ENABLE_FILE_LOGGING=true
```

### Environment Variables

- `VITE_API_BASE_URL`: Backend API base URL (default: `http://localhost:8000`)
- `VITE_LOG_LEVEL`: Logging level - `debug`, `info`, `warn`, `error` (default: `info`)
- `VITE_ENABLE_FILE_LOGGING`: Enable file-based logging (default: `true` in development)

## Running the Application

### Development Mode

```bash
npm run dev
```

The application will be available at `http://localhost:5173` (or the next available port).

### Production Build

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Usage

1. **Load a Graph**: Enter a ticker symbol (e.g., `AAPL`) in the header and click "Load Graph"
2. **Explore Nodes**: Click on nodes to view their details in the right panel
3. **Expand Nodes**: Double-click Filing or Section nodes to load their children
4. **Filter Graph**: Use the left panel to filter by form type, fiscal year, or node types
5. **View Chunk Content**: Click on Chunk nodes to see their full content in the right panel
6. **Collapse Panels**: Click the toggle buttons to collapse side panels for more graph space

## Project Structure

```
src/
├── App.tsx                    # Main application component
├── components/
│   ├── layout/               # Layout components (AppLayout, LeftPanel, RightPanel, CenterPanel)
│   ├── graph/                # Graph visualization (GraphCanvas, CustomNodes, CustomEdges)
│   ├── details/              # Node details (NodeDetailsPanel, PropertiesView, ContentView, RelationshipsView)
│   ├── filters/              # Filter panel
│   ├── header/               # App header with ticker input
│   └── common/                # Common components (LoadingSpinner, ErrorMessage, EmptyState)
├── hooks/                     # Custom React hooks
│   ├── useGraphData.ts       # Graph data management
│   ├── useNodeSelection.ts   # Node selection state
│   ├── usePanelState.ts      # Panel visibility state
│   └── useFilters.ts         # Filter state management
├── services/
│   ├── api.ts                # API client
│   └── logger.ts             # Logging utility
├── types/
│   ├── graph.ts              # Graph data types
│   └── ui.ts                 # UI state types
└── utils/
    ├── graphLayout.ts        # Graph layout algorithms
    ├── formatters.ts         # Data formatting utilities
    └── logger.ts             # Logging utility
```

## Key Components

### AppLayout
Three-panel layout using CSS Grid for proper space management. Panels properly release space when collapsed.

### GraphCanvas
React Flow wrapper with custom nodes and edges. Handles node clicks, double-clicks for expansion, and graph interactions.

### NodeDetailsPanel
Displays node properties, relationships, and chunk content. Properly handles scrolling and content display.

### ContentView
Critical component for displaying chunk content. Includes search functionality, expand/collapse, and proper formatting.

### FilterPanel
Enhanced filter panel with visual feedback and active filter indicators.

## Logging

The application includes comprehensive file-based logging:

- **Log Levels**: `debug`, `info`, `warn`, `error`
- **Log Location**: Browser localStorage (with download option)
- **Log Format**: JSON Lines (JSONL) format
- **Download Logs**: Use browser console: `logger.downloadLogs()`

Logs include:
- User interactions (node clicks, filter changes, etc.)
- API calls and responses
- State changes
- Errors with stack traces
- Performance metrics

## Troubleshooting

### Graph Not Loading
- Check that the backend API is running
- Verify `VITE_API_BASE_URL` is correct
- Check browser console for errors
- Review logs using `logger.downloadLogs()`

### Chunk Content Not Displaying
- Ensure chunk nodes have `content` property
- Check browser console for errors
- Verify node details API is returning content
- Check logs for API response details

### Panels Not Collapsing Properly
- Clear browser cache
- Check browser console for errors
- Verify CSS is loading correctly

### Performance Issues
- Reduce number of visible nodes using filters
- Check browser performance tab
- Review logs for slow API calls

## Development

### Adding New Node Types
1. Update `types/graph.ts` with new node type
2. Add node component in `components/graph/CustomNodes.tsx`
3. Update node type mapping in `GraphCanvas.tsx`
4. Add styling in `CustomNodes.css`

### Adding New Filters
1. Update `types/ui.ts` FilterOptions interface
2. Add filter UI in `components/filters/FilterPanel.tsx`
3. Update filter logic in `hooks/useFilters.ts`
4. Apply filters in `App.tsx`

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

See parent directory for license information.

