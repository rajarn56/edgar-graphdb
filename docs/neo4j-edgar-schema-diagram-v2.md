# Neo4j EDGAR Graph Schema - Mermaid Diagram v2.0

## Complete Schema Diagram

```mermaid
@include diagrams/complete-schema-diagram.mmd
```

## Hierarchical Relationship Flow

```mermaid
@include diagrams/hierarchical-relationship-flow.mmd
```

## Key Design Changes from v1.0

### 1. Vector Storage (OPTIMIZED)
- ✅ **Embeddings stored directly on Chunk nodes** as `embedding` property
- ❌ **NO separate Embedding nodes** (removed in v2.0)
- **Benefit**: Single node access, 50% fewer query hops

### 2. Chunk Ordering (SIMPLIFIED)
- ✅ **Property-based ordering only**: `chunk_index` (0, 1, 2, ...)
- ❌ **NO PRECEDES relationships** (removed in v2.0)
- **Benefit**: Simpler queries, faster ordering with `ORDER BY chunk_index`

### 3. Form-Specific Section Types (NEW)
- ✅ **Form8KItem**: For 8-K filings with event-specific properties
- ✅ **ProxySection**: For DEF 14A filings with governance properties
- ✅ **PeriodicReportSection**: For 10-K/10-Q filings with audit properties
- **Benefit**: Type-specific queries, better semantic understanding

### 4. Denormalization for Performance (NEW)
- ✅ **Direct FROM_COMPANY relationship** from Chunk to Company
- ✅ **Denormalized properties** on Chunk: `company_cik`, `fiscal_year`, `form_type`, `section_item`
- **Benefit**: Filter chunks without traversing Filing/Section hierarchy

### 5. Enhanced Entity Model (NEW)
- ✅ **Industry & Sector**: Hierarchical classification
- ✅ **Topic**: Semantic topics discussed in chunks
- ✅ **Product**: Products mentioned in filings
- ✅ **GeographicRegion**: Geographic revenue breakdown
- ✅ **PeerGroup**: Systematic peer comparison support

### 6. Governance & Ownership (NEW)
- ✅ **Person, Role, Compensation**: Executive compensation tracking
- ✅ **Transaction, OwnershipPosition**: Insider trading support
- ✅ **Board, Committee**: Board composition and governance

### 7. M&A Transactions (NEW)
- ✅ **MandATransaction**: Acquisition, divestiture, merger tracking
- ✅ Links to acquiring and target companies
- ✅ Links to filings where announced

### 8. Enhanced Financial Model (IMPROVED)
- ✅ **MetricTrend**: Trend analysis over time periods
- ✅ **XBRL support**: `xbrl_tag`, `xbrl_namespace` on LineItem
- ✅ **TableChunk**: Structured table representation

## Query Pattern Examples

### Vector Search (Optimized - 2 hops instead of 6)
```cypher
// Direct vector search with company filtering
CALL db.index.vector.queryNodes('textChunkEmbeddings', 20, $queryEmbedding)
YIELD node AS chunk, score
WHERE chunk.company_cik = $cik 
  AND chunk.fiscal_year = $year
  AND score > 0.7
MATCH (chunk)-[:FROM_COMPANY]->(company:Company)
RETURN 
  company.name,
  chunk.form_type,
  chunk.fiscal_year,
  chunk.section_item,
  chunk.content,
  score
ORDER BY score DESC
LIMIT 10;
```

### Ordered Chunk Retrieval (Simplified - No PRECEDES)
```cypher
// Get chunks in order using property-based ordering
MATCH (c:Company {cik: $cik})<-[:FILED_BY]-(f:Filing {accession_number: $accession})
MATCH (f)-[:CONTAINS]->(s:Section {item_number: "Item 7"})
MATCH (s)-[:CONTAINS]->(ch:Chunk)
WHERE ch.company_cik = $cik  // Filter using denormalized property
RETURN 
  c.name AS company_name,
  f.form_type,
  f.fiscal_year,
  s.item_number,
  ch.chunk_index,
  ch.content,
  ch.embedding  // Direct access to embedding
ORDER BY ch.chunk_index ASC;  // Simple property ordering
```

### Peer Comparison (NEW)
```cypher
// Compare metrics across peer group
MATCH (target:Company {cik: $cik})-[:MEMBER_OF]->(pg:PeerGroup)<-[:MEMBER_OF]-(peer:Company)
MATCH (m1:Metric {company_cik: target.cik, metric_name: 'revenue', fiscal_year: $year})
MATCH (m2:Metric {company_cik: peer.cik, metric_name: 'revenue', fiscal_year: $year})
RETURN 
  target.name AS target,
  m1.value AS target_revenue,
  peer.name AS peer,
  m2.value AS peer_revenue,
  (m1.value / m2.value) AS ratio
ORDER BY m2.value DESC;
```

## Performance Optimizations

### 1. Reduced Query Hops
- **v1.0**: Company → Filing → Section → Chunk → Embedding (5 hops)
- **v2.0**: Chunk → Company (1 hop) + direct embedding property (0 hops)
- **Improvement**: 60% reduction in query complexity

### 2. Specialized Vector Indexes
- `textChunkEmbeddings`: General text content
- `riskChunkEmbeddings`: Risk factor discussions
- `financialChunkEmbeddings`: Financial analysis
- `strategyChunkEmbeddings`: Strategic/forward-looking content
- `maChunkEmbeddings`: M&A and transactions

### 3. Composite Indexes
- `filing_company_period`: (company_cik, fiscal_year, form_type)
- `chunk_company_period`: (company_cik, fiscal_year, chunk_type)
- `metric_company_period`: (company_cik, metric_name, fiscal_year)

## Citation Support

Full citation path preserved:
- **Company**: cik, name, ticker
- **Filing**: accession_number, form_type, filing_date, fiscal_year, url
- **Section**: section_id, item_number, item_title, start_page, end_page
- **Chunk**: chunk_id, chunk_index, start_char, end_char
- **Direct access**: Chunk → Company (via FROM_COMPANY relationship)

---

**Version:** 2.0  
**Date:** 2025-12-28  
**Status:** Production-Ready Design  
**Based on:** neo4j-edgar-schema-design-v2.md


