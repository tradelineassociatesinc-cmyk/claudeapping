# R1: Compliance and Credit-Data Proposal (FCRA / CROA / ECOA / GLBA / Metro 2)

Verified current facts (October 2026) that the rules depend on:
- The CFPB medical-debt rule (Jan 2025) was **vacated** by E.D. Tex. in July 2025. The bureaus' voluntary policy still applies: paid medical collections are not reported (since 7/2022), medical collections under $500 original balance are not reported (since 4/2023), and there is a 1-year wait before reporting. ([CFPB](https://www.consumerfinance.gov/archive/blog/medical-debt-anything-already-paid-or-under-500-should-no-longer-be-on-your-credit-report/), [Mondaq](https://admin.mondaq.com/unitedstates/financial-services/1653558/federal-judge-vacates-cfpb-medical-debt-rule))
- About 15 states have their own medical-debt reporting bans (NY, CO, CT, VA, MN, NJ, IL, CA, ME, RI, VT, WA; MD, DE and OR newer). In October 2025 the CFPB issued an interpretive rule saying the FCRA **preempts** those state laws. This is contested and unsettled. ([Goodwin](https://www.goodwinlaw.com/en/insights/blogs/2025/11/cfpb-issues-rule-that-fcra-preempts-state-measures-barring-medical-debt), [beancount summary](https://beancount.io/blog/2026/08/21/medical-debt-credit-report-ban-vacated-protections-2026-guide))
- Mortgage: tri-merge is still required. VantageScore 4.0 is allowed for a limited set of approved lenders (FHFA, April 2026). FICO 10T is approved but not yet live. ([Freddie Mac](https://sf.freddiemac.com/general/credit-score-models), [HousingWire](https://www.housingwire.com/articles/fhfa-credit-models-mortgage-lending/))
- Civil judgments and tax liens have been off the bureau files since the NCAP changes (judgments July 2017; all tax liens April 2018). A judgment or lien parsed from a 3-bureau consumer report is almost always a parsing or data-source error. Their absence also does **not** mean the client has none (see section 7).

---

## 1. Data quality and extraction rules

**1.1 Source capture (required for every upload)**
- Record `bureau`, `report_date`, `source_type`, and `score_model` for each score.
  - `source_type` is one of: annualcreditreport disclosure, monitoring service such as IdentityIQ/SmartCredit/MyFICO, or lender tri-merge.
  - `score_model` is one of: FICO 8, FICO 9, FICO 10/10T, Bankcard 8, Auto 8, VantageScore 3.0/4.0, or unknown.
- **Never treat a VantageScore as a FICO.** Monitoring-service scores are usually VS3. They can differ from FICO 8 by 20 to 60+ points. If `score_model = unknown`, all score-based thresholds run at **low confidence**.
- **Staleness:**
  - Report older than 30 days: mark stale for revolving products, because utilization moves monthly.
  - Older than 60 days: the readiness score is provisional.
  - Older than 90 days: block the funding-range estimate.

**1.2 Normalization**
- Map every tradeline to Metro 2 concepts, whatever the display format:
  - **Account Status:** 11 current; 13 paid/closed; 71/78/80/82/83/84 = 30/60/90/120/150/180+ days late; 93 collection; 94 foreclosure; 95 voluntary surrender; 96 repossession; 97 charge-off; 61–65 paid derogatory variants; DA/DF deleted.
  - **ECOA code:** 1 individual, 2 joint, 3 AU, 5/7 co-maker, T terminated, W business, X deceased.
  - **Payment-history grid:** 24–84 months.
  - **DOFD:** date of first delinquency.
  - **Compliance Condition Code:** XB disputed, XC dispute resolved but consumer disagrees, XH resolved.
  - **Consumer Information Indicator:** BK chapter and disposition codes.
- Business-type accounts (ECOA W) on a personal report are tagged `business_reported_personally`.

**1.3 Cross-bureau merge**
- Match key: normalized creditor name (alias table, e.g. "SYNCB/AMAZON" = "Synchrony Amazon") + last 4 of account number (when shown) + open date within ±31 days + account type.
- Score each match from 0 to 1. **≥0.85 auto-merge; 0.60–0.85 merge with low confidence; <0.60 keep separate.**
- Tolerances for agreement after merge:
  - Balance: ±10% or ±$150 (reporting-date lag).
  - Limit: exact. A limit missing on one bureau is a known issue for some issuers (high-balance substitution). Flag it but don't score it as a mismatch.
  - Status: must match at the severity tier.
  - DOFD: within ±60 days.

**1.4 Duplicate and double-count detection**
- **OC + collector double-count:** the original creditor shows a charge-off with balance >$0 **and** a collection agency shows the same debt with balance >$0. When the OC sold the debt it should report $0 and "transferred/sold". Use only the collector balance for DTI and flag "possible double reporting – verify."
- Two collectors reporting the same debt (same original creditor, amount within 5%): count one and flag.
- The same account reported twice on one bureau with different account numbers (common after servicing transfers): count one and flag.
- Student loans: count each disbursement separately for history, but group them for derogatory counts (one default = one event).

**1.5 Inconsistency flags** (these drive "items to verify"; see section 5)
- Status tier differs across bureaus, e.g. 90-day late on EX but current on TU.
- DOFD differs by more than 60 days, or DOFD is later than the charge-off date. These suggest **re-aging**.
- An item is past its FCRA §605 period: 7 years + 180 days from DOFD for collections and charge-offs; 7 years for lates; Ch.13 at 7 years and Ch.7 at 10 years from filing (bureau practice).
- A paid medical collection appears, or a medical collection under $500 original balance appears (violates bureau policy).
- A balance appears on an account reported as included in bankruptcy.
- The account shows open but has had no updates for more than 6 months ("stale tradeline").

**1.6 Extraction confidence and when to stop**
- The extractor returns per-field confidence. Core fields are status, balance, limit, open date, ECOA, and the late grid.
- Send the whole report to **human review before scoring** if any of these are true:
  - Fewer than 90% of tradelines have all core fields at ≥0.8 confidence.
  - Extracted tradeline count differs from the report's own summary count by more than 1 per bureau.
  - Extracted total revolving balance or limit differs from the summary by more than 5%.
  - Any score cannot be tied to a model and bureau.
  - Personal-info section confidence is below 0.9. Identity checks depend on it.
  - Scanned or image-only pages make up more than 20% of pages, or the OCR fallback was used.
- Show the confidence for each output section in the report. Don't hide it.

---

## 2. Derogatory classification and decay (numeric)

**Severity points (0–100).** Per-item severity = base × decay. Aggregate derogatory load = highest item + 0.5 × second + 0.25 × each further item, capped at 100. Funding-type rules (owned by the other council members) consume this load plus the hard stops.

| Item | Base | Notes on score-model treatment |
|---|---|---|
| 30-day late | 20 | All models. An isolated single 30-day late is often forgiven manually after 24 months. |
| 60-day late | 35 | |
| 90-day late | 50 | Most card issuers treat any 90+ within 24 months as a decline. |
| 120–180+ late | 60 | |
| ≥3 lates on one tradeline within 12 months ("rolling") | +15 on that tradeline | |
| Collection, unpaid, non-medical, ≥$100 | 60 | FICO 8 ignores collections with **original balance <$100**. Put those at 10 (manual-UW visibility only). |
| Collection, paid, non-medical | 35 | FICO 9/10 and VS3/4 ignore paid collections. **FICO 8 does not.** Most card issuers still use FICO 8, so the 35 stands for card products. Use 15 for products scored on FICO 9/10/VS4. |
| Medical collection, unpaid, ≥$500 | 25 | FICO 9 weights medical less and VS3/4 ignore it. Lenders discount it manually. |
| Medical collection, paid or <$500 | 0 | Generates the data-quality flag in 1.5 instead of a penalty. |
| Charge-off, unpaid | 75 | |
| Charge-off, paid / settled for less | 55 | "Settled for less" is still derogatory. |
| Repossession (96) | 80 | |
| Voluntary surrender (95) | 75 | |
| Foreclosure (94) / deed-in-lieu / short sale | 90 / 80 / 80 | |
| Civil judgment or tax lien (if present) | 70 / 85 | **Always human review**, because these should not appear on a bureau file (1.5). A federal tax lien or IRS debt matters heavily for SBA (delinquent federal debt). |
| BK7 discharged | 90 | |
| BK13 active (in plan) | 95 | Needs trustee permission for new credit, so it is a **hard stop** for new credit. |
| BK13 discharged | 80 | |
| BK7/13 dismissed | 95 | Debts survive. Worse than discharged. |
| BK filed / open (no disposition) | 100 | Hard stop. |
| Default on a federal debt (student loan, SBA, FHA) | 85 | SBA/CAIVRS relevance. Human review. |

**Decay multiplier** (lates, collections, charge-offs, repos, foreclosures). Age is measured from DOFD (or the event date for repo/foreclosure). Age from the date of last activity or last payment is **not** used, because paying an old collection does not restart its age.

| Months since DOFD/event | 0–6 | 6–12 | 12–24 | 24–36 | 36–60 | 60–84 | >84 (+6 for coll/CO) |
|---|---|---|---|---|---|---|---|
| Multiplier | 1.00 | 0.85 | 0.65 | 0.45 | 0.30 | 0.15 | → obsolete; data-quality flag, score 0 |

**Bankruptcy decay** is measured from the **discharge/dismissal date**, because lender seasoning rules key off discharge:

| Months since discharge | 0–12 | 12–24 | 24–48 | 48–84 | 84–120 |
|---|---|---|---|---|---|
| Multiplier | 1.00 | 0.80 | 0.55 | 0.35 | 0.20 |

Bureaus remove a BK at 10 years from filing (Ch.7) or 7 years (Ch.13).

**Rules of thumb that should be configurable:**
- Recovery evidence lowers residual severity by a further ×0.8. Evidence means ≥12 months of perfect history on at least 2 primary revolving accounts opened after the derogatory event.
- AU accounts (ECOA 3) **never** add positive depth credit in the rules engine. They are listed separately. Their lates are noted but not scored.

---

## 3. Identity and fraud-indicator rules

| Indicator | Detection | Action |
|---|---|---|
| **Different SSN** across bureaus or vs intake (not a 1-digit transposition) | Compare last 4 or full SSN as shown | **HARD BLOCK + compliance review.** Possible mixed file, synthetic ID, or CPN. Never proceed. |
| SSN invalid structure (area 000/666/9xx, group 00, serial 0000) | Rule | Hard block |
| SSN-to-age inconsistency | SSN issued after June 2011 (randomized) with DOB before ~2005, or oldest tradeline opened when client was under 16 (excluding AU) | Hard block, compliance review (CPN indicator) |
| Thin or new file for an older adult | Client ≥30 years old with oldest primary tradeline <24 months, many AU lines, and few or no inquiries before last year | Human review (synthetic/CPN pattern) |
| DOB variation | Year differs | Human review (mixed file). Day/month differs only: low-severity flag. |
| Name variations | Different first name, or a surname not explained by intake (maiden/married) | Human review (mixed file) |
| Address variations | >5 addresses in 24 months, a state the client says they never lived in, CMRA/mail-drop/UPS Store address, or an address on a business-report record | >5 or never-lived: human review. CMRA: compliance flag. |
| Accounts the client says are not theirs (intake checkbox per tradeline) | Intake attestation | **Block applications** on that bureau until resolved. The resolution route is an identity-theft report (FTC IdentityTheft.gov) and an FCRA §605B block. Not ordinary credit repair. |
| Inquiries client doesn't recognize | Intake | Human review. If ≥2 unrecognized: treat as possible identity theft. |
| **Fraud alert** – initial (1 yr), extended (7 yr), active duty (1 yr) (FCRA §605A) | Report flag | **Not a block.** Under §605A(h), creditors must verify identity, and with an extended alert they must call the listed phone number. Warn about delays and auto-declines. Card stacking that relies on instant decisions is "delayed – plan for manual verification." Advise the client to **keep it** if fraud is real. Never suggest removing a legitimately placed alert to speed up approvals. |
| **Security freeze** | Report flag | **Blocks** applications that pull the frozen bureau. Action item: "Client must temporarily lift the freeze before applying." Lifts are free and fast online. Never recommend selective freezing to steer which bureau a lender pulls (see section 7). |
| Consumer statement on file | Report text | Display it verbatim to the reviewer only. Human review if it mentions identity theft, dispute, or military service. |
| Deceased indicator (ECOA X) on any account of a living client | Rule | Hard block. Data error. Human review. |
| OFAC / "potential match" alert on a report | Report flag | Hard block, compliance review |

---

## 4. Human-review triggers (software must not decide alone)

1. **Any hard block in section 3.** Identity integrity can't be inferred, and proceeding risks facilitating fraud (18 U.S.C. §1014 false statements to banks; CROA §1679b(a)(2) identity alteration).
2. **Extraction confidence failures** (1.6). The score would be built on bad data.
3. **Judgment, tax lien, or federal-debt default appearing.** These are atypical for a bureau file and have heavy SBA impact.
4. **Open or active bankruptcy, BK13 in plan, or BK dismissed less than 24 months ago.** There are legal constraints on new credit, and the trustee or court is involved.
5. **Re-aging or obsolete-item signals** (1.5). Possible FCRA violation by a furnisher. Needs careful, accurate dispute guidance.
6. **Client says an item is inaccurate or not theirs.** The human decides whether it is a genuine inaccuracy or an identity-theft route and documents the basis.
7. **Intake income inconsistent with the bureau data or documents.** Examples: stated income above 3× what employer and tradeline profile suggest, or stated business revenue that doesn't match bank statements by more than 20%. Misrepresentation risk.
8. **Client asks for or mentions CPN, "new credit profile," EIN-in-place-of-SSN for personal credit, tradeline purchase to qualify, or "removing all negatives."** Compliance escalation. The tool must never auto-answer.
9. **Active-duty servicemember** (active-duty alert, SCRA/MLA indicators). Special protections (MLA 36% MAPR on covered consumer credit).
10. **Elderly or vulnerable client signals** (age 70+ taking large PG debt, or a cognitive concern noted by staff). UDAAP/elder financial exploitation risk.
11. **Aggregate new personal-guarantee exposure** recommended over $100k or more than 50% of verified annual income. Suitability: the client carries the risk.
12. **Any medical collection in a state with a reporting ban.** The law is unsettled given the CFPB's preemption position, so a human decides how to describe it.
13. **Report shows XB/XC dispute codes.** Some lenders (and mortgage AUS) treat disputed accounts differently. Disputes may need resolving before underwriting.
14. **Mixed bureau sources** (e.g., one bureau older than 60 days) or **unknown score model**.
15. **Any funder-facing profile before it is sent** (section 6.4).

---

## 5. Compliance guardrails for the report text

**5.1 Never generate (hard-coded blocklist plus LLM output filter; regenerate or escalate on hit):**
- "Remove/delete negative items," "clean up your credit," "dispute everything," "609 letter/loophole," "credit sweep," "sweep inquiries," "dispute inquiries you authorized."
- Any reference to CPN, credit privacy number, secondary credit profile, using an EIN/ITIN in place of an SSN on a personal application, or "new credit identity."
- Advice to state income, revenue, time in business, employment, or business purpose other than as documented.
  - Allowed: "On consumer card applications, issuers may consider income to which you have a reasonable expectation of access (Reg Z §1026.51(b)). Report it accurately."
- Guarantees: "guaranteed approval," "you will receive $X," "will raise your score by N points," "approval odds 95%."
- "Credit repair," "fix your credit" as service descriptions. (Using them may trigger CROA and state CSO registration or bonding, e.g. CA, TX, FL, GA.)
- Recommending purchased AU tradelines **for the purpose of qualifying**, or "piggybacking to hide derogatories."
- Recommending converting card limits to cash via third-party "liquidation" or manufactured transactions that breach cardholder agreements.
- Legal conclusions: "this item is illegal/inaccurate," "the creditor violated the FCRA."
- Any use of a prohibited basis (race, color, religion, national origin, sex, marital status, age except as permitted, public-assistance income, good-faith exercise of CCPA rights) in scoring or text. A broker that refers applicants is a "creditor" for Reg B §1002.4(a)/(b) purposes (§1002.2(l)).

**5.2 "Items to verify" wording.** The tool may list an item only if an **objective trigger** from 1.5 fired. Template:
> "**Item to verify:** [Creditor] is reported as [status A] by [Bureau 1] and [status B] by [Bureau 2] (or: appears to be past the standard reporting period / appears to be reported by both the original creditor and a collector). Please review whether this information is accurate and complete. Under the FCRA you may dispute information **you believe is inaccurate or incomplete** with the credit bureau or the furnisher. Accurate, timely information cannot lawfully be required to be removed, and a dispute should not be filed for information you believe is correct."
- Never use "inaccurate," "error," or "wrong" as the tool's own conclusion. Use "inconsistent," "appears," "verify."
- For accurate derogatory items, the action-plan language is time and behavior based: "This item ages; its impact typically lessens after [X] months." Allowed alternatives: "You may ask the creditor about a goodwill adjustment; creditors are not obligated." "Paying or settling may help with lenders that review collections manually; it may not change some scores."

**5.3 CROA-safe framing**
- The firm is likely within CROA if it sells, for a fee, a service to "improve a consumer's credit record, credit history, or credit rating" (15 U.S.C. §1679a(3)). An action plan with score-improvement steps can fall in scope. **Counsel must decide before launch.**
- If in scope, CROA requires all of the following:
  - No fees before the services are fully performed (§1679b(b)). The TSR advance-fee ban also applies to telemarketed sales.
  - A written contract with a 3-business-day cancellation right.
  - The "Consumer Credit File Rights Under State and Federal Law" disclosure.
  - No untrue or misleading statements to bureaus or creditors.
- Safer framing: the report is a **funding-readiness assessment and education**, not credit repair. Score-related items are phrased as general education ("lower revolving utilization is generally associated with stronger scores").

**5.4 Required disclaimers** (footer on every page, and in full on page 1)
- "This is an educational readiness assessment, not a credit decision, loan offer, or guarantee of approval, terms, or amount. Lenders make independent decisions using their own criteria and may obtain their own credit reports."
- "Estimated ranges are illustrative, based on general industry practices, and may not reflect any specific lender."
- "Scores shown are [model] from [source] dated [date] and may differ from scores lenders use."
- "Tradeline Associates is not a lender [and not a credit repair organization — only if counsel confirms]. You can dispute inaccurate information yourself, for free, directly with the credit bureaus."
- "Business credit cards and loans typically require a personal guarantee; you are personally liable. Promotional 0% APR periods end; the rate afterward may be high, and balance-transfer and cash-advance fees apply."
- Products with no TILA disclosures (MCA, factoring): "This product may not be a loan; the effective cost can be very high. Review the total repayment amount." Several states require commercial-financing disclosures, including NY, CA, UT, VA, GA, FL, CT, and KS. Point the team to counsel.

---

## 6. Data-handling rules

1. **Consent and permissible purpose.** Collect a signed (e-sign) authorization before upload. It states the purpose (funding-readiness consulting), the uses, sharing, and retention.
   - If the firm pulls reports through a reseller or monitoring service, it needs written instructions under FCRA §604(a)(2) and must comply with the reseller's end-user terms.
   - Client-uploaded self-disclosures avoid a pull but still need consent.
2. **GLBA.** The firm is likely a "financial institution" for FTC purposes.
   - **Safeguards Rule** (16 CFR 314): written infosec program, a qualified individual, risk assessment, MFA, encryption in transit and at rest, vendor oversight, and FTC breach notice within 30 days for incidents affecting 500+ consumers (in force since May 2024).
   - **Privacy Rule:** privacy notice. Sharing with funders relies on the consumer-initiated-transaction exception, so it is documented per funder.
   - **Disposal Rule** (16 CFR 682) for consumer-report information.
3. **Retention.**
   - Raw report PDFs: delete within **30 days** after the report is generated, or at engagement end, whichever comes first, unless the client consents in writing to longer.
   - Extracted structured data: engagement + 24 months, then delete or anonymize.
   - Audit logs: 5 years.
   - Never use client data to train models. The LLM vendor must have zero-retention or no-training terms and a DPA.
4. **Masking in generated reports.**
   - SSN: never displayed (only "SSN variations: 0 / 1 detected").
   - DOB: year only.
   - Account numbers: last 4.
   - Addresses: full in the internal view; city/state only in the funder profile.
   - Reviewer screens show full data behind role-based access, with access logged.
5. **CRA risk in the funder-facing profile.** If the firm regularly assembles consumer credit information and furnishes it to third parties (funders) for credit eligibility, it risks being a **consumer reporting agency** under FCRA §603(f). Mitigations:
   - Send the profile only at the consumer's direction, for a specific named funder, after the consumer reviews it.
   - Summarize; don't attach raw reports.
   - Funders pull their own credit.
   - Counsel sign-off required.
6. **Accuracy of the profile.** It must contain only verified facts with the source shown: no rounding up of revenue, no time-in-business inflation, AU accounts labeled.
7. **Adverse information.** The tool does not make credit decisions, so no adverse action notice is needed. But if funder declines are relayed, do not paraphrase them as the firm's own decision.

---

## 7. What the other experts will likely get wrong or overstate

**SBA underwriter**
- Will treat a single score cutoff as SBA policy. In fact, the SBSS minimum (currently 165 for 7(a) small loans under SOP 50 10 8; confirm the current SOP), lender overlays, and personal FICO are three different things. Practice varies widely by lender.
- Will assume a clean bureau report means no judgments, liens, or federal delinquencies. NCAP removed judgments and liens, and **CAIVRS and federal debt never appear on a consumer report**. The tool must ask in intake and require document or third-party checks; it must not infer.
- May over-penalize old or medical collections. SBA lenders routinely accept them with a written explanation.
- May push the tool to collect criminal-history detail beyond what SBA forms require. Keep that to the forms and route it to human review.

**Card-stacking broker** (highest compliance risk)
- Will count AU tradelines as "aged primary depth," and may recommend **buying** AU slots. Issuers and manual reviewers discount AUs, and the rules engine must not reward them.
- Will encourage aggressive income and revenue statements and "household income" without the Reg Z reasonable-access nuance. False statements on bank applications are a federal crime (18 U.S.C. §1014).
- Will recommend "inquiry removal" or disputing authorized inquiries (disputing accurate information). They may also recommend **freezing bureaus to steer pulls**: not illegal per se, but it can cause auto-declines and can look evasive. Don't build rules around it.
- Will treat business-card reporting as uniform. It isn't: some issuers report business cards to personal files (e.g., Capital One, Discover per issuer statements), many report only on delinquency. Practice varies and changes.
- Will overstate expected funding totals and understate PG liability and post-promo APR. The FTC has pursued "business funding" sellers that obtained personal cards for consumers and charged percentage fees with deceptive claims (e.g., FTC v. Seek Capital, 2023). Funding-range outputs need ranges, assumptions, and disclaimers, never point promises.
- Will rely on monitoring-service VantageScores as if they were FICO 8 or Bankcard 8.

**MCA underwriter**
- Will dismiss personal credit as irrelevant ("we fund 500s"). That is true for approval, but it ignores identity integrity: MCA is a prime channel for synthetic and CPN fraud, so section 3 still applies in full.
- Will equate "not a loan" with "unregulated." State commercial-financing disclosure laws, UDAP, and New York's 2019 ban on out-of-state confessions of judgment matter. Stacking positions and default-risk language must be disclosed plainly.
- Will see judgments and UCC liens in their data (Clear/LexisNexis/UCC searches) and assume the consumer report should show them. It won't, so the tool must ask in intake.
- May overweight bank-statement revenue without checking it against stated revenue. Mismatches over 20% are a human-review trigger, not something to quietly average away.

**General**
- Everyone will want derogatory penalties keyed to the "date of last activity." Use DOFD.
- Everyone will want the tool to say "dispute this." It may only say "verify this" when there is an objective trigger.
