/**
 * UI-specific TypeScript types for panel states, filter states, and UI interactions.
 */

/**
 * Panel visibility and collapse states
 */
export interface PanelState {
  /** Whether the panel is visible */
  visible: boolean;
  /** Whether the panel is collapsed (takes up minimal/no space) */
  collapsed: boolean;
  /** Panel width when expanded (in pixels) */
  expandedWidth: number;
}

/**
 * Application panel states
 */
export interface AppPanelStates {
  /** Left panel (filters) state */
  leftPanel: PanelState;
  /** Right panel (node details) state */
  rightPanel: PanelState;
}

/**
 * Filter options for graph visualization
 */
export interface FilterOptions {
  /** Filter by form type (e.g., '10-K', '10-Q') */
  formType?: string;
  /** Filter by fiscal year */
  fiscalYear?: number;
  /** Node types to show/hide */
  nodeTypes: string[];
}

/**
 * Node selection state
 */
export interface NodeSelectionState {
  /** Selected node ID */
  nodeId: string | null;
  /** Selected node labels */
  labels: string[];
  /** Whether details are being loaded */
  loading: boolean;
  /** Error message if loading failed */
  error: string | null;
}

/**
 * Graph loading state
 */
export interface GraphLoadingState {
  /** Whether graph is currently loading */
  loading: boolean;
  /** Error message if loading failed */
  error: string | null;
  /** Current ticker being loaded */
  ticker: string | null;
}

/**
 * Node expansion state
 */
export interface NodeExpansionState {
  /** Set of expanded node IDs */
  expandedNodes: Set<string>;
  /** Currently expanding node ID */
  expandingNodeId: string | null;
}

/**
 * UI interaction events
 */
export type UIEventType = 
  | 'node_click'
  | 'node_double_click'
  | 'node_expand'
  | 'node_select'
  | 'panel_toggle'
  | 'panel_close'
  | 'filter_change'
  | 'graph_load'
  | 'graph_reset';

/**
 * UI event data
 */
export interface UIEvent {
  type: UIEventType;
  timestamp: string;
  data?: any;
  component?: string;
}

/**
 * Panel configuration
 */
export interface PanelConfig {
  /** Default width when expanded */
  defaultWidth: number;
  /** Minimum width */
  minWidth: number;
  /** Maximum width */
  maxWidth: number;
  /** Whether panel can be collapsed */
  collapsible: boolean;
  /** Whether panel can be resized */
  resizable: boolean;
}

/**
 * Layout configuration
 */
export interface LayoutConfig {
  /** Left panel configuration */
  leftPanel: PanelConfig;
  /** Right panel configuration */
  rightPanel: PanelConfig;
  /** Header height */
  headerHeight: number;
  /** Footer/Stats bar height */
  footerHeight: number;
}

/**
 * Default layout configuration
 */
export const DEFAULT_LAYOUT_CONFIG: LayoutConfig = {
  leftPanel: {
    defaultWidth: 250,
    minWidth: 0,
    maxWidth: 400,
    collapsible: true,
    resizable: false,
  },
  rightPanel: {
    defaultWidth: 400,
    minWidth: 0,
    maxWidth: 600,
    collapsible: true,
    resizable: false,
  },
  headerHeight: 60,
  footerHeight: 40,
};

