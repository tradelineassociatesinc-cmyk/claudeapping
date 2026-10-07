# R2: Compliance and Credit-Data Cross-Examination

## 1. Challenges

### SBA / Bank (r1_sba_bank.md)

| Ref | Problem | Replacement |
|---|---|---|
| §2 Derogatories ("paid, >36 mo old") | Ages are measured from the paid date. Paying an item doesn't reset its age; FCRA reporting runs from DOFD. A rule keyed to paid date would make an old item look newer after payment and penalize clients for paying. | "Age = months since **DOFD** (date of first delinquency). Paid status changes the band, not the age." |
| §2 Inquiries ("14-day cluster") | This is wrong for the models card issuers and banks actually use. FICO 8/9/10 de-dupe rate-shopping inquiries (mortgage, auto, student loan) within **45 days** and ignore them for the first 30 days. Classic mortgage FICO 2/4/5 and VantageScore use **14 days**. Credit-card inquiries are never de-duped. | Make the window a config value set per score model: FICO8+ = 45, FICO 2/4/5 = 14, Vantage = 14. Card and business inquiries are counted individually. |
| K7 FICO floors (620 SBA, etc.) | SBA publishes no personal FICO floor. Showing 620 as "SBA policy" is a misstatement in client-facing text. | Label every K7 value "**typical lender minimum**, not an SBA rule". |
| §6 "Credit freeze on new applications" | A security freeze is a legal term (FCRA §605A(i)). Telling a client to "freeze" so they stop applying conflates two different things and causes failed applications later. | "**Pause** new credit applications for 6 months." |
| K4, Q11 (criminal history) and K1 (citizenship) | These are permitted for SBA only (Form 1919; Reg B §1002.6(b)(7) allows considering immigration status). The engine must not let them spill into card, MCA or other lanes, and must not ask about national origin. | "Collect only when the goal includes SBA. Encrypt as sensitive, use only for SBA eligibility, and route to human review (H1)." The same rule applies to marital status: ask it only for a joint application, a community-property state, or a guarantor/spouse signature requirement (Reg B §1002.5(d)(1)). |

### Card broker (r1_card_broker.md)

| Ref | Problem | Replacement |
|---|---|---|
| K3 "reported or **updated** in last 24 mo" | Collections refresh their "date reported" monthly, so this rule catches every open collection regardless of age. It is a data-accuracy bug. Separately, the medical exclusion is a voluntary bureau policy, not a "CFPB change"; the CFPB rule was vacated in July 2025. | "Unpaid non-medical collection or charge-off, balance > $0, with **DOFD within 24 mo**. Older unpaid items count as a scored derogatory, not a knock-out. Medical collections that are paid or under $500 should not appear; if one does, raise a data-quality flag instead of a penalty." |
| K6 "tax lien, judgment" | These can't come from a bureau file (NCAP removed them). An empty field is not a clear record. | Source this from intake or public-records search. Any lien or judgment that does appear in the bureau data goes to human review. |
| K11 | The rule lumps freezes, fraud alerts and §605B identity-theft blocks together under "until lifted". An alert placed because of real fraud should be kept, and a §605B block is never "lifted" to make funding faster. | Freeze: client temporarily lifts it, no block once lifted. Fraud alert: **keep it**; expect identity verification and possible delays (§605A(h)); not a knock-out. §605B block or confirmed identity theft: hard block until the identity case is resolved. |
| Q1 income ("household income you have reasonable access to") | Reg Z §1026.51(b)(1)(ii) applies to **consumer** cards for applicants **21 or older**. Business cards and personal loans ask their own questions, often for individual income. Asking one blended question invites inaccurate answers on business applications. | Ask three separate fields: (a) individual income, (b) other household income you have regular access to, (c) business revenue. Report text: "Answer each issuer's income question exactly as that application words it." |
| §3 Optimistic estimate and the $200k ceiling | An optimistic multiple, shown to a client next to a PG product, reads as a promise (UDAAP; FTC v. Seek Capital, 2023). | Show the client Conservative to Expected only. Optimistic is visible to staff only. Add a human-review flag when total new PG exposure is over **$100k or over 50% of documented annual income**. |
| §6 Sequencing: "same-day … so new accounts don't show on later pulls" | The stated reason is concealment. Even though applying the same day isn't illegal, putting that reason in writing creates deception evidence. Issuers also later reduce limits on, or close, accounts opened in a burst. | Keep the order, change the reason: "Issuers apply their own velocity rules; this order follows published and observed issuer rules. Answer every application question truthfully, including questions about recent credit." Remove any wording about not showing or hiding. |
| §6 "Form an entity, get an EIN" | Clients then report the formation date as time in business, or overstate it. | Add: "Time in business on every application = the date the business actually started operating." |

### Alternative lending (r1_alt_lending.md)

| Ref | Problem | Replacement |
|---|---|---|
| §6 "Credit-repair coordination stays within FCRA" | The term "credit repair" pulls the firm toward CROA and state CSO law. | "Verify any item that appears inconsistent (see guardrails). Accurate items are not disputed." |
| Optional bank-statement upload | Statements are GLBA nonpublic personal information (NPI) and contain full account numbers. They are not covered by my data rules yet. | Apply the same consent, retention and masking rules as credit reports: delete raw files at 30 days, mask account numbers to the last 4. |
| §2 "commercial inquiries" | A consumer report doesn't mark inquiries as commercial. | Match inquiry names against an editable list of known business lenders. If an inquiry can't be matched, don't classify it. |
| §7 APR-equivalent ×2 heuristic | Fine, but the client could read it as a disclosed APR. | Label it "rough estimate; ask the funder for its state-required cost disclosure." |
| §8 broker commissions | Agree. Make it mandatory in the report text. | When the firm may be paid by a funder, the report must say so. |

---

## 2. Conflicts to resolve (proposed final policy)

### AU tradelines
1. **Detection.** ECOA code 3 identifies AU accounts. They are excluded from depth, highest limit, limit totals and primary-revolver counts in **every** lane. FICO 8 still counts them, so the displayed score stays as is, with a note.
2. **AU-heavy file.** Any of these triggers it: AU limits make up 30% or more of open revolving limits; the oldest account or the highest-limit account is an AU; or 2 or more AU accounts were added in the last 6 months that are older than 5 years or carry a limit of $10k or more. For an AU-heavy file the engine recomputes everything on primary accounts only, shows both versions, and sends the file to **human review**.
3. **Recommendations.** The tool **never** recommends acquiring, buying or renting AU tradelines. It never lists them as an action-plan step and never mentions any tradeline product. The only AU wording allowed is for genuine family members on thin files, and only as education: "Being an authorized user on a family member's well-managed card may help some scoring models; lenders reviewing applications often discount it." It is never presented as a way to qualify.
4. **Firm-level.** If Tradeline Associates sells tradelines, the audit tool must be **walled off** from that business: no cross-sell, no referral link, no readiness-score credit for added tradelines. Selling AU access "to improve a credit rating" for a fee is very likely a CROA service, which brings the advance-fee ban (§1679b(b)). Using purchased tradelines to obtain credit carries deception and fraud risk. **Counsel must review before launch.**

### Funding-estimate presentation
- Show a **range per product** (Conservative to Expected), rounded to $5k, and labeled "Indicative" plus a confidence level (High, Medium or Low, based on data source and staleness).
- Never show one number. Never show a "total available" headline that adds products together. Any combined scenario must state the sequence it assumes and the total PG exposure.
- No range is shown when: the score model is unknown, the report is more than 90 days old, extraction failed, or a hard block is active.
- Each range lists its main assumptions (score, highest limit, income, revenue source: self-reported or statements). MCA, factoring and stacking ranges show cost alongside.

### Stacking sequence
I adopt the SBA/alt consensus: **bank/SBA/term/LOC first, then cards**, with a 60–90 day gap, whenever both are goals. The tool may describe published and observed issuer rules (5/24, 2/90 and similar). It must not give any reason based on concealment, may not tell clients to freeze bureaus to control which bureau a lender pulls, and must show total PG exposure and the 0% payoff plan. More than 5 planned applications in 30 days triggers human review.

### Paid collections and pay-for-delete
- The age of a collection is measured from DOFD and **payment never resets it**.
- Report text: "Paying a collection resolves the debt. Its score effect depends on the model; FICO 8 still counts paid collections, while FICO 9/10 and VantageScore 3/4 do not. Lenders reviewing manually generally prefer resolved items."
- The tool **does not recommend pay-for-delete** and never promises deletion. A human may discuss it, but the client must be told that deletion is at the collector's discretion and that any agreement should be in writing.
- A paid medical collection that is still showing goes to "items to verify."

---

## 3. Concessions (changes to my R1)
1. **SBSS: corrected.** SBA stopped using SBSS for 7(a) Small loans approved on or after **March 1, 2026** (Procedural Notice 5000-875701; supplemented by 5000-876777). Lenders now underwrite with a credit memo and DSCR ≥ 1.10. My "165, confirm SOP" line is withdrawn, and no rule may reference SBSS. ([NAGGL](https://www.naggl.org/sba-notice-formally-announcing-sunsetting-of-sbss-scoring-and-providing-new-underwriting-requirements-for-7a-small-loans/), [Experian](https://www.experian.com/blogs/business-information/2026/07/22/the-sba-sbss-sunset/))
2. **Fraud alerts:** I now agree with the card broker. An alert is a review and delay flag, not a block.
3. **Medical collections in ban states:** downgraded from a human-review trigger to an informational flag. A human is needed only if the client asks about it.
4. **Income mismatch:** I adopt the lane-specific thresholds in place of my single 3× trigger. SBA uses intake vs. tax returns > 15%; alt uses self-reported deposits > 1.5× tax-return revenue/12; cards use stated income > 3× what the file implies.
5. **Added human-review triggers:** score spread between bureaus of 40 points or more (card broker); bank-statement alteration signals (alt HR-12); occupancy contradictions (alt HR-5).
6. **Intake addition:** a question on recent applications not yet on the report (card broker Q5), which feeds staleness.
7. **Data handling** now covers bank statements and tax returns (4506-C data) as well as credit reports.

---

## 4. Final guardrails list (for the report-generator system prompt)

**You must NEVER output:**
1. Advice to dispute, remove, delete or "challenge" information without the qualifier "only if you believe it is inaccurate or incomplete." Never use "609 letter," "credit sweep," "inquiry removal," "dispute everything," or "remove negative items."
2. Any statement that an item **is** inaccurate, illegal, or a violation by a creditor or bureau. Use "appears inconsistent," "verify."
3. Any mention of CPNs, credit privacy or secondary credit numbers, new credit identities, or using an EIN or ITIN instead of an SSN on a personal-credit application.
4. Advice to overstate or "optimize" income, revenue, time in business, employment, occupancy, use of funds, or business purpose. Never suggest hiding, moving or splitting deposits, altering documents, or amending tax returns to look better.
5. Advice to buy, rent or acquire authorized-user tradelines, or a cross-sell of any tradeline product.
6. Application timing framed as a way to keep lenders from seeing accounts or inquiries. Never advise selective bureau freezes to steer which bureau is pulled.
7. Guarantees or certainty: "guaranteed," "you will be approved," "you qualify for $X," "will raise your score N points," approval-odds percentages, or a single-number funding amount.
8. "Credit repair," "fix your credit," or "clean up your report" as a description of the firm's services.
9. Any statement that an SBA, issuer or lender rule is official policy unless the rule's config entry is marked "published." Otherwise say "typical lender practice."
10. Any use of or reference to race, color, religion, national origin, sex, marital status (except where permitted), age (except as a permitted factor), receipt of public assistance, or exercise of consumer-credit rights. Citizenship and criminal history may appear only in the SBA section.
11. Full SSN, full DOB, full account numbers, or full addresses in any funder-facing text.
12. Advice to stop paying a funder, default, or move accounts to avoid debits. Route these to human review and attorney referral.
13. Pay-for-delete as a recommended strategy, or any promise of deletion.

**You MUST include:**
1. On page 1 and in the footer: "Educational funding-readiness assessment, not a credit decision, loan offer, or guarantee of approval, terms, or amount. Lenders decide independently and may obtain their own reports."
2. Next to each estimate: "Indicative range based on general industry practices and the data provided; [confidence]; [self-reported / verified]."
3. Score provenance: "[model] from [bureau/source] dated [date]; lenders may use different scores."
4. For any item to verify: the objective reason, plus "You may dispute information you believe is inaccurate or incomplete directly with the credit bureau or furnisher, free of charge. Accurate, timely information may continue to be reported."
5. For any PG product: "Business credit typically requires a personal guarantee; you are personally liable. Promotional rates end; review post-promotional APR and fees." Also show total projected PG exposure.
6. For MCA, RBF and factoring: total payback in dollars, the debit amount, an estimated cost range, and "may not be a loan; request the state-required cost disclosure."
7. If the firm may receive compensation from a funder: a compensation disclosure.
8. A list of open human-review items. While any of these items is open, every eligibility statement it affects is marked "Pending review."
