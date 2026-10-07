# R3: Commercial Credit Bureaus, UCC and Business-File Rules

**Persona:** commercial credit bureau specialist (Experian Business, D&B, Equifax Business, SBFE/FICO LiquidCredit, LexisNexis, UCC/public records, vendor tradelines).
**Scope:** FRA audit points 11, 12, 13, 18, 19 and the Part II commercial bureau cards. It plugs into RULEBOOK v1.0. It reuses source labels **[PUB]** (published by the bureau/agency), **[DP]** (industry/community data point), **[EXP]** (expert judgment, team-tunable), and guardrails G-01 to G-22.
**Privacy:** every example uses fictional placeholders ("Acme Widgets LLC", BIN `000000000`, D-U-N-S `00-000-0000`).

---

## 0. Verified score scales and channels (reference table)

| Bureau / model | Scale | Direction | Bands used by the engine | Source |
|---|---|---|---|---|
| Experian Intelliscore Plus **V2** | 1–100 percentile, risk class 1–5 | Higher = lower risk | 76–100 Low · 51–75 Low-Med · 26–50 Med · 11–25 Med-High · 1–10 High | [PUB/DP] creditplus.com, nav.com |
| Experian Intelliscore Plus **V3** | 300–850 | Higher = lower risk | 781–850 Low · 721–780 Med-Low · 661–720 Med · 601–660 Med-High · 300–600 High | [PUB] experian.com, nav.com |
| Experian Financial Stability Risk (FSR) | 1–100 percentile + class 1–5 | Higher = lower risk | 66–100 class 1 · 31–65 class 2 · 11–30 class 3 · 4–10 class 4 · 1–3 class 5 | [PUB] experian.com FSR V2 |
| Experian DBT | Days beyond terms, dollar-weighted | Lower = better | 0 ideal; see §2 | [PUB] |
| D&B PAYDEX | 1–100 | Higher = better | 80 = pays on terms; >80 early; <80 late (≈70 = 15 days late, ≈50 = 30 days late [DP]) | [PUB] dnb.com |
| D&B Failure Score (Financial Stress) | Raw 1,001–1,875 · percentile 1–100 · class 1–5 | Higher raw/percentile = lower risk; **class 1 = lowest risk** | | [PUB] dnb.com |
| D&B Delinquency Predictor | Raw 101–670 · percentile 1–100 · class 1–5 | Same as above | | [PUB] dnb.com |
| Equifax Business Credit Risk Score (US) | 101–992 | Higher = lower risk | ">556 good" | [DP] creditstrong, LendingTree |
| Equifax Business Failure Score (US) | 1,000–1,880 | Higher = lower risk | ">1,315 good" | [DP] |
| Equifax Payment Index (US) | 1–100 | Higher = better; 90+ = paid as agreed | | [DP] LendingTree. **Equifax Canada's index is a different scale; never mix.** |
| FICO SBSS (LiquidCredit) | 0–300 | Higher = lower risk | Lender-generated only | [PUB] FICO via nav.com. **SBA stopped using SBSS for 7(a) Small on 3/1/2026 (Procedural Notices 5000-875701 and 5000-876777)** |

**Correction and disclosure channels (each card shows `channel_verified_date` and must be re-verified every 6 months)**

| Bureau | Identity / firmographic updates | Data disputes | Notes |
|---|---|---|---|
| Experian Business | BusinessCreditFacts.com (authenticated officer) | "Submit Data Dispute" link on a live report, or BusinessDisputes@experian.com · Commercial Relations 1-888-211-0728 | Investigations are generally completed in about 30 days [PUB] |
| D&B | D-U-N-S Profile Manager (dnb.com/duns/duns-manager), free | Same tool, for "payment experiences you believe do not apply" | Officer, owner or director must verify; D&B may call to validate [PUB] |
| Equifax Commercial (US) | Commercial Research Request Form → commercialdisclosures@equifax.com | Same channel | Phone numbers differ by source (1-888-407-0359 in past reports; 1-877-254-3263 per LendingTree). **Mark "verify current number"** [DP] |
| LexisNexis | Business report via the LexisNexis Risk Solutions small-business request channel (P.O. Box 105108, Atlanta, GA 30348-5108, confirmed as the Consumer Center address) | Same | Owner's personal disclosure: consumer.risk.lexisnexis.com, 1-888-497-0011 |
| SBFE | No direct business report. Data reaches lenders through Certified Vendors | Dispute with the furnishing lender | sbfe.org/faqs |
| UCC | The state SOS UCC debtor search in the **state of formation** for a registered organization (UCC §9-307(e)) | Only the secured party files an amendment or termination (UCC-3). The debtor may file an information statement (§9-518) | [PUB] UCC Art. 9 |

---

## 1. Extraction schema (per commercial report)

Every field carries `confidence` (0–1), `source_page` and `bureau`. A blank field is extracted as `null`, never as 0. A value of "0" printed by the bureau is extracted as 0, with `bureau_default_zero=true` when it is a known placeholder (see 1.6).

### 1.1 Report metadata
`bureau` {EXP, DNB, EFX, LNX, SBFE_vendor} · `product_name` (e.g., "Business Credit Advantage", "CreditSignal", "Credit Insights", "Business Credit Report Plus") · `report_date` · `file_id` (BIN / D-U-N-S / Equifax commercial ID / LexID) · `source_type` {bureau direct, monitoring service, reseller, lender-provided} · `no_record_found` flag · `insufficient_data` flag · summary counts (tradelines, inquiries, UCC, derogatories).

### 1.2 Identity block (compared against Master Identity, §3)
legal_name · dba/trade names (all) · entity_type · state_of_incorporation · date_incorporated / year_started · address(es) with "current/previous" tag · phone · website · email · NAICS (code + text) · SIC (code + text) · years_in_business · employee_count (+ "estimated" flag) · sales/revenue (+ "estimated/modeled" flag) · officers/principals · parent / headquarters / branch indicator · corporate linkage (D&B family tree) · EIN/TIN if shown (often masked) · business status (active / out of business / inactive).

### 1.3 Scores
For each score: `model` + `version`, value, class, percentile, raw, `scale_min/max`, `direction`, risk label as printed, key factors/reason codes (verbatim), score_date.
- EXP: Intelliscore Plus (V2 or V3, **always record the version**), FSR (V1/V2), DBT current, DBT predicted, Experian "Days Within Terms" section, credit limit recommendation.
- DNB: PAYDEX (current + 3-month or 12-month trend if shown), Failure Score (raw/percentile/class/failure rate %), Delinquency Predictor (raw/percentile/class/delinquency rate %), D&B Rating (e.g., "1R3"), Viability Rating if shown, Overall Business Risk label, Maximum Credit Recommendation, "% within terms".
- EFX: Business Credit Risk Score, Business Failure Score, Payment Index, Equifax "credit limit/ utilization" summary if shown.
- SBFE / SBSS: value only if a lender document shows it. **Never estimated.**

### 1.4 Tradelines (one row per trade experience)
category/industry of furnisher (raw + normalized: vendor/supplier, financial services, card, leasing, telecom/utility, fleet, other) · furnisher name if shown (Experian usually shows category only) · account type (open/net-terms, revolving, installment, lease, contract) · terms (Net 10/15/30/60, REVOLVE, CONTRCT, COD) · date opened · last activity · **last reported/sale date** · recent high credit · credit limit · balance owed · current % · DBT 1–30 / 31–60 / 61–90 / 91+ (% or $) · payment status (current, slow, collection, charged-off, placed for collection) · active/inactive flag · comments.
D&B payment experiences add: "paying record" (prompt/slow 30/etc.), "high credit", "now owes", "past due", "selling terms", "last sale within", and the experience count.

### 1.5 Inquiries, public records, collateral
- Inquiries: date, industry/category, count by month (Experian shows a 9-month grid).
- UCC: filing number, state, filing type (initial/amendment/continuation/termination), filed date, lapse date, secured party, collateral text (verbatim; often truncated), status, debtor name/address as filed.
- Judgments, tax liens, suits, bankruptcies: type, filing date, amount, status/disposition, plaintiff/creditor, court. **Commercial files are not covered by consumer NCAP removal. A judgment or lien on a business file is a real finding, not a data error. HR-06 does not apply to commercial files.**
- Collections (commercial agency placements): agency, date placed, amount, status.

### 1.6 Fields that are commonly blank or 0, and what that means

| Field | Typical artifact | Engine treatment |
|---|---|---|
| Years in business = 0, employees = 0, sales = $0 (Experian) | Bureau has no firmographic input yet | `UNDERSTATED` if documents show otherwise; correctable through BusinessCreditFacts. Not a derogatory |
| Sales or employees "estimated/modeled" (D&B) | D&B models these | `VERIFY`; supply tax-return-supported figure via Profile Manager after identity lock |
| PAYDEX blank / "—" | Fewer than 3 experiences from 2 suppliers [DP] | Status "Not generated – thin file". **Never displayed as 0** |
| NAICS/SIC blank | Not self-reported | `BLANK`; models then apply an industry default |
| Legal name blank, DBA only | Trade-style file | `BLANK` critical (§3) |
| Equifax "no record / insufficient" | No furnisher matched | `INSUFFICIENT DATA` |
| UCC count 0 on a bureau | Bureau public-record depth varies | **Not proof of no filings.** Point 18 needs the SOS search |
| Inquiries 0 | Normal; few commercial pulls report | Neutral |

---

## 2. Audit-point rules (11, 12, 13, 18, 19)

**Status precedence (all points):** ACTION REQUIRED > PENDING-NEED DOCUMENT > NEEDS IMPROVEMENT > PASS. N/A is set only by the stated N/A rule. The one-line finding lists the controlling reason first and secondary findings after it. A PENDING point with a bureau that returned no file is labeled **"PENDING – INSUFFICIENT DATA"**: the report was obtained, but the bureau could not score or identify the business. Nothing is inferred from other bureaus.
**Freshness:** a commercial report counts as "on file" only if `audit_date − report_date ≤ 90` (`COMM_REPORT_MAX_AGE=90`). At 91 days or more it counts as missing (PENDING), with "re-pull".

### Point 11: Business Credit Bureaus
**Required sources:** Experian and D&B. Equifax Commercial is required when the goal includes BL, BT, SBA, EQB or OL (banks and SBFE-linked lenders use it). Otherwise it is advisory.

| Status | Logic |
|---|---|
| **ACTION REQUIRED** | Any of: (a) Intelliscore V2 ≤25 or V3 ≤660 (`IS_AR_V2=25`, `IS_AR_V3=660`); (b) PAYDEX generated and <70; (c) D&B Failure or Delinquency class 4–5; (d) Equifax BCRS <450 or Payment Index <70 [EXP]; (e) any **critical identity defect** at any bureau (§3: legal name blank or different, wrong entity type, non-master or stale address, wrong state, TIN conflict); (f) open bankruptcy, judgment, tax lien or commercial collection on any commercial file; (g) bureau status "out of business/inactive" for an operating company |
| **PENDING-NEED DOCUMENT** | No AR trigger, but a required report is missing or stale, or a required bureau returned INSUFFICIENT DATA |
| **NEEDS IMPROVEMENT** | Any of: Intelliscore V2 26–75 / V3 661–720; FSR class 3 or worse; PAYDEX 70–79, or PAYDEX not generated with Experian scored; D&B class 3; Equifax BCRS 450–555 or Payment Index 70–89; **material identity defects** only (phone, NAICS/SIC, years in business, sales, employees, website blank or understated) |
| **PASS** | All required reports ≤90 days old; Intelliscore V2 ≥76 or V3 ≥721; PAYDEX ≥80; D&B Failure and Delinquency class ≤2; Equifax (if required) BCRS ≥556 and Payment Index ≥90; identity identical to Master Identity on all critical and material fields |
| **N/A** | Only for a sole proprietor with no EIN whose goal is limited to PC or PL. Shown as "N/A – personal-credit-only engagement" |

Scoring note: a business with no file at all is PENDING (obtain reports), not ACTION REQUIRED. The defect is the absence of data, not bad data.

### Point 12: Vendor / Payment Experiences
**Derived fields:** `trades_exp_active` (Experian active), `trades_dnb` (D&B experiences), `suppliers_dnb` (distinct furnishers), `trades_efx`, `distinct_trades_all` (de-duplicated by category + terms + open date ±31 days + high credit ±10%), `oldest_trade_months`, `wDBT` (dollar-weighted DBT across bureaus), `max_dbt_bucket`, `rev_util_comm` = Σ balance / Σ limit (or recent high credit when no limit is shown) on revolving commercial trades.

| Status | Logic |
|---|---|
| **ACTION REQUIRED** | `distinct_trades_all ≤1`; or any trade 61+ DBT, collection or charge-off; or `wDBT >15`; or `rev_util_comm ≥90%` across ≥2 trades |
| **PENDING-NEED DOCUMENT** | Experian or D&B report missing or stale |
| **NEEDS IMPROVEMENT** | `distinct_trades_all` 2–4; or fewer than 3 active trades at Experian, or fewer than 3 experiences from 2 suppliers at D&B; or `oldest_trade_months <6`; or `wDBT` 1–15; or any 1–30 DBT bucket >0; or `rev_util_comm` 50–89%; or zero net-terms vendor trades (financial-only file); or Experian factor text "limited accounts/ limited active accounts" present |
| **PASS** | ≥3 active reporting trades at **both** Experian and D&B (D&B ≥2 suppliers), ≥5 distinct overall, oldest ≥6 months, `wDBT = 0` (≤2 tolerated if transient, [EXP]), `rev_util_comm <50%`, PAYDEX generated |
| **N/A** | Same rule as Point 11 |

### Point 13: LexisNexis

| Status | Logic |
|---|---|
| **ACTION REQUIRED** | The report links a second TIN, an unrelated business, or unrelated principals to the EIN or owner; or shows an undisclosed lien, judgment or bankruptcy; or shows an address set that conflicts with the Master Identity in a way the client cannot document |
| **PENDING-NEED DOCUMENT** | Not obtained, or older than 90 days. If the bureau answered "no record found": **PENDING – INSUFFICIENT DATA** |
| **NEEDS IMPROVEMENT** | One identity, but stale/historic addresses, name variants or phone variants appear without conflict, or prior-officer linkage that needs a governance document on file |
| **PASS** | Obtained ≤90 days; one business identity; every address explained (current = master, others documented as prior); liens/UCC/public records match Point 18; no duplicate or conflicting records |
| **N/A** | Never (only the Point 11 N/A rule) |

### Point 18: Public Records / UCC
**Required source:** a SOS UCC debtor search in the state of formation, plus any state where the company has a principal place of business if it was ever a different entity type. Searches cover exact legal name and every prior legal name. Bureau UCC sections are corroborating only.

Each open filing is classified (see §4) as SPECIFIC, BLANKET, ACCOUNTS-INCLUSIVE, MCA/FACTOR, or UNMATCHED.

| Status | Logic |
|---|---|
| **ACTION REQUIRED** | Any of: an UNMATCHED filing (secured party is not on the intake debt schedule); an MCA/FACTOR filing (also HR-C04); a filing for debt the client says is paid with no termination (secured party must file UCC-3; HR-C05); a debtor-name error on a filing; an open judgment, tax lien, suit or bankruptcy on any source; a SOS search showing a filing against a different entity with the same name that the bureaus attach to this file |
| **PENDING-NEED DOCUMENT** | SOS search not completed, or original financing statements not reviewed (collateral text unknown) |
| **NEEDS IMPROVEMENT** | All filings matched to disclosed, current debt, but at least one is BLANKET or ACCOUNTS-INCLUSIVE **and** the funding goal includes a lien-taking product (BL, BT, SBA, EQB/EQA with blanket requirement, FAC, secured OL). Wording: "legitimate filings; not a defect; constrains new secured borrowing" |
| **PASS** | No open filings; or all open filings matched to disclosed debt with collateral understood, and either they are SPECIFIC (e.g., the financed equipment) or the goal uses only non-lien products |
| **N/A** | Never. A sole proprietor's UCC filings are searched under the owner's name |

PASS STANDARD text (from the gold-standard report pattern): "Every open filing is in the funding file, with secured party and collateral scope understood. The point fully passes once the collateral position has been addressed with the prospective secured lender, or the strategy is limited to products that do not take a lien in business assets."

### Point 19: Duplicate Business Files
See §5 for detection. The status uses the signals there.

| Status | Logic |
|---|---|
| **ACTION REQUIRED** | Confirmed duplicate: ≥2 BINs, ≥2 D-U-N-S or ≥2 Equifax IDs at the same bureau for the same legal entity at the same location (not a legitimate branch/HQ linkage), or tradelines/UCCs attached to a file under a different TIN or entity type |
| **PENDING-NEED DOCUMENT** | Any **risk factor** (§5.2) is present and the explicit duplicate search is not complete at every bureau; or a required bureau has not been obtained |
| **NEEDS IMPROVEMENT** | Search complete and one file per bureau, but legacy records remain (e.g., old-address sub-record, trade-style file not linked) and need a linkage/update request |
| **PASS** | One file per bureau, confirmed by searches under every name variant, EIN, master and prior addresses and phone; identifiers recorded in the funding file |
| **N/A** | Same rule as Point 11 |

**Do not overstate:** contradictory data across bureaus is a Point 20 consistency issue, **not** evidence of a duplicate. The report must not say "duplicate" until a second file is found.

---

## 3. Bureau-card content rules

One card each for Experian, D&B, Equifax Commercial, SBFE/SBSS and LexisNexis, followed by a UCC/public-record card. Bureaus are reviewed separately. Header text: "These bureaus do not share data; a correction at one does not reach the others."

**Card layout (fixed order):**
1. **Header:** bureau, file ID (masked to the last 4 in any funder-facing text), report date, card status (point-11 logic applied to that bureau alone).
2. **Headline metrics (max 5 tiles):**
   - EXP: Intelliscore (with version), FSR, active trades, current %/DBT, UCC count.
   - DNB: PAYDEX (or "Not generated"), Failure class/percentile, Delinquency class/percentile, Max Credit Recommendation, total experiences.
   - EFX: BCRS, Failure Score, Payment Index, trades, or one tile "INSUFFICIENT DATA".
   - LNX: identities linked, addresses, liens/UCC/records, or "Not obtained".
3. **Tradeline table:** category, terms, recent high credit, balance, current %, DBT, last reported. Show the computed balance-to-high-credit ratio next to the bureau's figure when they differ by >2 points ("computes to ~X%; bureau displays Y%; either indicates…").
4. **Identity comparison table:** field | bureau reports | Master Identity | TLA assessment.

   | Assessment code | Meaning | Severity |
   |---|---|---|
   | MATCH | Identical | — |
   | FORMAT VARIANT | Case, punctuation, "LLC" vs "L.L.C.", Suite vs Ste | None; not a correction |
   | BLANK | Field empty | Critical if name/address/entity type; else material |
   | STALE | A former value (old address, former officer) | Critical for address; material otherwise |
   | CONFLICT | A different value with no documentary support | Critical |
   | UNDERSTATED | Sales/employees/years below documented value | Material |
   | VERIFY | Can't be resolved from documents on file | Human review if critical |

   Critical fields: legal name, entity type, state of formation, street address, TIN. Material: phone, NAICS/SIC, years in business/incorporation year, sales, employees, website.
5. **Corrections required:** bullets, each naming the field, the supporting document ("Certificate of Formation", "IRS CP 575 / 147C", "filed tax return"), and the channel.
6. **What's clean:** an explicit list ("no bankruptcies, judgments, liens, collections or inquiries"). It is shown only for sections the bureau actually returned.
7. **Channel line:** from §0, with expected turnaround.
8. **Score-factor notes:** reason codes quoted verbatim, with a neutral reading. Example: "'Leadership changed recently' may be consistent with a documented management change; TLA cannot determine the exact data used. Keep governance documents in the funding file. This is not a dispute item."

**Card hard rules:** never infer a score at one bureau from another. Never show an SBSS estimate. Never present the Equifax Canada scale. Corrections are always sequenced **identity first, then depth** (new trades attach to whatever record the furnisher matches).

---

## 4. UCC and public-record interpretation rules

| Rule | Spec |
|---|---|
| U-1 Not a defect | A UCC-1 is a notice filing. A legitimate filing matched to disclosed debt is never called "derogatory," "negative" or "adverse." Wording: "consistent with the existing credit relationship." |
| U-2 Classification | **SPECIFIC:** collateral names identified goods (VIN, serial number, "equipment financed under agreement #"). **BLANKET:** "all assets," or an all-categories list (inventory, accounts, equipment, general intangibles, chattel paper, deposit accounts), with "now owned or hereafter acquired." **ACCOUNTS-INCLUSIVE:** "accounts," "receivables," "payment intangibles" or "future receipts" appear. **MCA/FACTOR:** see U-5. **UNMATCHED:** the secured party can't be tied to an item on the debt schedule. |
| U-3 Product effect | BLANKET or ACCOUNTS-INCLUSIVE → FAC and A/R lines need a payoff, subordination or intercreditor agreement (flag in those lanes; "receivables should not be presented as unencumbered"). New bank LOC/term/SBA: the lender evaluates lien position. SBA lenders commonly take available business-asset liens [DP]. EQB/EQA: purchase-money security interests in the new equipment are usually workable [DP]. BC, PC, PL and unsecured OL: little direct effect; the debt still counts in DSCR/PBR. |
| U-4 Existing lienholder first | If an open blanket lien belongs to a bank, the action plan lists "evaluate the existing relationship bank first" before adding a new secured lender. |
| U-5 MCA tell-tales | Secured party name matches the MCA/RBF funder alias table, or contains "Funding," "Capital," "Advance," "Merchant," "Receivables" **and** the collateral text says "future receipts," "receivables sold/purchased," "all accounts... whether now existing or hereafter arising" with a purchase recital; or a filing by a known UCC-filing service acting as representative; or ≥2 filings within 6 months by different non-bank parties. Result: MCA/FACTOR class, Point 18 AR, HR-C04, and MCA position-stacking checks (RULEBOOK HR-39, SA rules). Wording: "appears consistent with a receivables-purchase or advance; please confirm with the agreement." |
| U-6 Paid but open | If the client says the debt is paid, the action is: "request that the secured party file a UCC-3 termination" (UCC §9-513 sets the secured party's duty once the obligation is satisfied and the debtor demands it). The client doesn't file a termination itself. |
| U-7 Lapse | Filings lapse 5 years after filing unless continued (§9-515). Lapsed filings are informational only. A continuation filed in the 6-month window keeps the filing open. |
| U-8 Priority | TLA never determines priority, perfection or subordination. Standard text: "Those matters are determined by the applicable lenders and, where necessary, legal counsel." |
| U-9 Debtor address | Different debtor addresses across filings → note for Point 15/20 (master address), not a UCC defect. |
| U-10 Bureau vs state | Bureau UCC counts that differ from the SOS search are "differing public-record depth," not an error by either. |
| U-11 Judgments / liens / suits | From the SOS/court/LexisNexis/bureau commercial sections. Open business judgment or tax lien → Point 18 AR + RULEBOOK HR-32/HR-38 as relevant. Satisfied → NI with "keep satisfaction document in the funding file." |

---

## 5. Duplicate / fragmented file detection

### 5.1 Hard signals (confirm a duplicate)
- D-1: Two file IDs at one bureau whose normalized legal name (stripped of punctuation and entity suffix) matches ≥0.90 **and** share the EIN, phone, or street address.
- D-2: Same entity under two entity types (e.g., "Corporation" file and "LLC" file) at one bureau.
- D-3: Tradelines or UCCs the client recognizes appear on a file other than the primary file.
- D-4: A D&B family tree shows an unexplained "branch" at the same address, or an HQ file with no linkage. Legitimate branches with real separate locations are **not** duplicates.

### 5.2 Risk factors (require an explicit search before PASS)
Legal-name change or amendment · entity-type conversion or a mismatch between SOS and a bureau · prior manager, member or registered address in another state · ≥2 addresses in 5 years · DBA or trade-style use · a second TIN on any bank, tax or bureau document · client unaware of the BIN or D-U-N-S at intake · bureau sales/years figures that look like a different company · prior sole-proprietor operation of the same business.

### 5.3 Search protocol (the action item text)
At each bureau, search by every legal name and DBA variant, the EIN, the master and prior addresses, and the phone. Record every file ID returned. Request a merge or linkage (Experian Commercial Relations; D&B Profile Manager; Equifax Commercial Research Request) **only after** the Master Identity is locked.

---

## 6. Internal-inconsistency detection

| ID | Check | Flag text (compliance-safe) |
|---|---|---|
| IC-01 | A trade shows DBT >0 while another section shows "no payment history"/"no days-within-terms data" | "These two presentations appear internally inconsistent and should be verified with [bureau]. If the DBT marker is inaccurate, submit a supported dispute. Accurate information should not be disputed." |
| IC-02 | PAYDEX blank while ≥3 experiences from ≥2 suppliers are listed | "Verify why a PAYDEX was not generated." |
| IC-03 | Years in business = 0, or incorporation year ≠ SOS formation year | UNDERSTATED / CONFLICT → identity correction (not a dispute) |
| IC-04 | Sales or employees differ >50% between bureaus, or from the tax return | UNDERSTATED / VERIFY |
| IC-05 | Balance > recent high credit, or the bureau's current %/utilization differs >2 pts from computed | "Displayed and computed figures differ; either indicates [reading]." |
| IC-06 | Summary counts (trades, UCC, inquiries, derogatories) ≠ detail rows | Extraction check first. If still unequal, VERIFY |
| IC-07 | Risk factor cites an industry while NAICS/SIC are blank | "Model applied an industry default; supply the correct codes." |
| IC-08 | "% current" = 100 while a DBT bucket >0 on the same bureau | VERIFY |
| IC-09 | Bureau status "inactive/out of business" vs active SOS and current deposits | Critical; HR-C08 |
| IC-10 | Bureau A reports a trade late, bureau B reports a trade current | **Not an inconsistency.** "Two bureaus may be reporting different underlying trade experiences; validate the specific furnisher and account behind each before assuming either is wrong." |

All IC flags follow RULEBOOK G-02 and G-17: "appears inconsistent; please verify." Never "is wrong," "violation" or "illegal." Note: commercial reports aren't FCRA consumer reports, so business disputes rest on bureau policy, not FCRA §611 deadlines. Wording uses "generally about 30 days" and never "legally required."

---

## 7. Action-plan library (commercial)

| ID | Trigger | Remedy (client-facing basis) | Timeline | Expected impact |
|---|---|---|---|---|
| AP-C01 | Any critical identity defect | Lock the Master Identity (legal name per SOS, entity type, formation state, master address, business phone, EIN), then submit updates: Experian BusinessCreditFacts, D&B Profile Manager, Equifax Research Request, LexisNexis. Attach formation documents and the IRS EIN notice | 2–6 weeks for submissions; ~30 days per bureau to post | Prerequisite for every other item |
| AP-C02 | No D-U-N-S / BIN known | Look up existing files first (avoid creating a duplicate); request a D-U-N-S only if none exists (free) | 1–30 days | Point 19 protection |
| AP-C03 | Firmographics understated | After identity lock, submit tax-return-supported sales, employees, NAICS/SIC through the officer channels | 30–60 days | Removes model defaults |
| AP-C04 | `distinct_trades_all <5` or PAYDEX not generated | Open 2–3 net-terms vendor accounts in the exact legal name and master address, **for supplies the business actually uses**. Confirm in writing that the vendor reports, and to which bureau. Pay early or on terms | First reports usually 30–90 days after the first paid invoice [DP]. PAYDEX needs ≥3 experiences from ≥2 suppliers [DP]; plan 60–120 days | Generates PAYDEX; lifts "limited accounts" factors |
| AP-C05 | Financial-only file | Add a business card or fleet/telecom account that reports commercially; ask the issuer which commercial bureaus it reports to (practice varies, [DP]) | 60–120 days | Depth and mix |
| AP-C06 | PAYDEX 70–79 or wDBT 1–15 | Pay vendor invoices before the due date. PAYDEX rewards early payment: above 80 = paid before terms | 60–90 days of new experiences | PAYDEX/DBT |
| AP-C07 | rev_util_comm ≥50% | Pay down revolving commercial balances before the reporting date | 1–2 cycles | Intelliscore utilization factor |
| AP-C08 | Equifax/LexisNexis missing | Request the disclosure through the channels in §0 | 2–4 weeks | Unblocks Points 11/13/19 |
| AP-C09 | Paid debt with open UCC | Ask the secured party for a UCC-3 termination and keep the payoff letter | 20–30 days [DP] | Point 18 |
| AP-C10 | Blanket/Accounts lien + secured goal | Talk to the existing lienholder first; for a new lender, prepare the debt schedule and lien list up front | Deal-dependent | Product fit |
| AP-C11 | Duplicate confirmed | Merge/link request at the bureau after AP-C01 | 30–60 days | Point 19 |

**Vendor reporting data points (`vendor_table`, [DP], must carry `verified_on`, re-verified quarterly, never shown as guaranteed):** The table holds vendor, bureaus reported to (as stated by the vendor or community sources), approval requirements (D-U-N-S, EIN, minimum age, deposit), minimum purchase, and whether there is a membership fee. Commonly cited starter vendors include large office/industrial suppliers that reportedly report to D&B and/or Experian. Equifax-reporting vendors are fewer. The report says: "Reporting practices change; confirm with the vendor before relying on it."

**Sequencing rule:** AP-C01 → AP-C02/C08 → AP-C03 → AP-C04/C05 → AP-C06/C07. The engine blocks AP-C04 from being listed as a "now" action while any critical identity defect is open.

**Prohibited content (adds to G-01 to G-13):**
- C-G1: No buying, renting or "adding" business tradelines, and no "tradeline packages" to represent payment history that the business did not generate. Paid "reporting memberships" with no real purchasing need are labeled "low value; lenders may discount" and are never required.
- C-G2: No shelf or aged-corporation strategies. Time in business is measured from when **this owner's business began operating** (RULEBOOK AP-49, HR-27). An acquired older entity must be disclosed as an acquisition, with its prior history attributed truthfully.
- C-G3: No new EIN, new entity or new D-U-N-S created to escape existing negative business history ("file segregation"). Escalate as HR-28.
- C-G4: No promise of a PAYDEX, Intelliscore or approval number or date. Use "typically," "generally" and ranges.
- C-G5: Dispute language only per IC flags: "verify; if inaccurate, submit a supported dispute; accurate information should not be disputed."

---

## 8. Human-review triggers (commercial)

| ID | Trigger | Sev |
|---|---|---|
| HR-C01 | A second TIN appears on any bureau, bank or tax document | BP: all business lanes |
| HR-C02 | An entity-type, formation-state or legal-name conflict that survives document review | AD |
| HR-C03 | Open business bankruptcy, judgment, tax lien or suit on any commercial source | BP: SBA, BT, BL, EQB; AD: alt |
| HR-C04 | Any MCA/FACTOR UCC (U-5), or ≥2 non-bank UCCs within 6 months | AD (+ RULEBOOK HR-39/40 checks) |
| HR-C05 | An UNMATCHED UCC, or a "paid" debt with an open UCC | AD |
| HR-C06 | Client doesn't recognize a commercial tradeline, inquiry or UCC | AD; possible business identity theft → stop building until resolved |
| HR-C07 | Shelf/aged entity, recent ownership change of an older entity, or stated TIB > operating history by >6 months | AD (compliance) |
| HR-C08 | Bureau shows "out of business/inactive," or SOS status not active | BP: all business lanes |
| HR-C09 | Client asks for tradeline purchase, a new EIN/entity to escape history, or bulk disputes of accurate items | BA (= HR-28) |
| HR-C10 | Commercial collection placement or charge-off by a lender | AD (= HR-41) |
| HR-C11 | Bureau sales figure exceeds documented revenue by >25% | AD (possible misreported self-supplied data; never use the higher figure) |
| HR-C12 | Commercial extraction confidence <0.85 on scores or the identity block, or summary/detail mismatch after re-extraction | Point 11/12 → PENDING; reviewer must confirm |
| HR-C13 | LexisNexis links unrelated individuals to the owner or EIN | AD |

---

## 9. Plain-English client explanations

Each tile carries "What this is / What lenders do with it / What good looks like." Text below is the default copy.

**Experian Business (the bureau).** Experian keeps a business credit file built mostly from what your suppliers, card issuers and lenders report about how you pay, plus public records and company details. Many online lenders, card issuers and suppliers check it. It is completely separate from your personal Experian file.

**Intelliscore Plus.** *What it is:* Experian's main business score. It estimates how likely your business is to pay seriously late over the next year. Version 2 runs 1–100 and version 3 runs 300–850; higher is better. *What lenders do with it:* screen applications and set limits. *What good looks like:* 76+ on version 2, or 721+ on version 3.

**Financial Stability Risk Score.** *What it is:* Experian's estimate of the chance your business fails to meet its obligations or goes bankrupt in the next year, shown as a 1–100 score and a 1–5 risk class. *What lenders do with it:* use it alongside Intelliscore, mostly for larger or longer-term credit. *What good looks like:* risk class 1–2 (a score of about 31+).

**Days Beyond Terms (DBT).** *What it is:* the average number of days your business pays after the due date, weighted by dollar amount. *What lenders do with it:* treat it as a quick read on payment habits. *What good looks like:* 0. Even a few days late shows up.

**Dun & Bradstreet (the bureau).** D&B identifies your business by a D-U-N-S number and gathers payment experiences, mainly from suppliers. Banks, large vendors and government buyers often look here. You can view and update your basic company information for free in D&B's Profile Manager.

**PAYDEX.** *What it is:* a 1–100 score of how promptly you pay suppliers. 80 means "on time" and higher means "early." It appears only once at least three payment experiences from two suppliers are on file. *What lenders do with it:* vendors use it to set terms; lenders use it as a payment-habit check. *What good looks like:* 80 or higher. A blank PAYDEX means "not enough history yet," not "bad."

**D&B Failure Score.** *What it is:* D&B's estimate of the chance your business closes or seeks legal relief from creditors in the next year, shown as a class from 1 (lowest risk) to 5 and a 1–100 percentile. *What lenders do with it:* a stability screen. *What good looks like:* class 1–2.

**D&B Delinquency Predictor.** *What it is:* the chance your business pays severely late in the next year, using the same 1–5 class (1 is best) and percentile. *What lenders do with it:* help set credit limits and terms. *What good looks like:* class 1–2.

**Equifax Business (the bureau).** Equifax keeps a business file that draws heavily on reporting from banks and card issuers, including many members of the Small Business Financial Exchange. Banks and SBA lenders often check it. It can be empty even when your other files aren't.

**Equifax Business Credit Risk Score.** *What it is:* a 101–992 score estimating the chance your business goes 90+ days late in the next two years. *What lenders do with it:* screen bank and card applications. *What good looks like:* commonly cited as above about 556.

**Equifax Business Failure Score.** *What it is:* a 1,000–1,880 score estimating the chance your business fails in the next year. *What lenders do with it:* a stability check. *What good looks like:* commonly cited as above about 1,315.

**Equifax Payment Index.** *What it is:* a 1–100 measure of how on time your business has paid. *What lenders do with it:* a quick payment-habit check. *What good looks like:* 90 or higher, which means paid as agreed.

**SBFE and FICO SBSS.** *What it is:* SBFE is a lender-only exchange of small-business loan and card payment data. SBSS is a FICO score (0–300) that a lender generates at application from personal credit, business credit and application data. *What lenders do with it:* some banks still use it in their own decisions; the SBA stopped using it for 7(a) Small loans on March 1, 2026. *What good looks like:* it can't be ordered or previewed in advance. The best lever is a strong, accurate business and personal file.

**LexisNexis.** *What it is:* a large public-records and identity database that links businesses, owners, addresses, liens and filings. *What lenders do with it:* verify that your business is who it says it is and look for hidden records or duplicates. *What good looks like:* one clean business identity, current addresses, and no unexplained records.

**UCC filings.** *What it is:* a public notice a lender files with the state when a loan is secured by business assets. *What lenders do with it:* see what is already pledged before they lend against the same assets. *What good looks like:* every filing matches a loan you know about. Broad "all assets" filings are normal with bank loans, but a new secured lender will need to work around them.

---

## Sources
- Experian Intelliscore Plus V3 and score bands: https://www.experian.com/business-information/credit-risk-management.html ; https://www.nav.com/business-credit-scores/experian-intelliscore-plus/
- Intelliscore V2 and FSR risk classes: https://creditplus.com/knowledge-hub/blogs/business-data-portfolio-scoring-the-meaning-behind-the-numbers/ ; https://www.experian.com/business-information/financial-stability-risk-score
- Experian business disputes and contacts: https://www.experian.com/small-business/business-credit-information ; https://www.experian.com/business-information/businessiq-support
- D&B PAYDEX, Failure and Delinquency scales: https://www.dnb.com/en-us/smb/resources/credit-scores/failure-score.html ; https://www.dnb.com/en-us/smb/resources/credit-scores/delinquency-predictor-score.html ; https://www.dnb.com/en-us/smb/resources/credit-scores/db-credit-scores-ratings.html
- PAYDEX minimum experiences [DP]: https://creditstrong.com/paydex-score
- D-U-N-S Profile Manager: https://www.dnb.com/en-us/smb/duns/duns-manager.html ; https://www.dnb.com/en-us/utilities/credit-insights-product-terms.html
- Equifax US scores [DP]: https://www.lendingtree.com/business/equifax-small-business/ ; https://creditstrong.com/what-is-a-good-equifax-business-credit-score
- Equifax commercial disclosure email [DP]: https://www.lendingtree.com/business/equifax-small-business/
- FICO SBSS range and SBFE: https://www.nav.com/business-credit-scores/fico-sbss/
- SBSS sunset: https://www.naggl.org/wp-content/uploads/2026/05/5000-875701.pdf ; https://www.naggl.org/wp-content/uploads/2026/05/5000-876777.pdf ; https://www.experian.com/blogs/business-information/2026/07/22/the-sba-sbss-sunset/
- LexisNexis consumer center address: https://consumer.risk.lexisnexis.com/
- UCC Article 9 (§§9-307, 9-513, 9-515, 9-518): Uniform Commercial Code as enacted by each state.
