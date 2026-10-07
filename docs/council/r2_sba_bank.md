# R2 — SBA & Commercial Bank Underwriter: Cross-Examination and Revision

## 1. Challenges

### Card broker (r1_card_broker.md)
1. **§3A caps ignore ability to pay.** "1.0 × income + 0.25 × revenue" does not test cash flow. A $90k earner with no other debt could show $90k+ of new limits.
   - **Replace with a payment check.** New limits × 50% expected utilization × 3% imputed payment, plus existing monthly debt, must stay ≤ 45% of gross monthly income. Whichever cap is lower controls.
   - For personal cards, issuers are legally required to consider ability to pay (Reg Z §1026.51).
2. **K6 judgment and tax-lien knock-out reads from the bureau report.** Compliance (§1.5) is right that judgments and liens have been off consumer files since 2017–2018. If K6 is sourced from the report, it will almost never fire.
   - **Source it from intake attestation.** If a judgment or lien does appear in a parsed report, treat it as a data-quality flag for human review.
3. **§6 sequencing ("apply same-day so new accounts don't show on later pulls") is incomplete.** Issuer-to-issuer ordering is legitimate. But nothing in it protects a pending bank or SBA deal. Banks re-pull credit before closing. Five new PG cards between approval and funding can kill or re-size the loan.
   - **Add a hard sequencing rule:** no card applications while any bank, SBA or term-loan request is pending or within 30 days of its closing (§2 below).
4. **D (fintech LOC) knock-outs (FICO 600, TIB 6 months) are labeled "fintech/bank LOC."** For a bank LOC they are far too loose. Banks want 24+ months TIB, 660–680+ FICO and tax returns.
   - **Split the product:** "Fintech LOC" stays with the broker and alt lending. "Bank LOC" uses my K7/K8/K9/K10.
5. **§2 "3-bureau composite = average" works for cards** because issuers pull one bureau. It must not feed bank, SBA or mortgage logic, which use the median score of the weakest guarantor.

### Alt lending (r1_alt_lending.md)
1. **§3 online-term payment cap of 10–15% of monthly deposits ignores margin.** A 6%-margin restaurant paying 12% of revenue in debt service is underwater from day one.
   - **When tax returns exist,** also require new payments plus existing payments ≤ 50% of monthly EBITDA (roughly a DSCR of 2.0 on short-term debt, because there is no amortization cushion). Use the lower cap.
2. **§7 APR-equivalent ≈ (factor − 1) ÷ term × 2 is a rough approximation that the report will print as fact.**
   - **Compute the IRR from the actual debit schedule** (daily or weekly count, holdback, fees). This is deterministic and easy. The ×2 shortcut can be off by 20–40 points on short terms.
3. **KO-ALT-5 "51% ownership" conflicts with SBA.** Since Mar 1, 2026, 100% of owners and guarantors must be U.S. citizens or nationals living in the U.S. (Procedural Notice 5000-876626). The 51% rule is fine for alt products, but the engine must not reuse it as a general eligibility test.
4. **HR-1 (deposits > 1.5× return revenue ÷ 12) is too loose.** A 50% gap between bank deposits and tax-reported revenue is exactly the pattern that sinks SBA files and suggests under-reported taxes.
   - Use **one shared 20% mismatch threshold** (§2).
5. **Equipment.** My 600 FICO floor and their 550 floor are both right, for different lanes. Model equipment as **one product with two lanes**: Bank/captive (≥ 660 preferred, 600 floor, 24 months TIB) and Non-bank (550 floor). Don't let the two floors contradict each other in the report.

### Compliance (r1_compliance.md)
1. **§7 "SBSS minimum currently 165 … under SOP 50 10 8" is outdated.** SBA stopped using SBSS for 7(a) Small loans numbered on or after **Mar 1, 2026**. 165 was the pre-sunset minimum. Lenders now run full credit analysis with **DSCR ≥ 1.10x** and may use internal models that don't rely solely on consumer scores (SBA notices 5000-875701 and 5000-876777, via NAGGL; Experian, 7/22/2026). **Remove any SBSS reference from the config.**
2. **HR #11 (new PG exposure > $100k or > 50% of income) would fire on every SBA loan.** SBA requires an unlimited guaranty from every 20%+ owner, and repayment comes from business cash flow tested by DSCR.
   - **Apply the trigger to unsecured, cash-flow-unverified PG exposure only:** cards, fintech LOC, personal loans and MCA guaranties. Exempt loans that have passed a DSCR test.
3. **The §2 paid-collection base of 35 under FICO 8 is right for cards and wrong for banks.** Manual bank and SBA underwriting gives near-zero weight to a paid collection older than 24 months that comes with an explanation letter.
   - Keep the shared severity × DOFD decay. Let **each product apply its own consumption multiplier**: bank/SBA × 0.5 for paid items 24+ months old.
4. **The §1.2 staleness rule covers credit reports only.** For bank and SBA files, financial data goes stale too.
   - If the last fiscal year-end is more than 6 months old, require **interim YTD financials**.
   - If the most recent filed return is more than 18 months old, block the DSCR estimate.

## 2. Conflicts to resolve

| Issue | Position | Evidence |
|---|---|---|
| **Order of card stacking vs bank/SBA** | **Bank/SBA/conventional term → fintech LOC/term → card stack → MCA last.** No card or credit applications from the bank application until 30 days after funding. Alt lending (§8.4) agrees. The broker's issuer ordering applies *inside* the stack step. | Banks re-verify credit before closing. New PG card debt enters global DSCR at 3% of balance. |
| **SBSS** | Retired. No SBSS gate or estimate. Model DSCR ≥ 1.10 (SBA floor) and 1.15 (our conservative target), plus lender FICO overlays as config. | SBA notices 5000-875701 and 5000-876777 |
| **AU tradelines** | All four proposals agree to discount them. Rule: **scores are used as reported (they include AU accounts), but depth, highest limit, utilization and limit-based estimates use primary and joint accounts only.** Flag "score may be AU-inflated" when AU limits are ≥ 30% of total revolving limits. Purchased-looking AU accounts go to human review. Never advise buying AU slots. | Manual underwriting practice; compliance §5.1 |
| **Paid collections** | Shared severity with DOFD decay. Product multipliers: cards use FICO 8 treatment (paid still counts). Bank/SBA discount paid items 24+ months old. Never recommend pay-for-delete or disputing accurate items. | FICO 8 vs 9/10 treatment (compliance §2) |
| **Score aggregation** | Engine outputs per-bureau, median-of-3, and lowest-guarantor median. Cards use the target bureau. Bank, SBA, mortgage and alt lending use the **lowest guarantor's median**. | Standard bank and mortgage practice |
| **Judgments, tax liens, CAIVRS** | Intake attestation only, plus human review. Never infer "none" from a clean report. | NCAP; CAIVRS is lender-access only |
| **TIB definition** | Store three values (shared engine #11). Bank and SBA use *years of filed business returns showing revenue*. Alt uses *months since first deposits*. Cards use formation date. | — |
| **Revenue mismatch thresholds** (15% / 20% / 1.5×) | One rule: any two documented or stated revenue sources differing by more than **20%** go to human review, and scoring uses the **lower** figure. | Misrepresentation risk (18 U.S.C. §1014) |

## 3. Concessions (changes to r1_sba_bank)
1. **Derogatories.** I replace my ad-hoc derogatory bands with compliance's severity × DOFD decay, consumed through bank/SBA multipliers. Age is measured from DOFD, not date of last activity.
2. **Medical collections.** Unpaid medical under $500 should not appear on reports at all, so it becomes a data-quality flag, not a penalty. Unpaid medical of $500+ gets a light bank penalty (base × 0.5).
3. **Criminal-history question.** My Q11 is limited to the SBA Form 1919 scope: currently incarcerated, on parole or probation, or under indictment. No broader history questions. Any yes goes to human review (H1).
4. **Inquiries.** De-duplication of rate-shopping clusters applies to the *scoring* factor only. Raw per-bureau counts stay visible for velocity and human review. (Broker §8.2 is right.)
5. **Bank LOC deposit data.** Add the optional bank-statement upload (alt §4) to the bank LOC branch. Banks do weigh average balances and overdrafts on LOC renewals. The statement data reuses the alt-lending metrics.
6. **Equipment** moves to the two-lane model (§1 alt #5).
7. **Unknown score model or a stale report** forces low confidence on my K7 FICO knock-out. In that case it becomes human review instead of an automatic fail.
8. **K2 tax lien** is sourced from intake, not the report.

## 4. Shared-engine recommendations (compute once, every product consumes)

1. **Canonical tradeline set.** Use compliance §1.3 merge keys and thresholds. Each tradeline gets `owner_type` (primary / joint / AU / business-reported), `bureaus_present`, and DOFD. Remove OC + collector double counts (§1.4).
2. **Scores.** Per bureau, with model and date. Derived: median-of-3 (or the lower of 2), lowest-guarantor median, and target-bureau score. A VantageScore is never treated as a FICO.
3. **Utilization.**
   - Aggregate = Σ balances ÷ Σ limits across open primary and joint revolvers that have a limit. Exclude AU accounts and no-preset-limit charge cards.
   - Also compute max single-card utilization and an "as-reported including AU" figure for context.
   - Per bureau, plus merged using each tradeline's latest-reported balance.
4. **Inquiries.** Per bureau over 3/6/12/24 months. Two versions: *raw* (velocity) and *scoring* (mortgage, auto and student inquiries within 14 days counted as one).
5. **New accounts.** Counted by open date on the merged set over 6/12/24 months. Primary and AU counted separately (5/24 counts AU).
6. **Derogatory load.** Compliance §2 severity × DOFD decay, with aggregate = max + 0.5 × 2nd + 0.25 × rest. Each product applies its own multipliers and hard stops.
7. **Late-payment summary.** Most recent late (severity, months since), and counts within 12 and 24 months, with mortgage lates tracked separately.
8. **Depth.** Oldest primary account, primary average account age, number of primary revolvers, highest primary limit, and whether installment or mortgage history exists.
9. **Monthly personal debt obligations.** Use the reported payment. For revolvers without one, use max(3% of balance, $25). 0% promotional balances are included. Deferred or IDR $0 student loans use 1% of balance. This feeds card DTI, personal-loan DTI and bank global DSCR.
10. **Revenue (three fields).** Tax-return gross receipts, true bank deposits, and stated revenue. *Underwriting revenue* = the lower of the documented sources. Use stated × 0.8 only if nothing is documented. The 20% mismatch rule applies.
11. **Business history.** Formation date, first-deposit date, number of filed business returns showing revenue.
12. **Business debt positions.** Count of MCA positions, daily/weekly debit burden as a percentage of revenue, term-debt annual debt service, and whether a UCC blanket lien exists. Shared by DSCR, alt affordability and steer-away rules.
13. **Integrity gate.** Compliance §3 identity flags and §1.6 extraction confidence. Computed once and applied to every product before any score is shown.
14. **Unsecured PG exposure.** The total of recommended cards, fintech LOC, personal loans and MCA guaranties, used by compliance HR #11 as revised above.
