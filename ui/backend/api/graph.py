"""
Graph API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import sys
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.neo4j_service import Neo4jGraphService
from models.graph import GraphData, Node, Edge, NodeDetails
from utils.logger_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Global service instance (in production, use dependency injection)
_service: Optional[Neo4jGraphService] = None


def get_service() -> Neo4jGraphService:
    """Get or create Neo4j service instance"""
    global _service
    if _service is None:
        _service = Neo4jGraphService()
    return _service


@router.get("/graph/{ticker}", response_model=GraphData)
async def get_graph(ticker: str):
    """
    Get complete graph for a ticker with all levels expanded (Company + Filings + Sections + Chunks).
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL)
    
    Returns:
        Graph data with nodes and edges
    """
    try:
        service = get_service()
        # Use get_complete_graph to load all levels at once
        graph_data = service.get_complete_graph(ticker)
        
        if not graph_data.get("nodes"):
            raise HTTPException(status_code=404, detail=f"No data found for ticker: {ticker}")
        
        # Convert to Pydantic models
        nodes = [Node(**node) for node in graph_data["nodes"]]
        edges = [Edge(**edge) for edge in graph_data["edges"]]
        
        return GraphData(nodes=nodes, edges=edges)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/{ticker}/expand/{node_id}", response_model=GraphData)
async def expand_node(
    ticker: str,
    node_id: str,
    node_type: str = Query(..., description="Node type: filing, section")
):
    """
    Expand a specific node to show its children.
    
    Args:
        ticker: Stock ticker symbol
        node_id: Node ID to expand
        node_type: Type of node (filing, section)
    
    Returns:
        Graph data with expanded nodes and edges
    """
    start_time = time.time()
    logger.info(f"Expanding node {node_id} (type: {node_type}) for ticker: {ticker}")
    
    try:
        service = get_service()
        
        if node_type == "filing":
            graph_data = service.expand_filing(node_id)
        elif node_type == "section":
            graph_data = service.expand_section(node_id)
        else:
            logger.warning(f"Invalid node_type: {node_type}")
            raise HTTPException(status_code=400, detail=f"Invalid node_type: {node_type}")
        
        if not graph_data.get("nodes"):
            logger.warning(f"No data found for node: {node_id}")
            raise HTTPException(status_code=404, detail=f"No data found for node: {node_id}")
        
        # Convert to Pydantic models
        nodes = [Node(**node) for node in graph_data["nodes"]]
        edges = [Edge(**edge) for edge in graph_data["edges"]]
        
        elapsed = time.time() - start_time
        logger.info(
            f"Node {node_id} expanded: "
            f"{len(nodes)} nodes, {len(edges)} edges in {elapsed:.3f}s"
        )
        
        return GraphData(nodes=nodes, edges=edges)
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"Error expanding node {node_id} after {elapsed:.3f}s: {str(e)}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/node/{node_id}", response_model=NodeDetails)
async def get_node_details(
    node_id: str,
    labels: str = Query(..., description="Comma-separated node labels (e.g., Company,Filing)")
):
    """
    Get full details of a node including properties and relationships.
    
    Args:
        node_id: Node ID
        labels: Comma-separated node labels
    
    Returns:
        Node details with relationships
    """
    start_time = time.time()
    node_labels = [label.strip() for label in labels.split(",")]
    logger.info(f"Getting details for node {node_id} with labels: {node_labels}")
    
    try:
        service = get_service()
        
        node_data = service.get_node_details(node_id, node_labels)
        if not node_data:
            logger.warning(f"Node not found: {node_id}")
            raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")
        
        relationships = service.get_node_relationships(node_id, node_labels)
        
        # Convert to Pydantic models
        node = Node(**node_data)
        incoming_edges = [Edge(**edge) for edge in relationships.get("incoming", [])]
        outgoing_edges = [Edge(**edge) for edge in relationships.get("outgoing", [])]
        
        # Build relationships list for display
        rels_list = []
        for edge in incoming_edges:
            rels_list.append({
                "direction": "incoming",
                "type": edge.type,
                "source": edge.source,
                "target": edge.target,
                "properties": edge.properties
            })
        for edge in outgoing_edges:
            rels_list.append({
                "direction": "outgoing",
                "type": edge.type,
                "source": edge.source,
                "target": edge.target,
                "properties": edge.properties
            })
        
        elapsed = time.time() - start_time
        logger.info(
            f"Node details retrieved for {node_id}: "
            f"{len(incoming_edges)} incoming, {len(outgoing_edges)} outgoing relationships in {elapsed:.3f}s"
        )
        
        return NodeDetails(
            node=node,
            relationships=rels_list,
            incoming_edges=incoming_edges,
            outgoing_edges=outgoing_edges
        )
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"Error getting node details for {node_id} after {elapsed:.3f}s: {str(e)}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/node/{node_id}/relationships")
async def get_node_relationships(
    node_id: str,
    labels: str = Query(..., description="Comma-separated node labels")
):
    """
    Get relationships for a node.
    
    Args:
        node_id: Node ID
        labels: Comma-separated node labels
    
    Returns:
        Dictionary with incoming and outgoing relationships
    """
    try:
        service = get_service()
        node_labels = [label.strip() for label in labels.split(",")]
        
        relationships = service.get_node_relationships(node_id, node_labels)
        
        return relationships
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

