/**
 * Main node details panel component with proper scrolling and close functionality.
 */

import React from 'react';
import type { NodeDetails } from '../../types/graph';
import PropertiesView from './PropertiesView';
import ContentView from './ContentView';
import RelationshipsView from './RelationshipsView';
import { logger } from '../../utils/logger';
import './NodeDetailsPanel.css';

export interface NodeDetailsPanelProps {
  /** Node details to display */
  nodeDetails: NodeDetails | null;
  /** Whether details are loading */
  loading?: boolean;
  /** Error message */
  error?: string | null;
  /** Callback when panel is closed */
  onClose?: () => void;
}

export default function NodeDetailsPanel({
  nodeDetails,
  loading = false,
  error = null,
  onClose,
}: NodeDetailsPanelProps) {
  // Debug logging
  logger.debug('NodeDetailsPanel render', { 
    hasNodeDetails: !!nodeDetails,
    loading,
    error,
    nodeId: nodeDetails?.node?.id,
  }, 'NodeDetailsPanel');

  if (loading) {
    logger.debug('NodeDetailsPanel showing loading state', {}, 'NodeDetailsPanel');
    return (
      <div className="node-details-panel">
        <div className="node-details-loading">
          <div className="spinner"></div>
          <p>Loading node details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    logger.warn('NodeDetailsPanel showing error state', { error }, 'NodeDetailsPanel');
    return (
      <div className="node-details-panel">
        <div className="node-details-error">
          <p>Error loading details</p>
          <p className="error-message">{error}</p>
        </div>
      </div>
    );
  }

  if (!nodeDetails) {
    logger.debug('NodeDetailsPanel showing empty state', {}, 'NodeDetailsPanel');
    return (
      <div className="node-details-panel">
        <div className="node-details-empty">
          <p>Select a node to view details</p>
        </div>
      </div>
    );
  }

  const { node } = nodeDetails;
  const isChunk = node.labels.includes('Chunk');
  const hasContent = isChunk && node.properties && node.properties.content;
  const hasRelationships = nodeDetails.relationships && nodeDetails.relationships.length > 0;
  const hasProperties = node.properties && Object.keys(node.properties).length > 0;

  logger.debug('Rendering node details content', { 
    nodeId: node.id, 
    labels: node.labels,
    hasContent,
    hasRelationships,
    hasProperties,
    propertyCount: node.properties ? Object.keys(node.properties).length : 0,
  }, 'NodeDetailsPanel');

  return (
    <div className="node-details-panel">
      {/* Node type badge */}
      <div className="node-details-header-badge">
        <span className="node-type-badge">
          {node.labels.join(', ')}
        </span>
      </div>

      {/* Properties section - always show, even if empty */}
      {hasProperties ? (
        <PropertiesView node={node} />
      ) : (
        <div className="properties-view">
          <h3 className="properties-view-title">Properties</h3>
          <div className="properties-empty">
            <p>No properties available for this node.</p>
          </div>
        </div>
      )}

      {/* Content section (for Chunk nodes) */}
      {hasContent && (
        <ContentView content={node.properties.content} />
      )}

      {/* Relationships section - always show */}
      <RelationshipsView relationships={nodeDetails.relationships || []} />
    </div>
  );
}

