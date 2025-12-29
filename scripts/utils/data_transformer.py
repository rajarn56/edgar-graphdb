"""Transform EDGAR JSON data to Neo4j node/relationship structures"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tiktoken
from loguru import logger


class DataTransformer:
    """Transforms EDGAR data to Neo4j graph format"""
    
    def __init__(self, max_chunk_tokens: int = 800, overlap_tokens: int = 75):
        """
        Initialize data transformer.
        
        Args:
            max_chunk_tokens: Maximum tokens per chunk (default: 800)
            overlap_tokens: Token overlap between chunks (default: 75)
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.overlap_tokens = overlap_tokens
        
        # Initialize tokenizer (cl100k_base is used by GPT-3.5/4)
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Could not initialize tiktoken: {e}. Using simple word-based estimation.")
            self.tokenizer = None
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(text) // 4
    
    def transform_edgar_data(self, edgar_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform complete EDGAR data structure to Neo4j format.
        
        Args:
            edgar_data: EDGAR data dictionary with company, filing, financials, xbrl
        
        Returns:
            Dictionary with transformed nodes and relationships
        """
        company_data = edgar_data.get("company", {})
        filing_data = edgar_data.get("filing", {})
        financials_data = edgar_data.get("financials", {})
        xbrl_data = edgar_data.get("xbrl", {})
        
        # Transform company
        company_node = self._transform_company(company_data)
        
        # Transform filing
        filing_node, period_node = self._transform_filing(filing_data, company_data)
        
        # Transform sections and chunks
        sections = []
        chunks = []
        if filing_data.get("items"):
            for item_data in filing_data["items"]:
                section_node, section_chunks = self._transform_section(
                    item_data, filing_data, company_data
                )
                sections.append(section_node)
                chunks.extend(section_chunks)
        
        # Transform financial statements
        financial_nodes = []
        if financials_data:
            financial_nodes = self._transform_financials(
                financials_data, filing_data, company_data
            )
        
        # Transform XBRL facts
        xbrl_nodes = []
        if xbrl_data.get("facts"):
            xbrl_nodes = self._transform_xbrl_facts(
                xbrl_data["facts"], filing_data, company_data
            )
        
        return {
            "company": company_node,
            "filing": filing_node,
            "period": period_node,
            "sections": sections,
            "chunks": chunks,
            "financials": financial_nodes,
            "xbrl": xbrl_nodes,
        }
    
    def _transform_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform company data to Company node"""
        logger.debug("Transforming company data...")
        logger.debug(f"Input company_data keys: {list(company_data.keys())}")
        
        cik = company_data.get("cik", "")
        if not cik:
            logger.error(f"Company CIK is missing. Available keys: {list(company_data.keys())}")
            raise ValueError("Company CIK is required")
        
        # Ensure CIK is zero-padded to 10 digits
        original_cik = cik
        cik = str(cik).zfill(10)
        if original_cik != cik:
            logger.debug(f"CIK zero-padded: {original_cik} -> {cik}")
        
        # Log field mappings
        ticker = company_data.get("tickers", [""])[0] if company_data.get("tickers") else ""
        exchange = company_data.get("exchanges", [""])[0] if company_data.get("exchanges") else ""
        
        logger.debug(f"Company field mappings: cik={cik}, name={company_data.get('name', '')}, "
                    f"ticker={ticker}, sic={company_data.get('sic', '')}, "
                    f"exchange={exchange}")
        
        # Warn about missing optional fields
        missing_fields = []
        if not company_data.get("name"):
            missing_fields.append("name")
        if not ticker:
            missing_fields.append("ticker")
        if missing_fields:
            logger.warning(f"Company missing optional fields: {missing_fields}")
        
        return {
            "node_type": "Company",
            "properties": {
                "cik": cik,
                "name": company_data.get("name", ""),
                "ticker": ticker,
                "sic": company_data.get("sic", ""),
                "sic_description": company_data.get("sic_description", ""),
                "exchange": exchange,
                "incorporation_state": company_data.get("state_of_incorporation", ""),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        }
    
    def _transform_filing(
        self, filing_data: Dict[str, Any], company_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Transform filing data to Filing and Period nodes"""
        logger.debug("Transforming filing data...")
        logger.debug(f"Input filing_data keys: {list(filing_data.keys())}")
        
        accession_number = filing_data.get("accession_no", "")
        if not accession_number:
            logger.error(f"Filing accession number is missing. Available keys: {list(filing_data.keys())}")
            raise ValueError("Filing accession number is required")
        
        form_type = filing_data.get("form", "")
        filing_date = filing_data.get("filing_date", "")
        period_end_date = filing_data.get("period_of_report", "")
        fiscal_year_end = filing_data.get("fiscal_year_end", "1231")
        
        logger.debug(f"Filing field mappings: accession_no={accession_number}, form={form_type}, "
                    f"filing_date={filing_date}, period_of_report={period_end_date}, "
                    f"fiscal_year_end={fiscal_year_end}")
        
        # Warn about missing date fields
        if not filing_date:
            logger.warning("Filing date is missing - will be set to null in database")
        if not period_end_date:
            logger.warning("Period end date is missing - will be set to null in database")
        
        # Parse fiscal year and quarter
        fiscal_year = None
        fiscal_quarter = None
        if period_end_date:
            try:
                year = int(period_end_date[:4])
                fiscal_year = year
                # Determine quarter based on fiscal year end
                fiscal_quarter = self._determine_fiscal_quarter(period_end_date, fiscal_year_end)
            except (ValueError, IndexError):
                pass
        
        # Calculate period start
        period_start = self._calculate_period_start(period_end_date, fiscal_quarter) if period_end_date else None
        
        filing_node = {
            "node_type": "Filing",
            "properties": {
                "accession_number": accession_number,
                "form_type": form_type,
                "filing_date": filing_date,
                "period_end_date": period_end_date,
                "fiscal_year": fiscal_year,
                "fiscal_quarter": fiscal_quarter,
                "fiscal_period": f"{fiscal_year}-{'Q' + str(fiscal_quarter) if fiscal_quarter else 'FY'}" if fiscal_year else None,
                "url": filing_data.get("document_url", ""),
                "company_cik": company_data.get("cik", ""),
                "company_name": company_data.get("name", ""),
                "company_ticker": company_data.get("tickers", [""])[0] if company_data.get("tickers") else "",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "ingestion_status": "processing",
            }
        }
        
        period_id = f"{fiscal_year}_{'Q' + str(fiscal_quarter) if fiscal_quarter else 'FY'}" if fiscal_year else None
        period_node = None
        if period_id:
            period_node = {
                "node_type": "Period",
                "properties": {
                    "period_id": period_id,
                    "fiscal_year": fiscal_year,
                    "fiscal_quarter": fiscal_quarter,
                    "period_start": period_start,
                    "period_end": period_end_date,
                    "period_type": "quarterly" if fiscal_quarter else "annual",
                    "created_at": datetime.now(),
                }
            }
        
        return filing_node, period_node
    
    def _transform_section(
        self, item_data: Dict[str, Any], filing_data: Dict[str, Any], company_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Transform section/item data to Section node and Chunk nodes"""
        accession_number = filing_data.get("accession_no", "")
        item_number = item_data.get("item", "")
        item_title = item_data.get("name", "")
        content = item_data.get("text", "")
        
        section_id = f"{accession_number}_Item{item_number}"
        
        # Determine section type based on form type
        form_type = filing_data.get("form", "")
        section_labels = ["Section"]
        if form_type == "8-K":
            section_labels.append("Form8KItem")
        elif form_type == "DEF 14A":
            section_labels.append("ProxySection")
        elif form_type in ["10-K", "10-Q"]:
            section_labels.append("PeriodicReportSection")
        
        fiscal_year = None
        if filing_data.get("period_of_report"):
            try:
                fiscal_year = int(filing_data["period_of_report"][:4])
            except (ValueError, IndexError):
                pass
        
        section_node = {
            "node_type": "Section",
            "labels": section_labels,
            "properties": {
                "section_id": section_id,
                "item_number": f"Item {item_number}",
                "item_title": item_title,
                "content": content,
                "content_length": len(content),
                "word_count": len(content.split()),
                "company_cik": company_data.get("cik", ""),
                "fiscal_year": fiscal_year,
                "form_type": form_type,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        }
        
        # Add form-specific properties
        if form_type == "8-K":
            section_node["properties"]["item_code"] = item_number
            section_node["properties"]["event_type"] = self._infer_event_type(item_number)
        
        # Chunk the content
        chunks = self._chunk_content(
            content, section_id, company_data, filing_data, item_number
        )
        
        return section_node, chunks
    
    def _chunk_content(
        self,
        content: str,
        section_id: str,
        company_data: Dict[str, Any],
        filing_data: Dict[str, Any],
        item_number: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk content with context preservation (as per schema design).
        
        Args:
            content: Text content to chunk
            section_id: Section ID for chunk IDs
            company_data: Company data for context
            filing_data: Filing data for context
            item_number: Item number for context
        
        Returns:
            List of chunk dictionaries
        """
        if not content or not content.strip():
            return []
        
        # Split into paragraphs
        paragraphs = self._split_paragraphs(content)
        
        chunks = []
        chunk_index = 0
        current_chunk_text = ""
        context_before = ""
        
        fiscal_year = None
        if filing_data.get("period_of_report"):
            try:
                fiscal_year = int(filing_data["period_of_report"][:4])
            except (ValueError, IndexError):
                pass
        
        fiscal_quarter = None
        if filing_data.get("period_of_report") and filing_data.get("fiscal_year_end"):
            fiscal_quarter = self._determine_fiscal_quarter(
                filing_data["period_of_report"], filing_data.get("fiscal_year_end", "1231")
            )
        
        for i, para in enumerate(paragraphs):
            # Check if adding this paragraph would exceed token limit
            test_chunk = current_chunk_text + "\n\n" + para if current_chunk_text else para
            test_tokens = self.estimate_tokens(test_chunk)
            
            if test_tokens > self.max_chunk_tokens and current_chunk_text:
                # Save current chunk
                chunk = self._create_chunk(
                    section_id=section_id,
                    chunk_index=chunk_index,
                    content=current_chunk_text,
                    context_before=context_before,
                    context_after=self._get_context_after(paragraphs, i, self.overlap_tokens),
                    company_data=company_data,
                    filing_data=filing_data,
                    item_number=item_number,
                    fiscal_year=fiscal_year,
                    fiscal_quarter=fiscal_quarter,
                )
                chunks.append(chunk)
                
                # Prepare next chunk with overlap
                context_before = self._get_last_n_tokens(current_chunk_text, self.overlap_tokens)
                current_chunk_text = context_before + "\n\n" + para
                chunk_index += 1
            else:
                current_chunk_text = test_chunk if current_chunk_text else para
        
        # Add final chunk
        if current_chunk_text:
            chunk = self._create_chunk(
                section_id=section_id,
                chunk_index=chunk_index,
                content=current_chunk_text,
                context_before=context_before,
                context_after="",
                company_data=company_data,
                filing_data=filing_data,
                item_number=item_number,
                fiscal_year=fiscal_year,
                fiscal_quarter=fiscal_quarter,
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(
        self,
        section_id: str,
        chunk_index: int,
        content: str,
        context_before: str,
        context_after: str,
        company_data: Dict[str, Any],
        filing_data: Dict[str, Any],
        item_number: str,
        fiscal_year: Optional[int],
        fiscal_quarter: Optional[int],
    ) -> Dict[str, Any]:
        """Create a chunk node dictionary"""
        chunk_id = f"{section_id}_chunk_{chunk_index}"
        
        # Determine semantic type
        semantic_type = self._infer_semantic_type(content, item_number)
        
        # Determine chunk type
        chunk_type = "paragraph"
        if self._is_table(content):
            chunk_type = "table"
        
        return {
            "node_type": "Chunk",
            "properties": {
                "chunk_id": chunk_id,
                "chunk_index": chunk_index,
                "content": content,
                "content_length": len(content),
                "word_count": len(content.split()),
                "token_count": self.estimate_tokens(content),
                "chunk_type": chunk_type,
                "semantic_type": semantic_type,
                "context_before": context_before,
                "context_after": context_after,
                "company_cik": company_data.get("cik", ""),
                "fiscal_year": fiscal_year,
                "fiscal_quarter": fiscal_quarter,
                "form_type": filing_data.get("form", ""),
                "section_item": f"Item {item_number}",
                "created_at": datetime.now(),
            }
        }
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split by double newlines or single newline followed by capital letter
        paragraphs = re.split(r'\n\s*\n', text)
        # Filter out empty paragraphs
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _get_context_after(self, paragraphs: List[str], current_index: int, tokens: int) -> str:
        """Get context after current position"""
        if current_index >= len(paragraphs) - 1:
            return ""
        
        context_parts = []
        token_count = 0
        for i in range(current_index + 1, len(paragraphs)):
            para = paragraphs[i]
            para_tokens = self.estimate_tokens(para)
            if token_count + para_tokens > tokens:
                break
            context_parts.append(para)
            token_count += para_tokens
        
        return "\n\n".join(context_parts)
    
    def _get_last_n_tokens(self, text: str, tokens: int) -> str:
        """Get last N tokens from text"""
        if not text:
            return ""
        
        # Simple approach: take last portion of text
        # More sophisticated: could use tokenizer to get exact tokens
        estimated_chars = tokens * 4  # Rough estimate
        if len(text) <= estimated_chars:
            return text
        return text[-estimated_chars:]
    
    def _infer_semantic_type(self, content: str, item_number: str) -> str:
        """Infer semantic type from content and item number"""
        content_lower = content.lower()
        
        # Item-specific semantic types
        if item_number == "1A" or "risk factor" in content_lower:
            return "risk_discussion"
        elif item_number == "7" or "management" in content_lower or "md&a" in content_lower:
            return "financial_analysis"
        elif "revenue" in content_lower or "sales" in content_lower:
            return "revenue_analysis"
        elif "strategy" in content_lower or "forward" in content_lower or "outlook" in content_lower:
            return "strategy"
        elif "acquisition" in content_lower or "merger" in content_lower:
            return "acquisition"
        else:
            return "narrative"
    
    def _is_table(self, content: str) -> bool:
        """Check if content appears to be a table"""
        # Simple heuristic: check for multiple pipe characters or tab-separated values
        lines = content.split('\n')
        if len(lines) < 2:
            return False
        
        # Check for table-like patterns
        pipe_count = sum(line.count('|') for line in lines[:5])
        tab_count = sum(line.count('\t') for line in lines[:5])
        
        return pipe_count > 5 or tab_count > 5
    
    def _determine_fiscal_quarter(self, period_end_date: str, fiscal_year_end: str) -> Optional[int]:
        """Determine fiscal quarter from period end date and fiscal year end"""
        if not period_end_date or len(period_end_date) < 7:
            return None
        
        try:
            # Parse date (format: YYYY-MM-DD)
            year = int(period_end_date[:4])
            month = int(period_end_date[5:7])
            day = int(period_end_date[8:10])
            
            # Parse fiscal year end (format: MMDD)
            fy_month = int(fiscal_year_end[:2])
            fy_day = int(fiscal_year_end[2:4])
            
            # Calculate quarter based on fiscal year end
            # This is simplified - actual calculation depends on fiscal year structure
            if month <= 3:
                return 1
            elif month <= 6:
                return 2
            elif month <= 9:
                return 3
            else:
                return 4
        except (ValueError, IndexError):
            return None
    
    def _calculate_period_start(self, period_end_date: str, fiscal_quarter: Optional[int]) -> Optional[str]:
        """Calculate period start date"""
        if not period_end_date or len(period_end_date) < 10:
            return None
        
        try:
            year = int(period_end_date[:4])
            month = int(period_end_date[5:7])
            day = int(period_end_date[8:10])
            
            if fiscal_quarter == 1:
                # Q1: start 3 months before
                start_month = month - 3
                start_year = year
                if start_month <= 0:
                    start_month += 12
                    start_year -= 1
            elif fiscal_quarter == 2:
                # Q2: start 3 months before
                start_month = month - 3
                start_year = year
                if start_month <= 0:
                    start_month += 12
                    start_year -= 1
            elif fiscal_quarter == 3:
                # Q3: start 3 months before
                start_month = month - 3
                start_year = year
                if start_month <= 0:
                    start_month += 12
                    start_year -= 1
            else:
                # Annual or Q4: start 12 months before
                start_month = month
                start_year = year - 1
            
            return f"{start_year}-{start_month:02d}-{day:02d}"
        except (ValueError, IndexError):
            return None
    
    def _infer_event_type(self, item_code: str) -> str:
        """Infer event type for 8-K items"""
        event_map = {
            "1.01": "entry_into_agreement",
            "2.02": "earnings_release",
            "5.02": "management_change",
            "8.01": "other_events",
        }
        return event_map.get(item_code, "other_events")
    
    def _transform_financials(
        self, financials_data: Dict[str, Any], filing_data: Dict[str, Any], company_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Transform financial statements data"""
        # This is a placeholder - actual implementation would parse financial statements
        # and create FinancialStatement, LineItem, and Value nodes
        logger.info("Financial statements transformation not yet implemented")
        return []
    
    def _transform_xbrl_facts(
        self, facts: List[Dict[str, Any]], filing_data: Dict[str, Any], company_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Transform XBRL facts to LineItem and Value nodes"""
        # This is a placeholder - actual implementation would parse XBRL facts
        # and create LineItem and Value nodes
        logger.info("XBRL facts transformation not yet implemented")
        return []

