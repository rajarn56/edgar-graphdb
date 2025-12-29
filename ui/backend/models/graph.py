"""
Pydantic models for graph data structures.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Node(BaseModel):
    """Node representation"""
    id: str = Field(..., description="Node ID")
    labels: List[str] = Field(..., description="Node labels")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")
    position: Optional[Dict[str, float]] = Field(None, description="Node position (x, y)")


class Edge(BaseModel):
    """Edge/Relationship representation"""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: str = Field(..., description="Relationship type")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Relationship properties")


class GraphData(BaseModel):
    """Complete graph data"""
    nodes: List[Node] = Field(default_factory=list, description="Graph nodes")
    edges: List[Edge] = Field(default_factory=list, description="Graph edges")


class NodeDetails(BaseModel):
    """Full node details with relationships"""
    node: Node = Field(..., description="Node data")
    relationships: List[Dict[str, Any]] = Field(default_factory=list, description="Connected nodes and relationships")
    incoming_edges: List[Edge] = Field(default_factory=list, description="Incoming edges")
    outgoing_edges: List[Edge] = Field(default_factory=list, description="Outgoing edges")


class CompanyInfo(BaseModel):
    """Company information"""
    cik: str
    name: str
    ticker: Optional[str] = None
    sic: Optional[str] = None
    sic_description: Optional[str] = None
    exchange: Optional[str] = None
    incorporation_state: Optional[str] = None


class FilingInfo(BaseModel):
    """Filing information"""
    accession_number: str
    form_type: str
    filing_date: Optional[str] = None
    period_end_date: Optional[str] = None
    fiscal_year: Optional[int] = None
    fiscal_quarter: Optional[int] = None
    fiscal_period: Optional[str] = None
    url: Optional[str] = None


class GraphStats(BaseModel):
    """Graph statistics"""
    company: CompanyInfo
    filings_count: int = 0
    sections_count: int = 0
    chunks_count: int = 0
    financial_statements_count: int = 0

