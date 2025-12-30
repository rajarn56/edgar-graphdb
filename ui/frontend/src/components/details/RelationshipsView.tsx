/**
 * Relationships view component to display node relationships with navigation.
 */

import React from 'react';
import type { NodeDetails } from '../../types/graph';
import { logger } from '../../utils/logger';
import './RelationshipsView.css';

export interface RelationshipsViewProps {
  /** Relationships to display */
  relationships: NodeDetails['relationships'];
  /** Callback when a relationship node is clicked */
  onNodeClick?: (nodeId: string) => void;
}

export default function RelationshipsView({ 
  relationships, 
  onNodeClick 
}: RelationshipsViewProps) {
  const handleNodeClick = (nodeId: string) => {
    logger.debug('Relationship node clicked', { nodeId }, 'RelationshipsView');
    if (onNodeClick) {
      onNodeClick(nodeId);
    }
  };

  if (relationships.length === 0) {
    return (
      <div className="relationships-view">
        <h3 className="relationships-view-title">Relationships</h3>
        <div className="relationships-empty">
          <p>No relationships found for this node.</p>
        </div>
      </div>
    );
  }

  // Group by direction
  const incoming = relationships.filter(r => r.direction === 'incoming');
  const outgoing = relationships.filter(r => r.direction === 'outgoing');

  return (
    <div className="relationships-view">
      <h3 className="relationships-view-title">
        Relationships ({relationships.length})
      </h3>

      {incoming.length > 0 && (
        <div className="relationships-section">
          <h4 className="relationships-section-title">
            Incoming ({incoming.length})
          </h4>
          <div className="relationships-list">
            {incoming.map((rel, index) => (
              <div
                key={`incoming-${index}`}
                className="relationship-item"
                onClick={() => handleNodeClick(rel.source)}
              >
                <span className="relationship-type">{rel.type}</span>
                <span className="relationship-node-id">{rel.source}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {outgoing.length > 0 && (
        <div className="relationships-section">
          <h4 className="relationships-section-title">
            Outgoing ({outgoing.length})
          </h4>
          <div className="relationships-list">
            {outgoing.map((rel, index) => (
              <div
                key={`outgoing-${index}`}
                className="relationship-item"
                onClick={() => handleNodeClick(rel.target)}
              >
                <span className="relationship-type">{rel.type}</span>
                <span className="relationship-node-id">{rel.target}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

