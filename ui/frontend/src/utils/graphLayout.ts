/**
 * Graph layout algorithms for positioning nodes.
 */

import type { GraphNode, GraphEdge } from '../types/graph';

const NODE_WIDTH = 200;
const NODE_HEIGHT = 100;
// Doubled spacing for better visibility of connectors and relationships
const HORIZONTAL_SPACING = 560; // Was 280
const VERTICAL_SPACING = 360; // Was 180

// Node type specific spacing (doubled for better visibility)
const NODE_TYPE_SPACING: Record<string, { horizontal: number; vertical: number }> = {
  Company: { horizontal: 600, vertical: 400 }, // Was 300, 200
  Filing: { horizontal: 500, vertical: 300 }, // Was 250, 150
  Section: { horizontal: 400, vertical: 240 }, // Was 200, 120
  Chunk: { horizontal: 300, vertical: 200 }, // Was 150, 100
};

/**
 * Calculate hierarchical layout positions for nodes
 */
export function calculateHierarchicalLayout(
  nodes: GraphNode[],
  edges: GraphEdge[]
): Map<string, { x: number; y: number }> {
  const positions = new Map<string, { x: number; y: number }>();
  
  // Find root nodes (nodes with no incoming edges)
  const incomingCount = new Map<string, number>();
  nodes.forEach(node => incomingCount.set(node.id, 0));
  edges.forEach(edge => {
    const count = incomingCount.get(edge.target) || 0;
    incomingCount.set(edge.target, count + 1);
  });
  
  const rootNodes = nodes.filter(node => (incomingCount.get(node.id) || 0) === 0);
  
  // Group nodes by level (distance from root)
  const levels = new Map<number, GraphNode[]>();
  const nodeLevel = new Map<string, number>();
  
  // BFS to assign levels
  const queue: Array<{ node: GraphNode; level: number }> = rootNodes.map(node => ({ node, level: 0 }));
  const visited = new Set<string>();
  
  while (queue.length > 0) {
    const { node, level } = queue.shift()!;
    
    if (visited.has(node.id)) continue;
    visited.add(node.id);
    
    nodeLevel.set(node.id, level);
    
    if (!levels.has(level)) {
      levels.set(level, []);
    }
    levels.get(level)!.push(node);
    
    // Add children to queue
    edges
      .filter(edge => edge.source === node.id)
      .forEach(edge => {
        const targetNode = nodes.find(n => n.id === edge.target);
        if (targetNode && !visited.has(targetNode.id)) {
          queue.push({ node: targetNode, level: level + 1 });
        }
      });
  }
  
  // Position nodes by level with improved spacing
  const maxLevel = Math.max(...Array.from(levels.keys()), 0);
  const levelWidths = new Map<number, number>();
  
  // Calculate width needed for each level (considering node types)
  levels.forEach((levelNodes, level) => {
    let totalWidth = 0;
    levelNodes.forEach(node => {
      const nodeType = node.labels[0] || 'default';
      const spacing = NODE_TYPE_SPACING[nodeType] || { horizontal: HORIZONTAL_SPACING, vertical: VERTICAL_SPACING };
      totalWidth += spacing.horizontal;
    });
    levelWidths.set(level, totalWidth || HORIZONTAL_SPACING);
  });
  
  // Position nodes with type-aware spacing
  levels.forEach((levelNodes, level) => {
    const levelWidth = levelWidths.get(level) || HORIZONTAL_SPACING;
    let currentX = -levelWidth / 2;
    const y = level * VERTICAL_SPACING + 150;
    
    levelNodes.forEach((node) => {
      const nodeType = node.labels[0] || 'default';
      const spacing = NODE_TYPE_SPACING[nodeType] || { horizontal: HORIZONTAL_SPACING, vertical: VERTICAL_SPACING };
      const x = currentX + spacing.horizontal / 2;
      positions.set(node.id, { x, y });
      currentX += spacing.horizontal;
    });
  });
  
  // Handle nodes not reached by BFS (orphans)
  nodes.forEach(node => {
    if (!positions.has(node.id)) {
      positions.set(node.id, { x: 0, y: 0 });
    }
  });
  
  return positions;
}

/**
 * Calculate node levels (distance from root)
 * Returns a map of node ID to level
 */
export function calculateNodeLevels(
  nodes: GraphNode[],
  edges: GraphEdge[]
): Map<string, number> {
  const nodeLevel = new Map<string, number>();
  
  // Find root nodes (nodes with no incoming edges)
  const incomingCount = new Map<string, number>();
  nodes.forEach(node => incomingCount.set(node.id, 0));
  edges.forEach(edge => {
    const count = incomingCount.get(edge.target) || 0;
    incomingCount.set(edge.target, count + 1);
  });
  
  const rootNodes = nodes.filter(node => (incomingCount.get(node.id) || 0) === 0);
  
  // BFS to assign levels
  const queue: Array<{ node: GraphNode; level: number }> = rootNodes.map(node => ({ node, level: 0 }));
  const visited = new Set<string>();
  
  while (queue.length > 0) {
    const { node, level } = queue.shift()!;
    
    if (visited.has(node.id)) continue;
    visited.add(node.id);
    
    nodeLevel.set(node.id, level);
    
    // Add children to queue
    edges
      .filter(edge => edge.source === node.id)
      .forEach(edge => {
        const targetNode = nodes.find(n => n.id === edge.target);
        if (targetNode && !visited.has(targetNode.id)) {
          queue.push({ node: targetNode, level: level + 1 });
        }
      });
  }
  
  // Handle nodes not reached by BFS (orphans) - assign level 999
  nodes.forEach(node => {
    if (!nodeLevel.has(node.id)) {
      nodeLevel.set(node.id, 999);
    }
  });
  
  return nodeLevel;
}

/**
 * Filter nodes based on expanded state
 * Shows: root nodes (level 0), level 1 nodes, and children of expanded nodes
 */
export function filterNodesByExpandedState(
  nodes: GraphNode[],
  edges: GraphEdge[],
  expandedNodes: Set<string>
): { nodes: GraphNode[]; edges: GraphEdge[] } {
  if (nodes.length === 0) {
    return { nodes: [], edges: [] };
  }
  
  const nodeLevels = calculateNodeLevels(nodes, edges);
  const visibleNodeIds = new Set<string>();
  
  // Always show level 0 (root) nodes - these are nodes with no incoming edges
  // Also show level 1 nodes (direct children of root)
  nodes.forEach(node => {
    const level = nodeLevels.get(node.id);
    if (level !== undefined && level <= 1) {
      visibleNodeIds.add(node.id);
    }
  });
  
  // If no level 0 nodes found (edge case), show all nodes with level 0
  // This handles cases where level calculation might have issues
  if (visibleNodeIds.size === 0) {
    // Fallback: show all nodes that are roots (no incoming edges)
    const incomingCount = new Map<string, number>();
    nodes.forEach(node => incomingCount.set(node.id, 0));
    edges.forEach(edge => {
      const count = incomingCount.get(edge.target) || 0;
      incomingCount.set(edge.target, count + 1);
    });
    nodes.forEach(node => {
      if ((incomingCount.get(node.id) || 0) === 0) {
        visibleNodeIds.add(node.id);
        // Also add their direct children
        edges
          .filter(edge => edge.source === node.id)
          .forEach(edge => visibleNodeIds.add(edge.target));
      }
    });
  }
  
  // Recursively add children of expanded nodes
  const addChildrenRecursively = (parentId: string) => {
    edges
      .filter(edge => edge.source === parentId)
      .forEach(edge => {
        visibleNodeIds.add(edge.target);
        // If the child is also expanded, recursively add its children
        if (expandedNodes.has(edge.target)) {
          addChildrenRecursively(edge.target);
        }
      });
  };
  
  expandedNodes.forEach(expandedNodeId => {
    addChildrenRecursively(expandedNodeId);
  });
  
  // Filter nodes - preserve positions from original nodes
  const visibleNodes = nodes
    .filter(node => visibleNodeIds.has(node.id))
    .map(node => {
      // Preserve the node object with its position (if it exists)
      // This ensures manually positioned nodes keep their positions when filtered
      return node;
    });
  
  // Filter edges to only include connections between visible nodes
  const visibleNodeIdSet = new Set(visibleNodes.map(n => n.id));
  const visibleEdges = edges.filter(edge => 
    visibleNodeIdSet.has(edge.source) && visibleNodeIdSet.has(edge.target)
  );
  
  return { nodes: visibleNodes, edges: visibleEdges };
}

/**
 * Apply layout to nodes
 * Preserves existing positions if they exist (for manually positioned nodes or nodes positioned relative to parent)
 * Only calculates positions for nodes that don't have positions set
 */
export function applyLayout(
  nodes: GraphNode[],
  edges: GraphEdge[]
): GraphNode[] {
  // Separate nodes with and without positions
  const nodesWithPositions = nodes.filter(node => node.position);
  const nodesWithoutPositions = nodes.filter(node => !node.position);
  
  // Only calculate layout for nodes without positions
  let calculatedPositions = new Map<string, { x: number; y: number }>();
  if (nodesWithoutPositions.length > 0) {
    // Calculate hierarchical layout for all nodes to get proper level-based positioning
    // But we'll only use positions for nodes that don't have them
    calculatedPositions = calculateHierarchicalLayout(nodes, edges);
  }
  
  return nodes.map(node => {
    // Preserve existing position if it exists (e.g., manually positioned or positioned relative to parent)
    // Only use calculated position if node doesn't have a position yet
    if (node.position) {
      return {
        ...node,
        position: node.position,
      };
    }
    
    // Use calculated position for nodes without positions
    const calculatedPos = calculatedPositions.get(node.id) || { x: 0, y: 0 };
    return {
      ...node,
      position: calculatedPos,
    };
  });
}

