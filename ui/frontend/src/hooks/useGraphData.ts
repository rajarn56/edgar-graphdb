/**
 * Hook for managing graph data state and API calls.
 */

import { useState, useCallback, useRef } from 'react';
import type { GraphData, GraphNode, GraphEdge } from '../types/graph';
import { graphApi } from '../services/api';
import { logger } from '../utils/logger';
import { applyLayout, filterNodesByExpandedState } from '../utils/graphLayout';

export interface UseGraphDataReturn {
  /** Current graph data */
  graphData: GraphData;
  /** Whether graph is loading */
  loading: boolean;
  /** Error message */
  error: string | null;
  /** Current ticker */
  ticker: string | null;
  /** Set of expanded node IDs */
  expandedNodes: Set<string>;
  /** Load graph for a ticker */
  loadGraph: (ticker: string) => Promise<void>;
  /** Expand a node */
  expandNode: (nodeId: string, nodeType: 'filing' | 'section', ticker: string) => Promise<void>;
  /** Collapse a node (hide its children) */
  collapseNode: (nodeId: string) => void;
  /** Toggle node expansion state (UI only, for showing/hiding children) */
  toggleNodeExpansion: (nodeId: string) => void;
  /** Add nodes and edges to graph */
  addToGraph: (newData: GraphData) => void;
  /** Reset graph data */
  resetGraph: () => void;
  /** Update node positions */
  updateNodePositions: (positions: Map<string, { x: number; y: number }>) => void;
}

export function useGraphData(): UseGraphDataReturn {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ticker, setTicker] = useState<string | null>(null);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const graphDataRef = useRef<GraphData>({ nodes: [], edges: [] });

  const loadGraph = useCallback(async (newTicker: string) => {
    logger.info('Loading graph', { ticker: newTicker }, 'useGraphData');
    setLoading(true);
    setError(null);
    setTicker(newTicker);
    setExpandedNodes(new Set());

    try {
      const data = await graphApi.getGraph(newTicker);
      logger.info('Graph loaded', { 
        nodeCount: data.nodes.length, 
        edgeCount: data.edges.length 
      }, 'useGraphData');

      // Apply layout
      const nodesWithLayout = applyLayout(data.nodes, data.edges);
      const layoutedData = { nodes: nodesWithLayout, edges: data.edges };
      
      setGraphData(layoutedData);
      graphDataRef.current = layoutedData;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load graph';
      logger.error('Failed to load graph', { ticker: newTicker, error: errorMessage }, 'useGraphData', err);
      setError(errorMessage);
      setGraphData({ nodes: [], edges: [] });
      graphDataRef.current = { nodes: [], edges: [] };
    } finally {
      setLoading(false);
    }
  }, []);

  const expandNode = useCallback(async (nodeId: string, nodeType: 'filing' | 'section', currentTicker: string) => {
    if (expandedNodes.has(nodeId)) {
      logger.debug('Node already expanded', { nodeId }, 'useGraphData');
      return;
    }

    logger.info('Expanding node', { nodeId, nodeType, ticker: currentTicker }, 'useGraphData');

    try {
      const expandedData = await graphApi.expandNode(currentTicker, nodeId, nodeType);
      logger.info('Node expanded', { 
        nodeId, 
        newNodeCount: expandedData.nodes.length, 
        newEdgeCount: expandedData.edges.length 
      }, 'useGraphData');

      // Merge with existing graph data
      const existingNodeIds = new Set(graphDataRef.current.nodes.map(n => n.id));
      const existingEdgeKeys = new Set(
        graphDataRef.current.edges.map(e => `${e.source}-${e.target}-${e.type}`)
      );

      const newNodes = expandedData.nodes.filter(n => !existingNodeIds.has(n.id));
      const newEdges = expandedData.edges.filter(e => {
        const key = `${e.source}-${e.target}-${e.type}`;
        return !existingEdgeKeys.has(key);
      });

      const updatedNodes = [...graphDataRef.current.nodes, ...newNodes];
      const updatedEdges = [...graphDataRef.current.edges, ...newEdges];

      // Position new child nodes near their parent instead of using full layout
      // This provides better UX - children appear close to parent when expanded
      const parentNode = updatedNodes.find(n => n.id === nodeId);
      if (parentNode && parentNode.position && newNodes.length > 0) {
        // Position children relative to parent
        const parentX = parentNode.position.x;
        const parentY = parentNode.position.y;
        const childSpacing = 300; // Horizontal spacing between children (reduced for closer positioning)
        const verticalOffset = 250; // Vertical offset below parent (reduced for closer positioning)
        
        // Find direct children of the expanded node
        const directChildren = newNodes.filter(childNode => 
          newEdges.some(e => e.source === nodeId && e.target === childNode.id)
        );
        
        // Update positions on updatedNodes array (not newNodes) so they're preserved
        directChildren.forEach((childNode, index) => {
          const nodeIndex = updatedNodes.findIndex(n => n.id === childNode.id);
          if (nodeIndex !== -1 && !updatedNodes[nodeIndex].position) {
            // Position relative to parent - center children horizontally around parent
            const totalWidth = (directChildren.length - 1) * childSpacing;
            const startX = parentX - totalWidth / 2;
            const childX = startX + (index * childSpacing);
            const childY = parentY + verticalOffset;
            
            updatedNodes[nodeIndex] = {
              ...updatedNodes[nodeIndex],
              position: { x: childX, y: childY },
            };
            logger.debug('Positioned child node relative to parent', {
              childId: childNode.id,
              parentId: nodeId,
              position: { x: childX, y: childY },
              parentPosition: { x: parentX, y: parentY },
              childIndex: index,
              totalChildren: directChildren.length,
            }, 'useGraphData');
          }
        });
      }

      // Apply layout to updated graph (will preserve manually positioned nodes)
      // applyLayout now explicitly preserves nodes with positions and only calculates for nodes without positions
      const nodesWithLayout = applyLayout(updatedNodes, updatedEdges);
      const mergedData = { nodes: nodesWithLayout, edges: updatedEdges };

      setGraphData(mergedData);
      graphDataRef.current = mergedData;
      setExpandedNodes(prev => new Set([...prev, nodeId]));

      logger.debug('Graph updated after expansion', { 
        totalNodes: nodesWithLayout.length, 
        totalEdges: updatedEdges.length 
      }, 'useGraphData');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to expand node';
      logger.error('Failed to expand node', { nodeId, nodeType, error: errorMessage, fullError: err }, 'useGraphData', err);
      
      // Don't set global error for expansion failures - just log it
      // Expansion failures are not critical and shouldn't break the UI
      logger.warn('Node expansion failed, but continuing', { nodeId, nodeType, error: errorMessage }, 'useGraphData');
    }
  }, [expandedNodes]);

  const collapseNode = useCallback((nodeId: string) => {
    if (!expandedNodes.has(nodeId)) {
      logger.debug('Node not expanded, cannot collapse', { nodeId }, 'useGraphData');
      return;
    }

    logger.info('Collapsing node', { nodeId }, 'useGraphData');
    
    // Remove from expanded nodes set
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      newSet.delete(nodeId);
      return newSet;
    });
  }, [expandedNodes]);

  const toggleNodeExpansion = useCallback((nodeId: string) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(nodeId)) {
        logger.info('Collapsing node (UI)', { nodeId }, 'useGraphData');
        newSet.delete(nodeId);
      } else {
        logger.info('Expanding node (UI)', { nodeId }, 'useGraphData');
        newSet.add(nodeId);
      }
      return newSet;
    });
  }, []);

  const addToGraph = useCallback((newData: GraphData) => {
    logger.debug('Adding to graph', { 
      newNodeCount: newData.nodes.length, 
      newEdgeCount: newData.edges.length 
    }, 'useGraphData');

    const existingNodeIds = new Set(graphDataRef.current.nodes.map(n => n.id));
    const existingEdgeKeys = new Set(
      graphDataRef.current.edges.map(e => `${e.source}-${e.target}-${e.type}`)
    );

    const nodesToAdd = newData.nodes.filter(n => !existingNodeIds.has(n.id));
    const edgesToAdd = newData.edges.filter(e => {
      const key = `${e.source}-${e.target}-${e.type}`;
      return !existingEdgeKeys.has(key);
    });

    const updatedNodes = [...graphDataRef.current.nodes, ...nodesToAdd];
    const updatedEdges = [...graphDataRef.current.edges, ...edgesToAdd];

    const nodesWithLayout = applyLayout(updatedNodes, updatedEdges);
    const mergedData = { nodes: nodesWithLayout, edges: updatedEdges };

    setGraphData(mergedData);
    graphDataRef.current = mergedData;
  }, []);

  const resetGraph = useCallback(() => {
    logger.debug('Resetting graph', {}, 'useGraphData');
    setGraphData({ nodes: [], edges: [] });
    graphDataRef.current = { nodes: [], edges: [] };
    setExpandedNodes(new Set());
    setTicker(null);
    setError(null);
  }, []);

  const updateNodePositions = useCallback((positions: Map<string, { x: number; y: number }>) => {
    const updatedNodes = graphDataRef.current.nodes.map(node => {
      const pos = positions.get(node.id);
      if (pos) {
        return { ...node, position: pos };
      }
      return node;
    });

    const updatedData = { ...graphDataRef.current, nodes: updatedNodes };
    setGraphData(updatedData);
    graphDataRef.current = updatedData;
  }, []);

  return {
    graphData,
    loading,
    error,
    ticker,
    expandedNodes,
    loadGraph,
    expandNode,
    collapseNode,
    toggleNodeExpansion,
    addToGraph,
    resetGraph,
    updateNodePositions,
  };
}

