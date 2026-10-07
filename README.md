# Funding Readiness Audit (FRA) tool

Internal tool for Tradeline Associates Inc. analysts. It reads a client's documents, runs the
council-designed rules, and drafts the branded FRA client report for analyst review.

```
Intake + documents ──► AI reads documents ──► analyst confirms data ──► rules engine
      ──► AI drafts plain-English narrative ──► analyst review & release ──► branded PDF
```

- **The AI only reads and writes.** It transcribes documents into structured data and drafts
  narrative text from the engine's results. Every status, score, range and recommendation comes
  from fixed, editable rules (`fra/engine/`, `fra/config.py`).
- **The analyst stays in charge.** Every extracted value, status and sentence can be edited; status
  overrides need a written reason and are logged.
- **Works without an API key.** Analysts can enter data manually and still generate the report.

## Run it

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export FRA_APP_PASSWORD='choose-a-team-password'
export ANTHROPIC_API_KEY='…'          # optional: enables AI reading and drafting
streamlit run app.py
```

Click **Load demo** to open a fictional client ("Northwind Example LLC") and click through all six tabs.

PDF generation uses WeasyPrint, which needs Pango on Linux (`apt install libpango-1.0-0 libpangoft2-1.0-0`).
On Windows or Mac, see the WeasyPrint install guide.

## Try it on GitHub (no installs)

**Use the app in your browser (Codespaces):** on the repository page click **Code → Codespaces →
Create codespace on this branch**. After about 2–3 minutes of setup the app starts by itself; if it
doesn't open, use the **Ports** tab and open port 8501. Click **Load demo**.
To turn on the AI reading, first add `ANTHROPIC_API_KEY` under GitHub **Settings → Codespaces →
Secrets** and give it access to this repository. Codespaces are private to your GitHub account.
Stop the codespace when you're done, because usage beyond the free monthly hours is billed.

**Automatic tests (Actions):** every push runs the unit tests, checks that the app starts, and renders
the demo report. Open the **Actions** tab, click a run, and download **demo-report** to see the PDF.

## Workflow (six tabs)

1. **Intake**: the current website questions, plus the funding-goal questions asked first,
   revenue and income, and eligibility questions.
2. **Documents**: upload PDFs or images by type, then **Read with AI**.
3. **Extracted data**: review and edit identity sources, personal credit, business bureaus and financials.
4. **Research**: record the external checks (Secretary of State, 411, Google Business Profile, UCC, domain, licensing…).
5. **Review audit**: the 20 points, five areas, address candidates, product fit; override with reasons.
6. **Report**: AI-drafted narrative (editable), release checklist, stage, **Generate PDF**.

## Where the rules live

| What | File |
|---|---|
| Council rulebook (personal credit, products, sequencing, guardrails) | `docs/RULEBOOK.md` |
| Business bureaus, UCC, duplicate files | `docs/council/r3_commercial_bureaus.md` |
| Identity matrix, 20 points, areas, composite score | `docs/council/r3_identity_audit.md` |
| Report design and client-explanation standards | `docs/council/r3_report_spec.md` |
| Editable thresholds | `fra/config.py` |
| Report wording, point explanations, glossary, disclosures | `fra/content.py` |

## AI cost

Reading uses Claude Opus 5.5 by default (`AI_MODEL` in `fra/config.py`). The app logs each call's
token use and cost per case (sidebar and the Report tab). Rough estimate per audit: a 3-bureau
personal report plus the business reports, returns and statements is about **$2–5** to read, plus
about **$0.30–0.60** for the narrative. Switching extraction to `claude-sonnet-5-5` roughly halves the
reading cost.

## Privacy

- Client files and case data live only under `data/` (or `FRA_DATA_DIR`), which is git-ignored.
- Uploaded documents are sent to the Anthropic API only when an analyst clicks **Read with AI**.
- The narrative step sends a masked fact sheet (no full tax IDs or account numbers), never raw documents.
- The report masks tax IDs to the last 4 digits.
- Set `FRA_APP_PASSWORD` before sharing the app, and host it somewhere private.

## Before using with clients (from the council)

Have counsel review: Credit Repair Organizations Act exposure for paid action plans; sharing client
profiles with funders; state broker rules; keeping tradeline and shelf-company sales separate
from the audit. Confirm the open numbers in `docs/RULEBOOK.md` §14: the SBA Express cap, the prime rate
placeholder and the $100k card-stack ceiling.

## Tests

```bash
python -m pytest -q
PYTHONPATH=. python scripts/render_demo.py   # renders data/out/demo.pdf (add --images for page images)
```
