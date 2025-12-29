/**
 * Node details panel component showing properties and relationships.
 */

import React, { useState } from 'react';
import type { NodeDetails as NodeDetailsType } from '../types/graph';
import './NodeDetails.css';

interface NodeDetailsProps {
  nodeDetails: NodeDetailsType | null;
  onClose: () => void;
}

export default function NodeDetails({ nodeDetails, onClose }: NodeDetailsProps) {
  const [expandedContent, setExpandedContent] = useState(false);

  if (!nodeDetails) {
    return null;
  }

  const { node, relationships } = nodeDetails;
  const isChunk = node.labels.includes('Chunk');
  const content = node.properties.content;

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    if (value instanceof Date) return value.toISOString().split('T')[0];
    return String(value);
  };

  const groupedProperties = {
    basic: [] as Array<[string, any]>,
    dates: [] as Array<[string, any]>,
    metadata: [] as Array<[string, any]>,
    other: [] as Array<[string, any]>,
  };

  Object.entries(node.properties).forEach(([key, value]) => {
    if (key === 'content') return; // Handle separately
    
    const lowerKey = key.toLowerCase();
    if (lowerKey.includes('date') || lowerKey.includes('time') || lowerKey.includes('created') || lowerKey.includes('updated')) {
      groupedProperties.dates.push([key, value]);
    } else if (lowerKey.includes('id') || lowerKey.includes('cik') || lowerKey.includes('accession') || lowerKey.includes('ticker') || lowerKey.includes('name')) {
      groupedProperties.basic.push([key, value]);
    } else if (lowerKey.includes('embedding') || lowerKey.includes('metadata') || lowerKey.includes('status')) {
      groupedProperties.metadata.push([key, value]);
    } else {
      groupedProperties.other.push([key, value]);
    }
  });

  return (
    <div className="node-details-panel">
      <div className="node-details-header">
        <h2>Node Details</h2>
        <button className="close-button" onClick={onClose}>×</button>
      </div>
      
      <div className="node-details-content">
        <div className="node-type-badge">
          {node.labels.join(', ')}
        </div>

        <div className="properties-section">
          <h3>Properties</h3>
          
          {groupedProperties.basic.length > 0 && (
            <div className="property-group">
              <h4>Basic Information</h4>
              <table className="properties-table">
                <tbody>
                  {groupedProperties.basic.map(([key, value]) => (
                    <tr key={key}>
                      <td className="property-key">{key}</td>
                      <td className="property-value">{formatValue(value)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {groupedProperties.dates.length > 0 && (
            <div className="property-group">
              <h4>Dates</h4>
              <table className="properties-table">
                <tbody>
                  {groupedProperties.dates.map(([key, value]) => (
                    <tr key={key}>
                      <td className="property-key">{key}</td>
                      <td className="property-value">{formatValue(value)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {groupedProperties.other.length > 0 && (
            <div className="property-group">
              <h4>Other Properties</h4>
              <table className="properties-table">
                <tbody>
                  {groupedProperties.other.map(([key, value]) => (
                    <tr key={key}>
                      <td className="property-key">{key}</td>
                      <td className="property-value">{formatValue(value)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {groupedProperties.metadata.length > 0 && (
            <div className="property-group">
              <h4>Metadata</h4>
              <table className="properties-table">
                <tbody>
                  {groupedProperties.metadata.map(([key, value]) => {
                    if (key.toLowerCase().includes('embedding')) {
                      return (
                        <tr key={key}>
                          <td className="property-key">{key}</td>
                          <td className="property-value">
                            {Array.isArray(value) ? `[${value.length} dimensions]` : formatValue(value)}
                          </td>
                        </tr>
                      );
                    }
                    return (
                      <tr key={key}>
                        <td className="property-key">{key}</td>
                        <td className="property-value">{formatValue(value)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {isChunk && content && (
            <div className="property-group">
              <h4>Content</h4>
              <div className="content-viewer">
                <div className={`content-text ${expandedContent ? 'expanded' : 'collapsed'}`}>
                  {content}
                </div>
                {content.length > 500 && (
                  <button
                    className="expand-button"
                    onClick={() => setExpandedContent(!expandedContent)}
                  >
                    {expandedContent ? 'Collapse' : 'Expand'}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        {relationships.length > 0 && (
          <div className="relationships-section">
            <h3>Relationships ({relationships.length})</h3>
            <table className="relationships-table">
              <thead>
                <tr>
                  <th>Direction</th>
                  <th>Type</th>
                  <th>Connected Node</th>
                </tr>
              </thead>
              <tbody>
                {relationships.map((rel, index) => (
                  <tr key={index}>
                    <td className={`direction-badge ${rel.direction}`}>
                      {rel.direction}
                    </td>
                    <td>{rel.type}</td>
                    <td>{rel.direction === 'incoming' ? rel.source : rel.target}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

