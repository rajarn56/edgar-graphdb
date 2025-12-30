/**
 * Properties view component with organized property display and formatting.
 */

import React, { useState } from 'react';
import type { GraphNode } from '../../types/graph';
import { formatValue } from '../../utils/formatters';
import { logger } from '../../utils/logger';
import './PropertiesView.css';

export interface PropertiesViewProps {
  /** Node to display properties for */
  node: GraphNode;
}

interface PropertyGroup {
  name: string;
  properties: Array<[string, any]>;
  expanded: boolean;
}

export default function PropertiesView({ node }: PropertiesViewProps) {
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['basic', 'dates']));

  const groupedProperties: Record<string, PropertyGroup> = {
    basic: {
      name: 'Basic Information',
      properties: [],
      expanded: expandedGroups.has('basic'),
    },
    dates: {
      name: 'Dates',
      properties: [],
      expanded: expandedGroups.has('dates'),
    },
    metadata: {
      name: 'Metadata',
      properties: [],
      expanded: expandedGroups.has('metadata'),
    },
    other: {
      name: 'Other Properties',
      properties: [],
      expanded: expandedGroups.has('other'),
    },
  };

  // Group properties
  Object.entries(node.properties).forEach(([key, value]) => {
    if (key === 'content') return; // Handle separately in ContentView

    const lowerKey = key.toLowerCase();
    if (lowerKey.includes('date') || lowerKey.includes('time') || lowerKey.includes('created') || lowerKey.includes('updated')) {
      groupedProperties.dates.properties.push([key, value]);
    } else if (lowerKey.includes('id') || lowerKey.includes('cik') || lowerKey.includes('accession') || lowerKey.includes('ticker') || lowerKey.includes('name')) {
      groupedProperties.basic.properties.push([key, value]);
    } else if (lowerKey.includes('embedding') || lowerKey.includes('metadata') || lowerKey.includes('status')) {
      groupedProperties.metadata.properties.push([key, value]);
    } else {
      groupedProperties.other.properties.push([key, value]);
    }
  });

  const toggleGroup = (groupName: string) => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(groupName)) {
        newSet.delete(groupName);
      } else {
        newSet.add(groupName);
      }
      logger.debug('Property group toggled', { groupName, expanded: newSet.has(groupName) }, 'PropertiesView');
      return newSet;
    });
  };

  const copyToClipboard = async (value: any) => {
    try {
      const text = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
      await navigator.clipboard.writeText(text);
      logger.debug('Value copied to clipboard', { valueType: typeof value }, 'PropertiesView');
    } catch (err) {
      logger.warn('Failed to copy to clipboard', { error: err }, 'PropertiesView');
    }
  };

  return (
    <div className="properties-view">
      <h3 className="properties-view-title">Properties</h3>

      {Object.entries(groupedProperties).map(([groupKey, group]) => {
        if (group.properties.length === 0) return null;

        return (
          <div key={groupKey} className="property-group">
            <button
              className="property-group-header"
              onClick={() => toggleGroup(groupKey)}
              aria-expanded={expandedGroups.has(groupKey)}
            >
              <span className="property-group-name">{group.name}</span>
              <span className="property-group-count">({group.properties.length})</span>
              <svg
                className={`property-group-icon ${expandedGroups.has(groupKey) ? 'expanded' : ''}`}
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
              >
                <path
                  d="M4 6L8 10L12 6"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>

            {expandedGroups.has(groupKey) && (
              <div className="property-group-content">
                <table className="properties-table">
                  <tbody>
                    {group.properties.map(([key, value]) => (
                      <tr key={key} className="property-row">
                        <td className="property-key">
                          <span>{key}</span>
                        </td>
                        <td className="property-value">
                          <span>{formatValue(value)}</span>
                          <button
                            className="property-copy-button"
                            onClick={() => copyToClipboard(value)}
                            title="Copy to clipboard"
                            aria-label={`Copy ${key} to clipboard`}
                          >
                            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                              <path
                                d="M4 4V2C4 1.44772 4.44772 1 5 1H12C12.5523 1 13 1.44772 13 2V9C13 9.55228 12.5523 10 12 10H10V12C10 12.5523 9.55228 13 9 13H2C1.44772 13 1 12.5523 1 12V5C1 4.44772 1.44772 4 2 4H4Z"
                                stroke="currentColor"
                                strokeWidth="1.5"
                                fill="none"
                              />
                            </svg>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

