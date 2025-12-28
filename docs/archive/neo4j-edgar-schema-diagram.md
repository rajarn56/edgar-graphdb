# Neo4j EDGAR Graph Schema - Mermaid Diagram

## Complete Schema Diagram

```mermaid
erDiagram
    Company ||--o{ Filing : "FILED_BY"
    Filing ||--o{ Section : "CONTAINS (order)"
    Filing ||--o{ FinancialStatement : "CONTAINS"
    Filing ||--o{ RiskFactor : "CONTAINS (order)"
    Section ||--o{ Chunk : "CONTAINS (order, chunk_index)"
    Chunk ||--|| Embedding : "EMBEDDED_AS"
    Chunk ||--o{ Chunk : "PRECEDES (sequential order)"
    FinancialStatement ||--o{ LineItem : "HAS_LINE_ITEM (order, level)"
    LineItem ||--o{ Value : "HAS_VALUE"
    Value }o--|| Period : "FOR_PERIOD"
    FinancialStatement }o--|| Period : "FOR_PERIOD"
    Metric }o--|| Period : "FOR_PERIOD"
    LineItem ||--o{ Metric : "CALCULATES"
    Section ||--o{ Metric : "HAS_METRIC"
    Company ||--o{ Person : "HAS_EXECUTIVE"
    Company ||--o{ Company : "COMPETES_WITH"
    Filing ||--o{ Filing : "REFERENCES"
    Filing ||--o{ Filing : "AMENDS"

    Company {
        string cik PK
        string name
        string ticker
        string industry
        string sector
    }
    
    Filing {
        string accession_number PK
        string form_type
        date filing_date
        date period_end_date
        int fiscal_year
        int fiscal_quarter
        string url
        int file_size
        int page_count
    }
    
    Section {
        string section_id PK
        string item_number
        string item_title
        string content
        int content_length
        int start_page
        int end_page
        string chunking_status
    }
    
    Chunk {
        string chunk_id PK
        int chunk_index
        string content
        int content_length
        int start_char
        int end_char
        string chunk_type
        string semantic_type
    }
    
    Embedding {
        string embedding_id PK
        list vector
        string model
        int dimension
    }
    
    FinancialStatement {
        string statement_id PK
        string statement_type
        string period_type
        string currency
        string units
    }
    
    LineItem {
        string line_item_id PK
        string line_name
        string line_label
        string line_category
    }
    
    Value {
        string value_id PK
        float value
        date period_start
        date period_end
        int fiscal_year
        int fiscal_quarter
        string currency
        string units
    }
    
    Period {
        string period_id PK
        int fiscal_year
        int fiscal_quarter
        date period_start
        date period_end
    }
    
    Metric {
        string metric_id PK
        string metric_name
        string metric_type
        float value
        int fiscal_year
        string calculation_method
    }
    
    RiskFactor {
        string risk_id PK
        string risk_category
        string risk_title
        string risk_description
    }
    
    Person {
        string person_id PK
        string name
        string title
        string role_type
    }
```

## Hierarchical Relationship Flow

```mermaid
graph TD
    A[Company] -->|FILED_BY| B[Filing]
    B -->|CONTAINS order:1| C1[Section: Item 1]
    B -->|CONTAINS order:7| C2[Section: Item 7]
    B -->|CONTAINS order:8| C3[Section: Item 8]
    B -->|CONTAINS| D[FinancialStatement]
    
    C1 -->|CONTAINS chunk_index:0| E1[Chunk 0]
    C1 -->|CONTAINS chunk_index:1| E2[Chunk 1]
    C1 -->|CONTAINS chunk_index:2| E3[Chunk 2]
    
    C2 -->|CONTAINS chunk_index:0| F1[Chunk 0]
    C2 -->|CONTAINS chunk_index:1| F2[Chunk 1]
    C2 -->|CONTAINS chunk_index:2| F3[Chunk 2]
    C2 -->|CONTAINS chunk_index:3| F4[Chunk 3]
    
    E1 -->|PRECEDES| E2
    E2 -->|PRECEDES| E3
    
    F1 -->|PRECEDES| F2
    F2 -->|PRECEDES| F3
    F3 -->|PRECEDES| F4
    
    E1 -->|EMBEDDED_AS| G1[Embedding]
    E2 -->|EMBEDDED_AS| G2[Embedding]
    E3 -->|EMBEDDED_AS| G3[Embedding]
    F1 -->|EMBEDDED_AS| H1[Embedding]
    F2 -->|EMBEDDED_AS| H2[Embedding]
    F3 -->|EMBEDDED_AS| H3[Embedding]
    F4 -->|EMBEDDED_AS| H4[Embedding]
    
    D -->|HAS_LINE_ITEM| I[LineItem]
    I -->|HAS_VALUE| J[Value]
    J -->|FOR_PERIOD| K[Period]
    
    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C1 fill:#e8f5e9
    style C2 fill:#e8f5e9
    style C3 fill:#e8f5e9
    style E1 fill:#fce4ec
    style E2 fill:#fce4ec
    style E3 fill:#fce4ec
    style F1 fill:#fce4ec
    style F2 fill:#fce4ec
    style F3 fill:#fce4ec
    style F4 fill:#fce4ec
    style G1 fill:#f3e5f5
    style G2 fill:#f3e5f5
    style G3 fill:#f3e5f5
    style H1 fill:#f3e5f5
    style H2 fill:#f3e5f5
    style H3 fill:#f3e5f5
    style H4 fill:#f3e5f5
```

## Key Relationships Summary

### 1. Document Hierarchy (Filing → Section → Chunk)
- **Filing CONTAINS Section:** One-to-many, with `order` property
- **Section CONTAINS Chunk:** One-to-many, with `order` and `chunk_index` properties
- **Chunk PRECEDES Chunk:** Sequential ordering within section

### 2. Chunk Ordering
- **Property-based:** `chunk_index` (0, 1, 2, ...) for fast sorting
- **Relationship-based:** `PRECEDES` for graph traversal
- **Both mechanisms ensure correct order**

### 3. Citation Support
- **Filing:** accession_number, form_type, filing_date, url, fiscal_year
- **Section:** section_id, item_number, item_title, start_page, end_page
- **Chunk:** chunk_id, chunk_index, start_char, end_char
- **Full path traceable:** Company → Filing → Section → Chunk

### 4. Vector Search
- **Chunk → Embedding:** One-to-one relationship
- **Each chunk has exactly one embedding**
- **Vector index on Embedding.vector for similarity search**

## Example: Retrieving Ordered Chunks with Citations

```cypher
// Get chunks for a section in order with full citation path
MATCH (c:Company {cik: "0000320193"})<-[:FILED_BY]-(f:Filing {accession_number: "0000320193-24-000077"})
MATCH (f)-[:CONTAINS]->(s:Section {item_number: "Item 7"})
MATCH (s)-[:CONTAINS]->(ch:Chunk)
MATCH (ch)-[:EMBEDDED_AS]->(e:Embedding)
RETURN 
  c.name AS company_name,
  c.ticker AS ticker,
  f.form_type AS form_type,
  f.fiscal_year AS fiscal_year,
  f.url AS filing_url,
  s.item_number AS section_item,
  s.item_title AS section_title,
  s.start_page AS section_start_page,
  s.end_page AS section_end_page,
  ch.chunk_index AS chunk_order,
  ch.chunk_id AS chunk_id,
  ch.content AS chunk_content,
  ch.start_char AS chunk_start_char,
  ch.end_char AS chunk_end_char,
  e.embedding_id AS embedding_id
ORDER BY ch.chunk_index ASC;
```

This query returns chunks in order with all information needed for citations.

