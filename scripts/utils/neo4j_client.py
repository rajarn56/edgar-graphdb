"""Neo4j database client wrapper with connection management and retry logic"""

import os
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, TransientError
from loguru import logger


class Neo4jClient:
    """Wrapper for Neo4j driver with connection management and retry logic"""
    
    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize Neo4j client.
        
        Args:
            uri: Neo4j connection URI (defaults to NEO4J_URI env var)
            user: Neo4j username (defaults to NEO4J_USER env var)
            password: Neo4j password (defaults to NEO4J_PASSWORD env var)
            max_retries: Maximum number of retry attempts for transient errors
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD")
        
        if not self.password:
            raise ValueError("Neo4j password must be provided via parameter or NEO4J_PASSWORD env var")
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.driver: Optional[Driver] = None
        
        # Debug logging enabled via environment variable
        self.debug_logging = os.getenv("NEO4J_DEBUG_LOGGING", "false").lower() in ("true", "1", "yes")
        if self.debug_logging:
            # Determine log path relative to scripts directory
            scripts_dir = Path(__file__).parent.parent
            self.debug_log_dir = scripts_dir / "logs"
            self.debug_log_dir.mkdir(parents=True, exist_ok=True)
            self.debug_log_path = self.debug_log_dir / "debug.log"
        
        logger.info(f"Initializing Neo4j client: {self.uri} (user: {self.user})")
    
    def connect(self) -> None:
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=30 * 60,  # 30 minutes
                max_connection_pool_size=50,
                connection_acquisition_timeout=2 * 60,  # 2 minutes
            )
            # Verify connectivity
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self) -> None:
        """Close Neo4j driver connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        if not self.driver:
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    @contextmanager
    def session(self, **kwargs):
        """
        Get a Neo4j session with automatic cleanup.
        
        Args:
            **kwargs: Additional arguments to pass to driver.session()
        
        Yields:
            Neo4j Session instance
        """
        if not self.driver:
            self.connect()
        
        session = self.driver.session(**kwargs)
        try:
            yield session
        finally:
            session.close()
    
    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        retry_on_transient: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query with retry logic.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            retry_on_transient: Whether to retry on transient errors
        
        Returns:
            List of result records as dictionaries
        """
        if parameters is None:
            parameters = {}
        
        attempt = 0
        while attempt < self.max_retries:
            try:
                with self.session() as session:
                    result = session.run(query, parameters)
                    records = [dict(record) for record in result]
                    return records
            except (ServiceUnavailable, TransientError) as e:
                attempt += 1
                if not retry_on_transient or attempt >= self.max_retries:
                    logger.error(f"Query failed after {attempt} attempts: {e}")
                    raise
                
                delay = self.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                logger.warning(f"Transient error (attempt {attempt}/{self.max_retries}), retrying in {delay}s: {e}")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Query execution failed: {e}\nQuery: {query[:200]}...")
                raise
        
        return []
    
    def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        retry_on_transient: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute a write query with retry logic.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            retry_on_transient: Whether to retry on transient errors
        
        Returns:
            List of result records as dictionaries
        """
        if parameters is None:
            parameters = {}
        
        attempt = 0
        while attempt < self.max_retries:
            try:
                with self.session() as session:
                    # #region debug logging
                    if self.debug_logging:
                        try:
                            with open(self.debug_log_path, 'a') as f:
                                f.write(json.dumps({
                                    "sessionId": "neo4j-client",
                                    "runId": f"attempt-{attempt}",
                                    "location": "neo4j_client.py:execute_write",
                                    "message": "Session object type check",
                                    "data": {
                                        "session_type": str(type(session)),
                                        "has_commit": hasattr(session, 'commit'),
                                        "session_methods": [m for m in dir(session) if not m.startswith('_')][:10]
                                    },
                                    "timestamp": int(time.time() * 1000)
                                }) + '\n')
                        except Exception:
                            pass
                    # #endregion debug logging
                    result = session.run(query, parameters)
                    records = [dict(record) for record in result]
                    # #region debug logging
                    if self.debug_logging:
                        try:
                            with open(self.debug_log_path, 'a') as f:
                                f.write(json.dumps({
                                    "sessionId": "neo4j-client",
                                    "runId": f"attempt-{attempt}",
                                    "location": "neo4j_client.py:execute_write",
                                    "message": "After query execution",
                                    "data": {
                                        "records_count": len(records),
                                        "has_commit_method": hasattr(session, 'commit')
                                    },
                                    "timestamp": int(time.time() * 1000)
                                }) + '\n')
                        except Exception:
                            pass
                    # #endregion debug logging
                    # Note: Neo4j Python driver auto-commits transactions when session context exits
                    # No explicit commit() call needed
                    return records
            except (ServiceUnavailable, TransientError) as e:
                attempt += 1
                if not retry_on_transient or attempt >= self.max_retries:
                    logger.error(f"Write query failed after {attempt} attempts: {e}")
                    raise
                
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.warning(f"Transient error (attempt {attempt}/{self.max_retries}), retrying in {delay}s: {e}")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Write query execution failed: {e}\nQuery: {query[:200]}...")
                raise
        
        return []
    
    def execute_transaction(
        self,
        queries: List[tuple],
        retry_on_transient: bool = True
    ) -> List[List[Dict[str, Any]]]:
        """
        Execute multiple queries in a single transaction.
        
        Args:
            queries: List of (query, parameters) tuples
            retry_on_transient: Whether to retry on transient errors
        
        Returns:
            List of result lists (one per query)
        """
        attempt = 0
        while attempt < self.max_retries:
            try:
                with self.session() as session:
                    # #region debug logging
                    if self.debug_logging:
                        try:
                            with open(self.debug_log_path, 'a') as f:
                                f.write(json.dumps({
                                    "sessionId": "neo4j-client",
                                    "runId": f"attempt-{attempt}",
                                    "location": "neo4j_client.py:execute_transaction",
                                    "message": "Transaction session type check",
                                    "data": {
                                        "session_type": str(type(session)),
                                        "has_commit": hasattr(session, 'commit'),
                                        "queries_count": len(queries)
                                    },
                                    "timestamp": int(time.time() * 1000)
                                }) + '\n')
                        except Exception:
                            pass
                    # #endregion debug logging
                    results = []
                    for query, parameters in queries:
                        if parameters is None:
                            parameters = {}
                        result = session.run(query, parameters)
                        records = [dict(record) for record in result]
                        results.append(records)
                    # #region debug logging
                    if self.debug_logging:
                        try:
                            with open(self.debug_log_path, 'a') as f:
                                f.write(json.dumps({
                                    "sessionId": "neo4j-client",
                                    "runId": f"attempt-{attempt}",
                                    "location": "neo4j_client.py:execute_transaction",
                                    "message": "After transaction queries",
                                    "data": {
                                        "has_commit_method": hasattr(session, 'commit'),
                                        "results_count": len(results)
                                    },
                                    "timestamp": int(time.time() * 1000)
                                }) + '\n')
                        except Exception:
                            pass
                    # #endregion debug logging
                    # Note: Neo4j Python driver auto-commits transactions when session context exits
                    # No explicit commit() call needed
                    return results
            except (ServiceUnavailable, TransientError) as e:
                attempt += 1
                if not retry_on_transient or attempt >= self.max_retries:
                    logger.error(f"Transaction failed after {attempt} attempts: {e}")
                    raise
                
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.warning(f"Transient error (attempt {attempt}/{self.max_retries}), retrying in {delay}s: {e}")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Transaction execution failed: {e}")
                raise
        
        return []
    
    def verify_connectivity(self) -> bool:
        """
        Verify Neo4j database connectivity.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            with self.session() as session:
                result = session.run("RETURN 1 AS test")
                record = result.single()
                if record and record["test"] == 1:
                    logger.info("Neo4j connectivity verified")
                    return True
        except Exception as e:
            logger.error(f"Neo4j connectivity check failed: {e}")
            return False
        return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information.
        
        Returns:
            Dictionary with database metadata
        """
        try:
            with self.session() as session:
                # Get Neo4j version
                version_result = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions[0] AS version")
                version_info = {}
                for record in version_result:
                    version_info[record["name"]] = record["version"]
                
                # Get node counts
                node_counts = {}
                node_types = ["Company", "Filing", "Section", "Chunk", "FinancialStatement", "LineItem", "Value"]
                for node_type in node_types:
                    count_result = session.run(f"MATCH (n:{node_type}) RETURN count(n) AS count")
                    count_record = count_result.single()
                    if count_record:
                        node_counts[node_type] = count_record["count"]
                
                return {
                    "version": version_info,
                    "node_counts": node_counts
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {}

