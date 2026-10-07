# R3: Business Identity & Entity Compliance Rules for the FRA

**Author persona:** Business-entity compliance and lender KYC specialist ("fundability" / business identity).
**Scope:** The Master Business Identity Matrix, the Master Business Address decision, all 20 audit points (11, 12, 13, 18 and 19 are brief here; another expert covers them in depth), area ratings, flag ordering, First Three Actions, the composite-score withhold rule, the Resource Directory, client explanations, and guardrails.
**Conventions:** Status codes: **PASS**, **NI** (Needs Improvement), **AR** (Action Required), **PEND** (Pending / Need Document), **N/A**. Source labels follow RULEBOOK: **[PUB]** published rule, **[DP]** industry data point, **[EXP]** expert judgment the team tunes. All examples use fictional placeholders ("Example Co LLC", "EIN 00-0000000", "100 Main St").

---

## 0. Global status logic (applies to every point)

Evaluate in this order. The first rule that matches sets the status.

1. **N/A**: the point's applicability test fails, and the analyst records the basis (for example, "domestic entity, no out-of-state nexus").
2. **AR**: a material defect is **confirmed** from the evidence in hand. A confirmed defect beats missing evidence, so a point can be AR while other inputs are still outstanding.
3. **PEND**: a required input is missing, or a source returned **INSUFFICIENT DATA**, and nothing confirmed fails. PEND is not a negative finding and is never scored as one.
4. **NI**: the element exists and works, but a weakness could affect the underwriting outcome or capacity.
5. **PASS**: the point's PASS STANDARD is fully met from documents.

**Evidence rule:** a client's statement is enough for PEND→NI movement only. **PASS always requires a document or verified third-party research.** The one exception is points that are research determinations by nature, such as 5 and 16, where TLA's documented research is the evidence.

**Finding text rule (inherits RULEBOOK G-02):** say "appears inconsistent; please verify," never "is wrong." When two documents disagree, state the disagreement. Never resolve it silently.

---

## 1. Master Business Identity Matrix

### 1.1 Fields (rows)

| # | Field | Controlling source (wins on conflict) | Notes |
|---|---|---|---|
| F1 | Legal name | SOS formation and amendment filings | Exact spelling, including suffix |
| F2 | DBA / assumed name(s) | Assumed-name filing (state or county) | Only a filed name counts as a DBA |
| F3 | Entity type | SOS filing (LLC, PLLC, Corp, PC, LP, LLP, etc.) | Tax classification (S-corp election, disregarded) is **not** entity type |
| F4 | State and formation date | SOS filing | Formation date ≠ operations start date (RULEBOOK D3, HR-27) |
| F5 | EIN / TIN | IRS CP 575 or Letter 147C | SS-4 is the application, not proof of issuance |
| F6 | Business address (master) | Client designation plus proof (§2) | Physical and mailing tracked separately |
| F7 | Registered agent and office | SOS current record | Statutory address, not a business address |
| F8 | Phone | Client attestation plus carrier/411 verification | Must be controlled by the business |
| F9 | Email | Client, checked for domain match | Free-mail is flagged |
| F10 | Website / domain | Live site plus registrar data (RDAP) | |
| F11 | NAICS (6-digit) | Client-selected truthful code | Tax-return business code is recorded and compared, never changed by TLA |
| F12 | SIC (4-digit) | Derived from the same activity as F11 | |
| F13 | Annual revenue | Most recent filed tax return (gross receipts) | Lower-of rule, RULEBOOK R10 |
| F14 | Employees | Payroll records (W-3/941) or client attestation | |
| F15 | Owners (≥20%) and percentages | Operating agreement / stock ledger / membership records | **Not** the SOS record |
| F16 | Management / control person | SOS management filings plus resolutions; bank control-prong certification | Ownership and management are separate rows |
| F17 | Years in business (as displayed) | Derived from F4 | Bureau "years in business" is compared to F4 |

### 1.2 Sources (columns)

Reliability tiers decide which value "controls." They never permit TLA to overwrite a record with a value it can't document.

| Tier | Sources |
|---|---|
| A: Authoritative | IRS CP 575 / Letter 147C (SS-4 as supporting); SOS formation, amendments, certificate of status/existence; registered-agent filings; operating agreement / bylaws / stock ledger; assumed-name filings |
| B: Institutional | Bank account profile, beneficial-ownership certification and W-9; business tax returns; business license(s); lease or utility in the business name |
| C: Reported data | Experian Business, D&B, Equifax Business (incl. SBFE), LexisNexis business file, UCC filings (debtor name/address as filed by the secured party) |
| D: Self-published | Website, Google Business Profile, 411/directory listing, domain registration (RDAP) |
| E: Client-stated | Intake answers |
| P: Personal | Guarantor's consumer-report addresses and name variants (used only to explain address history and business-address leakage; never shown in the business matrix to funders) |

A source that was not obtained displays **"Not available"**. That is different from a source that was obtained and shows **"Blank"**.

### 1.3 Normalization before comparison

**Names (F1, F2):**
- Uppercase, trim, collapse whitespace. Strip `. , ' "` and a leading "THE". Treat `&` and `AND` as equal.
- Suffix equivalence classes: {LLC, L.L.C., LIMITED LIABILITY COMPANY, LTD LIABILITY CO}; {PLLC, P.L.L.C., PROFESSIONAL LIMITED LIABILITY COMPANY}; {INC, INC., INCORPORATED}; {CORP, CORPORATION}; {CO, COMPANY}; {LP, LIMITED PARTNERSHIP}; {LLP}; {PC, P.C., PROFESSIONAL CORPORATION}.
- **INC vs CORP is a VARIANT, not EQUIVALENT.** The SOS name is literal.
- Record the IRS name control (the first four significant characters the IRS uses for TIN matching [PUB, IRS TIN Matching / Pub 1281]). A difference in the first four characters is always a CONFLICT.

**Addresses (F6, F7):** Standardize to USPS Publication 28: suffix abbreviations (Appendix C), directionals, and secondary-unit designators STE/UNIT/#/APT [PUB]. Compare street + secondary + ZIP5. Ignore ZIP+4 and case. Flag these tokens: `PMB`, `#` following a commercial suite at a known CMRA, `PO BOX`, `C/O`, and registered-agent office addresses (matched against the SOS RA field and a maintained list of national RA providers).

**Entity type (F3):** Map every source's vocabulary to the SOS type. "Limited Liability Company" (D&B) = LLC. "Disregarded entity," "partnership," "S corporation" or "C corporation" on an IRS or tax document describe tax classification and are **EQUIVALENT** to an LLC legal type. "Corporation" shown for an LLC at a bureau is a **CONFLICT**. LLC vs PLLC between two SOS documents is a **CONFLICT** that needs the live SOS record.

**People (F15, F16):** Match on first + last name. Middle name or initial and generational suffix (Sr., Jr., II) differences are **VARIANT**. A different first name is a **CONFLICT** unless it appears in the nickname table (RULEBOOK ID-05).

**Phone:** Strip to 10 digits. **Domain/email:** lowercase, root domain.

### 1.4 Comparison outcomes and severity

Each cell gets one outcome: **MATCH**, **EQUIVALENT**, **VARIANT**, **BLANK**, **CONFLICT**, or **NOT AVAILABLE**. A cell that needs correction is shaded in the report.

| Mismatch type | Severity | Feeds point(s) |
|---|---|---|
| Different 9-digit EIN/TIN on any Tier A–C record (including transposition) | **S1, gating** | 1, 20 (→ 19 search) |
| Legal name CONFLICT (different words) on IRS, bank or SOS | **S1** | 17, 20 |
| State of formation conflict between Tier A documents | **S1** | 2, 17 |
| No master address designated while ≥2 active candidates exist | **S1** | 15, 20 |
| Bureau shows an unrelated / out-of-state / prior-party address as current | **S2** (S1 if it's the only address the bureau shows) | 15, 20, 19 |
| Entity type CONFLICT at a bureau, or LLC/PLLC conflict in SOS filings | **S2** | 17, 20 |
| Legal name BLANK at a bureau that has a file | **S2** | 17, 20 |
| Owner/control person on bank certification ≠ governing documents | **S2** (S1 if the person is entirely different) | 1, 20 |
| Formation date differs >6 months, or bureau years-in-business = 0 on an entity ≥1 year old | **S2** | 20 (HR-27) |
| Bureau revenue differs from return gross receipts by >30% (R10 pair) | **S2** | 20 |
| NAICS/SIC conflict across bureaus, or vs. the business description | **S2** | 4 |
| Intake value contradicts a Tier A document (e.g., wrong formation state) | **S2**, never propagated | 20 |
| Phone, website, NAICS, SIC or employees BLANK at a bureau | **S3** | 4, 6, 9, 20 |
| Name VARIANT (INC vs CORP; owner middle name or suffix) | **S3** | 17 |
| EQUIVALENT only (punctuation, suffix class, tax classification) | **S4, info** | none |
| Tax-return business code ≠ lender-facing NAICS but the same 4-digit industry group | **S4, info** (TLA does not recommend changing returns) | 4 |

**Roll-up:** any S1 → point 20 is AR and the Legal/Identity area is AR. Any S2 → the owning point is at least AR, unless the analyst documents that the field is cosmetic (e.g., a historical address on a trade-reference record).

### 1.5 Companion "Legal / identity status picture" table

Under the matrix, print one line per item with status and basis: SOS formation, entity type, ownership, management authority, registered agent, EIN documentation, EIN/TIN record consistency, master address, proof of address, NAICS/SIC, licensing, foreign qualification. **EIN documentation** (does a CP 575/147C exist?) and **EIN record consistency** (does every record carry it?) are separate lines. Where governing documents and SOS filings tell different organizational-history stories (e.g., a shelf/aged entity acquired later), add an **Entity History** chain (date | event | source document) and an NI "document-consistency note." TLA never determines which document controls or sets an ownership-transfer date.

---

## 2. Master Business Address Decision

### 2.1 Classify every address found before presenting candidates

| Class | Definition | Displayed as |
|---|---|---|
| **Active candidate** | The business plausibly operates from it or is entitled to use it, and it appears on ≥1 lender-facing record (IRS, SOS principal office, bank, bureau, UCC debtor address) | "Active lender-facing address candidates: a decision is required" |
| **Bureau correction** | Shown by a bureau as current, but it is not and never was a business location (prior manager, organizer, filing service) | "Commercial bureau correction: not an address candidate" |
| **Record / statutory** | Registered-agent office, governing-person address, organizer or filing-agent correspondence address, superseded RA | "Record addresses: historical or statutory only" |
| **Personal** | Guarantor residence(s) from consumer reports | Shown only if it also appears on a business record |

### 2.2 Candidate assessment criteria (show each as Yes / No / Unknown)

1. **Legitimate:** the business actually operates there or has a right to use it (lease, ownership, service agreement, staffed coworking membership).
2. **Provable:** can produce lease/deed, utility or telecom bill, or a service agreement in the legal name, dated within 90 days [EXP].
3. **Commercial vs residential:** residential is acceptable and truthful for home-based businesses. Note that some lenders and issuers treat a residence on a commercial file as a soft negative [DP].
4. **CMRA / virtual / PO box:** a USPS CMRA requires PS Form 1583 and is addressed with "PMB" [PUB, USPS]. A PO box is never a physical address. Google Business Profile does not accept virtual offices or remote mailboxes as a location [PUB, Google guidelines]. Many lenders refuse PO boxes and decline or manually review CMRAs [DP]. **A CMRA may be used only if it is disclosed as such ("PMB" retained) and the business has a separate truthful physical location on file where required.**
5. **Record alignment:** how many of IRS, SOS principal office, bank, UCC debtor address and bureaus already carry it. More alignment means fewer filings to change.
6. **Filings required if chosen:** IRS Form 8822-B (only if the IRS record differs), SOS principal-office/RA change (state-specific), bank update, bureau updates.

### 2.3 What TLA must and must not do

- **TLA does not select the address.** The report presents candidates, trade-offs and the filings each choice triggers. The client designates the address and provides proof. Fixed sentence: *"TLA does not decide the factual operating address; the client must select the legitimate, supportable lender-facing address and provide proof."*
- Never recommend an address the business doesn't use or have a right to use. Never recommend acquiring a virtual office **to make a business look commercial** or to hide a home base. Virtual-office vendors may appear in the directory only as "commercial business address, if needed," for a real operational need.
- Recommend an IRS filing **only if the IRS record must change**. Otherwise state "no IRS filing required."
- Any need to amend a UCC financing statement is determined by the **secured party**, not TLA.
- Point 15 can't PASS until the address is designated, proven and propagated.

### 2.4 Propagation checklist (in order, after designation and proof)

1. IRS: Form 8822-B if the business location or mailing address changed (4–6 weeks; responsible-party changes are due within 60 days) [PUB]. Optional Letter 147C afterward as KYC evidence.
2. SOS: principal-office / mailing-address update or annual-report correction (state-specific). RA office only if the client wants it to follow.
3. Bank(s): account profile, statement address, beneficial-ownership certification refresh, W-9.
4. Experian (BusinessCreditFacts), D&B (D-U-N-S Manager), Equifax Commercial (Research Request Form).
5. LexisNexis business file (after it's obtained).
6. 411 / directory listing; Google Business Profile (only after designation, because verification locks in the address).
7. Website footer/contact page, email signature.
8. Licenses, insurance, card issuers, vendors and reporting tradelines.
9. Re-verify each bureau 30–45 days after submission. Record results in the correction tracker.

---

## 3. The 20 points

**Format:** Inputs · Status logic · PASS standard · Typical findings · Why it matters · Correction template · Where to fix · Research.

### 01 EIN / IRS Identity
- **Inputs:** CP 575 or 147C (SS-4 supporting); bank W-9 / beneficial-ownership certification; bureau Tax ID fields; tax returns' EIN.
- **Status:** N/A only for a sole proprietor with no EIN who uses an SSN (note: most business-credit lanes need an EIN, AP-49). **PEND** if no IRS EIN document is uploaded. **AR** on any S1 TIN conflict, an EIN document in a different name or entity than the SOS record, or evidence that an EIN from a prior structure is being reused after an entity-structure change (IRS "Do You Need a New EIN?" [PUB]). **NI** if the EIN is documented and consistent but the IRS name/address on the notice is outdated relative to the master record. **PASS** otherwise.
- **PASS standard:** "One EIN matching exactly across the IRS record, the bank record and all commercial bureau files, with the IRS EIN notice on file."
- **Typical findings:** a different TIN on the bank certification; SS-4 only, no CP 575; a sole-prop EIN carried into an LLC; IRS address = old residence.
- **Why it matters:** "The EIN is the primary key lenders, banks and bureaus use to match the business. A mismatch can fail KYC or TIN matching outright and fragment bureau files. This is an identity issue, not a tax matter."
- **Correction:** "Obtain the [bank] account profile and current W-9; if the TIN on file differs from the IRS-issued EIN, have the bank correct it before any application. A Letter 147C is optional supporting evidence only [if a lender requires it / after an IRS address update]."
- **Where:** Bank relationship officer; IRS Business & Specialty Tax Line 800-829-4933 (147C, authorized person) [PUB]; Form 8822-B for address or responsible-party changes [PUB].
- **Research:** none external. Cross-check every document's EIN digit by digit.

### 02 Secretary of State Registration
- **Inputs:** formation document; amendments; certificate of status (good standing / existence / fact); live SOS search.
- **Status:** **PEND** if no formation document and no live search. **AR** if the status is not active (forfeited, delinquent, administratively dissolved, inactive), the entity is not found, or Tier A documents conflict on state or type. **NI** if active but the annual report is due within 60 days or overdue-but-curable, or the status certificate is >90 days old with submission imminent [EXP]. **PASS** if active with a complete filing chain.
- **PASS standard:** "Entity documented as validly formed with a complete filing chain and an active status on the live state record, with a fresh status certificate obtained near submission where the lender requires it."
- **Typical:** forfeited for a missed annual report or franchise tax; amendment checkbox conflicts with formation (LLC vs PLLC); intake state ≠ SOS state.
- **Why:** "Lenders confirm the entity exists and is in good standing before closing; a lapsed entity can't sign loan documents."
- **Correction:** "File the overdue [annual report / reinstatement] with the [State] SOS and obtain a current certificate of [status]."
- **Where:** the formation state's SOS business-entity search and certificate ordering (find via NASS directory).
- **Research (required):** SOS search by exact name **and** filing number. Capture status, formation date, entity type, principal office, RA, managers/officers, filing history and the date of the search.

### 03 Registered Agent
- **Inputs:** current SOS record; RA-change filings.
- **Status:** **AR** if there's no agent, the agent resigned, the agent is listed at a non-street address, or SOS flags the agent. **NI** if the agent is current but the RA office is the only address in circulation and is being used as a business address, or the RA is the owner's residence while an address decision is pending (informational trade-off). **PEND** without an SOS record. **PASS** if a current designation has a street address in-state.
- **PASS standard:** "A registered agent on file at the Secretary of State with a current designation and an in-state street address."
- **Why:** "A valid agent keeps the entity in good standing and ensures legal notices are received."
- **Correction:** "File a change of registered agent/office with the [State] SOS; never present the agent's office as the business address."
- **Where:** state SOS change-of-agent form. **Research:** included in the Point 2 search.

### 04 NAICS / SIC Consistency
- **Inputs:** intake description and NAICS; tax-return business code; Experian/D&B/Equifax codes; website description.
- **Status:** **PEND** if no bureau file and no client selection. **AR** on any S2 conflict, or a code that doesn't describe the actual primary revenue activity. **NI** if the codes are consistent but blank at one bureau, or a borderline/restricted industry (HR-34). **PASS** if one NAICS and one SIC are identical across bureaus and consistent with the description.
- **PASS standard:** "One truthful NAICS and one truthful SIC, identical across all commercial bureaus and consistent with the description of business used on applications."
- **Why:** "Underwriting and automated screens route by industry code; many lenders keep restricted-industry lists, and a blank code can't be benchmarked."
- **Correction:** "Confirm [NAICS] as the truthful primary classification and propagate it with the matching SIC to each bureau. TLA does not recommend changes to tax-return classification."
- **Where:** Census NAICS search [PUB]; OSHA SIC Manual; Experian BusinessCreditFacts; D&B D-U-N-S Manager; Equifax Research Request.
- **Research:** Census keyword search; SIC concordance; read the website's service description.
- **Guardrail:** never pick a code to avoid a restricted list (G-04).

### 05 Licensing (if applicable)
- **Inputs:** activity description; licenses uploaded; state/local licensing research.
- **Status:** **N/A** when TLA research finds no specialized occupational or professional license for the documented activity (record the sources). **AR** if a required license is missing, expired, or held in a different name. **NI** if the license is valid but in a variant name or at a non-master address. **PEND** if the activity is plausibly regulated and research is not yet complete. **PASS** if a current license is on file matching legal name and master address.
- **PASS standard:** "Either a documented determination that no specialized license is required, or a current license on file matching the exact legal name and master address."
- **Why:** "Operating without a required license is a hard decline; claiming one that doesn't exist is a misrepresentation."
- **Correction:** "Obtain/renew [license] from [agency] in the exact legal name."
- **Where:** SBA "Apply for licenses and permits"; state licensing board(s); state business-permit portal; city/county.
- **Research checklist:** the state occupational-licensing agency and board for the activity; industry federal licensing (e.g., transportation, firearms, alcohol, financial services); state license lookup by name. Local zoning and general business permits are noted separately and are not this point's test.

### 06 Business Phone / 411
- **Inputs:** intake phone; 411/directory result; bureau phone fields; website and GBP phone.
- **Status:** **AR** if there's no business phone, the number is the owner's personal cell listed in the owner's name, the bureaus are blank, or the number is unverified. **NI** if listed but in a variant name or address, or populated at only one bureau. **PEND** if a number is provided and verification is not yet run. **PASS** otherwise.
- **PASS standard:** "A dedicated business number listed in directory assistance under the exact legal name and master address, populated at every commercial bureau."
- **Why:** "A listed, verifiable phone is one of the most commonly checked data points; some lenders and issuers verify it against name and address."
- **Correction:** "Confirm the business controls the number, list it under the exact legal name and master address, then add it to each bureau, the website and Google profile."
- **Where:** ListYourself.net (free national directory-assistance listing); carrier listing service; bureau update channels.
- **Research checklist:** 411 lookup by name + city; reverse lookup of the number; check that the line answers in the business name; check that the GBP and website show the same number.

### 07 Business Domain
- **Inputs:** domain from intake/email/website; RDAP data.
- **Status:** **AR** if no domain exists, it has expired, or it is registered to an unrelated party. **NI** if active but registered personally (where visible), expiring within 60 days, or not matching the legal or trade name. **PASS** if active, matches the name, and the business controls it.
- **PASS standard:** "An active domain matching the legal or filed trade name, controlled by the business."
- **Why:** "A matching domain supports identity verification and underpins professional email, the website and the Google profile."
- **Correction:** "Register [name].[tld] in the business name, or update the registrant organization; enable auto-renew."
- **Where:** registrar of record. **Research:** ICANN RDAP lookup (registrar, creation and expiry dates; registrant is often redacted, so don't infer ownership from redaction).

### 08 Professional Email
- **Inputs:** intake business email; MX check.
- **Status:** **AR** if the business uses free-mail (gmail/yahoo/etc.) on applications. **NI** if a domain mailbox exists but free-mail is still used on bank or bureau records. **PASS** if domain email is used consistently.
- **PASS standard:** "All applications and bureau correspondence sent from a domain-matched business email address."
- **Why:** "Several lenders treat free-mail addresses as a minor negative signal, and bureau updates from a domain-matched officer address carry more weight."
- **Correction:** "Create [role]@[domain] and use it on the bank, bureaus, applications and directories."
- **Where:** email host for the domain. **Research:** DNS MX lookup on the domain; send-test not required.

### 09 Website
- **Inputs:** URL; page content; bureau URL fields.
- **Status:** **AR** if there is no site or it is a parked page. **NI** if live but missing legal name, contact information, or NAP consistency, or the content conflicts with the NAICS/description. **PASS** if a live site represents the business; bureau URL propagation is tracked under Point 20.
- **PASS standard:** "A live website representing the business, showing the legal or filed trade name and the master address/phone consistently."
- **Why:** "When the bureau file is thin, analysts look for a coherent web presence to corroborate the business."
- **Correction:** "Publish a site with legal name, master address (or service area), business phone and a description matching [NAICS]; submit the URL to each bureau."
- **Where:** domain host; bureau update channels. **Research:** load the site; check footer/contact NAP vs master; check that services match the description.

### 10 Business Banking
- **Inputs:** ≥3 months of statements (all pages); bank, account title, account age; beneficial-ownership certification.
- **Status:** **PEND** if statements are missing. **AR** if there's no account in the legal name, funds are commingled in a personal account (AP-40), the account title name ≠ legal name, or statements show alteration signals (HR-29 → BA). **NI** if statements show NSF/negative days, ADB is weak, or the account is <6 months old (thresholds in RULEBOOK §6). **PASS** otherwise.
- **PASS standard:** "Three or more months of complete statements; account titled in the exact legal name; statement address matching the master address; no NSF or overdraft activity; deposits consistent with reported revenue."
- **Why:** "Statements show real cash flow; lenders compare deposits to stated revenue and check balances and overdrafts."
- **Correction:** "Provide [3/6] consecutive months for every business account; align account title and address to the master record."
- **Where:** online banking or the relationship officer. Distinguish deposit, credit and client-reported relationships; never present them as the same.

### 11 Business Credit Bureaus (brief; detail by the bureau expert)
- **Inputs:** Experian, D&B, Equifax/SBFE reports ≤90 days old.
- **Status:** **PEND** if a bureau isn't obtained or returns INSUFFICIENT DATA (no negative scoring). **AR** if identity fields are wrong at a bureau, or scores fall in the bottom bands. **NI** if the file is scored but thin. **PASS** if all files are ≤90 days old, identity is identical, and both Experian and D&B generate a score.
- **PASS standard:** "All commercial bureau files reviewed within 90 days, identity data identical across them, and a generated score at Experian and D&B."
- **Where:** see Resource Directory. Fix identity before building depth.

### 12 Vendor / Payment Experiences (brief)
- **Status:** **AR** if there are <3 reporting trade experiences, or no PAYDEX can be generated. **NI** with 3–4 lines, or reported slow pay. **PASS** with ≥3 reporting accounts with ≥6 months on-time history.
- **Rule:** build only after Points 1, 15, 17 and 20 are corrected; accounts must be real, used for actual business purchases, and paid on time. Never recommend tradeline products or fabricated trade references.

### 13 LexisNexis (brief)
- **Status:** **PEND** until the business file is obtained. **AR** if it shows a second identity, an unexplained address, or a wrong TIN linkage. **PASS** with one identity and no unexplained records within 90 days.
- **Where:** LexisNexis Risk Solutions business-file request (per TLA directory); the guarantor separately requests the personal Consumer Disclosure Report.

### 14 Google Business Profile
- **Inputs:** GBP search result; owner access; verification status.
- **Status:** **N/A** if the business is ineligible under Google's guidelines (e.g., online-only with no staffed location and no in-person service area). Do not push a profile that would breach the guidelines. **PEND** if no profile is documented and the master address is not yet designated (verification would lock in the wrong address). **AR** if a profile exists showing a wrong name, address or phone, is unclaimed, or is suspended, or the business is eligible with no profile after the address is designated. **NI** if verified but NAP is partially inconsistent. **PASS** otherwise.
- **PASS standard:** "A verified profile (or a documented ineligibility determination) whose name, address or service area, and phone match the master record, website and directory listing."
- **Why:** "A verified profile is low-cost independent corroboration of name, address and phone."
- **Correction:** "After designating the master address, create or claim and verify the profile using the exact legal or filed trade name; use service-area mode if you don't receive customers at the address."
- **Where:** business.google.com; guidelines support.google.com/business/answer/3038177. Verification may be by phone, text, email or video [PUB].
- **Guardrail:** GBP guidelines exclude virtual offices and remote mailboxes. Never advise a virtual office or keyword-stuffed name to obtain a listing.
- **Research:** Google Maps search by name + city and by phone; note duplicates and claimed status.

### 15 Proof of Business Address
- **Inputs:** all addresses (matrix F6/F7); client designation; proof document.
- **Status:** **AR** with no designation and ≥2 active candidates (S1), a bureau showing a bureau-correction address, an undisclosed CMRA or PO box used as a physical address, or a designated address not yet propagated. **PEND** if designated but proof not received. **NI** if designated, proven and propagated but the address is residential or a disclosed CMRA with a known lender-acceptance impact (informational trade-off, no correction implied). **PASS** if one master address appears identically everywhere with proof on file.
- **PASS standard:** "One master address appearing identically at the IRS, the bank, all commercial bureaus, LexisNexis, the website, the Google profile and directory assistance, with supporting proof in the funding file."
- **Why:** "Address consistency is the backbone of business identity verification; conflicting addresses trigger manual review and document requests."
- **Correction:** "Designate one Master Business Address with proof; propagate per the §2.4 checklist; correct [bureau] using [supporting filing]."
- **Where:** Section-06 decision page; Form 8822-B (only if the IRS record changes); bureau channels.
- **Research:** USPS ZIP lookup to standardize; check CMRA/PMB status (USPS) and whether a street address belongs to a known virtual-office or RA provider; check Street View/occupancy where relevant (internal note only).

### 16 Foreign Qualification
- **Inputs:** formation state; operating locations; employees, property, inventory by state; master address state.
- **Status:** **N/A** if documented that there's no out-of-state nexus. **AR** if the master address, an office, employees or property sit in a state where the entity is not registered (common for home-state businesses formed in another state for perceived benefits). **NI** if registered but the foreign registration is not in good standing or the RA lapsed. **PEND** if the nexus facts are unknown. **PASS** if registered in every nexus state.
- **PASS standard:** "Registered in every state where the company transacts business, or documented confirmation that no out-of-state nexus exists."
- **Why:** "An unregistered company can face penalties and may be barred from enforcing contracts in that state; lenders check this in diligence."
- **Correction:** "File a [certificate of authority / foreign registration] with the [State] SOS and appoint an in-state agent."
- **Where:** the nexus state's SOS. **Research:** SOS search in the operating state for the entity name; compare against the master-address state. "Doing business" thresholds are state-defined, so recommend counsel when facts are borderline.

### 17 Legal Name / DBA Consistency
- **Inputs:** matrix F1–F3; assumed-name filings; trade name used on the website, GBP, signage and bank.
- **Status:** **AR** on S1/S2 name or type conflicts, a blank legal name at a bureau, or a trade name used in commerce without a filed assumed name. **NI** on VARIANT only (INC/CORP; owner name formatting). **PASS** if identical (EQUIVALENT allowed) everywhere and any trade name is filed.
- **PASS standard:** "Identical legal name and entity type across SOS, IRS, bank, all bureaus and LexisNexis, with any trade name properly filed."
- **Why:** "Entity-type and name mismatches are a known cause of split bureau files that never build full history."
- **Correction:** "Adopt the SOS spelling and entity type as controlling; correct [bureau] with the formation document and status certificate; file an assumed name for [trade name]; standardize one owner-name format."
- **Where:** bureau channels; state or county assumed-name filing (varies by state).
- **Research:** assumed-name search (state or county); confirm the live SOS type.

### 18 Public Records / UCC (brief)
- **Status:** **NI** for legitimate filings that are understood (collateral constraint, not a defect). **AR** for liens, judgments or a filing that appears erroneous. **PEND** if the search is not done. **PASS** if no filings, or all are understood and the collateral is addressed.
- **Rule:** TLA makes no lien-priority determination; amendments belong to the secured party. Research = SOS UCC debtor search under every name variant and the master address. Judgments and liens come from intake and documents (R20).

### 19 Duplicate Business Files (brief)
- **Status:** **PEND** until an explicit search at each bureau and LexisNexis under every TIN, name variant and address. **AR** if a second file is confirmed. **PASS** with one file per bureau confirmed.
- **Rule:** contradictory data inside one file belongs under Point 20. Never call it a duplicate without a found second record.

### 20 Core Business Record Consistency
- **Inputs:** the full matrix.
- **Status:** **AR** on any S1, or ≥2 S2 [EXP]. **NI** on one S2 or only S3 blanks. **PEND** if fewer than two Tier C sources are obtained (consistency can't be tested). **PASS** if all rows MATCH or are EQUIVALENT.
- **PASS standard:** "One legal name, one entity type, one EIN, one master address, one phone, one website, one NAICS/SIC pair and one revenue basis appearing identically on every record a lender can pull."
- **Why:** "Record inconsistency is one of the largest drivers of automated declines that are never explained to the applicant."
- **Correction sequence (fixed):** TIN (1) → master address (15) → name/type (17) → NAICS/SIC, phone, website (4, 6, 9) → supportable revenue and employees → re-verify each bureau after 30–45 days → only then build depth (12).
- **Where:** Action Center and Resource Directory.

---

## 4. Rating the five lender areas

| Area | Core inputs | Supporting inputs |
|---|---|---|
| Business Legal / Identity | Points 1, 2, 15, 17, 20; matrix S1/S2 | 3, 5, 6, 7, 8, 9, 14, 16; entity-history note |
| Business Credit | 11, 12, 19; Part II bureau analysis | 4, 13, 18 |
| Banking / Financials | 10; Part II statements, returns, financial-document consistency (R10, HR-25/26) | 18 (collateral availability) |
| Personal Guarantor | RULEBOOK GF, HR flags, ID gates (never the 20 points) | Personal-address consistency |
| Funding Goal / Structure | Amount, use of proceeds, repayment source, timeline; RULEBOOK G\*, H, coverage cap | Steer-away rules, PG exposure (R8) |

**Rule (applied in order) [EXP]:**
1. **AR** if any core input is AR, any S1 exists (Legal/Identity), or a RULEBOOK hard block or BA HR touches the area.
2. **NI** if any supporting input is AR, any core input is NI, or ≥2 supporting inputs are NI.
3. **PEND** if any core input is PEND and nothing above applies.
4. **PASS** otherwise. Supporting PEND items are noted in the narrative.

**Personal Guarantor specifics:** AR if GF <620, any hard knock-out, or BA/BP HR. NI if GF 620–679, or any advisory HR (inquiries, a recent late, address inconsistency across bureaus). PASS if GF ≥680 with no open HR.

**Funding Goal specifics:** AR if amount or purpose is missing, the purpose is ineligible, or MCA steer-away fires. NI if use of proceeds, repayment source or terms are undocumented, or the coverage cap applies. PASS if documented and matched to a product in G\*.

**Narrative template (2–4 sentences):** what passes → what remains → the single root cause. "Formation, ownership and EIN documentation pass. What remains is record consistency: [top 2–3 items]."

---

## 5. Ordering, actions, concentration, and the composite score

### 5.1 Priority Risk & Correction Flags (ordered by underwriting impact)
Sort key: **impact tier → status (AR > NI > PEND) → number of downstream items unlocked → number of products affected.**

| Tier | Class |
|---|---|
| T1 | Identity/KYC failures: S1 matrix items, TIN conflict, no master address, SOS not active, RULEBOOK hard blocks |
| T2 | Automated-screen failures: wrong or blank bureau identity fields, entity-type conflict, thin/no bureau score |
| T3 | Financial-package consistency (statements vs returns vs debt schedule vs PFS): NI wording, "confirmation by the client's financial professional" |
| T4 | Collateral/UCC position |
| T5 | Guarantor advisory items |
| T6 | Infrastructure (phone, email, GBP, website propagation) |
| T7 | Pending documents and sources |

Each flag carries: short title, status, and a one-sentence underwriting consequence. Don't include account or filing numbers on client-facing flags beyond what the client needs to act on.

### 5.2 First Three Actions (gating items)
1. Build a dependency graph. Standing edges: TIN fix → bureau corrections → depth building; master address → 411, GBP, bureau address, proof (15); identity lock (17/20) → Point 12 building; SOS reinstatement → everything; bank account in legal name → all cash-flow lanes.
2. Candidates = AR items that are client-actionable now (not "wait").
3. Score = tier weight (T1=3, T2=2, else 1) × (1 + count of downstream dependents). Take the top 3. Ties go to the lower tier number.
4. If fewer than three gating items exist, fill with the highest-ranked remaining AR. The third action is often a bundle ("Lock the commercial business identity").
5. Everything else that is open goes under "Secondary open items, important but not gating," with status and note.

### 5.3 "Where the weaknesses are concentrated"
Group non-PASS points by root cause. Show only groups with ≥1 non-PASS point, ordered by number of points.

| Root cause | Points |
|---|---|
| Lender-facing identity consistency | 1, 15, 17, 19, 20 |
| Verifiable business infrastructure | 6, 7, 8, 9, 14 |
| Commercial bureau depth and alignment | 4, 11, 12 |
| Legal standing | 2, 3, 5, 16 |
| Documents/sources outstanding | any PEND (10, 13, 19…) |
| Research completed in this audit | points TLA resolved by research (5, 16, 18) |

Template: "[n] of the twenty points trace to [root cause]: [one-sentence consequence]. Fixing [X] resolves most of the audit."

### 5.4 Composite Funding Readiness Score: withhold vs issue
**Issue only if ALL are true [EXP]:**
1. No open S1 identity conflict (TIN, legal name, formation state, undesignated master address). The score must describe one identity.
2. None of Points 1, 2, 10, 15, 20 is PEND, and ≤2 points total are PEND.
3. Experian and D&B business files were obtained ≤90 days ago, and the 3-bureau personal report was obtained within RULEBOOK §1.5 staleness.
4. ≥3 months of business bank statements are in hand (R19 staleness).
5. Funding amount and use of proceeds are stated.
6. No RULEBOOK hard block or BA HR is open.

**Otherwise print "Withheld"** with the fixed rationale ("TLA does not publish a composite score on an incomplete file, because doing so misrepresents the business in both directions") and a numbered list of the specific failed conditions as "unlocks."

**Computation when issued [EXP, team-tunable]:**
- Point values: PASS 100, NI 60, AR 20, PEND excluded, N/A excluded. Core points (1, 2, 15, 17, 20) weight 2; others weight 1.
- Area score = weighted mean of its points (Legal/Identity, Business Credit, Banking), plus Part II factors for Credit and Banking. Guarantor = RULEBOOK GF mapping (≥740 100, 680–739 85, 620–679 60, <620 25), minus 10 per open advisory HR (floor 0). Funding Goal = RULEBOOK headline H.
- Composite = 0.25 Legal/Identity + 0.20 Business Credit + 0.25 Banking + 0.20 Guarantor + 0.10 Funding Goal.
- Caps: any open AR in a core point → cap 79; ≥5 AR points → cap 64.
- Tier vocabulary per RULEBOOK R17. Never presented as approval likelihood (G-07). The composite is distinct from the RULEBOOK §9 product headline and is printed separately.

---

## 6. Resource Directory (official channels; national, with the state pattern)

| Resource | Points | Access |
|---|---|---|
| IRS Business & Specialty Tax Line | 1, 15 | 800-829-4933, Mon–Fri 7am–7pm local; Letter 147C by fax/mail to an authorized person |
| IRS Form 8822-B | 1, 15 | irs.gov/form8822b: business mailing/location address and responsible-party changes |
| IRS "Do You Need a New EIN?" | 1 | irs.gov: structure-change guidance |
| State Secretary of State (pattern) | 2, 3, 16, 17, 18 | "[State] SOS business entity search," certificate of status/good standing, change of agent, annual report, assumed name, UCC debtor search; find the office via nass.org |
| County clerk (pattern) | 17 | Assumed-name / DBA filings in county-filing states |
| SBA: Register your business; Apply for licenses and permits | 2, 5, 16 | sba.gov business guide |
| U.S. Census NAICS | 4 | census.gov/naics |
| OSHA SIC Manual | 4 | osha.gov/data/sic-manual |
| USPS ZIP Code Lookup / Pub 28 | 15 | tools.usps.com; pe.usps.com/text/pub28 |
| USPS CMRA FAQ | 15 | faq.usps.com (CMRA, PS Form 1583) |
| Experian BusinessCreditFacts | 4, 6, 9, 15, 17, 20 | businesscreditfacts.com: authenticated-officer identity updates |
| Experian Commercial Relations (disputes) | 11, 17, 19 | Per TLA directory; verify contact before publishing |
| D&B D-U-N-S Manager | 4, 6, 9, 15, 19, 20 | dnb.com D-U-N-S Manager (free view and update) |
| Equifax Commercial | 4, 11, 15, 19 | commercialdisclosures@equifax.com → report plus Research Request Form |
| LexisNexis Risk Solutions | 13, 19 | Business-file request (per TLA directory); personal disclosure at consumer.risk.lexisnexis.com |
| ListYourself.net | 6 | Free national directory-assistance listing |
| Google Business Profile | 14 | business.google.com; guidelines support.google.com/business/answer/3038177 |
| ICANN Lookup (RDAP) | 7 | lookup.icann.org |
| FinCEN CDD rule reference | 1, 20 | fincen.gov: bank beneficial-ownership certification context |

**Note on BOI:** since FinCEN's March 2025 interim final rule, U.S.-formed entities are exempt from CTA BOI reporting [PUB]. Banks still collect beneficial ownership under the CDD rule (31 CFR 1010.230: each ≥25% owner plus one control person) [PUB]. The report must not tell domestic clients to file BOI. It may ask them to confirm their bank certification is current.

---

## 7. Plain-English client explanations

| # | What this is | Why lenders care |
|---|---|---|
| 01 | Your EIN is your business's federal tax ID, issued by the IRS. It's the number that identifies your company on every bank, bureau and loan record. | Lenders match your business by this number. If any record shows a different number, the application can stop at identity verification. |
| 02 | Your state registration is the filing that legally created your company with the Secretary of State, plus its current standing. | A lender can only lend to a company that legally exists and is in good standing. A lapsed filing can stop a closing. |
| 03 | Your registered agent is the person or company the state has on file to receive legal notices for your business. | A missing or lapsed agent can put your company out of good standing. Lenders check it as part of basic legal review. |
| 04 | NAICS and SIC codes are standard numbers that describe what industry you're in. | Lenders sort and screen applications by industry. A blank or conflicting code can put you in the wrong group or on a restricted list. |
| 05 | Some industries need a state or professional license to operate. This point checks whether yours does and whether it's current. | Operating without a required license is usually an automatic decline. A documented "not required" answer removes the question. |
| 06 | This is a business phone number listed under your company name in directory assistance (411). | Many lenders and card issuers check that a listed phone matches your business name and address. It's a quick sign the business is real. |
| 07 | Your domain is your web address (yourbusiness.com), owned by the company. | A matching domain helps prove the business is established and supports your website and email. |
| 08 | A professional email uses your own domain (you@yourbusiness.com) instead of a free service. | Some lenders see free email on an application as a small warning sign. Bureaus also give more weight to update requests from a business address. |
| 09 | Your website describes your business, products and contact details. | When your credit file is thin, underwriters look online to confirm the business is real and does what you say. |
| 10 | This covers your business bank account in the company's legal name and your recent statements. | Statements show lenders your real cash flow, balances and any overdrafts. Most business loans start here. |
| 11 | Business credit bureaus (Experian, Dun & Bradstreet, Equifax) keep credit files on companies, separate from your personal credit. | Lenders pull these files to score your business. Missing, thin or wrong files limit what you can qualify for. |
| 12 | These are vendor and supplier accounts that report your on-time payments to the business bureaus. | Business scores are built from reported payment history. Without it, even a profitable company can look brand new. |
| 13 | LexisNexis is a data company many lenders use to verify identity and check public records on a business. | It's often where duplicate or conflicting records show up, so lenders rely on it to confirm who they're dealing with. |
| 14 | Your Google Business Profile is the listing that shows your business on Google Search and Maps. | A verified profile is independent proof of your name, address and phone, and lenders can check it in seconds. |
| 15 | This is the one business address you use everywhere, plus documents that prove it (a lease or utility bill). | When different records show different addresses, lenders slow down, ask for more documents, or quietly decline. |
| 16 | If your company was formed in one state but operates in another, it usually has to register in the second state too. | An unregistered company can face penalties and may be unable to enforce contracts there. Lenders check this. |
| 17 | Your exact legal name and entity type (LLC, corporation), plus any registered trade name (DBA). | Small name or type differences can split your business into separate credit files that never build full history. |
| 18 | This checks for liens, judgments and UCC filings, the public notices lenders file when they take business assets as collateral. | Existing filings affect what collateral is still available and which loans you can get next. |
| 19 | This checks whether a bureau has more than one file for your business. | Payments can land on a file the lender never pulls, so your good history doesn't count. |
| 20 | This is the overall check that every record (IRS, state, bank, bureaus, online) describes your company the same way. | Mismatched records are one of the biggest reasons applications get declined without explanation. Fixing this resolves most of the audit. |

---

## 8. Compliance guardrails for entity and identity work

Add these as G-ID entries to the RULEBOOK §12 blocklist and filter.

1. **Time in business:** never recommend buying aged or shelf entities to claim time in business. When an entity was acquired, the report states "time in business on applications = the date the business actually began operating" (AP-49) and flags HR-27. The report describes a shelf history factually and never as an advantage.
2. **No fabricated identity elements:** never create, suggest or "optimize" addresses, phone numbers, websites, employees, revenue or trade references that don't reflect real operations. Bureau updates submit only documented, truthful values. The lower-of revenue rule applies (R10).
3. **TLA does not select the master address.** The client designates it and proves it.
4. **CMRA, virtual office and PO box:** these must be disclosed as such ("PMB" retained). Never advise dropping the PMB designation, presenting a mail drop as a physical office, or acquiring a virtual office to mask a home base or to qualify for GBP. Virtual offices are listed only "if needed" for a real operational need.
5. **No EIN as SSN substitute** on personal applications, and no new or alternate identities (G-03). A second EIN is recommended only where IRS rules require one for a structure change, never to "start fresh."
6. **Industry codes** must truthfully describe the primary revenue activity. Never select a code to avoid a restricted-industry list. Never recommend changing tax-return codes.
7. **Disputes at business bureaus** cover only inaccurate or outdated data, with supporting documents. Never "dispute everything" or remove accurate negative trade or public-record data.
8. **No legal conclusions:** TLA does not determine lien priority, which governing document controls, ownership-transfer dates, or foreign-qualification nexus in borderline cases. Refer these to counsel or the secured party.
9. **No tax advice:** IRS filings are recommended only for identity-record accuracy (8822-B, 147C), never for tax positions. Say "This is identity documentation, not tax advice."
10. **Accurate beneficial-ownership data:** the bank's certification must reflect actual owners and control persons. Never advise omitting a ≥25% owner or restructuring ownership on paper to avoid a guarantor.
11. **Licensing:** never advise operating without a license, or implying a license that is not held. A "no license required" finding must cite research sources and the date.
12. **Privacy:** full EINs and street addresses stay internal or client-only. Funder-facing profiles show city/state only and the last 4 digits of the EIN (G-11, §13).
13. **Directory and GBP listings** must follow the platform's rules (eligibility, real name, no keyword stuffing).
14. **"Insufficient data" is never scored negatively.** It shows as PEND with the source to obtain.

---

### Sources consulted
- [IRS About Form 8822-B](https://www.irs.gov/forms-pubs/about-form-8822-b) · [IRS Business & Specialty Tax Line / 147C overview](https://www.zenind.com/help/post/how-to-request-an-irs-ein-verification-letter-147c-in-2026) · [IRS TIN matching / Pub 1281 context](https://www.resourcefulfinancepro.com/articles/spring-b-notice-season/)
- [FinCEN CDD FAQ (31 CFR 1010.230)](https://www.fincen.gov/sites/default/files/2018-04/FinCEN_Guidance_CDD_FAQ_FINAL_508_2.pdf) · [FinCEN BOI page (March 2025 interim final rule)](https://www.fincen.gov/BOI) · [Davis Polk summary](https://www.davispolk.com/insights/client-update/fincen-eliminates-beneficial-ownership-reporting-requirements-u-s-companies)
- [USPS CMRA FAQ](https://faq.usps.com/articles/Knowledge/Commercial-Mail-Receiving-Agency-CMRA) · [USPS Pub 28 suffixes](https://pe.usps.com/TEXT/pub28/28c2_015.htm)
- [Google Business Profile guidelines](https://support.google.com/business/answer/3038177) · [GBP video verification](https://support.google.com/business/answer/14271705)
- [OSHA SIC/NAICS FAQ](https://www.osha.gov/faq/2-1) · Census NAICS (census.gov/naics)
- [ICANN RDAP lookup](https://www.icann.org/news/blog/updated-lookup-tool-for-domain-name-registration-data-now-available)
- [D&B D-U-N-S Manager](https://www.dnb.com/en-us/smb/duns/duns-manager.html) · [Experian business credit information](https://www.experian.com/small-business/business-credit-information) · [Equifax commercial disclosure process](https://ficoforums.myfico.com/t5/Business-Credit/Equifax-Business-Report-free/td-p/6642948) (community source; confirm with Equifax)
- [LexisNexis Small Business Credit Report](https://risk.lexisnexis.com/products/small-business-credit-report) · [ListYourself.net overview](https://localiq.com/blog/411-directory-listings/)
