/**
 * Custom edge components for React Flow.
 * Styled edges with labels and relationship type styling.
 */

import React from 'react';
import { BaseEdge, EdgeProps, getBezierPath } from 'reactflow';
import type { GraphEdge } from '../../types/graph';
import { logger } from '../../utils/logger';
import './CustomEdges.css';

export default function CustomEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  data,
  markerEnd,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const edge = data?.edge as GraphEdge | undefined;
  const edgeType = edge?.type || '';
  const edgeLabel = edgeType || '';

  // Color based on relationship type - more vibrant colors for better visibility
  const getEdgeColor = (type: string): string => {
    if (type.includes('FILED_BY')) return '#2563eb'; // Brighter Blue
    if (type.includes('CONTAINS')) return '#059669'; // Brighter Green
    if (type.includes('RELATES')) return '#d97706'; // Brighter Amber
    return '#4b5563'; // Darker Gray for better contrast
  };

  const edgeColor = getEdgeColor(edgeType);
  
  // Log edge rendering details (only for first few edges to avoid spam)
  if (id && (id.includes('-0') || id.includes('-1') || id.includes('-2'))) {
    logger.debug('CustomEdge rendering', {
      id,
      edgeType,
      edgeColor,
      sourceX,
      sourceY,
      targetX,
      targetY,
      hasPath: !!edgePath,
      styleOpacity: style?.opacity,
      hasMarkerEnd: !!markerEnd,
    }, 'CustomEdge');
  }

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          stroke: edgeColor,
          strokeWidth: 3,
          opacity: 1, // Increased opacity for better visibility
        }}
        className="custom-edge"
      />
      {edgeLabel && (
        <g transform={`translate(${labelX},${labelY})`}>
          <rect
            x={-edgeLabel.length * 3 - 4}
            y={-8}
            width={edgeLabel.length * 6 + 8}
            height={16}
            fill="white"
            stroke={edgeColor}
            strokeWidth={1}
            rx={4}
            className="edge-label-bg"
          />
          <text
            x={0}
            y={4}
            textAnchor="middle"
            fontSize={12}
            fill={edgeColor}
            fontWeight={600}
            className="edge-label-text"
          >
            {edgeLabel}
          </text>
        </g>
      )}
    </>
  );
}

