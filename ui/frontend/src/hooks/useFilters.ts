/**
 * Hook for filter state management and application.
 */

import { useState, useCallback, useMemo } from 'react';
import type { FilterOptions } from '../types/ui';
import type { GraphNode, GraphEdge } from '../types/graph';
import { logger } from '../utils/logger';

export interface UseFiltersReturn {
  /** Current filter options */
  filters: FilterOptions;
  /** Set filter options */
  setFilters: (filters: FilterOptions) => void;
  /** Apply filters to graph data */
  applyFilters: (nodes: GraphNode[], edges: GraphEdge[]) => { nodes: GraphNode[]; edges: GraphEdge[] };
  /** Clear all filters */
  clearFilters: () => void;
  /** Get active filter count */
  getActiveFilterCount: () => number;
}

const DEFAULT_FILTERS: FilterOptions = {
  nodeTypes: ['Company', 'Filing', 'Section', 'Chunk'],
};

export function useFilters(): UseFiltersReturn {
  const [filters, setFiltersState] = useState<FilterOptions>(DEFAULT_FILTERS);

  const setFilters = useCallback((newFilters: FilterOptions) => {
    logger.debug('Filters updated', newFilters, 'useFilters');
    setFiltersState(newFilters);
  }, []);

  const applyFilters = useCallback(
    (nodes: GraphNode[], edges: GraphEdge[]): { nodes: GraphNode[]; edges: GraphEdge[] } => {
      // Filter by node types
      let filteredNodes = nodes.filter(node => {
        if (!filters.nodeTypes || filters.nodeTypes.length === 0) {
          return false;
        }
        return node.labels.some(label => filters.nodeTypes!.includes(label));
      });

      // Filter by form type
      if (filters.formType) {
        // Build a reverse graph (child -> parent mapping) to traverse up the hierarchy
        // Use original edges to ensure we can traverse the full graph
        const parentMap = new Map<string, string>();
        edges.forEach(edge => {
          parentMap.set(edge.target, edge.source);
        });

        // Build a node lookup map for quick access
        // Use original nodes to ensure we can find all nodes in the hierarchy
        const nodeMap = new Map<string, GraphNode>();
        nodes.forEach(node => {
          nodeMap.set(node.id, node);
        });

        // Helper function to find ancestor Filing node
        const findAncestorFiling = (nodeId: string): GraphNode | null => {
          const visited = new Set<string>();
          let currentId: string | undefined = nodeId;

          while (currentId && !visited.has(currentId)) {
            visited.add(currentId);
            const currentNode = nodeMap.get(currentId);
            
            if (currentNode && currentNode.labels.includes('Filing')) {
              return currentNode;
            }

            // Move to parent
            currentId = parentMap.get(currentId);
          }

          return null;
        };

        filteredNodes = filteredNodes.filter(node => {
          // If it's a Filing node, check if form_type matches
          if (node.labels.includes('Filing')) {
            return node.properties.form_type === filters.formType;
          }

          // If it's a Company node (root level), keep it
          if (node.labels.includes('Company')) {
            return true;
          }

          // For other nodes (Section, Chunk, etc.), find ancestor Filing node
          const ancestorFiling = findAncestorFiling(node.id);
          
          // If no ancestor Filing found, keep the node (edge case - shouldn't happen in normal hierarchy)
          if (!ancestorFiling) {
            logger.warn('Node has no ancestor Filing node', { nodeId: node.id, labels: node.labels }, 'useFilters');
            return true;
          }

          // Check if ancestor Filing matches the form type filter
          return ancestorFiling.properties.form_type === filters.formType;
        });
      }

      // Filter by fiscal year
      if (filters.fiscalYear !== undefined) {
        filteredNodes = filteredNodes.filter(node => {
          if (node.properties.fiscal_year !== undefined) {
            return node.properties.fiscal_year === filters.fiscalYear;
          }
          // Keep nodes without fiscal_year
          return true;
        });
      }

      // Filter edges to only include connections between filtered nodes
      const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
      const filteredEdges = edges.filter(edge => {
        return filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target);
      });

      logger.debug('Filters applied', {
        originalNodeCount: nodes.length,
        filteredNodeCount: filteredNodes.length,
        originalEdgeCount: edges.length,
        filteredEdgeCount: filteredEdges.length,
      }, 'useFilters');

      return { nodes: filteredNodes, edges: filteredEdges };
    },
    [filters]
  );

  const clearFilters = useCallback(() => {
    logger.debug('Filters cleared', {}, 'useFilters');
    setFiltersState(DEFAULT_FILTERS);
  }, []);

  const getActiveFilterCount = useCallback((): number => {
    let count = 0;
    if (filters.formType) count++;
    if (filters.fiscalYear !== undefined) count++;
    if (filters.nodeTypes && filters.nodeTypes.length < 6) {
      // Assuming 6 is the total number of possible node types
      count++;
    }
    return count;
  }, [filters]);

  return {
    filters,
    setFilters,
    applyFilters,
    clearFilters,
    getActiveFilterCount,
  };
}

