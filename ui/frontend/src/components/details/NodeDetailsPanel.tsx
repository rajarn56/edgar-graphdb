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
  if (loading) {
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
  const hasContent = isChunk && node.properties.content;

  logger.debug('Rendering node details', { 
    nodeId: node.id, 
    labels: node.labels,
    hasContent 
  }, 'NodeDetailsPanel');

  return (
    <div className="node-details-panel">
      {/* Node type badge */}
      <div className="node-details-header-badge">
        <span className="node-type-badge">
          {node.labels.join(', ')}
        </span>
      </div>

      {/* Properties section */}
      <PropertiesView node={node} />

      {/* Content section (for Chunk nodes) */}
      {hasContent && (
        <ContentView content={node.properties.content} />
      )}

      {/* Relationships section */}
      {nodeDetails.relationships.length > 0 && (
        <RelationshipsView relationships={nodeDetails.relationships} />
      )}
    </div>
  );
}

