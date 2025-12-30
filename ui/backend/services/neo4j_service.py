"""
Neo4j service for graph queries.
"""

import sys
import time
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import Neo4jClient directly from file path to avoid sys.path issues with uvicorn reloader
# This file lives at: edgar-graphdb/ui/backend/services/neo4j_service.py
# We want:           edgar-graphdb/scripts/utils/neo4j_client.py
scripts_dir = Path(__file__).resolve().parent.parent.parent.parent / "scripts"
neo4j_client_path = scripts_dir / "utils" / "neo4j_client.py"

if not neo4j_client_path.exists():
    raise ImportError(f"Could not find neo4j_client.py at: {neo4j_client_path}")

# Load module directly from file path
spec = importlib.util.spec_from_file_location("neo4j_client", neo4j_client_path)
neo4j_client_module = importlib.util.module_from_spec(spec)
sys.modules["neo4j_client"] = neo4j_client_module
spec.loader.exec_module(neo4j_client_module)
Neo4jClient = neo4j_client_module.Neo4jClient

# Import models from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.graph import Node, Edge, NodeDetails, CompanyInfo, FilingInfo, GraphStats
from utils.logger_config import get_logger

logger = get_logger(__name__)


def convert_neo4j_value(value: Any) -> Any:
    """
    Convert Neo4j temporal types and other special types to JSON-serializable values.
    
    Args:
        value: Value that may contain Neo4j types
        
    Returns:
        JSON-serializable value
    """
    if value is None:
        return None
    
    # Check if it's a Neo4j temporal type by checking the module name
    value_type = type(value)
    module_name = getattr(value_type, '__module__', '')
    type_name = value_type.__name__
    
    # Handle Neo4j temporal types (from neo4j.time module)
    # Check both module name and type name to catch all Neo4j temporal types
    is_neo4j_temporal = (
        'neo4j.time' in module_name or 
        'neo4j' in module_name.lower() or
        type_name in ('DateTime', 'Date', 'Time', 'Duration', 'LocalDateTime', 'LocalTime', 'LocalDate')
    )
    
    if is_neo4j_temporal:
        try:
            # Try to convert to native Python datetime first
            if hasattr(value, 'to_native'):
                native_value = value.to_native()
                # Convert Python datetime to ISO string
                if hasattr(native_value, 'isoformat'):
                    return native_value.isoformat()
                return str(native_value)
            # Try iso_format() method (some Neo4j versions)
            elif hasattr(value, 'iso_format'):
                return value.iso_format()
            # Fallback: convert to string
            else:
                return str(value)
        except Exception as e:
            logger.debug(f"Error converting Neo4j temporal type {type_name}: {e}, using str()")
            try:
                return str(value)
            except Exception:
                logger.warning(f"Could not convert {type_name}: {value}")
                return None
    
    # Handle Python datetime objects
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    
    # Handle lists and dicts recursively
    if isinstance(value, list):
        return [convert_neo4j_value(item) for item in value]
    
    if isinstance(value, dict):
        return {k: convert_neo4j_value(v) for k, v in value.items()}
    
    # Return as-is for other types (int, str, float, bool, etc.)
    return value


class Neo4jGraphService:
    """Service for querying Neo4j graph database"""
    
    def __init__(self):
        """Initialize Neo4j client"""
        logger.info("Initializing Neo4jGraphService")
        try:
            self.client = Neo4jClient()
            self.client.connect()
            logger.info("Neo4jGraphService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4jGraphService: {str(e)}", exc_info=True)
            raise
    
    def close(self):
        """Close Neo4j connection"""
        if self.client:
            self.client.close()
    
    def _node_to_dict(self, record: Dict[str, Any], node_var: str) -> Optional[Dict[str, Any]]:
        """Convert Neo4j node record to dictionary"""
        if node_var not in record:
            return None
        
        node = record[node_var]
        if not node:
            return None
        
        # Extract labels
        labels = list(node.labels) if hasattr(node, 'labels') else []
        
        # Extract properties and convert Neo4j types to JSON-serializable values
        raw_properties = dict(node) if hasattr(node, '__iter__') else {}
        properties = {k: convert_neo4j_value(v) for k, v in raw_properties.items()}
        
        # Determine node ID based on labels
        node_id = None
        if "Company" in labels:
            node_id = properties.get("cik") or properties.get("id")
        elif "Filing" in labels:
            node_id = properties.get("accession_number") or properties.get("id")
        elif "Section" in labels:
            node_id = properties.get("section_id") or properties.get("id")
        elif "Chunk" in labels:
            node_id = properties.get("chunk_id") or properties.get("id")
        elif "Period" in labels:
            node_id = properties.get("period_id") or properties.get("id")
        elif "FinancialStatement" in labels:
            node_id = properties.get("statement_id") or properties.get("id")
        elif "LineItem" in labels:
            node_id = properties.get("line_item_id") or properties.get("id")
        elif "Value" in labels:
            node_id = properties.get("value_id") or properties.get("id")
        elif "Metric" in labels:
            node_id = properties.get("metric_id") or properties.get("id")
        elif "RiskFactor" in labels:
            node_id = properties.get("risk_id") or properties.get("id")
        else:
            # Fallback: try common ID property names
            node_id = properties.get("id") or properties.get("node_id") or properties.get("_id")
        
        if not node_id:
            logger.warning(f"Could not determine node ID for labels: {labels}, properties: {list(properties.keys())}")
            return None
        
        return {
            "id": str(node_id),
            "labels": labels,
            "properties": properties
        }
    
    def _relationship_to_dict(self, record: Dict[str, Any], rel_var: str) -> Optional[Dict[str, Any]]:
        """Convert Neo4j relationship record to dictionary"""
        if rel_var not in record:
            return None
        
        rel = record[rel_var]
        if not rel:
            return None
        
        raw_properties = dict(rel) if hasattr(rel, '__iter__') else {}
        properties = {k: convert_neo4j_value(v) for k, v in raw_properties.items()}
        
        return {
            "type": rel.type if hasattr(rel, 'type') else str(rel),
            "properties": properties
        }
    
    def get_company_graph(self, ticker: str) -> Dict[str, Any]:
        """
        Get Company node and all Filing nodes for a ticker.
        
        Returns:
            Dictionary with nodes and edges
        """
        start_time = time.time()
        logger.debug(f"Executing get_company_graph query for ticker: {ticker}")
        
        query = """
        MATCH (c:Company {ticker: $ticker})<-[:FILED_BY]-(f:Filing)
        RETURN c, f
        ORDER BY f.fiscal_year DESC, f.fiscal_quarter DESC
        """
        
        logger.debug(f"Query: {query.strip()}")
        logger.debug(f"Parameters: ticker={ticker.upper()}")
        
        results = self.client.execute_query(query, {"ticker": ticker.upper()})
        
        elapsed = time.time() - start_time
        logger.debug(f"Query returned {len(results)} results in {elapsed:.3f}s")
        
        nodes = []
        edges = []
        company_node = None
        
        for record in results:
            # Process Company node
            c_node = self._node_to_dict(record, "c")
            if c_node and not company_node:
                company_node = c_node
                nodes.append(c_node)
            
            # Process Filing node
            f_node = self._node_to_dict(record, "f")
            if f_node:
                # Check if node already added
                if not any(n["id"] == f_node["id"] for n in nodes):
                    nodes.append(f_node)
                
                # Add edge
                if company_node:
                    edges.append({
                        "source": company_node["id"],
                        "target": f_node["id"],
                        "type": "FILED_BY",
                        "properties": {}
                    })
        
        elapsed_total = time.time() - start_time
        logger.info(
            f"get_company_graph completed for {ticker}: "
            f"{len(nodes)} nodes, {len(edges)} edges in {elapsed_total:.3f}s"
        )
        
        return {"nodes": nodes, "edges": edges}
    
    def expand_filing(self, accession_number: str) -> Dict[str, Any]:
        """
        Expand Filing node to include Sections.
        
        Returns:
            Dictionary with nodes and edges
        """
        start_time = time.time()
        logger.debug(f"Executing expand_filing query for accession: {accession_number}")
        
        query = """
        MATCH (f:Filing {accession_number: $accession_number})-[:CONTAINS]->(s:Section)
        RETURN f, s
        ORDER BY s.item_number
        """
        
        logger.debug(f"Query: {query.strip()}")
        logger.debug(f"Parameters: accession_number={accession_number}")
        
        results = self.client.execute_query(query, {"accession_number": accession_number})
        
        elapsed = time.time() - start_time
        logger.debug(f"Query returned {len(results)} results in {elapsed:.3f}s")
        
        nodes = []
        edges = []
        filing_node = None
        
        for record in results:
            # Process Filing node
            f_node = self._node_to_dict(record, "f")
            if f_node and not filing_node:
                filing_node = f_node
                nodes.append(f_node)
            
            # Process Section node
            s_node = self._node_to_dict(record, "s")
            if s_node:
                if not any(n["id"] == s_node["id"] for n in nodes):
                    nodes.append(s_node)
                
                # Add edge
                if filing_node:
                    edges.append({
                        "source": filing_node["id"],
                        "target": s_node["id"],
                        "type": "CONTAINS",
                        "properties": {}
                    })
        
        elapsed_total = time.time() - start_time
        logger.info(
            f"expand_filing completed for {accession_number}: "
            f"{len(nodes)} nodes, {len(edges)} edges in {elapsed_total:.3f}s"
        )
        
        return {"nodes": nodes, "edges": edges}
    
    def expand_section(self, section_id: str) -> Dict[str, Any]:
        """
        Expand Section node to include Chunks.
        
        Returns:
            Dictionary with nodes and edges
        """
        start_time = time.time()
        logger.debug(f"Executing expand_section query for section_id: {section_id}")
        
        # Try multiple property names to find the section node
        # First try section_id, then try if the ID matches any property
        query = """
        MATCH (s:Section)
        WHERE s.section_id = $section_id 
           OR s.id = $section_id
        WITH s
        MATCH (s)-[:CONTAINS]->(ch:Chunk)
        RETURN s, ch
        ORDER BY ch.chunk_index
        """
        
        logger.debug(f"Query: {query.strip()}")
        logger.debug(f"Parameters: section_id={section_id}")
        
        results = self.client.execute_query(query, {"section_id": section_id})
        
        elapsed = time.time() - start_time
        logger.debug(f"Query returned {len(results)} results in {elapsed:.3f}s")
        
        nodes = []
        edges = []
        section_node = None
        
        for record in results:
            # Process Section node
            s_node = self._node_to_dict(record, "s")
            if s_node and not section_node:
                section_node = s_node
                nodes.append(s_node)
            
            # Process Chunk node
            ch_node = self._node_to_dict(record, "ch")
            if ch_node:
                if not any(n["id"] == ch_node["id"] for n in nodes):
                    nodes.append(ch_node)
                
                # Add edge
                if section_node:
                    edges.append({
                        "source": section_node["id"],
                        "target": ch_node["id"],
                        "type": "CONTAINS",
                        "properties": {}
                    })
        
        elapsed_total = time.time() - start_time
        logger.info(
            f"expand_section completed for {section_id}: "
            f"{len(nodes)} nodes, {len(edges)} edges in {elapsed_total:.3f}s"
        )
        
        return {"nodes": nodes, "edges": edges}
    
    def get_node_details(self, node_id: str, node_labels: List[str]) -> Optional[Dict[str, Any]]:
        """
        Get full details of a node by ID and labels.
        
        Returns:
            Node details dictionary or None
        """
        start_time = time.time()
        logger.debug(f"Executing get_node_details query for node_id: {node_id}, labels: {node_labels}")
        
        # Build query based on node type with fallback options
        label_str = ":".join(node_labels)
        
        if "Company" in node_labels:
            query = f"""MATCH (n:{label_str})
                       WHERE n.cik = $node_id OR n.id = $node_id
                       RETURN n LIMIT 1"""
        elif "Filing" in node_labels:
            query = f"""MATCH (n:{label_str})
                       WHERE n.accession_number = $node_id OR n.id = $node_id
                       RETURN n LIMIT 1"""
        elif "Section" in node_labels:
            query = f"""MATCH (n:{label_str})
                       WHERE n.section_id = $node_id OR n.id = $node_id
                       RETURN n LIMIT 1"""
        elif "Chunk" in node_labels:
            query = f"""MATCH (n:{label_str})
                       WHERE n.chunk_id = $node_id OR n.id = $node_id
                       RETURN n LIMIT 1"""
        else:
            # Generic query - try multiple approaches
            query = f"""MATCH (n:{label_str})
                       WHERE n.id = $node_id
                       RETURN n LIMIT 1"""
        
        logger.debug(f"Query: {query.strip()}")
        logger.debug(f"Parameters: node_id={node_id}")
        
        results = self.client.execute_query(query, {"node_id": node_id})
        
        elapsed = time.time() - start_time
        logger.debug(f"Query returned {len(results)} results in {elapsed:.3f}s")
        
        if not results:
            logger.warning(f"No node found for node_id: {node_id}, labels: {node_labels}")
            return None
        
        node_dict = self._node_to_dict(results[0], "n")
        elapsed_total = time.time() - start_time
        logger.debug(f"get_node_details completed for {node_id} in {elapsed_total:.3f}s")
        
        return node_dict
    
    def get_node_relationships(self, node_id: str, node_labels: List[str]) -> Dict[str, Any]:
        """
        Get all relationships for a node.
        
        Returns:
            Dictionary with incoming and outgoing edges
        """
        start_time = time.time()
        logger.debug(f"Executing get_node_relationships query for node_id: {node_id}, labels: {node_labels}")
        
        label_str = ":".join(node_labels)
        
        # Build WHERE clause with multiple fallback options
        if "Company" in node_labels:
            where_clause = "n.cik = $node_id OR n.id = $node_id"
        elif "Filing" in node_labels:
            where_clause = "n.accession_number = $node_id OR n.id = $node_id"
        elif "Section" in node_labels:
            where_clause = "n.section_id = $node_id OR n.id = $node_id"
        elif "Chunk" in node_labels:
            where_clause = "n.chunk_id = $node_id OR n.id = $node_id"
        else:
            where_clause = "n.id = $node_id"
        
        query = f"""
        MATCH (n:{label_str})
        WHERE {where_clause}
        OPTIONAL MATCH (n)-[r_out]->(target)
        OPTIONAL MATCH (source)-[r_in]->(n)
        RETURN 
            COLLECT(DISTINCT {{rel: r_out, target: target, direction: 'outgoing'}}) AS outgoing,
            COLLECT(DISTINCT {{rel: r_in, source: source, direction: 'incoming'}}) AS incoming
        """
        
        logger.debug(f"Query: {query.strip()}")
        logger.debug(f"Parameters: node_id={node_id}")
        
        results = self.client.execute_query(query, {"node_id": node_id})
        
        elapsed = time.time() - start_time
        logger.debug(f"Query returned {len(results)} results in {elapsed:.3f}s")
        
        if not results:
            return {"incoming": [], "outgoing": []}
        
        result = results[0]
        incoming = []
        outgoing = []
        
        # Process outgoing relationships
        for item in result.get("outgoing", []):
            if item.get("rel") and item.get("target"):
                target_node = self._node_to_dict({"target": item["target"]}, "target")
                if target_node:
                    rel = self._relationship_to_dict({"rel": item["rel"]}, "rel")
                    if rel:
                        outgoing.append({
                            "source": node_id,
                            "target": target_node["id"],
                            "type": rel["type"],
                            "properties": rel["properties"],
                            "target_node": target_node
                        })
        
        # Process incoming relationships
        for item in result.get("incoming", []):
            if item.get("rel") and item.get("source"):
                source_node = self._node_to_dict({"source": item["source"]}, "source")
                if source_node:
                    rel = self._relationship_to_dict({"rel": item["rel"]}, "rel")
                    if rel:
                        incoming.append({
                            "source": source_node["id"],
                            "target": node_id,
                            "type": rel["type"],
                            "properties": rel["properties"],
                            "source_node": source_node
                        })
        
        elapsed_total = time.time() - start_time
        logger.info(
            f"get_node_relationships completed for {node_id}: "
            f"{len(incoming)} incoming, {len(outgoing)} outgoing in {elapsed_total:.3f}s"
        )
        
        return {"incoming": incoming, "outgoing": outgoing}
    
    def get_company_info(self, ticker: str) -> Optional[CompanyInfo]:
        """Get company information"""
        query = """
        MATCH (c:Company {ticker: $ticker})
        RETURN c.cik AS cik,
               c.name AS name,
               c.ticker AS ticker,
               c.sic AS sic,
               c.sic_description AS sic_description,
               c.exchange AS exchange,
               c.incorporation_state AS incorporation_state
        LIMIT 1
        """
        
        results = self.client.execute_query(query, {"ticker": ticker.upper()})
        
        if not results:
            return None
        
        return CompanyInfo(**results[0])
    
    def get_filings(self, ticker: str, form_type: Optional[str] = None) -> List[FilingInfo]:
        """Get filings for a company"""
        query = """
        MATCH (c:Company {ticker: $ticker})<-[:FILED_BY]-(f:Filing)
        WHERE 1=1
        """
        params = {"ticker": ticker.upper()}
        
        if form_type:
            query += " AND f.form_type = $form_type"
            params["form_type"] = form_type
        
        query += """
        RETURN f.accession_number AS accession_number,
               f.form_type AS form_type,
               f.filing_date AS filing_date,
               f.period_end_date AS period_end_date,
               f.fiscal_year AS fiscal_year,
               f.fiscal_quarter AS fiscal_quarter,
               f.fiscal_period AS fiscal_period,
               f.url AS url
        ORDER BY f.fiscal_year DESC, f.fiscal_quarter DESC
        """
        
        results = self.client.execute_query(query, params)
        
        filings = []
        for record in results:
            # Convert dates to strings
            filing_date = str(record.get("filing_date")) if record.get("filing_date") else None
            period_end_date = str(record.get("period_end_date")) if record.get("period_end_date") else None
            
            filings.append(FilingInfo(
                accession_number=record["accession_number"],
                form_type=record["form_type"],
                filing_date=filing_date,
                period_end_date=period_end_date,
                fiscal_year=record.get("fiscal_year"),
                fiscal_quarter=record.get("fiscal_quarter"),
                fiscal_period=record.get("fiscal_period"),
                url=record.get("url")
            ))
        
        return filings
    
    def get_graph_stats(self, ticker: str) -> Optional[GraphStats]:
        """Get graph statistics for a company"""
        company_info = self.get_company_info(ticker)
        if not company_info:
            return None
        
        cik = company_info.cik
        
        # Count nodes
        query = """
        MATCH (c:Company {cik: $cik})<-[:FILED_BY]-(f:Filing)
        OPTIONAL MATCH (f)-[:CONTAINS]->(s:Section)
        OPTIONAL MATCH (s)-[:CONTAINS]->(ch:Chunk)
        OPTIONAL MATCH (f)-[:CONTAINS]->(fs:FinancialStatement)
        RETURN 
            COUNT(DISTINCT f) AS filings_count,
            COUNT(DISTINCT s) AS sections_count,
            COUNT(DISTINCT ch) AS chunks_count,
            COUNT(DISTINCT fs) AS financial_statements_count
        """
        
        results = self.client.execute_query(query, {"cik": cik})
        
        if not results:
            return GraphStats(
                company=company_info,
                filings_count=0,
                sections_count=0,
                chunks_count=0,
                financial_statements_count=0
            )
        
        result = results[0]
        return GraphStats(
            company=company_info,
            filings_count=result.get("filings_count", 0),
            sections_count=result.get("sections_count", 0),
            chunks_count=result.get("chunks_count", 0),
            financial_statements_count=result.get("financial_statements_count", 0)
        )

