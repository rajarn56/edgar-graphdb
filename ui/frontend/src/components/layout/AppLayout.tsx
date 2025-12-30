/**
 * Main application layout component with three-panel structure.
 * Uses CSS Grid for proper space management (no fixed positioning).
 */

import React, { createContext } from 'react';
import type { UsePanelStateReturn } from '../../hooks/usePanelState';
import { DEFAULT_LAYOUT_CONFIG } from '../../types/ui';
import { logger } from '../../utils/logger';
import LeftPanel from './LeftPanel';
import CenterPanel from './CenterPanel';
import RightPanel from './RightPanel';
import AppHeader from '../header/AppHeader';
import './AppLayout.css';

export interface AppLayoutProps {
  /** Header content */
  header?: React.ReactNode;
  /** Left panel content (filters) */
  leftPanelContent?: React.ReactNode;
  /** Center panel content (graph canvas) */
  centerPanelContent?: React.ReactNode;
  /** Right panel content (node details) */
  rightPanelContent?: React.ReactNode;
  /** Footer/stats bar content */
  footer?: React.ReactNode;
  /** Custom layout configuration */
  layoutConfig?: typeof DEFAULT_LAYOUT_CONFIG;
  /** Panel state management (required to avoid duplicate instances) */
  panelState: UsePanelStateReturn;
}

export default function AppLayout({
  header,
  leftPanelContent,
  centerPanelContent,
  rightPanelContent,
  footer,
  layoutConfig = DEFAULT_LAYOUT_CONFIG,
  panelState,
}: AppLayoutProps) {
  const leftWidth = panelState.getLeftPanelWidth();
  const rightWidth = panelState.getRightPanelWidth();
  
  // Log layout state changes
  React.useEffect(() => {
    logger.debug('AppLayout state', {
      leftWidth,
      rightWidth,
      leftPanelCollapsed: panelState.panelStates.leftPanel.collapsed,
      rightPanelCollapsed: panelState.panelStates.rightPanel.collapsed,
      rightPanelVisible: panelState.panelStates.rightPanel.visible,
      hasRightPanelContent: !!rightPanelContent,
    }, 'AppLayout');
  }, [leftWidth, rightWidth, panelState.panelStates, rightPanelContent]);

  return (
    <div className="app-layout">
      {/* Header */}
      <div className="app-layout-header" style={{ height: `${layoutConfig.headerHeight}px` }}>
        {header || <AppHeader />}
      </div>

      {/* Main content area */}
      <div className="app-layout-body">
        {/* Left Panel */}
        <div
          className={`app-layout-left-panel ${panelState.panelStates.leftPanel.collapsed ? 'collapsed' : ''}`}
          style={{
            width: `${leftWidth}px`,
            minWidth: leftWidth > 0 ? `${layoutConfig.leftPanel.minWidth}px` : '0',
            maxWidth: `${layoutConfig.leftPanel.maxWidth}px`,
          }}
        >
          <LeftPanel
            collapsed={panelState.panelStates.leftPanel.collapsed}
            onToggle={panelState.toggleLeftPanel}
          >
            {leftPanelContent}
          </LeftPanel>
        </div>

        {/* Center Panel */}
        <div
          className="app-layout-center-panel"
          style={{
            marginLeft: `${leftWidth}px`,
            marginRight: `${rightWidth}px`,
          }}
        >
          <CenterPanel>{centerPanelContent}</CenterPanel>
        </div>

        {/* Right Panel */}
        <div
          className={`app-layout-right-panel ${panelState.panelStates.rightPanel.collapsed ? 'collapsed' : ''}`}
          style={{
            width: `${rightWidth}px`,
            minWidth: rightWidth > 0 ? `${layoutConfig.rightPanel.minWidth}px` : '0',
            maxWidth: `${layoutConfig.rightPanel.maxWidth}px`,
          }}
        >
          <RightPanel
            collapsed={panelState.panelStates.rightPanel.collapsed}
            onToggle={panelState.toggleRightPanel}
            onClose={panelState.collapseRightPanel}
          >
            {rightPanelContent}
          </RightPanel>
        </div>
      </div>

      {/* Footer/Stats Bar */}
      {footer && (
        <div className="app-layout-footer" style={{ height: `${layoutConfig.footerHeight}px` }}>
          {footer}
        </div>
      )}

    </div>
  );
}

// Create context for panel state (for components that need it)
export const PanelStateContext = createContext<UsePanelStateReturn | null>(null);

// Hook to access panel state from context
export function usePanelStateContext(): UsePanelStateReturn {
  const context = React.useContext(PanelStateContext);
  if (!context) {
    throw new Error('usePanelStateContext must be used within AppLayout');
  }
  return context;
}

