/**
 * TypeScript types for graph data structures.
 */

export interface GraphNode {
  id: string;
  labels: string[];
  properties: Record<string, any>;
  position?: { x: number; y: number };
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  properties: Record<string, any>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface NodeDetails {
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

export interface CompanyInfo {
  cik: string;
  name: string;
  ticker?: string;
  sic?: string;
  sic_description?: string;
  exchange?: string;
  incorporation_state?: string;
}

export interface FilingInfo {
  accession_number: string;
  form_type: string;
  filing_date?: string;
  period_end_date?: string;
  fiscal_year?: number;
  fiscal_quarter?: number;
  fiscal_period?: string;
  url?: string;
}

export interface GraphStats {
  company: CompanyInfo;
  filings_count: number;
  sections_count: number;
  chunks_count: number;
  financial_statements_count: number;
}

export type NodeType = 'Company' | 'Filing' | 'Section' | 'Chunk' | 'Period' | 'FinancialStatement' | 'LineItem' | 'Value' | 'Metric' | 'RiskFactor' | string;

/**
 * Node type helpers
 */
export const NODE_TYPES = {
  COMPANY: 'Company',
  FILING: 'Filing',
  SECTION: 'Section',
  CHUNK: 'Chunk',
  PERIOD: 'Period',
  FINANCIAL_STATEMENT: 'FinancialStatement',
  LINE_ITEM: 'LineItem',
  VALUE: 'Value',
  METRIC: 'Metric',
  RISK_FACTOR: 'RiskFactor',
} as const;

/**
 * Check if a node is of a specific type
 */
export function isNodeType(node: GraphNode, type: string): boolean {
  return node.labels.includes(type);
}

/**
 * Get primary node type (first label)
 */
export function getNodeType(node: GraphNode): NodeType {
  return node.labels[0] || 'default';
}

/**
 * Check if a node can be expanded
 */
export function canExpandNode(node: GraphNode): boolean {
  const nodeType = getNodeType(node);
  return nodeType === NODE_TYPES.FILING || nodeType === NODE_TYPES.SECTION;
}

/**
 * Get expand node type for API call
 */
export function getExpandNodeType(node: GraphNode): 'filing' | 'section' | null {
  const nodeType = getNodeType(node);
  if (nodeType === NODE_TYPES.FILING) return 'filing';
  if (nodeType === NODE_TYPES.SECTION) return 'section';
  return null;
}

/**
 * Graph node with React Flow specific data
 */
export interface ReactFlowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: {
    label: string;
    node: GraphNode;
  };
  selected?: boolean;
  dragging?: boolean;
}

/**
 * Graph edge with React Flow specific data
 */
export interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  label?: string;
  animated?: boolean;
  style?: Record<string, any>;
  data?: {
    edge: GraphEdge;
  };
}

/**
 * Graph viewport state
 */
export interface GraphViewport {
  x: number;
  y: number;
  zoom: number;
}

/**
 * Graph layout options
 */
export interface LayoutOptions {
  /** Layout algorithm to use */
  algorithm: 'hierarchical' | 'force-directed' | 'circular';
  /** Horizontal spacing between nodes */
  horizontalSpacing: number;
  /** Vertical spacing between nodes */
  verticalSpacing: number;
  /** Direction of layout (for hierarchical) */
  direction: 'TB' | 'BT' | 'LR' | 'RL';
}

