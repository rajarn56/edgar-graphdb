#!/usr/bin/env python3
"""
EDGAR data retrieval script.

Queries Neo4j database and displays EDGAR data in readable formats.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# Load environment variables
load_dotenv(dotenv_path=scripts_dir / ".env")

from utils.logger_config import setup_logger, get_logger
from utils.neo4j_client import Neo4jClient

logger = get_logger(__name__)


def get_company_info(client: Neo4jClient, ticker: str) -> Optional[Dict[str, Any]]:
    """Get company information by ticker"""
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
    result = client.execute_query(query, {"ticker": ticker.upper()})
    if result:
        return result[0]
    return None


def get_filings(
    client: Neo4jClient,
    ticker: str,
    form_type: Optional[str] = None,
    fiscal_year: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Get filings for a company"""
    query = """
    MATCH (c:Company {ticker: $ticker})<-[:FILED_BY]-(f:Filing)
    WHERE 1=1
    """
    params = {"ticker": ticker.upper()}
    
    if form_type:
        query += " AND f.form_type = $form_type"
        params["form_type"] = form_type
    
    if fiscal_year:
        query += " AND f.fiscal_year = $fiscal_year"
        params["fiscal_year"] = fiscal_year
    
    query += """
    RETURN f.accession_number AS accession_number,
           f.form_type AS form_type,
           f.filing_date AS filing_date,
           f.period_end_date AS period_end_date,
           f.fiscal_year AS fiscal_year,
           f.fiscal_quarter AS fiscal_quarter,
           f.fiscal_period AS fiscal_period,
           f.url AS url
    ORDER BY f.fiscal_year DESC, f.fiscal_quarter DESC NULLS LAST
    """
    
    return client.execute_query(query, params)


def get_section_content(
    client: Neo4jClient,
    ticker: str,
    accession_number: Optional[str] = None,
    section_item: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get section content with chunks"""
    query = """
    MATCH (c:Company {ticker: $ticker})<-[:FILED_BY]-(f:Filing)
    """
    params = {"ticker": ticker.upper()}
    
    if accession_number:
        query += " WHERE f.accession_number = $accession_number"
        params["accession_number"] = accession_number
    
    query += """
    MATCH (f)-[:CONTAINS]->(s:Section)
    """
    
    if section_item:
        query += " WHERE s.item_number = $section_item"
        params["section_item"] = section_item
    
    query += """
    OPTIONAL MATCH (s)-[:CONTAINS]->(ch:Chunk)
    WITH s, COLLECT(ch ORDER BY ch.chunk_index) AS chunks
    RETURN s.section_id AS section_id,
           s.item_number AS item_number,
           s.item_title AS item_title,
           s.content_length AS content_length,
           s.word_count AS word_count,
           f.accession_number AS filing_accession,
           f.form_type AS form_type,
           f.fiscal_year AS fiscal_year,
           chunks
    ORDER BY s.item_number
    """
    
    return client.execute_query(query, params)


def get_financial_statements(
    client: Neo4jClient,
    ticker: str,
    accession_number: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get financial statements"""
    query = """
    MATCH (c:Company {ticker: $ticker})<-[:FILED_BY]-(f:Filing)
    """
    params = {"ticker": ticker.upper()}
    
    if accession_number:
        query += " WHERE f.accession_number = $accession_number"
        params["accession_number"] = accession_number
    
    query += """
    MATCH (f)-[:CONTAINS]->(fs:FinancialStatement)
    OPTIONAL MATCH (fs)-[:HAS_LINE_ITEM]->(li:LineItem)
    OPTIONAL MATCH (li)-[:HAS_VALUE]->(v:Value)
    WITH fs, li, v
    RETURN fs.statement_id AS statement_id,
           fs.statement_type AS statement_type,
           fs.period_type AS period_type,
           fs.currency AS currency,
           COLLECT(DISTINCT {
               line_item: li.line_name,
               value: v.value,
               period: v.fiscal_year
           }) AS line_items
    ORDER BY fs.statement_type
    """
    
    return client.execute_query(query, params)


def get_node_counts(client: Neo4jClient, ticker: str) -> Dict[str, int]:
    """Get node counts for a company"""
    cik_query = """
    MATCH (c:Company {ticker: $ticker})
    RETURN c.cik AS cik
    LIMIT 1
    """
    cik_result = client.execute_query(cik_query, {"ticker": ticker.upper()})
    if not cik_result:
        return {}
    
    cik = cik_result[0]["cik"]
    
    query = """
    MATCH (c:Company {cik: $cik})<-[:FILED_BY]-(f:Filing)
    OPTIONAL MATCH (f)-[:CONTAINS]->(s:Section)
    OPTIONAL MATCH (s)-[:CONTAINS]->(ch:Chunk)
    RETURN COUNT(DISTINCT f) AS filings,
           COUNT(DISTINCT s) AS sections,
           COUNT(DISTINCT ch) AS chunks
    """
    
    result = client.execute_query(query, {"cik": cik})
    if result:
        return result[0]
    return {}


def format_tree_output(data: Dict[str, Any]) -> str:
    """Format data as tree structure"""
    output = []
    
    if "company" in data:
        company = data["company"]
        output.append(f"Company: {company.get('name', 'N/A')} ({company.get('ticker', 'N/A')})")
        output.append(f"  CIK: {company.get('cik', 'N/A')}")
        output.append(f"  Exchange: {company.get('exchange', 'N/A')}")
        output.append("")
    
    if "filings" in data:
        output.append("Filings:")
        for filing in data["filings"]:
            output.append(f"  - {filing.get('form_type', 'N/A')} {filing.get('fiscal_year', 'N/A')}")
            output.append(f"    Accession: {filing.get('accession_number', 'N/A')}")
            output.append(f"    Filing Date: {filing.get('filing_date', 'N/A')}")
            output.append(f"    Period: {filing.get('fiscal_period', 'N/A')}")
            output.append("")
    
    if "sections" in data:
        output.append("Sections:")
        for section in data["sections"]:
            output.append(f"  - {section.get('item_number', 'N/A')}: {section.get('item_title', 'N/A')}")
            output.append(f"    Content Length: {section.get('content_length', 0)} chars")
            output.append(f"    Word Count: {section.get('word_count', 0)} words")
            chunks = section.get("chunks", [])
            if chunks:
                output.append(f"    Chunks: {len(chunks)}")
            output.append("")
    
    return "\n".join(output)


def format_table_output(data: Dict[str, Any]) -> str:
    """Format data as table"""
    output = []
    
    if "filings" in data:
        output.append("Filings:")
        output.append("-" * 80)
        output.append(f"{'Form':<10} {'Year':<6} {'Quarter':<8} {'Accession':<20} {'Date':<12}")
        output.append("-" * 80)
        for filing in data["filings"]:
            form = filing.get("form_type", "N/A")
            year = str(filing.get("fiscal_year", "N/A"))
            quarter = str(filing.get("fiscal_quarter", "N/A")) if filing.get("fiscal_quarter") else "FY"
            accession = filing.get("accession_number", "N/A")[:20]
            date = str(filing.get("filing_date", "N/A"))
            output.append(f"{form:<10} {year:<6} {quarter:<8} {accession:<20} {date:<12}")
        output.append("")
    
    return "\n".join(output)


def format_json_output(data: Dict[str, Any]) -> str:
    """Format data as JSON"""
    # Convert datetime objects to strings for JSON serialization
    def json_serializer(obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    return json.dumps(data, indent=2, default=json_serializer)


def retrieve_data(
    client: Neo4jClient,
    ticker: str,
    form_type: Optional[str] = None,
    fiscal_year: Optional[int] = None,
    section: Optional[str] = None,
    output_format: str = "tree"
) -> Dict[str, Any]:
    """Retrieve and format data"""
    result = {}
    
    # Get company info
    company = get_company_info(client, ticker)
    if not company:
        logger.warning(f"Company not found for ticker: {ticker}")
        return result
    
    result["company"] = company
    
    # Get filings
    filings = get_filings(client, ticker, form_type, fiscal_year)
    result["filings"] = filings
    
    # Get sections if requested
    if section or len(filings) > 0:
        accession = filings[0]["accession_number"] if filings else None
        sections = get_section_content(client, ticker, accession, section)
        result["sections"] = sections
    
    # Get node counts
    counts = get_node_counts(client, ticker)
    result["counts"] = counts
    
    return result


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Retrieve EDGAR data from Neo4j")
    parser.add_argument("--ticker", required=True, help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("--form-type", help="Form type filter (optional)")
    parser.add_argument("--fiscal-year", type=int, help="Fiscal year filter (optional)")
    parser.add_argument("--section", help="Section/item number (e.g., 'Item 7')")
    parser.add_argument("--format", choices=["tree", "table", "json"], default="tree",
                       help="Output format (default: tree)")
    
    args = parser.parse_args()
    
    setup_logger("retrieve")
    logger.info("=" * 60)
    logger.info("EDGAR Data Retrieval")
    logger.info("=" * 60)
    logger.info(f"Ticker: {args.ticker}")
    if args.form_type:
        logger.info(f"Form Type: {args.form_type}")
    if args.fiscal_year:
        logger.info(f"Fiscal Year: {args.fiscal_year}")
    
    try:
        with Neo4jClient() as client:
            # Verify connectivity
            if not client.verify_connectivity():
                logger.error("Failed to connect to Neo4j. Please check your configuration.")
                return 1
            
            # Retrieve data
            data = retrieve_data(
                client,
                args.ticker,
                args.form_type,
                args.fiscal_year,
                args.section,
                args.format
            )
            
            # Format and display
            if args.format == "json":
                print(format_json_output(data))
            elif args.format == "table":
                print(format_table_output(data))
            else:
                print(format_tree_output(data))
            
            logger.info("Retrieval completed successfully!")
            return 0
            
    except Exception as e:
        logger.error(f"Retrieval failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

