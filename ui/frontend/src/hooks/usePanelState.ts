/**
 * Hook for managing panel visibility and collapse states.
 */

import { useState, useCallback, useMemo } from 'react';
import type { AppPanelStates, PanelState, LayoutConfig } from '../types/ui';
import { DEFAULT_LAYOUT_CONFIG } from '../types/ui';
import { logger } from '../utils/logger';

export interface UsePanelStateReturn {
  /** Current panel states */
  panelStates: AppPanelStates;
  /** Toggle left panel visibility */
  toggleLeftPanel: () => void;
  /** Toggle right panel visibility */
  toggleRightPanel: () => void;
  /** Collapse left panel */
  collapseLeftPanel: () => void;
  /** Expand left panel */
  expandLeftPanel: () => void;
  /** Collapse right panel */
  collapseRightPanel: () => void;
  /** Expand right panel */
  expandRightPanel: () => void;
  /** Set left panel state */
  setLeftPanelState: (state: Partial<PanelState>) => void;
  /** Set right panel state */
  setRightPanelState: (state: Partial<PanelState>) => void;
  /** Get left panel width */
  getLeftPanelWidth: () => number;
  /** Get right panel width */
  getRightPanelWidth: () => number;
  /** Reset all panels to default state */
  resetPanels: () => void;
}

export function usePanelState(
  config: LayoutConfig = DEFAULT_LAYOUT_CONFIG
): UsePanelStateReturn {
  const [leftPanelState, setLeftPanelStateInternal] = useState<PanelState>({
    visible: true,
    collapsed: false,
    expandedWidth: config.leftPanel.defaultWidth,
  });

  const [rightPanelState, setRightPanelStateInternal] = useState<PanelState>({
    visible: true, // Start as visible so content can render
    collapsed: true, // But collapsed initially
    expandedWidth: config.rightPanel.defaultWidth,
  });

  const toggleLeftPanel = useCallback(() => {
    setLeftPanelStateInternal(prev => {
      const newState = {
        ...prev,
        collapsed: !prev.collapsed,
        visible: true,
      };
      logger.debug('Left panel toggled', { collapsed: newState.collapsed }, 'usePanelState');
      return newState;
    });
  }, []);

  const toggleRightPanel = useCallback(() => {
    setRightPanelStateInternal(prev => {
      const newState = {
        ...prev,
        collapsed: !prev.collapsed,
        visible: !prev.collapsed || prev.visible, // If collapsing, keep visible; if expanding, make visible
      };
      logger.debug('Right panel toggled', { collapsed: newState.collapsed }, 'usePanelState');
      return newState;
    });
  }, []);

  const collapseLeftPanel = useCallback(() => {
    setLeftPanelStateInternal(prev => ({
      ...prev,
      collapsed: true,
    }));
    logger.debug('Left panel collapsed', {}, 'usePanelState');
  }, []);

  const expandLeftPanel = useCallback(() => {
    setLeftPanelStateInternal(prev => ({
      ...prev,
      collapsed: false,
      visible: true,
    }));
    logger.debug('Left panel expanded', {}, 'usePanelState');
  }, []);

  const collapseRightPanel = useCallback(() => {
    setRightPanelStateInternal(prev => ({
      ...prev,
      collapsed: true,
      visible: true, // Keep visible so content can be rendered
    }));
    logger.debug('Right panel collapsed', {}, 'usePanelState');
  }, []);

  const expandRightPanel = useCallback(() => {
    setRightPanelStateInternal(prev => {
      const newState = {
        ...prev,
        collapsed: false,
        visible: true,
      };
      logger.info('Right panel expanded', {
        previousState: {
          collapsed: prev.collapsed,
          visible: prev.visible,
          expandedWidth: prev.expandedWidth,
        },
        newState: {
          collapsed: newState.collapsed,
          visible: newState.visible,
          expandedWidth: newState.expandedWidth,
        },
      }, 'usePanelState');
      return newState;
    });
  }, []);

  const setLeftPanelState = useCallback((state: Partial<PanelState>) => {
    setLeftPanelStateInternal(prev => {
      const newState = { ...prev, ...state };
      logger.debug('Left panel state updated', newState, 'usePanelState');
      return newState;
    });
  }, []);

  const setRightPanelState = useCallback((state: Partial<PanelState>) => {
    setRightPanelStateInternal(prev => {
      const newState = { ...prev, ...state };
      logger.debug('Right panel state updated', newState, 'usePanelState');
      return newState;
    });
  }, []);

  const getLeftPanelWidth = useCallback((): number => {
    if (leftPanelState.collapsed || !leftPanelState.visible) {
      return 0;
    }
    return leftPanelState.expandedWidth;
  }, [leftPanelState]);

  const getRightPanelWidth = useCallback((): number => {
    // If collapsed, return 0 (panel is hidden)
    if (rightPanelState.collapsed) {
      logger.debug('Right panel width calculated', {
        width: 0,
        collapsed: rightPanelState.collapsed,
        visible: rightPanelState.visible,
        expandedWidth: rightPanelState.expandedWidth,
      }, 'usePanelState');
      return 0;
    }
    // If not collapsed, return the expanded width (even if visible is false initially)
    const width = rightPanelState.expandedWidth;
    logger.debug('Right panel width calculated', {
      width,
      collapsed: rightPanelState.collapsed,
      visible: rightPanelState.visible,
      expandedWidth: rightPanelState.expandedWidth,
    }, 'usePanelState');
    return width;
  }, [rightPanelState]);

  const resetPanels = useCallback(() => {
    setLeftPanelStateInternal({
      visible: true,
      collapsed: false,
      expandedWidth: config.leftPanel.defaultWidth,
    });
    setRightPanelStateInternal({
      visible: true,
      collapsed: true,
      expandedWidth: config.rightPanel.defaultWidth,
    });
    logger.debug('Panels reset to default state', {}, 'usePanelState');
  }, [config]);

  const panelStates = useMemo<AppPanelStates>(
    () => ({
      leftPanel: leftPanelState,
      rightPanel: rightPanelState,
    }),
    [leftPanelState, rightPanelState]
  );

  return {
    panelStates,
    toggleLeftPanel,
    toggleRightPanel,
    collapseLeftPanel,
    expandLeftPanel,
    collapseRightPanel,
    expandRightPanel,
    setLeftPanelState,
    setRightPanelState,
    getLeftPanelWidth,
    getRightPanelWidth,
    resetPanels,
  };
}

