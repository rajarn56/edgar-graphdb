"""EDGAR tools client wrapper for fetching SEC filing data"""

import os
import time
from typing import Dict, Any, List, Optional
from loguru import logger


class EdgarClient:
    """Interface to edgartools library for fetching SEC EDGAR filing data"""
    
    def __init__(self, identity_email: Optional[str] = None):
        """
        Initialize EDGAR client.
        
        Args:
            identity_email: Email address for SEC EDGAR identity (required by SEC).
                           If not provided, will try to get from EDGAR_IDENTITY env var.
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._rate_limit_delay = 1.0  # Seconds between requests
        self._last_request_time = 0.0
        
        # Try to import edgartools library
        self._edgar_module = None
        self._Company = None
        self._Filing = None
        self._set_identity = None
        self._initialize_client(identity_email)
    
    def _initialize_client(self, identity_email: Optional[str] = None):
        """Initialize the edgartools client library"""
        try:
            # Import edgartools (the library uses 'edgar' as module name)
            import edgar
            from edgar import Company, Filing, set_identity
            
            self._edgar_module = edgar
            self._Company = Company
            self._Filing = Filing
            self._set_identity = set_identity
            
            # Set identity (required by SEC)
            email = identity_email or os.getenv("EDGAR_IDENTITY")
            if email:
                set_identity(email)
                logger.info(f"Set EDGAR identity: {email}")
            else:
                logger.warning("EDGAR_IDENTITY not set. SEC requires identity for EDGAR access.")
                logger.warning("Set EDGAR_IDENTITY environment variable or pass identity_email parameter.")
                logger.warning("Example: export EDGAR_IDENTITY='your.email@example.com'")
            
            logger.info("Successfully imported edgartools library")
            return
            
        except ImportError as e:
            logger.warning(f"Could not import edgartools library: {e}")
            logger.warning("Using mock implementation.")
            logger.warning("Please install edgartools: pip install edgartools")
            logger.warning("GitHub: https://github.com/dgunning/edgartools")
    
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
            if self._Company:
                # Use edgartools Company class
                company = self._Company(ticker)
                # Convert to dict - edgartools Company objects have attributes
                company_data = {
                    "cik": str(company.cik).zfill(10),  # Ensure CIK is 10 digits
                    "name": company.name,
                    "tickers": [ticker.upper()],
                    "exchanges": getattr(company, "exchange", []),
                    "sic": getattr(company, "sic", ""),
                    "sic_description": getattr(company, "sic_description", ""),
                    "state_of_incorporation": getattr(company, "state_of_incorporation", ""),
                }
            else:
                return self._mock_company_data(ticker)
            
            # Normalize company data structure
            normalized = self._normalize_company_data(company_data)
            self._cache[cache_key] = normalized
            logger.info(f"Fetched company data for {ticker}: {normalized['name']}")
            return normalized
            
        except Exception as e:
            logger.error(f"Error fetching company data for {ticker}: {e}", exc_info=True)
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
            if self._Filing:
                # Use edgartools Filing class
                # Get company first to ensure we have CIK
                company_data = self.get_company_by_ticker(ticker)
                if not company_data:
                    logger.error(f"Could not get company data for {ticker}")
                    return self._mock_filing_data(ticker, form_type, fiscal_year)
                
                # Get filings for the company
                company = self._Company(ticker)
                
                # Normalize form type for edgartools (handle spaces and variations)
                # edgartools may expect "DEF14A" instead of "DEF 14A"
                normalized_form_type = form_type
                if form_type.upper() == "DEF 14A" or form_type.upper() == "DEF14A":
                    # Try both formats - edgartools may accept either
                    normalized_form_type = "DEF 14A"  # Standard SEC format
                    logger.debug(f"Normalized form type: {form_type} -> {normalized_form_type}")
                
                # Get the specific filing
                if fiscal_year:
                    # Get filing for specific year
                    filings = company.get_filings(form=normalized_form_type)
                    # Filter by fiscal year if possible
                    filing = None
                    for f in filings:
                        if hasattr(f, 'filing_date') and str(fiscal_year) in str(f.filing_date):
                            filing = f
                            break
                    if not filing and len(filings) > 0:
                        filing = filings[0]  # Fallback to first filing
                else:
                    # Get latest filing
                    filings = company.get_filings(form=normalized_form_type)
                    filing = filings[0] if len(filings) > 0 else None
                
                # If no filing found with normalized form, try alternative formats
                if not filing and normalized_form_type == "DEF 14A":
                    logger.debug(f"Trying alternative form type format: DEF14A")
                    try:
                        filings = company.get_filings(form="DEF14A")
                        filing = filings[0] if len(filings) > 0 else None
                        if filing:
                            normalized_form_type = "DEF14A"
                            logger.info(f"Found filing using alternative form type: DEF14A")
                    except Exception as e:
                        logger.debug(f"Alternative form type failed: {e}")
                
                if not filing:
                    logger.warning(f"No {form_type} filing found for {ticker} (tried: {normalized_form_type})")
                    return self._mock_filing_data(ticker, form_type, fiscal_year)
                
                # Extract filing data
                filing_data = {
                    "company": company_data,
                    "filing": {
                        "form": form_type,
                        "filing_date": str(filing.filing_date) if hasattr(filing, 'filing_date') else "",
                        "accession_no": filing.accession_number if hasattr(filing, 'accession_number') else "",
                        "period_of_report": str(filing.period_end_date) if hasattr(filing, 'period_end_date') else "",
                        "fiscal_year_end": "",
                        "document_url": filing.url if hasattr(filing, 'url') else "",
                        "items": [],
                    },
                    "financials": {},
                    "xbrl": {},
                }
                
                # Get filing items/sections if available
                try:
                    logger.debug(f"Filing object type: {type(filing).__name__}")
                    logger.debug(f"Filing object attributes: {[attr for attr in dir(filing) if not attr.startswith('_')][:20]}")
                    items = self._extract_filing_items(filing, form_type)
                    filing_data["filing"]["items"] = items
                    if items:
                        logger.info(f"Extracted {len(items)} items/sections from filing")
                        for item in items[:3]:  # Log first 3 items
                            logger.debug(f"  - Item {item.get('item')}: {item.get('name')} ({len(item.get('text', ''))} chars)")
                    else:
                        logger.warning(f"No items extracted from filing. Check debug logs for details.")
                except Exception as e:
                    logger.warning(f"Could not extract filing items: {e}")
                    logger.debug(f"Exception details: {e}", exc_info=True)
                    filing_data["filing"]["items"] = []
                
            else:
                return self._mock_filing_data(ticker, form_type, fiscal_year)
            
            # Normalize filing data structure
            normalized = self._normalize_filing_data(filing_data, ticker)
            self._cache[cache_key] = normalized
            logger.info(f"Fetched filing data for {ticker} {form_type}: {normalized['filing'].get('accession_no', 'N/A')}")
            return normalized
            
        except Exception as e:
            logger.error(f"Error fetching filing data for {ticker} {form_type}: {e}", exc_info=True)
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
    
    def _extract_filing_items(self, filing: Any, form_type: str) -> List[Dict[str, Any]]:
        """
        Extract items/sections from edgartools Filing object.
        
        Uses edgartools structured data objects (TenK, TenQ, etc.) for better extraction.
        
        Args:
            filing: edgartools Filing object
            form_type: Form type (e.g., "10-K", "10-Q", "8-K")
        
        Returns:
            List of item dictionaries with 'item', 'name', 'text', 'html' keys
        """
        items = []
        
        try:
            # Method 1: Use edgartools structured data objects (TenK, TenQ, etc.)
            # This is the recommended way to access filing sections
            if hasattr(filing, 'obj'):
                try:
                    logger.info(f"Attempting to convert filing to structured object using obj() method...")
                    structured_obj = filing.obj()
                    if structured_obj:
                        logger.info(f"Successfully converted to structured object: {type(structured_obj).__name__}")
                        items = self._extract_from_structured_object(structured_obj, form_type)
                        if items:
                            logger.info(f"Extracted {len(items)} items using structured object method")
                            return items
                        else:
                            logger.warning(f"Structured object conversion succeeded but no items extracted")
                    else:
                        logger.warning(f"obj() method returned None")
                except Exception as e:
                    logger.warning(f"Structured object extraction failed: {type(e).__name__}: {str(e)}")
                    logger.debug(f"Exception details: {e}", exc_info=True)
            
            # Method 2: Try to get HTML content and parse it
            html_content = None
            if hasattr(filing, 'html'):
                try:
                    html_content = filing.html
                    if html_content and len(str(html_content)) > 100:
                        logger.debug(f"Found HTML content ({len(str(html_content))} chars), parsing for items...")
                        items = self._parse_html_for_items(str(html_content), form_type)
                        if items:
                            logger.info(f"Extracted {len(items)} items from HTML content")
                            return items
                except Exception as e:
                    logger.debug(f"HTML access/parsing failed: {e}")
            
            # Method 3: Try to get text content and parse it
            if hasattr(filing, 'text'):
                try:
                    text_content = filing.text
                    if text_content and len(str(text_content)) > 100:
                        logger.debug(f"Found text content ({len(str(text_content))} chars), parsing for items...")
                        items = self._parse_text_for_items(str(text_content), form_type)
                        if items:
                            logger.info(f"Extracted {len(items)} items from text content")
                            return items
                except Exception as e:
                    logger.debug(f"Text access/parsing failed: {e}")
            
            # Method 4: Try to get documents and extract from them
            if hasattr(filing, 'documents'):
                try:
                    documents = filing.documents
                    if documents:
                        doc_list = list(documents) if hasattr(documents, '__iter__') else [documents]
                        logger.debug(f"Found {len(doc_list)} documents")
                        for doc in doc_list:
                            if hasattr(doc, 'html'):
                                html_content = doc.html
                                if html_content and len(str(html_content)) > 100:
                                    items = self._parse_html_for_items(str(html_content), form_type)
                                    if items:
                                        logger.info(f"Extracted {len(items)} items from document HTML")
                                        return items
                            elif hasattr(doc, 'text'):
                                text_content = doc.text
                                if text_content and len(str(text_content)) > 100:
                                    items = self._parse_text_for_items(str(text_content), form_type)
                                    if items:
                                        logger.info(f"Extracted {len(items)} items from document text")
                                        return items
                except Exception as e:
                    logger.debug(f"Document extraction failed: {e}")
            
            # Log available attributes for debugging
            logger.debug(f"Filing object attributes: {[attr for attr in dir(filing) if not attr.startswith('_')]}")
            logger.warning(f"Could not extract items from filing using any method")
            return []
            
        except Exception as e:
            logger.error(f"Error extracting filing items: {e}", exc_info=True)
            return []
    
    def _extract_from_structured_object(self, structured_obj: Any, form_type: str) -> List[Dict[str, Any]]:
        """
        Extract items from edgartools structured data objects (TenK, TenQ, etc.)
        
        Args:
            structured_obj: Structured data object (TenK, TenQ, etc.)
            form_type: Form type for context
        
        Returns:
            List of item dictionaries
        """
        items = []
        
        try:
            # Map form types to their structured object class names
            obj_type = type(structured_obj).__name__
            logger.debug(f"Processing structured object type: {obj_type}")
            
            # Common section mappings for different form types
            # edgartools provides structured objects: TenK, TenQ, EightK, etc.
            section_mappings = {
                'TenK': {
                    '1': ('business', 'Business'),
                    '1A': ('risk_factors', 'Risk Factors'),
                    '2': ('properties', 'Properties'),
                    '3': ('legal_proceedings', 'Legal Proceedings'),
                    '7': ('management_discussion', "Management's Discussion and Analysis"),
                    '7A': ('quantitative_qualitative', 'Quantitative and Qualitative Disclosures'),
                    '8': ('financial_statements', 'Financial Statements'),
                    '9': ('controls_procedures', 'Controls and Procedures'),
                },
                'TenQ': {
                    '1': ('business', 'Business'),
                    '2': ('risk_factors', 'Risk Factors'),
                    '3': ('legal_proceedings', 'Legal Proceedings'),
                    '4': ('controls_procedures', 'Controls and Procedures'),
                },
                'EightK': {
                    # 8-K forms have items like 1.01, 2.02, 5.02, etc.
                    # These are typically accessed as attributes or through items()
                    # We'll use fallback inspection for 8-K
                },
                'Def14A': {
                    # Proxy statements (DEF 14A) sections
                    # Common attributes in edgartools Def14A object
                    'compensation': ('compensation', 'Executive Compensation'),
                    'compensation_discussion': ('compensation_discussion', 'Compensation Discussion & Analysis'),
                    'directors': ('directors', 'Director Information'),
                    'board': ('board', 'Board Information'),
                    'committees': ('committees', 'Board Committees'),
                    'proposals': ('proposals', 'Shareholder Proposals'),
                    'governance': ('governance', 'Corporate Governance'),
                    'voting': ('voting', 'Voting Procedures'),
                    'auditor': ('auditor', 'Auditor Information'),
                    'related_party': ('related_party', 'Related Party Transactions'),
                },
                'Def14C': {
                    # Information statements (DEF 14C) - similar to DEF 14A
                    'action': ('action', 'Action Taken'),
                    'voting_results': ('voting_results', 'Voting Results'),
                    'governance': ('governance', 'Corporate Governance'),
                }
            }
            
            # Get section mappings for this form type
            mappings = section_mappings.get(obj_type, {})
            
            # Try to extract sections using known attribute names
            for item_num, (attr_name, item_title) in mappings.items():
                try:
                    if hasattr(structured_obj, attr_name):
                        section_content = getattr(structured_obj, attr_name)
                        if section_content:
                            # Convert to text if it's an object
                            text = None
                            if hasattr(section_content, 'text'):
                                text = section_content.text
                            elif hasattr(section_content, 'html'):
                                # If it has HTML, extract text from it
                                html = section_content.html
                                if html:
                                    try:
                                        from bs4 import BeautifulSoup
                                        soup = BeautifulSoup(str(html), 'html.parser')
                                        text = soup.get_text(separator='\n', strip=True)
                                    except:
                                        text = str(html)
                            elif hasattr(section_content, '__str__'):
                                text = str(section_content)
                            else:
                                text = str(section_content)
                            
                            if text and len(str(text).strip()) > 100:
                                text_str = str(text)[:50000]  # Limit size
                                items.append({
                                    "item": item_num,
                                    "name": item_title,
                                    "text": text_str,
                                    "html": f"<p>{text_str}</p>",
                                })
                                logger.info(f"Extracted Item {item_num}: {item_title} ({len(text_str)} chars)")
                except Exception as e:
                    logger.debug(f"Failed to extract {attr_name}: {e}")
            
            # If no items found with mappings, try to inspect the object structure
            # This handles form types without explicit mappings (8-K, DEF 14A, etc.)
            if not items:
                logger.debug(f"No items found using mappings. Inspecting object structure for {obj_type}...")
                # Try to find any attributes that might contain section content
                obj_attrs = [attr for attr in dir(structured_obj) if not attr.startswith('_')]
                logger.debug(f"Available attributes: {obj_attrs[:20]}")
                
                # For 8-K forms, try to access items() method if available
                if obj_type == 'EightK' and hasattr(structured_obj, 'items'):
                    try:
                        eightk_items = structured_obj.items()
                        if eightk_items:
                            # items() might return a dict or list
                            if isinstance(eightk_items, dict):
                                for item_key, item_content in eightk_items.items():
                                    text = str(item_content) if not hasattr(item_content, 'text') else item_content.text
                                    if text and len(str(text).strip()) > 100:
                                        items.append({
                                            "item": str(item_key),
                                            "name": f"Item {item_key}",
                                            "text": str(text)[:50000],
                                            "html": f"<p>{str(text)[:50000]}</p>",
                                        })
                                        logger.info(f"Extracted 8-K Item {item_key} ({len(str(text))} chars)")
                            elif hasattr(eightk_items, '__iter__'):
                                for idx, item_content in enumerate(eightk_items):
                                    text = str(item_content) if not hasattr(item_content, 'text') else item_content.text
                                    if text and len(str(text).strip()) > 100:
                                        items.append({
                                            "item": str(idx + 1),
                                            "name": f"Item {idx + 1}",
                                            "text": str(text)[:50000],
                                            "html": f"<p>{str(text)[:50000]}</p>",
                                        })
                                        logger.info(f"Extracted 8-K Item {idx + 1} ({len(str(text))} chars)")
                    except Exception as e:
                        logger.debug(f"Failed to extract 8-K items: {e}")
                
                # For DEF 14A, try sections() method if available (common in edgartools)
                if obj_type == 'Def14A' and hasattr(structured_obj, 'sections'):
                    try:
                        sections = structured_obj.sections()
                        if sections:
                            if isinstance(sections, dict):
                                for section_key, section_content in sections.items():
                                    text = None
                                    if hasattr(section_content, 'text'):
                                        text = section_content.text
                                    elif hasattr(section_content, 'html'):
                                        html = section_content.html
                                        if html:
                                            try:
                                                from bs4 import BeautifulSoup
                                                soup = BeautifulSoup(str(html), 'html.parser')
                                                text = soup.get_text(separator='\n', strip=True)
                                            except:
                                                text = str(html)
                                    else:
                                        text = str(section_content)
                                    
                                    if text and len(str(text).strip()) > 100:
                                        items.append({
                                            "item": str(section_key),
                                            "name": f"Section {section_key}",
                                            "text": str(text)[:50000],
                                            "html": f"<p>{str(text)[:50000]}</p>",
                                        })
                                        logger.info(f"Extracted DEF 14A section '{section_key}' ({len(str(text))} chars)")
                    except Exception as e:
                        logger.debug(f"Failed to extract DEF 14A sections: {e}")
                
                # Try common patterns for all form types
                for attr in obj_attrs:
                    # Skip methods and common non-content attributes
                    if attr in ['items', 'obj', 'html', 'text', 'documents', 'url', 'accession_number', 'sections']:
                        continue
                    
                    # Extended keyword list for DEF 14A and other forms
                    keywords = ['business', 'risk', 'management', 'discussion', 'mda', 'item', 'section', 
                               'content', 'description', 'compensation', 'director', 'board', 'committee',
                               'proposal', 'governance', 'voting', 'auditor', 'related', 'party']
                    
                    if any(keyword in attr.lower() for keyword in keywords):
                        try:
                            content = getattr(structured_obj, attr)
                            if content and not callable(content):
                                # Convert to text
                                text = None
                                if hasattr(content, 'text'):
                                    text = content.text
                                elif hasattr(content, 'html'):
                                    html = content.html
                                    if html:
                                        try:
                                            from bs4 import BeautifulSoup
                                            soup = BeautifulSoup(str(html), 'html.parser')
                                            text = soup.get_text(separator='\n', strip=True)
                                        except:
                                            text = str(html)
                                else:
                                    text = str(content)
                                
                                if text and len(str(text).strip()) > 100:
                                    # Try to infer item number from attribute name
                                    item_num = '1'  # Default
                                    if 'risk' in attr.lower():
                                        item_num = '1A'
                                    elif 'business' in attr.lower():
                                        item_num = '1'
                                    elif 'management' in attr.lower() or 'mda' in attr.lower():
                                        item_num = '7'
                                    elif 'financial' in attr.lower():
                                        item_num = '8'
                                    elif 'compensation' in attr.lower():
                                        item_num = 'compensation'
                                    elif 'director' in attr.lower() or 'board' in attr.lower():
                                        item_num = 'directors'
                                    elif 'proposal' in attr.lower():
                                        item_num = 'proposals'
                                    elif 'governance' in attr.lower():
                                        item_num = 'governance'
                                    
                                    items.append({
                                        "item": item_num,
                                        "name": attr.replace('_', ' ').title(),
                                        "text": str(text)[:50000],
                                        "html": f"<p>{str(text)[:50000]}</p>",
                                    })
                                    logger.info(f"Extracted from attribute '{attr}': Item {item_num} ({len(str(text))} chars)")
                        except Exception as e:
                            logger.debug(f"Failed to extract from {attr}: {e}")
            
            # Also try generic methods that might exist
            # Some structured objects have methods like get_section() or similar
            if hasattr(structured_obj, 'get_section'):
                try:
                    # Try common item numbers
                    for item_num in ['1', '1A', '2', '3', '7', '7A', '8', '9']:
                        try:
                            section = structured_obj.get_section(item_num)
                            if section:
                                text = str(section) if not hasattr(section, 'text') else section.text
                                if text and len(text.strip()) > 100:
                                    items.append({
                                        "item": item_num,
                                        "name": f"Item {item_num}",
                                        "text": text[:50000],
                                        "html": f"<p>{text[:50000]}</p>",
                                    })
                        except:
                            pass
                except Exception as e:
                    logger.debug(f"get_section() method failed: {e}")
            
            return items
            
        except Exception as e:
            logger.error(f"Error extracting from structured object: {e}", exc_info=True)
            return []
    
    def _normalize_items(self, items: List[Any]) -> List[Dict[str, Any]]:
        """Normalize items to expected format"""
        normalized = []
        for item in items:
            if isinstance(item, dict):
                normalized.append({
                    "item": item.get("item") or item.get("item_number") or item.get("number", ""),
                    "name": item.get("name") or item.get("title") or item.get("item_title", ""),
                    "text": item.get("text") or item.get("content") or "",
                    "html": item.get("html") or "",
                })
            elif hasattr(item, '__dict__'):
                # Object with attributes
                normalized.append({
                    "item": getattr(item, "item", "") or getattr(item, "item_number", "") or getattr(item, "number", ""),
                    "name": getattr(item, "name", "") or getattr(item, "title", "") or getattr(item, "item_title", ""),
                    "text": getattr(item, "text", "") or getattr(item, "content", ""),
                    "html": getattr(item, "html", ""),
                })
        return normalized
    
    def _parse_html_for_items(self, html_content: str, form_type: str) -> List[Dict[str, Any]]:
        """Parse HTML content to extract items/sections"""
        import re
        from html import unescape
        
        items = []
        
        # Common item patterns for 10-K, 10-Q forms
        # Pattern: Item 1, Item 1A, Item 7, etc.
        item_patterns = [
            r'<h[1-6][^>]*>.*?Item\s+(\d+[A-Z]?)[\.:]?\s*(.*?)</h[1-6]>',
            r'<p[^>]*>.*?Item\s+(\d+[A-Z]?)[\.:]?\s*(.*?)</p>',
            r'Item\s+(\d+[A-Z]?)[\.:]?\s*(.*?)(?=<|$)',
        ]
        
        # Try to extract using BeautifulSoup if available
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all potential item headers
            item_headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div'], 
                                        string=re.compile(r'Item\s+\d+[A-Z]?', re.IGNORECASE))
            
            for header in item_headers:
                text = header.get_text() if hasattr(header, 'get_text') else str(header)
                match = re.search(r'Item\s+(\d+[A-Z]?)[\.:]?\s*(.*?)$', text, re.IGNORECASE)
                if match:
                    item_num = match.group(1)
                    item_title = match.group(2).strip() if match.group(2) else ""
                    
                    # Extract content after header - find the section content
                    # Look for the next sibling elements until we hit another item header
                    content_elements = []
                    current = header.find_next_sibling()
                    max_elements = 1000  # Limit to prevent excessive content
                    element_count = 0
                    
                    while current and element_count < max_elements:
                        # Stop at next item header
                        if hasattr(current, 'get_text'):
                            current_text = current.get_text()
                            if re.search(r'Item\s+\d+[A-Z]?', current_text, re.IGNORECASE):
                                break
                        
                        # Collect content elements
                        if hasattr(current, 'name') and current.name in ['p', 'div', 'span', 'li', 'td', 'th']:
                            content_elements.append(current)
                            element_count += 1
                        
                        current = current.find_next_sibling()
                    
                    # Extract clean text from elements
                    content_text_parts = []
                    for elem in content_elements:
                        if hasattr(elem, 'get_text'):
                            text = elem.get_text(separator=' ', strip=True)
                            if text and len(text.strip()) > 10:  # Skip very short fragments
                                content_text_parts.append(text)
                    
                    content_text = '\n\n'.join(content_text_parts)
                    
                    # Also get HTML for reference (limited)
                    content_html = str(header) + ''.join(str(elem) for elem in content_elements[:20])
                    
                    # Clean and normalize text
                    content_text = self._clean_extracted_text(content_text)
                    
                    if content_text.strip() and len(content_text.strip()) > 100:
                        items.append({
                            "item": item_num,
                            "name": item_title or f"Item {item_num}",
                            "text": content_text[:50000],  # Limit text size
                            "html": content_html[:100000],  # Limit HTML size
                        })
            
            if items:
                logger.info(f"Extracted {len(items)} items from HTML using BeautifulSoup")
                return items
                
        except ImportError:
            logger.debug("BeautifulSoup not available, using regex parsing")
        except Exception as e:
            logger.debug(f"BeautifulSoup parsing failed: {e}")
        
        # Fallback: Simple regex parsing
        # This is less accurate but doesn't require BeautifulSoup
        for pattern in item_patterns:
            matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                item_num = match.group(1)
                item_title = match.group(2).strip() if len(match.groups()) > 1 else ""
                
                # Extract text content (simplified)
                start_pos = match.end()
                # Find next item or end of document
                next_match = re.search(r'Item\s+\d+[A-Z]?', html_content[start_pos:], re.IGNORECASE)
                end_pos = start_pos + next_match.start() if next_match else len(html_content)
                
                content_html = html_content[start_pos:end_pos]
                # Strip HTML tags for text
                content_text = re.sub(r'<[^>]+>', ' ', content_html)
                content_text = unescape(content_text)
                # Clean extracted text
                content_text = self._clean_extracted_text(content_text)
                
                if content_text and len(content_text.strip()) > 100:  # Minimum content length
                    items.append({
                        "item": item_num,
                        "name": item_title or f"Item {item_num}",
                        "text": content_text[:50000],
                        "html": content_html[:100000],
                    })
                    break  # Use first matching pattern
        
        if items:
            logger.info(f"Extracted {len(items)} items from HTML using regex")
        
        return items
    
    def _parse_text_for_items(self, text_content: str, form_type: str) -> List[Dict[str, Any]]:
        """Parse text content to extract items/sections"""
        import re
        
        items = []
        
        # Pattern to find items in text
        pattern = r'Item\s+(\d+[A-Z]?)[\.:]?\s*(.*?)(?=\n|Item\s+\d+[A-Z]?|$)'
        matches = re.finditer(pattern, text_content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            item_num = match.group(1)
            rest = match.group(2).strip()
            
            # Extract title (first line or first sentence)
            lines = rest.split('\n')
            item_title = lines[0].strip() if lines else ""
            if len(item_title) > 200:
                item_title = item_title[:200]
            
            # Extract content (everything after title)
            content_start = len(item_title)
            content_text = rest[content_start:].strip()
            
            # Find next item
            next_match = re.search(r'Item\s+\d+[A-Z]?', content_text, re.IGNORECASE)
            if next_match:
                content_text = content_text[:next_match.start()].strip()
            
            # Clean extracted text
            content_text = self._clean_extracted_text(content_text)
            
            if content_text and len(content_text.strip()) > 100:
                items.append({
                    "item": item_num,
                    "name": item_title or f"Item {item_num}",
                    "text": content_text[:50000],
                    "html": f"<p>{content_text[:50000]}</p>",
                })
        
        if items:
            logger.info(f"Extracted {len(items)} items from text content")
        
        return items
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean extracted text for RAG consumption.
        
        Args:
            text: Raw extracted text
        
        Returns:
            Clean, normalized text
        """
        if not text:
            return ""
        
        import re
        from html import unescape
        
        # Unescape HTML entities
        text = unescape(text)
        
        # Remove excessive whitespace
        text = re.sub(r' +', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines to double newline
        text = text.replace('\t', ' ')  # Tabs to spaces
        text = text.replace('\r', '')  # Remove carriage returns
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove control characters and zero-width spaces
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Final cleanup
        text = text.strip()
        
        return text
    
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

