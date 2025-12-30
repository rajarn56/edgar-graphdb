/**
 * Graph layout algorithms for positioning nodes.
 */

import type { GraphNode, GraphEdge } from '../types/graph';

const NODE_WIDTH = 200;
const NODE_HEIGHT = 100;
const HORIZONTAL_SPACING = 250;
const VERTICAL_SPACING = 150;

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
  
  // Position nodes by level
  const maxLevel = Math.max(...Array.from(levels.keys()));
  const levelWidths = new Map<number, number>();
  
  // Calculate width needed for each level
  levels.forEach((levelNodes, level) => {
    levelWidths.set(level, levelNodes.length);
  });
  
  // Position nodes
  levels.forEach((levelNodes, level) => {
    const levelWidth = levelWidths.get(level) || 1;
    const startX = -(levelWidth * HORIZONTAL_SPACING) / 2;
    const y = level * VERTICAL_SPACING + 100;
    
    levelNodes.forEach((node, index) => {
      const x = startX + index * HORIZONTAL_SPACING;
      positions.set(node.id, { x, y });
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
 * Apply layout to nodes
 */
export function applyLayout(
  nodes: GraphNode[],
  edges: GraphEdge[]
): GraphNode[] {
  const positions = calculateHierarchicalLayout(nodes, edges);
  
  return nodes.map(node => {
    const pos = positions.get(node.id) || { x: 0, y: 0 };
    return {
      ...node,
      position: pos,
    };
  });
}

