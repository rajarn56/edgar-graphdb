# EDGAR Graph Database Test Scripts

## Overview

This directory contains test scripts to verify Neo4j graph database schema, EDGAR data ingestion, and retrieval functionality. These scripts validate the complete pipeline from EDGAR data retrieval to graph database storage and querying.

## Purpose

The scripts serve as a verification and testing suite for:
1. **Schema Setup**: Creating and validating Neo4j schema (constraints, indexes, vector indexes)
2. **Data Ingestion**: Retrieving EDGAR data, transforming it, generating embeddings, and writing to Neo4j
3. **Data Retrieval**: Querying Neo4j and displaying EDGAR data in readable formats

## Prerequisites

- Python 3.12+
- Neo4j running locally (default: bolt://localhost:7687)
- LMStudio running locally with embedding model configured
- Virtual environment (recommended)

## Setup

### 1. Create Virtual Environment

```bash 
uv venv edgarvenv --python 3.12
source venv/bin/activate
```

### 2. Install Dependencies

```bash
uv pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and update with your configuration:

```bash
cp .env.example .env
# Edit .env with your Neo4j and LMStudio settings
```

### 4. Ensure Neo4j is Running

```bash
# Check Neo4j is accessible
# Default: http://localhost:7474 (browser) and bolt://localhost:7687 (driver)
```

### 5. Ensure LMStudio is Running

```bash
# Start LMStudio server with embedding model loaded
# Default: http://localhost:1234/v1
```

## Scripts

### 1. `setup_schema.py`

Creates all Neo4j constraints, indexes, and vector indexes as per schema design v2.0.

**Usage**:
```bash
python setup_schema.py
```

**What it does**:
- Creates unique constraints for all primary keys
- Creates property indexes (including composite indexes)
- Creates specialized vector indexes for different content types
- Validates schema creation
- Idempotent (safe to run multiple times)

### 2. `ingest_edgar_data.py`

Retrieves EDGAR data for a ticker, transforms to graph format, and writes to Neo4j.

**Usage**:
```bash
python ingest_edgar_data.py --ticker AAPL
python ingest_edgar_data.py --ticker AAPL --form-type 10-K --fiscal-year 2024
python ingest_edgar_data.py --ticker AAPL --force  # Force re-ingestion
```

**Parameters**:
- `--ticker`: Stock ticker symbol (required)
- `--form-type`: Form type filter (optional, default: latest 10-K)
- `--fiscal-year`: Specific fiscal year (optional)
- `--force`: Force re-ingestion even if exists (optional)

**What it does**:
- Connects to Neo4j
- Retrieves EDGAR data using edgar-tools library
- Checks for existing data (handles duplicates)
- Transforms EDGAR structure to Neo4j format
- Generates embeddings using LMStudio
- Writes nodes and relationships to Neo4j
- Verifies ingestion

### 3. `retrieve_edgar_data.py`

Queries Neo4j and displays EDGAR data in readable format.

**Usage**:
```bash
python retrieve_edgar_data.py --ticker AAPL
python retrieve_edgar_data.py --ticker AAPL --form-type 10-K --fiscal-year 2024
python retrieve_edgar_data.py --ticker AAPL --section "Item 7"
python retrieve_edgar_data.py --ticker AAPL --format json
```

**Parameters**:
- `--ticker`: Stock ticker symbol (required)
- `--form-type`: Form type filter (optional)
- `--fiscal-year`: Fiscal year filter (optional)
- `--section`: Section/item number (optional, e.g., "Item 7")
- `--format`: Output format - json, table, or tree (optional, default: tree)

**What it does**:
- Queries company information
- Lists all filings for company
- Retrieves section content
- Displays financial statements
- Shows metrics and trends
- Performs vector search (if query provided)

### 4. `delete_schema.py`

⚠️ **WARNING**: This script will DELETE ALL DATA in the Neo4j database!

Completely removes all schema elements (nodes, relationships, constraints, indexes) from Neo4j database, making it clean again. This operation is irreversible.

**Usage**:
```bash
python delete_schema.py
python delete_schema.py --yes  # Skip confirmation prompt
```

**Parameters**:
- `--yes`: Skip confirmation prompt (use with extreme caution)

**What it does**:
- Shows current database statistics (node count, relationship count, constraints, indexes, property keys)
- Clears properties from all nodes before deletion (attempts to reduce property keys)
- Deletes all nodes and relationships
- Drops all constraints
- Drops all indexes (property, vector, full-text)
- Checks property keys metadata (property keys are harmless and may persist)
- Verifies deletion was successful
- Idempotent (safe to run multiple times)

**Note on Property Keys**: Property keys are metadata that may persist in Neo4j even after deleting all nodes. The script attempts to clear properties from nodes before deletion, which may help reduce property keys. However, property keys are harmless metadata and don't affect database functionality. They will be automatically cleared when Neo4j is restarted or the database is recreated.

**Equivalent Cypher Queries**:

The script performs the following operations, which can also be done manually:

```cypher
// Delete all nodes and relationships
MATCH (n)
DETACH DELETE n

// List all constraints
SHOW CONSTRAINTS

// Drop a specific constraint (example)
DROP CONSTRAINT company_cik_unique IF EXISTS

// List all indexes
SHOW INDEXES

// Drop a specific index (example)
DROP INDEX company_ticker IF EXISTS

// Drop a vector index (example)
DROP INDEX textChunkEmbeddings IF EXISTS

// Clear properties from all nodes before deletion (may help reduce property keys)
MATCH (n)
SET n = {}
RETURN count(n) AS nodes_updated

// List property keys (for information - property keys are harmless metadata)
CALL db.propertyKeys() YIELD propertyKey RETURN propertyKey

// Note: Property keys persist as metadata even after deleting nodes.
// They are harmless and don't affect functionality.
// To clear them: Restart Neo4j or recreate the database.
```

**When to use**:
- Before setting up a fresh schema
- To completely reset the database
- For testing/development cleanup
- When you need to start over with a clean database

**Safety Features**:
- Shows database statistics before deletion
- Requires confirmation prompt (unless `--yes` flag is used)
- Verifies deletion was successful
- Logs all operations for audit trail

## Execution Sequence

Follow this sequence for first-time setup:

1. **Setup Schema**:
   ```bash
   python setup_schema.py
   ```

2. **Ingest Test Data**:
   ```bash
   python ingest_edgar_data.py --ticker AAPL
   ```

3. **Verify Data**:
   ```bash
   python retrieve_edgar_data.py --ticker AAPL
   ```

### Clean Database (Optional)

To completely reset the database and start fresh:

```bash
# ⚠️ WARNING: This will delete all data!
python delete_schema.py

# Then run setup_schema.py again
python setup_schema.py
```

## Dependencies

See `requirements.txt` for complete list. Key dependencies:
- `neo4j>=5.15.0`: Neo4j Python driver
- `litellm>=1.30.0`: Multi-LLM provider for embeddings
- `loguru>=0.7.2`: Logging
- `python-dotenv>=1.0.0`: Environment variable management
- `pydantic>=2.5.0`: Data validation
- `tiktoken>=0.5.0`: Token counting for chunking

**Note on EDGAR Tools**: The scripts use `edgartools` library (https://github.com/dgunning/edgartools) for fetching SEC EDGAR data. Install it with:
```bash
pip install edgartools
```

**Important**: Set `EDGAR_IDENTITY` environment variable with your email address. The SEC requires this to identify who is accessing their data:
```bash
export EDGAR_IDENTITY=your.email@example.com
```
Or add it to your `.env` file.

## Environment Variables

Required environment variables (in `.env`):
- `NEO4J_URI`: Neo4j connection URI (default: bolt://localhost:7687)
- `NEO4J_USER`: Neo4j username (default: neo4j)
- `NEO4J_PASSWORD`: Neo4j password
- `EDGAR_IDENTITY`: Your email address (required by SEC for EDGAR access). Example: `your.email@example.com`
- `EMBEDDING_PROVIDER`: Embedding provider (default: lmstudio)
- `LM_STUDIO_API_BASE`: LMStudio API base URL (default: http://localhost:1234/v1)
- `EMBEDDING_MODEL`: Embedding model name
- `OPENAI_API_KEY`: OpenAI API key (optional, for fallback)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_DIR`: Log directory (default: logs)
- `NEO4J_DEBUG_LOGGING`: Enable debug logging for Neo4j client (default: false). Set to `true`, `1`, or `yes` to enable. Debug logs written to `logs/debug.log`

## Logging

Logs are written to the `logs/` directory:
- `setup_schema_YYYYMMDD.log`: Schema setup operations
- `delete_schema_YYYYMMDD.log`: Schema deletion operations
- `ingest_YYYYMMDD.log`: Ingestion operations
- `retrieve_YYYYMMDD.log`: Retrieval operations
- `errors_YYYYMMDD.log`: Error-only log

## Troubleshooting

### Neo4j Connection Issues

- Verify Neo4j is running: `docker ps` or check Neo4j service
- Check connection URI matches your setup
- Verify credentials in `.env` file
- Test connection: `cypher-shell -u neo4j -p password`

### LMStudio Embedding Issues

- Verify LMStudio server is running
- Check `LM_STUDIO_API_BASE` matches your LMStudio configuration
- Verify embedding model is loaded in LMStudio
- Check `EMBEDDING_MODEL` matches your model name
- If embeddings are all zeros, check LMStudio logs

### EDGAR Data Retrieval Issues

- Verify edgartools library is installed: `pip install edgartools`
- **Set EDGAR_IDENTITY environment variable** with your email address (required by SEC)
- Check network connectivity to SEC EDGAR
- Verify ticker symbol is valid (use uppercase)
- Check for rate limiting (SEC may throttle requests)
- If you see "Using mock data" warnings, edgartools is not installed or EDGAR_IDENTITY is not set

### Schema Creation Issues

- Ensure Neo4j version supports vector indexes (5.11+)
- Check Neo4j plugins are installed (if needed)
- Verify user has CREATE INDEX permissions
- Check logs for specific error messages
- Vector indexes may not be supported in older Neo4j versions (will log warning)

### Data Ingestion Issues

- Verify EDGAR tools library is installed and accessible
- Check ticker symbol is valid (use uppercase)
- Ensure sufficient disk space for embeddings
- Monitor embedding generation (may take time for large filings)
- Check for rate limiting from SEC EDGAR

### Data Retrieval Issues

- Verify data was ingested successfully
- Check ticker symbol matches ingested data
- Use correct form type and fiscal year filters
- Check Neo4j query logs for performance issues

## Architecture

See the plan document for detailed architecture and design decisions.

## Architecture

### Data Flow

```
EDGAR Tools → Data Transformer → Embedding Generator → Neo4j Database
     ↓              ↓                    ↓                  ↓
  Raw JSON    Graph Nodes         Vector Embeddings    Stored Graph
```

### Key Components

1. **EDGAR Client** (`utils/edgar_client.py`): Interfaces with edgar-tools library to fetch SEC filing data
2. **Data Transformer** (`utils/data_transformer.py`): Converts EDGAR JSON to Neo4j node/relationship structures with intelligent chunking
3. **Embedding Generator** (`utils/embedding_generator.py`): Generates vector embeddings using LMStudio (with OpenAI fallback)
4. **Neo4j Client** (`utils/neo4j_client.py`): Manages Neo4j connections with retry logic and session handling

### Chunking Strategy

- **Chunk Size**: 500-1000 tokens (default: 800)
- **Overlap**: 50-100 tokens (default: 75)
- **Context Preservation**: 100 tokens before/after each chunk
- **Semantic Types**: Automatically inferred (risk_discussion, financial_analysis, strategy, etc.)

### Upsert Logic

- **Company Nodes**: MERGE on CIK, update all properties
- **Filing Nodes**: MERGE on accession_number, update if changed
- **Sections**: MERGE on section_id, update content if changed
- **Chunks**: DELETE old chunks, CREATE new ones (for re-ingestion)
- **Relationships**: MERGE to avoid duplicates

## Notes

- All scripts are idempotent where possible (safe to run multiple times)
- Duplicate data is handled via MERGE operations
- Embeddings are generated using LMStudio with OpenAI fallback
- Chunking follows schema design: 500-1000 tokens with 50-100 token overlap
- Vector indexes are specialized by content type for better performance
- Schema setup must be run before ingestion
- Neo4j version 5.11+ required for vector indexes support

## Support

For issues or questions, refer to:
- Schema design: `../docs/neo4j-edgar-schema-design-v2.md`
- Schema diagram: `../docs/neo4j-edgar-schema-diagram-v2.md`
- Troubleshooting guide: `../docs/TROUBLESHOOTING.md`
- Logs in `logs/` directory

