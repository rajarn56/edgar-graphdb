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
    
    # Log data field mapping and types for debugging
    logger.debug("=" * 60)
    logger.debug("Creating Company Node - Data Mapping Verification")
    logger.debug("=" * 60)
    logger.debug(f"CIK: {props.get('cik')} (type: {type(props.get('cik')).__name__})")
    logger.debug(f"Name: {props.get('name')} (type: {type(props.get('name')).__name__})")
    logger.debug(f"Ticker: {props.get('ticker')} (type: {type(props.get('ticker')).__name__})")
    logger.debug(f"SIC: {props.get('sic')} (type: {type(props.get('sic')).__name__})")
    logger.debug(f"SIC Description: {props.get('sic_description')} (type: {type(props.get('sic_description')).__name__})")
    logger.debug(f"Exchange: {props.get('exchange')} (type: {type(props.get('exchange')).__name__})")
    logger.debug(f"Incorporation State: {props.get('incorporation_state')} (type: {type(props.get('incorporation_state')).__name__})")
    
    # Validate required fields
    required_fields = ["cik", "name"]
    missing_fields = [field for field in required_fields if not props.get(field)]
    if missing_fields:
        logger.warning(f"Missing required Company fields: {missing_fields}")
    
    # Check for empty strings that might indicate missing data
    empty_fields = [k for k, v in props.items() if isinstance(v, str) and not v.strip() and k not in ["cik"]]
    if empty_fields:
        logger.debug(f"Empty string fields (may indicate missing data): {empty_fields}")
    
    # Validate data types
    if props.get("cik") and not isinstance(props["cik"], str):
        logger.warning(f"CIK type mismatch: expected str, got {type(props['cik']).__name__}")
    if props.get("name") and not isinstance(props["name"], str):
        logger.warning(f"Name type mismatch: expected str, got {type(props['name']).__name__}")
    
    query = """
    MERGE (c:Company {cik: $cik})
    ON CREATE SET c.created_at = datetime(),
        c.name = $name,
        c.ticker = $ticker,
        c.sic = $sic,
        c.sic_description = $sic_description,
        c.exchange = $exchange,
        c.incorporation_state = $incorporation_state,
        c.updated_at = datetime()
    ON MATCH SET c.name = $name,
        c.ticker = $ticker,
        c.sic = $sic,
        c.sic_description = $sic_description,
        c.exchange = $exchange,
        c.incorporation_state = $incorporation_state,
        c.updated_at = datetime()
    RETURN c.cik AS cik
    """
    
    logger.debug(f"Executing Company node write query with {len(props)} parameters")
    client.execute_write(query, props)
    logger.info(f"Created/updated Company node: {props['cik']} ({props['name']})")


def create_filing_node(client: Neo4jClient, filing_node: dict, period_node: dict, company_cik: str) -> None:
    """Create or update Filing node and Period node, create relationships"""
    filing_props = filing_node["properties"]
    
    # Log data field mapping and types for debugging
    logger.debug("=" * 60)
    logger.debug("Creating Filing Node - Data Mapping Verification")
    logger.debug("=" * 60)
    logger.debug(f"Accession Number: {filing_props.get('accession_number')} (type: {type(filing_props.get('accession_number')).__name__})")
    logger.debug(f"Form Type: {filing_props.get('form_type')} (type: {type(filing_props.get('form_type')).__name__})")
    logger.debug(f"Filing Date (raw): {filing_props.get('filing_date')} (type: {type(filing_props.get('filing_date')).__name__})")
    logger.debug(f"Period End Date (raw): {filing_props.get('period_end_date')} (type: {type(filing_props.get('period_end_date')).__name__})")
    logger.debug(f"Fiscal Year: {filing_props.get('fiscal_year')} (type: {type(filing_props.get('fiscal_year')).__name__})")
    logger.debug(f"Fiscal Quarter: {filing_props.get('fiscal_quarter')} (type: {type(filing_props.get('fiscal_quarter')).__name__})")
    logger.debug(f"Fiscal Period: {filing_props.get('fiscal_period')} (type: {type(filing_props.get('fiscal_period')).__name__})")
    logger.debug(f"URL: {filing_props.get('url')} (type: {type(filing_props.get('url')).__name__})")
    logger.debug(f"Company CIK: {company_cik} (type: {type(company_cik).__name__})")
    
    # Get date values and validate - handle empty strings
    filing_date = filing_props.get("filing_date")
    period_end_date = filing_props.get("period_end_date")
    
    # Log original date values
    logger.debug(f"Original filing_date value: {repr(filing_date)}")
    logger.debug(f"Original period_end_date value: {repr(period_end_date)}")
    
    # Normalize empty strings to None
    filing_date = filing_date.strip() if filing_date and filing_date.strip() else None
    period_end_date = period_end_date.strip() if period_end_date and period_end_date.strip() else None
    
    # Log normalized date values
    logger.debug(f"Normalized filing_date: {repr(filing_date)}")
    logger.debug(f"Normalized period_end_date: {repr(period_end_date)}")
    
    # Validate date formats if dates are provided
    if filing_date:
        try:
            from datetime import datetime as dt
            dt.strptime(filing_date, "%Y-%m-%d")
            logger.debug(f"Filing date format validated: {filing_date}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Filing date format may be invalid: {filing_date} (error: {e})")
    
    if period_end_date:
        try:
            from datetime import datetime as dt
            dt.strptime(period_end_date, "%Y-%m-%d")
            logger.debug(f"Period end date format validated: {period_end_date}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Period end date format may be invalid: {period_end_date} (error: {e})")
    
    # Validate required fields
    required_fields = ["accession_number", "form_type"]
    missing_fields = [field for field in required_fields if not filing_props.get(field)]
    if missing_fields:
        logger.warning(f"Missing required Filing fields: {missing_fields}")
    
    # Validate data types
    if filing_props.get("fiscal_year") is not None and not isinstance(filing_props["fiscal_year"], int):
        logger.warning(f"Fiscal year type mismatch: expected int, got {type(filing_props['fiscal_year']).__name__}")
    if filing_props.get("fiscal_quarter") is not None and not isinstance(filing_props["fiscal_quarter"], int):
        logger.warning(f"Fiscal quarter type mismatch: expected int, got {type(filing_props['fiscal_quarter']).__name__}")
    
    # Create/update Filing node with conditional date handling
    query = """
    MERGE (f:Filing {accession_number: $accession_number})
    ON CREATE SET f.created_at = datetime(),
        f.form_type = $form_type,
        f.filing_date = CASE WHEN $filing_date IS NOT NULL AND $filing_date <> '' THEN date($filing_date) ELSE null END,
        f.period_end_date = CASE WHEN $period_end_date IS NOT NULL AND $period_end_date <> '' THEN date($period_end_date) ELSE null END,
        f.fiscal_year = $fiscal_year,
        f.fiscal_quarter = $fiscal_quarter,
        f.fiscal_period = $fiscal_period,
        f.url = $url,
        f.company_cik = $company_cik,
        f.company_name = $company_name,
        f.company_ticker = $company_ticker,
        f.updated_at = datetime(),
        f.ingestion_status = 'processing'
    ON MATCH SET f.form_type = $form_type,
        f.filing_date = CASE WHEN $filing_date IS NOT NULL AND $filing_date <> '' THEN date($filing_date) ELSE null END,
        f.period_end_date = CASE WHEN $period_end_date IS NOT NULL AND $period_end_date <> '' THEN date($period_end_date) ELSE null END,
        f.fiscal_year = $fiscal_year,
        f.fiscal_quarter = $fiscal_quarter,
        f.fiscal_period = $fiscal_period,
        f.url = $url,
        f.company_cik = $company_cik,
        f.company_name = $company_name,
        f.company_ticker = $company_ticker,
        f.updated_at = datetime(),
        f.ingestion_status = 'processing'
    WITH f
    MATCH (c:Company {cik: $company_cik})
    MERGE (f)-[:FILED_BY {filed_at: datetime()}]->(c)
    RETURN f.accession_number AS accession
    """
    
    # Prepare parameters
    params = {
        **filing_props,
        "company_cik": company_cik,
        "filing_date": filing_date or "",
        "period_end_date": period_end_date or "",
    }
    
    # Log final parameters being sent to database
    logger.debug(f"Filing node parameters: accession_number={params.get('accession_number')}, "
                f"filing_date={params.get('filing_date')}, period_end_date={params.get('period_end_date')}, "
                f"fiscal_year={params.get('fiscal_year')}, fiscal_quarter={params.get('fiscal_quarter')}")
    
    logger.debug(f"Executing Filing node write query with {len(params)} parameters")
    client.execute_write(query, params)
    logger.info(f"Created/updated Filing node: {filing_props['accession_number']}")
    
    # Create Period node and relationship if period data exists
    if period_node:
        period_props = period_node["properties"]
        
        # Log Period node data mapping
        logger.debug("=" * 60)
        logger.debug("Creating Period Node - Data Mapping Verification")
        logger.debug("=" * 60)
        logger.debug(f"Period ID: {period_props.get('period_id')} (type: {type(period_props.get('period_id')).__name__})")
        logger.debug(f"Fiscal Year: {period_props.get('fiscal_year')} (type: {type(period_props.get('fiscal_year')).__name__})")
        logger.debug(f"Fiscal Quarter: {period_props.get('fiscal_quarter')} (type: {type(period_props.get('fiscal_quarter')).__name__})")
        logger.debug(f"Period Start (raw): {period_props.get('period_start')} (type: {type(period_props.get('period_start')).__name__})")
        logger.debug(f"Period End (raw): {period_props.get('period_end')} (type: {type(period_props.get('period_end')).__name__})")
        logger.debug(f"Period Type: {period_props.get('period_type')} (type: {type(period_props.get('period_type')).__name__})")
        
        # Get date values and validate - handle empty strings
        period_start = period_props.get("period_start")
        period_end = period_props.get("period_end")
        
        # Log original date values
        logger.debug(f"Original period_start value: {repr(period_start)}")
        logger.debug(f"Original period_end value: {repr(period_end)}")
        
        # Normalize empty strings to None
        period_start = period_start.strip() if period_start and period_start.strip() else None
        period_end = period_end.strip() if period_end and period_end.strip() else None
        
        # Log normalized date values
        logger.debug(f"Normalized period_start: {repr(period_start)}")
        logger.debug(f"Normalized period_end: {repr(period_end)}")
        
        # Validate date formats if dates are provided
        if period_start:
            try:
                from datetime import datetime as dt
                dt.strptime(period_start, "%Y-%m-%d")
                logger.debug(f"Period start date format validated: {period_start}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Period start date format may be invalid: {period_start} (error: {e})")
        
        if period_end:
            try:
                from datetime import datetime as dt
                dt.strptime(period_end, "%Y-%m-%d")
                logger.debug(f"Period end date format validated: {period_end}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Period end date format may be invalid: {period_end} (error: {e})")
        
        # Validate required fields
        required_fields = ["period_id", "fiscal_year", "period_type"]
        missing_fields = [field for field in required_fields if not period_props.get(field)]
        if missing_fields:
            logger.warning(f"Missing required Period fields: {missing_fields}")
        
        period_query = """
        MERGE (p:Period {period_id: $period_id})
        ON CREATE SET p.created_at = datetime(),
            p.fiscal_year = $fiscal_year,
            p.fiscal_quarter = $fiscal_quarter,
            p.period_start = CASE WHEN $period_start IS NOT NULL AND $period_start <> '' THEN date($period_start) ELSE null END,
            p.period_end = CASE WHEN $period_end IS NOT NULL AND $period_end <> '' THEN date($period_end) ELSE null END,
            p.period_type = $period_type
        ON MATCH SET p.fiscal_year = $fiscal_year,
            p.fiscal_quarter = $fiscal_quarter,
            p.period_start = CASE WHEN $period_start IS NOT NULL AND $period_start <> '' THEN date($period_start) ELSE null END,
            p.period_end = CASE WHEN $period_end IS NOT NULL AND $period_end <> '' THEN date($period_end) ELSE null END,
            p.period_type = $period_type
        WITH p
        MATCH (f:Filing {accession_number: $accession_number})
        MERGE (f)-[:FOR_PERIOD]->(p)
        RETURN p.period_id AS period_id
        """
        period_params = {
            **period_props,
            "accession_number": filing_props["accession_number"],
            "period_start": period_start or "",
            "period_end": period_end or "",
        }
        
        # Log final parameters being sent to database
        logger.debug(f"Period node parameters: period_id={period_params.get('period_id')}, "
                    f"period_start={period_params.get('period_start')}, period_end={period_params.get('period_end')}, "
                    f"fiscal_year={period_params.get('fiscal_year')}, fiscal_quarter={period_params.get('fiscal_quarter')}")
        
        logger.debug(f"Executing Period node write query with {len(period_params)} parameters")
        client.execute_write(period_query, period_params)
        logger.info(f"Created/updated Period node: {period_props['period_id']}")


def create_section_node(client: Neo4jClient, section_node: dict, filing_accession: str, order: int) -> None:
    """Create or update Section node and create CONTAINS relationship"""
    props = section_node["properties"]
    labels = section_node.get("labels", ["Section"])
    label_str = ":".join(labels)
    
    # Log Section node data mapping (only for first few sections to avoid log spam)
    if order < 3:
        logger.debug("=" * 60)
        logger.debug(f"Creating Section Node #{order} - Data Mapping Verification")
        logger.debug("=" * 60)
        logger.debug(f"Section ID: {props.get('section_id')} (type: {type(props.get('section_id')).__name__})")
        logger.debug(f"Labels: {labels}")
        logger.debug(f"Item Number: {props.get('item_number')} (type: {type(props.get('item_number')).__name__})")
        logger.debug(f"Item Title: {props.get('item_title', '')[:50]}... (type: {type(props.get('item_title')).__name__})")
        logger.debug(f"Content Length: {props.get('content_length')} (type: {type(props.get('content_length')).__name__})")
        logger.debug(f"Word Count: {props.get('word_count')} (type: {type(props.get('word_count')).__name__})")
        logger.debug(f"Company CIK: {props.get('company_cik')} (type: {type(props.get('company_cik')).__name__})")
        logger.debug(f"Fiscal Year: {props.get('fiscal_year')} (type: {type(props.get('fiscal_year')).__name__})")
        logger.debug(f"Form Type: {props.get('form_type')} (type: {type(props.get('form_type')).__name__})")
        
        # Validate data types
        if props.get("content_length") is not None and not isinstance(props["content_length"], int):
            logger.warning(f"Content length type mismatch: expected int, got {type(props['content_length']).__name__}")
        if props.get("word_count") is not None and not isinstance(props["word_count"], int):
            logger.warning(f"Word count type mismatch: expected int, got {type(props['word_count']).__name__}")
        
        # Check for form-specific properties
        if "Form8KItem" in labels:
            logger.debug(f"Form8KItem properties: item_code={props.get('item_code')}, event_type={props.get('event_type')}")
    
    # Build base query
    base_on_create = """s.created_at = datetime(),
        s.item_number = $item_number,
        s.item_title = $item_title,
        s.content = $content,
        s.content_length = $content_length,
        s.word_count = $word_count,
        s.company_cik = $company_cik,
        s.fiscal_year = $fiscal_year,
        s.form_type = $form_type,
        s.updated_at = datetime()"""
    
    base_on_match = """s.item_number = $item_number,
        s.item_title = $item_title,
        s.content = $content,
        s.content_length = $content_length,
        s.word_count = $word_count,
        s.company_cik = $company_cik,
        s.fiscal_year = $fiscal_year,
        s.form_type = $form_type,
        s.updated_at = datetime()"""
    
    # Add form-specific properties for Form8KItem
    if "Form8KItem" in labels:
        base_on_create += ",\n        s.item_code = $item_code,\n        s.event_type = $event_type"
        base_on_match += ",\n        s.item_code = $item_code,\n        s.event_type = $event_type"
    
    query = f"""
    MERGE (s:{label_str} {{section_id: $section_id}})
    ON CREATE SET {base_on_create}
    ON MATCH SET {base_on_match}
    WITH s
    MATCH (f:Filing {{accession_number: $filing_accession}})
    MERGE (f)-[:CONTAINS {{order: $order}}]->(s)
    RETURN s.section_id AS section_id
    """
    
    params = {
        **props,
        "filing_accession": filing_accession,
        "order": order,
    }
    
    if order < 3:
        logger.debug(f"Section node parameters: section_id={params.get('section_id')}, "
                    f"item_number={params.get('item_number')}, content_length={params.get('content_length')}, "
                    f"word_count={params.get('word_count')}")
        logger.debug(f"Executing Section node write query with {len(params)} parameters")
    
    client.execute_write(query, params)
    if order < 3:
        logger.debug(f"Created/updated Section node: {props['section_id']}")
    else:
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
        
        # Log Chunk node data mapping (only for first chunk to avoid log spam)
        if idx == 0:
            logger.debug("=" * 60)
            logger.debug("Creating Chunk Node - Data Mapping Verification")
            logger.debug("=" * 60)
            logger.debug(f"Chunk ID: {chunk_props.get('chunk_id')} (type: {type(chunk_props.get('chunk_id')).__name__})")
            logger.debug(f"Chunk Index: {chunk_props.get('chunk_index')} (type: {type(chunk_props.get('chunk_index')).__name__})")
            logger.debug(f"Content Length: {chunk_props.get('content_length')} (type: {type(chunk_props.get('content_length')).__name__})")
            logger.debug(f"Word Count: {chunk_props.get('word_count')} (type: {type(chunk_props.get('word_count')).__name__})")
            logger.debug(f"Token Count: {chunk_props.get('token_count')} (type: {type(chunk_props.get('token_count')).__name__})")
            logger.debug(f"Chunk Type: {chunk_props.get('chunk_type')} (type: {type(chunk_props.get('chunk_type')).__name__})")
            logger.debug(f"Semantic Type: {chunk_props.get('semantic_type')} (type: {type(chunk_props.get('semantic_type')).__name__})")
            logger.debug(f"Embedding Dimension: {chunk_props.get('embedding_dimension')} (type: {type(chunk_props.get('embedding_dimension')).__name__})")
            logger.debug(f"Embedding Model: {chunk_props.get('embedding_model')} (type: {type(chunk_props.get('embedding_model')).__name__})")
            logger.debug(f"Company CIK: {chunk_props.get('company_cik')} (type: {type(chunk_props.get('company_cik')).__name__})")
            logger.debug(f"Fiscal Year: {chunk_props.get('fiscal_year')} (type: {type(chunk_props.get('fiscal_year')).__name__})")
            
            # Validate embedding
            if embedding:
                logger.debug(f"Embedding shape: {len(embedding)} dimensions")
                if all(x == 0 for x in embedding[:10]):  # Check first 10 values
                    logger.warning("Embedding appears to be all zeros - check embedding generation")
            else:
                logger.error("Embedding is None or empty!")
            
            # Validate data types
            if chunk_props.get("chunk_index") is not None and not isinstance(chunk_props["chunk_index"], int):
                logger.warning(f"Chunk index type mismatch: expected int, got {type(chunk_props['chunk_index']).__name__}")
            if chunk_props.get("token_count") is not None and not isinstance(chunk_props["token_count"], int):
                logger.warning(f"Token count type mismatch: expected int, got {type(chunk_props['token_count']).__name__}")
            if chunk_props.get("embedding_dimension") is not None and not isinstance(chunk_props["embedding_dimension"], int):
                logger.warning(f"Embedding dimension type mismatch: expected int, got {type(chunk_props['embedding_dimension']).__name__}")
        
        # Create chunk node
        query = """
        MERGE (ch:Chunk {chunk_id: $chunk_id})
        ON CREATE SET ch.created_at = datetime(),
            ch.chunk_index = $chunk_index,
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
            ch.section_item = $section_item
        ON MATCH SET ch.chunk_index = $chunk_index,
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
            ch.section_item = $section_item
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
        
        if idx == 0:
            logger.debug(f"Chunk node parameters: chunk_id={params.get('chunk_id')}, "
                        f"chunk_index={params.get('chunk_index')}, content_length={params.get('content_length')}, "
                        f"embedding_dimension={params.get('embedding_dimension')}")
            logger.debug(f"Executing Chunk node write query with {len(params)} parameters")
        
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
    
    # Log raw EDGAR data structure for debugging
    logger.debug("=" * 60)
    logger.debug("Raw EDGAR Data Structure")
    logger.debug("=" * 60)
    logger.debug(f"Company keys: {list(edgar_data.get('company', {}).keys())}")
    logger.debug(f"Filing keys: {list(edgar_data.get('filing', {}).keys())}")
    logger.debug(f"Filing form: {edgar_data.get('filing', {}).get('form')}")
    logger.debug(f"Filing accession_no: {edgar_data.get('filing', {}).get('accession_no')}")
    logger.debug(f"Filing filing_date: {edgar_data.get('filing', {}).get('filing_date')}")
    logger.debug(f"Filing period_of_report: {edgar_data.get('filing', {}).get('period_of_report')}")
    logger.debug(f"Number of items/sections: {len(edgar_data.get('filing', {}).get('items', []))}")
    if edgar_data.get('filing', {}).get('items'):
        logger.debug(f"First item keys: {list(edgar_data['filing']['items'][0].keys())}")
    
    transformed = transformer.transform_edgar_data(edgar_data)
    
    # Log transformed data structure for debugging
    logger.debug("=" * 60)
    logger.debug("Transformed Data Structure")
    logger.debug("=" * 60)
    logger.debug(f"Company node properties: {list(transformed.get('company', {}).get('properties', {}).keys())}")
    logger.debug(f"Filing node properties: {list(transformed.get('filing', {}).get('properties', {}).keys())}")
    logger.debug(f"Period node: {transformed.get('period') is not None}")
    logger.debug(f"Number of sections: {len(transformed.get('sections', []))}")
    logger.debug(f"Number of chunks: {len(transformed.get('chunks', []))}")
    if transformed.get('sections'):
        logger.debug(f"First section properties: {list(transformed['sections'][0].get('properties', {}).keys())}")
    if transformed.get('chunks'):
        logger.debug(f"First chunk properties: {list(transformed['chunks'][0].get('properties', {}).keys())}")
    
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

