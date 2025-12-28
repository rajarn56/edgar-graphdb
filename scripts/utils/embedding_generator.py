"""Embedding generation using LMStudio with OpenAI fallback"""

import os
from typing import List, Optional
import litellm
from loguru import logger


class EmbeddingGenerator:
    """Handles embedding generation for vector database with LMStudio support"""
    
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_base: Optional[str] = None
    ):
        """
        Initialize embedding generator.
        
        Args:
            provider: Embedding provider (lmstudio, openai, etc.)
                     If None, uses EMBEDDING_PROVIDER env var or defaults to lmstudio
            model: Embedding model name
                   If None, uses EMBEDDING_MODEL env var or provider default
            api_base: API base URL (for LMStudio)
                     If None, uses LM_STUDIO_API_BASE env var
        """
        # Get provider
        embedding_provider = os.getenv("EMBEDDING_PROVIDER")
        if embedding_provider:
            self.provider = embedding_provider
        elif provider:
            self.provider = provider
        else:
            self.provider = "lmstudio"  # Default to LMStudio
        
        # Get model
        embedding_model_env = os.getenv("EMBEDDING_MODEL")
        if model:
            self.embedding_model = model
        elif embedding_model_env:
            self.embedding_model = embedding_model_env
        elif self.provider == "openai":
            self.embedding_model = "text-embedding-ada-002"
        elif self.provider == "lmstudio":
            self.embedding_model = embedding_model_env or "text-embedding-ada-002"
        else:
            self.embedding_model = "text-embedding-ada-002"
        
        # Get API base for LMStudio
        if api_base:
            self.api_base = api_base
        else:
            self.api_base = os.getenv("LM_STUDIO_API_BASE", "http://localhost:1234/v1")
        
        # Cache for detected embedding dimension
        self._cached_dimension: Optional[int] = None
        
        logger.info(f"EmbeddingGenerator initialized: provider={self.provider}, model={self.embedding_model}")
        if self.provider == "lmstudio":
            logger.info(f"LMStudio API base: {self.api_base}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector (list of floats)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding, returning zero vector")
            return [0.0] * self.get_embedding_dimension()
        
        # LMStudio uses OpenAI-compatible API
        if self.provider == "lmstudio":
            return self._generate_lmstudio_embedding(text)
        
        # OpenAI or other providers
        return self._generate_openai_embedding(text)
    
    def _generate_lmstudio_embedding(self, text: str) -> List[float]:
        """Generate embedding using LMStudio"""
        try:
            # Set up LMStudio API base
            if self.api_base:
                os.environ["OPENAI_API_BASE"] = self.api_base
            
            # LiteLLM requires OPENAI_API_KEY to be set even for LMStudio
            # Set a dummy key if not already set - LMStudio doesn't actually use it
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                os.environ["OPENAI_API_KEY"] = "lm-studio"
            
            # Format model name for LiteLLM
            model_name = self.embedding_model
            if not model_name.startswith("openai/"):
                model_name = f"openai/{model_name}"
            
            logger.debug(f"Generating LMStudio embedding with model: {model_name}")
            
            # Generate embedding
            response = litellm.embedding(
                model=model_name,
                input=[text],
                api_base=self.api_base
            )
            embedding = response.data[0]["embedding"]
            
            # Validate embedding is not all zeros
            if all(x == 0.0 for x in embedding):
                logger.warning("Received zero vector from LMStudio embedding API")
                raise ValueError("Zero vector received from LMStudio")
            
            # Cache the dimension
            self._cached_dimension = len(embedding)
            logger.debug(f"Successfully generated LMStudio embedding (dimension: {self._cached_dimension})")
            return embedding
            
        except Exception as e:
            logger.warning(f"LMStudio embedding failed: {e}")
            logger.info("Falling back to OpenAI embeddings")
            return self._generate_openai_embedding(text, is_fallback=True)
    
    def _generate_openai_embedding(self, text: str, is_fallback: bool = False) -> List[float]:
        """Generate embedding using OpenAI (or as fallback)"""
        try:
            # Check if OpenAI API key is available
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key or openai_key == "lm-studio":
                if is_fallback:
                    logger.warning("No OPENAI_API_KEY found, using zero vector fallback")
                    return [0.0] * self.get_embedding_dimension()
                else:
                    logger.warning("No OPENAI_API_KEY found for OpenAI embeddings")
                    return [0.0] * self.get_embedding_dimension()
            
            # Use OpenAI embeddings
            response = litellm.embedding(
                model="text-embedding-ada-002",
                input=[text]
            )
            embedding = response.data[0]["embedding"]
            
            # Cache the dimension
            self._cached_dimension = len(embedding)
            
            # Validate embedding is not all zeros
            if all(x == 0.0 for x in embedding):
                logger.warning("Received zero vector from OpenAI embedding API")
            else:
                if is_fallback:
                    logger.info("Successfully generated OpenAI embedding (fallback)")
                else:
                    logger.debug("Successfully generated OpenAI embedding")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate OpenAI embedding: {e}")
            logger.warning("Using zero vector fallback - semantic search will be disabled")
            return [0.0] * self.get_embedding_dimension()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        total = len(texts)
        for idx, text in enumerate(texts, 1):
            if idx % 10 == 0:
                logger.info(f"Generating embeddings: {idx}/{total}")
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for the current model.
        Detects dimension dynamically by generating a test embedding if not cached.
        
        Returns:
            Embedding dimension (e.g., 1536 for OpenAI ada-002)
        """
        # Return cached dimension if available
        if self._cached_dimension is not None:
            return self._cached_dimension
        
        # Try to detect dimension by generating a test embedding
        try:
            test_embedding = self.generate_embedding("test")
            if test_embedding and len(test_embedding) > 0 and not all(x == 0.0 for x in test_embedding):
                self._cached_dimension = len(test_embedding)
                logger.debug(f"Detected embedding dimension: {self._cached_dimension} for model {self.embedding_model}")
                return self._cached_dimension
        except Exception as e:
            logger.debug(f"Could not detect dimension dynamically: {e}")
        
        # Fallback to known dimensions based on model name
        model_lower = self.embedding_model.lower()
        if "nomic-embed" in model_lower or "nomic-embed-text" in model_lower:
            self._cached_dimension = 768
            logger.debug("Using known dimension 768 for nomic-embed model")
            return 768
        elif "ada-002" in model_lower or "text-embedding-ada-002" in model_lower:
            self._cached_dimension = 1536
            logger.debug("Using known dimension 1536 for ada-002 model")
            return 1536
        elif "text-embedding-3" in model_lower:
            self._cached_dimension = 1536
            return 1536
        else:
            # Default fallback (will be corrected on first actual embedding)
            self._cached_dimension = 1536
            logger.warning(f"Unknown model {self.embedding_model}, defaulting to dimension 1536")
            return 1536
    
    def prepare_embedding_input(
        self,
        chunk_content: str,
        context_before: Optional[str] = None,
        context_after: Optional[str] = None,
        company_name: Optional[str] = None,
        company_ticker: Optional[str] = None,
        form_type: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        section_item: Optional[str] = None
    ) -> str:
        """
        Prepare text for embedding with context (as per schema design).
        
        Args:
            chunk_content: Main chunk content
            context_before: Context before chunk (100 tokens)
            context_after: Context after chunk (100 tokens)
            company_name: Company name for context
            company_ticker: Company ticker for context
            form_type: Form type (e.g., "10-K")
            fiscal_year: Fiscal year
            section_item: Section/item number (e.g., "Item 7")
        
        Returns:
            Formatted text ready for embedding
        """
        parts = []
        
        # Company context
        if company_name:
            ticker_str = f" ({company_ticker})" if company_ticker else ""
            parts.append(f"Company: {company_name}{ticker_str}")
        
        # Filing context
        if form_type and fiscal_year:
            parts.append(f"Filing: {form_type} {fiscal_year}")
        
        # Section context
        if section_item:
            parts.append(f"Section: {section_item}")
        
        # Context before
        if context_before:
            parts.append(f"[Context] {context_before}")
        
        # Main content
        parts.append(chunk_content)
        
        # Context after
        if context_after:
            parts.append(f"[Context] {context_after}")
        
        return "\n".join(parts)

