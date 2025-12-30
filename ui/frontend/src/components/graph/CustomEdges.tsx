/**
 * Custom edge components for React Flow.
 * Styled edges with labels and relationship type styling.
 */

import React from 'react';
import { BaseEdge, EdgeProps, getBezierPath } from 'reactflow';
import type { GraphEdge } from '../../types/graph';
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

  // Color based on relationship type
  const getEdgeColor = (type: string): string => {
    if (type.includes('FILED_BY')) return '#3b82f6'; // Blue
    if (type.includes('CONTAINS')) return '#10b981'; // Green
    if (type.includes('RELATES')) return '#f59e0b'; // Amber
    return '#6b7280'; // Gray
  };

  const edgeColor = getEdgeColor(edgeType);

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          stroke: edgeColor,
          strokeWidth: 2,
        }}
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
            fontSize={11}
            fill={edgeColor}
            fontWeight={500}
            className="edge-label-text"
          >
            {edgeLabel}
          </text>
        </g>
      )}
    </>
  );
}

