# Funding Readiness Audit Tool — Council Brief

We are building an internal tool (used only by a funding-consulting team, Tradeline Associates) that:
1. Takes uploaded consumer credit reports (Experian / Equifax / TransUnion, often a 3-bureau merged report) plus an intake questionnaire.
2. AI extracts structured data from the reports (scores, tradelines with type/limit/balance/open date/status/late history/AU vs primary, inquiries with dates and bureau, collections, charge-offs, public records, personal info: names, addresses, employers, DOB/SSN variations).
3. A DETERMINISTIC rules engine scores "funding readiness" — overall and per funding type — and flags items that need HUMAN review.
4. Generates a report: readiness score + tier, estimated funding range, eligible products, prioritized action plan with timelines, human-review items, a funder-facing profile summary, document checklist.

Funding types in scope (all of them):
- Business 0% APR credit cards (personal-guarantee based "card stacking")
- Personal 0% APR credit cards / personal unsecured loans
- Business unsecured line of credit (bank / fintech)
- SBA loans (7(a), Express, microloans)
- Business term loans (bank and online lenders)
- Revenue-based financing / merchant cash advance
- Equipment financing
- Invoice factoring / receivables financing
- Real-estate investor loans (DSCR, fix & flip) — light coverage
- "Not sure" — tool should recommend

The intake must ASK QUESTIONS ABOUT THE FUNDING GOAL FIRST (type, amount, purpose, timeline, personal vs business) and then branch to only the follow-up questions relevant to the chosen type(s).

Rules must be: concrete numeric thresholds, explainable, editable config, based on how real funders/underwriters actually decide. Industry-standard thresholds are fine for now (the team will tune later). Where your claims come from published sources (SBA SOP 50 10, bank card issuer rules like Chase 5/24, Amex, etc.), say so. Be honest where practice varies.

Compliance context: this is a consulting tool, not a lender. Must avoid advice that violates FCRA / CROA (e.g., no "dispute accurate items", no CPN/new-identity advice, no misrepresentation of income/business). Human-review flags should catch these risks.
