# Form Registry Guide

## Overview

The Form Registry system provides a centralized, extensible way to configure and extract sections from all EDGAR form types. It supports multiple extraction strategies and ensures RAG compatibility for all extracted content.

## Architecture

### Components

1. **Form Registry** (`utils/form_registry.py`): Centralized configuration management
2. **Form Config** (`config/form_config.yaml`): YAML configuration file defining form metadata and extraction strategies
3. **Extraction Strategies** (`utils/extraction_strategies.py`): Strategy pattern implementations for different extraction methods
4. **EDGAR Client Integration**: Updated `edgar_client.py` to use registry and strategies
5. **Data Transformer Integration**: Updated `data_transformer.py` to use registry for schema labels

## Form Configuration

Forms are configured in `config/form_config.yaml` with the following structure:

```yaml
forms:
  "10-K":
    category: "periodic_report"
    name: "Annual Report"
    description: "Comprehensive annual report with audited financial statements"
    structured_object: "TenK"
    extraction_strategy: "structured_object"
    schema_labels:
      - "Section"
      - "PeriodicReportSection"
    section_mappings:
      "1": ["business", "Business"]
      "1A": ["risk_factors", "Risk Factors"]
    rag_compatible: true
```

### Configuration Fields

- **category**: Form category (periodic_report, proxy_governance, registration, ownership, investment, foreign, other)
- **name**: Human-readable form name
- **description**: Form description
- **structured_object**: edgartools structured object name (if applicable)
- **extraction_strategy**: Strategy to use (structured_object, attribute_inspection, html_pattern, text_pattern, generic)
- **schema_labels**: Neo4j schema labels to apply
- **section_mappings**: Section extraction mappings (varies by strategy)
- **rag_compatible**: Whether form is RAG-compatible (should always be true)

## Extraction Strategies

### 1. Structured Object Strategy

**Use for**: Forms with edgartools structured objects (10-K, 10-Q, 8-K)

**How it works**: Uses explicit section mappings to extract from structured objects

**Example**: 10-K uses `TenK` object with mappings for Items 1, 1A, 7, etc.

### 2. Attribute Inspection Strategy

**Use for**: Forms with structured objects but no explicit mappings (DEF 14A, DEF 14C)

**How it works**: Inspects object attributes using keyword matching and section mappings

**Example**: DEF 14A inspects for attributes like `compensation`, `directors`, `board`, etc.

### 3. HTML Pattern Matching Strategy

**Use for**: Forms with HTML content and identifiable section patterns (S-1, S-3, S-4, 20-F, 40-F)

**How it works**: Parses HTML using BeautifulSoup and regex patterns to find sections

**Example**: S-1 finds sections using "Item X" patterns in HTML

### 4. Text Pattern Matching Strategy

**Use for**: Forms with plain text content and structured patterns (Form 3, 4, 5, 13D, 13G)

**How it works**: Uses regex patterns to find sections in plain text

**Example**: Form 4 finds transaction sections using text patterns

### 5. Generic Fallback Strategy

**Use for**: Any form type as a last resort

**How it works**: Extracts all available content as a single generic section

**Example**: Form 144 extracts all content as one section

## RAG Compatibility

All extraction strategies ensure RAG compatibility by:

1. **Content Cleaning**: All content passes through `clean_text_for_rag()` method
2. **HTML Removal**: HTML tags removed, entities unescaped
3. **Whitespace Normalization**: Multiple spaces → single space, multiple newlines → double newline
4. **Control Character Removal**: Removes control characters and zero-width spaces
5. **Proper Chunking**: Content chunked with context preservation (500-1000 tokens, 50-100 token overlap)
6. **Embedding Context**: Embeddings include company, form type, fiscal year, section context

## Adding a New Form

To add support for a new form type:

1. **Add to `form_config.yaml`**:
   ```yaml
   "NEW-FORM":
     category: "category_name"
     name: "Form Name"
     description: "Form description"
     extraction_strategy: "strategy_name"
     schema_labels:
       - "Section"
     rag_compatible: true
   ```

2. **Implement extraction strategy** (if needed):
   - If using existing strategy, just configure mappings
   - If new strategy needed, add to `extraction_strategies.py`

3. **Test extraction**:
   ```bash
   python ingest_edgar_data.py --ticker AAPL --form-type "NEW-FORM"
   ```

4. **Verify RAG compatibility**:
   - Check that content is cleaned (no HTML tags)
   - Verify chunks are properly sized
   - Ensure embeddings include context

## Usage

### Using Form Registry in Code

```python
from utils.form_registry import get_registry

registry = get_registry()

# Get form configuration
config = registry.get_form_config("10-K")

# Get extraction strategy
strategy_name = registry.get_extraction_strategy("10-K")

# Get schema labels
labels = registry.get_schema_labels("DEF 14A")

# Check RAG compatibility
is_compatible = registry.is_rag_compatible("S-1")
```

### Ingesting All Forms

```bash
# Ingest all forms
./ingest_all_forms.sh AAPL

# Ingest specific category
./ingest_all_forms.sh AAPL periodic
./ingest_all_forms.sh AAPL ownership
```

## Form Categories

- **periodic**: 10-K, 10-Q, 8-K
- **proxy**: DEF 14A, DEF 14C
- **registration**: S-1, S-3, S-4, 10
- **ownership**: 3, 4, 5, 13D, 13G
- **investment**: 13F, N-CSR, 11-K
- **foreign**: 20-F, 40-F
- **other**: 144, 424B

## Troubleshooting

### Form Not Found

If a form is not found in the registry:
- Check `form_config.yaml` for the form
- Verify form type normalization (e.g., "DEF14A" → "DEF 14A")
- Check logs for form type used

### Extraction Fails

If extraction fails:
- Check which strategy is being used
- Verify form has content available (HTML/text)
- Check logs for specific error messages
- Try generic fallback strategy

### RAG Compatibility Issues

If content is not RAG-ready:
- Verify `clean_text_for_rag()` is being called
- Check for HTML tags in chunks
- Verify whitespace normalization
- Check chunk sizes and overlap

## Related Files

- `config/form_config.yaml`: Form configurations
- `utils/form_registry.py`: Registry implementation
- `utils/extraction_strategies.py`: Strategy implementations
- `utils/edgar_client.py`: EDGAR client with registry integration
- `utils/data_transformer.py`: Data transformer with registry integration
- `ingest_all_forms.sh`: Script to ingest all forms

