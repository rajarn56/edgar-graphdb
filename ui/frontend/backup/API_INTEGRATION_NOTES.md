# API Integration Notes - Current Implementation

## Backend API Endpoints

### Graph Endpoints
- `GET /api/graph/{ticker}` - Get graph data for a ticker
- `GET /api/graph/{ticker}/expand/{node_id}?node_type={type}` - Expand a node (filing or section)
- `GET /api/graph/node/{node_id}?labels={labels}` - Get node details
- `GET /api/graph/node/{node_id}/relationships?labels={labels}` - Get node relationships

### Ticker Endpoints
- `GET /api/ticker/{ticker}/info` - Get company information
- `GET /api/ticker/{ticker}/filings?form_type={type}` - Get filings list
- `GET /api/ticker/{ticker}/stats` - Get graph statistics

## Data Structures

### GraphData
```typescript
{
  nodes: GraphNode[];
  edges: GraphEdge[];
}
```

### GraphNode
```typescript
{
  id: string;
  labels: string[];
  properties: Record<string, any>;
  position?: { x: number; y: number };
}
```

### GraphEdge
```typescript
{
  source: string;
  target: string;
  type: string;
  properties: Record<string, any>;
}
```

### NodeDetails
```typescript
{
  node: GraphNode;
  relationships: Array<{
    direction: 'incoming' | 'outgoing';
    type: string;
    source: string;
    target: string;
    properties: Record<string, any>;
  }>;
  incoming_edges: GraphEdge[];
  outgoing_edges: GraphEdge[];
}
```

## Key Integration Points

1. **Graph Loading**: `graphApi.getGraph(ticker)` - Returns GraphData
2. **Node Expansion**: `graphApi.expandNode(ticker, nodeId, nodeType)` - Returns GraphData with new nodes/edges
3. **Node Details**: `graphApi.getNodeDetails(nodeId, labels)` - Returns NodeDetails
4. **Stats**: `tickerApi.getStats(ticker)` - Returns GraphStats

## Important Notes

- Chunk nodes have `content` property in `node.properties.content`
- Node labels are arrays (e.g., ['Company'], ['Filing'], ['Section'], ['Chunk'])
- Node expansion requires `nodeType` parameter: 'filing' or 'section'
- API base URL: `http://localhost:8000` (configurable via VITE_API_BASE_URL)

