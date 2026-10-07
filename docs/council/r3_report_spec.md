# R3: Report Architect: FRA Client Report Specification (v1.0)

**Role:** Report Architect. **Inputs:** the current gold-standard FRA (52 pages, 18 sections, Rev 15 final delivery), `FRA_CURRENT_INTAKE.md`, and `RULEBOOK.md` §9 (headline and tier), §11 (action library) and §12 (guardrails).
**Privacy:** every name, number and example in this paper is fictional. The fictional client used throughout is **Northwind Example LLC**, owner **Jordan Sample**.

Provenance tags used throughout:
- **[DATA]** extracted from documents or bureau files by the pipeline.
- **[RULE]** computed or selected by the deterministic engine (Rulebook).
- **[AI]** drafted by the LLM from DATA and RULE outputs only.
- **[ANALYST]** entered or confirmed by the analyst.

---

## 1. Critique of the current report

### 1.1 What works (keep)

1. **The brand frame.** The navy header bar with the TRADELINE ASSOCIATES INC. wordmark, the gold rule under each title, the letterspaced gold "SECTION 0X" eyebrow, and the navy footer band all look premium and consistent. Keep them as they are.
2. **The five-status system** (PASS / NEEDS IMPROVEMENT / ACTION REQUIRED / PENDING-NEED DOCUMENT / N/A) with colored pills. Clients learn it in one page and can scan for orange. "Pending is not a negative finding" is a good piece of client reassurance.
3. **The finding card** (What we found / Why it matters / Recommended correction / Where & how to fix / Pass standard). This is the best part of the report. It is evidence first, it states the consequence, and it gives a channel and a finish line.
4. **"The central underwriting story"** callout. One paragraph that tells the client how a lender will see them. This is the paragraph they remember.
5. **Withholding the composite score on an incomplete file**, with a numbered list of what must close first. This is honest, and it matches the website promise.
6. **The identity matrix** (record holder × data point, with disagreeing cells shaded). It makes "your records don't describe the same company" visible at a glance.
7. **Disciplined language:** "appears inconsistent and should be verified", "TLA does not determine…", "dispute only if inaccurate", "directional positioning, not approval prediction". This already matches Rulebook G-02 and G-07.
8. **Action-path labels** (Client action / Third-party / Optional implementation / Completed in FRA) and the "Completed in FRA" checklist. The client can see the value delivered.
9. **Separate bureau cards** with KPI tiles, plus the explicit statement that bureaus do not share data.

### 1.2 What is hard for a non-expert client

| Problem | Evidence in the sample | Effect |
|---|---|---|
| **Length** | 52 pages. Section 09 alone (20 findings) runs about 11 pages. PASS points get the same full five-row card as ACTION REQUIRED points. | Clients stop reading after Section 05, which is where the "how to fix" content starts. |
| **Repetition** | The same 3–6 issues (TIN conflict, address, UCC filings, bureau depth) are restated in Sections 02, 04, 05, 06, 07, 08, 09, 10, 13, 14, 15 and 18. The strengths appear in 03, 04 and 18. The first actions appear in 02, 05, 15 and the 18 objectives. | Repetition reads as padding. It also creates inconsistency risk: one revision edits one copy and misses another. |
| **Jargon with no definitions** | DBT, PAYDEX, Intelliscore, SBFE, SBSS, KYC, UCC, "Accounts" as collateral, DSO, PFS, CP 575, 147C, intercreditor, subordination, shelf company, 411, CMRA, AU. There is no glossary. | Clients either feel talked down to or call the analyst. Both cost time. |
| **Density** | Paragraphs of 8–12 lines inside table cells. Up to 15 numbers in one sentence. | Hard to skim, and it looks like a legal brief. |
| **Exposure of raw identifiers** | Full tax IDs, full filing and document numbers, full street addresses, bureau file numbers. | Rulebook §13 masking applies. Showing the last 4 is enough to prove a mismatch. |
| **No "so what" line** | "Why it matters" is written for an underwriter ("can fail a KYC screen"). The owner still has to ask, "Is this bad for me, and how bad?" | This is exactly the gap the owner described: "explanation for the client is much appreciated." |
| **Phases with no dates** | The Section 14 roadmap has four phase columns of text. There are no weeks, dependencies or "you are here" marker. | The client cannot plan around it. |
| **Tracker is not a tracker** | Section 15 has priority, item, path and status. It has no checkbox, owner, target date, "done when" or space for notes. | The client cannot work the list or report back on it. |

### 1.3 Visual and production defects

- **Overflow.** The 5-tile status distribution bar on the scorecard page runs past the right margin, so the N/A tile is clipped. The layout component must use the full content width with fixed fractions.
- **Orphans.** A bureau card's table header row sits alone at the bottom of a page, and its body starts on the next page. Use `break-inside: avoid` on cards and keep each header with its first row.
- **Contrast.** White text on the gold NEEDS IMPROVEMENT pill and the amber PENDING pill is roughly 2.5–3:1. Fix this with token changes (§3).
- **Duplicated contact details.** The header and the footer both carry the full phone, fax, email and web block on every page. The footer space should hold the required disclaimer instead (G-14).
- **No table of contents with page numbers**, and no running section name in the header.

### 1.4 Compliance gaps against the Rulebook (must fix)

1. **G-01:** Section 01 lists "inquiry-removal" as an optional separate service. That phrase is on the blocklist. Remove it.
2. **R11:** The SBFE/SBSS section discusses SBSS scoring. The Rulebook says there is to be no SBSS gate or estimate. Keep SBFE as a data-source check only.
3. **G-14:** The disclaimer appears only on the final page. It must be on page 1 and in every footer.
4. **G-15 / G-16:** Product fit has no indicative ranges, confidence label or verified/self-reported label. Guarantor scores are educational VantageScore figures. The model label is in prose but is not standardized.
5. **G-21:** There is no consolidated list of open human-review items.
6. **ID-06 / CMRA:** The Resource Directory lists virtual-office providers as a source of a "commercial business address." A virtual or CMRA address can fail lender verification (ID-06 / HR-13), and it can look like an attempt to present a physical presence that doesn't exist. This listing needs analyst and counsel sign-off. The default is to remove it.

### 1.5 What is missing

1. A one-page **visual summary** ("At a Glance").
2. A **plain-English "What this means for you" line** on every finding and every bureau card.
3. A **glossary**, with the first use of each term in the body linked to it.
4. A **timeline** in weeks, with dependencies and the earliest application window.
5. A **progress tracker** the client can work through: checkboxes, owner, target date, "done when".
6. **Indicative ranges per product** under Rulebook §12, or the reason a range was suppressed.
7. A **revision and change log**, so a Rev 15 client can see what changed since Rev 14.
8. A **"what to send us" document checklist** that turns every PENDING item into a request.

---

## 2. Improved report structure

### 2.1 Principles

- **Keep sections 01–18 with the same numbers and titles**, so the website promise and returning clients still match. New material is either unnumbered front matter (At a Glance) or lettered appendices (A–D). Nothing is renumbered.
- **One canonical home per finding.** Each issue is fully described once, in its finding card (Section 09) or bureau card (Section 10), and gets an ID such as `F-01`, `B-EXP-02`, `G-03`. Every other mention is at most one line plus a cross-reference ("see F-01, p. 14"). This removes most of the repetition.
- **Tiered depth.** Cards for PASS and N/A points are compact (2 rows). Only NEEDS IMPROVEMENT, ACTION REQUIRED and PENDING points get the full card.
- **Length target:** 28–36 pages for a typical file. Soft warning at 40 pages, hard review at 46. The engine reports a page count before release.

### 2.2 Report-level content model (shared fields)

```
report.number              TLA-FRA-YYMM-XXXX                        [RULE]
report.revision            integer (0 = first delivery)             [RULE]
report.stage               DRAFT | IN REVIEW | FINAL CLIENT DELIVERY [ANALYST]
report.date, report.data_as_of_date                                 [DATA/ANALYST]
client.owner_display_name, client.owner_role, client.ownership_pct  [DATA]
entity.legal_name, entity.type, entity.formation_state, entity.formation_date [DATA]
funding.objective_amount_low/high, funding.purpose, funding.timeline [DATA intake A1–A5]
readiness.status           SCORED | WITHHELD | ON_HOLD               [RULE §9]
readiness.headline_H, readiness.tier, readiness.tier_meaning         [RULE §9]
readiness.withheld_reasons[]                                         [RULE + ANALYST]
statuses.distribution{pass,ni,ar,pending,na}                         [RULE]
findings[]  (see 3.6 for the card model)                             [mixed]
hr_items[]  {id, severity, plain_reason, affected_products[]}        [RULE §10]
analyst.name, analyst.reviewer2, signoff_timestamp                   [ANALYST]
```

### 2.3 Section-by-section

Each entry lists: purpose · fields · components · length · who writes it.

**Cover (unnumbered, p. 1)**
- *Purpose:* identify the report and set expectations.
- *Fields:* `report.*`, `client.owner_display_name`, `entity.legal_name/type/formation_state/formation_date`, `funding.objective_*`, `readiness.one_line_assessment` [AI, ≤25 words], `report.stage`.
- *Components:* cover block, Report Details key-value table, "Underwriting before the underwriting" callout, the 7-step sequence strip, and the G-14 disclaimer box.
- *Length:* 1 page. Everything is RULE/DATA except the one-line assessment [AI], which the analyst must approve.

**At a Glance (unnumbered, new, p. 2)**
- *Purpose:* the whole report on one page, for a client who reads nothing else.
- *Fields:* `readiness.status/tier/headline_H` or the withheld badge; `statuses.distribution`; `first_actions[0..2].title`; `strengths_top3[]` [AI from DATA]; `roadmap.phases[]` mini-timeline; `glance.what_this_means` [AI, 2–3 sentences, grade 8]; `hr_items.count_open`.
- *Components:* readiness dial or withheld badge, status distribution bar, three numbered action rows, a 3-tile strengths row, mini roadmap, and a navy "What this means for you" callout.
- *Length:* exactly 1 page, enforced. The text is [AI]; the numbers are [RULE].

**Contents (unnumbered, p. 3):** sections with page numbers and the Part I / Part II grouping. [RULE]

**01 How to Read & Use Your FRA**
- *Purpose:* explain the status system and the finding card, and point to the glossary.
- *Fields:* static template text, plus `report.sections_present[]`.
- *Components:* section table (shortened), status legend with pills, and a new annotated "How to read a finding card" sample graphic. The scope and limitations text moves to Appendix D, leaving a one-line pointer here.
- *Length:* 1 page (was 2). Static template text [RULE].

**02 Your First Three Actions**
- *Purpose:* the three gating items.
- *Fields:* `first_actions[3]{id, title, why_one_line, finding_ref, owner, target_window}`, where title and owner come from [RULE] (ranking by gating severity, from the AP library and the identity gates) and `why_one_line` is [AI]. `secondary_items[]{label, status, note}` [RULE + AI note].
- *Components:* numbered action cards (each with a "What this means for you" line), then a compact secondary-items table.
- *Length:* 1 page. The analyst may reorder the actions, and must give a reason if they do.

**03 Key Funding Strengths**
- *Purpose:* what a lender will like. These are the facts to lead with.
- *Fields:* `strength_tiles[6–12]{value, label, sublabel, source_doc_id}` [DATA, chosen by RULE from a fixed priority list]; `central_story` [AI, 90–140 words]; `no_derogs_statement` [RULE, printed only if verified].
- *Components:* KPI tile grid (3 columns, at most 4 rows) and the green "Central underwriting story" callout.
- *Length:* 1 page.

**04 Overall Assessment & Scorecard**
- *Purpose:* rate the five lender areas and show the readiness headline, or say why it is withheld.
- *Fields:* `areas[5]{key, status, summary}`, where status is [RULE] and summary is [AI, ≤60 words]; `readiness.*`; `readiness.withheld_reasons[]`; `concentrations[]{theme, points[], meaning}` [RULE grouping + AI meaning].
- *Components:* five area cards (2 + 2 + 1), the distribution bar, a readiness block ("Fund-Ready 82", printed with the tier meaning from §9 and the G-16 provenance line) or a withheld box, and a concentration table.
- *Length:* 2 pages.
- *Rule:* readiness is shown only when `readiness.status = SCORED`. ON_HOLD prints "On Hold — Pending Review" and no number.

**05 Priority Risk & Correction Flags**
- *Purpose:* every issue in one list, ordered by underwriting impact.
- *Fields:* `flags[]{rank, finding_ref, title, status, consequence_short}`. Rank and status are [RULE]; `consequence_short` is [AI, ≤30 words].
- *Components:* a ranked table, with the full detail left to the cards through the reference column.
- *Length:* 1 page (was about 2). This table holds no narrative.

**06 Master Business Address Decision**
- *Purpose:* separate the address candidates from stale and record-only addresses, and state the decision the client must make.
- *Fields:* `addresses[]{masked_display, class: CANDIDATE|BUREAU_CORRECTION|RECORD_ONLY, associated_records[], assessment}`. Class is [RULE]; assessment is [AI]; the analyst confirms. `address_decision.state: NOT_REQUIRED|PENDING_CLIENT|DESIGNATED` [ANALYST]; `cmra_flag` [RULE ID-06].
- *Components:* three grouped tables and a decision callout.
- *Length:* 1–2 pages. If only one consistent address exists, this section prints a half-page "No decision required" card so the numbering stays intact.
- *Masking:* street number and street name are shown, unit numbers abbreviated. Never show the owner's residence in full when it is not a candidate.

**07 Master Business Identity Matrix**
- *Purpose:* what each record holder believes about the business.
- *Fields:* `matrix.columns[]{source, date}`; `matrix.rows[]{field, values[], mismatch_mask[]}` [DATA + RULE comparison]; `entity_history[]{date, event, source_doc}` [DATA]; `identity_status[]{item, status, basis}` [RULE]; `intake_discrepancies[]` [RULE + AI].
- *Components:* identity matrix table (landscape-safe; shaded mismatch cells), status table, entity-history timeline, and callouts.
- *Length:* 2–3 pages.

**PART I — 08 20-Point Business Compliance Scorecard**
- *Purpose:* the 20 points on one page.
- *Fields:* `points[20]{no, name, status, one_line}`. Status is [RULE or ANALYST override]; one_line is [AI, ≤14 words].
- *Components:* scorecard table, plus a mini distribution bar at the top.
- *Length:* 1 page, hard limit.

**09 20-Point Audit — Detailed Findings**
- *Purpose:* the canonical home of each point.
- *Fields:* see the finding card model (§3.6).
- *Components:* full finding cards for non-PASS points; compact cards (header, "What we found" in one sentence, and the pass standard) for PASS and N/A.
- *Length:* 6–9 pages (was 11+).

**PART II — 10 Commercial Credit Bureau Analysis**
- *Purpose:* Experian, D&B and Equifax, each read separately, plus SBFE and LexisNexis status.
- *Fields:* `bureaus[]{name, file_id_masked, report_date, status, kpis[]{value,label}, tradelines[], corrections[], verify_items[], clean_items[], channel_ref, what_this_means}`.
- *Components:* one bureau card per bureau, then a "Funding implications" callout [AI].
- *Length:* 3–5 pages.
- *Rule:* `verify_items` print only when HR-05 has fired, with G-17 wording. No SBSS estimate (R11).

**11 Banking & Financial Analysis**
- *Purpose:* deposits, statements, returns, statements-vs-schedule consistency, and business debt.
- *Fields:* `banking.kpis[]`; `debt_schedule[]{lender_masked, product, commitment, balance, monthly}`; `consistency_gaps[]{item, source_a, source_b, gap, status, resolution}`, where the gap is [RULE R10] and wording follows "TLA identifies the discrepancy only"; `statement_status` [RULE R19].
- *Components:* KPI tiles, debt table, gap table, callout.
- *Length:* 2–3 pages.

**12 Personal Guarantor Snapshot**
- *Purpose:* the guarantor's credit, kept separate from Part I.
- *Fields:* `scores[]{bureau, value, model, date}` with a G-16 provenance line; `util_overall`, `util_cards[]` (AU excluded, per R14); `inquiries{raw_by_bureau, window}`; `derogs`; `liabilities_vs_pfs[]`; `highest_value_action` [RULE from AP-01/02 + AI wording].
- *Components:* score tiles, bureau-by-bureau table, utilization table, and a gold "Highest-value, lowest-cost action" callout.
- *Length:* 2–3 pages.

**13 Funding Objective & Product Fit**
- *Purpose:* separate the transactions, document the use of proceeds, and show product fit with ranges where allowed.
- *Fields:* `transactions[]`; `use_of_proceeds_checklist[]{item, status}`; `products[]{code, name, fit_label, S_p, tier, earliest_ready_date, range_low, range_expected, confidence, income_basis, assumptions[], suppression_reason, pg_flag, cost_disclosure}`. All [RULE] except `rationale` [AI, ≤70 words].
- *Components:* transaction table, checklist, product-fit cards ordered by the §8 sequence (MCA always last, with its cost), and a PG-exposure line (F-32).
- *Length:* 3–4 pages.
- *Rule:* never sum the ranges into a total (G-07).

**14 Corrective Action Roadmap**
- *Purpose:* phases on a timeline.
- *Fields:* `roadmap.phases[]{n, title, start_week, end_week, items[]{finding_ref, label}, depends_on[]}` [RULE from SEQ-0…SEQ-7 and AP timelines]; `application_window{earliest_date, condition}` [RULE]; `workstreams[]` (parallel tracks) [RULE + ANALYST]; `execution_sequence[]{rank, channel, rationale}` [RULE order + AI rationale].
- *Components:* the new Gantt-style roadmap timeline, the "Read this before any application" callout (with the SEQ-7 truthfulness sentence), and the sequence table.
- *Length:* 2 pages.

**15 Funding Readiness Action Center**
- *Purpose:* the working tracker.
- *Fields:* `actions[]{pri, finding_ref, task, done_when, owner: CLIENT|THIRD_PARTY|OPTIONAL|COMPLETED, target_date, status}`; `corrections_paths[]`; `completed_in_fra[]`; `documents_to_send[]{doc, why, finding_ref}` (new).
- *Components:* action-path legend, action tracker table with checkboxes, implementation-path table, a 2-column completed checklist, and the "Send us" checklist.
- *Length:* 3–4 pages.

**16 Resource Directory**
- *Fields:* `resources[]{group, name, points[], access}`. The source is a config table carrying `last_verified` [RULE], filtered to the channels referenced in this report.
- *Length:* 1–2 pages. No commercial vendor is listed unless the analyst approves it and it is wall-off compliant (§13).

**17 Documents Reviewed**
- *Fields:* `documents[]{doc_id, title, date_of_record, key_facts_masked}`. The doc_id is the citation key used in every finding.
- *Length:* 1–2 pages. [DATA + ANALYST]

**18 Current Audit Conclusion**
- *Fields:* `conclusion.summary` [AI, ≤180 words, no new facts]; `objectives[≤6]{objective, completion_standard}` [RULE from first actions and phases]; the process strip with "you are here"; the critical disclaimer [RULE static].
- *Length:* 1–2 pages.

**Appendix A — Glossary** (new). Terms are auto-selected from the 4.4 list when the term appears in the rendered body; analysts may add terms. 1–2 pages.

**Appendix B — Open Review Items & Assumptions** (new, G-15 and G-21). `hr_items[]` in plain language, the "Pending review" product list, and the range assumptions (score used, income/revenue source, rates and terms). 1 page.

**Appendix C — Revision & Change Log** (new). `revisions[]{rev, date, summary, sections_changed[]}`. 0.5 page.

**Appendix D — Scope, Limitations & Disclosures.** Scope text moved from 01, "What this report does not do", the G-22 dispute right, "not a lender", and the compensation disclosure (G-20) where applicable. 1–2 pages.

---

## 3. Component library (HTML/CSS → PDF with WeasyPrint)

### 3.1 Brand tokens

Values were sampled by eye from the PDF. Verify them against the brand files if those exist.

```css
:root{
  /* Brand */
  --navy-900:#14294A;   /* table header rows, footer band */
  --navy-800:#17325B;   /* header bar */
  --navy-700:#1B3A66;   /* H1/H2 titles, KPI values */
  --blue-600:#2E5C8A;   /* intro/lede text, H3 subheads, links */
  --gold-600:#B58A2E;   /* rules under titles, eyebrow, tile underline, left accent bars */
  --gold-300:#E2BF69;   /* header website text, footer wordmark */
  /* Status (pill backgrounds / text) */
  --pass:#1F7A35;            --pass-fg:#FFFFFF;
  --ni:#BF8A12;              --ni-fg:#1F1500;   /* dark text: fixes contrast */
  --ar:#C2571A;              --ar-fg:#FFFFFF;
  --pending:#DDB04A;         --pending-fg:#2B2100;
  --na:#6B7280;              --na-fg:#FFFFFF;
  --third-party:#2B5C8F;     --third-party-fg:#FFFFFF;
  --open:#E5E7EB;            --open-fg:#374151;
  /* Neutrals */
  --ink:#1F2937; --muted:#6B7280; --rule:#D9DEE5;
  --panel:#F1F3F6; --panel-2:#F7F8FA; --white:#FFFFFF;
  /* Callout tints */
  --green-tint:#EEF6EF; --gold-tint:#FBF5E6; --navy-tint:#EEF2F8; --ar-tint:#FBEFE8;
  /* Type */
  --font-sans:"Lato", "Helvetica Neue", Arial, sans-serif;
  --font-wordmark:"Libre Baskerville", Georgia, serif; /* fallback only; use logo SVG */
}
```

**Fonts.** The body, headings, tables and pills are Lato (Google Fonts): 400, 400 italic, 700 and 900. The wordmark is a letterspaced serif in caps. Use the official logo as an SVG asset. If no SVG exists, set `--font-wordmark` in caps with 0.06em tracking. Bundle the font files locally with `@font-face` and `url(fonts/...)`, because the render must not depend on network access.

**Type scale (pt).**

| Use | Size and weight | Notes |
|---|---|---|
| Cover title | 30 / 900 | navy-700 |
| Section title | 17 / 900 | navy-700 |
| Eyebrow | 8.5 / 700 | gold-600, 0.28em tracking, uppercase |
| Lede | 10.5 / 400 | blue-600 |
| Body | 9.5 / 400 | line-height 1.45, ink |
| Table | 8.5 | |
| Labels | 7.5 / 700 | 0.12em tracking, uppercase, muted or navy |
| KPI value | 16 / 900 | |

Use `font-variant-numeric: tabular-nums` for money columns, and fall back gracefully if the font build doesn't support it.

**Page.** US Letter, margins 0.95in top / 0.6in sides / 0.9in bottom, content width about 7.3in.

### 3.2 Page header and footer

- **Header:** a `position: running(hdr)` element placed through `@page { @top-center { content: element(hdr) } }`. It is a full-bleed navy-800 bar, 0.75in high, with a 3pt gold-600 bottom border. The logo goes on the left. The right side carries the website (gold-300) plus email and phone (white, 7.5pt). Interior pages add the running section name in small caps through `string-set: section content()` on H2.
- **Footer:**
  - Line 1 (muted, 7pt): `Funding Readiness Audit • {entity.legal_name} • {report.number} Rev {n} {stage} • {date} • Page counter(page) of counter(pages)`.
  - Line 2 (6.5pt, italic): the short G-14 disclaimer, "Educational funding-readiness assessment, not a credit decision, loan offer, or guarantee of approval, terms, or amount. Lenders decide independently."
  - A navy-900 band below that holds only the gold letterspaced wordmark, so the contact details are not duplicated.
- **Cover:** `@page :first` uses the same header, and its footer shows the full G-14 sentence.

### 3.3 Cover page

Gold eyebrow "FUNDING READINESS SERIES", then the title "Funding Readiness Audit" at 30pt, then a gold rule, then the subtitle "Lender Preparation & Fundability Diagnostic for {entity}". Below that come the lede paragraph, the "How to use this report" panel (panel background, gold left bar), the sequence strip, and the Report Details key-value table (labels 7.5pt letterspaced, rows separated by 0.5pt rules). The final row is OVERALL ASSESSMENT, with the one-line assessment in blue-600 bold. After the table come the "Underwriting before the underwriting" callout (navy left bar) and the confidentiality line. A diagonal DRAFT watermark appears when `stage ≠ FINAL` (§6).

### 3.4 Section opener

`<header class="section">` contains the eyebrow ("SECTION 09", or "PART II · SECTION 10"), the H2, a 2pt gold rule, and an optional lede (blue-600). Use `break-before: page` for 01–18 and the appendices. Use `break-after: avoid` on the opener so it never sits alone at the bottom of a page.

### 3.5 Atoms

- **Status pill:** an inline-block, 7pt, 700 weight, 0.12em tracking, uppercase, padding 2pt 7pt, radius 2pt, with status tokens for background and text. Text values: `PASS`, `NEEDS IMPROVEMENT`, `ACTION REQUIRED`, `PENDING / NEED DOCUMENT`, `N/A`. Variants: `INSUFFICIENT DATA` (pending colors with italic text) and `PENDING REVIEW` (an outline style for HR-affected items).
- **Tracker pills:** `AWAITING CLIENT` (pending), `IN PROGRESS` (gold-tint background, gold text), `THIRD-PARTY ACTION` (third-party), `OPEN` (open), `DONE` (pass).
- **KPI tile:** panel background, a 3pt gold-600 bottom border, padding 10pt, a value line (16pt, 900, navy-700) and a 7pt label in two uppercase lines. Add a source footnote marker (¹) linked to `source_doc_id`. Lay tiles out with CSS grid (`grid-template-columns: repeat(3,1fr)`; WeasyPrint ≥ 62) or with a table fallback. Each tile gets `break-inside: avoid`.
- **Status distribution bar:** a 5-cell table at 100% width with `table-layout: fixed`. Each cell is 20% wide, so it cannot overflow (this fixes the defect in the current report). Each cell shows the count (18pt) and the label.

### 3.6 Finding card (the core component)

Content model:
```
finding{
  id: "F-04", point_no: 4, title, status,                         [RULE]
  what_we_found: rich text with source cites [D-03]                [AI from DATA]
  why_it_matters                                                    [AI, from rule-library rationale]
  what_this_means_for_you: one sentence, ≤30 words, grade ≤8        [AI]  NEW
  recommended_correction                                            [RULE AP-ID → AI wording]
  where_how_to_fix: resource_refs[] → Section 16                    [RULE]
  pass_standard + pass_progress ("met" / "outstanding: …")          [RULE text + RULE eval]
  effort: QUICK (≤2 wks) | MEDIUM (2–8 wks) | LONG (>8 wks)         [RULE]  NEW
  owner: CLIENT | THIRD_PARTY | OPTIONAL                            [RULE]
  sources: doc_id[]                                                 [DATA]
  analyst_override{status_from, status_to, reason}                  [ANALYST, internal only]
}
```
Layout: a white card with a 0.5pt rule border and a 4pt gold-600 left bar. The left bar is orange (`--ar`) for ACTION REQUIRED and green for PASS.
- **Header row:** panel background, with "04." in gold and the title in navy 700. The pill sits on the right, next to an effort chip ("≈ 2–8 weeks").
- **Body:** a 2-column grid. The labels column is 1.45in wide, 7.5pt letterspaced navy, with PASS STANDARD in green.
- **"What this means for you":** sits directly under the header, before WHAT WE FOUND. It is a full-width navy-tint band with a small "i" icon and the label IN PLAIN ENGLISH. This is the first thing a client reads in each card.
- **Sources:** a footer line in 7pt muted: "Sources: D-01 IRS EIN notice · D-07 Bank beneficial-ownership certification".
- **Breaking:** `break-inside: avoid` for compact cards. Full cards may break between rows, never inside a row.
- **Compact variant** (PASS/N/A): header, the plain-English band, a one-sentence finding and the pass standard.

### 3.7 Bureau card

A white card with a 4pt navy top border.
1. Header: bureau name (H3), a masked file ID and the report date (7.5pt muted), and the pill.
2. A KPI tile row (4–5 tiles; "—" plus "NO SCORE DISPLAYED" when null).
3. A tradeline table (navy-900 header row; numbers right-aligned; DBT shown as a chip).
4. CORRECTIONS REQUIRED (gold eyebrow and bullets).
5. ITEMS TO VERIFY (only with HR-05, and only with the fixed G-17 sentence).
6. A "Clean:" line.
7. A "Channel:" line referencing Section 16.
8. The plain-English band.

Set `break-inside: avoid` on the header and KPI row as a unit, and keep `thead` with the first row (`tr { break-inside: avoid }`, with `thead` repeated through `display: table-header-group`).

### 3.8 Identity matrix table

The first column (data point) is 1.1in, bold. The remaining source columns share the width equally; above six sources, switch to a landscape named page (`@page wide { size: letter landscape }`). The header row is navy-900 with the source name and the date on a second line. Mismatched cells get the `--ar-tint` background, a 1pt `--ar` left border and a "≠" glyph, so the meaning is not carried by color alone. Matching cells are white. "Not available" is italic and muted. A legend sits below the table.

### 3.9 Scorecard table

Columns: # (0.35in, gold, bold) · Audit point · Status (pill) · One-line finding · Page ref. Rows have zebra striping (`--panel-2`). The table is limited to one page: if it overflows, the one-line text is cut to 14 words and the build logs a warning.

### 3.10 Roadmap timeline (new)

This is an inline SVG generated server-side; WeasyPrint renders SVG reliably. It is a horizontal Gantt chart.
- The x-axis covers weeks 0–N, with N set by the latest phase end, rounded up to 4. Gridlines are drawn every 2 weeks with month labels.
- There is one lane per phase (Phase 1 Identity · 2 Credit Strength · 3 Debt/UCC Verification · 4 Funding Execution), plus parallel workstream lanes such as "Existing facility renewal".
- Bars are navy-700 with white labels. Dependency arrows are gold.
- A dashed gold vertical line marks the **Earliest application window**, with its date and condition.
- A "Reassessment" diamond marks the reassessment point.
- A "You are here" marker shows week 0 on the report date.

The roadmap also appears as a simplified strip (phases only) on the At-a-Glance page. Dates are always "target" dates computed from the AP timelines, and they are labeled "estimated; depends on third-party processing times."

### 3.11 Action tracker table (new design for 15A)

Columns:
- ☐ (a 10pt empty square drawn in CSS, with a border so it prints)
- Pri
- Task (bold title plus one line)
- Done when (from `pass_standard`)
- Owner (pill)
- Target date
- Status (pill)
- Notes (a blank ruled cell for the client to write in)

Completed rows show ☑ in green with the text struck through in muted gray. The table repeats its header on every page. A small progress bar at the top shows "4 of 17 actions complete (24%)" [RULE]; it is useful on reassessment revisions.

### 3.12 Callouts

| Variant | Style | Use |
|---|---|---|
| `callout--story` | green-tint background, 4pt pass bar, green eyebrow | Central underwriting story |
| `callout--plain` | navy-tint background, navy bar, eyebrow "WHAT THIS MEANS FOR YOU" | At a Glance, end of a section |
| `callout--key` | gold-tint background, gold bar | Highest-value action, "Read this before any application" |
| `callout--caution` | ar-tint background, orange bar | Withheld score, on-hold notice |
| `callout--info` | panel background, gold bar | How to use this section |
| `callout--navy` | solid navy-800, white text, gold eyebrow | Disclaimers, the "Underwriting before the underwriting" quote |

All callouts use `break-inside: avoid`.

### 3.13 Glossary

A two-column layout (`columns: 2; column-gap: 18pt`). Each entry has the term in bold navy (with its abbreviation expanded) and a one-line definition. At the first use in the body, the term gets a dotted underline and a superscript "G" that links to the glossary anchor; PDF internal links work in WeasyPrint. Entries are sorted A–Z and grouped by letter, with gold letter headers.

### 3.14 Other

- **Product-fit card:** the product name, the fit label (FIT · CONDITIONAL · NOT YET · NOT RECOMMENDED), a range line ("Indicative range $X–$Y · Confidence: Medium · Revenue: verified") or the suppression reason, the PG/cost disclosure line where it applies, and the rationale.
- **Sequence strip:** seven chevrons (DISCOVER…FUND). Completed steps are navy, and the current step is gold.
- **Masked identifier helper:** `mask_tin("123456789") → "•••••6789"`. Use the same helper for account and file IDs.

---

## 4. Client explanation standards

### 4.1 Reading level and tone

| Text type | Target (Flesch-Kincaid grade) | Rule |
|---|---|---|
| Plain-English lines, At a Glance | ≤ 8 | Short sentences of ≤ 20 words. Second person ("you", "your business"). |
| Narrative body (story, summaries, findings) | ≤ 11 | ≤ 28 words per sentence on average. One idea per sentence. |
| Technical rows (tables, channels, pass standards) | no target | Terms must be in the glossary. |

The generator computes the grade for each block and flags anything over target to the analyst. It does not auto-rewrite.

**Tone:**
- **Direct.** Say what is wrong in the first sentence.
- **Respectful.** The client is a business owner preparing for lenders, not a problem case.
- **Not alarming.** Don't use "critical failure", "red flag", "fatal", "disaster" or "urgent!". Exclamation marks are banned.
- **No blame.** Write "the bank record shows a different number", not "you gave the bank the wrong number".
- **Confident but bounded.** "Lenders typically…", "This can…", never "will".
- **Constructive.** Every negative statement is paired with a path.
- **Strengths first** in each area summary when real strengths exist.
- **Numbers:** round in prose (≈ $1.9M) and keep exact values in tables. Never introduce a number that is not in DATA or RULE output.

### 4.2 The "What this means for you" rule

Every finding card, bureau card, area card (Section 04) and product card carries exactly **one** plain-English sentence that:
1. States the practical effect on the client's funding path, in their terms (time, approval friction, cost, options).
2. Uses no unexplained abbreviations. Glossary terms are allowed only if the term is spelled out.
3. Is ≤ 30 words and grade ≤ 8.
4. Contains no new facts and no numbers beyond what the card already shows.
5. For PASS: confirms the strength and says what to protect ("Keep this as is; lenders will check it again at closing.").
6. For PENDING: says what we need and that it is not a negative ("We couldn't check this yet. Send the statements and we'll complete it.").
7. Never promises an outcome.

Examples (fictional):
- ACTION REQUIRED, TIN mismatch: "Until the bank's record shows the same tax ID as the IRS, a lender's identity check can stop your application before anyone looks at your finances."
- NEEDS IMPROVEMENT, UCC: "Two lenders already have a claim on your receivables, so a new lender will want to know what's left before using them as security."
- PASS, registered agent: "This is in order. Keep the agent current so official notices always reach you."

### 4.3 Formatting rules for clarity

- At most 6 lines per paragraph inside cards. Use bullets for lists of 3 or more corrections.
- Abbreviations are spelled out at first use in each Part. The glossary covers the rest.
- Cross-reference instead of repeating ("see F-17").
- Dates are always MM/DD/YYYY. Money is formatted $X,XXX in tables and $X.XM in prose.

### 4.4 Glossary terms (minimum set; one-line definitions)

1. **Tradeline:** an account a creditor reports to a credit bureau, with its balance and payment history.
2. **Revolving utilization:** how much of your available credit-card limit you are using, as a percentage.
3. **Hard inquiry:** a record that a lender pulled your credit for an application. It is visible to other lenders.
4. **Derogatory item:** a negative record, such as a late payment, collection or charge-off.
5. **Collection:** a debt passed to a collector after it went unpaid.
6. **Charge-off:** a debt the creditor wrote off as a loss. It is still owed.
7. **Authorized user (AU):** a person added to someone else's card. Lenders often discount these accounts.
8. **Personal guarantee (PG):** your personal promise to repay a business debt if the business can't.
9. **FICO Score:** the consumer credit score family most lenders use. There are several versions.
10. **VantageScore:** an alternative consumer score, often shown in free apps. Lenders may see different numbers.
11. **Middle score:** the middle of your three bureau scores. Banks and the SBA often use it.
12. **PAYDEX:** Dun & Bradstreet's 1–100 score for how promptly a business pays its suppliers.
13. **DBT (Days Beyond Terms):** how many days past the due date a business usually pays.
14. **Intelliscore Plus:** Experian's 1–100 business credit risk score.
15. **D-U-N-S Number:** Dun & Bradstreet's nine-digit ID for a business file.
16. **SBFE:** Small Business Financial Exchange, a members-only network where lenders share business-loan payment data.
17. **UCC filing:** a public notice that a lender has a claim on certain business assets as collateral.
18. **Blanket lien:** a UCC filing that covers most or all business assets.
19. **Subordination / intercreditor agreement:** agreements that set which lender gets paid first from shared collateral.
20. **DSCR (Debt Service Coverage Ratio):** cash available to pay debts divided by the debt payments due. Lenders typically look for 1.25 or more.
21. **NAICS code:** the six-digit government code describing what your business does.
22. **SIC code:** an older four-digit industry code that some bureaus and lenders still use.
23. **EIN:** your business's federal tax ID number from the IRS.
24. **CP 575 / Letter 147C:** IRS letters that confirm a business's EIN (the original notice, and a later confirmation).
25. **KYC (Know Your Customer):** the identity checks banks must run before opening accounts or lending.
26. **Beneficial ownership certification:** a bank form listing who owns and controls a business.
27. **Secretary of State (SOS):** the state office that records business formations and status.
28. **Registered agent:** the person or company designated to receive legal notices for the business.
29. **CMRA:** Commercial Mail Receiving Agency, a mailbox or virtual-office address. Lenders may not accept it as a business location.
30. **411 / directory listing:** a public phone listing under the business name that lenders can verify.
31. **LexisNexis business file:** a data file that lenders and insurers use to verify a business's identity and records.
32. **Time in business (TIB):** how long the business has actually operated, measured from when it began operating.
33. **Use of proceeds:** exactly what the borrowed money will be spent on.
34. **Source of repayment:** the cash flow that will repay the loan.
35. **SBA 7(a):** a bank loan partly guaranteed by the U.S. Small Business Administration.
36. **MCA (Merchant Cash Advance):** an advance repaid from future sales through daily or weekly debits. It is often very expensive.
37. **Invoice factoring:** selling unpaid invoices to a company for cash now.
38. **PFS (Personal Financial Statement):** a form listing your personal assets, debts and income.
39. **DSO (Days Sales Outstanding):** the average number of days customers take to pay you.
40. **NSF:** a non-sufficient-funds event, when a payment bounces for lack of funds.
41. **Net-30 account:** a supplier account that gives you 30 days to pay. Some report to business bureaus.
42. **Promotional (0%) APR:** a temporary interest rate that ends on a set date and then resets higher.
43. **Statement closing date:** the date your card balance is reported to bureaus. This is not the due date.
44. **Fund-Ready / Near-Ready / Needs Work / Not Ready:** TLA's readiness tiers. They describe preparation, not approval.

---

## 5. AI drafting prompt guidance

### 5.1 Inputs the model receives (and nothing else)

1. A **structured fact sheet** (JSON) containing `entity`, `funding`, `documents[]{doc_id,title,date}`, and extracted facts. Each fact carries `{value, source_doc_id, confidence}`.
2. **Engine outputs:** statuses, findings with the AP-library remedy IDs and their rationale strings, HR items, product scores and ranges or suppression reasons, and the sequence.
3. **Section instructions:** the field to draft, a word limit, the reading-level target, and the required phrases (G-14 to G-22 text is inserted by the template, not by the model).
4. **The house style guide** (§4) and two exemplars (§5.4).

The model never receives raw credit-report PDFs at drafting time, and it never sees full SSNs, DOBs or account numbers. Masking happens before the prompt.

### 5.2 Hard rules (system prompt; enforced by the §12 filter)

- **No invented facts.** Every number, date, name and status in the output must appear in the fact sheet or the engine output. A post-check extracts every number and date from the draft and matches it to the inputs. Any mismatch sends the draft back for regeneration, then to the analyst.
- **No new math** beyond what the engine provides. Simple rounding for prose ("about $1.9M") is allowed only with the "about/≈" marker.
- **Cite sources.** Every sentence in *What we found* ends with source keys in brackets, such as "[D-03]" or "[D-03, D-07]". The renderer turns these into the card's Sources line and removes them from the inline text, keeping them in the analyst view.
- **State disagreements; never resolve them.** When two sources conflict, name both, say which is controlling only if the engine marked one as controlling, and recommend verification by the appropriate party. Required pattern: "{Source A} shows X; {Source B} shows Y. TLA does not determine which is correct; {party} should confirm before lender submission."
- **No guarantees** (G-07): no "will be approved", "qualify for", "raise your score by", odds, or single-number amounts.
- **Disputes only for possible inaccuracy** (G-01, G-02, G-17). Never suggest disputing, removing or "challenging" accurate information. Never call an item illegal or a violation.
- **No §12 blocklist terms** (CPN, 609, sweep, inquiry removal, credit repair, AU purchase, concealment timing, and the rest).
- **No legal, tax or accounting conclusions.** Use "the appropriate financial professional should confirm" and "TLA makes no legal lien-priority determination."
- **Missing data stays missing.** If a field is null, write "not provided" or "not yet obtained" and mark it PENDING. Never infer it.
- **Respect the canonical-home rule.** Outside the finding's own card, refer to it in one sentence with its ID.
- **Use no prohibited-basis language** (G-10). Write "the guarantor", not personal descriptors.
- **Return JSON** with `{field, text, cited_doc_ids[], numbers_used[]}`, so the checks can run.

### 5.3 Generation flow

Engine → fact sheet → per-field drafting calls (small, bounded fields, not "write the whole report") → number/date trace check → blocklist and LLM guardrail filter → reading-level check → analyst review queue. On a guardrail hit, the field is regenerated once, then escalated (§12 enforcement).

### 5.4 House-style exemplars (fictional)

**Key Funding Strengths: "The central underwriting story"** (fictional client Northwind Example LLC):

> **This is an operating business with real, documented results whose paperwork has not kept up with its growth.** Two years of federal returns show revenue of about $640K and then $710K, with a profit margin near 14% each year [D-11, D-12], and the business has kept the same operating bank account for more than three years [D-05]. The guarantor's credit is a strength: low card usage and no collections or public records on the three reports dated 09/18/2026 [D-14]. The weaknesses are about consistency and depth, not about how bills have been paid. The business's records show two different addresses, and its business credit files are thin. One isolated 30-day late payment on a personal card from early 2026 is noted in Section 12. These are the kinds of issues that are typically corrected in weeks, not years.
>
> *In plain English:* lenders will like your numbers; your job now is to make every record describe the same business.

**Finding card** (fictional point 15, Proof of Business Address):

> **15. Proof of Business Address — ACTION REQUIRED · ≈ 2–8 weeks**
> **In plain English:** Lenders need to see one business address that matches everywhere. Right now two are in use, which can slow an approval or trigger extra questions.
> **What we found:** The state registration and the IRS notice list the business at a suite address on Harbor Street [D-02, D-03]. The bank's account profile lists the owner's home address [D-06]. The Experian business file shows the suite address; the D&B file shows the home address [D-15, D-16]. No lease, utility bill or service agreement has been provided for either address. TLA does not determine which address is correct.
> **Why it matters:** Lenders and bureaus match a business by its name, tax ID and address. When the address differs between records, automated checks may send the file to manual review or stop it.
> **Recommended correction:** Choose the address the business genuinely operates from or is entitled to use, provide one supporting document, then update the records that differ (see Section 06).
> **Where / how to fix:** Bank relationship officer (account profile update); D&B D-U-N-S Manager; Experian business profile update — see Section 16.
> **Pass standard:** One address, supported by a document, appearing identically on the state, IRS, bank and bureau records. *Outstanding: designation and proof.*
> *Sources: D-02 State formation record · D-03 IRS EIN notice · D-06 Bank account profile · D-15 Experian Business · D-16 D&B report*

---

## 6. Analyst review workflow

### 6.1 Report numbering and stages

- **Report number:** `TLA-FRA-YYMM-XXXX`. YYMM is the month the engagement opened. XXXX is a 4-character sequential or random base-32 code. Don't use client initials, so the number carries no PII. The number is fixed for the life of an engagement.
- **Revision:** `Rev N`. Rev 0 is the first client release. Every regenerated client-visible PDF after release increments N. Internal drafts are numbered separately, as `Draft d.N` (d.1, d.2…), and never show a Rev number.
- **Reassessment** after corrections is a **new report number**, with "Follows TLA-FRA-YYMM-XXXX Rev N" on the cover, so the original audit stays intact as the baseline.

| Stage | Watermark | Footer label | Who can set it |
|---|---|---|---|
| DRAFT (AI output, unreviewed) | Diagonal "DRAFT — NOT FOR CLIENT DELIVERY", 60pt, navy at 8% opacity, on every page (`position: fixed` element) | `Draft d.N` | system |
| IN REVIEW | Diagonal "IN REVIEW", same style | `Draft d.N — In Review` | analyst |
| FINAL CLIENT DELIVERY | none | `Rev N FINAL` | analyst + second reviewer when required |

PDF metadata (title, author "Tradeline Associates Inc.", subject = report number + Rev) is set in all stages. Draft PDFs also carry "DRAFT" in the filename.

### 6.2 Release checklist ("FINAL CLIENT DELIVERY" stays disabled until every box is checked)

**Data and facts**
1. Every extracted fact used in a finding has been viewed against its source document. The analyst confirms each card's Sources line.
2. The number/date trace check passes with zero unmatched values. Any manual edits to AI text have been re-traced.
3. Entity name, type, formation state and date match the controlling state record exactly. Intake discrepancies (for example, a formation state that differs from the state record) are shown, not silently fixed.
4. Document dates fall within staleness limits (§1.5 and R19), or the report labels them as stale.

**Rules and review items**
5. All BA items are resolved; otherwise no client PDF is produced. All BP items show "Pending review" on the affected products. All AD items have been acknowledged with a note. Appendix B matches the open list.
6. Status overrides each have a reason in the log (internal only), and a second reviewer has approved any override to PASS.
7. Readiness is shown only if `SCORED`. Otherwise the withheld or on-hold wording is used.
8. Ranges are shown only where §6.0 allows them, with the G-15 label and the assumptions. There is no summed total, and MCA appears last with its cost.

**Language and compliance**
9. The §12 blocklist scan and LLM filter are clean. G-14 to G-22 are present (the template self-checks).
10. Every "What this means for you" line is present and within limits. Reading-level flags have been reviewed.
11. Masking: no full SSN or DOB; tax IDs, account numbers and file IDs show the last 4 only; the residence address appears only where it is a candidate; nothing beyond city/state appears in any funder-facing extract.
12. Resource Directory: every link has a current `last_verified` date. No unapproved commercial vendors or CMRA promotion. No cross-sell of tradeline products (§13 wall-off).
13. The compensation disclosure is included if applicable. The client fee is shown in dollars where any range is shown (G-20).

**Production**
14. Page count is within target, or a reason is logged. There are no orphaned headers, no clipped components and no empty sections. Visual QA covers pages 1–3 and one page of each component type.
15. The change log (Appendix C) is updated for Rev ≥ 1.
16. The analyst signs off. A second reviewer is required when any of these apply: a BA/BP item was cleared, a status was overridden, a cards-first exception applies (HR-52), PG exposure triggers apply (HR-54), or this is the client's first FRA under a new analyst.

### 6.3 Change log

- **Internal (audit trail, kept 5 years under §13):** each event records timestamp, user, field path, old value, new value, reason and engine/config version. The input snapshot hash is stored with each Rev, so a deterministic re-run reproduces it.
- **Client-facing (Appendix C):** one row per Rev: `Rev · Date · What changed (plain English) · Sections affected`. For example: "Rev 2 · 10/21/2026 · Bank statements received; Point 10 moved from Pending to Pass; Sections 04, 08, 09, 11, 15 updated."
- **Status deltas:** on Rev ≥ 1, the generator adds a "Changed since last revision" chip (gold outline, "UPDATED") on affected cards, and the action tracker progress bar shows the new completion count.

### 6.4 Analyst edit surface

Analysts edit only [AI] and [ANALYST] fields in a side-by-side view: the draft text, the source facts with document thumbnails, and the trace-check results. [RULE] fields are read-only, except through a logged override. [DATA] corrections go back through extraction correction, which re-runs the engine, never through hand-editing the narrative. This keeps the narrative, the numbers and the rules consistent across revisions.
