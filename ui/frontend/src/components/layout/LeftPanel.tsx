/**
 * Left panel component for filters (collapsible).
 */

import React from 'react';
import { logger } from '../../utils/logger';
import './LeftPanel.css';

export interface LeftPanelProps {
  /** Whether the panel is collapsed */
  collapsed: boolean;
  /** Toggle collapse/expand */
  onToggle: () => void;
  /** Panel content */
  children?: React.ReactNode;
}

export default function LeftPanel({ collapsed, onToggle, children }: LeftPanelProps) {
  const handleToggle = () => {
    logger.debug('Left panel toggle clicked', { collapsed: !collapsed }, 'LeftPanel');
    onToggle();
  };

  return (
    <div className={`left-panel ${collapsed ? 'collapsed' : ''}`}>
      {/* Toggle button */}
      <button
        className="left-panel-toggle"
        onClick={handleToggle}
        aria-label={collapsed ? 'Expand left panel' : 'Collapse left panel'}
        title={collapsed ? 'Expand filters' : 'Collapse filters'}
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={collapsed ? 'rotate-180' : ''}
        >
          <path
            d="M6 12L10 8L6 4"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* Panel content */}
      <div className="left-panel-content">
        {children}
      </div>
    </div>
  );
}

