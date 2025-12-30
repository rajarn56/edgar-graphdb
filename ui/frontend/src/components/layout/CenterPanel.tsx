/**
 * Center panel component for graph canvas.
 * Dynamically adjusts based on side panel states.
 */

import React from 'react';
import './CenterPanel.css';

export interface CenterPanelProps {
  /** Panel content */
  children?: React.ReactNode;
}

export default function CenterPanel({ children }: CenterPanelProps) {
  return (
    <div className="center-panel">
      <div className="center-panel-content">
        {children}
      </div>
    </div>
  );
}

