# R1 — Alternative-Lending Underwriter Proposal
Scope: RBF/MCA, online term loans & LOCs (OnDeck/Bluevine/Fundbox-style), invoice factoring, non-bank equipment finance, real-estate investor loans (DSCR, fix & flip).

**Core position:** alt lenders underwrite cash flow from bank statements first, then credit. A credit report alone can't produce a reliable alt-lending decision. So the tool should (a) ask intake proxies for bank-statement metrics, (b) offer an **optional upload of 3–6 months of business bank statements** that, when present, overrides the self-reported numbers, and (c) label every alt-lending result "Indicative — self-reported cash flow" until statements are verified.

Published-minimum spot checks (these change; store them as config):
- OnDeck: 625 FICO, $100k annual revenue, 1 yr TIB. Bluevine LOC: 625 FICO, ~$480k annual revenue (~$40k/mo), 2 yrs TIB. Fundbox: ~600 FICO, 3–6 mo TIB, revenue floor reported as $30k–$100k depending on source (NerdWallet; UnitedCapitalSource).
- MCA: commonly 500+ FICO and ~$15k+/mo revenue. Credibly lists ~$180k/yr. Factor rates run 1.1–1.5 and holdbacks 10–20% (NerdWallet/Credibly review; Funding Circle).
- Factoring: 75–90% advance, 1–5% fee per invoice/month (Xero, Ramp, Advance Partners).
- Equipment (non-bank): 550–620 FICO and 6–24 mo TIB depending on lender, 0–20% down (NerdWallet, Bankrate, OnDeck).
- DSCR: 620 FICO floor at most lenders, DSCR ≥1.0 (1.25 for best pricing), 70–80% LTV that steps down with score (Griffin Funding, Rize Mortgage).
- Fix & flip: 70–75% of ARV cap, 80–90% LTC, lower leverage for first-time flippers (NerdWallet, RidgeStreet Capital).

---

## 1. Knock-out rules (hard fails → product "Not eligible now")

Each threshold is a config value. "Hard" means no lender in the normal market will fund it. A "Soft" fail drops the product to "Possible via subprime/broker — human review."

**All business alt products**
- KO-ALT-1 (Hard): no business bank account in the business's legal name. Alt lenders debit and credit that account. Remedy: open one and run all revenue through it for 3+ months.
- KO-ALT-2 (Hard): open bankruptcy (personal or business), or a BK discharged < 12 months ago (MCA) / < 24 months ago (term loan, equipment).
- KO-ALT-3 (Hard): prohibited industry. Includes cannabis/plant-touching, adult, firearms dealers (many lenders), gambling, crypto, debt collection, MLM, pawn, and shell/holding companies with no operations. Restricted industries (trucking, auto sales, construction, restaurants, real estate, nonprofits, financial services) are **Soft**. They get fewer lenders and lower amounts. This list varies by lender and must be editable.
- KO-ALT-4 (Hard): an active tax lien or judgment over $10k with no payment plan (Soft if a plan exists and 3+ payments have been made).
- KO-ALT-5 (Hard): the applicant can't confirm they own at least 51% (or that the guarantors together own 51%+).

**MCA / RBF**
- Time in business < 4 months: Hard. 4–5 months: Soft.
- Avg monthly deposits < $10,000: Hard. $10k–$15k: Soft.
- FICO < 500: Hard. 500–549: Soft.
- 4 or more open MCA positions: Hard. 3 positions: Soft.
- Current positions' combined daily/weekly payments > 35% of avg monthly deposits: Hard.
- NSFs in the last 30 days > 6, or avg monthly negative days > 8: Hard. Only checkable with statements, or self-reported.

**Online term loan / LOC**
- TIB < 12 months: Hard for term loans. Fundbox-style LOCs go down to 3–6 months, so for LOCs this is Soft at 6–11 months.
- Annual revenue < $100k: Hard. For LOC-lite products, < $30k is Hard.
- FICO < 600: Hard. 600–624: Soft.
- 2 or more MCA positions open: Hard. Most online term lenders will only refinance one position at most.
- Avg daily balance < $1,000: Soft.

**Invoice factoring**
- B2C invoices only: Hard. Factoring needs commercial or government debtors.
- Monthly B2B receivables < $10,000: Soft. < $5,000: Hard.
- Invoices already pledged under a UCC blanket lien that the lender won't subordinate: Hard. This needs an intercreditor agreement or payoff.
- Receivables older than 90 days make up > 50% of A/R: Hard.
- Note: the client's FICO is **not** a knock-out here. The debtors' credit matters more. A client FICO < 500 only goes to human review.

**Equipment (non-bank)**
- FICO < 550: Hard. 550–599: Soft (needs a larger down payment).
- TIB < 6 months: Hard. 6–23 months: Soft. Startup programs need 680+ FICO and 10–20% down.
- The equipment is used, older than 10 years, or can't be titled or easily resold: Soft (human review).
- A private-party sale with no invoice or bill of sale: Soft.

**DSCR loan**
- FICO < 620: Hard. A few lenders go to 600 at 65% LTV, so 600–619 is Soft.
- DSCR < 0.75: Hard. 0.75–0.99 is Soft and limited to "no-ratio" programs at ≤ 65–70% LTV.
- Down payment/equity < 20%: Hard. 20–24%: Soft.
- Reserves < 3 months PITIA: Soft. < 1 month: Hard.
- The property is owner-occupied, or will be: Hard. DSCR loans are business-purpose only, and misrepresenting occupancy is mortgage fraud, so this also triggers a human-review flag.
- Foreclosure or short sale < 36 months ago: Hard. 36–47 months ago: Soft.
- 60+ day mortgage late in the last 12 months: Hard.

**Fix & flip**
- FICO < 620: Hard. 620–659: Soft.
- Requested loan > 75% of ARV or > 90% of total cost: Hard.
- Cash to close plus 10% reno contingency not verified as liquid: Hard.
- No exit plan and no comps: Soft.
- First flip with no GC and a scope over $50k: Soft (human review).

---

## 2. Scoring factors (per-product score 0–100)

The bands are the same for MCA, term loans and equipment, but each product weights them differently. Points = band score (0–1) × weight.

| Factor | Bands → band score | MCA wt | Term/LOC wt | Equip wt |
|---|---|---|---|---|
| Avg monthly deposits (true revenue, excluding transfers and loan proceeds) | <15k:0.2 · 15–25k:0.5 · 25–50k:0.7 · 50–100k:0.85 · >100k:1.0 | 25 | 20 | 12 |
| Time in business | <6mo:0.2 · 6–11:0.4 · 12–23:0.7 · 24–59:0.9 · 60+:1.0 | 10 | 15 | 15 |
| FICO (lowest of guarantors') | <550:0.1 · 550–599:0.35 · 600–649:0.6 · 650–699:0.8 · 700+:1.0 | 10 | 20 | 25 |
| Avg daily balance as % of monthly deposits | <3%:0.2 · 3–7%:0.5 · 7–15%:0.8 · >15%:1.0 | 12 | 12 | 8 |
| NSFs/overdrafts per month (3-mo avg) | 0:1.0 · 1–2:0.75 · 3–4:0.4 · 5–6:0.15 · >6:0 | 12 | 10 | 8 |
| Negative-balance days/month | 0:1.0 · 1–3:0.6 · 4–8:0.25 · >8:0 | 6 | 6 | 4 |
| Deposit count/month | <5:0.3 · 5–10:0.6 · 11–20:0.85 · >20:1.0 | 5 | 3 | 2 |
| Existing positions (MCA/daily-debit loans) | 0:1.0 · 1:0.6 · 2:0.3 · 3+:0 | 15 | 10 | 8 |
| Revenue trend (last 3 mo vs prior 3 mo) | <−25%:0.1 · −25 to −10%:0.5 · ±10%:0.85 · >+10%:1.0 | 5 | 4 | 3 |
| Collateral/down payment (equip) | n/a | — | — | 15 |

Notes:
- **Industry modifier:** subtract 10 points for a restricted industry, after weighting.
- **Data-confidence modifier:** if cash-flow data is self-reported only, cap the score at 80. The report labels it "Indicative" and asks for statements to raise the cap.
- **Credit-report-derived signals** that alt lenders do check: recent commercial inquiries (more than 6 in 90 days suggests shopping or stacking, −5), recent charge-offs or collections from business lenders (−10, human review), and current personal delinquency 30+ days (−5 each, capped at −15).

**Factoring score:** debtor quality (government or investment-grade debtors: 1.0; established mid-market: 0.7; small or unrated: 0.4), weight 35. Avg days-to-pay (≤30: 1.0, 31–45: 0.8, 46–60: 0.5, 61–90: 0.2), weight 25. Concentration, meaning the largest debtor's share of A/R (≤25%: 1.0, 26–50%: 0.7, 51–75%: 0.4, >75%: 0.2), weight 15. Monthly invoice volume (same bands as deposits), weight 15. Liens/taxes clean, weight 10.

**DSCR score:** DSCR (≥1.25: 1.0, 1.10–1.24: 0.8, 1.00–1.09: 0.6, 0.75–0.99: 0.25), weight 35. FICO (620–659: 0.4, 660–699: 0.6, 700–739: 0.85, 740+: 1.0), weight 25. Equity (20–24%: 0.5, 25–29%: 0.75, ≥30%: 1.0), weight 20. Reserves (3–5 mo: 0.6, 6–11: 0.85, 12+: 1.0), weight 10. Investor experience (0 properties: 0.5, 1–2: 0.8, 3+: 1.0), weight 10.

**Fix-and-flip score:** FICO, weight 20. Completed flips in 36 months (0: 0.3, 1–2: 0.6, 3–4: 0.85, 5+: 1.0), weight 25. Loan/ARV (≤65%: 1.0, 65–70%: 0.8, 70–75%: 0.5), weight 25. Liquidity ≥ 15% of total project cost, weight 20. Licensed GC plus a written scope, weight 10.

**Tiers:** 80+ Strong · 65–79 Fundable · 50–64 Marginal (subprime pricing) · <50 Not ready.

---

## 3. Funding amount estimation (conservative / expected / optimistic)

"Rev" is average monthly **true** deposits, excluding transfers, loan proceeds and refunds. Subtract existing positions' remaining balances where the formulas say so.

**MCA / RBF**
- First position: 0.5× / 1.0× / 1.5× Rev. Use 0.5× when FICO < 550, NSFs ≥ 3 or TIB < 12 months.
- Second position and beyond: halve each multiple, then subtract existing balances.
- **Affordability cap**, which overrides the multiples: total daily-debit burden after funding must be ≤ 15% (conservative), 20% (expected) or 25% (optimistic) of Rev.
  - Max advance = (cap% × Rev − existing monthly debits) × term months ÷ factor rate.
  - Use a 6-month term at factor 1.35 by default.
- Example: Rev = $40k, no positions, expected cap 20%. ($8,000 × 6) ÷ 1.35 = $35.5k, which agrees with the 1.0× multiple.

**Online term loan**
- 0.5× / 0.85× / 1.25× Rev for 6–18 month terms. This is roughly 8–15% of annual revenue, and up to 20% for a strong file.
- Also subject to a payment-to-revenue cap: ≤ 10% / 12% / 15% of Rev, at an assumed 30–60% APR.
- Bank-quality files (TIB 2+ years, FICO 680+) can stretch to 1.5–2× Rev with a 24–36 month term.

**Online LOC (Fundbox/Bluevine-style)**
- Credit limit of 0.25× / 0.5× / 1.0× Rev, with the product cap configurable (typically $150k–$250k).

**Invoice factoring**
- Facility = eligible A/R × advance rate.
- Eligible A/R excludes invoices over 90 days, government invoices without assignment, contra accounts and affiliate debtors.
- Advance rate: 70% / 80% / 90%. Trucking typically gets 90–95%, construction 60–75%.
- Cost: 1.5% / 2.5% / 4% per 30 days outstanding.
- Show net cash = advance − fees.

**Equipment**
- Financed amount = equipment cost × (1 − down%).
- Down payment: 20% / 10% / 0%. Use 20–30% when FICO < 600, TIB < 2 years, or the equipment is used.
- Cap the monthly payment at ≤ 10% / 12% / 15% of Rev.
- Term: 24–60 months, never longer than the equipment's useful life.

**DSCR**
- DSCR = gross monthly market rent (from a lease, or a 1007 rent schedule) ÷ PITIA.
- Max loan = min(LTV cap × value, loan size where DSCR = target). Solve the payment = rent ÷ target DSCR at the current note rate.
- LTV caps by FICO for a purchase: 620–659: 65–70%; 660–699: 70–75%; 700+: 75–80%. Subtract 5 points for a cash-out refi.
- Target DSCR: 1.25 (conservative), 1.10 (expected), 1.00 (optimistic).
- Minimum loan is usually $75k–$100k.

**Fix & flip**
- Loan = min(LTC% × (purchase + rehab), ARV% × ARV).
- First-time flipper: LTC 75/80/85%, ARV 65/70/70%.
- Experienced (3+ flips): LTC 85/90/90%, ARV 70/75/75%.
- Rehab is funded in draws, so the client still needs the first draw plus a 10% contingency in cash.

---

## 4. Intake follow-up questions (branch only for selected products)

**Bank statements:** add an optional upload of the last 3 months (MCA/LOC) or 6 months (term/equipment) of business statements, PDF. Strongly recommended. Uploaded statements unlock the score cap and replace the self-reported answers. If none are uploaded, ask:

**Common business block (MCA, term, LOC, equipment, factoring)**
1. "What is your business's legal start date (per formation docs or EIN letter)?" (date)
2. "What industry is the business in? (NAICS or description)" (select + text)
3. "Do you have a business checking account in the business's legal name?" (Y/N)
4. "Average total monthly deposits into your business account over the last 3 months, NOT counting transfers between your own accounts or loan proceeds?" (currency)
5. "Approximate number of separate deposits per month?" (select: <5, 5–10, 11–20, 20+)
6. "Typical ending daily balance on a normal day?" (currency)
7. "In the last 3 months, how many overdrafts / NSF / returned items have you had?" (integer)
8. "How many days per month does the account go negative?" (integer)
9. "Gross revenue last full year, and year-to-date?" (currency ×2)
10. "Do you currently have any merchant cash advances or loans that debit your account daily or weekly?" (Y/N). If Y, repeat for each: funder, original amount, current balance, payment amount + frequency, and date funded.
11. "Any business tax liens, judgments, or UCC filings against the business?" (Y/N + amount + payment plan Y/N)
12. "What percentage do you own? Any other owners with 20%+?" (percent + list)
13. "Has revenue in the last 3 months gone up, stayed flat, or gone down vs. the prior 3?" (select + approximate %)
14. "Do you file business tax returns showing a profit? (most recent year net income)" (currency, allow negative)

**MCA/RBF add:** "What share of revenue comes in through card processing?" (percent). "Monthly card processing volume?" (currency)

**Factoring add:**
- "Do you invoice other businesses or government agencies (not consumers)?" (Y/N)
- "Total unpaid invoices right now, and the amount over 90 days?" (currency ×2)
- "Average days for customers to pay?" (integer)
- "Largest customer's share of receivables?" (percent)
- "Name your top 3 customers" (text, used by the debtor-quality check)
- "Has any lender filed a blanket UCC lien on your assets?" (Y/N/Unknown)

**Equipment add:**
- "Equipment type, new/used, year, cost?" (select, select, year, currency)
- "Vendor/dealer or private seller?" (select)
- "Do you have a quote/invoice?" (Y/N)
- "Down payment available?" (currency)

**DSCR add:**
- "Purchase or refinance (rate/term or cash-out)?" (select)
- "Property type and units?" (select: SFR, 2–4, 5+, condo, STR)
- "Purchase price / estimated value?" (currency)
- "Current or market monthly rent (lease or appraiser rent schedule)?" (currency)
- "Annual property taxes, insurance, HOA?" (currency ×3)
- "Down payment and post-closing liquid reserves?" (currency ×2)
- "Will you or a family member live in it?" (Y/N). If Y, ineligible for DSCR and flagged for human review.
- "How many investment properties do you own now?" (integer)
- "Will you close in an LLC?" (Y/N)

**Fix & flip add:**
- "Purchase price, rehab budget, after-repair value (with comps source)?" (currency ×3 + text)
- "Number of flips completed in last 36 months?" (integer)
- "Licensed GC with written scope?" (Y/N)
- "Cash available for down payment, closing, and first draw?" (currency)
- "Planned exit: sell / refi to DSCR / unsure?" (select)

---

## 5. Human-review triggers

- **HR-1:** self-reported deposits are more than 1.5× annual tax-return revenue ÷ 12. This is a possible income overstatement, and coaching it would be misrepresentation.
- **HR-2:** 3 or more existing MCA positions, or payments over 25% of Rev. Stacking/debt-spiral risk. Steer toward a consolidation or reverse-consolidation review with a cost analysis, not another advance.
- **HR-3:** a client asks how to "hide," "move" or "split" deposits to avoid a holdback or a lender's view, or asks about using a different bank account. This is fraud or contract-breach risk, and a breach can trigger the MCA's confession-of-judgment or default clauses.
- **HR-4:** an existing MCA is in default, a funder has filed a UCC, there is a lawsuit, or a client wants to stop paying. This needs attorney referral, not consulting.
- **HR-5:** occupancy contradictions on a DSCR file. Examples: an intake address matches the subject property, or the credit report shows it as the primary residence.
- **HR-6:** prohibited or restricted industry, or an industry description that doesn't match the NAICS code given.
- **HR-7:** a business commercial charge-off or collection from a known alt lender on the credit report.
- **HR-8:** TIB on intake disagrees with the oldest business-related tradeline or with the Secretary of State formation date by more than 6 months.
- **HR-9:** factoring debtor concentration over 75%, or government receivables (Assignment of Claims Act paperwork).
- **HR-10:** a fix & flip where ARV exceeds purchase + rehab by more than 60% with no comps. Inflated-ARV risk.
- **HR-11:** recent heavy commercial-inquiry clustering (8 or more in 60 days). Likely broker shotgunning, which can lead to unwanted stacking offers.
- **HR-12:** uploaded statements show possible alterations, such as font mismatches or running balances that don't reconcile. Never coach statement edits.

---

## 6. Action-plan rules (remedy → timeline)

| Trigger | Remedy | Timeline to re-score |
|---|---|---|
| No business bank account / commingled funds | Open a dedicated account and route 100% of revenue through it | 3 months (MCA), 6 months (term) |
| NSF ≥ 3/mo or negative days ≥ 4 | Keep a buffer of ≥ 10% of monthly deposits and turn on overdraft alerts; aim for 0 NSFs | 90 days of clean statements |
| ADB < 5% of Rev | Build ADB toward 10% and avoid draining the account to near zero after deposits | 60–90 days |
| TIB short of a product minimum | Recommend an interim product and give the exact date the client crosses 6/12/24 months | Date-based |
| Revenue below the minimum | Show the revenue gap, e.g. "need +$X/mo for 3 consecutive months" | 3 months |
| Existing MCA positions | Pay off or let the smallest position run off first, and don't take a new position within 30 days. Lenders view the file better when a position is "paid down 50%+" | Position runoff date |
| FICO 600–624 (online term) | Bring revolving utilization under 30%, then under 10%. Credit-repair coordination stays within FCRA (accurate items are not disputed) | 30–90 days |
| DSCR < 1.0 | Larger down payment to lower PITIA, an interest-only option, a rent increase supported by a lease, or a cheaper property | Per deal |
| DSCR reserves short | Season the reserves in an account for 60 days | 60 days |
| Factoring: aged A/R > 90 days | Run collections and tighten payment terms to net-30 | 60–90 days |
| Tax lien without a plan | Set up an IRS installment agreement and make 3 on-time payments | ~90 days |
| Flip with no track record | Partner with an experienced flipper, hire a GC, or lower leverage | Deal-by-deal |

---

## 7. Cost and risk warnings, and steer-away rules

The report must show for every MCA/RBF result:
- **Estimated APR-equivalent:** APR ≈ (factor − 1) ÷ (term in days ÷ 365) × ~2. The ×2 accounts for the amortizing balance. Example: 1.35 over 6 months is about **70% simple and ~120–140% APR-equivalent**. Display a range of 40–350% (published industry range).
- **Total payback in dollars and the daily/weekly debit amount**, alongside the client's average daily balance.
- **Stacking warning:** "Each additional advance typically costs more and shortens your cash runway. Most defaults occur in 2nd–4th position."
- **Contract-risk warning:** confession of judgment (now restricted for out-of-state use in NY), personal guarantee, UCC blanket lien, and anti-stacking covenants. Also note that commercial financing disclosure laws in NY, CA, UT, VA, GA, FL and CT require APR or cost disclosure in many cases, so tell the client to ask for the disclosure.
- **Factoring:** state the effective annual cost (fee per 30 days × 12, so 3%/mo ≈ 36%/yr) and note that debtors will be notified under recourse vs. non-recourse terms.

**Steer-away rules** (the report recommends cheaper products first):
- **SA-1:** if the client qualifies for a business card stack, a business LOC, SBA or a bank term loan at ≥ 50% of the requested amount within the client's timeline, rank MCA last and add the label "Expensive — not recommended unless time-critical."
- **SA-2:** MCA purpose is "pay off another MCA," "cover payroll shortfall from declining revenue," or "start the business": add a red warning, put MCA last, and flag for human review.
- **SA-3:** projected total debits after funding exceed 20% of Rev: don't recommend at all.
- **SA-4:** revenue is declining more than 25%: don't recommend MCA or a short-term loan. Point to a restructuring or cost plan.
- **SA-5:** use of funds has no ROI path, such as personal expenses or debt from a failed venture: don't recommend.
- **SA-6:** fix & flip for a first-time investor with less than 20% liquidity: recommend a partnership or education, not a loan.

---

## 8. Cross-cutting opinions (what other experts may get wrong)

1. **Credit score is a gate, not the driver, in alt lending.** A 720 FICO with 4 NSFs/month gets declined by an MCA funder. A 560 with a clean $60k/month account gets funded. Don't let a high bureau score make a business look alt-lending-ready without cash-flow data.
2. **"Revenue" means true deposits, not gross sales or P&L.** Transfers, loan proceeds, owner injections, refunds and Zelle from yourself are all backed out. Self-reported revenue is routinely 20–40% higher than true deposits, so apply a 0.8× haircut when there are no statements.
3. **Time in business is measured from first revenue in the business bank account, as well as from formation date.** An LLC formed in 2019 that has deposited only for 4 months is a 4-month business to an alt underwriter.
4. **Business card stacking hurts later alt and bank approvals.** Many new tradelines plus heavy inquiries in 6 months reads as stacking to OnDeck- and Bluevine-type models, as does high personal revolving utilization from cards used for business. The tool should sequence the products: get term/LOC approvals before the card stack if both are goals, or leave a 60–90 day gap after.
5. **The UCC lien is the hidden blocker.** One MCA's blanket UCC can block factoring and some equipment and bank deals. Ask about it every time.
6. **DSCR is a real-estate product, not a personal-income product.** Personal DTI and employment don't matter, but FICO, reserves, and the absence of recent mortgage lates or foreclosures do. Don't apply business-card or SBA logic to it.
7. **Funding estimates must be the lesser of the multiple and the affordability cap.** A tool that shows "up to 1.5× revenue" without the payment-burden cap will push clients into default.
8. **Consulting fee and compliance:** if the team earns a broker commission on MCA placement, disclose it. MCA commissions can be 8–12 points, which is a conflict that the steer-away rules help neutralize. Several states (NY, CA, UT, VA) require broker registration or disclosure, so flag it for the team's counsel.

---
Sources: [NerdWallet – Best online business loans](https://www.nerdwallet.com/business/loans/best/online); [UnitedCapitalSource – Fundbox review](https://www.unitedcapitalsource.com/business-loans/lender-reviews/fundbox-review/); [Bankrate – OnDeck review](https://www.bankrate.com/loans/small-business/reviews/ondeck); [NerdWallet – Credibly MCA review](https://www.nerdwallet.com/business/loans/reviews/credibly); [Funding Circle – MCA](https://fundingcircle.com/us/resources/merchant-cash-advance); [Griffin Funding – DSCR requirements](https://griffinfunding.com/blog/investor-loans/dscr-loan-requirements/); [Rize Mortgage – DSCR requirements](https://rizemtg.com/blog/dscr-loan-requirements); [Xero – Invoice factoring](https://www.xero.com/us/guides/invoice-factoring-what-it-is-how-to-use/); [Advance Partners – Factoring cost](https://www.advancepartners.com/blog/how-much-does-invoice-factoring-cost/); [NerdWallet – Fix & flip loans](https://www.nerdwallet.com/business/loans/learn/fix-and-flip-loans); [RidgeStreet Capital – First-time flip loans](https://www.ridgestreetcap.com/blog/first-time-fix-and-flip-loans); [NerdWallet – Equipment loans bad credit](https://www.nerdwallet.com/business/loans/learn/no-credit-check-equipment-financing); [Bankrate – Equipment loans](https://www.bankrate.com/loans/small-business/how-to-get-equipment-loan); [OnDeck – Equipment financing](https://www.ondeck.com/loantype-equipment-financing). State disclosure-law and NY confession-of-judgment notes come from general industry knowledge. Counsel should verify them.
