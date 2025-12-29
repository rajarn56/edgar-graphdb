/**
 * Main application component.
 */

import React, { useState, useCallback, useMemo } from 'react';
import GraphCanvas from './components/GraphCanvas';
import NodeDetails from './components/NodeDetails';
import TickerInput from './components/TickerInput';
import FilterPanel, { FilterOptions } from './components/FilterPanel';
import { graphApi, tickerApi } from './services/api';
import type { GraphData, NodeDetails as NodeDetailsType, GraphStats } from './types/graph';
import { applyLayout } from './utils/graphLayout';
import { logger } from './utils/logger';
import './App.css';

function App() {
  const [ticker, setTicker] = useState<string>('');
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [selectedNodeDetails, setSelectedNodeDetails] = useState<NodeDetailsType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [filters, setFilters] = useState<FilterOptions>({ nodeTypes: ['Company', 'Filing', 'Section', 'Chunk'] });
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  // Log app initialization
  React.useEffect(() => {
    logger.info('App initialized', { 
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      environment: import.meta.env.MODE 
    });
  }, []);

  // Extract available form types and years from graph data
  const availableFormTypes = useMemo(() => {
    const formTypes = new Set<string>();
    graphData.nodes.forEach(node => {
      if (node.labels.includes('Filing') && node.properties.form_type) {
        formTypes.add(node.properties.form_type);
      }
    });
    return Array.from(formTypes).sort();
  }, [graphData]);

  const availableYears = useMemo(() => {
    const years = new Set<number>();
    graphData.nodes.forEach(node => {
      if (node.properties.fiscal_year) {
        years.add(node.properties.fiscal_year);
      }
    });
    return Array.from(years).sort((a, b) => b - a);
  }, [graphData]);

  const handleTickerSubmit = useCallback(async (newTicker: string) => {
    logger.info('Ticker submitted', { ticker: newTicker });
    setTicker(newTicker);
    setLoading(true);
    setError(null);
    setSelectedNodeDetails(null);
    setExpandedNodes(new Set());

    try {
      // Fetch graph data
      logger.debug('Fetching graph data', { ticker: newTicker });
      const data = await graphApi.getGraph(newTicker);
      logger.info('Graph data received', { 
        nodeCount: data.nodes.length, 
        edgeCount: data.edges.length 
      });
      
      // Apply layout
      const nodesWithLayout = applyLayout(data.nodes, data.edges);
      setGraphData({ nodes: nodesWithLayout, edges: data.edges });
      logger.debug('Layout applied to graph');

      // Fetch stats
      try {
        logger.debug('Fetching stats', { ticker: newTicker });
        const statsData = await tickerApi.getStats(newTicker);
        setStats(statsData);
        logger.info('Stats received', statsData);
      } catch (err: any) {
        logger.warn('Failed to fetch stats', { ticker: newTicker, error: err });
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load graph data';
      logger.error('Failed to load graph', { ticker: newTicker, error: errorMessage }, err);
      setError(errorMessage);
      setGraphData({ nodes: [], edges: [] });
    } finally {
      setLoading(false);
    }
  }, []);

  const handleNodeClick = useCallback(async (nodeId: string, labels: string[]) => {
    logger.debug('Node clicked', { nodeId, labels });
    try {
      const details = await graphApi.getNodeDetails(nodeId, labels);
      logger.info('Node details received', { 
        nodeId, 
        relationshipCount: details.relationships.length 
      });
      setSelectedNodeDetails(details);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load node details';
      logger.error('Failed to fetch node details', { nodeId, labels, error: errorMessage }, err);
      setError(errorMessage);
    }
  }, []);

  const handleNodeExpand = useCallback(async (nodeId: string, nodeType: 'filing' | 'section') => {
    if (expandedNodes.has(nodeId)) {
      logger.debug('Node already expanded', { nodeId });
      return; // Already expanded
    }

    logger.info('Expanding node', { nodeId, nodeType, ticker });
    try {
      const expandedData = await graphApi.expandNode(ticker, nodeId, nodeType);
      logger.info('Node expanded', { 
        nodeId, 
        newNodeCount: expandedData.nodes.length, 
        newEdgeCount: expandedData.edges.length 
      });
      
      // Merge with existing graph data
      const existingNodeIds = new Set(graphData.nodes.map(n => n.id));
      const newNodes = expandedData.nodes.filter(n => !existingNodeIds.has(n.id));
      const newEdges = expandedData.edges.filter(e => {
        const existingEdgeIds = new Set(
          graphData.edges.map(edge => `${edge.source}-${edge.target}`)
        );
        return !existingEdgeIds.has(`${e.source}-${e.target}`);
      });

      const updatedNodes = [...graphData.nodes, ...newNodes];
      const updatedEdges = [...graphData.edges, ...newEdges];

      // Apply layout to updated graph
      const nodesWithLayout = applyLayout(updatedNodes, updatedEdges);
      
      setGraphData({ nodes: nodesWithLayout, edges: updatedEdges });
      setExpandedNodes(prev => new Set([...prev, nodeId]));
      logger.debug('Graph updated after expansion', { 
        totalNodes: nodesWithLayout.length, 
        totalEdges: updatedEdges.length 
      });
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to expand node';
      logger.error('Failed to expand node', { nodeId, nodeType, error: errorMessage }, err);
      setError(errorMessage);
    }
  }, [ticker, graphData, expandedNodes]);

  const handleFilterChange = useCallback((newFilters: FilterOptions) => {
    logger.debug('Filters changed', newFilters);
    setFilters(newFilters);
    // Filter logic would be applied here if needed
    // For now, we just store the filters
  }, []);

  // Apply filters to graph data
  const filteredGraphData = useMemo(() => {
    if (!filters.nodeTypes.length) {
      return { nodes: [], edges: [] };
    }

    const filteredNodes = graphData.nodes.filter(node => {
      return node.labels.some(label => filters.nodeTypes.includes(label));
    });

    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = graphData.edges.filter(edge => {
      return filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target);
    });

    // Apply form type and fiscal year filters
    let finalNodes = filteredNodes;
    if (filters.formType) {
      finalNodes = finalNodes.filter(node => {
        if (node.labels.includes('Filing')) {
          return node.properties.form_type === filters.formType;
        }
        // Keep non-filing nodes
        return true;
      });
    }

    if (filters.fiscalYear) {
      finalNodes = finalNodes.filter(node => {
        if (node.properties.fiscal_year !== undefined) {
          return node.properties.fiscal_year === filters.fiscalYear;
        }
        // Keep nodes without fiscal_year
        return true;
      });
    }

    const finalNodeIds = new Set(finalNodes.map(n => n.id));
    const finalEdges = filteredEdges.filter(edge => {
      return finalNodeIds.has(edge.source) && finalNodeIds.has(edge.target);
    });

    return { nodes: finalNodes, edges: finalEdges };
  }, [graphData, filters]);

  return (
    <div className="app">
      <div className="app-header">
        <TickerInput
          onSubmit={handleTickerSubmit}
          loading={loading}
          error={error}
        />
      </div>

      <div className="app-body">
        <FilterPanel
          onFilterChange={handleFilterChange}
          availableFormTypes={availableFormTypes}
          availableYears={availableYears}
        />

        <div className="app-main">
          <div className="graph-container">
            {graphData.nodes.length > 0 ? (
              <GraphCanvas
                nodes={filteredGraphData.nodes}
                edges={filteredGraphData.edges}
                onNodeClick={handleNodeClick}
                onNodeExpand={handleNodeExpand}
              />
            ) : (
              <div className="empty-state">
                {loading ? (
                  <div className="loading-message">Loading graph data...</div>
                ) : (
                  <div className="empty-message">
                    Enter a ticker symbol to visualize the graph
                  </div>
                )}
              </div>
            )}
          </div>

          {stats && (
            <div className="stats-panel">
              <h3>Statistics</h3>
              <div className="stats-content">
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
                <div className="stat-item">
                  <span className="stat-label">Financial Statements:</span>
                  <span className="stat-value">{stats.financial_statements_count}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <NodeDetails
          nodeDetails={selectedNodeDetails}
          onClose={() => setSelectedNodeDetails(null)}
        />
      </div>
    </div>
  );
}

export default App;

