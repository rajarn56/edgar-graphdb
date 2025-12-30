/**
 * React Flow graph canvas component.
 */

import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeTypes,
  EdgeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import type { GraphNode, GraphEdge } from '../types/graph';
import { applyLayout } from '../utils/graphLayout';
import CustomNode from './NodeTypes';

const nodeTypes: NodeTypes = {
  Company: CustomNode,
  Filing: CustomNode,
  Section: CustomNode,
  Chunk: CustomNode,
  default: CustomNode,
};

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (nodeId: string, labels: string[]) => void;
  onNodeExpand?: (nodeId: string, nodeType: 'filing' | 'section') => void;
}

export default function GraphCanvas({
  nodes: initialNodes,
  edges: initialEdges,
  onNodeClick,
  onNodeExpand,
}: GraphCanvasProps) {
  // Convert to React Flow format
  const rfNodes = useMemo(() => {
    return initialNodes.map(node => ({
      id: node.id,
      type: node.labels[0] || 'default',
      position: node.position || { x: 0, y: 0 },
      data: {
        label: getNodeLabel(node),
        node: node,
      },
    }));
  }, [initialNodes]);

  const rfEdges = useMemo(() => {
    return initialEdges.map(edge => ({
      id: `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      label: edge.type,
      type: 'smoothstep',
    }));
  }, [initialEdges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(rfNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(rfEdges);

  // Update nodes/edges when props change
  React.useEffect(() => {
    setNodes(rfNodes);
    setEdges(rfEdges);
  }, [rfNodes, rfEdges, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge(params, eds));
    },
    [setEdges]
  );

  const onNodeClickHandler = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      const graphNode = node.data.node as GraphNode;
      if (onNodeClick) {
        onNodeClick(graphNode.id, graphNode.labels);
      }
    },
    [onNodeClick]
  );

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClickHandler}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}

function getNodeLabel(node: GraphNode): string {
  if (node.labels.includes('Company')) {
    return node.properties.name || node.properties.ticker || node.id;
  }
  if (node.labels.includes('Filing')) {
    return `${node.properties.form_type || ''} ${node.properties.fiscal_year || ''}`.trim();
  }
  if (node.labels.includes('Section')) {
    return node.properties.item_number || node.properties.item_title || node.id;
  }
  if (node.labels.includes('Chunk')) {
    return `Chunk ${node.properties.chunk_index ?? ''}`.trim();
  }
  return node.id;
}

