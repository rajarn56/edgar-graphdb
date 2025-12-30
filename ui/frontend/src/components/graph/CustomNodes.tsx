/**
 * Custom node components for React Flow.
 * Includes Company, Filing, Section, and Chunk nodes with proper styling.
 */

import React from 'react';
import { Handle, Position } from 'reactflow';
import type { GraphNode } from '../../types/graph';
import { getNodeType, canExpandNode } from '../../types/graph';
import { logger } from '../../utils/logger';
import './CustomNodes.css';

interface NodeData {
  label: string;
  node: GraphNode;
  canExpand?: boolean;
}

interface CustomNodeProps {
  data: NodeData;
  selected?: boolean;
}

function getNodeColor(nodeType: string): string {
  switch (nodeType) {
    case 'Company':
      return '#3b82f6'; // Blue
    case 'Filing':
      return '#f59e0b'; // Amber/Yellow
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
      return { width: 220, height: 140 };
    case 'Filing':
      return { width: 200, height: 110 };
    case 'Section':
      return { width: 180, height: 90 };
    case 'Chunk':
      return { width: 140, height: 70 };
    default:
      return { width: 160, height: 90 };
  }
}

export default function CustomNode({ data, selected }: CustomNodeProps) {
  const nodeType = getNodeType(data.node);
  const color = getNodeColor(nodeType);
  const size = getNodeSize(nodeType);
  const isCompany = nodeType === 'Company';
  const isFiling = nodeType === 'Filing';
  const isSection = nodeType === 'Section';
  const isChunk = nodeType === 'Chunk';
  const canExpand = data.canExpand ?? canExpandNode(data.node);

  const handleMouseEnter = () => {
    logger.debug('Node hover', { nodeId: data.node.id, nodeType }, 'CustomNode');
  };

  return (
    <div
      className={`custom-node custom-node-${nodeType.toLowerCase()} ${selected ? 'selected' : ''}`}
      style={{
        backgroundColor: color,
        width: size.width,
        height: size.height,
        borderRadius: isCompany || isChunk ? '50%' : '12px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '12px',
        color: 'white',
        fontSize: isCompany ? '15px' : isFiling ? '13px' : '12px',
        fontWeight: isCompany ? 'bold' : 'normal',
        boxShadow: selected 
          ? '0 4px 12px rgba(0,0,0,0.3)' 
          : '0 2px 8px rgba(0,0,0,0.2)',
        border: `3px solid ${selected ? '#ffffff' : 'rgba(255,255,255,0.3)'}`,
        transition: 'all 0.2s ease',
        cursor: 'pointer',
        position: 'relative',
      }}
      onMouseEnter={handleMouseEnter}
    >
      <Handle type="target" position={Position.Top} style={{ background: color }} />
      
      <div style={{ 
        textAlign: 'center', 
        wordBreak: 'break-word',
        width: '100%',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
      }}>
        <div style={{ fontWeight: isCompany ? 'bold' : '600' }}>
          {data.label}
        </div>
        
        {isCompany && data.node.properties.ticker && (
          <div style={{ fontSize: '11px', marginTop: '4px', opacity: 0.9 }}>
            {data.node.properties.ticker}
          </div>
        )}
        
        {isFiling && data.node.properties.fiscal_quarter && (
          <div style={{ fontSize: '11px', marginTop: '4px', opacity: 0.9 }}>
            Q{data.node.properties.fiscal_quarter}
          </div>
        )}
        
        {isSection && data.node.properties.item_title && (
          <div style={{ fontSize: '10px', marginTop: '4px', opacity: 0.85 }}>
            {data.node.properties.item_title.substring(0, 30)}
            {data.node.properties.item_title.length > 30 ? '...' : ''}
          </div>
        )}
        
        {isChunk && data.node.properties.chunk_type && (
          <div style={{ fontSize: '10px', marginTop: '4px', opacity: 0.85 }}>
            {data.node.properties.chunk_type}
          </div>
        )}
      </div>

      {canExpand && (
        <div 
          className="expand-indicator"
          title="Double-click to expand"
          style={{
            position: 'absolute',
            bottom: '4px',
            right: '4px',
            width: '16px',
            height: '16px',
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '10px',
          }}
        >
          +
        </div>
      )}

      <Handle type="source" position={Position.Bottom} style={{ background: color }} />
    </div>
  );
}

// Export individual node components for future customization
export const CompanyNode = CustomNode;
export const FilingNode = CustomNode;
export const SectionNode = CustomNode;
export const ChunkNode = CustomNode;

