/**
 * Main application component with comprehensive state management.
 * Integrates all components and handles all user interactions.
 */

import React, { useCallback, useMemo, useEffect, useRef } from 'react';
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
import { getNodeType, getExpandNodeType, canExpandNode } from './types/graph';
import { filterNodesByExpandedState } from './utils/graphLayout';
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

  // Apply filters and expanded state to graph data
  const filteredGraphData = useMemo(() => {
    // First filter by expanded state (show only level 0-1 and children of expanded nodes)
    const expandedFiltered = filterNodesByExpandedState(
      graphData.graphData.nodes,
      graphData.graphData.edges,
      graphData.expandedNodes
    );
    
    // Then apply user filters
    return filters.applyFilters(expandedFiltered.nodes, expandedFiltered.edges);
  }, [graphData.graphData, graphData.expandedNodes, filters]);

  // Handle ticker submission
  const handleTickerSubmit = useCallback(async (ticker: string) => {
    // Handle reset (empty ticker)
    if (!ticker.trim()) {
      logger.info('Resetting graph', {}, 'App');
      graphData.resetGraph();
      nodeSelection.clearSelection();
      panelState.collapseRightPanel();
      filters.clearFilters();
      setStats(null);
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
  }, [graphData, nodeSelection, panelState, filters]);

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

  // Handle node double-click (expand via API - loads more data)
  const handleNodeDoubleClick = useCallback(async (nodeId: string, nodeType: 'filing' | 'section') => {
    if (!graphData.ticker) {
      logger.warn('Cannot expand node: no ticker loaded', { nodeId }, 'App');
      return;
    }

    logger.info('Node double-clicked (expand via API)', { nodeId, nodeType }, 'App');
    await graphData.expandNode(nodeId, nodeType, graphData.ticker);
  }, [graphData]);

  // Handle node expand/collapse (toggle visibility of children)
  const handleNodeExpandCollapse = useCallback((nodeId: string, isExpanded: boolean) => {
    logger.info('Node expand/collapse toggled', { nodeId, isExpanded }, 'App');
    
    if (isExpanded) {
      // Expanding: Check if node needs API expansion first, or just show existing children
      const node = graphData.graphData.nodes.find(n => n.id === nodeId);
      const hasChildrenInGraph = graphData.graphData.edges.some(e => e.source === nodeId);
      
      if (!hasChildrenInGraph && node && canExpandNode(node) && graphData.ticker) {
        // Node doesn't have children yet, need to load them via API first
        const expandType = getExpandNodeType(node);
        if (expandType) {
          logger.debug('Expanding node via API first', { nodeId, expandType }, 'App');
          graphData.expandNode(nodeId, expandType, graphData.ticker).then(() => {
            // After API expansion succeeds, toggle UI expansion to show children
            graphData.toggleNodeExpansion(nodeId);
          }).catch(err => {
            logger.warn('API expansion failed', { nodeId, error: err }, 'App');
          });
          return;
        }
      }
      
      // Node already has children in graph, just toggle UI expansion to show them
      graphData.toggleNodeExpansion(nodeId);
    } else {
      // Collapse: hide children
      graphData.toggleNodeExpansion(nodeId);
    }
  }, [graphData]);

  // Handle filter change
  const handleFilterChange = useCallback((newFilters: typeof filters.filters) => {
    logger.debug('Filters changed', newFilters, 'App');
    filters.setFilters(newFilters);
  }, [filters]);

  // Handle panel close
  const handlePanelClose = useCallback(() => {
    logger.debug('Panel closed', {}, 'App');
    // Mark that user manually closed the panel before clearing selection
    // This prevents the useEffect from re-expanding the panel
    userClosedPanelRef.current = true;
    // Clear selection and collapse panel
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
  // IMPORTANT: Don't auto-expand if user manually closed the panel (selectedNodeId cleared)
  const prevSelectedNodeIdRef = useRef<string | null>(null);
  const userClosedPanelRef = useRef(false);
  
  useEffect(() => {
    const wasCleared = prevSelectedNodeIdRef.current !== null && nodeSelection.selectedNodeId === null;
    const isNewSelection = nodeSelection.selectedNodeId !== null && nodeSelection.selectedNodeId !== prevSelectedNodeIdRef.current;
    
    // If selection was cleared, mark that user closed the panel
    if (wasCleared) {
      userClosedPanelRef.current = true;
    }
    
    // Reset the flag when a new node is selected
    if (isNewSelection) {
      userClosedPanelRef.current = false;
    }
    
    // Only expand if:
    // 1. There's a selected node
    // 2. It's a new selection OR panel is collapsed
    // 3. User didn't manually close the panel
    if (nodeSelection.selectedNodeId && (isNewSelection || panelState.panelStates.rightPanel.collapsed)) {
      if (!userClosedPanelRef.current) {
        panelState.expandRightPanel();
        logger.debug('Right panel expanded due to node selection', { 
          nodeId: nodeSelection.selectedNodeId,
          hasDetails: !!nodeSelection.nodeDetails,
          loading: nodeSelection.loading,
          wasCleared,
          isNewSelection,
          userClosedPanel: userClosedPanelRef.current,
        }, 'App');
      } else {
        logger.debug('Skipping panel expansion - user manually closed panel', {
          nodeId: nodeSelection.selectedNodeId,
        }, 'App');
      }
    }
    
    prevSelectedNodeIdRef.current = nodeSelection.selectedNodeId;
    // Don't auto-collapse when selection is cleared - let user control it via close button
  }, [nodeSelection.selectedNodeId, panelState.panelStates.rightPanel.collapsed, nodeSelection, panelState]);

  return (
    <div className="app">
      <AppLayout
        panelState={panelState}
        onRightPanelClose={handlePanelClose}
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
              onNodeExpandCollapse={handleNodeExpandCollapse}
              expandedNodes={graphData.expandedNodes}
              fitViewOnChange={true}
              onNodePositionsChange={graphData.updateNodePositions}
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
