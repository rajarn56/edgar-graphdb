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
  const handleNodeClick = useCallback(async (nodeId: string, labels: string[]) => {
    logger.info('Node clicked in App', { nodeId, labels }, 'App');
    
    // Find the graph node to use its properties as fallback
    const graphNode = graphData.graphData.nodes.find(n => n.id === nodeId);
    logger.debug('Graph node found for click', {
      nodeId,
      found: !!graphNode,
      hasProperties: !!graphNode?.properties,
      propertyCount: graphNode?.properties ? Object.keys(graphNode.properties).length : 0,
    }, 'App');
    
    // Expand panel FIRST and wait a tick to ensure state updates
    logger.debug('Expanding right panel', { 
      nodeId,
      currentCollapsed: panelState.panelStates.rightPanel.collapsed,
      currentVisible: panelState.panelStates.rightPanel.visible,
    }, 'App');
    
    panelState.expandRightPanel();
    
    // Use requestAnimationFrame to ensure DOM updates after state change
    requestAnimationFrame(() => {
      logger.debug('Panel expansion state after RAF', {
        nodeId,
        panelCollapsed: panelState.panelStates.rightPanel.collapsed,
        panelVisible: panelState.panelStates.rightPanel.visible,
        panelWidth: panelState.getRightPanelWidth(),
      }, 'App');
    });
    
    // Then select the node (this will trigger API call)
    logger.debug('Calling selectNode', { nodeId, labels }, 'App');
    try {
      await nodeSelection.selectNode(nodeId, labels, graphNode);
      logger.info('Node selection completed', { 
        nodeId,
        hasDetails: !!nodeSelection.nodeDetails,
        loading: nodeSelection.loading,
        error: nodeSelection.error,
      }, 'App');
    } catch (err: any) {
      logger.error('Error in selectNode', { 
        nodeId, 
        error: err?.message || err,
        stack: err?.stack 
      }, 'App', err);
      // Panel should still be expanded even if API call fails
    }
    
    // Verify panel state after a short delay to ensure state has updated
    setTimeout(() => {
      const panelWidth = panelState.getRightPanelWidth();
      logger.debug('Node click handling completed', {
        nodeId,
        selectedNodeId: nodeSelection.selectedNodeId,
        panelCollapsed: panelState.panelStates.rightPanel.collapsed,
        panelVisible: panelState.panelStates.rightPanel.visible,
        panelWidth: panelWidth,
        hasNodeDetails: !!nodeSelection.nodeDetails,
      }, 'App');
      
      // If panel width is still 0, force expansion again
      if (panelWidth === 0 && !panelState.panelStates.rightPanel.collapsed) {
        logger.warn('Panel width is 0 but not collapsed, forcing expansion', { nodeId }, 'App');
        panelState.expandRightPanel();
      }
    }, 200);
  }, [nodeSelection, panelState, graphData]);

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
  // NOTE: This effect is intentionally minimal - handleNodeClick already expands the panel
  // This is a safety net for programmatic node selection, but we guard against duplicate calls
  useEffect(() => {
    if (nodeSelection.selectedNodeId) {
      // Only expand if panel is currently collapsed (avoid duplicate calls)
      if (panelState.panelStates.rightPanel.collapsed) {
        panelState.expandRightPanel();
        logger.debug('Right panel expanded due to node selection', { 
          nodeId: nodeSelection.selectedNodeId,
          hasDetails: !!nodeSelection.nodeDetails,
          loading: nodeSelection.loading 
        }, 'App');
      }
    }
    // Don't auto-collapse when selection is cleared - let user control it via close button
  }, [nodeSelection.selectedNodeId, panelState]);

  return (
    <div className="app">
      <AppLayout
        panelState={panelState}
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
