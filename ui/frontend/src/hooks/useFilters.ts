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
        filteredNodes = filteredNodes.filter(node => {
          if (node.labels.includes('Filing')) {
            return node.properties.form_type === filters.formType;
          }
          // Keep non-filing nodes
          return true;
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

