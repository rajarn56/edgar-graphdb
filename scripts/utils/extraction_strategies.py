"""Extraction strategies for different EDGAR form types"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from loguru import logger
import re


class ExtractionStrategy(ABC):
    """Base class for extraction strategies"""
    
    @abstractmethod
    def extract_sections(
        self, 
        filing: Any, 
        form_config: Dict[str, Any],
        form_type: str
    ) -> List[Dict[str, Any]]:
        """
        Extract sections from a filing.
        
        Args:
            filing: Filing object (from edgartools)
            form_config: Form configuration from registry
            form_type: Form type (e.g., "10-K")
        
        Returns:
            List of section dictionaries with 'item', 'name', 'text', 'html' keys
        """
        pass
    
    def _clean_text_for_rag(self, text: str) -> str:
        """Clean text for RAG consumption (helper method)"""
        if not text:
            return ""
        
        # Import here to avoid circular dependencies
        try:
            from .data_transformer import DataTransformer
            transformer = DataTransformer()
            return transformer.clean_text_for_rag(text)
        except ImportError:
            # Fallback: simple cleaning
            import re
            from html import unescape
            text = unescape(text)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r' +', ' ', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text.strip()


class StructuredObjectStrategy(ExtractionStrategy):
    """Extract sections from edgartools structured objects (TenK, TenQ, etc.)"""
    
    def extract_sections(
        self, 
        filing: Any, 
        form_config: Dict[str, Any],
        form_type: str
    ) -> List[Dict[str, Any]]:
        """Extract sections using structured object mappings"""
        items = []
        
        try:
            # Get structured object
            if not hasattr(filing, 'obj'):
                logger.warning(f"Filing object does not have obj() method for {form_type}")
                return items
            
            structured_obj = filing.obj()
            if not structured_obj:
                logger.warning(f"obj() returned None for {form_type}")
                return items
            
            obj_type = type(structured_obj).__name__
            logger.debug(f"Processing structured object type: {obj_type}")
            
            # Get section mappings from config
            section_mappings = form_config.get("section_mappings", {})
            
            # Extract sections using mappings
            for item_num, mapping in section_mappings.items():
                if isinstance(mapping, list) and len(mapping) >= 2:
                    attr_name, item_title = mapping[0], mapping[1]
                elif isinstance(mapping, tuple) and len(mapping) >= 2:
                    attr_name, item_title = mapping[0], mapping[1]
                else:
                    logger.debug(f"Invalid mapping format for {item_num}: {mapping}")
                    continue
                
                try:
                    if hasattr(structured_obj, attr_name):
                        section_content = getattr(structured_obj, attr_name)
                        if section_content:
                            text = self._extract_text_from_content(section_content)
                            if text and len(str(text).strip()) > 100:
                                # Clean text for RAG
                                text_cleaned = self._clean_text_for_rag(str(text)[:50000])
                                items.append({
                                    "item": item_num,
                                    "name": item_title,
                                    "text": text_cleaned,
                                    "html": f"<p>{text_cleaned}</p>",
                                })
                                logger.info(f"Extracted {item_num}: {item_title} ({len(text_cleaned)} chars)")
                except Exception as e:
                    logger.debug(f"Failed to extract {attr_name}: {e}")
            
            return items
            
        except Exception as e:
            logger.error(f"Error in StructuredObjectStrategy: {e}", exc_info=True)
            return items
    
    def _extract_text_from_content(self, content: Any) -> Optional[str]:
        """Extract text from content object"""
        if hasattr(content, 'text'):
            return content.text
        elif hasattr(content, 'html'):
            html = content.html
            if html:
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(str(html), 'html.parser')
                    return soup.get_text(separator='\n', strip=True)
                except:
                    return str(html)
        elif hasattr(content, '__str__'):
            return str(content)
        else:
            return str(content)


class AttributeInspectionStrategy(ExtractionStrategy):
    """Extract sections by inspecting structured object attributes"""
    
    def extract_sections(
        self, 
        filing: Any, 
        form_config: Dict[str, Any],
        form_type: str
    ) -> List[Dict[str, Any]]:
        """Extract sections by inspecting object attributes"""
        items = []
        
        try:
            if not hasattr(filing, 'obj'):
                return items
            
            structured_obj = filing.obj()
            if not structured_obj:
                return items
            
            obj_type = type(structured_obj).__name__
            logger.debug(f"Inspecting attributes for {obj_type}")
            
            # Get section mappings
            section_mappings = form_config.get("section_mappings", {})
            
            # Try mappings first
            for item_num, mapping in section_mappings.items():
                if isinstance(mapping, list) and len(mapping) >= 2:
                    attr_name, item_title = mapping[0], mapping[1]
                elif isinstance(mapping, tuple) and len(mapping) >= 2:
                    attr_name, item_title = mapping[0], mapping[1]
                else:
                    continue
                
                try:
                    if hasattr(structured_obj, attr_name):
                        content = getattr(structured_obj, attr_name)
                        if content and not callable(content):
                            text = self._extract_text_from_content(content)
                            if text and len(str(text).strip()) > 100:
                                text_cleaned = self._clean_text_for_rag(str(text)[:50000])
                                items.append({
                                    "item": item_num,
                                    "name": item_title,
                                    "text": text_cleaned,
                                    "html": f"<p>{text_cleaned}</p>",
                                })
                                logger.info(f"Extracted {item_num}: {item_title}")
                except Exception as e:
                    logger.debug(f"Failed to extract {attr_name}: {e}")
            
            # If no items found, try sections() method
            if not items and hasattr(structured_obj, 'sections'):
                try:
                    sections = structured_obj.sections()
                    if sections:
                        if isinstance(sections, dict):
                            for section_key, section_content in sections.items():
                                text = self._extract_text_from_content(section_content)
                                if text and len(str(text).strip()) > 100:
                                    text_cleaned = self._clean_text_for_rag(str(text)[:50000])
                                    items.append({
                                        "item": str(section_key),
                                        "name": f"Section {section_key}",
                                        "text": text_cleaned,
                                        "html": f"<p>{text_cleaned}</p>",
                                    })
                except Exception as e:
                    logger.debug(f"Failed to use sections() method: {e}")
            
            # Fallback: inspect all attributes
            if not items:
                obj_attrs = [attr for attr in dir(structured_obj) if not attr.startswith('_')]
                keywords = ['compensation', 'director', 'board', 'committee', 'proposal', 
                           'governance', 'voting', 'auditor', 'related', 'party']
                
                for attr in obj_attrs:
                    if attr in ['items', 'obj', 'html', 'text', 'documents', 'url', 'accession_number', 'sections']:
                        continue
                    
                    if any(keyword in attr.lower() for keyword in keywords):
                        try:
                            content = getattr(structured_obj, attr)
                            if content and not callable(content):
                                text = self._extract_text_from_content(content)
                                if text and len(str(text).strip()) > 100:
                                    text_cleaned = self._clean_text_for_rag(str(text)[:50000])
                                    items.append({
                                        "item": attr,
                                        "name": attr.replace('_', ' ').title(),
                                        "text": text_cleaned,
                                        "html": f"<p>{text_cleaned}</p>",
                                    })
                        except Exception as e:
                            logger.debug(f"Failed to extract from {attr}: {e}")
            
            return items
            
        except Exception as e:
            logger.error(f"Error in AttributeInspectionStrategy: {e}", exc_info=True)
            return items
    
    def _extract_text_from_content(self, content: Any) -> Optional[str]:
        """Extract text from content object"""
        if hasattr(content, 'text'):
            return content.text
        elif hasattr(content, 'html'):
            html = content.html
            if html:
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(str(html), 'html.parser')
                    return soup.get_text(separator='\n', strip=True)
                except:
                    return str(html)
        else:
            return str(content)


class HTMLPatternStrategy(ExtractionStrategy):
    """Extract sections from HTML using pattern matching"""
    
    def extract_sections(
        self, 
        filing: Any, 
        form_config: Dict[str, Any],
        form_type: str
    ) -> List[Dict[str, Any]]:
        """Extract sections from HTML content"""
        items = []
        
        try:
            # Get HTML content
            html_content = None
            if hasattr(filing, 'html'):
                html_content = filing.html
            elif hasattr(filing, 'documents'):
                documents = filing.documents
                if documents:
                    doc_list = list(documents) if hasattr(documents, '__iter__') else [documents]
                    for doc in doc_list:
                        if hasattr(doc, 'html'):
                            html_content = doc.html
                            break
            
            if not html_content:
                logger.warning(f"No HTML content found for {form_type}")
                return items
            
            html_str = str(html_content)
            
            # Use BeautifulSoup if available
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_str, 'html.parser')
                
                # Find section headers
                section_patterns = form_config.get("section_patterns", [])
                if section_patterns:
                    # Use configured patterns
                    for pattern_config in section_patterns:
                        pattern = pattern_config.get("pattern", "")
                        if pattern:
                            matches = re.finditer(pattern, html_str, re.IGNORECASE | re.DOTALL)
                            for match in matches:
                                item_num = match.group(1) if match.groups() else "1"
                                item_title = match.group(2).strip() if len(match.groups()) > 1 else f"Section {item_num}"
                                
                                # Extract content after header
                                start_pos = match.end()
                                next_match = re.search(pattern, html_str[start_pos:], re.IGNORECASE)
                                end_pos = start_pos + next_match.start() if next_match else len(html_str)
                                
                                content_html = html_str[start_pos:end_pos]
                                content_soup = BeautifulSoup(content_html, 'html.parser')
                                text = content_soup.get_text(separator='\n', strip=True)
                                
                                if text and len(text.strip()) > 100:
                                    text_cleaned = self._clean_text_for_rag(text[:50000])
                                    items.append({
                                        "item": item_num,
                                        "name": item_title,
                                        "text": text_cleaned,
                                        "html": content_html[:100000],
                                    })
                else:
                    # Default: find Item headers
                    item_headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div'],
                                                string=re.compile(r'Item\s+\d+[A-Z]?', re.IGNORECASE))
                    
                    for header in item_headers:
                        text = header.get_text() if hasattr(header, 'get_text') else str(header)
                        match = re.search(r'Item\s+(\d+[A-Z]?)[\.:]?\s*(.*?)$', text, re.IGNORECASE)
                        if match:
                            item_num = match.group(1)
                            item_title = match.group(2).strip() if match.group(2) else f"Item {item_num}"
                            
                            # Extract content
                            content_elements = []
                            current = header.find_next_sibling()
                            for _ in range(1000):  # Limit iterations
                                if not current:
                                    break
                                if hasattr(current, 'get_text'):
                                    current_text = current.get_text()
                                    if re.search(r'Item\s+\d+[A-Z]?', current_text, re.IGNORECASE):
                                        break
                                if hasattr(current, 'name') and current.name in ['p', 'div', 'span', 'li']:
                                    content_elements.append(current)
                                current = current.find_next_sibling()
                            
                            content_text = '\n\n'.join([elem.get_text(separator=' ', strip=True) 
                                                       for elem in content_elements if hasattr(elem, 'get_text')])
                            
                            if content_text and len(content_text.strip()) > 100:
                                text_cleaned = self._clean_text_for_rag(content_text[:50000])
                                items.append({
                                    "item": item_num,
                                    "name": item_title,
                                    "text": text_cleaned,
                                    "html": str(header) + ''.join(str(elem) for elem in content_elements[:20]),
                                })
                
            except ImportError:
                logger.warning("BeautifulSoup not available, using regex fallback")
                # Fallback to regex
                pattern = r'Item\s+(\d+[A-Z]?)[\.:]?\s*(.*?)(?=<|$)'
                matches = re.finditer(pattern, html_str, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    item_num = match.group(1)
                    item_title = match.group(2).strip() if len(match.groups()) > 1 else f"Item {item_num}"
                    
                    start_pos = match.end()
                    next_match = re.search(r'Item\s+\d+[A-Z]?', html_str[start_pos:], re.IGNORECASE)
                    end_pos = start_pos + next_match.start() if next_match else len(html_str)
                    
                    content_html = html_str[start_pos:end_pos]
                    # Simple HTML tag removal
                    content_text = re.sub(r'<[^>]+>', ' ', content_html)
                    content_text = re.sub(r'\s+', ' ', content_text)
                    
                    if content_text and len(content_text.strip()) > 100:
                        text_cleaned = self._clean_text_for_rag(content_text[:50000])
                        items.append({
                            "item": item_num,
                            "name": item_title,
                            "text": text_cleaned,
                            "html": content_html[:100000],
                        })
            
            return items
            
        except Exception as e:
            logger.error(f"Error in HTMLPatternStrategy: {e}", exc_info=True)
            return items


class TextPatternStrategy(ExtractionStrategy):
    """Extract sections from plain text using pattern matching"""
    
    def extract_sections(
        self, 
        filing: Any, 
        form_config: Dict[str, Any],
        form_type: str
    ) -> List[Dict[str, Any]]:
        """Extract sections from text content"""
        items = []
        
        try:
            # Get text content
            text_content = None
            if hasattr(filing, 'text'):
                text_content = filing.text
            elif hasattr(filing, 'documents'):
                documents = filing.documents
                if documents:
                    doc_list = list(documents) if hasattr(documents, '__iter__') else [documents]
                    for doc in doc_list:
                        if hasattr(doc, 'text'):
                            text_content = doc.text
                            break
            
            if not text_content:
                logger.warning(f"No text content found for {form_type}")
                return items
            
            text_str = str(text_content)
            
            # Pattern to find items/sections
            pattern = r'Item\s+(\d+[A-Z]?)[\.:]?\s*(.*?)(?=\n|Item\s+\d+[A-Z]?|$)'
            matches = re.finditer(pattern, text_str, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                item_num = match.group(1)
                rest = match.group(2).strip()
                
                # Extract title (first line)
                lines = rest.split('\n')
                item_title = lines[0].strip() if lines else f"Item {item_num}"
                if len(item_title) > 200:
                    item_title = item_title[:200]
                
                # Extract content
                content_start = len(item_title)
                content_text = rest[content_start:].strip()
                
                # Find next item
                next_match = re.search(r'Item\s+\d+[A-Z]?', content_text, re.IGNORECASE)
                if next_match:
                    content_text = content_text[:next_match.start()].strip()
                
                if content_text and len(content_text.strip()) > 100:
                    text_cleaned = self._clean_text_for_rag(content_text[:50000])
                    items.append({
                        "item": item_num,
                        "name": item_title,
                        "text": text_cleaned,
                        "html": f"<p>{text_cleaned}</p>",
                    })
            
            return items
            
        except Exception as e:
            logger.error(f"Error in TextPatternStrategy: {e}", exc_info=True)
            return items


class GenericFallbackStrategy(ExtractionStrategy):
    """Generic fallback strategy - extract all available content"""
    
    def extract_sections(
        self, 
        filing: Any, 
        form_config: Dict[str, Any],
        form_type: str
    ) -> List[Dict[str, Any]]:
        """Extract all available content as generic sections"""
        items = []
        
        try:
            # Try to get text content
            text_content = None
            if hasattr(filing, 'text'):
                text_content = filing.text
            elif hasattr(filing, 'html'):
                html = filing.html
                if html:
                    try:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(str(html), 'html.parser')
                        text_content = soup.get_text(separator='\n', strip=True)
                    except:
                        text_content = str(html)
            
            if text_content and len(str(text_content).strip()) > 100:
                text_cleaned = self._clean_text_for_rag(str(text_content)[:50000])
                items.append({
                    "item": "1",
                    "name": f"{form_type} Content",
                    "text": text_cleaned,
                    "html": f"<p>{text_cleaned}</p>",
                })
                logger.info(f"Extracted generic content for {form_type} ({len(text_cleaned)} chars)")
            
            return items
            
        except Exception as e:
            logger.error(f"Error in GenericFallbackStrategy: {e}", exc_info=True)
            return items


def get_strategy(strategy_name: str) -> ExtractionStrategy:
    """Get extraction strategy by name"""
    strategies = {
        "structured_object": StructuredObjectStrategy(),
        "attribute_inspection": AttributeInspectionStrategy(),
        "html_pattern": HTMLPatternStrategy(),
        "text_pattern": TextPatternStrategy(),
        "generic": GenericFallbackStrategy(),
    }
    return strategies.get(strategy_name, GenericFallbackStrategy())

