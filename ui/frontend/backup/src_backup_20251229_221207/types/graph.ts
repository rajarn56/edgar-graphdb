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

