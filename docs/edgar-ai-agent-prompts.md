# EDGAR AI Agent Prompts & Analysis Guide

## Overview
This document provides an exhaustive list of prompts/questions that users can ask an AI agent analyzing EDGAR filings. For each prompt, it specifies:
- Which forms contain the relevant data
- Specific sections within those forms
- How to interpret and analyze the data
- Guidance for the AI agent on providing accurate answers

**Important:** All prompts in this guide are designed to serve **both financially knowledgeable and non-financially knowledgeable users**. Each prompt's AI Agent Guidance section includes:
- Instructions for non-financial users (plain language, definitions, benchmarks, practical interpretations)
- Instructions for financial users (technical details, advanced metrics, peer comparisons)

The AI agent should adapt responses based on the user's apparent knowledge level or provide both levels of detail when uncertain.

---

## User Adaptation Framework

### Understanding User Types

The AI agent must adapt responses to serve two distinct user types:

1. **Financially Knowledgeable Users:**
   - Understand financial terminology and concepts
   - Familiar with financial statements and ratios
   - Can interpret technical metrics without explanation
   - Prefer concise, technical responses with industry jargon

2. **Non-Financially Knowledgeable Users:**
   - May not understand financial terminology
   - Need explanations of what metrics mean and why they matter
   - Require context and benchmarks to interpret numbers
   - Prefer plain language with analogies and examples

### Adaptation Strategy

For each prompt, the AI agent should:

1. **Detect User Knowledge Level** (if possible):
   - Analyze user's question phrasing (technical vs. plain language)
   - Consider user's follow-up questions
   - Default to non-financial user approach if uncertain

2. **Provide Dual-Level Responses:**
   - **For Non-Financial Users:**
     - Start with a simple, direct answer in plain language
     - Define all financial terms when first used
     - Provide context: "This means..." or "In simple terms..."
     - Include benchmarks: "This is considered good/bad because..."
     - Use analogies and real-world examples
     - Explain why the metric matters
     - Provide visual aids when helpful (tables, simple charts)
   
   - **For Financial Users:**
     - Provide technical, concise answers
     - Use standard financial terminology
     - Include detailed calculations and methodologies
     - Reference industry standards and peer comparisons
     - Provide deeper analytical insights

3. **Common Elements for Both:**
   - Accurate data extraction and calculations
   - Clear data presentation (tables, numbers)
   - Trend identification and analysis
   - Risk factors and caveats
   - Source citations (which forms/sections)

### Response Structure Template

**For Non-Financial Users:**
```
[Simple Answer] - Direct answer in plain language
[What This Means] - Explanation of the concept/metric
[Why It Matters] - Context and importance
[The Numbers] - Data presentation with context
[What's Good/Bad] - Benchmarks and interpretation
[Key Takeaways] - Summary in simple terms
```

**For Financial Users:**
```
[Technical Answer] - Concise response with metrics
[Methodology] - Calculation approach
[Data Analysis] - Detailed numbers and trends
[Peer Comparison] - Industry benchmarks
[Analytical Insights] - Deeper analysis
[Key Metrics] - Summary of key ratios/figures
```

---

## Table of Contents
1. [Performance Analysis Prompts](#performance-analysis-prompts)
2. [Trend Analysis Prompts](#trend-analysis-prompts)
3. [Comparative Analysis Prompts](#comparative-analysis-prompts)
4. [Risk Analysis Prompts](#risk-analysis-prompts)
5. [Valuation & Financial Health Prompts](#valuation--financial-health-prompts)
6. [Strategic & Operational Prompts](#strategic--operational-prompts)
7. [Governance & Management Prompts](#governance--management-prompts)
8. [Ownership & Insider Activity Prompts](#ownership--insider-activity-prompts)
9. [M&A & Corporate Actions Prompts](#ma--corporate-actions-prompts)
10. [Forward-Looking & Guidance Prompts](#forward-looking--guidance-prompts)
11. [Sector & Industry Analysis Prompts](#sector--industry-analysis-prompts)
12. [Compliance & Regulatory Prompts](#compliance--regulatory-prompts)

---

## Performance Analysis Prompts

### P1: What is the company's revenue growth rate over the past 5 years?

**Forms Required:**
- **Form 10-K** (5 years of filings)

**Sections to Analyze:**
- **Item 6: Selected Financial Data** - Provides 5-year summary of key metrics including net sales/revenue
- **Item 8: Financial Statements and Supplementary Data** - Income Statement (Consolidated Statements of Operations)
  - Look for "Net sales", "Revenue", "Total revenue", or "Net revenues" line items
- **Item 7: Management's Discussion and Analysis (MD&A)** - Section discussing revenue trends

**How to Interpret:**
1. Extract revenue figures from each year's 10-K Item 6 or Item 8
2. Calculate year-over-year growth: ((Current Year - Prior Year) / Prior Year) × 100
3. Calculate 5-year CAGR: ((Final Year / First Year)^(1/5) - 1) × 100
4. Identify any years with negative growth or acceleration
5. Check MD&A for management's explanation of growth drivers

**AI Agent Guidance:**

**For Non-Financial Users:**
- Start with simple explanation: "Revenue growth tells us how fast the company is making more money each year"
- Define terms: "Year-over-year (YoY) growth compares this year to last year. CAGR (Compound Annual Growth Rate) shows the average growth rate over 5 years"
- Provide context: "A 10% growth rate means the company made 10% more money than the previous year"
- Use benchmarks: "Generally, growth above 5-10% is considered good for mature companies, while startups may grow 20-50%+"
- Explain what the numbers mean: "If revenue grew from $100M to $150M over 5 years, that's a 50% total increase, or about 8.4% per year on average"
- Highlight trends in plain language: "The company's growth is accelerating/decelerating/stable"
- Format: "Company X's revenue (the money it makes from selling products/services) increased from $Y million in Year 1 to $Z million in Year 5. This means the company grew by an average of X% per year. The growth was [consistent/volatile/accelerating]. This is [good/average/concerning] because [reason]"

**For Financial Users:**
- Present growth rates both as YoY percentages and 5-year CAGR
- Highlight any significant changes in growth trajectory
- Reference MD&A explanations for growth drivers
- Note any one-time events (acquisitions, divestitures) that affected growth
- Include growth quality analysis (organic vs. acquisition-driven)
- Format: "Company X's revenue grew from $Y in Year 1 to $Z in Year 5, representing a CAGR of X% and YoY growth rates of [list]. Growth trajectory shows [analysis]. Key drivers per MD&A: [factors]"

---

### P2: What are the company's profit margins (gross, operating, net) and how have they trended?

**Forms Required:**
- **Form 10-K** (multiple years for trend analysis)
- **Form 10-Q** (for quarterly margin trends)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Income Statement
  - Gross profit = Revenue - Cost of Goods Sold (COGS)
  - Operating income = Gross profit - Operating expenses
  - Net income = Operating income - Interest - Taxes + Other items
- **Form 10-K, Item 6: Selected Financial Data** - Historical margin data
- **Form 10-K, Item 7: MD&A** - Discussion of margin trends and drivers
- **Form 10-Q, Part I, Item 1: Financial Statements** - Quarterly income statements

**How to Interpret:**
1. Calculate margins:
   - Gross Margin = (Gross Profit / Revenue) × 100
   - Operating Margin = (Operating Income / Revenue) × 100
   - Net Margin = (Net Income / Revenue) × 100
2. Compare margins across years to identify trends
3. Analyze quarterly margins (10-Q) for short-term trends
4. Review MD&A for explanations of margin changes
5. Identify which expense categories are driving margin changes

**AI Agent Guidance:**

**For Non-Financial Users:**
- Start with simple explanation: "Profit margins show how much profit the company keeps from each dollar of sales"
- Define each margin type:
  - "Gross margin: After paying for the product itself, how much is left? This shows pricing power"
  - "Operating margin: After all operating costs (salaries, rent, etc.), how much profit remains? This shows efficiency"
  - "Net margin: After everything including taxes and interest, the final profit percentage"
- Provide context: "A 20% net margin means for every $100 in sales, the company keeps $20 as profit"
- Use benchmarks: "Net margins vary by industry - tech companies often have 15-25%, retailers may have 2-5%, software companies can have 30%+"
- Explain trends: "If margins are increasing, the company is becoming more profitable. If decreasing, costs are rising faster than prices"
- Format: "Profit margins show how profitable the company is. Gross margin (profit after product costs): X% - this is [good/average/low] for this industry. Operating margin (profit after all operating expenses): Y% - this shows the company is [efficient/struggling]. Net margin (final profit after everything): Z% - meaning the company keeps Z cents from each dollar of sales. Over time, margins have [improved/declined/stayed stable], which indicates [interpretation]"

**For Financial Users:**
- Present margins as percentages with trend indicators (↑, ↓, →)
- Explain drivers of margin changes (cost inflation, pricing power, efficiency gains, operating leverage)
- Compare quarterly vs. annual margins to identify seasonality
- Highlight any margin compression or expansion periods
- Analyze margin quality (sustainable vs. one-time factors)
- Format: "Gross margin: X% (trend), Operating margin: Y% (trend), Net margin: Z% (trend). Key drivers: [explanation]. Margin quality: [analysis]"

---

### P3: What is the company's return on equity (ROE) and return on assets (ROA)?

**Forms Required:**
- **Form 10-K** (multiple years)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements**
  - Balance Sheet: Total assets, Total shareholders' equity
  - Income Statement: Net income
- **Form 10-K, Item 6: Selected Financial Data** - May include ROE/ROA directly

**How to Interpret:**
1. Calculate ROE = (Net Income / Average Shareholders' Equity) × 100
   - Use average equity: (Beginning Equity + Ending Equity) / 2
2. Calculate ROA = (Net Income / Average Total Assets) × 100
   - Use average assets: (Beginning Assets + Ending Assets) / 2
3. Compare to prior years to identify trends
4. Compare to industry benchmarks (if available)

**AI Agent Guidance:**

**For Non-Financial Users:**
- Start with simple explanation: "ROE and ROA measure how well the company uses money to make profit"
- Define terms:
  - "ROE (Return on Equity): How much profit the company makes for each dollar shareholders invested. If ROE is 15%, shareholders get 15 cents profit per dollar invested"
  - "ROA (Return on Assets): How efficiently the company uses all its assets (buildings, equipment, cash) to make profit"
- Provide context: "Think of it like this: If you invest $100 in a business and it makes $15 profit, that's 15% ROE"
- Use benchmarks: "ROE above 15% is generally considered good. ROA above 5-10% is typically strong, but varies by industry"
- Explain what it means: "Higher ROE/ROA means the company is better at turning investments into profits"
- Format: "Return on Equity (ROE) measures how much profit the company makes from shareholder investments. Company X has an ROE of X%, meaning for every $100 shareholders invested, the company generates $X in profit. This is [excellent/good/average/poor] compared to typical companies (15%+ is good). Return on Assets (ROA) shows how efficiently the company uses all its assets - Company X has Y% ROA, which means [interpretation]. Over time, these returns have [improved/declined], indicating [trend analysis]"

**For Financial Users:**
- Calculate using average balance sheet figures (not year-end)
- Present both absolute values and trends
- Explain what ROE/ROA levels indicate (e.g., ROE >15% generally good, but industry-dependent)
- Decompose ROE using DuPont analysis if relevant (ROE = Net Margin × Asset Turnover × Equity Multiplier)
- Note any significant changes and potential causes
- Compare to cost of equity/cost of capital
- Format: "ROE: X% (trend from Y% to Z%), ROA: A% (trend). ROE decomposition: [if applicable]. vs. Cost of Equity: [comparison]. This indicates [interpretation]"

---

### P4: How much free cash flow does the company generate?

**Forms Required:**
- **Form 10-K** (multiple years)
- **Form 10-Q** (for quarterly FCF)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Statement of Cash Flows
  - Operating Cash Flow (from operating activities)
  - Capital Expenditures (from investing activities, typically negative)
- **Form 10-K, Item 7: MD&A** - Discussion of cash flow generation

**How to Interpret:**
1. Calculate Free Cash Flow (FCF) = Operating Cash Flow - Capital Expenditures
2. Calculate FCF margin = (FCF / Revenue) × 100
3. Track FCF trends over multiple years
4. Identify FCF conversion rate: FCF / Net Income
5. Review MD&A for cash flow drivers and uses

**AI Agent Guidance:**

**For Non-Financial Users:**
- Start with simple explanation: "Free cash flow is the money left over after the company pays for its operations and necessary investments"
- Define terms: "It's like your take-home pay after paying bills and necessary expenses - money you can use for anything"
- Explain calculation: "Free Cash Flow = Money from operations - Money spent on equipment/buildings"
- Provide context: "Positive FCF means the company generates more cash than it spends. Negative FCF means it's spending more than it makes"
- Use benchmarks: "FCF should generally be positive for healthy companies. FCF of 10-20% of revenue is typically strong"
- Explain why it matters: "Companies with strong FCF can pay dividends, buy back stock, pay down debt, or invest in growth without borrowing"
- Format: "Free Cash Flow (FCF) is the cash the company has left after paying for operations and necessary investments. Company X generated $X million in FCF, which is Y% of its revenue. This means the company has $X million available to pay dividends, reduce debt, or invest in growth. This is [strong/adequate/weak] because [reason]. Over the past years, FCF has [trend], indicating [analysis]"

**For Financial Users:**
- Clearly define FCF calculation methodology (Operating Cash Flow - CapEx)
- Present FCF in absolute dollars and as a percentage of revenue
- Highlight FCF conversion efficiency (FCF/Net Income ratio)
- Note any years with negative FCF and reasons
- Discuss FCF quality (sustainable vs. one-time items, working capital impacts)
- Analyze FCF yield (FCF/Market Cap)
- Format: "FCF: $X million (Y% of revenue), FCF conversion: Z%, FCF yield: A%. Trend: [analysis]. Quality: [sustainable/one-time factors]. FCF bridge: [key drivers]"

---

### P5: What is the company's quarterly revenue and earnings performance?

**Forms Required:**
- **Form 10-Q** (most recent 4-8 quarters)
- **Form 10-K** (for annual context)

**Sections to Analyze:**
- **Form 10-Q, Part I, Item 1: Financial Statements** - Income Statement
  - Quarterly revenue, net income, EPS
- **Form 10-Q, Part I, Item 2: Management's Discussion and Analysis** - Quarterly MD&A
- **Form 8-K, Item 2.02** - Earnings releases (if filed)

**How to Interpret:**
1. Extract quarterly revenue, net income, and EPS
2. Calculate QoQ (quarter-over-quarter) growth
3. Calculate YoY (year-over-year) growth for same quarters
4. Identify seasonal patterns
5. Compare to analyst expectations (if mentioned in 8-K)
6. Review MD&A for quarterly performance drivers

**AI Agent Guidance:**

**For Non-Financial Users:**
- Start with simple explanation: "Quarterly reports show how the company performed in each 3-month period"
- Define terms:
  - "QoQ (Quarter-over-Quarter): Compares this quarter to the previous quarter"
  - "YoY (Year-over-Year): Compares this quarter to the same quarter last year (better for seasonal businesses)"
- Provide context: "Companies report earnings every 3 months, so we can see if performance is improving or declining"
- Explain seasonality: "Some businesses are seasonal - retailers do better in Q4 (holidays), while others are steady year-round"
- Use simple language: "If Q1 revenue was $100M and Q2 is $110M, that's 10% growth quarter-over-quarter"
- Format: "Quarterly Performance: The company reports results every 3 months. In Q1 [year], revenue was $X million, which is [Y% higher/lower] than the same quarter last year and [Z% higher/lower] than the previous quarter. Q2 results were [analysis]. The company shows [seasonal patterns/steady growth/declining trends]. This performance is [meeting/exceeding/falling short of] expectations because [reason]"

**For Financial Users:**
- Present data in a quarterly table format
- Highlight QoQ and YoY growth rates
- Identify seasonality patterns and adjust for seasonality if needed
- Compare actual results to guidance and consensus estimates (if provided)
- Note any one-time items affecting quarterly results
- Analyze sequential trends and momentum
- Format: "Q1: $X revenue (YoY: Y%, QoQ: Z%, vs. guidance: [beat/miss]), Q2: [etc.]. Seasonality: [analysis]. Underlying trends: [analysis]"

---

## Trend Analysis Prompts

### T1: What are the long-term trends in the company's revenue growth?

**Forms Required:**
- **Form 10-K** (5-10 years)

**Sections to Analyze:**
- **Form 10-K, Item 6: Selected Financial Data** - 5-year revenue summary
- **Form 10-K, Item 8: Financial Statements** - Historical income statements
- **Form 10-K, Item 7: MD&A** - Revenue trend discussion

**How to Interpret:**
1. Plot revenue over time
2. Calculate growth rates for each period
3. Identify acceleration, deceleration, or stabilization phases
4. Analyze MD&A for explanations of trend changes
5. Look for inflection points (when trends changed direction)
6. Consider segment-level trends if company reports segments

**AI Agent Guidance:**
- Create a visual narrative of revenue trajectory
- Identify distinct phases (high growth, moderate growth, decline, recovery)
- Explain drivers of trend changes
- Compare to industry growth rates if available
- Format: "Revenue trend analysis: [Phase 1 description], [Phase 2], etc. Key inflection points: [dates and reasons]"

---

### T2: How has the company's debt-to-equity ratio changed over time?

**Forms Required:**
- **Form 10-K** (multiple years)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Balance Sheet
  - Total debt (short-term + long-term)
  - Total shareholders' equity
- **Form 10-K, Item 7: MD&A** - Capital structure discussion
- **Form 10-K, Item 6: Selected Financial Data** - Historical debt/equity data

**How to Interpret:**
1. Calculate Debt-to-Equity = Total Debt / Total Shareholders' Equity
2. Track ratio over multiple years
3. Identify increases/decreases and timing
4. Review MD&A for capital structure strategy
5. Check for debt issuances or repayments (from cash flow statement)
6. Consider net debt (debt minus cash) for more accurate picture

**AI Agent Guidance:**
- Present ratio trends with context (industry norms)
- Explain what changes indicate (leverage increase/decrease)
- Note any significant debt events (issuances, repayments, refinancings)
- Discuss implications for financial flexibility
- Format: "Debt-to-equity ratio: X in Year 1 → Y in Year 5. Trend: [analysis]. Key events: [debt activities]"

---

### T3: What are the trends in the company's operating expenses as a percentage of revenue?

**Forms Required:**
- **Form 10-K** (multiple years)
- **Form 10-Q** (for quarterly trends)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Income Statement
  - Operating expenses breakdown (SG&A, R&D, etc.)
- **Form 10-K, Item 7: MD&A** - Expense trend discussion
- **Form 10-Q, Part I, Item 1** - Quarterly expense data

**How to Interpret:**
1. Calculate expense ratios: (Expense Category / Revenue) × 100
2. Track SG&A ratio, R&D ratio, etc. over time
3. Identify which expense categories are growing faster/slower than revenue
4. Look for operating leverage (expenses growing slower than revenue = positive leverage)
5. Review MD&A for expense management initiatives

**AI Agent Guidance:**
- Break down by expense category (SG&A, R&D, COGS)
- Identify operating leverage trends
- Explain drivers of expense changes
- Highlight efficiency improvements or cost pressures
- Format: "SG&A ratio: X% (trend), R&D ratio: Y% (trend). Operating leverage: [positive/negative/neutral]"

---

### T4: How has the company's market share changed over time?

**Forms Required:**
- **Form 10-K** (multiple years)

**Sections to Analyze:**
- **Form 10-K, Item 1: Business** - Market position discussion
- **Form 10-K, Item 7: MD&A** - Market share references
- **Form 10-K, Item 8: Financial Statements** - Revenue by segment/geography

**How to Interpret:**
1. Extract market share references from Business and MD&A sections
2. Analyze revenue growth vs. industry growth (if available)
3. Review segment performance for market share indicators
4. Look for competitive positioning discussions
5. Consider geographic market share if company operates globally

**AI Agent Guidance:**
- Note that explicit market share data may not always be available
- Infer trends from revenue growth vs. industry growth
- Reference management's market position statements
- Highlight any market share gains/losses mentioned
- Format: "Market share analysis: [explicit data if available] or [inferred from growth rates]. Management commentary: [quotes]"

---

### T5: What are the trends in the company's capital expenditures?

**Forms Required:**
- **Form 10-K** (multiple years)
- **Form 10-Q** (for quarterly trends)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Statement of Cash Flows
  - Capital expenditures (investing activities)
- **Form 10-K, Item 7: MD&A** - Capital allocation discussion
- **Form 10-K, Item 1: Business** - Capital requirements discussion

**How to Interpret:**
1. Extract CapEx amounts from cash flow statements
2. Calculate CapEx as % of revenue
3. Calculate CapEx as % of depreciation (maintenance vs. growth CapEx)
4. Track trends over time
5. Review MD&A for CapEx strategy and future plans
6. Identify maintenance vs. growth CapEx (if disclosed)

**AI Agent Guidance:**
- Present CapEx trends in absolute dollars and as % of revenue
- Distinguish between maintenance and growth CapEx if possible
- Explain CapEx strategy (expansion, efficiency, maintenance)
- Note any major CapEx projects mentioned
- Format: "CapEx: $X million (Y% of revenue). Trend: [analysis]. Strategy: [maintenance vs. growth]"

---

## Comparative Analysis Prompts

### C1: How does the company's profit margins compare to its industry peers?

**Forms Required:**
- **Form 10-K** (target company)
- **Form 10-K** (peer companies - multiple)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Income Statement (all companies)
  - Calculate gross, operating, and net margins for each
- **Form 10-K, Item 7: MD&A** - Margin discussion and competitive positioning

**How to Interpret:**
1. Calculate margins for target company
2. Calculate margins for peer companies
3. Rank companies by each margin metric
4. Calculate average and median peer margins
5. Identify where target company ranks (above/below average)
6. Analyze reasons for differences (business model, scale, efficiency)

**AI Agent Guidance:**

**For Non-Financial Users:**
- Start with simple explanation: "Comparing profit margins shows if the company is more or less profitable than similar companies"
- Explain what comparison means: "If the company's margin is higher than peers, it's more profitable. If lower, it's less profitable"
- Use simple language: "The company keeps X cents per dollar of sales, while competitors keep Y cents on average"
- Provide context: "Being above average is good - it means the company is more efficient or can charge higher prices"
- Format: "Compared to similar companies, Company X's profit margins are [higher/lower/about the same]. Company X keeps [X%] of each sales dollar as profit, while competitors average [Y%]. This means Company X is [more/less] profitable than its peers because [reason in plain language - e.g., 'better at controlling costs' or 'can charge premium prices']"

**For Financial Users:**
- Create comparison table with all companies
- Highlight target company's position (percentile ranking, standard deviations from mean)
- Explain margin differences (business model, scale, efficiency, pricing power, product mix)
- Note any outliers and reasons
- Analyze margin sustainability and quality
- Format: "Target company margins vs. peers: Gross [X% vs. Y% avg, Zth percentile], Operating [A% vs. B% avg], Net [C% vs. D% avg]. Ranking: [position]. Margin drivers: [analysis]. Sustainability: [assessment]"

---

### C2: How does the company's revenue growth compare to competitors?

**Forms Required:**
- **Form 10-K** (target and peers - multiple years)

**Sections to Analyze:**
- **Form 10-K, Item 6: Selected Financial Data** - Revenue history
- **Form 10-K, Item 8: Financial Statements** - Income statements
- **Form 10-K, Item 7: MD&A** - Growth strategy discussion

**How to Interpret:**
1. Calculate revenue growth rates (YoY, CAGR) for all companies
2. Compare growth rates across companies
3. Identify fastest and slowest growers
4. Analyze growth consistency (volatility)
5. Consider company size (larger companies typically grow slower)
6. Review MD&A for growth strategies

**AI Agent Guidance:**
- Present growth rates in comparison table
- Adjust for company size if relevant
- Highlight growth consistency vs. volatility
- Explain growth differentials (market share gains, new products, M&A)
- Format: "Revenue growth comparison: Target [X% CAGR], Peer 1 [Y%], Peer 2 [Z%]. Target ranks [position]. Key differentiators: [factors]"

---

### C3: How does the company's debt levels compare to industry standards?

**Forms Required:**
- **Form 10-K** (target and peers)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Balance Sheet
  - Total debt, cash, net debt
  - Total shareholders' equity
- **Form 10-K, Item 7: MD&A** - Capital structure discussion

**How to Interpret:**
1. Calculate debt-to-equity, debt-to-assets, net debt-to-EBITDA for all companies
2. Compare ratios across peer group
3. Identify leverage outliers
4. Consider industry norms (some industries naturally more leveraged)
5. Analyze interest coverage ratios
6. Review capital structure strategies in MD&A

**AI Agent Guidance:**
- Present multiple leverage metrics (debt/equity, debt/assets, net debt/EBITDA)
- Rank companies by leverage
- Explain leverage differences (capital structure strategy, cash generation, growth stage)
- Note industry-specific leverage norms
- Format: "Leverage comparison: Target [X debt/equity], Peers [Y avg]. Target is [more/less] leveraged. Implications: [analysis]"

---

### C4: How does executive compensation compare to peer companies?

**Forms Required:**
- **Form DEF 14A** (target and peers)

**Sections to Analyze:**
- **Form DEF 14A, Executive Compensation Tables**
  - Summary Compensation Table
  - Grants of Plan-Based Awards Table
  - Outstanding Equity Awards Table
- **Form DEF 14A, Compensation Discussion and Analysis (CD&A)**
  - Peer group definition
  - Compensation philosophy

**How to Interpret:**
1. Extract total compensation for CEO and other NEOs (Named Executive Officers)
2. Compare to peer company executives
3. Analyze compensation mix (salary, bonus, equity)
4. Review pay-for-performance alignment
5. Check if peer group is appropriate
6. Compare compensation ratios (CEO to median employee)

**AI Agent Guidance:**
- Present compensation comparison table
- Analyze compensation mix differences
- Evaluate pay-for-performance alignment
- Note any compensation controversies or shareholder concerns
- Format: "CEO compensation: Target [$X], Peers [avg $Y]. Mix: [salary/bonus/equity breakdown]. Pay-for-performance: [alignment assessment]"

---

### C5: How does the company's return on invested capital (ROIC) compare to peers?

**Forms Required:**
- **Form 10-K** (target and peers)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements**
  - Income Statement: Operating income (EBIT)
  - Balance Sheet: Total assets, Total debt, Total equity
- **Form 10-K, Item 7: MD&A** - May discuss ROIC

**How to Interpret:**
1. Calculate ROIC = (EBIT × (1 - Tax Rate)) / (Total Debt + Total Equity)
2. Calculate for all companies in peer group
3. Compare ROIC levels
4. Identify companies with superior capital efficiency
5. Analyze drivers of ROIC differences (profitability, capital efficiency)

**AI Agent Guidance:**
- Present ROIC comparison with methodology
- Rank companies by ROIC
- Explain ROIC differences (operating margins, asset turnover, capital structure)
- Note if target company creates/destroys value (ROIC vs. WACC)
- Format: "ROIC comparison: Target [X%], Peers [Y% avg]. Target ranks [position]. Value creation: [ROIC vs. WACC analysis]"

---

## Risk Analysis Prompts

### R1: What are the primary business risks facing the company?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for updated risks)

**Sections to Analyze:**
- **Form 10-K, Item 1A: Risk Factors** - Comprehensive risk disclosure
- **Form 10-K, Item 7: MD&A** - Risk discussion in context of operations
- **Form 10-Q, Part II, Item 1A** - Updated risk factors

**How to Interpret:**
1. List all risk factors from Item 1A
2. Categorize risks (operational, financial, regulatory, competitive, etc.)
3. Identify most material risks (often listed first or discussed at length)
4. Look for new risks added in recent filings
5. Review MD&A for how risks are being managed
6. Note any risk mitigation strategies mentioned

**AI Agent Guidance:**

**For Non-Financial Users:**
- Start with simple explanation: "Risk factors are things that could hurt the company's business or financial performance"
- Categorize risks in plain language:
  - "Operational risks: Things that could disrupt day-to-day business"
  - "Financial risks: Money-related problems like too much debt or cash shortages"
  - "Regulatory risks: Government rules that could hurt the business"
  - "Competitive risks: Competitors taking market share"
- Explain impact: "Each risk could affect the company's ability to make money or grow"
- Prioritize by explaining which risks are most serious
- Format: "The company faces several risks that could hurt its business. The most serious risks are: 1) [Risk in plain language] - This could [impact]. 2) [Risk] - This might [impact]. The company is trying to reduce these risks by [mitigation strategies in plain language]"

**For Financial Users:**
- Categorize risks by type (operational, financial, regulatory, strategic, etc.)
- Prioritize risks by materiality (order in filing, length of discussion, cross-reference with MD&A)
- Highlight new or emerging risks (compare to prior year filings)
- Note risk mitigation strategies and their effectiveness
- Assess risk correlation and concentration
- Format: "Primary risks: [Category 1: risks], [Category 2: risks]. Most material: [top 3-5]. Mitigation: [strategies]. Risk assessment: [analysis]"

---

### R2: What are the company's financial risks and liquidity concerns?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for current liquidity)

**Sections to Analyze:**
- **Form 10-K, Item 1A: Risk Factors** - Financial risk factors
- **Form 10-K, Item 7: MD&A** - Liquidity and Capital Resources section
- **Form 10-K, Item 8: Financial Statements**
  - Balance Sheet: Cash, debt maturities, working capital
  - Cash Flow Statement: Operating cash flow, financing activities
- **Form 8-K, Item 2.03** - Creation of financial obligations

**How to Interpret:**
1. Analyze liquidity ratios: Current ratio, Quick ratio, Cash to short-term debt
2. Review debt maturity schedule (from notes to financial statements)
3. Assess operating cash flow generation
4. Evaluate debt covenants and restrictions
5. Check for going concern warnings
6. Review credit facility availability

**AI Agent Guidance:**

**For Non-Financial Users:**
- Start with simple explanation: "Liquidity means having enough cash and assets that can be quickly turned into cash to pay bills and debts"
- Explain ratios in plain language:
  - "Current ratio: Can the company pay its short-term bills? A ratio above 1.0 means yes, below 1.0 means potential trouble"
  - "Cash position: How much cash does the company have in the bank?"
- Explain debt maturities: "The company has debts that need to be paid back. We check if it has enough cash to pay them when due"
- Use simple language: "If the company has $100M in cash and $50M in debts due soon, it can easily pay. If it has $20M cash and $50M due, that's a problem"
- Format: "Financial health check: Company X has [X] times more current assets than current liabilities, which means it [can/cannot easily] pay its short-term bills. The company has $Y million in cash, and debts of $Z million coming due in the next [timeframe]. This means the company [has enough/needs to raise] cash to pay its debts. The company's ability to generate cash is [strong/adequate/weak] because [reason]"

**For Financial Users:**
- Calculate and present liquidity ratios (Current, Quick, Cash ratios)
- Analyze debt maturity profile and refinancing needs
- Assess cash generation ability (FCF, operating cash flow trends)
- Identify any liquidity constraints or concerns
- Note debt covenant compliance and headroom
- Analyze credit facility availability and usage
- Format: "Liquidity: Current ratio [X], Quick ratio [Y], Cash [Z], Debt maturities [schedule]. Cash generation: [analysis]. Covenant compliance: [status]. Liquidity runway: [assessment]. Concerns: [any red flags]"

---

### R3: What regulatory or legal risks does the company face?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for updates)
- **Form 8-K** (for material legal events)

**Sections to Analyze:**
- **Form 10-K, Item 1A: Risk Factors** - Regulatory and legal risks
- **Form 10-K, Item 3: Legal Proceedings** - Pending litigation
- **Form 10-Q, Part II, Item 1: Legal Proceedings** - Updated litigation
- **Form 8-K, Item 1.02** - Termination of material agreements (may relate to legal issues)

**How to Interpret:**
1. List all pending legal proceedings from Item 3
2. Assess potential financial impact (if disclosed)
3. Identify regulatory risks (industry-specific regulations, compliance)
4. Review any regulatory investigations or enforcement actions
5. Note any material settlements or judgments
6. Assess likelihood and potential impact

**AI Agent Guidance:**
- List all material legal proceedings
- Assess potential financial impact (if quantifiable)
- Categorize by type (product liability, regulatory, employment, etc.)
- Note any regulatory investigations
- Highlight any significant settlements or judgments
- Format: "Legal risks: [list of proceedings]. Potential impact: [if disclosed]. Regulatory risks: [list]. Status: [ongoing/resolved]"

---

### R4: What are the competitive risks and market position threats?

**Forms Required:**
- **Form 10-K** (most recent)

**Sections to Analyze:**
- **Form 10-K, Item 1: Business** - Competitive environment discussion
- **Form 10-K, Item 1A: Risk Factors** - Competitive risks
- **Form 10-K, Item 7: MD&A** - Competitive positioning discussion

**How to Interpret:**
1. Extract competitive landscape description
2. Identify main competitors mentioned
3. List competitive risk factors
4. Assess market position (leader, follower, niche)
5. Review competitive advantages and disadvantages
6. Note any market share losses mentioned

**AI Agent Guidance:**
- Describe competitive landscape
- List main competitors
- Assess competitive position (market share, competitive advantages)
- Identify competitive threats
- Note any competitive disadvantages
- Format: "Competitive landscape: [description]. Main competitors: [list]. Market position: [assessment]. Threats: [list]. Advantages: [list]"

---

### R5: What are the company's operational risks?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for operational updates)
- **Form 8-K** (for material operational events)

**Sections to Analyze:**
- **Form 10-K, Item 1A: Risk Factors** - Operational risks
- **Form 10-K, Item 1: Business** - Operations description
- **Form 10-K, Item 7: MD&A** - Operational discussion
- **Form 8-K, Item 2.05** - Exit or disposal activities
- **Form 8-K, Item 2.06** - Material impairments

**How to Interpret:**
1. List operational risk factors
2. Identify key operational dependencies (suppliers, customers, facilities)
3. Assess operational complexity
4. Review any operational disruptions mentioned
5. Note supply chain risks
6. Assess technology and cybersecurity risks

**AI Agent Guidance:**
- Categorize operational risks (supply chain, technology, facilities, people)
- Identify critical dependencies
- Assess operational resilience
- Note any recent operational issues
- Format: "Operational risks: [categories and risks]. Key dependencies: [list]. Resilience: [assessment]. Recent issues: [if any]"

---

## Valuation & Financial Health Prompts

### V1: What is the company's enterprise value and valuation multiples?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for most recent financials)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements**
  - Income Statement: Revenue, EBITDA, Net Income
  - Balance Sheet: Total debt, Cash
- Market data (stock price, shares outstanding) - may be in Form 10-K, Item 5

**How to Interpret:**
1. Calculate Market Cap = Stock Price × Shares Outstanding
2. Calculate Enterprise Value = Market Cap + Total Debt - Cash
3. Calculate valuation multiples:
   - EV/Revenue
   - EV/EBITDA
   - P/E (Price/Earnings)
   - P/B (Price/Book)
4. Compare to historical multiples and peer multiples

**AI Agent Guidance:**
- Calculate EV using most recent financials
- Present key valuation multiples
- Compare to historical and peer multiples
- Note if company is trading at premium/discount
- Format: "Valuation: Market Cap [$X], EV [$Y]. Multiples: EV/Revenue [A], EV/EBITDA [B], P/E [C]. vs. Peers: [comparison]"

---

### V2: What is the company's financial health score?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for current position)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements**
  - All three statements (Income, Balance Sheet, Cash Flow)
- **Form 10-K, Item 7: MD&A** - Financial condition discussion

**How to Interpret:**
1. Calculate key financial health metrics:
   - Profitability: Margins, ROE, ROA
   - Liquidity: Current ratio, Quick ratio, Cash position
   - Solvency: Debt-to-equity, Interest coverage
   - Efficiency: Asset turnover, Inventory turnover
   - Cash generation: FCF, FCF margin
2. Score each category (1-5 scale)
3. Weight and combine for overall score
4. Identify strengths and weaknesses

**AI Agent Guidance:**
- Create comprehensive financial health assessment
- Score multiple dimensions (profitability, liquidity, solvency, efficiency, cash generation)
- Provide overall score with rationale
- Highlight strengths and weaknesses
- Format: "Financial Health Score: X/5. Breakdown: Profitability [score], Liquidity [score], etc. Strengths: [list]. Weaknesses: [list]"

---

### V3: Can the company service its debt obligations?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for current position)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements**
  - Income Statement: Operating income, Interest expense
  - Balance Sheet: Total debt, Current portion of debt
  - Cash Flow Statement: Operating cash flow
- **Form 10-K, Item 7: MD&A** - Liquidity and Capital Resources
- Notes to Financial Statements: Debt maturities, covenants

**How to Interpret:**
1. Calculate Interest Coverage Ratio = Operating Income / Interest Expense
2. Calculate Debt Service Coverage = Operating Cash Flow / (Interest + Principal Payments)
3. Review debt maturity schedule
4. Assess cash generation vs. debt service requirements
5. Check debt covenant compliance
6. Evaluate refinancing risk

**AI Agent Guidance:**
- Calculate interest coverage and debt service coverage ratios
- Analyze debt maturity profile
- Assess ability to meet debt obligations
- Identify any refinancing needs
- Note covenant compliance status
- Format: "Debt serviceability: Interest coverage [X], Debt service coverage [Y]. Maturities: [schedule]. Ability to service: [assessment]"

---

### V4: What is the company's dividend-paying capacity?

**Forms Required:**
- **Form 10-K** (multiple years)
- **Form 10-Q** (for recent dividend activity)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements**
  - Cash Flow Statement: Operating cash flow, Capital expenditures
  - Statement of Shareholders' Equity: Dividends paid
- **Form 10-K, Item 5: Market Information** - Dividend history
- **Form 10-K, Item 7: MD&A** - Capital allocation discussion

**How to Interpret:**
1. Calculate Free Cash Flow = Operating Cash Flow - CapEx
2. Calculate Dividend Coverage = FCF / Dividends Paid
3. Calculate Payout Ratio = Dividends / Net Income
4. Track dividend history and growth
5. Assess sustainability of current dividend level
6. Review capital allocation priorities

**AI Agent Guidance:**
- Calculate FCF and dividend coverage
- Assess dividend sustainability
- Analyze payout ratio trends
- Note dividend growth history
- Discuss capital allocation priorities
- Format: "Dividend capacity: FCF [$X], Dividends [$Y], Coverage [Zx]. Payout ratio: [A%]. Sustainability: [assessment]"

---

### V5: What is the company's working capital position and efficiency?

**Forms Required:**
- **Form 10-K** (multiple years)
- **Form 10-Q** (for quarterly trends)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Balance Sheet
  - Current assets, Current liabilities
  - Accounts receivable, Inventory, Accounts payable
- **Form 10-K, Item 7: MD&A** - Working capital discussion

**How to Interpret:**
1. Calculate Working Capital = Current Assets - Current Liabilities
2. Calculate Current Ratio = Current Assets / Current Liabilities
3. Calculate Days Sales Outstanding (DSO) = (AR / Revenue) × 365
4. Calculate Days Inventory Outstanding (DIO) = (Inventory / COGS) × 365
5. Calculate Days Payable Outstanding (DPO) = (AP / COGS) × 365
6. Calculate Cash Conversion Cycle = DSO + DIO - DPO
7. Track trends over time

**AI Agent Guidance:**
- Present working capital metrics
- Analyze cash conversion cycle
- Identify efficiency trends
- Compare to industry norms
- Format: "Working capital: $X, Current ratio: Y. Cash conversion cycle: Z days (DSO: A, DIO: B, DPO: C). Efficiency: [trend]"

---

## Strategic & Operational Prompts

### S1: What is the company's business model and strategy?

**Forms Required:**
- **Form 10-K** (most recent)

**Sections to Analyze:**
- **Form 10-K, Item 1: Business** - Comprehensive business description
- **Form 10-K, Item 7: MD&A** - Strategic discussion
- **Form 10-K, Item 1A: Risk Factors** - Strategic risks

**How to Interpret:**
1. Extract business model description from Item 1
2. Identify revenue streams and business segments
3. Understand value proposition and competitive advantages
4. Review strategic initiatives and priorities
5. Assess strategic positioning
6. Note any strategic pivots or changes

**AI Agent Guidance:**

**For Non-Financial Users:**
- Start with simple explanation: "The business model explains how the company makes money"
- Use plain language: "What does the company sell? Who buys it? How does it make a profit?"
- Explain value proposition simply: "Why do customers choose this company over competitors?"
- Break down revenue streams: "The company makes money from: 1) [source], 2) [source]"
- Format: "Business Model: Company X makes money by [simple description - e.g., 'selling software to businesses' or 'operating retail stores']. The company's main products/services are [list]. Customers buy from Company X because [value proposition in plain language - e.g., 'lower prices' or 'better quality']. The company makes money from [revenue streams]. Its strategy is to [priorities in simple terms]"

**For Financial Users:**
- Summarize business model clearly with industry context
- Identify key revenue streams with percentages and growth rates
- Explain value proposition and competitive moats
- List strategic priorities with resource allocation
- Assess strategic positioning (market share, competitive advantages)
- Analyze business model sustainability and scalability
- Format: "Business model: [description]. Revenue streams: [list with % and growth]. Strategy: [priorities]. Value proposition: [explanation]. Competitive positioning: [analysis]. Model sustainability: [assessment]"

---

### S2: What are the company's main business segments and their performance?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for quarterly segment data)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Segment Reporting (Notes to Financial Statements)
  - Revenue by segment
  - Operating income by segment
  - Assets by segment
- **Form 10-K, Item 1: Business** - Segment descriptions
- **Form 10-K, Item 7: MD&A** - Segment performance discussion

**How to Interpret:**
1. Extract segment revenue, operating income, and assets
2. Calculate segment margins
3. Calculate segment revenue growth rates
4. Identify fastest/slowest growing segments
5. Assess segment profitability differences
6. Review segment strategies

**AI Agent Guidance:**
- Present segment performance table
- Analyze segment growth and profitability
- Identify key segments
- Note segment trends
- Format: "Segments: [Segment 1: Revenue $X, Margin Y%, Growth Z%], [Segment 2: etc.]. Key segments: [analysis]"

---

### S3: What is the company's geographic revenue breakdown?

**Forms Required:**
- **Form 10-K** (most recent)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Geographic Revenue (Notes to Financial Statements)
- **Form 10-K, Item 1: Business** - Geographic operations description
- **Form 10-K, Item 1A: Risk Factors** - Geographic risks

**How to Interpret:**
1. Extract revenue by geographic region
2. Calculate percentage of total revenue by region
3. Identify largest markets
4. Assess geographic concentration risk
5. Review geographic growth trends
6. Note any geographic expansion or contraction

**AI Agent Guidance:**
- Present geographic revenue breakdown
- Identify key markets
- Assess concentration risk
- Note geographic trends
- Format: "Geographic revenue: [Region 1: $X, Y% of total], [Region 2: etc.]. Key markets: [list]. Concentration: [risk assessment]"

---

### S4: What are the company's key customers and customer concentration?

**Forms Required:**
- **Form 10-K** (most recent)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Customer Concentration (Notes to Financial Statements)
- **Form 10-K, Item 1A: Risk Factors** - Customer concentration risks

**How to Interpret:**
1. Extract customer concentration data (if disclosed)
2. Identify largest customers and % of revenue
3. Assess customer concentration risk
4. Review customer relationships and contracts
5. Note any customer losses or gains

**AI Agent Guidance:**
- Present customer concentration data
- Assess concentration risk
- Note key customer relationships
- Format: "Customer concentration: [Top customer: X% of revenue], [Top 3: Y%]. Risk: [assessment]. Key customers: [if disclosed]"

---

### S5: What are the company's research and development investments?

**Forms Required:**
- **Form 10-K** (multiple years)
- **Form 10-Q** (for quarterly R&D)

**Sections to Analyze:**
- **Form 10-K, Item 8: Financial Statements** - Income Statement
  - R&D expense line item
- **Form 10-K, Item 7: MD&A** - R&D discussion
- **Form 10-K, Item 1: Business** - R&D activities description

**How to Interpret:**
1. Extract R&D expense amounts
2. Calculate R&D as % of revenue
3. Track R&D trends over time
4. Compare to industry peers
5. Review R&D focus areas and projects
6. Assess innovation pipeline

**AI Agent Guidance:**
- Present R&D spending trends
- Calculate R&D intensity (R&D/Revenue)
- Compare to peers
- Note R&D focus areas
- Format: "R&D: $X million (Y% of revenue). Trend: [analysis]. vs. Peers: [comparison]. Focus areas: [list]"

---

## Governance & Management Prompts

### G1: Who are the company's key executives and what are their backgrounds?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form DEF 14A** (for detailed biographies)

**Sections to Analyze:**
- **Form 10-K, Item 10: Directors, Executive Officers and Corporate Governance**
  - Executive officers list
- **Form DEF 14A, Director and Executive Information**
  - Detailed biographies
  - Experience and qualifications

**How to Interpret:**
1. List all executive officers
2. Extract key biographical information
3. Assess experience and qualifications
4. Review tenure with company
5. Note any recent changes in leadership

**AI Agent Guidance:**
- List key executives with roles
- Summarize backgrounds and experience
- Assess leadership quality
- Note any leadership changes
- Format: "Key executives: [Name: Role, Background summary]. Leadership quality: [assessment]"

---

### G2: What is the composition and quality of the board of directors?

**Forms Required:**
- **Form DEF 14A** (most recent)

**Sections to Analyze:**
- **Form DEF 14A, Director Information**
  - Director names and biographies
  - Director independence
  - Board committees
- **Form DEF 14A, Corporate Governance**
  - Board structure and practices

**How to Interpret:**
1. List all directors
2. Assess independence (independent vs. non-independent)
3. Review committee memberships
4. Evaluate director qualifications and diversity
5. Assess board size and structure
6. Review board meeting attendance

**AI Agent Guidance:**
- Present board composition
- Assess independence and diversity
- Evaluate director qualifications
- Note committee structure
- Format: "Board: [X] directors, [Y] independent. Committees: [list]. Quality: [assessment]. Diversity: [if disclosed]"

---

### G3: How is executive compensation structured and aligned with performance?

**Forms Required:**
- **Form DEF 14A** (most recent)

**Sections to Analyze:**
- **Form DEF 14A, Executive Compensation Tables**
  - Summary Compensation Table
  - Grants of Plan-Based Awards
  - Outstanding Equity Awards
  - Option Exercises and Stock Vested
- **Form DEF 14A, Compensation Discussion and Analysis (CD&A)**
  - Compensation philosophy
  - Performance metrics
  - Pay-for-performance alignment

**How to Interpret:**
1. Extract total compensation for each NEO
2. Analyze compensation mix (salary, bonus, equity)
3. Review performance metrics used for incentive compensation
4. Assess pay-for-performance alignment
5. Compare to peer companies
6. Review say-on-pay voting results

**AI Agent Guidance:**

**For Non-Financial Users:**
- Start with simple explanation: "Executive compensation is how much the company pays its top leaders"
- Break down compensation simply:
  - "Salary: Fixed amount paid each year"
  - "Bonus: Extra pay based on performance"
  - "Stock/Equity: Company shares that can become valuable if the company does well"
- Explain pay-for-performance: "Good companies tie pay to performance - if the company does well, executives get more. If it does poorly, they get less"
- Use simple comparisons: "The CEO makes $X million per year, which is [higher/lower/about the same] as CEOs at similar companies"
- Format: "Executive Pay: The CEO of Company X receives total compensation of $X million per year. This includes: $Y million in salary (guaranteed), $Z million in bonus (based on performance), and $A million in company stock (value depends on stock price). This pay is [higher/lower/similar] compared to CEOs at similar companies. The pay is [well/poorly] aligned with company performance because [reason in plain language]"

**For Financial Users:**
- Present compensation structure with detailed breakdown
- Analyze pay mix (fixed vs. variable, cash vs. equity)
- Assess pay-for-performance alignment using performance metrics
- Compare to peers (percentile ranking, peer group analysis)
- Evaluate compensation philosophy and structure
- Review say-on-pay results and shareholder feedback
- Format: "Compensation: CEO total [$X, Yth percentile], Mix: [salary Y%, bonus Z%, equity A%]. Performance metrics: [list]. Pay-for-performance: [alignment score/assessment]. vs. Peers: [comparison]. Shareholder feedback: [say-on-pay results]"

---

### G4: What are the company's corporate governance practices?

**Forms Required:**
- **Form DEF 14A** (most recent)
- **Form 10-K** (for governance policies)

**Sections to Analyze:**
- **Form DEF 14A, Corporate Governance**
  - Board structure
  - Committee charters
  - Governance policies
- **Form 10-K, Item 10: Corporate Governance**
  - Code of ethics
  - Governance policies

**How to Interpret:**
1. Review board structure and independence
2. Assess committee structure and charters
3. Evaluate governance policies (code of ethics, etc.)
4. Review shareholder rights
5. Assess governance best practices compliance
6. Note any governance concerns or controversies

**AI Agent Guidance:**
- Summarize governance structure
- Assess governance quality
- Note best practices compliance
- Highlight any concerns
- Format: "Governance: Board [structure], Committees [list], Policies [summary]. Quality: [assessment]. Concerns: [if any]"

---

### G5: Have there been any recent changes in management or board?

**Forms Required:**
- **Form 8-K** (recent filings)
- **Form 10-K** (for current leadership)
- **Form DEF 14A** (for board composition)

**Sections to Analyze:**
- **Form 8-K, Item 5.02** - Departure of directors or principal officers
- **Form 8-K, Item 5.01** - Changes in control
- **Form 10-K, Item 10** - Current executive officers
- **Form DEF 14A** - Current board composition

**How to Interpret:**
1. Review recent 8-K filings for Item 5.02
2. Identify departures and new appointments
3. Assess reasons for changes (if disclosed)
4. Evaluate impact on company
5. Note any patterns (frequent turnover)

**AI Agent Guidance:**
- List recent management/board changes
- Assess reasons and impact
- Note any patterns or concerns
- Format: "Recent changes: [Date: Change description, Reason if disclosed]. Impact: [assessment]. Patterns: [if any]"

---

## Ownership & Insider Activity Prompts

### O1: Who are the company's largest shareholders?

**Forms Required:**
- **Form 10-K** (most recent)
- **Schedule 13D/13G** (for 5%+ holders)
- **Form DEF 14A** (for beneficial ownership table)

**Sections to Analyze:**
- **Form DEF 14A, Security Ownership** - Beneficial ownership table
- **Schedule 13D/13G** - 5%+ beneficial owners
- **Form 10-K, Item 12** - Security ownership information

**How to Interpret:**
1. Extract largest shareholders from ownership table
2. Identify ownership percentages
3. Distinguish between institutional and individual holders
4. Note any 5%+ holders filing 13D/13G
5. Assess ownership concentration
6. Review insider ownership

**AI Agent Guidance:**
- List largest shareholders with percentages
- Categorize by type (institutional, individual, insider)
- Assess ownership concentration
- Format: "Largest shareholders: [Holder 1: X%], [Holder 2: Y%]. Concentration: [assessment]. Insider ownership: [%]"

---

### O2: What is the pattern of insider buying and selling?

**Forms Required:**
- **Form 4** (multiple recent filings)
- **Form 5** (annual summary)

**Sections to Analyze:**
- **Form 4** - Individual insider transactions
  - Transaction date, type, price, shares
  - Ownership after transaction
- **Form 5** - Annual summary of delayed transactions

**How to Interpret:**
1. Extract all Form 4 transactions for recent period
2. Categorize by transaction type (buy, sell, grant, exercise)
3. Calculate net buying/selling by insider
4. Identify patterns (clusters of buying/selling)
5. Compare transaction prices to current stock price
6. Assess insider sentiment

**AI Agent Guidance:**
- Summarize insider transaction activity
- Identify buying vs. selling patterns
- Assess insider sentiment
- Note any significant transactions
- Format: "Insider activity: [Period]. Net buying/selling: [summary]. Key transactions: [notable ones]. Sentiment: [assessment]"

---

### O3: How has institutional ownership changed?

**Forms Required:**
- **Form 13F** (multiple quarters)
- **Schedule 13G** (for passive 5%+ holders)

**Sections to Analyze:**
- **Form 13F** - Quarterly institutional holdings
  - Holdings by institution
  - Total shares held
- **Schedule 13G** - Passive institutional holders

**How to Interpret:**
1. Extract institutional holdings from multiple 13F filings
2. Calculate total institutional ownership
3. Track changes quarter-over-quarter
4. Identify institutions increasing/decreasing positions
5. Assess ownership trends
6. Compare to peer companies

**AI Agent Guidance:**
- Present institutional ownership trends
- Identify key institutional holders
- Note changes in ownership
- Format: "Institutional ownership: [X%], Trend: [increasing/decreasing]. Key holders: [list]. Changes: [summary]"

---

### O4: Are there any activist investors or potential takeover threats?

**Forms Required:**
- **Schedule 13D** (for active investors)
- **Form 8-K** (for control changes)
- **Form DEF 14A** (for proxy fights)

**Sections to Analyze:**
- **Schedule 13D** - Active investor filings
  - Purpose of transaction
  - Plans or proposals
- **Form 8-K, Item 5.01** - Changes in control
- **Form DEF 14A** - Shareholder proposals, proxy contests

**How to Interpret:**
1. Review Schedule 13D filings for activist language
2. Identify investors with control intentions
3. Review any shareholder proposals
4. Check for proxy contest mentions
5. Assess takeover defenses
6. Evaluate activist campaign likelihood

**AI Agent Guidance:**
- Identify activist investors
- Assess their intentions
- Evaluate takeover risk
- Format: "Activist investors: [list if any]. Intentions: [if disclosed]. Takeover risk: [assessment]"

---

## M&A & Corporate Actions Prompts

### M1: What acquisitions has the company made recently?

**Forms Required:**
- **Form 8-K** (recent filings)
- **Form 10-K** (for acquisition summary)
- **Form S-4** (for material acquisitions)

**Sections to Analyze:**
- **Form 8-K, Item 2.01** - Completion of acquisition or disposition
- **Form 10-K, Item 7: MD&A** - Acquisition discussion
- **Form S-4** - Merger/acquisition registration (if material)
- **Form 10-K, Item 8: Financial Statements** - Pro forma financials for acquisitions

**How to Interpret:**
1. Review recent 8-K filings for Item 2.01
2. Extract acquisition details (target, purchase price, terms)
3. Assess strategic rationale
4. Review pro forma financial impact
5. Evaluate integration progress
6. Note any acquisition-related risks

**AI Agent Guidance:**
- List recent acquisitions with details
- Assess strategic rationale
- Evaluate financial impact
- Format: "Recent acquisitions: [Date: Target, Price $X, Rationale]. Impact: [financial/strategic]. Integration: [status if available]"

---

### M2: Has the company divested any businesses?

**Forms Required:**
- **Form 8-K** (recent filings)
- **Form 10-K** (for divestiture summary)

**Sections to Analyze:**
- **Form 8-K, Item 2.01** - Disposition of assets
- **Form 8-K, Item 2.05** - Exit or disposal activities
- **Form 10-K, Item 7: MD&A** - Divestiture discussion

**How to Interpret:**
1. Review 8-K filings for dispositions
2. Extract divestiture details
3. Assess reasons for divestiture
4. Review financial impact
5. Evaluate strategic implications

**AI Agent Guidance:**
- List recent divestitures
- Assess reasons and impact
- Format: "Recent divestitures: [Date: Business, Proceeds $X, Reason]. Impact: [financial/strategic]"

---

### M3: What is the company's M&A strategy?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 8-K** (for M&A activity)
- **Form S-4** (for material transactions)

**Sections to Analyze:**
- **Form 10-K, Item 1: Business** - Strategic discussion
- **Form 10-K, Item 7: MD&A** - M&A strategy discussion
- **Form 8-K, Item 2.01** - M&A transactions
- **Form S-4** - Merger details

**How to Interpret:**
1. Extract M&A strategy from Business and MD&A sections
2. Review historical M&A activity
3. Identify M&A focus areas (geography, product, technology)
4. Assess M&A track record
5. Review integration capabilities

**AI Agent Guidance:**
- Summarize M&A strategy
- Review historical activity
- Assess strategy execution
- Format: "M&A strategy: [description]. Focus areas: [list]. Track record: [assessment]"

---

### M4: Are there any pending mergers or acquisitions?

**Forms Required:**
- **Form 8-K** (recent filings)
- **Form S-4** (for pending mergers)
- **Form 10-Q** (for pending transaction updates)

**Sections to Analyze:**
- **Form 8-K, Item 1.01** - Entry into material definitive agreements (M&A)
- **Form S-4** - Merger registration statement
- **Form 10-Q, Part I, Item 2: MD&A** - Pending transaction updates

**How to Interpret:**
1. Review recent 8-K filings for M&A agreements
2. Extract transaction details
3. Assess regulatory approval status
4. Review expected closing timeline
5. Evaluate transaction terms and fairness

**AI Agent Guidance:**
- List pending transactions
- Assess status and timeline
- Evaluate terms
- Format: "Pending M&A: [Transaction details, Status, Expected close date]. Terms: [summary]"

---

## Forward-Looking & Guidance Prompts

### F1: What guidance has management provided for future performance?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for updated guidance)
- **Form 8-K, Item 2.02** (earnings releases with guidance)

**Sections to Analyze:**
- **Form 10-K, Item 7: MD&A** - Forward-looking statements
- **Form 10-Q, Part I, Item 2: MD&A** - Updated guidance
- **Form 8-K, Item 2.02** - Earnings releases (often include guidance)
- **Form 8-K, Item 7.01** - Regulation FD disclosure (guidance updates)

**How to Interpret:**
1. Extract quantitative guidance (revenue, earnings, etc.)
2. Identify guidance ranges
3. Track guidance changes over time
4. Assess guidance accuracy (compare to actuals)
5. Review qualitative forward-looking statements
6. Note any guidance withdrawals or changes

**AI Agent Guidance:**
- Present current guidance
- Track guidance history and changes
- Assess guidance credibility
- Format: "Guidance: Revenue [range], EPS [range]. Changes: [history]. Credibility: [assessment based on track record]"

---

### F2: What are management's strategic priorities for the coming year?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for updated priorities)

**Sections to Analyze:**
- **Form 10-K, Item 1: Business** - Strategic discussion
- **Form 10-K, Item 7: MD&A** - Strategic priorities and initiatives
- **Form 10-Q, Part I, Item 2: MD&A** - Updated strategic discussion

**How to Interpret:**
1. Extract strategic priorities from MD&A
2. Identify key initiatives
3. Assess progress on stated priorities
4. Review capital allocation priorities
5. Note any strategic shifts

**AI Agent Guidance:**
- List strategic priorities
- Assess progress
- Format: "Strategic priorities: [Priority 1: description, progress], [Priority 2: etc.]"

---

### F3: What are the company's capital allocation plans?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for capital allocation updates)

**Sections to Analyze:**
- **Form 10-K, Item 7: MD&A** - Liquidity and Capital Resources section
- **Form 10-K, Item 5: Market Information** - Share repurchase programs, dividends
- **Form 10-Q, Part I, Item 2: MD&A** - Capital allocation discussion

**How to Interpret:**
1. Extract capital allocation priorities (CapEx, M&A, dividends, buybacks, debt repayment)
2. Review historical capital allocation
3. Assess capital allocation strategy
4. Evaluate return on invested capital
5. Review share repurchase programs

**AI Agent Guidance:**
- Summarize capital allocation strategy
- Review historical allocation
- Assess strategy effectiveness
- Format: "Capital allocation: [Priorities: CapEx X%, M&A Y%, Dividends Z%, Buybacks A%]. Strategy: [description]"

---

### F4: What are the key risks to the company's future performance?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for updated risks)

**Sections to Analyze:**
- **Form 10-K, Item 1A: Risk Factors** - Comprehensive risk list
- **Form 10-K, Item 7: MD&A** - Risk discussion in context
- **Form 10-Q, Part II, Item 1A** - Updated risk factors

**How to Interpret:**
1. List all risk factors
2. Prioritize by materiality
3. Identify emerging risks
4. Assess risk mitigation strategies
5. Evaluate risk impact on future performance

**AI Agent Guidance:**
- List key risks
- Prioritize by materiality
- Assess impact on future performance
- Format: "Key risks: [Risk 1: description, impact], [Risk 2: etc.]. Mitigation: [strategies]"

---

## Sector & Industry Analysis Prompts

### I1: How does the company position itself in its industry?

**Forms Required:**
- **Form 10-K** (most recent)

**Sections to Analyze:**
- **Form 10-K, Item 1: Business** - Industry description and positioning
- **Form 10-K, Item 1A: Risk Factors** - Competitive risks
- **Form 10-K, Item 7: MD&A** - Competitive positioning discussion

**How to Interpret:**
1. Extract industry description
2. Identify competitive positioning
3. Assess market position (leader, follower, niche)
4. Review competitive advantages
5. Evaluate market share (if disclosed)

**AI Agent Guidance:**
- Describe industry position
- Assess competitive advantages
- Format: "Industry position: [description]. Market position: [leader/follower/niche]. Advantages: [list]"

---

### I2: What are the industry trends affecting the company?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for trend updates)

**Sections to Analyze:**
- **Form 10-K, Item 1: Business** - Industry trends discussion
- **Form 10-K, Item 7: MD&A** - Industry trend impact
- **Form 10-K, Item 1A: Risk Factors** - Industry-related risks

**How to Interpret:**
1. Extract industry trend discussions
2. Identify positive and negative trends
3. Assess company's exposure to trends
4. Evaluate company's ability to adapt
5. Review trend impact on financials

**AI Agent Guidance:**
- List industry trends
- Assess impact on company
- Format: "Industry trends: [Trend 1: description, Impact], [Trend 2: etc.]. Company exposure: [assessment]"

---

### I3: Who are the company's main competitors?

**Forms Required:**
- **Form 10-K** (most recent)

**Sections to Analyze:**
- **Form 10-K, Item 1: Business** - Competitive environment
- **Form 10-K, Item 1A: Risk Factors** - Competitive risks

**How to Interpret:**
1. Extract competitor names from Business section
2. Identify competitive landscape
3. Assess competitive intensity
4. Review competitive advantages/disadvantages

**AI Agent Guidance:**
- List main competitors
- Describe competitive landscape
- Format: "Main competitors: [list]. Competitive landscape: [description]"

---

## Compliance & Regulatory Prompts

### L1: Are there any material legal proceedings?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for updates)
- **Form 8-K** (for material legal events)

**Sections to Analyze:**
- **Form 10-K, Item 3: Legal Proceedings** - Pending litigation
- **Form 10-Q, Part II, Item 1: Legal Proceedings** - Updated litigation
- **Form 8-K, Item 1.02** - Material legal events

**How to Interpret:**
1. List all material legal proceedings
2. Assess potential financial impact (if disclosed)
3. Evaluate likelihood of adverse outcome
4. Review any settlements or judgments
5. Note any regulatory investigations

**AI Agent Guidance:**
- List material legal proceedings
- Assess potential impact
- Format: "Legal proceedings: [Case 1: description, Status, Potential impact], [Case 2: etc.]"

---

### L2: What regulatory risks does the company face?

**Forms Required:**
- **Form 10-K** (most recent)
- **Form 10-Q** (for regulatory updates)

**Sections to Analyze:**
- **Form 10-K, Item 1A: Risk Factors** - Regulatory risks
- **Form 10-K, Item 1: Business** - Regulatory environment
- **Form 10-Q, Part II, Item 1A** - Updated regulatory risks

**How to Interpret:**
1. Extract regulatory risk factors
2. Identify applicable regulations
3. Assess regulatory compliance
4. Evaluate impact of regulatory changes
5. Review any regulatory actions or investigations

**AI Agent Guidance:**
- List regulatory risks
- Assess compliance status
- Format: "Regulatory risks: [Risk 1: description, Impact], [Risk 2: etc.]. Compliance: [status]"

---

## AI Agent Implementation Guidance

### Data Extraction Strategy

1. **Form Identification:**
   - Identify which forms are needed for each prompt
   - Check filing dates to ensure most recent data
   - Verify form completeness (some filings may be amended)

2. **Section Navigation:**
   - Use form structure (Items, Parts) to locate sections
   - Cross-reference between forms when needed
   - Note that section numbers may vary slightly by form type

3. **Data Extraction:**
   - Extract quantitative data from financial statements
   - Extract qualitative information from MD&A and Business sections
   - Note any assumptions or estimates used in calculations

4. **Data Validation:**
   - Cross-check data across forms (e.g., 10-K vs. 10-Q)
   - Verify calculations
   - Note any discrepancies or restatements

### Analysis Methodology

1. **Trend Analysis:**
   - Always use multiple periods (minimum 3-5 years for annual, 4-8 quarters for quarterly)
   - Calculate growth rates, ratios, and percentages
   - Identify inflection points and patterns

2. **Comparative Analysis:**
   - Always compare to relevant benchmarks (peers, industry, historical)
   - Adjust for company size and stage when comparing
   - Use multiple metrics for comprehensive comparison

3. **Risk Assessment:**
   - Prioritize risks by materiality and likelihood
   - Consider both quantitative and qualitative factors
   - Assess risk mitigation strategies

4. **Forward-Looking Analysis:**
   - Base projections on historical trends and management guidance
   - Consider multiple scenarios
   - Clearly distinguish between facts and assumptions

### Response Format Guidelines

**For Non-Financial Users:**

1. **Structure:**
   - Start with a simple, direct answer in plain language
   - Follow with "What This Means" explanation
   - Provide "Why It Matters" context
   - Include "The Numbers" with explanations
   - End with "Key Takeaways" summary

2. **Language:**
   - Use everyday language, avoid jargon
   - Define all financial terms when first used
   - Use analogies and real-world examples
   - Explain what numbers mean in practical terms
   - Provide benchmarks: "This is considered good/bad because..."

3. **Data Presentation:**
   - Use simple tables with clear labels
   - Include explanations next to numbers
   - Use visual aids when helpful (simple charts)
   - Format numbers clearly: "$1.5 billion" not "$1,500,000,000"
   - Add context: "This is 10% higher than last year"

4. **Examples:**
   - "Think of it like this: [analogy]"
   - "In simple terms: [explanation]"
   - "This means: [practical interpretation]"
   - "For comparison: [benchmark]"

**For Financial Users:**

1. **Structure:**
   - Start with concise technical answer
   - Provide detailed methodology
   - Include comprehensive data analysis
   - Add peer comparisons and benchmarks
   - Conclude with analytical insights

2. **Language:**
   - Use standard financial terminology
   - Include technical details and calculations
   - Reference industry standards
   - Provide deeper analytical insights

3. **Data Presentation:**
   - Use detailed tables with multiple metrics
   - Include calculations and methodologies
   - Provide peer comparison tables
   - Show trends with statistical analysis
   - Format: Standard financial reporting format

4. **Technical Depth:**
   - Include calculation methodologies
   - Provide ratio analysis and decompositions
   - Reference accounting standards when relevant
   - Include sensitivity analysis where applicable

**Common Elements for Both:**

1. **Caveats:**
   - Note data limitations
   - Identify assumptions made
   - Highlight any uncertainties
   - Mention if data is unaudited or estimated

2. **Source Citations:**
   - Always cite which forms and sections were used
   - Note filing dates
   - Mention if data is from most recent filing or historical

### Quality Assurance

1. **Accuracy:**
   - Verify all calculations
   - Cross-check data sources
   - Ensure consistency across responses

2. **Completeness:**
   - Address all aspects of the question
   - Include relevant context
   - Note any missing or unavailable data

3. **Relevance:**
   - Focus on material information
   - Avoid unnecessary detail
   - Prioritize actionable insights

---

## Conclusion

This guide provides a comprehensive framework for building an AI agent capable of analyzing EDGAR filings. By following the form identification, section navigation, and analysis methodology outlined here, an AI agent can provide accurate, insightful answers to a wide range of financial analysis questions.

### Key Features of This Guide:

1. **Dual User Coverage:**
   - **Non-Financial Users:** Plain language explanations, definitions, benchmarks, and practical interpretations
   - **Financial Users:** Technical details, advanced metrics, peer comparisons, and deep analytical insights
   - Each prompt includes guidance for both user types

2. **Comprehensive Prompt Coverage:**
   - 52+ prompts across 12 major categories
   - Performance, trends, comparisons, risks, valuation, strategy, governance, ownership, M&A, guidance, industry, and compliance
   - Each prompt specifies exact forms and sections to analyze

3. **Practical Implementation:**
   - Clear data extraction strategies
   - Step-by-step interpretation methodologies
   - Response format templates for both user types
   - Quality assurance guidelines

### The key to effective EDGAR analysis is:

1. **Multi-form analysis** - Rarely rely on a single form
2. **Historical context** - Always consider trends over time
3. **Comparative perspective** - Compare to peers and benchmarks
4. **Qualitative + Quantitative** - Combine numbers with narrative
5. **Critical thinking** - Question assumptions and identify red flags
6. **User adaptation** - Tailor responses to user's financial knowledge level

### User Type Coverage Summary:

**✅ Non-Financial Users:**
- Plain language explanations for all concepts
- Definitions of financial terms
- Benchmarks and context for interpreting numbers
- Real-world analogies and examples
- Simple, practical interpretations
- "What this means" and "Why it matters" explanations

**✅ Financial Users:**
- Technical terminology and jargon
- Detailed calculations and methodologies
- Advanced metrics and ratio analysis
- Peer comparisons and industry benchmarks
- Deep analytical insights
- Standard financial reporting formats

This guide should be used as a reference for both prompt engineering and AI agent training to ensure comprehensive and accurate financial analysis capabilities that serve users regardless of their financial knowledge level.

