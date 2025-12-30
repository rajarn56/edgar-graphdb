/**
 * Main application component with comprehensive state management.
 * Integrates all components and handles all user interactions.
 */

import React, { useCallback, useMemo, useEffect } from 'react';
import AppLayout from './components/layout/AppLayout';
import GraphCanvas from './components/graph/GraphCanvas';
import NodeDetailsPanel from './components/details/NodeDetailsPanel';
import FilterPanel from './components/filters/FilterPanel';
import AppHeader from './components/header/AppHeader';
import { useGraphData } from './hooks/useGraphData';
import { useNodeSelection } from './hooks/useNodeSelection';
import { useFilters } from './hooks/useFilters';
import { usePanelState } from './hooks/usePanelState';
import { tickerApi } from './services/api';
import type { GraphStats } from './types/graph';
import { logger } from './utils/logger';
import { getNodeType, getExpandNodeType } from './types/graph';
import './App.css';

function App() {
  // Graph data management
  const graphData = useGraphData();
  
  // Node selection management
  const nodeSelection = useNodeSelection();
  
  // Filter management
  const filters = useFilters();
  
  // Panel state management
  const panelState = usePanelState();
  
  // Stats state
  const [stats, setStats] = React.useState<GraphStats | null>(null);

  // Extract available form types and years from graph data
  const availableFormTypes = useMemo(() => {
    const formTypes = new Set<string>();
    graphData.graphData.nodes.forEach(node => {
      if (node.labels.includes('Filing') && node.properties.form_type) {
        formTypes.add(node.properties.form_type);
      }
    });
    return Array.from(formTypes).sort();
  }, [graphData.graphData.nodes]);

  const availableYears = useMemo(() => {
    const years = new Set<number>();
    graphData.graphData.nodes.forEach(node => {
      if (node.properties.fiscal_year) {
        years.add(node.properties.fiscal_year);
      }
    });
    return Array.from(years).sort((a, b) => b - a);
  }, [graphData.graphData.nodes]);

  // Apply filters to graph data
  const filteredGraphData = useMemo(() => {
    return filters.applyFilters(graphData.graphData.nodes, graphData.graphData.edges);
  }, [graphData.graphData, filters]);

  // Handle ticker submission
  const handleTickerSubmit = useCallback(async (ticker: string) => {
    if (!ticker.trim()) {
      logger.warn('Empty ticker submitted', {}, 'App');
      return;
    }

    logger.info('Ticker submitted', { ticker }, 'App');
    
    // Load graph
    await graphData.loadGraph(ticker);
    
    // Clear node selection
    nodeSelection.clearSelection();
    
    // Expand right panel if node was selected
    if (nodeSelection.selectedNodeId) {
      panelState.expandRightPanel();
    } else {
      panelState.collapseRightPanel();
    }

    // Fetch stats
    try {
      const statsData = await tickerApi.getStats(ticker);
      setStats(statsData);
      logger.info('Stats loaded', statsData, 'App');
    } catch (err: any) {
      logger.warn('Failed to load stats', { ticker, error: err }, 'App');
    }
  }, [graphData, nodeSelection, panelState]);

  // Handle node click
  const handleNodeClick = useCallback((nodeId: string, labels: string[]) => {
    logger.info('Node clicked', { nodeId, labels }, 'App');
    nodeSelection.selectNode(nodeId, labels);
    panelState.expandRightPanel();
  }, [nodeSelection, panelState]);

  // Handle node double-click (expand)
  const handleNodeDoubleClick = useCallback(async (nodeId: string, nodeType: 'filing' | 'section') => {
    if (!graphData.ticker) {
      logger.warn('Cannot expand node: no ticker loaded', { nodeId }, 'App');
      return;
    }

    logger.info('Node double-clicked (expand)', { nodeId, nodeType }, 'App');
    await graphData.expandNode(nodeId, nodeType, graphData.ticker);
  }, [graphData]);

  // Handle filter change
  const handleFilterChange = useCallback((newFilters: typeof filters.filters) => {
    logger.debug('Filters changed', newFilters, 'App');
    filters.setFilters(newFilters);
  }, [filters]);

  // Handle panel close
  const handlePanelClose = useCallback(() => {
    logger.debug('Panel closed', {}, 'App');
    nodeSelection.clearSelection();
    panelState.collapseRightPanel();
  }, [nodeSelection, panelState]);

  // Log app initialization
  useEffect(() => {
    logger.info('App initialized', {
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      environment: import.meta.env.MODE,
    }, 'App');
  }, []);

  // Update right panel visibility based on node selection
  useEffect(() => {
    if (nodeSelection.selectedNodeId) {
      // Always expand panel when a node is selected, even if details are still loading
      panelState.expandRightPanel();
      logger.debug('Right panel expanded due to node selection', { 
        nodeId: nodeSelection.selectedNodeId,
        hasDetails: !!nodeSelection.nodeDetails,
        loading: nodeSelection.loading 
      }, 'App');
    }
    // Don't auto-collapse when selection is cleared - let user control it via close button
  }, [nodeSelection.selectedNodeId, panelState]);

  return (
    <div className="app">
      <AppLayout
        header={
          <AppHeader
            ticker={graphData.ticker || ''}
            loading={graphData.loading}
            error={graphData.error}
            onTickerSubmit={handleTickerSubmit}
            stats={stats ? {
              filings_count: stats.filings_count,
              sections_count: stats.sections_count,
              chunks_count: stats.chunks_count,
            } : undefined}
          />
        }
        leftPanelContent={
          <FilterPanel
            filters={filters.filters}
            onFilterChange={handleFilterChange}
            availableFormTypes={availableFormTypes}
            availableYears={availableYears}
            activeFilterCount={filters.getActiveFilterCount()}
          />
        }
        centerPanelContent={
          filteredGraphData.nodes.length > 0 ? (
            <GraphCanvas
              nodes={filteredGraphData.nodes}
              edges={filteredGraphData.edges}
              onNodeClick={handleNodeClick}
              onNodeDoubleClick={handleNodeDoubleClick}
              fitViewOnChange={true}
            />
          ) : (
            <div className="empty-state">
              {graphData.loading ? (
                <div className="loading-message">
                  <div className="spinner"></div>
                  <p>Loading graph data...</p>
                </div>
              ) : graphData.error ? (
                <div className="error-message">
                  <p>Error: {graphData.error}</p>
                </div>
              ) : (
                <div className="empty-message">
                  <p>Enter a ticker symbol to visualize the graph</p>
                </div>
              )}
            </div>
          )
        }
        rightPanelContent={
          <NodeDetailsPanel
            nodeDetails={nodeSelection.nodeDetails}
            loading={nodeSelection.loading}
            error={nodeSelection.error}
            onClose={handlePanelClose}
          />
        }
        footer={
          stats && (
            <div className="stats-footer">
              <div className="stats-footer-content">
                <div className="stat-item">
                  <span className="stat-label">Company:</span>
                  <span className="stat-value">{stats.company.name}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Filings:</span>
                  <span className="stat-value">{stats.filings_count}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Sections:</span>
                  <span className="stat-value">{stats.sections_count}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Chunks:</span>
                  <span className="stat-value">{stats.chunks_count}</span>
                </div>
              </div>
            </div>
          )
        }
      />
    </div>
  );
}

export default App;
