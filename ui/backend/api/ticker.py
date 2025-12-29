"""
Ticker-specific API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import sys
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.neo4j_service import Neo4jGraphService
from models.graph import CompanyInfo, FilingInfo, GraphStats
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


@router.get("/ticker/{ticker}/info", response_model=CompanyInfo)
async def get_ticker_info(ticker: str):
    """
    Get company information for a ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL)
    
    Returns:
        Company information
    """
    start_time = time.time()
    logger.info(f"Getting company info for ticker: {ticker}")
    
    try:
        service = get_service()
        company_info = service.get_company_info(ticker)
        
        if not company_info:
            logger.warning(f"Company not found for ticker: {ticker}")
            raise HTTPException(status_code=404, detail=f"Company not found for ticker: {ticker}")
        
        elapsed = time.time() - start_time
        logger.info(f"Company info retrieved for {ticker} in {elapsed:.3f}s")
        
        return company_info
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"Error getting company info for {ticker} after {elapsed:.3f}s: {str(e)}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ticker/{ticker}/filings", response_model=List[FilingInfo])
async def get_ticker_filings(
    ticker: str,
    form_type: Optional[str] = Query(None, description="Filter by form type (e.g., 10-K)")
):
    """
    Get all filings for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        form_type: Optional form type filter
    
    Returns:
        List of filing information
    """
    start_time = time.time()
    logger.info(f"Getting filings for ticker: {ticker}, form_type: {form_type}")
    
    try:
        service = get_service()
        filings = service.get_filings(ticker, form_type)
        
        elapsed = time.time() - start_time
        logger.info(f"Retrieved {len(filings)} filings for {ticker} in {elapsed:.3f}s")
        
        return filings
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"Error getting filings for {ticker} after {elapsed:.3f}s: {str(e)}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ticker/{ticker}/stats", response_model=GraphStats)
async def get_ticker_stats(ticker: str):
    """
    Get graph statistics for a ticker.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Graph statistics including node counts
    """
    start_time = time.time()
    logger.info(f"Getting stats for ticker: {ticker}")
    
    try:
        service = get_service()
        stats = service.get_graph_stats(ticker)
        
        if not stats:
            logger.warning(f"Company not found for ticker: {ticker}")
            raise HTTPException(status_code=404, detail=f"Company not found for ticker: {ticker}")
        
        elapsed = time.time() - start_time
        logger.info(
            f"Stats retrieved for {ticker}: "
            f"{stats.filings_count} filings, {stats.sections_count} sections, "
            f"{stats.chunks_count} chunks in {elapsed:.3f}s"
        )
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"Error getting stats for {ticker} after {elapsed:.3f}s: {str(e)}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))

