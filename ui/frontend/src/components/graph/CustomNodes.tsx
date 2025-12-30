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
  isExpanded?: boolean;
  hasChildren?: boolean;
  onExpandCollapse?: (nodeId: string, isExpanded: boolean) => void;
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
  const isExpanded = data.isExpanded ?? false;
  const hasChildren = data.hasChildren ?? false;
  
  const handleExpandCollapseClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent node click event
    if (data.onExpandCollapse) {
      data.onExpandCollapse(data.node.id, !isExpanded);
    }
  };

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
          ? '0 4px 12px rgba(0,0,0,0.4)' 
          : '0 2px 8px rgba(0,0,0,0.25)',
        border: `3px solid ${selected ? '#ffffff' : 'rgba(255,255,255,0.4)'}`,
        transition: 'all 0.2s ease',
        cursor: 'pointer',
        position: 'relative',
        opacity: 1,
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
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
      }}>
        {/* Main label */}
        <div style={{ fontWeight: isCompany ? 'bold' : '600', fontSize: isCompany ? '15px' : isFiling ? '13px' : '12px' }}>
          {data.label}
        </div>
        
        {/* Company attributes */}
        {isCompany && (
          <>
            {data.node.properties.ticker && (
              <div style={{ fontSize: '11px', opacity: 0.9, fontWeight: '500' }}>
                {data.node.properties.ticker}
              </div>
            )}
            {data.node.properties.cik && (
              <div style={{ fontSize: '10px', opacity: 0.8 }}>
                CIK: {data.node.properties.cik}
              </div>
            )}
          </>
        )}
        
        {/* Filing attributes */}
        {isFiling && (
          <>
            {data.node.properties.form_type && (
              <div style={{ fontSize: '11px', opacity: 0.9, fontWeight: '500' }}>
                {data.node.properties.form_type}
              </div>
            )}
            {data.node.properties.fiscal_year && (
              <div style={{ fontSize: '10px', opacity: 0.8 }}>
                FY {data.node.properties.fiscal_year}
                {data.node.properties.fiscal_quarter && ` Q${data.node.properties.fiscal_quarter}`}
              </div>
            )}
            {data.node.properties.filing_date && (
              <div style={{ fontSize: '9px', opacity: 0.75 }}>
                {new Date(data.node.properties.filing_date).getFullYear()}
              </div>
            )}
          </>
        )}
        
        {/* Section attributes */}
        {isSection && (
          <>
            {data.node.properties.item_number && (
              <div style={{ fontSize: '11px', opacity: 0.9, fontWeight: '500' }}>
                {data.node.properties.item_number}
              </div>
            )}
            {data.node.properties.item_title && (
              <div style={{ fontSize: '10px', opacity: 0.8, lineHeight: '1.2' }}>
                {data.node.properties.item_title.length > 25 
                  ? data.node.properties.item_title.substring(0, 25) + '...'
                  : data.node.properties.item_title}
              </div>
            )}
          </>
        )}
        
        {/* Chunk attributes */}
        {isChunk && (
          <>
            {data.node.properties.chunk_index !== undefined && (
              <div style={{ fontSize: '11px', opacity: 0.9, fontWeight: '500' }}>
                Chunk #{data.node.properties.chunk_index}
              </div>
            )}
            {data.node.properties.chunk_type && (
              <div style={{ fontSize: '10px', opacity: 0.8 }}>
                {data.node.properties.chunk_type}
              </div>
            )}
          </>
        )}
      </div>

      {/* Expand/Collapse button - show if node has children or can be expanded */}
      {(hasChildren || canExpand) && (
        <button
          onClick={handleExpandCollapseClick}
          className="expand-collapse-button"
          title={isExpanded ? 'Click to collapse' : 'Click to expand'}
          style={{
            position: 'absolute',
            bottom: '4px',
            right: '4px',
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            background: isExpanded ? 'rgba(255, 255, 255, 0.5)' : 'rgba(255, 255, 255, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
            fontWeight: 'bold',
            color: 'white',
            cursor: 'pointer',
            padding: 0,
            lineHeight: 1,
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.7)';
            e.currentTarget.style.transform = 'scale(1.1)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = isExpanded ? 'rgba(255, 255, 255, 0.5)' : 'rgba(255, 255, 255, 0.3)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          {isExpanded ? '−' : '+'}
        </button>
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

