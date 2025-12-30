# Architecture Documentation - EDGAR Graph UI

## Overview

The EDGAR Graph UI is a modern React application built with TypeScript, React Flow for graph visualization, and a custom three-panel layout system. The application visualizes EDGAR filing data as a hierarchical graph (Company → Filing → Section → Chunk) with interactive features for exploration and analysis.

## Technology Stack

- **React 18+** with TypeScript
- **React Flow** for graph visualization and interaction
- **Vite** for build tooling and development server
- **CSS Grid/Flexbox** for responsive layout
- **Custom hooks** for state management
- **File System Access API** for logging (with localStorage fallback)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          App.tsx                                 │
│  (Root Component - State Coordination & Event Handling)        │
│  - Graph data management                                         │
│  - Node selection coordination                                   │
│  - Panel state management                                        │
│  - Filter application                                            │
└───────────────┬─────────────────────────────────────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼────────┐      ┌──────▼────────┐
│   Hooks   │      │  Components   │
│           │      │                │
│ useGraph  │      │ AppLayout      │
│ Data      │      │ GraphCanvas    │
│ useNode   │      │ NodeDetails    │
│ Selection │      │ FilterPanel    │
│ usePanel  │      │ AppHeader      │
│ State     │      │ RightPanel     │
│ useFilters│      │ LeftPanel      │
└───────────┘      └────────────────┘
    │                       │
    └───────────┬───────────┘
                │
        ┌───────▼────────┐
        │   Services     │
        │                │
        │ API Client     │
        │ Logger         │
        │ Graph Layout   │
        └────────────────┘
```

## Component Hierarchy

### Root Component

**App.tsx**
- Main application component
- Coordinates all state management hooks
- Handles user interactions (ticker submission, node clicks, panel close)
- Manages filtered graph data computation
- Integrates all sub-components

### Layout Components

**AppLayout**
- Three-panel layout container (Left, Center, Right)
- Uses CSS Grid for space management
- Dynamically adjusts center panel margins based on side panel widths
- Manages panel state coordination
- Props: `panelState`, `onRightPanelClose`, content slots for each panel

**LeftPanel**
- Filter panel container
- Collapsible with smooth CSS transitions
- Width: 250px (expanded), 0px (collapsed)
- Contains FilterPanel component

**CenterPanel**
- Graph canvas container
- Dynamically adjusts margins based on side panel states
- Background grid pattern for visual reference
- Contains GraphCanvas component

**RightPanel**
- Node details container
- Collapsible with smooth CSS transitions
- Width: 400px (expanded), 0px (collapsed)
- Properly releases space when closed
- Contains NodeDetailsPanel component

**AppHeader**
- Top header bar with ticker input
- Loading states and error display
- Graph statistics display (filings, sections, chunks count)
- Reset button functionality
- Form submission handling

### Graph Components

**GraphCanvas**
- React Flow wrapper and configuration
- Manages React Flow node/edge state
- Handles node/edge rendering and interactions
- Implements position preservation for dragged nodes
- Syncs dragged positions back to graph data
- Fit view and zoom controls
- Prevents position reset on expand/collapse
- Props: `nodes`, `edges`, `onNodeClick`, `onNodeDoubleClick`, `onNodeExpandCollapse`, `expandedNodes`, `fitViewOnChange`, `onNodePositionsChange`

**CustomNodes**
- Custom node components for different node types:
  - **CompanyNode**: Large, blue, circular
  - **FilingNode**: Medium, amber, rectangular
  - **SectionNode**: Medium, green, rectangular
  - **ChunkNode**: Small, pink, circular
- Hover effects and selection states
- Expand/collapse indicators
- Click and double-click handlers

**CustomEdges**
- Styled edges with relationship type labels
- Color-coded by relationship type
- Smooth bezier curves
- Arrow markers

### Details Components

**NodeDetailsPanel**
- Main container for node details display
- Proper scrolling implementation
- Loading and error states
- Empty state handling
- Props: `nodeDetails`, `loading`, `error`, `onClose`

**PropertiesView**
- Organized property display
- Grouped by category (Basic, Dates, Metadata, Other)
- Expandable sections
- Copy-to-clipboard functionality
- Empty state handling

**ContentView**
- Chunk content display (for Chunk nodes)
- Search functionality
- Expand/collapse for long content
- Content statistics
- Proper text formatting

**RelationshipsView**
- Incoming/outgoing relationships display
- Relationship type badges
- Empty state handling
- Proper formatting

### Filter Components

**FilterPanel**
- Form type filter dropdown
- Fiscal year filter dropdown
- Node type checkboxes (Company, Filing, Section, Chunk)
- Active filter indicators
- Clear filters button
- Props: `filters`, `onFilterChange`, `availableFormTypes`, `availableYears`, `activeFilterCount`

## State Management

### useGraphData Hook

**Purpose**: Manages graph data state and API calls

**State**:
- `graphData`: Current graph data (nodes and edges)
- `loading`: Loading state
- `error`: Error message
- `ticker`: Current ticker symbol
- `expandedNodes`: Set of expanded node IDs

**Methods**:
- `loadGraph(ticker)`: Loads initial graph data for a ticker
- `expandNode(nodeId, nodeType, ticker)`: Expands a node via API and positions children near parent
- `collapseNode(nodeId)`: Removes node from expanded set
- `toggleNodeExpansion(nodeId)`: Toggles UI expansion state
- `addToGraph(newData)`: Merges new data into existing graph
- `resetGraph()`: Resets all graph data
- `updateNodePositions(positions)`: Updates node positions from React Flow drags

**Key Features**:
- Positions child nodes relative to parent when expanding (300px horizontal spacing, 250px vertical offset)
- Preserves manually positioned nodes through expand/collapse cycles
- Merges new nodes/edges without duplicates
- Maintains graph data reference for efficient updates

### useNodeSelection Hook

**Purpose**: Manages node selection and details fetching

**State**:
- `selectedNodeId`: Currently selected node ID
- `nodeDetails`: Node details data
- `loading`: Loading state for details
- `error`: Error message

**Methods**:
- `selectNode(nodeId, labels, graphNode)`: Selects a node and fetches details
- `clearSelection()`: Clears current selection

**Key Features**:
- Uses graph node properties as initial details (optimistic update)
- Fetches detailed node information from API
- Handles loading and error states
- Provides fallback to graph node properties if API fails

### usePanelState Hook

**Purpose**: Manages panel visibility and collapse states

**State**:
- `leftPanelState`: Left panel state (visible, collapsed, expandedWidth)
- `rightPanelState`: Right panel state (visible, collapsed, expandedWidth)

**Methods**:
- `toggleLeftPanel()`: Toggles left panel collapse state
- `toggleRightPanel()`: Toggles right panel collapse state
- `collapseLeftPanel()`: Collapses left panel
- `expandLeftPanel()`: Expands left panel
- `collapseRightPanel()`: Collapses right panel
- `expandRightPanel()`: Expands right panel
- `getLeftPanelWidth()`: Returns current left panel width
- `getRightPanelWidth()`: Returns current right panel width
- `resetPanels()`: Resets all panels to default state

**Key Features**:
- Prevents duplicate panel state instances
- Manages panel visibility and collapse separately
- Provides width calculations for layout

### useFilters Hook

**Purpose**: Manages filter state and application

**State**:
- `filters`: Filter options (nodeTypes, formType, fiscalYear)

**Methods**:
- `setFilters(newFilters)`: Updates filter options
- `applyFilters(nodes, edges)`: Applies filters to graph data
- `clearFilters()`: Resets filters to default
- `getActiveFilterCount()`: Returns count of active filters

**Key Features**:
- Filters by node types (checkboxes)
- Filters by form type (dropdown)
- Filters by fiscal year (dropdown)
- Maintains filter state across graph updates

## Data Flow

### Graph Loading Flow

1. **User enters ticker** → `AppHeader` → `handleTickerSubmit()` in `App.tsx`
2. **Graph data fetched** → `useGraphData.loadGraph()` → API call → `GET /api/graph/{ticker}`
3. **Layout applied** → `applyLayout()` → Hierarchical layout calculation
4. **Graph displayed** → `GraphCanvas` → React Flow renders nodes/edges

### Node Selection Flow

1. **User clicks node** → `GraphCanvas` → `onNodeClick` → `handleNodeClick()` in `App.tsx`
2. **Panel expanded** → `panelState.expandRightPanel()` → Right panel opens
3. **Node selected** → `nodeSelection.selectNode()` → API call → `GET /api/graph/node/{node_id}`
4. **Details displayed** → `NodeDetailsPanel` → Shows node properties and relationships

### Node Expansion Flow

1. **User double-clicks node** → `GraphCanvas` → `onNodeDoubleClick` → `handleNodeDoubleClick()` in `App.tsx`
2. **API expansion** → `useGraphData.expandNode()` → API call → `GET /api/graph/{ticker}/expand/{node_id}`
3. **Children positioned** → Positions calculated relative to parent (300px spacing, 250px offset)
4. **Layout applied** → `applyLayout()` → Preserves manually positioned nodes
5. **Graph updated** → New nodes/edges merged into graph data
6. **UI expansion** → Node added to `expandedNodes` set → Children become visible

### Node Collapse/Expand (UI) Flow

1. **User clicks expand/collapse button** → `CustomNode` → `onExpandCollapse` → `handleNodeExpandCollapse()` in `App.tsx`
2. **Toggle expansion** → `useGraphData.toggleNodeExpansion()` → Updates `expandedNodes` set
3. **Filtering applied** → `filterNodesByExpandedState()` → Filters visible nodes
4. **Graph updated** → `GraphCanvas` → React Flow updates visible nodes (preserves positions)

### Position Preservation Flow

1. **User drags node** → `GraphCanvas` → React Flow updates node position
2. **Position change detected** → `useEffect` in `GraphCanvas` → Detects position changes > 1px
3. **Positions synced** → `onNodePositionsChange()` → `graphData.updateNodePositions()` → Updates graph data
4. **Positions preserved** → On expand/collapse, positions maintained from graph data

### Reset Flow

1. **User clicks reset** → `AppHeader` → `handleReset()` → `onTickerSubmit('')`
2. **Reset handled** → `handleTickerSubmit()` in `App.tsx` → Detects empty ticker
3. **Graph reset** → `graphData.resetGraph()` → Clears graph data
4. **Selection cleared** → `nodeSelection.clearSelection()` → Clears selection
5. **Panel collapsed** → `panelState.collapseRightPanel()` → Closes right panel
6. **Filters cleared** → `filters.clearFilters()` → Resets filters
7. **Stats cleared** → `setStats(null)` → Clears statistics

## Graph Layout System

### Hierarchical Layout Algorithm

**Purpose**: Calculates positions for nodes based on their hierarchy level

**Algorithm**:
1. Find root nodes (nodes with no incoming edges)
2. Perform BFS to assign levels to all nodes
3. Group nodes by level
4. Calculate width needed for each level
5. Position nodes horizontally within each level
6. Position levels vertically with spacing

**Spacing Configuration**:
- `HORIZONTAL_SPACING`: 560px (default)
- `VERTICAL_SPACING`: 360px (default)
- Node-type specific spacing:
  - Company: 600px horizontal, 400px vertical
  - Filing: 500px horizontal, 300px vertical
  - Section: 400px horizontal, 240px vertical
  - Chunk: 300px horizontal, 200px vertical

### Expansion Positioning

**Purpose**: Positions child nodes near parent when expanding

**Algorithm**:
1. Find parent node position
2. Identify direct children (nodes connected via new edges)
3. Calculate horizontal spacing: 300px between children
4. Calculate vertical offset: 250px below parent
5. Center children horizontally around parent
6. Set positions on child nodes before layout calculation

**Key Feature**: Positions are set before `applyLayout()` is called, ensuring they're preserved

### Position Preservation

**applyLayout() Function**:
- Separates nodes with and without positions
- Only calculates hierarchical layout for nodes without positions
- Preserves existing positions (manually positioned or expansion-positioned)
- Prevents position overwriting

**GraphCanvas Position Sync**:
- Tracks node position changes
- Detects user drags (position changes > 1px)
- Syncs positions back to graph data via `updateNodePositions()`
- Prevents infinite loops by tracking prop updates

### Filtering by Expanded State

**filterNodesByExpandedState() Function**:
- Always shows level 0 (root) nodes
- Always shows level 1 nodes (direct children of root)
- Shows children of expanded nodes recursively
- Preserves node positions when filtering
- Filters edges to only include connections between visible nodes

## API Integration

### Endpoints Used

- `GET /api/graph/{ticker}` - Load complete graph for a ticker
- `GET /api/graph/{ticker}/expand/{node_id}?node_type={type}` - Expand a node (load children)
- `GET /api/graph/node/{node_id}?labels={labels}` - Get node details and relationships
- `GET /api/ticker/{ticker}/stats` - Get graph statistics

### Error Handling

- All API calls wrapped in try-catch blocks
- Error messages displayed to user in UI
- Errors logged to file via logger
- Graceful degradation (e.g., uses graph node properties if details API fails)
- Non-critical errors (like expansion failures) logged but don't break UI

## Layout System

### CSS Grid Approach

The layout uses CSS Grid for the main structure and Flexbox for component-level layouts:

```css
.app-layout {
  display: grid;
  grid-template-rows: auto 1fr auto;
  height: 100vh;
}

.app-layout-body {
  display: flex;
  position: relative;
}

.app-layout-left-panel {
  position: fixed;
  left: 0;
  width: var(--left-width);
}

.app-layout-center-panel {
  margin-left: var(--left-width);
  margin-right: var(--right-width);
}

.app-layout-right-panel {
  position: fixed;
  right: 0;
  width: var(--right-width);
}
```

**Key Features**:
- Fixed positioning for side panels
- Dynamic margins for center panel
- Width transitions when panels collapse/expand
- Proper space release when panels are closed

## Logging System

### Logger Features

- File-based logging using File System Access API
- Fallback to localStorage with download option
- Log levels: debug, info, warn, error
- Component-scoped logging
- Session tracking
- Buffer flushing every 5 seconds
- Structured JSON log format

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
3. **Node Rendering**: React Flow handles efficient node/edge rendering with virtualization
4. **Position Preservation**: Efficient position tracking to prevent unnecessary recalculations
5. **State Updates**: Optimized state updates to prevent unnecessary re-renders
6. **Logging**: Buffered logging to prevent performance impact
7. **Graph Data Reference**: Uses refs to maintain graph data without triggering re-renders

## Key Design Decisions

1. **Position Preservation**: Nodes maintain their positions through expand/collapse cycles, providing better UX
2. **Relative Positioning**: Child nodes positioned relative to parent for better visual hierarchy
3. **State Management**: Custom hooks for clear separation of concerns
4. **Panel State**: Single panel state instance passed as prop to avoid duplicate instances
5. **Optimistic Updates**: Uses graph node properties immediately while fetching detailed data
6. **Error Resilience**: Non-critical errors don't break the UI
7. **Reset Functionality**: Comprehensive reset that clears all application state

## Future Enhancements

1. **Virtual Scrolling**: For large graphs with many nodes
2. **Graph Clustering**: Group related nodes
3. **Search Functionality**: Search across all nodes
4. **Export Options**: Export graph as image or data
5. **Dark Mode**: Theme switching
6. **Keyboard Shortcuts**: Power user features
7. **Graph History**: Undo/redo for graph operations
8. **Node Grouping**: Visual grouping of related nodes
9. **Custom Layouts**: User-selectable layout algorithms
10. **Performance Metrics**: Display graph rendering performance
