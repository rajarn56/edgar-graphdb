# Architecture Documentation

## Overview

The frontend application is built using React with TypeScript, React Flow for graph visualization, and a custom three-panel layout system. The architecture follows a component-based structure with custom hooks for state management.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      App.tsx                             │
│  (State Management & Event Coordination)                 │
└───────────────┬─────────────────────────────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼────────┐      ┌──────▼────────┐
│   Hooks    │      │   Components  │
│            │      │                │
│ useGraph   │      │ AppLayout      │
│ useNode    │      │ GraphCanvas    │
│ usePanel   │      │ NodeDetails    │
│ useFilters │      │ FilterPanel    │
└────────────┘      └────────────────┘
    │                       │
    └───────────┬───────────┘
                │
        ┌───────▼────────┐
        │   Services     │
        │                │
        │ API Client     │
        │ Logger         │
        └────────────────┘
```

## Component Hierarchy

### Layout Components

**AppLayout**
- Root layout component
- Manages three-panel structure
- Uses CSS Grid for space management
- Coordinates panel state

**LeftPanel**
- Filter panel container
- Collapsible with smooth transitions
- Width: 250px (expanded), 0px (collapsed)

**CenterPanel**
- Graph canvas container
- Dynamically adjusts based on side panel states
- Background grid pattern

**RightPanel**
- Node details container
- Collapsible with smooth transitions
- Width: 400px (expanded), 0px (collapsed)
- Properly releases space when closed

**AppHeader**
- Top header with ticker input
- Loading states and error display
- Quick stats display

### Graph Components

**GraphCanvas**
- React Flow wrapper
- Handles node/edge rendering
- Manages graph interactions
- Implements fitView and zoom controls

**CustomNodes**
- CompanyNode: Large, blue, circular
- FilingNode: Medium, amber, rectangular
- SectionNode: Medium, green, rectangular
- ChunkNode: Small, pink, circular
- Hover effects and selection states
- Expand indicators

**CustomEdges**
- Styled edges with labels
- Color-coded by relationship type
- Smooth bezier curves

### Details Components

**NodeDetailsPanel**
- Main container for node details
- Proper scrolling
- Loading and error states

**PropertiesView**
- Organized property display
- Grouped by category (Basic, Dates, Metadata, Other)
- Expandable sections
- Copy-to-clipboard functionality

**ContentView**
- Chunk content display
- Search functionality
- Expand/collapse for long content
- Content statistics
- Proper text formatting

**RelationshipsView**
- Incoming/outgoing relationships
- Clickable relationship items
- Relationship type badges

### Filter Components

**FilterPanel**
- Form type filter
- Fiscal year filter
- Node type checkboxes
- Active filter indicators
- Clear filters button

## State Management

### useGraphData Hook
- Manages graph data state
- Handles graph loading
- Node expansion logic
- Graph data merging

### useNodeSelection Hook
- Selected node state
- Node details fetching
- Loading and error states

### usePanelState Hook
- Panel visibility state
- Collapse/expand logic
- Panel width calculations

### useFilters Hook
- Filter options state
- Filter application logic
- Active filter counting

## Data Flow

1. **User enters ticker** → App.tsx → useGraphData.loadGraph()
2. **Graph data fetched** → API → GraphData → GraphCanvas
3. **User clicks node** → GraphCanvas → App.tsx → useNodeSelection.selectNode()
4. **Node details fetched** → API → NodeDetails → NodeDetailsPanel
5. **User changes filters** → FilterPanel → useFilters → App.tsx → Filtered graph data
6. **User expands node** → GraphCanvas (double-click) → useGraphData.expandNode() → Merged graph data

## API Integration

### Endpoints Used

- `GET /api/graph/{ticker}` - Load graph data
- `GET /api/graph/{ticker}/expand/{node_id}` - Expand node
- `GET /api/graph/node/{node_id}` - Get node details
- `GET /api/ticker/{ticker}/stats` - Get graph statistics

### Error Handling

- All API calls wrapped in try-catch
- Error messages displayed to user
- Errors logged to file
- Retry logic (future enhancement)

## Layout System

### CSS Grid Approach

The layout uses a combination of fixed positioning for side panels and dynamic margins for the center panel:

```css
.app-layout-body {
  display: flex;
  position: relative;
}

.left-panel {
  position: fixed;
  left: 0;
  width: var(--left-width);
}

.center-panel {
  margin-left: var(--left-width);
  margin-right: var(--right-width);
}

.right-panel {
  position: fixed;
  right: 0;
  width: var(--right-width);
}
```

When panels collapse, their width becomes 0, and margins adjust accordingly, properly releasing space.

## Logging System

### Logger Features

- File-based logging using File System Access API
- Fallback to localStorage with download option
- Log levels: debug, info, warn, error
- Component-scoped logging
- Session tracking
- Buffer flushing every 5 seconds

### Log Format

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "info",
  "component": "App",
  "message": "Ticker submitted",
  "data": { "ticker": "AAPL" },
  "sessionId": "session_1234567890_abc123"
}
```

## Performance Considerations

1. **Graph Layout**: Hierarchical layout algorithm for efficient positioning
2. **Filtering**: Memoized filter application to avoid unnecessary recalculations
3. **Node Rendering**: React Flow handles efficient node/edge rendering
4. **Logging**: Buffered logging to prevent performance impact
5. **State Updates**: Optimized state updates to prevent unnecessary re-renders

## Future Enhancements

1. **Virtual Scrolling**: For large graphs with many nodes
2. **Graph Clustering**: Group related nodes
3. **Search Functionality**: Search across all nodes
4. **Export Options**: Export graph as image or data
5. **Dark Mode**: Theme switching
6. **Keyboard Shortcuts**: Power user features
7. **Graph History**: Undo/redo for graph operations

