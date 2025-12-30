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
  selectNode: (nodeId: string, labels: string[]) => Promise<void>;
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

  const selectNode = useCallback(async (nodeId: string, labels: string[]) => {
    logger.info('Selecting node', { nodeId, labels }, 'useNodeSelection');
    setLoading(true);
    setError(null);
    setSelectedNodeId(nodeId);

    try {
      const details = await graphApi.getNodeDetails(nodeId, labels);
      logger.info('Node details received', { 
        nodeId, 
        relationshipCount: details.relationships.length,
        hasContent: !!details.node.properties.content
      }, 'useNodeSelection');
      setNodeDetails(details);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load node details';
      logger.error('Failed to fetch node details', { nodeId, labels, error: errorMessage }, 'useNodeSelection', err);
      setError(errorMessage);
      setNodeDetails(null);
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

