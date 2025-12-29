"""Form registry for EDGAR form types - centralized configuration"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger


class FormRegistry:
    """Registry for EDGAR form configurations"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize form registry.
        
        Args:
            config_path: Path to form_config.yaml. If None, uses default location.
        """
        if config_path is None:
            # Default to config/form_config.yaml relative to this file
            scripts_dir = Path(__file__).parent.parent
            config_path = scripts_dir / "config" / "form_config.yaml"
        
        self.config_path = config_path
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._load_config()
    
    def _load_config(self):
        """Load form configurations from YAML file"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Form config file not found: {self.config_path}")
                logger.warning("Using default form configurations")
                self._load_default_config()
                return
            
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self._registry = config.get('forms', {})
            logger.info(f"Loaded {len(self._registry)} form configurations from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error loading form config: {e}")
            logger.warning("Falling back to default configurations")
            self._load_default_config()
    
    def _load_default_config(self):
        """Load default form configurations (fallback)"""
        # Default configurations for critical forms
        self._registry = {
            "10-K": {
                "category": "periodic_report",
                "structured_object": "TenK",
                "extraction_strategy": "structured_object",
                "schema_labels": ["Section", "PeriodicReportSection"],
                "rag_compatible": True,
            },
            "10-Q": {
                "category": "periodic_report",
                "structured_object": "TenQ",
                "extraction_strategy": "structured_object",
                "schema_labels": ["Section", "PeriodicReportSection"],
                "rag_compatible": True,
            },
            "8-K": {
                "category": "periodic_report",
                "structured_object": "EightK",
                "extraction_strategy": "structured_object",
                "schema_labels": ["Section", "Form8KItem"],
                "rag_compatible": True,
            },
            "DEF 14A": {
                "category": "proxy_governance",
                "structured_object": "Def14A",
                "extraction_strategy": "attribute_inspection",
                "schema_labels": ["Section", "ProxySection"],
                "rag_compatible": True,
            },
        }
    
    def get_form_config(self, form_type: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a form type.
        
        Args:
            form_type: Form type (e.g., "10-K", "DEF 14A")
        
        Returns:
            Form configuration dictionary or None if not found
        """
        # Normalize form type (handle variations)
        normalized = self._normalize_form_type(form_type)
        return self._registry.get(normalized)
    
    def _normalize_form_type(self, form_type: str) -> str:
        """Normalize form type to match registry keys"""
        # Handle common variations
        form_type = form_type.strip().upper()
        
        # Map variations
        variations = {
            "DEF14A": "DEF 14A",
            "DEF-14A": "DEF 14A",
            "DEF 14A": "DEF 14A",
            "DEF14C": "DEF 14C",
            "DEF-14C": "DEF 14C",
            "DEF 14C": "DEF 14C",
            "S1": "S-1",
            "S3": "S-3",
            "S4": "S-4",
        }
        
        return variations.get(form_type, form_type)
    
    def get_extraction_strategy(self, form_type: str) -> str:
        """Get extraction strategy for a form type"""
        config = self.get_form_config(form_type)
        if config:
            return config.get("extraction_strategy", "generic")
        return "generic"
    
    def get_schema_labels(self, form_type: str) -> List[str]:
        """Get schema labels for a form type"""
        config = self.get_form_config(form_type)
        if config:
            return config.get("schema_labels", ["Section"])
        return ["Section"]
    
    def get_structured_object_name(self, form_type: str) -> Optional[str]:
        """Get structured object name for a form type"""
        config = self.get_form_config(form_type)
        if config:
            return config.get("structured_object")
        return None
    
    def get_section_mappings(self, form_type: str) -> Dict[str, Any]:
        """Get section mappings for a form type"""
        config = self.get_form_config(form_type)
        if config:
            return config.get("section_mappings", {})
        return {}
    
    def is_rag_compatible(self, form_type: str) -> bool:
        """Check if form type is RAG compatible"""
        config = self.get_form_config(form_type)
        if config:
            return config.get("rag_compatible", True)
        return True  # Default to True
    
    def get_all_forms(self) -> List[str]:
        """Get list of all registered form types"""
        return list(self._registry.keys())
    
    def get_forms_by_category(self, category: str) -> List[str]:
        """Get forms in a specific category"""
        return [
            form_type for form_type, config in self._registry.items()
            if config.get("category") == category
        ]
    
    def get_form_metadata(self, form_type: str) -> Dict[str, Any]:
        """Get metadata for a form type"""
        config = self.get_form_config(form_type)
        if config:
            return {
                "name": config.get("name", form_type),
                "description": config.get("description", ""),
                "category": config.get("category", "other"),
            }
        return {
            "name": form_type,
            "description": "",
            "category": "other",
        }


# Global registry instance
_registry_instance: Optional[FormRegistry] = None


def get_registry() -> FormRegistry:
    """Get global form registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = FormRegistry()
    return _registry_instance

