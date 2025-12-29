/**
 * Custom node components for React Flow.
 */

import React from 'react';
import { Handle, Position } from 'reactflow';
import type { GraphNode } from '../types/graph';
import './NodeTypes.css';

interface NodeData {
  label: string;
  node: GraphNode;
}

interface CustomNodeProps {
  data: NodeData;
}

function getNodeType(node: GraphNode): string {
  if (node.labels.includes('Company')) return 'Company';
  if (node.labels.includes('Filing')) return 'Filing';
  if (node.labels.includes('Section')) return 'Section';
  if (node.labels.includes('Chunk')) return 'Chunk';
  return 'default';
}

function getNodeColor(nodeType: string): string {
  switch (nodeType) {
    case 'Company':
      return '#3b82f6'; // Blue
    case 'Filing':
      return '#fbbf24'; // Yellow
    case 'Section':
      return '#10b981'; // Green
    case 'Chunk':
      return '#ec4899'; // Pink
    default:
      return '#6b7280'; // Gray
  }
}

function getNodeSize(nodeType: string): { width: number; height: number } {
  switch (nodeType) {
    case 'Company':
      return { width: 200, height: 120 };
    case 'Filing':
      return { width: 180, height: 100 };
    case 'Section':
      return { width: 160, height: 80 };
    case 'Chunk':
      return { width: 120, height: 60 };
    default:
      return { width: 150, height: 80 };
  }
}

export default function CustomNode({ data }: CustomNodeProps) {
  const nodeType = getNodeType(data.node);
  const color = getNodeColor(nodeType);
  const size = getNodeSize(nodeType);
  const isCompany = nodeType === 'Company';
  const isFiling = nodeType === 'Filing';
  const isSection = nodeType === 'Section';
  const isChunk = nodeType === 'Chunk';

  return (
    <div
      className={`custom-node ${nodeType.toLowerCase()}`}
      style={{
        backgroundColor: color,
        width: size.width,
        height: size.height,
        borderRadius: isCompany ? '50%' : isChunk ? '50%' : '8px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '8px',
        color: 'white',
        fontSize: isCompany ? '14px' : isFiling ? '12px' : '11px',
        fontWeight: isCompany ? 'bold' : 'normal',
        boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
        border: '2px solid white',
      }}
    >
      <Handle type="target" position={Position.Top} />
      <div style={{ textAlign: 'center', wordBreak: 'break-word' }}>
        {data.label}
      </div>
      {isCompany && data.node.properties.ticker && (
        <div style={{ fontSize: '10px', marginTop: '4px', opacity: 0.9 }}>
          {data.node.properties.ticker}
        </div>
      )}
      {isFiling && data.node.properties.fiscal_quarter && (
        <div style={{ fontSize: '10px', marginTop: '4px', opacity: 0.9 }}>
          Q{data.node.properties.fiscal_quarter}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Export individual node components for future customization
export const CompanyNode = CustomNode;
export const FilingNode = CustomNode;
export const SectionNode = CustomNode;
export const ChunkNode = CustomNode;

