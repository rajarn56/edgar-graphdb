/**
 * Right panel component for node details (collapsible).
 * Properly releases space when closed.
 */

import React from 'react';
import { logger } from '../../utils/logger';
import './RightPanel.css';

export interface RightPanelProps {
  /** Whether the panel is collapsed */
  collapsed: boolean;
  /** Toggle collapse/expand */
  onToggle: () => void;
  /** Close panel (collapse and hide) */
  onClose: () => void;
  /** Panel content */
  children?: React.ReactNode;
  /** Panel title */
  title?: string;
}

export default function RightPanel({
  collapsed,
  onToggle,
  onClose,
  children,
  title = 'Node Details',
}: RightPanelProps) {
  // Log panel state changes (only when collapsed state actually changes, not on every render)
  const prevCollapsedRef = React.useRef(collapsed);
  React.useEffect(() => {
    if (prevCollapsedRef.current !== collapsed) {
      logger.debug('RightPanel state changed', {
        collapsed,
        hasChildren: !!children,
        childrenType: children ? typeof children : 'null',
        title,
      }, 'RightPanel');
      prevCollapsedRef.current = collapsed;
    }
  }, [collapsed, children, title]);

  const handleToggle = () => {
    logger.info('Right panel toggle clicked', { 
      currentCollapsed: collapsed,
      newCollapsed: !collapsed,
    }, 'RightPanel');
    onToggle();
  };

  const handleClose = () => {
    logger.info('Right panel close clicked', { collapsed }, 'RightPanel');
    onClose();
  };

  // Always render the panel structure - don't return null
  // Content will be hidden via CSS when collapsed, but structure remains for proper state management
  return (
    <div className={`right-panel ${collapsed ? 'collapsed' : ''}`}>
      {/* Header with title and controls */}
      <div className="right-panel-header">
        <h2 className="right-panel-title">{title}</h2>
        <div className="right-panel-controls">
          <button
            className="right-panel-toggle"
            onClick={handleToggle}
            aria-label={collapsed ? 'Expand right panel' : 'Collapse right panel'}
            title={collapsed ? 'Expand details' : 'Collapse details'}
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className={collapsed ? '' : 'rotate-180'}
            >
              <path
                d="M10 12L6 8L10 4"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <button
            className="right-panel-close"
            onClick={handleClose}
            aria-label="Close panel"
            title="Close details"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M12 4L4 12M4 4L12 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Panel content - always render but hide via CSS when collapsed */}
      <div className={`right-panel-content ${collapsed ? 'collapsed' : ''}`}>
        {children}
      </div>
    </div>
  );
}

