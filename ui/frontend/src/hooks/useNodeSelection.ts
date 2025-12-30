/**
 * Hook for managing selected node state and details fetching.
 */

import { useState, useCallback } from 'react';
import type { NodeDetails, GraphNode } from '../types/graph';
import { graphApi } from '../services/api';
import { logger } from '../utils/logger';

export interface UseNodeSelectionReturn {
  /** Selected node details */
  nodeDetails: NodeDetails | null;
  /** Whether details are loading */
  loading: boolean;
  /** Error message */
  error: string | null;
  /** Select a node and fetch its details */
  selectNode: (nodeId: string, labels: string[], graphNode?: GraphNode) => Promise<void>;
  /** Clear selection */
  clearSelection: () => void;
  /** Currently selected node ID */
  selectedNodeId: string | null;
}

export function useNodeSelection(): UseNodeSelectionReturn {
  const [nodeDetails, setNodeDetails] = useState<NodeDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const selectNode = useCallback(async (nodeId: string, labels: string[], graphNode?: GraphNode) => {
    logger.info('Selecting node', { nodeId, labels, hasGraphNode: !!graphNode }, 'useNodeSelection');
    setLoading(true);
    setError(null);
    setSelectedNodeId(nodeId);

    // If we have graph node data, create initial node details with its properties
    // This provides immediate feedback while API call is in progress
    let initialDetails: NodeDetails | null = null;
    if (graphNode) {
      initialDetails = {
        node: {
          id: graphNode.id,
          labels: graphNode.labels,
          properties: graphNode.properties || {},
        },
        relationships: [],
        incoming_edges: [],
        outgoing_edges: [],
      };
      setNodeDetails(initialDetails);
      logger.debug('Using graph node properties as initial details', { 
        propertyCount: Object.keys(graphNode.properties || {}).length 
      }, 'useNodeSelection');
    }

    try {
      const details = await graphApi.getNodeDetails(nodeId, labels);
      logger.info('Node details received', { 
        nodeId, 
        relationshipCount: details.relationships?.length || 0,
        hasContent: !!details.node?.properties?.content,
        propertyCount: details.node?.properties ? Object.keys(details.node.properties).length : 0
      }, 'useNodeSelection');
      
      // Ensure node has properties object - merge with graph node properties if available
      if (!details.node.properties) {
        details.node.properties = {};
      }
      
      // Merge properties from graph node if API didn't return all properties
      if (graphNode && graphNode.properties) {
        details.node.properties = {
          ...graphNode.properties,
          ...details.node.properties, // API properties take precedence
        };
      }
      
      // Ensure relationships array exists
      if (!details.relationships) {
        details.relationships = [];
      }
      
      setNodeDetails(details);
      setError(null);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load node details';
      logger.error('Failed to fetch node details', { nodeId, labels, error: errorMessage, fullError: err }, 'useNodeSelection', err);
      
      // If we have graph node data, use it even if API call failed
      if (graphNode && initialDetails) {
        logger.info('Using graph node data as fallback after API error', { nodeId }, 'useNodeSelection');
        setNodeDetails(initialDetails);
        setError(null); // Don't show error if we have fallback data
      } else {
        setError(errorMessage);
        setNodeDetails(null);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const clearSelection = useCallback(() => {
    logger.debug('Clearing node selection', {}, 'useNodeSelection');
    setNodeDetails(null);
    setSelectedNodeId(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    nodeDetails,
    loading,
    error,
    selectNode,
    clearSelection,
    selectedNodeId,
  };
}

