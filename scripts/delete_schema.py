#!/usr/bin/env python3
"""
Schema deletion script for Neo4j EDGAR graph database.

Completely removes all schema elements (nodes, relationships, constraints, indexes)
from Neo4j database, making it clean again.

⚠️  WARNING: This script will DELETE ALL DATA in the database!
This operation is irreversible. Use with caution.

Equivalent Cypher queries are documented in comments for reference.
"""

import sys
import argparse
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


def get_database_stats(client: Neo4jClient) -> dict:
    """
    Get current database statistics (node counts, relationship counts, etc.)
    
    Returns:
        Dictionary with database statistics
    """
    stats = {
        "node_count": 0,
        "relationship_count": 0,
        "constraint_count": 0,
        "index_count": 0,
    }
    
    try:
        # Count all nodes
        # Equivalent Cypher: MATCH (n) RETURN count(n) AS count
        node_query = "MATCH (n) RETURN count(n) AS count"
        result = client.execute_query(node_query)
        if result:
            stats["node_count"] = result[0].get("count", 0)
        
        # Count all relationships
        # Equivalent Cypher: MATCH ()-[r]->() RETURN count(r) AS count
        rel_query = "MATCH ()-[r]->() RETURN count(r) AS count"
        result = client.execute_query(rel_query)
        if result:
            stats["relationship_count"] = result[0].get("count", 0)
        
        # Count constraints
        # Equivalent Cypher: SHOW CONSTRAINTS
        constraints_query = "SHOW CONSTRAINTS"
        result = client.execute_query(constraints_query)
        stats["constraint_count"] = len(result) if result else 0
        
        # Count indexes
        # Equivalent Cypher: SHOW INDEXES
        indexes_query = "SHOW INDEXES"
        result = client.execute_query(indexes_query)
        stats["index_count"] = len(result) if result else 0
        
    except Exception as e:
        logger.warning(f"Error getting database stats: {e}")
    
    return stats


def delete_all_data(client: Neo4jClient) -> None:
    """
    Delete all nodes and relationships from the database.
    
    This uses DETACH DELETE which removes nodes and all their relationships.
    
    Equivalent Cypher query:
    ```
    MATCH (n)
    DETACH DELETE n
    ```
    
    Note: This will delete ALL nodes regardless of label. All relationships
    will be automatically deleted as well.
    """
    logger.warning("=" * 60)
    logger.warning("DELETING ALL NODES AND RELATIONSHIPS")
    logger.warning("=" * 60)
    
    # Equivalent Cypher: MATCH (n) DETACH DELETE n
    query = """
    MATCH (n)
    DETACH DELETE n
    """
    
    try:
        result = client.execute_write(query)
        logger.info("✓ Deleted all nodes and relationships")
        
        # Verify deletion
        verify_query = "MATCH (n) RETURN count(n) AS count"
        verify_result = client.execute_query(verify_query)
        remaining_nodes = verify_result[0].get("count", 0) if verify_result else 0
        
        if remaining_nodes == 0:
            logger.info("✓ Verification: All nodes deleted successfully")
        else:
            logger.warning(f"⚠ Warning: {remaining_nodes} nodes still remain")
            
    except Exception as e:
        logger.error(f"Failed to delete nodes: {e}")
        raise


def drop_all_constraints(client: Neo4jClient) -> None:
    """
    Drop all constraints from the database.
    
    This queries existing constraints and drops each one.
    
    Equivalent Cypher queries:
    ```
    # List all constraints
    SHOW CONSTRAINTS
    
    # Drop a specific constraint (example)
    DROP CONSTRAINT company_cik_unique IF EXISTS
    ```
    
    Note: Constraints are automatically discovered and dropped.
    """
    logger.info("Dropping all constraints...")
    
    try:
        # Get all constraints
        # Equivalent Cypher: SHOW CONSTRAINTS
        constraints_query = "SHOW CONSTRAINTS"
        constraints = client.execute_query(constraints_query)
        
        if not constraints:
            logger.info("No constraints found")
            return
        
        dropped_count = 0
        for constraint in constraints:
            constraint_name = constraint.get("name") or constraint.get("id")
            if not constraint_name:
                continue
            
            # Drop constraint
            # Equivalent Cypher: DROP CONSTRAINT constraint_name IF EXISTS
            drop_query = f"DROP CONSTRAINT {constraint_name} IF EXISTS"
            
            try:
                client.execute_write(drop_query)
                logger.info(f"✓ Dropped constraint: {constraint_name}")
                dropped_count += 1
            except Exception as e:
                error_str = str(e).lower()
                if "does not exist" in error_str or "not found" in error_str:
                    logger.debug(f"Constraint already removed: {constraint_name}")
                else:
                    logger.warning(f"Failed to drop constraint {constraint_name}: {e}")
        
        logger.info(f"✓ Dropped {dropped_count} constraint(s)")
        
        # Verify deletion
        remaining_constraints = client.execute_query(constraints_query)
        if len(remaining_constraints) == 0:
            logger.info("✓ Verification: All constraints dropped successfully")
        else:
            logger.warning(f"⚠ Warning: {len(remaining_constraints)} constraints still remain")
            
    except Exception as e:
        logger.error(f"Failed to drop constraints: {e}")
        raise


def drop_all_indexes(client: Neo4jClient) -> None:
    """
    Drop all indexes from the database (property, vector, and full-text indexes).
    
    This queries existing indexes and drops each one.
    
    Equivalent Cypher queries:
    ```
    # List all indexes
    SHOW INDEXES
    
    # Drop a specific index (example)
    DROP INDEX index_name IF EXISTS
    
    # Drop vector index (example)
    DROP INDEX vectorIndexName IF EXISTS
    ```
    
    Note: All index types (property, vector, full-text) are automatically discovered and dropped.
    """
    logger.info("Dropping all indexes...")
    
    try:
        # Get all indexes
        # Equivalent Cypher: SHOW INDEXES
        indexes_query = "SHOW INDEXES"
        indexes = client.execute_query(indexes_query)
        
        if not indexes:
            logger.info("No indexes found")
            return
        
        dropped_count = 0
        skipped_count = 0
        
        for index in indexes:
            index_name = index.get("name") or index.get("id")
            index_type = index.get("type", "").lower()
            
            if not index_name:
                continue
            
            # Skip token lookup indexes (internal Neo4j indexes)
            if "token lookup" in index_type or index_name.startswith("__"):
                skipped_count += 1
                logger.debug(f"Skipping internal index: {index_name}")
                continue
            
            # Drop index
            # Equivalent Cypher: DROP INDEX index_name IF EXISTS
            drop_query = f"DROP INDEX {index_name} IF EXISTS"
            
            try:
                client.execute_write(drop_query)
                logger.info(f"✓ Dropped index: {index_name} (type: {index_type})")
                dropped_count += 1
            except Exception as e:
                error_str = str(e).lower()
                if "does not exist" in error_str or "not found" in error_str:
                    logger.debug(f"Index already removed: {index_name}")
                else:
                    logger.warning(f"Failed to drop index {index_name}: {e}")
        
        logger.info(f"✓ Dropped {dropped_count} index(es) (skipped {skipped_count} internal indexes)")
        
        # Verify deletion (excluding internal indexes)
        remaining_indexes = client.execute_query(indexes_query)
        user_indexes = [
            idx for idx in remaining_indexes
            if not (idx.get("type", "").lower() == "token lookup" or 
                   (idx.get("name") or "").startswith("__"))
        ]
        
        if len(user_indexes) == 0:
            logger.info("✓ Verification: All user indexes dropped successfully")
        else:
            logger.warning(f"⚠ Warning: {len(user_indexes)} user indexes still remain")
            
    except Exception as e:
        logger.error(f"Failed to drop indexes: {e}")
        raise


def verify_deletion(client: Neo4jClient) -> dict:
    """
    Verify that all data, constraints, and indexes have been deleted.
    
    Returns:
        Dictionary with verification results
    """
    logger.info("Verifying deletion...")
    
    verification = {
        "nodes_remaining": 0,
        "relationships_remaining": 0,
        "constraints_remaining": 0,
        "indexes_remaining": 0,
        "is_clean": False,
    }
    
    try:
        # Check nodes
        node_query = "MATCH (n) RETURN count(n) AS count"
        result = client.execute_query(node_query)
        verification["nodes_remaining"] = result[0].get("count", 0) if result else 0
        
        # Check relationships
        rel_query = "MATCH ()-[r]->() RETURN count(r) AS count"
        result = client.execute_query(rel_query)
        verification["relationships_remaining"] = result[0].get("count", 0) if result else 0
        
        # Check constraints
        constraints_query = "SHOW CONSTRAINTS"
        constraints = client.execute_query(constraints_query)
        verification["constraints_remaining"] = len(constraints) if constraints else 0
        
        # Check indexes (excluding internal ones)
        indexes_query = "SHOW INDEXES"
        indexes = client.execute_query(indexes_query)
        user_indexes = [
            idx for idx in (indexes or [])
            if not (idx.get("type", "").lower() == "token lookup" or 
                   (idx.get("name") or "").startswith("__"))
        ]
        verification["indexes_remaining"] = len(user_indexes)
        
        # Determine if database is clean
        verification["is_clean"] = (
            verification["nodes_remaining"] == 0 and
            verification["relationships_remaining"] == 0 and
            verification["constraints_remaining"] == 0 and
            verification["indexes_remaining"] == 0
        )
        
        if verification["is_clean"]:
            logger.info("✓ Database is clean - all data, constraints, and indexes removed")
        else:
            logger.warning("⚠ Database is not completely clean:")
            if verification["nodes_remaining"] > 0:
                logger.warning(f"  - {verification['nodes_remaining']} nodes remaining")
            if verification["relationships_remaining"] > 0:
                logger.warning(f"  - {verification['relationships_remaining']} relationships remaining")
            if verification["constraints_remaining"] > 0:
                logger.warning(f"  - {verification['constraints_remaining']} constraints remaining")
            if verification["indexes_remaining"] > 0:
                logger.warning(f"  - {verification['indexes_remaining']} indexes remaining")
        
    except Exception as e:
        logger.error(f"Error during verification: {e}")
    
    return verification


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="Delete all schema elements from Neo4j EDGAR graph database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
⚠️  WARNING: This script will DELETE ALL DATA in the database!
This operation is irreversible. Use with caution.

Examples:
  # Delete schema with confirmation prompt
  python delete_schema.py
  
  # Delete schema without confirmation (use with caution)
  python delete_schema.py --yes
        """
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt (use with extreme caution)"
    )
    
    args = parser.parse_args()
    
    setup_logger("delete_schema")
    logger.warning("=" * 60)
    logger.warning("Neo4j EDGAR Schema Deletion")
    logger.warning("=" * 60)
    logger.warning("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    logger.warning("=" * 60)
    
    try:
        with Neo4jClient() as client:
            # Verify connectivity
            if not client.verify_connectivity():
                logger.error("Failed to connect to Neo4j. Please check your configuration.")
                return 1
            
            # Get current database statistics
            logger.info("Getting current database statistics...")
            stats_before = get_database_stats(client)
            
            logger.info("Current database state:")
            logger.info(f"  - Nodes: {stats_before['node_count']}")
            logger.info(f"  - Relationships: {stats_before['relationship_count']}")
            logger.info(f"  - Constraints: {stats_before['constraint_count']}")
            logger.info(f"  - Indexes: {stats_before['index_count']}")
            
            # Confirmation prompt (unless --yes flag is used)
            if not args.yes:
                logger.warning("")
                logger.warning("This operation will DELETE ALL DATA!")
                response = input("Are you sure you want to continue? (yes/no): ")
                if response.lower() not in ["yes", "y"]:
                    logger.info("Operation cancelled by user")
                    return 0
            
            logger.warning("")
            logger.warning("Proceeding with deletion...")
            logger.warning("")
            
            # Delete in order: data first, then constraints, then indexes
            # (Constraints and indexes may depend on data existing)
            
            # 1. Delete all data (nodes and relationships)
            delete_all_data(client)
            
            # 2. Drop all constraints
            drop_all_constraints(client)
            
            # 3. Drop all indexes
            drop_all_indexes(client)
            
            # 4. Verify deletion
            verification = verify_deletion(client)
            
            # Summary
            logger.info("")
            logger.info("=" * 60)
            if verification["is_clean"]:
                logger.info("✓ Schema deletion completed successfully!")
                logger.info("Database is now clean and ready for fresh schema setup.")
            else:
                logger.warning("⚠ Schema deletion completed with warnings.")
                logger.warning("Some elements may still remain. Check logs for details.")
            logger.info("=" * 60)
            
            return 0 if verification["is_clean"] else 1
            
    except KeyboardInterrupt:
        logger.warning("\nOperation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Schema deletion failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

