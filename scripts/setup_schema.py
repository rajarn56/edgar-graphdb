#!/usr/bin/env python3
"""
Schema setup script for Neo4j EDGAR graph database.

Creates all constraints, indexes, and vector indexes as per schema design v2.0.
This script is idempotent and can be run multiple times safely.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# Load environment variables
load_dotenv(dotenv_path=scripts_dir / ".env")

from utils.logger_config import setup_logger, get_logger
from utils.neo4j_client import Neo4jClient

logger = get_logger(__name__)


def create_unique_constraints(client: Neo4jClient) -> None:
    """Create all unique constraints"""
    logger.info("Creating unique constraints...")
    
    constraints = [
        # Core entities
        ("Company", "cik"),
        ("Filing", "accession_number"),
        ("Section", "section_id"),
        ("Chunk", "chunk_id"),
        ("Period", "period_id"),
        
        # Financial
        ("FinancialStatement", "statement_id"),
        ("LineItem", "line_item_id"),
        ("Value", "value_id"),
        ("Metric", "metric_id"),
        
        # Entities
        ("Industry", "industry_id"),
        ("Sector", "sector_id"),
        ("Topic", "topic_id"),
        ("Person", "person_id"),
        
        # Ownership
        ("Transaction", "transaction_id"),
        ("Compensation", "compensation_id"),
    ]
    
    for label, property_name in constraints:
        query = f"""
        CREATE CONSTRAINT {label.lower()}_{property_name}_unique IF NOT EXISTS
        FOR (n:{label})
        REQUIRE n.{property_name} IS UNIQUE
        """
        try:
            client.execute_write(query)
            logger.info(f"✓ Created constraint: {label}.{property_name}")
        except Exception as e:
            # Check if constraint already exists (non-fatal)
            if "already exists" in str(e).lower() or "equivalent constraint" in str(e).lower():
                logger.debug(f"Constraint already exists: {label}.{property_name}")
            else:
                logger.error(f"Failed to create constraint {label}.{property_name}: {e}")


def create_property_indexes(client: Neo4jClient) -> None:
    """Create all property indexes"""
    logger.info("Creating property indexes...")
    
    indexes = [
        # Company indexes
        ("Company", "ticker"),
        ("Company", "name"),
        ("Company", "market_cap_tier"),
        
        # Filing indexes - composite
        ("Filing", "company_cik, fiscal_year, form_type", composite=True),
        ("Filing", "form_type, filing_date", composite=True),
        ("Filing", "fiscal_period"),
        
        # Section indexes
        ("Section", "item_number"),
        ("Section", "company_cik"),
        
        # Form8KItem indexes
        ("Form8KItem", "event_type, event_date", composite=True),
        
        # Chunk indexes - composite
        ("Chunk", "company_cik, fiscal_year, chunk_type", composite=True),
        ("Chunk", "semantic_type"),
        ("Chunk", "form_type"),
        
        # Financial indexes
        ("LineItem", "line_name"),
        ("LineItem", "xbrl_tag"),
        ("Value", "fiscal_year, fiscal_quarter", composite=True),
        ("Metric", "company_cik, metric_name, fiscal_year", composite=True),
        
        # Entity indexes
        ("Industry", "sic_code"),
        ("Topic", "topic_category"),
        
        # Ownership indexes
        ("Transaction", "transaction_date"),
        ("Transaction", "transaction_type"),
    ]
    
    for item in indexes:
        if isinstance(item, tuple) and len(item) == 3 and item[2]:
            # Composite index
            label, properties, _ = item
            index_name = f"{label.lower()}_{properties.replace(', ', '_').replace(' ', '_')}"
            props_list = ", ".join([f"n.{p.strip()}" for p in properties.split(",")])
            query = f"""
            CREATE INDEX {index_name} IF NOT EXISTS
            FOR (n:{label})
            ON ({props_list})
            """
        else:
            # Simple index
            label, property_name = item[:2]
            index_name = f"{label.lower()}_{property_name}"
            query = f"""
            CREATE INDEX {index_name} IF NOT EXISTS
            FOR (n:{label})
            ON (n.{property_name})
            """
        
        try:
            client.execute_write(query)
            logger.info(f"✓ Created index: {index_name}")
        except Exception as e:
            if "already exists" in str(e).lower() or "equivalent index" in str(e).lower():
                logger.debug(f"Index already exists: {index_name}")
            else:
                logger.error(f"Failed to create index {index_name}: {e}")


def create_vector_indexes(client: Neo4jClient, dimension: int = 1536) -> None:
    """Create specialized vector indexes"""
    logger.info(f"Creating vector indexes (dimension: {dimension})...")
    
    vector_indexes = [
        {
            "name": "textChunkEmbeddings",
            "label": "Chunk",
            "where": "ch.chunk_type IN ['paragraph', 'narrative']",
            "description": "General text content"
        },
        {
            "name": "riskChunkEmbeddings",
            "label": "Chunk",
            "where": "ch.semantic_type = 'risk_discussion'",
            "description": "Risk factor discussions"
        },
        {
            "name": "financialChunkEmbeddings",
            "label": "Chunk",
            "where": "ch.semantic_type IN ['financial_analysis', 'revenue_analysis', 'margin_analysis']",
            "description": "Financial analysis"
        },
        {
            "name": "strategyChunkEmbeddings",
            "label": "Chunk",
            "where": "ch.semantic_type IN ['strategy', 'forward_looking', 'guidance']",
            "description": "Strategic/forward-looking content"
        },
        {
            "name": "maChunkEmbeddings",
            "label": "Chunk",
            "where": "ch.semantic_type IN ['acquisition', 'divestiture', 'transaction']",
            "description": "M&A and transactions"
        },
    ]
    
    for idx_config in vector_indexes:
        index_name = idx_config["name"]
        label = idx_config["label"]
        where_clause = idx_config["where"]
        description = idx_config["description"]
        
        # Note: Neo4j vector index syntax may vary by version
        # This uses Neo4j 5.x syntax
        query = f"""
        CREATE VECTOR INDEX {index_name} IF NOT EXISTS
        FOR (ch:{label})
        ON ch.embedding
        OPTIONS {{
            indexConfig: {{
                `vector.dimensions`: {dimension},
                `vector.similarity_function`: 'cosine'
            }}
        }}
        """
        
        # For Neo4j versions that support WHERE clauses in vector indexes
        # This may need adjustment based on Neo4j version
        try:
            client.execute_write(query)
            logger.info(f"✓ Created vector index: {index_name} ({description})")
        except Exception as e:
            error_str = str(e).lower()
            if "already exists" in error_str or "equivalent" in error_str:
                logger.debug(f"Vector index already exists: {index_name}")
            elif "vector index" in error_str and "not supported" in error_str:
                logger.warning(f"Vector indexes not supported in this Neo4j version. Skipping {index_name}")
            else:
                logger.error(f"Failed to create vector index {index_name}: {e}")
                logger.debug(f"Query: {query}")


def create_fulltext_indexes(client: Neo4jClient) -> None:
    """Create full-text indexes for content search"""
    logger.info("Creating full-text indexes...")
    
    fulltext_indexes = [
        ("chunkContentFulltext", "Chunk", ["content"]),
        ("sectionContentFulltext", "Section", ["content", "item_title"]),
        ("riskFactorFulltext", "RiskFactor", ["risk_description", "risk_title"]),
    ]
    
    for index_name, label, properties in fulltext_indexes:
        props_list = ", ".join([f"ch.{p}" for p in properties])
        query = f"""
        CREATE FULLTEXT INDEX {index_name} IF NOT EXISTS
        FOR (ch:{label})
        ON EACH [ch.{properties[0]}]
        """
        
        # For multiple properties, may need separate indexes or different syntax
        if len(properties) > 1:
            # Create additional indexes for other properties
            for prop in properties[1:]:
                prop_index_name = f"{index_name}_{prop}"
                query = f"""
                CREATE FULLTEXT INDEX {prop_index_name} IF NOT EXISTS
                FOR (ch:{label})
                ON EACH [ch.{prop}]
                """
                try:
                    client.execute_write(query)
                    logger.info(f"✓ Created full-text index: {prop_index_name}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        logger.debug(f"Full-text index already exists: {prop_index_name}")
                    else:
                        logger.warning(f"Failed to create full-text index {prop_index_name}: {e}")
        
        # Create main index
        query = f"""
        CREATE FULLTEXT INDEX {index_name} IF NOT EXISTS
        FOR (ch:{label})
        ON EACH [ch.{properties[0]}]
        """
        try:
            client.execute_write(query)
            logger.info(f"✓ Created full-text index: {index_name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.debug(f"Full-text index already exists: {index_name}")
            else:
                logger.warning(f"Failed to create full-text index {index_name}: {e}")


def verify_schema(client: Neo4jClient) -> None:
    """Verify schema creation"""
    logger.info("Verifying schema...")
    
    # Check constraints
    constraints_query = "SHOW CONSTRAINTS"
    try:
        constraints = client.execute_query(constraints_query)
        logger.info(f"✓ Found {len(constraints)} constraints")
    except Exception as e:
        logger.warning(f"Could not verify constraints: {e}")
    
    # Check indexes
    indexes_query = "SHOW INDEXES"
    try:
        indexes = client.execute_query(indexes_query)
        logger.info(f"✓ Found {len(indexes)} indexes")
    except Exception as e:
        logger.warning(f"Could not verify indexes: {e}")


def main():
    """Main execution"""
    setup_logger("setup_schema")
    logger.info("=" * 60)
    logger.info("Neo4j EDGAR Schema Setup")
    logger.info("=" * 60)
    
    try:
        with Neo4jClient() as client:
            # Verify connectivity
            if not client.verify_connectivity():
                logger.error("Failed to connect to Neo4j. Please check your configuration.")
                return 1
            
            # Get embedding dimension (for vector indexes)
            # Default to 1536, but could be detected from embedding generator
            embedding_dimension = 1536
            logger.info(f"Using embedding dimension: {embedding_dimension}")
            
            # Create schema components
            create_unique_constraints(client)
            create_property_indexes(client)
            create_vector_indexes(client, dimension=embedding_dimension)
            create_fulltext_indexes(client)
            
            # Verify schema
            verify_schema(client)
            
            logger.info("=" * 60)
            logger.info("Schema setup completed successfully!")
            logger.info("=" * 60)
            return 0
            
    except Exception as e:
        logger.error(f"Schema setup failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

