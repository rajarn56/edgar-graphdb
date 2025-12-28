#!/usr/bin/env python3
"""
EDGAR data ingestion script.

Retrieves EDGAR data for a ticker, transforms to graph format, generates embeddings,
and writes to Neo4j database.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# Load environment variables
load_dotenv(dotenv_path=scripts_dir / ".env")

from utils.logger_config import setup_logger, get_logger
from utils.neo4j_client import Neo4jClient
from utils.edgar_client import EdgarClient
from utils.data_transformer import DataTransformer
from utils.embedding_generator import EmbeddingGenerator

logger = get_logger(__name__)


def check_existing_filing(client: Neo4jClient, accession_number: str) -> bool:
    """Check if filing already exists in database"""
    query = """
    MATCH (f:Filing {accession_number: $accession_number})
    RETURN f.accession_number AS accession
    LIMIT 1
    """
    result = client.execute_query(query, {"accession_number": accession_number})
    return len(result) > 0


def create_company_node(client: Neo4jClient, company_node: dict) -> None:
    """Create or update Company node"""
    props = company_node["properties"]
    query = """
    MERGE (c:Company {cik: $cik})
    SET c.name = $name,
        c.ticker = $ticker,
        c.sic = $sic,
        c.sic_description = $sic_description,
        c.exchange = $exchange,
        c.incorporation_state = $incorporation_state,
        c.updated_at = datetime()
    ON CREATE SET c.created_at = datetime()
    RETURN c.cik AS cik
    """
    client.execute_write(query, props)
    logger.info(f"Created/updated Company node: {props['cik']} ({props['name']})")


def create_filing_node(client: Neo4jClient, filing_node: dict, period_node: dict, company_cik: str) -> None:
    """Create or update Filing node and Period node, create relationships"""
    filing_props = filing_node["properties"]
    
    # Create/update Filing node
    query = """
    MERGE (f:Filing {accession_number: $accession_number})
    SET f.form_type = $form_type,
        f.filing_date = date($filing_date),
        f.period_end_date = date($period_end_date),
        f.fiscal_year = $fiscal_year,
        f.fiscal_quarter = $fiscal_quarter,
        f.fiscal_period = $fiscal_period,
        f.url = $url,
        f.company_cik = $company_cik,
        f.company_name = $company_name,
        f.company_ticker = $company_ticker,
        f.updated_at = datetime(),
        f.ingestion_status = 'processing'
    ON CREATE SET f.created_at = datetime()
    WITH f
    MATCH (c:Company {cik: $company_cik})
    MERGE (f)-[:FILED_BY {filed_at: datetime()}]->(c)
    RETURN f.accession_number AS accession
    """
    
    # Prepare parameters
    params = {
        **filing_props,
        "company_cik": company_cik,
        "filing_date": filing_props.get("filing_date") or "",
        "period_end_date": filing_props.get("period_end_date") or "",
    }
    
    client.execute_write(query, params)
    logger.info(f"Created/updated Filing node: {filing_props['accession_number']}")
    
    # Create Period node and relationship if period data exists
    if period_node:
        period_props = period_node["properties"]
        period_query = """
        MERGE (p:Period {period_id: $period_id})
        SET p.fiscal_year = $fiscal_year,
            p.fiscal_quarter = $fiscal_quarter,
            p.period_start = date($period_start),
            p.period_end = date($period_end),
            p.period_type = $period_type
        ON CREATE SET p.created_at = datetime()
        WITH p
        MATCH (f:Filing {accession_number: $accession_number})
        MERGE (f)-[:FOR_PERIOD]->(p)
        RETURN p.period_id AS period_id
        """
        period_params = {
            **period_props,
            "accession_number": filing_props["accession_number"],
            "period_start": period_props.get("period_start") or "",
            "period_end": period_props.get("period_end") or "",
        }
        client.execute_write(period_query, period_params)
        logger.info(f"Created/updated Period node: {period_props['period_id']}")


def create_section_node(client: Neo4jClient, section_node: dict, filing_accession: str, order: int) -> None:
    """Create or update Section node and create CONTAINS relationship"""
    props = section_node["properties"]
    labels = section_node.get("labels", ["Section"])
    label_str = ":".join(labels)
    
    query = f"""
    MERGE (s:{label_str} {{section_id: $section_id}})
    SET s.item_number = $item_number,
        s.item_title = $item_title,
        s.content = $content,
        s.content_length = $content_length,
        s.word_count = $word_count,
        s.company_cik = $company_cik,
        s.fiscal_year = $fiscal_year,
        s.form_type = $form_type,
        s.updated_at = datetime()
    ON CREATE SET s.created_at = datetime()
    """
    
    # Add form-specific properties
    if "Form8KItem" in labels:
        query += """
        SET s.item_code = $item_code,
            s.event_type = $event_type
        """
    
    query += """
    WITH s
    MATCH (f:Filing {accession_number: $filing_accession})
    MERGE (f)-[:CONTAINS {order: $order}]->(s)
    RETURN s.section_id AS section_id
    """
    
    params = {
        **props,
        "filing_accession": filing_accession,
        "order": order,
    }
    
    client.execute_write(query, params)
    logger.debug(f"Created/updated Section node: {props['section_id']}")


def create_chunk_nodes(
    client: Neo4jClient,
    chunks: list,
    section_id: str,
    company_cik: str,
    embedding_generator: EmbeddingGenerator
) -> None:
    """Create Chunk nodes with embeddings"""
    logger.info(f"Creating {len(chunks)} chunk nodes for section {section_id}...")
    
    # Generate embeddings for all chunks
    chunk_texts = []
    for chunk in chunks:
        chunk_props = chunk["properties"]
        # Prepare embedding input with context
        embedding_text = embedding_generator.prepare_embedding_input(
            chunk_content=chunk_props["content"],
            context_before=chunk_props.get("context_before"),
            context_after=chunk_props.get("context_after"),
            company_name=chunk_props.get("company_name"),
            company_ticker=chunk_props.get("company_ticker"),
            form_type=chunk_props.get("form_type"),
            fiscal_year=chunk_props.get("fiscal_year"),
            section_item=chunk_props.get("section_item"),
        )
        chunk_texts.append(embedding_text)
    
    # Generate embeddings in batch
    logger.info("Generating embeddings...")
    embeddings = embedding_generator.generate_embeddings_batch(chunk_texts)
    
    # Create chunks with embeddings
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_props = chunk["properties"]
        chunk_props["embedding"] = embedding
        chunk_props["embedding_model"] = embedding_generator.embedding_model
        chunk_props["embedding_dimension"] = len(embedding)
        chunk_props["embedding_created_at"] = datetime.now()
        
        # Create chunk node
        query = """
        MERGE (ch:Chunk {chunk_id: $chunk_id})
        SET ch.chunk_index = $chunk_index,
            ch.content = $content,
            ch.content_length = $content_length,
            ch.word_count = $word_count,
            ch.token_count = $token_count,
            ch.chunk_type = $chunk_type,
            ch.semantic_type = $semantic_type,
            ch.context_before = $context_before,
            ch.context_after = $context_after,
            ch.embedding = $embedding,
            ch.embedding_model = $embedding_model,
            ch.embedding_dimension = $embedding_dimension,
            ch.embedding_created_at = datetime(),
            ch.company_cik = $company_cik,
            ch.fiscal_year = $fiscal_year,
            ch.fiscal_quarter = $fiscal_quarter,
            ch.form_type = $form_type,
            ch.section_item = $section_item,
            ch.created_at = datetime()
        WITH ch
        MATCH (s:Section {section_id: $section_id})
        MERGE (s)-[:CONTAINS]->(ch)
        WITH ch
        MATCH (c:Company {cik: $company_cik})
        MERGE (ch)-[:FROM_COMPANY]->(c)
        RETURN ch.chunk_id AS chunk_id
        """
        
        params = {
            **chunk_props,
            "section_id": section_id,
            "company_cik": company_cik,
        }
        
        client.execute_write(query, params)
        
        if (idx + 1) % 10 == 0:
            logger.info(f"Created {idx + 1}/{len(chunks)} chunks...")


def ingest_filing(
    client: Neo4jClient,
    edgar_client: EdgarClient,
    transformer: DataTransformer,
    embedding_generator: EmbeddingGenerator,
    ticker: str,
    form_type: str,
    fiscal_year: Optional[int],
    force: bool = False
) -> bool:
    """Main ingestion function"""
    logger.info(f"Ingesting filing for {ticker} ({form_type})...")
    
    # Retrieve EDGAR data
    logger.info("Retrieving EDGAR data...")
    edgar_data = edgar_client.get_filing(ticker, form_type, fiscal_year)
    if not edgar_data:
        logger.error(f"Failed to retrieve EDGAR data for {ticker}")
        return False
    
    # Transform data
    logger.info("Transforming data to graph format...")
    transformed = transformer.transform_edgar_data(edgar_data)
    
    # Check if filing already exists
    filing_accession = transformed["filing"]["properties"]["accession_number"]
    if check_existing_filing(client, filing_accession) and not force:
        logger.info(f"Filing {filing_accession} already exists. Use --force to re-ingest.")
        return True
    
    # Create company node
    logger.info("Creating company node...")
    company_node = transformed["company"]
    company_cik = company_node["properties"]["cik"]
    create_company_node(client, company_node)
    
    # Create filing and period nodes
    logger.info("Creating filing node...")
    create_filing_node(
        client,
        transformed["filing"],
        transformed["period"],
        company_cik
    )
    
    # Create sections and chunks
    logger.info(f"Creating {len(transformed['sections'])} sections...")
    for idx, section_node in enumerate(transformed["sections"]):
        section_id = section_node["properties"]["section_id"]
        
        # Find chunks for this section
        section_chunks = [
            chunk for chunk in transformed["chunks"]
            if chunk["properties"]["chunk_id"].startswith(section_id)
        ]
        
        # Create section node
        create_section_node(client, section_node, filing_accession, idx)
        
        # Create chunk nodes with embeddings
        if section_chunks:
            create_chunk_nodes(
                client,
                section_chunks,
                section_id,
                company_cik,
                embedding_generator
            )
    
    # Update filing status
    query = """
    MATCH (f:Filing {accession_number: $accession_number})
    SET f.ingestion_status = 'completed',
        f.updated_at = datetime()
    RETURN f.accession_number AS accession
    """
    client.execute_write(query, {"accession_number": filing_accession})
    
    logger.info(f"Successfully ingested filing {filing_accession}")
    return True


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Ingest EDGAR data into Neo4j graph database")
    parser.add_argument("--ticker", required=True, help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("--form-type", default="10-K", help="Form type (default: 10-K)")
    parser.add_argument("--fiscal-year", type=int, help="Specific fiscal year (optional)")
    parser.add_argument("--force", action="store_true", help="Force re-ingestion even if exists")
    
    args = parser.parse_args()
    
    setup_logger("ingest")
    logger.info("=" * 60)
    logger.info("EDGAR Data Ingestion")
    logger.info("=" * 60)
    logger.info(f"Ticker: {args.ticker}")
    logger.info(f"Form Type: {args.form_type}")
    if args.fiscal_year:
        logger.info(f"Fiscal Year: {args.fiscal_year}")
    
    try:
        # Initialize clients
        neo4j_client = Neo4jClient()
        edgar_client = EdgarClient()
        transformer = DataTransformer()
        embedding_generator = EmbeddingGenerator()
        
        with neo4j_client:
            # Verify connectivity
            if not neo4j_client.verify_connectivity():
                logger.error("Failed to connect to Neo4j. Please check your configuration.")
                return 1
            
            # Ingest filing
            success = ingest_filing(
                neo4j_client,
                edgar_client,
                transformer,
                embedding_generator,
                args.ticker,
                args.form_type,
                args.fiscal_year,
                args.force
            )
            
            if success:
                logger.info("=" * 60)
                logger.info("Ingestion completed successfully!")
                logger.info("=" * 60)
                return 0
            else:
                logger.error("Ingestion failed!")
                return 1
                
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

