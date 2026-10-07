"""Funding Readiness Audit — analyst app (Streamlit).

Run:  streamlit run app.py
Env:  FRA_APP_PASSWORD (team password), ANTHROPIC_API_KEY (AI reading and drafting)
"""
from __future__ import annotations

import hmac
import os
import uuid
from datetime import date

import pandas as pd
import streamlit as st
from pydantic import TypeAdapter

from fra import storage
from fra.ai import client as ai
from fra.content import POINTS
from fra.demo import demo_case
from fra.engine.audit import run_audit
from fra.engine.products import PRODUCTS
from fra.models import (Address, BankMonth, BusinessScore, BusinessTradeline, Case, CommercialBureau, CommercialReport,
                        ConsumerCredit, CreditScore, DebtItem, DocType, Document, IdentitySource, Inquiry, Owner,
                        PointOverride, RESEARCH_ITEMS, ResearchFinding, Status, TaxReturn, Tradeline, UCCFiling,
                        UseOfFunds)
from fra.report.render import find_forbidden, render_html, render_pdf

st.set_page_config(page_title="Funding Readiness Audit", page_icon="📊", layout="wide")

NAVY, GOLD = "#17325B", "#B58A2E"
st.markdown(f"""<style>
.block-container {{ padding-top: 1.2rem; }}
h1, h2, h3 {{ color: {NAVY}; }}
.fra-pill {{ display:inline-block; padding:2px 8px; border-radius:3px; font-size:0.72rem; font-weight:700; letter-spacing:.06em; color:#fff; }}
.fra-PASS {{ background:#1F7A35 }} .fra-NI {{ background:#BF8A12; color:#1F1500 }} .fra-AR {{ background:#C2571A }}
.fra-PEND {{ background:#DDB04A; color:#2B2100 }} .fra-NA {{ background:#6B7280 }}
</style>""", unsafe_allow_html=True)

STATUS_KEY = {Status.PASS: "PASS", Status.NI: "NI", Status.AR: "AR", Status.PEND: "PEND", Status.NA: "NA"}


def esc(text: str) -> str:
    """Stop Streamlit markdown from treating $ amounts as math."""
    return (text or "").replace("$", "\\$")


def pill(s: Status) -> str:
    return f'<span class="fra-pill fra-{STATUS_KEY[s]}">{s.value}</span>'


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def check_password() -> bool:
    expected = os.environ.get("FRA_APP_PASSWORD") or (st.secrets.get("FRA_APP_PASSWORD") if hasattr(st, "secrets") and _has_secrets() else None)
    if not expected:
        st.sidebar.warning("No team password set (FRA_APP_PASSWORD). Set one before sharing this app.")
        return True
    if st.session_state.get("authed"):
        return True
    st.title("Funding Readiness Audit")
    pw = st.text_input("Team password", type="password")
    if st.button("Sign in", type="primary"):
        if hmac.compare_digest(pw, expected):
            st.session_state.authed = True
            st.rerun()
        st.error("Incorrect password.")
    return False


def _has_secrets() -> bool:
    try:
        return bool(st.secrets)
    except Exception:
        return False


if not check_password():
    st.stop()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def save(case: Case, msg: str = "Saved."):
    storage.save_case(case)
    st.toast(msg)


def df_from(models: list, cls) -> pd.DataFrame:
    rows = [m.model_dump(mode="json") for m in models]
    if not rows:
        rows = []
        cols = list(cls.model_fields.keys())
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows)


def models_from(df: pd.DataFrame, cls) -> list:
    out = []
    for rec in df.to_dict(orient="records"):
        clean = {}
        for k, v in rec.items():
            if v is None or (isinstance(v, float) and pd.isna(v)) or (isinstance(v, str) and v == "" and cls.model_fields.get(k) and cls.model_fields[k].annotation is not str):
                continue
            clean[k] = v
        if not any(v not in (None, "", [], 0) for v in clean.values()):
            continue
        try:
            out.append(cls.model_validate(clean))
        except Exception as e:
            st.warning(f"Skipped a row that could not be read: {e}")
    return out


def addr_inputs(prefix: str, a: Address) -> Address:
    c1, c2 = st.columns([3, 2])
    line1 = c1.text_input("Street address", a.line1, key=f"{prefix}_l1")
    line2 = c2.text_input("Line 2", a.line2, key=f"{prefix}_l2")
    c3, c4, c5 = st.columns([3, 1, 1])
    city = c3.text_input("City", a.city, key=f"{prefix}_city")
    state = c4.text_input("State", a.state, key=f"{prefix}_state")
    zp = c5.text_input("ZIP", a.zip, key=f"{prefix}_zip")
    return Address(line1=line1, line2=line2, city=city, state=state, zip=zp)


def opt_num(label: str, value, key: str, help: str | None = None):
    txt = st.text_input(label, "" if value is None else f"{value:g}", key=key, help=help)
    txt = txt.replace(",", "").replace("$", "").strip()
    try:
        return float(txt) if txt else None
    except ValueError:
        st.caption(f":red[{label}: enter a number]")
        return value


def opt_date(label: str, value, key: str):
    has = st.checkbox(f"{label} known", value=value is not None, key=f"{key}_has")
    return st.date_input(label, value or date.today(), key=key, format="MM/DD/YYYY") if has else None


# ---------------------------------------------------------------------------
# Sidebar: case selection
# ---------------------------------------------------------------------------

st.sidebar.markdown(f"<h2 style='color:{NAVY};margin:0'>TRADELINE<br>ASSOCIATES INC.</h2><div style='color:{GOLD};font-weight:700;letter-spacing:.2em;font-size:.7rem'>FUNDING READINESS AUDIT</div>", unsafe_allow_html=True)
cases = storage.list_cases()
labels = {c.id: f"{c.display_name} · {c.meta.report_number or c.id}" for c in cases}
c1, c2 = st.sidebar.columns(2)
if c1.button("➕ New case", use_container_width=True):
    nc = storage.new_case()
    nc.meta.report_number = f"TLA-FRA-{date.today():%y%m}-{len(cases) + 1:04d}"
    nc.meta.report_date = date.today()
    storage.save_case(nc)
    st.session_state.case_id = nc.id
    st.rerun()
if c2.button("Load demo", use_container_width=True, help="A fictional client for training and testing"):
    d = demo_case()
    d.id = "demo" + uuid.uuid4().hex[:4]
    storage.save_case(d)
    st.session_state.case_id = d.id
    st.rerun()
if not cases:
    st.title("Funding Readiness Audit")
    st.info("Create a new case, or load the fictional demo client to see how it works.")
    st.stop()
ids = [c.id for c in cases]
cur = st.session_state.get("case_id", ids[0])
if cur not in ids:
    cur = ids[0]
case_id = st.sidebar.radio("Cases", ids, index=ids.index(cur), format_func=lambda i: labels[i])
st.session_state.case_id = case_id
case = storage.load_case(case_id)

st.sidebar.divider()
if ai.available():
    st.sidebar.success("AI reading & drafting: on")
else:
    st.sidebar.info("AI is off (no ANTHROPIC_API_KEY). Enter data manually; reports still generate.")
spent = sum(u.get("cost_usd", 0) for u in case.ai_usage)
st.sidebar.metric("AI cost for this case", f"${spent:,.2f}")

st.title(case.display_name)
st.caption(f"{case.meta.report_number or 'No report number'} · {case.meta.stage} · Draft {case.meta.revision}")

tabs = st.tabs(["1 · Intake", "2 · Documents", "3 · Extracted data", "4 · Research", "5 · Review audit", "6 · Report"])


# ---------------------------------------------------------------------------
# 1. Intake
# ---------------------------------------------------------------------------
with tabs[0]:
    it = case.intake
    with st.form("intake"):
        st.subheader("Funding goal (asked first)")
        prod_codes = list(PRODUCTS) + ["NOT_SURE"]
        names = {**PRODUCTS, "NOT_SURE": "Not sure — recommend options"}
        sel = st.multiselect("What kind of funding are they looking for?", prod_codes, default=[p for p in it.funding.product_types if p in prod_codes], format_func=lambda c: names[c])
        g1, g2, g3 = st.columns(3)
        with g1:
            amt = opt_num("Total funding needed ($)", it.funding.amount_requested, "f_amt")
        with g2:
            amt_min = opt_num("Smallest amount that still works ($)", it.funding.amount_minimum, "f_min")
        with g3:
            timeline = st.selectbox("When needed", ["", "Within 14 days", "15-30 days", "1-3 months", "3-6 months", "6-12 months", "Flexible"],
                                    index=["", "Within 14 days", "15-30 days", "1-3 months", "3-6 months", "6-12 months", "Flexible"].index(it.funding.timeline) if it.funding.timeline in ["", "Within 14 days", "15-30 days", "1-3 months", "3-6 months", "6-12 months", "Flexible"] else 0)
        g4, g5, g6 = st.columns(3)
        for_whom = g4.selectbox("Funding is for", ["business", "personal", "property", "both"], index=["business", "personal", "property", "both"].index(it.funding.for_whom))
        repay = g5.selectbox("Repayment source", ["", "Business cash flow", "Personal income", "Sale of asset/property", "Refinance later", "Not sure"],
                             index=["", "Business cash flow", "Personal income", "Sale of asset/property", "Refinance later", "Not sure"].index(it.funding.repayment_source) if it.funding.repayment_source in ["", "Business cash flow", "Personal income", "Sale of asset/property", "Refinance later", "Not sure"] else 0)
        pg = g6.selectbox("Willing to sign a personal guarantee?", ["Not stated", "Yes", "No"], index={None: 0, True: 1, False: 2}[it.funding.willing_pg])
        uses_df = st.data_editor(df_from(it.funding.uses, UseOfFunds), num_rows="dynamic", key="uses", use_container_width=True,
                                 column_config={"purpose": "Use of proceeds", "amount": st.column_config.NumberColumn("Amount ($)", format="$%d")})

        st.subheader("Business owner")
        owners = list(it.owners) or [Owner()]
        o = owners[0]
        o1, o2, o3, o4 = st.columns(4)
        o.first_name = o1.text_input("First name", o.first_name)
        o.last_name = o2.text_input("Last name", o.last_name)
        o.ownership_pct = opt_num("Ownership %", o.ownership_pct, "o_pct", help="Exact percentage (lender rules apply at 20% and 51%)")
        o.title = o4.text_input("Title", o.title)
        o5, o6 = st.columns(2)
        o.phone = o5.text_input("Phone", o.phone)
        o.email = o6.text_input("Email", o.email)
        st.caption("Home address")
        o.home_address = addr_inputs("home", o.home_address)

        st.subheader("Business information")
        b1, b2, b3 = st.columns(3)
        legal = b1.text_input("Exact legal name", it.legal_name)
        dba = b2.text_input("DBA", it.dba)
        ein = b3.text_input("EIN", it.ein)
        b4, b5, b6 = st.columns(3)
        etypes = ["", "C-Corp", "S-Corp", "Professional Corporation", "Partnership", "LLC “Limited Liability Company”", "Sole Proprietor", "Other"]
        etype = b4.selectbox("Entity type", etypes, index=etypes.index(it.entity_type) if it.entity_type in etypes else 0)
        fstate = b5.text_input("State formed", it.formation_state)
        with b6:
            fdate = opt_date("Formation date", it.formation_date, "fdate")
        st.caption("Primary business address")
        baddr = addr_inputs("biz", it.business_address)
        b7, b8, b9 = st.columns(3)
        bphone = b7.text_input("Business phone", it.business_phone)
        bemail = b8.text_input("Business email", it.business_email)
        web = b9.text_input("Website (or 'No Website')", it.website)
        desc = st.text_area("What the business does", it.business_description, height=70)

        st.subheader("Banking & debt")
        k1, k2, k3 = st.columns(3)
        bank = k1.text_input("Primary business bank", it.primary_bank)
        ages = ["", "Less than 3 months", "3–6 months", "6–12 months", "1–2 years", "2+ years"]
        bage = k2.selectbox("Account age", ages, index=ages.index(it.bank_account_age) if it.bank_account_age in ages else 0)
        with k3:
            bal30 = opt_num("Average 30-day balance ($)", it.avg_30day_balance, "bal30")
        rel = st.text_area("Banking relationships", it.banking_relationships, height=60)
        bp1, bp2 = st.columns([1, 3])
        bprob = bp1.selectbox("Previous banking problems", ["Not stated", "Yes", "No"], index={None: 0, True: 1, False: 2}[it.banking_problems])
        bprobd = bp2.text_input("Details (institution, account, date, reason, balance owed)", it.banking_problems_detail)
        with st.columns(3)[0]:
            totdebt = opt_num("Approximate total business debt ($)", it.total_business_debt, "totdebt")
        debts_df = st.data_editor(df_from(it.debts, DebtItem), num_rows="dynamic", key="debts", use_container_width=True)

        st.subheader("Business credit IDs")
        i1, i2, i3, i4, i5 = st.columns(5)
        naics = i1.text_input("NAICS", it.naics)
        sic = i2.text_input("SIC", it.sic)
        duns = i3.text_input("D-U-N-S", it.duns)
        bin_ = i4.text_input("Experian BIN", it.experian_bin)
        efx = i5.text_input("Equifax ID", it.equifax_commercial_id)

        st.subheader("Revenue, income & eligibility (added questions)")
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            rev1 = opt_num("Revenue last full year ($)", it.revenue_last_year, "rev1")
        with r2:
            rev0 = opt_num("Revenue prior year ($)", it.revenue_prior_year, "rev0")
        with r3:
            revy = opt_num("Revenue year-to-date ($)", it.revenue_ytd, "revy")
        with r4:
            dep = opt_num("Avg monthly deposits ($)", it.avg_monthly_deposits, "dep", help="Excluding transfers and loan/advance proceeds")
        r5, r6, r7, r8 = st.columns(4)
        with r5:
            inc = opt_num("Owner's individual income ($/yr)", it.personal_income, "inc")
        with r6:
            house = opt_num("Monthly housing payment ($)", it.housing_payment, "house")
        emp = r7.number_input("Employees", value=it.employees or 0, min_value=0)
        with r8:
            opstart = opt_date("Operations start date", it.operations_start_date, "opstart")
        yn = ["Not stated", "Yes", "No"]
        e1, e2, e3 = st.columns(3)
        liens = e1.selectbox("Unresolved tax liens or judgments?", yn, index={None: 0, True: 1, False: 2}[it.tax_liens_or_judgments])
        fed = e2.selectbox("Behind on any federal debt?", yn, index={None: 0, True: 1, False: 2}[it.federal_debt_delinquent])
        cit = e3.selectbox("SBA only: all owners U.S. citizens/nationals residing in the U.S.?", yn, index={None: 0, True: 1, False: 2}[it.sba_citizenship_ok],
                           help="Asked and used only when an SBA loan is in the goal (SBA rule effective 3/1/2026).")

        if st.form_submit_button("Save intake", type="primary"):
            yesno = {"Not stated": None, "Yes": True, "No": False}
            it.funding.product_types, it.funding.amount_requested, it.funding.amount_minimum = sel, amt, amt_min
            it.funding.timeline, it.funding.for_whom, it.funding.repayment_source = timeline, for_whom, repay
            it.funding.willing_pg = yesno[pg]
            it.funding.uses = models_from(uses_df, UseOfFunds)
            it.owners = [o] + owners[1:]
            it.legal_name, it.dba, it.ein, it.entity_type, it.formation_state, it.formation_date = legal, dba, ein, etype, fstate, fdate
            it.business_address, it.business_phone, it.business_email, it.website, it.business_description = baddr, bphone, bemail, web, desc
            it.primary_bank, it.bank_account_age, it.avg_30day_balance, it.banking_relationships = bank, bage, bal30, rel
            it.banking_problems, it.banking_problems_detail, it.total_business_debt = yesno[bprob], bprobd, totdebt
            it.debts = models_from(debts_df, DebtItem)
            it.naics, it.sic, it.duns, it.experian_bin, it.equifax_commercial_id = naics, sic, duns, bin_, efx
            it.revenue_last_year, it.revenue_prior_year, it.revenue_ytd, it.avg_monthly_deposits = rev1, rev0, revy, dep
            it.personal_income, it.housing_payment, it.employees, it.operations_start_date = inc, house, int(emp) or None, opstart
            it.tax_liens_or_judgments, it.federal_debt_delinquent, it.sba_citizenship_ok = yesno[liens], yesno[fed], yesno[cit]
            save(case, "Intake saved.")
            st.rerun()


# ---------------------------------------------------------------------------
# 2. Documents
# ---------------------------------------------------------------------------
with tabs[1]:
    st.subheader("Upload documents")
    st.caption("Files are stored only on this server under data/ and never committed to the code repository.")
    u1, u2 = st.columns([2, 3])
    dtype = u1.selectbox("Document type", list(DocType), format_func=lambda d: d.value)
    files = u2.file_uploader("Files (PDF or image)", accept_multiple_files=True, type=["pdf", "png", "jpg", "jpeg", "webp"])
    if st.button("Add to case", disabled=not files):
        for f in files:
            did = uuid.uuid4().hex[:8]
            storage.save_upload(case.id, did, f.name, f.getvalue())
            case.documents.append(Document(id=did, filename=f.name, doc_type=dtype))
        save(case, f"Added {len(files)} file(s).")
        st.rerun()

    st.subheader("Documents in this case")
    if not case.documents:
        st.info("No documents yet.")
    for d in list(case.documents):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
            c1.markdown(f"**{d.filename}**  \n{d.doc_type.value}")
            c2.markdown(f"Status: `{d.extraction_status}`" + (f"  \nDated {d.document_date:%m/%d/%Y}" if d.document_date else ""))
            path = storage.upload_path(case.id, d.id)
            can_ai = ai.available() and path is not None
            if c3.button("Read with AI", key=f"x_{d.id}", disabled=not can_ai, help=None if can_ai else "Needs an API key and an uploaded file"):
                from fra.ai.extract import apply_extraction, extract_document
                with st.spinner(f"Reading {d.filename}… this can take a minute for long reports."):
                    try:
                        result, usage = extract_document(path, d)
                        case.ai_usage.append(usage)
                        warns = apply_extraction(case, d, result)
                        save(case, f"Read {d.filename} (${usage['cost_usd']:.2f}).")
                        for w in warns:
                            st.warning(w)
                    except ai.AIUnavailable as e:
                        d.extraction_status, d.extraction_note = "failed", str(e)
                        save(case)
                        st.error(str(e))
            if c4.button("🗑", key=f"rm_{d.id}", help="Remove document"):
                case.documents = [x for x in case.documents if x.id != d.id]
                if path:
                    path.unlink(missing_ok=True)
                save(case, "Removed.")
                st.rerun()
            if d.extraction_note:
                st.caption(d.extraction_note)
            if d.extracted.get("_low_confidence"):
                st.warning("Low confidence — verify the extracted values in tab 3.")
            if d.extraction_status not in ("extracted",):
                if st.checkbox("Values entered manually", value=d.extraction_status == "manual", key=f"man_{d.id}") != (d.extraction_status == "manual"):
                    d.extraction_status = "manual" if d.extraction_status != "manual" else "not_extracted"
                    save(case)


# ---------------------------------------------------------------------------
# 3. Extracted data (review & edit)
# ---------------------------------------------------------------------------
with tabs[2]:
    st.caption("Everything here can be edited. The AI fills these tables; the analyst confirms them.")
    sec = st.radio("Section", ["Identity sources", "Personal credit", "Business bureaus", "Financials"], horizontal=True)

    if sec == "Identity sources":
        st.write("One row per document or record that states business identity details. Tier: A authoritative (IRS, SOS, operating agreement) · B institutional (bank, tax return, license) · D self-published · E client.")
        cols = ["source", "tier", "as_of", "legal_name", "dba", "entity_type", "formation_state", "formation_date", "ein", "phone", "email", "website", "naics", "sic", "revenue", "employees", "owners"]
        rows = []
        for s in case.identity_sources:
            d = s.model_dump(mode="json")
            a = s.address or Address()
            d.update(addr_line1=a.line1, addr_line2=a.line2, addr_city=a.city, addr_state=a.state, addr_zip=a.zip)
            rows.append({k: d.get(k) for k in cols + ["addr_line1", "addr_line2", "addr_city", "addr_state", "addr_zip", "document_id"]})
        df = pd.DataFrame(rows, columns=cols + ["addr_line1", "addr_line2", "addr_city", "addr_state", "addr_zip", "document_id"])
        ed = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="idsrc",
                            column_config={"tier": st.column_config.SelectboxColumn(options=["A", "B", "D", "E"])})
        if st.button("Save identity sources", type="primary"):
            new = []
            for rec in ed.to_dict(orient="records"):
                rec = {k: (None if (v is None or (isinstance(v, float) and pd.isna(v)) or v == "") else v) for k, v in rec.items()}
                if not rec.get("source"):
                    continue
                addr = Address(line1=rec.pop("addr_line1") or "", line2=rec.pop("addr_line2") or "", city=rec.pop("addr_city") or "",
                               state=rec.pop("addr_state") or "", zip=str(rec.pop("addr_zip") or ""))
                rec["address"] = None if addr.is_empty() else addr
                new.append(IdentitySource.model_validate({k: v for k, v in rec.items() if v is not None or k == "address"}))
            case.identity_sources = new
            save(case, "Identity sources saved.")
            st.rerun()

    elif sec == "Personal credit":
        cc = case.consumer_credit[0] if case.consumer_credit else ConsumerCredit()
        p1, p2, p3 = st.columns(3)
        cc.person = p1.text_input("Guarantor", cc.person)
        with p2:
            cc.report_date = opt_date("Report date", cc.report_date, "ccdate")
        cc.source = p3.text_input("Report source", cc.source)
        st.markdown("**Scores**")
        sc = st.data_editor(df_from(cc.scores, CreditScore), num_rows="dynamic", key="scores", use_container_width=True,
                            column_config={"bureau": st.column_config.SelectboxColumn(options=["Experian", "Equifax", "TransUnion"]),
                                           "model": st.column_config.SelectboxColumn(options=["FICO8", "FICO9", "FICO10T", "FICO2/4/5", "VS3", "VS4", "unknown"])})
        st.markdown("**Tradelines**")
        tl_df = df_from(cc.tradelines, Tradeline)
        if "bureaus" in tl_df:
            tl_df["bureaus"] = tl_df["bureaus"].apply(lambda b: ", ".join(b) if isinstance(b, list) else b)
        tl = st.data_editor(tl_df, num_rows="dynamic", key="tls", use_container_width=True,
                            column_config={"owner_type": st.column_config.SelectboxColumn(options=["primary", "joint", "au", "business", "terminated"]),
                                           "account_type": st.column_config.SelectboxColumn(options=["revolving", "installment", "mortgage", "open", "charge", "collection"]),
                                           "status": st.column_config.SelectboxColumn(options=["current", "collection", "paid_collection", "chargeoff", "paid_chargeoff", "repo", "foreclosure"])})
        st.markdown("**Hard inquiries**")
        iq = st.data_editor(df_from(cc.inquiries, Inquiry), num_rows="dynamic", key="inq", use_container_width=True,
                            column_config={"bureau": st.column_config.SelectboxColumn(options=["Experian", "Equifax", "TransUnion"])})
        f1, f2 = st.columns(2)
        cc.fraud_alert = f1.checkbox("Fraud alert on file", cc.fraud_alert)
        flags = f2.text_area("Identity issues noted by analyst (one per line, e.g. 'Different SSN on Equifax')", "\n".join(cc.identity_flags), height=70)
        addrs = st.text_area("Addresses reported (one per line)", "\n".join(cc.addresses), height=70)
        if st.button("Save personal credit", type="primary"):
            cc.scores = models_from(sc, CreditScore)
            tl = tl.copy()
            if "bureaus" in tl:
                tl["bureaus"] = tl["bureaus"].apply(lambda s: [b.strip() for b in str(s).split(",") if b.strip()] if isinstance(s, str) else s)
            cc.tradelines = models_from(tl, Tradeline)
            cc.inquiries = models_from(iq, Inquiry)
            cc.identity_flags = [x for x in flags.splitlines() if x.strip()]
            cc.addresses = [x for x in addrs.splitlines() if x.strip()]
            case.consumer_credit = [cc]
            save(case, "Personal credit saved.")
            st.rerun()

    elif sec == "Business bureaus":
        for b in CommercialBureau:
            rep = next((r for r in case.commercial_reports if r.bureau == b), None)
            with st.expander(f"{b.value} — {'on file' if rep else 'not on file'}", expanded=rep is not None):
                rep = rep or CommercialReport(bureau=b, file_found=False)
                k = b.name
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    rep.report_date = opt_date("Report date", rep.report_date, f"rd_{k}")
                rep.file_id = c2.text_input("File ID (BIN / D-U-N-S)", rep.file_id, key=f"fid_{k}")
                rep.file_found = c3.checkbox("File found", rep.file_found, key=f"ff_{k}")
                rep.insufficient_data = c4.checkbox("Insufficient data", rep.insufficient_data, key=f"ins_{k}")
                scs = st.data_editor(df_from(rep.scores, BusinessScore), num_rows="dynamic", key=f"bs_{k}", use_container_width=True)
                trs = st.data_editor(df_from(rep.tradelines, BusinessTradeline), num_rows="dynamic", key=f"bt_{k}", use_container_width=True)
                ucc = st.data_editor(df_from(rep.ucc_filings, UCCFiling), num_rows="dynamic", key=f"uc_{k}", use_container_width=True,
                                     column_config={"collateral_class": st.column_config.SelectboxColumn(options=["specific", "blanket", "accounts", "mca_factor", "unknown"])})
                st.markdown("Identity as the bureau shows it")
                idn = rep.identity
                i1, i2, i3 = st.columns(3)
                idn.legal_name = i1.text_input("Legal name", idn.legal_name or "", key=f"ln_{k}")
                idn.entity_type = i2.text_input("Entity type", idn.entity_type or "", key=f"et_{k}")
                idn.phone = i3.text_input("Phone", idn.phone or "", key=f"ph_{k}")
                i4, i5, i6, i7 = st.columns(4)
                idn.naics = i4.text_input("NAICS", idn.naics or "", key=f"na_{k}")
                idn.sic = i5.text_input("SIC", idn.sic or "", key=f"si_{k}")
                idn.website = i6.text_input("Website", idn.website or "", key=f"we_{k}")
                with i7:
                    idn.revenue = opt_num("Sales revenue", idn.revenue, f"rv_{k}")
                idn.address = addr_inputs(f"ba_{k}", idn.address or Address())
                incons = st.text_area("Internal inconsistencies (one per line)", "\n".join(rep.internal_inconsistencies), key=f"ic_{k}", height=60)
                derogs = st.text_area("Derogatories (judgments, liens, collections — one per line)", "\n".join(rep.derogatories), key=f"dg_{k}", height=60)
                if st.button(f"Save {b.value}", key=f"save_{k}", type="primary"):
                    rep.scores = models_from(scs, BusinessScore)
                    rep.tradelines = models_from(trs, BusinessTradeline)
                    rep.ucc_filings = models_from(ucc, UCCFiling)
                    rep.internal_inconsistencies = [x for x in incons.splitlines() if x.strip()]
                    rep.derogatories = [x for x in derogs.splitlines() if x.strip()]
                    if idn.address and idn.address.is_empty():
                        idn.address = None
                    case.commercial_reports = [r for r in case.commercial_reports if r.bureau != b] + ([rep] if (rep.report_date or rep.file_id or rep.scores) else [])
                    save(case, f"{b.value} saved.")
                    st.rerun()

    else:
        f = case.financials
        st.markdown("**Business tax returns**")
        trs = st.data_editor(df_from(f.tax_returns, TaxReturn), num_rows="dynamic", key="trs", use_container_width=True)
        st.markdown("**Bank statement months**")
        bms = st.data_editor(df_from(f.bank_months, BankMonth), num_rows="dynamic", key="bms", use_container_width=True)
        a1, a2, a3 = st.columns(3)
        with a1:
            f.pnl_period_end = opt_date("YTD P&L through", f.pnl_period_end, "pnlend")
            f.pnl_revenue = opt_num("YTD revenue", f.pnl_revenue, "pnlrev")
            f.pnl_net_income = opt_num("YTD net income", f.pnl_net_income, "pnlni")
        with a2:
            f.personal_net_worth = opt_num("Personal net worth (PFS)", f.personal_net_worth, "pnw")
            f.total_assets = opt_num("Total business assets", f.total_assets, "ta")
            f.total_liabilities = opt_num("Total liabilities", f.total_liabilities, "tl")
        with a3:
            f.ar_total = opt_num("Accounts receivable", f.ar_total, "ar")
            f.ar_over_90 = opt_num("A/R over 90 days", f.ar_over_90, "ar90")
            f.dso_days = opt_num("DSO (days)", f.dso_days, "dso")
        notes = st.text_area("Document-consistency issues noted (one per line — e.g. 'P&L revenue differs from tax return by 18%')", "\n".join(f.consistency_notes), height=70)
        if st.button("Save financials", type="primary"):
            f.tax_returns = sorted(models_from(trs, TaxReturn), key=lambda t: t.year)
            f.bank_months = sorted(models_from(bms, BankMonth), key=lambda m: m.month)
            f.consistency_notes = [x for x in notes.splitlines() if x.strip()]
            save(case, "Financials saved.")
            st.rerun()


# ---------------------------------------------------------------------------
# 4. Research checklist
# ---------------------------------------------------------------------------
with tabs[3]:
    st.write("External checks the analyst performs. Record what you found; points stay **Pending** until a check is recorded.")
    results = ["not_started", "found_ok", "found_issue", "not_found", "not_applicable"]
    labels_r = {"not_started": "Not started", "found_ok": "Checked — OK", "found_issue": "Checked — issue found", "not_found": "Checked — nothing found", "not_applicable": "Not applicable"}
    with st.form("research"):
        for key, label in RESEARCH_ITEMS.items():
            rf = case.research.get(key, ResearchFinding(item=key))
            c1, c2 = st.columns([2, 5])
            res_ = c1.selectbox(label, results, index=results.index(rf.result), format_func=lambda x: labels_r[x], key=f"r_{key}")
            fin = c2.text_input("Finding (client-facing wording)", rf.finding, key=f"rf_{key}")
            case.research[key] = ResearchFinding(item=key, result=res_, finding=fin, checked_on=rf.checked_on if res_ == rf.result and rf.checked_on else (date.today() if res_ != "not_started" else None), analyst=case.meta.analyst)
        if st.form_submit_button("Save research", type="primary"):
            save(case, "Research saved.")


# ---------------------------------------------------------------------------
# 5. Review audit
# ---------------------------------------------------------------------------
with tabs[4]:
    result = run_audit(case)
    sc = result.status_counts
    m = st.columns(5)
    for col, s in zip(m, [Status.PASS, Status.NI, Status.AR, Status.PEND, Status.NA]):
        col.metric(s.value.title(), sc.get(s.value, 0))
    if result.composite.issued:
        st.success(f"Composite Funding Readiness Score: **{result.composite.score} — {result.composite.tier}**")
    else:
        st.warning(esc("Composite score withheld until: " + "; ".join(result.composite.unlocks)))

    st.subheader("Five lender areas")
    for a in result.areas:
        st.markdown(f"{pill(a.status)} **{a.name}** — {esc(a.narrative)}", unsafe_allow_html=True)

    st.subheader("Master address")
    for c in result.address_candidates:
        st.markdown(f"- `{c.kind}` **{c.address}** — on {', '.join(c.seen_on)}" + (f" · {'; '.join(c.notes)}" if c.notes else ""))
    with st.expander("Record the client's master address designation (the client decides, not TLA)"):
        cur_m = case.meta.master_address_designation or Address()
        newm = addr_inputs("master", cur_m)
        if st.button("Save designation"):
            case.meta.master_address_designation = None if newm.is_empty() else newm
            case.meta.change_log.append(f"{date.today():%m/%d/%Y}: master address designation recorded")
            save(case, "Designation saved.")
            st.rerun()

    st.subheader("20 points — review and override")
    st.caption("Overrides are logged in the case file with your reason.")
    for f in result.findings:
        with st.expander(f"{f.number:02d}. {f.title} — {f.status.value}{' (overridden)' if f.overridden else ''}"):
            st.markdown(pill(f.status) + f" **{esc(f.one_line)}**", unsafe_allow_html=True)
            st.markdown(esc(f.found))
            if f.correction:
                st.caption("Correction: " + esc(f.correction))
            ov = case.overrides.get(str(f.number), PointOverride())
            o1, o2 = st.columns([1, 3])
            opts = ["(rules)"] + [s.value for s in Status]
            pick = o1.selectbox("Status", opts, index=opts.index(ov.status.value) if ov.status else 0, key=f"ovs_{f.number}")
            fin = o2.text_input("One-line finding override", ov.finding, key=f"ovf_{f.number}")
            why = st.text_input("Internal reason (required for an override)", ov.note, key=f"ovn_{f.number}")
            if st.button("Save override", key=f"ovb_{f.number}"):
                if (pick != "(rules)" or fin) and not why:
                    st.error("Give a reason for the override.")
                else:
                    case.overrides[str(f.number)] = PointOverride(status=None if pick == "(rules)" else Status(pick), finding=fin, note=why)
                    case.meta.change_log.append(f"{date.today():%m/%d/%Y}: point {f.number:02d} override — {why or 'cleared'}")
                    save(case, "Override saved.")
                    st.rerun()

    st.subheader("Product fit")
    for p in result.products:
        rng = f" · \\${p.range_low:,.0f}–\\${p.range_high:,.0f}" if p.range_high else ""
        st.markdown(f"**{p.name}** — `{p.fit}`{rng}" + (f" · score {p.score:.0f}" if p.score is not None else ""))
        for x in p.blockers + p.reasons:
            st.caption("• " + esc(x))

    if result.review_items:
        st.subheader("Open review items")
        for h in result.review_items:
            (st.error if h.blocking else st.warning)(esc(f"{h.id} — {h.title}: {h.reason}"))


# ---------------------------------------------------------------------------
# 6. Report
# ---------------------------------------------------------------------------
with tabs[5]:
    result = run_audit(case)
    meta = case.meta
    c1, c2, c3, c4 = st.columns(4)
    meta.report_number = c1.text_input("Report number", meta.report_number)
    meta.analyst = c2.text_input("Analyst", meta.analyst)
    meta.report_date = c3.date_input("Report date", meta.report_date or date.today(), format="MM/DD/YYYY")
    stages = ["DRAFT", "IN REVIEW", "FINAL CLIENT DELIVERY"]
    stage = c4.selectbox("Stage", stages, index=stages.index(meta.stage))

    st.subheader("Narrative")
    if st.button("✍️ Draft narrative with AI", disabled=not ai.available(), help=None if ai.available() else "Needs ANTHROPIC_API_KEY"):
        from fra.ai.narrative import draft_narrative
        with st.spinner("Drafting… (about 1–2 minutes)"):
            try:
                narr, usage, warns = draft_narrative(case, result)
                case.ai_usage.append(usage)
                case.narrative_overrides.update(narr)
                st.session_state.narr_warnings = warns
                save(case, f"Draft ready (${usage['cost_usd']:.2f}).")
                st.rerun()
            except ai.AIUnavailable as e:
                st.error(str(e))
    for w in st.session_state.get("narr_warnings", []):
        st.warning(w)
    from fra.report.render import fallback_narrative
    base = fallback_narrative(case, result)
    keys = ["cover_assessment", "glance_meaning", "central_story", "action_1", "action_2", "action_3", "area_legal", "area_credit",
            "area_banking", "area_guarantor", "area_goal", "funding_implications", "conclusion"]
    with st.form("narr"):
        edits = {}
        for k in keys:
            edits[k] = st.text_area(k.replace("_", " ").title(), case.narrative_overrides.get(k) or base.get(k, ""), height=90 if k in ("central_story", "conclusion") else 68)
        with st.expander("Per-point plain-English lines and product notes"):
            for f in result.findings:
                kk = f"plain_{f.number}"
                edits[kk] = st.text_input(f"{f.number:02d} {f.title}", case.narrative_overrides.get(kk) or f.plain)
            for p in result.products:
                kk = f"product_{p.code}"
                edits[kk] = st.text_area(p.name, case.narrative_overrides.get(kk, ""), height=60)
        if st.form_submit_button("Save narrative"):
            defaults = {**base, **{f"plain_{f.number}": f.plain for f in result.findings}}
            case.narrative_overrides = {k: v for k, v in edits.items() if v and v.strip() != (defaults.get(k) or "").strip()}
            save(case, "Narrative saved.")

    st.subheader("Release checklist")
    checks = [
        "All extracted values verified against source documents",
        "Every identity conflict in the matrix confirmed",
        "Research checklist complete or remaining items intentionally Pending",
        "Overrides have written reasons",
        "Narrative read in full; no figure that isn't in the documents",
        "No full tax IDs or account numbers in client-facing text",
        "Client consent and engagement on file",
    ]
    ok = all(st.checkbox(cx, key=f"chk_{i}") for i, cx in enumerate(checks))
    html = render_html(case, result)
    bad = find_forbidden(html)
    if bad:
        st.error("Prohibited phrases found in the report: " + ", ".join(bad))
    if stage == "FINAL CLIENT DELIVERY" and (not ok or bad):
        st.info("Complete the checklist (and remove prohibited phrases) to release the final version.")
        stage = meta.stage if meta.stage != "FINAL CLIENT DELIVERY" else "IN REVIEW"
    if stage != meta.stage:
        if stage == "FINAL CLIENT DELIVERY":
            meta.change_log.append(f"{date.today():%m/%d/%Y}: Rev {meta.revision} released to client")
        meta.stage = stage

    if st.button("📄 Generate PDF", type="primary"):
        with st.spinner("Building the report…"):
            save(case, "Saved.")
            pdf = render_pdf(case, result)
            st.session_state.pdf = pdf
    if st.session_state.get("pdf"):
        fname = f"{(case.intake.legal_name or 'client').replace(' ', '_')}_FRA_{meta.report_number}.pdf"
        st.download_button("⬇️ Download report", st.session_state.pdf, file_name=fname, mime="application/pdf")
    if st.button("Start next revision"):
        meta.revision += 1
        meta.stage = "DRAFT"
        meta.change_log.append(f"{date.today():%m/%d/%Y}: revision {meta.revision} started")
        save(case, "New revision started.")
        st.rerun()

    with st.expander("AI usage log"):
        if case.ai_usage:
            st.dataframe(pd.DataFrame(case.ai_usage), use_container_width=True)
        else:
            st.caption("No AI calls yet.")
