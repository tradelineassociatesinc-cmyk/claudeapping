# R2 — Card Broker: Cross-Examination and Revision

## 1. CHALLENGES

### SBA/Bank (r1_sba_bank.md)
1. **§2 Inquiries: "count 14-day clusters as one."** That window is wrong for current scoring, and it is wrong for cards altogether. FICO 8 de-duplicates mortgage, auto and student-loan shopping within **45 days** (14 days only in legacy models). **Card and personal-loan inquiries are never de-duplicated** in scoring or in manual review. *Replace with:* a shared `inquiry_cluster` rule keyed by inquiry type, using a 45-day window for FICO 8 and later.
2. **§2 New accounts "8+ in 12 mo → 0 and human review (stacking)".** This works only if the count excludes AU accounts and business cards that do not report to the personal file. Otherwise the tool flags people who never stacked. *Replace with:* count primary personal accounts only. Count business cards separately, from intake and the debt schedule.
3. **§7.1 "Card stacking hurts bank/SBA approval".** I agree with the direction, not the mechanism. Most Chase, Amex, Citi, BofA and US Bank business cards do not appear on the personal report. The bank sees the inquiries, plus the balances the client must list on the personal financial statement (SBA Form 413) and the debt schedule. So the harm comes from **disclosed balances and payments**, not from tradeline count. Concealing them is the real risk, and it should trigger human review.
4. **§2 Credit depth requires "≥1 installment loan" for full points.** That is fine for the bank lane. It must not leak into card scoring, because card issuers do not need installment history.

### Alt-Lending (r1_alt_lending.md)
1. **§2 "Recent commercial inquiries >6 in 90 days".** A consumer report does not label inquiries "commercial." *Replace with:* a creditor-name classifier: card issuer, bank, fintech, MCA/ISO, auto, mortgage, or unknown. Unknown inquiries go to human review instead of being penalized.
2. **§8.4 "60–90 day gap after a card stack".** This conflicts with lender reality. OnDeck/Bluevine-type models react to inquiries and personal utilization. A 0% stack that is drawn shows high utilization, if the cards report personally, for the life of the promo. *Replace with:* if the client wants both products, do the term loan or LOC **first**, then the stack. This matches the SBA position.
3. **§3 0.8× haircut on self-reported revenue.** I accept it. My personal-income input needs the same discipline: stated income that is not verified should score at 0.8× for C (personal loans) and be flagged.
4. **My product D overlaps with their Online LOC.** Their deposit-based method is better (§5 below), so I am ceding it.

### Compliance (r1_compliance.md)
1. **§3 SSN-to-age hard block** (randomized post-2011 SSN with DOB before about 2005). This produces many false positives. Immigrants, naturalized citizens and people who returned from abroad legitimately get an SSN as adults. A hard block here creates national-origin disparate-impact risk under Reg B, which compliance itself cites in §5.1. *Replace with:* human review, a documents request (SSA card or letter), and no automatic decline.
2. **§3 "Thin file for an older adult ≥30" pattern.** Same issue. Keep it as review only, with neutral wording.
3. **§2 "AU lates noted but not scored."** This is partly wrong for my products. AU accounts **do** affect the FICO 8 score that issuers pull. Many data points also show AU cards count toward **Chase 5/24** [DP]. *Replace with:* AU accounts never add depth or count toward highest limit (I agree), but they **do** count toward new-account velocity, and an AU late is shown with an "ask the primary to remove you" remedy. Removing an AU account is the consumer's own decision, not a dispute.
4. **§1.1 Staleness: provisional at 60 days, estimate blocked at 90.** I agree, and I would go tighter for cards. Stacking needs a report **≤ 14 days old** at application time, because utilization and inquiries change within one cycle. The audit can run on an older report, but the action plan must include "re-pull before applying."

## 2. CONFLICTS TO RESOLVE

| Conflict | Position |
|---|---|
| **Bank/SBA/fintech loan first, stack after** | **Revise; I agree.** Rule SEQ-1: if the goals include SBA, bank or online term/LOC **and** a card stack, schedule the loan to close first and the stack ≥ 30 days after closing. Exception: if the loan timeline is more than 120 days and the client urgently needs working capital, a human decides, and the bank must be told about any cards taken. The report shows the trade-off in dollars. |
| **Funding totals overstated (FTC v. Seek Capital, 2023)** | **Revise.** The FTC alleged the company promised business financing, delivered personal cards, and charged percentage fees. My R1 cap of 1.0× income + 0.25× revenue and the $150–200k ceiling invite exactly that pattern. New caps are in §3 below. The report must label the estimate as "personal credit you are personally liable for," never "business funding." |
| **Paid collections still hurt under FICO 8** | **Defend, with clarification.** My R1 already penalized paid derogatories (2 of 3 points if older than 36 months). I adopt compliance's severity/decay model (paid non-medical collection base 35, decayed from DOFD) as the shared derogatory load. My R1 K3 still knocks out *unpaid* collections; a paid collection reduces the score but does not knock the client out. |
| **AU never counts toward depth** | **Defend; we agree.** R1 K9 and every depth factor (highest limit, primary card count, oldest account, average account age) were already primary-only, and R1 §8.4 said never to base an estimate on an AU limit. The one disagreement is velocity (Challenge 3 above): AU accounts count toward new-account velocity. |
| **0% promo balances imputed at 3% payment** | **Agree.** Use the reported minimum payment, or 3% of balance if that is higher or nothing is reported. This applies to all revolving debt, including the 0% balances in a planned stack. It drives a new "post-stack DTI" check: after the projected stack is drawn at 50% utilization, DTI with imputed payments must stay ≤ 45%. If not, the stack amount is reduced. |
| **Fraud alert vs. freeze** | **Revise R1 K11.** A **freeze** blocks automated decisions until the client temporarily lifts it. A **fraud alert** only causes a delay; the client keeps it, and we plan for verification calls. We never advise removing an alert or freezing bureaus to steer which bureau gets pulled. |

## 3. CONCESSIONS (changes to R1)

1. **Funding caps (Section 3A).**
   - Expected total ≤ min(4 × HL, **0.5 × verified annual personal income**, $100k).
   - Optimistic total ≤ min(5 × HL, 0.75 × verified income, $150k), and it is **shown only after human review** (compliance HR-11).
   - Business revenue is no longer added to the card cap. Only documented owner draws and W-2 income count.
   - Unverified income is scored at 0.8×.
   - Conservative stays HL × m × max(N−2, 1).
   - Every range carries its assumptions and the post-promo APR range (about 20–30%).
2. **Payoff-plan gate.** If the Q14 exit plan cannot repay the expected stack within the promo period from documented cash flow, cap the stack at that payoff capacity.
3. **Fee transparency.** If the firm charges a percentage-of-funding fee, the report shows it in dollars next to the range. Human review applies when the fee exceeds 10% of the expected amount.
4. **Sequencing advice wording.** "Apply to inquiry-sensitive issuers first, same-day" stays factual, but I drop any language implying that new accounts should be hidden from later issuers. Applications must answer every question truthfully.
5. **K11** revised as above.
6. **Product D** is merged into alt-lending's Online LOC. My reweighting there is withdrawn.
7. **Inquiries:** apply the 45-day rule for scoring only. Issuer velocity rules always count the raw number.
8. **Issuer rule table** (5/24, Amex velocity, Citi 8/65, BofA 2/3/4 and 7/12, Capital One 1-in-6) is labeled [DP] with a `last_verified` date, and it is used for sequencing, not for scoring.

## 4. SHARED-ENGINE RECOMMENDATIONS (one definition each)

- **`score[bureau]`**: score plus its model and source. Only FICO 8, 9, 10 or Bankcard count toward thresholds. A VantageScore is shown but marked low-confidence.
- **`mid_score`**: the middle of 3 bureaus, or the lower of 2.
- **`worst_guarantor_mid`**: the lowest `mid_score` among owners with 20% or more, for business products.
- **`target_bureau_score`**: the score from the bureau predicted by the issuer × state table. If unknown, use the lowest bureau.
- **`util_overall`**: Σ balances ÷ Σ limits on **primary open revolving** accounts with a limit. Exclude AU accounts and charge cards with no preset limit. Include closed cards that still carry a balance in the balance total, but not their limit.
- **`util_max_card`**: the highest single-card ratio on the same set.
- **`inquiries[bureau][6|12|24]`**: raw hard pulls, plus `inquiries_scored` using the 45-day de-duplication for mortgage, auto and student loans. Classify by creditor type.
- **`new_accts_primary[6|12|24]`** and **`new_accts_all[6|12|24]`**: counted by open date. The "all" count includes AU accounts. Use this "all" count for the 5/24 proxy.
- **`HL`**: highest limit on a primary open revolver. **`n_primary_revolvers`**, **`oldest_primary_months`**, **`aaoa_primary_months`**.
- **`derog_load`**: compliance §2 severity × decay from DOFD, with no exceptions.
- **`late_max_recent`**: the worst late within 12 months and within 24 months, on primary accounts.
- **`monthly_debt_imputed`**: reported minimums, or 3% of the revolving balance if higher, including 0% promo balances. Installment payments as reported. Deferred student loans at 0.5% of balance.
- **`dti`** = `monthly_debt_imputed` (+ housing) ÷ verified gross monthly income. Unverified income is taken at 0.8×.
- **`pg_exposure_new`**: the sum of recommended personally guaranteed limits and loans across all products. Above $100k, or above 50% of verified income, triggers human review.
- **`data_confidence`** and **`report_age_days`**: the compliance §1.6 and §1.1 gates apply to every product.
- **`identity_flags`**: compliance §3, with the SSN-age rule downgraded to human review.
- **`sequencing_conflict`**: true when the goals include a card stack plus any bank, SBA or alt loan. This drives SEQ-1.
