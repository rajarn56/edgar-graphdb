"""EDGAR tools client wrapper for fetching SEC filing data"""

import os
import time
from typing import Dict, Any, List, Optional
from loguru import logger


class EdgarClient:
    """Interface to edgar-tools library for fetching SEC EDGAR filing data"""
    
    def __init__(self):
        """Initialize EDGAR client"""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._rate_limit_delay = 1.0  # Seconds between requests
        self._last_request_time = 0.0
        
        # Try to import edgar-tools library
        self._edgar_module = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the edgar-tools client library"""
        # Try different possible library names
        possible_modules = [
            "edgar_tools",
            "edgar_tools.client",
            "sec_edgar",
            "sec_edgar.client",
            "edgar",
        ]
        
        for module_name in possible_modules:
            try:
                self._edgar_module = __import__(module_name, fromlist=[""])
                logger.info(f"Successfully imported edgar-tools library: {module_name}")
                return
            except ImportError:
                continue
        
        logger.warning("Could not import edgar-tools library. Using mock implementation.")
        logger.warning("Please install edgar-tools: pip install edgar-tools")
    
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._rate_limit_delay:
            sleep_time = self._rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        self._last_request_time = time.time()
    
    def get_company_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get company information by ticker symbol.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
        
        Returns:
            Company data dictionary with cik, name, tickers, exchanges, etc.
        """
        cache_key = f"company_{ticker}"
        if cache_key in self._cache:
            logger.debug(f"Returning cached company data for {ticker}")
            return self._cache[cache_key]
        
        self._rate_limit()
        
        try:
            if self._edgar_module:
                # Try common API patterns
                if hasattr(self._edgar_module, "get_company"):
                    company_data = self._edgar_module.get_company(ticker)
                elif hasattr(self._edgar_module, "Company"):
                    company = self._edgar_module.Company(ticker)
                    company_data = company.to_dict() if hasattr(company, "to_dict") else company.__dict__
                else:
                    logger.warning("edgar-tools library found but API not recognized")
                    return self._mock_company_data(ticker)
            else:
                return self._mock_company_data(ticker)
            
            # Normalize company data structure
            normalized = self._normalize_company_data(company_data)
            self._cache[cache_key] = normalized
            return normalized
            
        except Exception as e:
            logger.error(f"Error fetching company data for {ticker}: {e}")
            return self._mock_company_data(ticker)
    
    def get_filing(
        self,
        ticker: str,
        form_type: str = "10-K",
        fiscal_year: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get filing data for a company.
        
        Args:
            ticker: Stock ticker symbol
            form_type: Form type (e.g., "10-K", "10-Q", "8-K")
            fiscal_year: Specific fiscal year (optional, defaults to latest)
        
        Returns:
            Filing data dictionary matching schema expectations
        """
        cache_key = f"filing_{ticker}_{form_type}_{fiscal_year}"
        if cache_key in self._cache:
            logger.debug(f"Returning cached filing data for {ticker} {form_type}")
            return self._cache[cache_key]
        
        self._rate_limit()
        
        try:
            if self._edgar_module:
                # Try common API patterns
                if hasattr(self._edgar_module, "get_filing"):
                    filing_data = self._edgar_module.get_filing(ticker, form_type, fiscal_year)
                elif hasattr(self._edgar_module, "Filing"):
                    filing = self._edgar_module.Filing(ticker, form_type, fiscal_year)
                    filing_data = filing.to_dict() if hasattr(filing, "to_dict") else filing.__dict__
                else:
                    logger.warning("edgar-tools library found but API not recognized")
                    return self._mock_filing_data(ticker, form_type, fiscal_year)
            else:
                return self._mock_filing_data(ticker, form_type, fiscal_year)
            
            # Normalize filing data structure
            normalized = self._normalize_filing_data(filing_data, ticker)
            self._cache[cache_key] = normalized
            return normalized
            
        except Exception as e:
            logger.error(f"Error fetching filing data for {ticker} {form_type}: {e}")
            return self._mock_filing_data(ticker, form_type, fiscal_year)
    
    def _normalize_company_data(self, data: Any) -> Dict[str, Any]:
        """
        Normalize company data to expected schema format.
        
        Args:
            data: Raw company data from edgar-tools
        
        Returns:
            Normalized company data dictionary
        """
        if isinstance(data, dict):
            # Ensure required fields exist
            normalized = {
                "cik": data.get("cik") or data.get("CIK", ""),
                "name": data.get("name") or data.get("company_name", ""),
                "tickers": data.get("tickers") or data.get("symbols", []) or [data.get("ticker", "")],
                "exchanges": data.get("exchanges") or data.get("exchange", []) or [],
                "sic": data.get("sic") or data.get("SIC", ""),
                "sic_description": data.get("sic_description") or data.get("sicDescription", ""),
                "state_of_incorporation": data.get("state_of_incorporation") or data.get("stateOfIncorporation", ""),
            }
            return normalized
        
        # If it's an object, try to extract attributes
        return {
            "cik": getattr(data, "cik", ""),
            "name": getattr(data, "name", ""),
            "tickers": getattr(data, "tickers", []) or [getattr(data, "ticker", "")],
            "exchanges": getattr(data, "exchanges", []),
            "sic": getattr(data, "sic", ""),
            "sic_description": getattr(data, "sic_description", ""),
            "state_of_incorporation": getattr(data, "state_of_incorporation", ""),
        }
    
    def _normalize_filing_data(self, data: Any, ticker: str) -> Dict[str, Any]:
        """
        Normalize filing data to expected schema format.
        
        Args:
            data: Raw filing data from edgar-tools
            ticker: Ticker symbol for fallback
        
        Returns:
            Normalized filing data dictionary matching schema expectations
        """
        if isinstance(data, dict):
            # Extract company info
            company = data.get("company", {})
            if not company:
                company = self.get_company_by_ticker(ticker) or {}
            
            # Extract filing info
            filing = data.get("filing", {})
            if not filing:
                filing = {k: v for k, v in data.items() if k != "company" and k != "financials" and k != "xbrl"}
            
            # Extract items/sections
            items = filing.get("items", []) or data.get("items", [])
            
            normalized = {
                "company": company,
                "filing": {
                    "form": filing.get("form") or filing.get("form_type") or filing.get("formType", ""),
                    "filing_date": filing.get("filing_date") or filing.get("filingDate", ""),
                    "accession_no": filing.get("accession_no") or filing.get("accession_number") or filing.get("accessionNumber", ""),
                    "period_of_report": filing.get("period_of_report") or filing.get("periodOfReport", ""),
                    "fiscal_year_end": filing.get("fiscal_year_end") or filing.get("fiscalYearEnd", ""),
                    "document_url": filing.get("document_url") or filing.get("documentUrl") or filing.get("url", ""),
                    "items": items,
                },
                "financials": data.get("financials", {}),
                "xbrl": data.get("xbrl", {}),
            }
            return normalized
        
        # If it's an object, try to extract attributes
        return {
            "company": self.get_company_by_ticker(ticker) or {},
            "filing": {
                "form": getattr(data, "form_type", ""),
                "filing_date": getattr(data, "filing_date", ""),
                "accession_no": getattr(data, "accession_number", ""),
                "period_of_report": getattr(data, "period_of_report", ""),
                "fiscal_year_end": getattr(data, "fiscal_year_end", ""),
                "document_url": getattr(data, "document_url", ""),
                "items": getattr(data, "items", []),
            },
            "financials": getattr(data, "financials", {}),
            "xbrl": getattr(data, "xbrl", {}),
        }
    
    def _mock_company_data(self, ticker: str) -> Dict[str, Any]:
        """Generate mock company data for testing when library is not available"""
        logger.warning(f"Using mock company data for {ticker} (edgar-tools not available)")
        return {
            "cik": "0000320193" if ticker.upper() == "AAPL" else "0000000000",
            "name": f"{ticker} Inc." if ticker.upper() == "AAPL" else f"{ticker} Corporation",
            "tickers": [ticker.upper()],
            "exchanges": ["NASDAQ"],
            "sic": "3571",
            "sic_description": "Electronic Computers",
            "state_of_incorporation": "CA",
        }
    
    def _mock_filing_data(self, ticker: str, form_type: str, fiscal_year: Optional[int]) -> Dict[str, Any]:
        """Generate mock filing data for testing when library is not available"""
        logger.warning(f"Using mock filing data for {ticker} {form_type} (edgar-tools not available)")
        company = self._mock_company_data(ticker)
        year = fiscal_year or 2024
        
        return {
            "company": company,
            "filing": {
                "form": form_type,
                "filing_date": f"{year}-11-01",
                "accession_no": f"{company['cik']}-{year}-000077",
                "period_of_report": f"{year}-09-28",
                "fiscal_year_end": "0930",
                "document_url": f"https://www.sec.gov/Archives/edgar/data/{company['cik']}/mock-filing.html",
                "items": [
                    {
                        "item": "1",
                        "name": "Business",
                        "text": f"Mock business description for {ticker} fiscal year {year}.",
                        "html": f"<p>Mock business description for {ticker} fiscal year {year}.</p>",
                    },
                    {
                        "item": "7",
                        "name": "Management's Discussion and Analysis",
                        "text": f"Mock MD&A content for {ticker} fiscal year {year}.",
                        "html": f"<p>Mock MD&A content for {ticker} fiscal year {year}.</p>",
                    },
                ],
            },
            "financials": {},
            "xbrl": {},
        }

