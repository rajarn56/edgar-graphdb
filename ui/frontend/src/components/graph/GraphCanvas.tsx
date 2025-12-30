/**
 * React Flow graph canvas component with node/edge handlers and proper configuration.
 */

import React, { useCallback, useMemo, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Connection,
  NodeTypes,
  ReactFlowProvider,
  useReactFlow,
} from 'reactflow';
import 'reactflow/dist/style.css';
import type { GraphNode, GraphEdge } from '../../types/graph';
import { getNodeType, canExpandNode, getExpandNodeType } from '../../types/graph';
import CustomNode from './CustomNodes';
import CustomEdge from './CustomEdges';
import { logger } from '../../utils/logger';
import './GraphCanvas.css';

const nodeTypes: NodeTypes = {
  Company: CustomNode,
  Filing: CustomNode,
  Section: CustomNode,
  Chunk: CustomNode,
  default: CustomNode,
};

const edgeTypes = {
  default: CustomEdge,
};

export interface GraphCanvasProps {
  /** Graph nodes */
  nodes: GraphNode[];
  /** Graph edges */
  edges: GraphEdge[];
  /** Callback when node is clicked */
  onNodeClick?: (nodeId: string, labels: string[]) => void;
  /** Callback when node is double-clicked (expand) */
  onNodeDoubleClick?: (nodeId: string, nodeType: 'filing' | 'section') => void;
  /** Whether to fit view on data change */
  fitViewOnChange?: boolean;
}

function GraphCanvasInner({
  nodes: initialNodes,
  edges: initialEdges,
  onNodeClick,
  onNodeDoubleClick,
  fitViewOnChange = true,
}: GraphCanvasProps) {
  const { fitView } = useReactFlow();

  // Convert to React Flow format
  const rfNodes = useMemo(() => {
    return initialNodes.map(node => ({
      id: node.id,
      type: getNodeType(node) || 'default',
      position: node.position || { x: 0, y: 0 },
      data: {
        label: getNodeLabel(node),
        node: node,
        canExpand: canExpandNode(node),
      },
      selected: false,
    }));
  }, [initialNodes]);

  const rfEdges = useMemo(() => {
    const edges = initialEdges.map((edge, index) => ({
      id: `${edge.source}-${edge.target}-${edge.type}-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.type,
      type: 'default',
      data: {
        edge: edge,
      },
      animated: false,
      style: {
        strokeWidth: 3,
        opacity: 1, // Full opacity for better visibility
      },
      markerEnd: {
        type: 'arrowclosed',
        color: '#4b5563',
      },
    }));
    
    // Only log when edges actually change (not on every render)
    logger.debug('React Flow edges created', {
      edgeCount: edges.length,
      initialEdgeCount: initialEdges.length,
    }, 'GraphCanvas');
    
    return edges;
  }, [initialEdges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(rfNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(rfEdges);

  // Update nodes/edges when props change
  useEffect(() => {
    logger.debug('Updating React Flow nodes and edges', {
      nodeCount: rfNodes.length,
      edgeCount: rfEdges.length,
      fitViewOnChange,
    }, 'GraphCanvas');
    
    setNodes(rfNodes);
    setEdges(rfEdges);
    
    // Log edge details after setting
    if (rfEdges.length > 0) {
      logger.debug('React Flow edges set', {
        totalEdges: rfEdges.length,
        firstEdge: {
          id: rfEdges[0].id,
          source: rfEdges[0].source,
          target: rfEdges[0].target,
          style: rfEdges[0].style,
          markerEnd: rfEdges[0].markerEnd,
        },
        lastEdge: {
          id: rfEdges[rfEdges.length - 1].id,
          source: rfEdges[rfEdges.length - 1].source,
          target: rfEdges[rfEdges.length - 1].target,
        },
      }, 'GraphCanvas');
    }
    
    if (fitViewOnChange && rfNodes.length > 0) {
      // Small delay to ensure nodes are rendered
      setTimeout(() => {
        logger.debug('Fitting view', { nodeCount: rfNodes.length, edgeCount: rfEdges.length }, 'GraphCanvas');
        fitView({ padding: 0.2, duration: 400 });
      }, 100);
    }
  }, [rfNodes, rfEdges, setNodes, setEdges, fitView, fitViewOnChange]);

  const onNodeClickHandler = useCallback(
    (event: React.MouseEvent, node: Node) => {
      // Prevent default to avoid any interference
      event.preventDefault();
      event.stopPropagation();
      
      const graphNode = node.data.node as GraphNode;
      const nodeType = getNodeType(graphNode);
      
      logger.info('Node clicked in GraphCanvas', { 
        nodeId: graphNode.id, 
        labels: graphNode.labels,
        nodeType: nodeType,
        hasOnNodeClick: !!onNodeClick,
        nodePosition: node.position,
      }, 'GraphCanvas');
      
      if (onNodeClick) {
        try {
          logger.debug('Calling onNodeClick callback', { nodeId: graphNode.id, labels: graphNode.labels }, 'GraphCanvas');
          onNodeClick(graphNode.id, graphNode.labels);
          logger.debug('onNodeClick callback completed', { nodeId: graphNode.id }, 'GraphCanvas');
        } catch (error: any) {
          logger.error('Error in onNodeClick callback', { 
            nodeId: graphNode.id, 
            error: error.message,
            stack: error.stack 
          }, 'GraphCanvas', error);
        }
      } else {
        logger.warn('onNodeClick callback not provided', { nodeId: graphNode.id }, 'GraphCanvas');
      }
    },
    [onNodeClick]
  );

  const onNodeDoubleClickHandler = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      const graphNode = node.data.node as GraphNode;
      const expandType = getExpandNodeType(graphNode);
      
      if (expandType && onNodeDoubleClick) {
        logger.info('Node double-clicked (expand)', { 
          nodeId: graphNode.id, 
          expandType 
        }, 'GraphCanvas');
        onNodeDoubleClick(graphNode.id, expandType);
      }
    },
    [onNodeDoubleClick]
  );

  return (
    <div className="graph-canvas">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClickHandler}
        onNodeDoubleClick={onNodeDoubleClickHandler}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        minZoom={0.05}
        maxZoom={2}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
        attributionPosition="bottom-left"
        edgesUpdatable={false}
        edgesFocusable={true}
        selectNodesOnDrag={false}
        onlyRenderVisibleElements={false}
        elevateEdgesOnSelect={false}
        elevateNodesOnSelect={false}
      >
        <Background color="#e5e7eb" gap={20} size={1} />
        <Controls />
        <MiniMap 
          nodeColor={(node) => {
            const nodeType = node.data?.node?.labels[0] || 'default';
            return getNodeColor(nodeType);
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
    </div>
  );
}

export default function GraphCanvas(props: GraphCanvasProps) {
  return (
    <ReactFlowProvider>
      <GraphCanvasInner {...props} />
    </ReactFlowProvider>
  );
}

function getNodeLabel(node: GraphNode): string {
  if (node.labels.includes('Company')) {
    return node.properties.name || node.properties.ticker || node.id;
  }
  if (node.labels.includes('Filing')) {
    const formType = node.properties.form_type || '';
    const fiscalYear = node.properties.fiscal_year || '';
    return `${formType} ${fiscalYear}`.trim() || node.id;
  }
  if (node.labels.includes('Section')) {
    return node.properties.item_number || node.properties.item_title || node.id;
  }
  if (node.labels.includes('Chunk')) {
    const index = node.properties.chunk_index ?? '';
    return `Chunk ${index}`.trim() || node.id;
  }
  return node.id;
}

function getNodeColor(nodeType: string): string {
  switch (nodeType) {
    case 'Company':
      return '#3b82f6'; // Blue
    case 'Filing':
      return '#f59e0b'; // Amber
    case 'Section':
      return '#10b981'; // Green
    case 'Chunk':
      return '#ec4899'; // Pink
    default:
      return '#6b7280'; // Gray
  }
}

