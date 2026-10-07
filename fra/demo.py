"""A fictional demo client ("Northwind Example LLC") used for demos and tests.
Every name, number and address here is invented."""
from __future__ import annotations

from datetime import date

from fra.models import (Address, BankMonth, Bureau, BusinessScore, BusinessTradeline, Case, CommercialBureau,
                        CommercialReport, ConsumerCredit, CreditScore, DebtItem, DocType, Document, Financials,
                        FundingGoal, IdentitySource, Inquiry, Intake, Owner, ReportMeta, ResearchFinding, TaxReturn,
                        Tradeline, UCCFiling, UseOfFunds)

AUDIT_DATE = date(2026, 9, 15)

HOME = Address(line1="418 Juniper Ridge Dr", city="Austin", state="TX", zip="78745")
OFFICE = Address(line1="2200 Meridian Blvd", line2="Ste 140", city="Austin", state="TX", zip="78741")
OLD_AGENT = Address(line1="1910 Prairie Ave", line2="Ste 300", city="Cheyenne", state="WY", zip="82001")


def demo_case() -> Case:
    owner = Owner(first_name="Jordan", last_name="Avery", ownership_pct=100, title="Sole Member",
                  phone="512-555-0142", email="jordan.avery@example.com", home_address=HOME)
    intake = Intake(
        owners=[owner], legal_name="Northwind Example LLC", entity_type="LLC “Limited Liability Company”",
        formation_state="Texas", formation_date=date(2022, 4, 12), ein="00-1234567",
        business_address=OFFICE, business_phone="512-555-0190", business_email="northwindexample@gmail.com",
        business_description="IT consulting and managed cloud services for small and mid-size businesses.",
        website="https://northwind-example.com", primary_bank="Lone Star Community Bank", bank_account_age="2+ years",
        existing_debt_types=["Business Line of Credit", "Business Credit Cards"], total_business_debt=96000,
        avg_30day_balance=48000, banking_relationships="Lone Star Community Bank (operating account, $100k line); Summit National (business card)",
        banking_problems=False, naics="541512", sic="I Don't Know", duns="I Don't Know", experian_bin="I Don't Know",
        revenue_last_year=1_240_000, revenue_prior_year=1_080_000, revenue_ytd=870_000, avg_monthly_deposits=104_000,
        employees=6, personal_income=165_000, housing_payment=3_100, tax_liens_or_judgments=False,
        federal_debt_delinquent=False, sba_citizenship_ok=True,
        debts=[DebtItem(lender="Lone Star Community Bank", kind="LOC", balance=82_000, payment=1_400, secured=True),
               DebtItem(lender="Summit National", kind="business card", balance=14_000, payment=420)],
        funding=FundingGoal(product_types=["BL", "SBA", "BC"], amount_requested=150_000, amount_minimum=100_000,
                            uses=[UseOfFunds(purpose="Hire two engineers (working capital)", amount=90_000),
                                  UseOfFunds(purpose="Equipment and software", amount=60_000)],
                            timeline="1-3 months", for_whom="business", willing_pg=True,
                            collateral=["Accounts receivable"], repayment_source="Business cash flow"),
    )
    docs = [
        Document(id="d1", filename="cp575_notice.pdf", doc_type=DocType.IRS_EIN, document_date=date(2022, 4, 14), extraction_status="manual"),
        Document(id="d2", filename="certificate_of_formation.pdf", doc_type=DocType.SOS_FILING, document_date=date(2022, 4, 12), extraction_status="manual"),
        Document(id="d3", filename="beneficial_ownership_cert.pdf", doc_type=DocType.BANK_CERT, document_date=date(2022, 5, 2), extraction_status="manual"),
        Document(id="d4", filename="2024_form_1120S.pdf", doc_type=DocType.TAX_RETURN, document_date=date(2025, 3, 10), extraction_status="manual"),
        Document(id="d5", filename="2025_form_1120S.pdf", doc_type=DocType.TAX_RETURN, document_date=date(2026, 3, 9), extraction_status="manual"),
        Document(id="d6", filename="3bureau_fico_report.pdf", doc_type=DocType.CONSUMER_CREDIT, document_date=date(2026, 9, 2), extraction_status="manual"),
        Document(id="d7", filename="experian_business.pdf", doc_type=DocType.EXPERIAN_BUSINESS, document_date=date(2026, 9, 3), extraction_status="manual"),
        Document(id="d8", filename="dnb_report.pdf", doc_type=DocType.DNB, document_date=date(2026, 9, 3), extraction_status="manual"),
        Document(id="d9", filename="equifax_business.pdf", doc_type=DocType.EQUIFAX_BUSINESS, document_date=date(2026, 9, 4), extraction_status="manual"),
        Document(id="d10", filename="ytd_pnl_2026-07.pdf", doc_type=DocType.PNL, document_date=date(2026, 8, 5), extraction_status="manual"),
    ]
    sources = [
        IdentitySource(source="IRS CP 575", tier="A", as_of=date(2022, 4, 14), legal_name="NORTHWIND EXAMPLE LLC", ein="00-1234567",
                       address=HOME, owners="Jordan Avery (sole member)"),
        IdentitySource(source="Texas SOS Certificate of Formation", tier="A", as_of=date(2022, 4, 12), legal_name="Northwind Example LLC",
                       entity_type="Limited Liability Company", formation_state="Texas", formation_date=date(2022, 4, 12)),
        IdentitySource(source="Bank beneficial-ownership certification", tier="B", as_of=date(2022, 5, 2), legal_name="Northwind Example LLC",
                       ein="00-1234576", address=HOME, owners="Jordan Avery"),
        IdentitySource(source="2025 business tax return (1120S)", tier="B", as_of=date(2026, 3, 9), legal_name="Northwind Example LLC",
                       entity_type="S corporation", ein="00-1234567", address=OFFICE, revenue=1_240_000, naics="541512"),
    ]
    consumer = ConsumerCredit(
        person="Jordan Avery", report_date=date(2026, 9, 2), source="myFICO 3-bureau",
        scores=[CreditScore(bureau=Bureau.TRANSUNION, value=731, model="FICO8"),
                CreditScore(bureau=Bureau.EXPERIAN, value=752, model="FICO8"),
                CreditScore(bureau=Bureau.EQUIFAX, value=744, model="FICO8")],
        tradelines=[
            Tradeline(creditor="Chase Sapphire", bureaus=list(Bureau), credit_limit=28_000, balance=1_150, open_date=date(2012, 6, 1)),
            Tradeline(creditor="Amex Gold", bureaus=list(Bureau), account_type="charge", balance=2_300, open_date=date(2015, 3, 1)),
            Tradeline(creditor="Citi Double Cash", bureaus=list(Bureau), credit_limit=16_500, balance=420, open_date=date(2017, 9, 1)),
            Tradeline(creditor="Discover It", bureaus=list(Bureau), credit_limit=12_000, balance=0, open_date=date(2019, 1, 1),
                      worst_late=30, last_late_date=date(2026, 2, 1), late_count_24m=1),
            Tradeline(creditor="Capital One Venture", bureaus=list(Bureau), credit_limit=9_500, balance=310, open_date=date(2021, 8, 1)),
            Tradeline(creditor="Lakeview Mortgage", bureaus=list(Bureau), account_type="mortgage", balance=388_000, payment=2_480, open_date=date(2018, 5, 1)),
            Tradeline(creditor="Toyota Financial", bureaus=list(Bureau), account_type="installment", balance=14_200, payment=510, open_date=date(2023, 10, 1)),
        ],
        inquiries=[Inquiry(creditor="Lone Star Community Bank", bureau=Bureau.EXPERIAN, inquiry_date=date(2026, 6, 3), kind="bank"),
                   Inquiry(creditor="Summit National", bureau=Bureau.EQUIFAX, inquiry_date=date(2026, 3, 11), kind="card_issuer"),
                   Inquiry(creditor="Fintech Capital", bureau=Bureau.TRANSUNION, inquiry_date=date(2026, 7, 20), kind="fintech"),
                   Inquiry(creditor="Auto Dealer", bureau=Bureau.TRANSUNION, inquiry_date=date(2025, 10, 2), kind="auto")],
        names=["JORDAN AVERY", "JORDAN M AVERY"],
        addresses=["418 Juniper Ridge Dr, Austin TX", "418 Juniper Ridge Drive, Austin TX", "77 Elm St, Round Rock TX"],
    )
    exp = CommercialReport(
        bureau=CommercialBureau.EXPERIAN, report_date=date(2026, 9, 3), file_id="700000123",
        scores=[BusinessScore(name="Intelliscore Plus V2", value=14, scale="1-100", risk_class="Medium-High"),
                BusinessScore(name="Financial Stability Risk", value=22, scale="1-100", risk_class="Class 3")],
        tradelines=[BusinessTradeline(creditor_category="Financial services", terms="Revolving", high_credit=18_000, balance=14_000, dbt=0, last_reported=date(2026, 8, 1))],
        identity=IdentitySource(source="Experian Business", tier="C", legal_name="", entity_type="Corporation", address=HOME,
                                years_in_business=0, employees=0, revenue=0),
        internal_inconsistencies=[],
    )
    dnb = CommercialReport(
        bureau=CommercialBureau.DNB, report_date=date(2026, 9, 3), file_id="080000456",
        scores=[BusinessScore(name="PAYDEX", value=None, note="Not generated"),
                BusinessScore(name="Failure Score", value=41, risk_class="Class 3"),
                BusinessScore(name="Delinquency Score", value=62, risk_class="Class 3")],
        tradelines=[BusinessTradeline(creditor_category="Bank", terms="Revolving", high_credit=100_000, balance=82_000, dbt=0)],
        identity=IdentitySource(source="Dun & Bradstreet", tier="C", legal_name="Northwind Example LLC", entity_type="Limited Liability Company",
                                address=OLD_AGENT, revenue=310_000, employees=1, sic="7379"),
        ucc_filings=[UCCFiling(secured_party="Lone Star Community Bank", filing_number="TX-26-000111", filing_date=date(2024, 2, 1),
                               state="TX", collateral="All assets including accounts", collateral_class="blanket")],
    )
    efx = CommercialReport(bureau=CommercialBureau.EQUIFAX, report_date=date(2026, 9, 4), file_found=True, insufficient_data=True)
    fin = Financials(
        tax_returns=[TaxReturn(year=2024, form="1120S", gross_receipts=1_080_000, net_income=214_000, depreciation=12_000, interest=6_100, business_code="541510"),
                     TaxReturn(year=2025, form="1120S", gross_receipts=1_240_000, net_income=268_000, depreciation=15_000, interest=7_400, business_code="541510")],
        pnl_period_end=date(2026, 7, 31), pnl_revenue=870_000, pnl_net_income=171_000,
        personal_net_worth=1_420_000,
        bank_months=[],
        consistency_notes=[],
    )
    research = {
        "sos_status": ResearchFinding(item="sos_status", result="found_ok", finding="Texas SOS shows the LLC in existence (active); filing chain complete.", checked_on=AUDIT_DATE),
        "registered_agent": ResearchFinding(item="registered_agent", result="found_ok", finding="Commercial registered agent on file in Austin, TX.", checked_on=AUDIT_DATE),
        "licensing": ResearchFinding(item="licensing", result="not_applicable", finding="No specialized state license identified for IT consulting (TX TDLR, SOS licensing directory checked).", checked_on=AUDIT_DATE),
        "domain": ResearchFinding(item="domain", result="found_ok", finding="northwind-example.com active; registered 2022; auto-renew on.", checked_on=AUDIT_DATE),
        "website": ResearchFinding(item="website", result="found_ok", finding="Live site describes managed cloud services; footer shows the Meridian Blvd office.", checked_on=AUDIT_DATE),
        "ucc_search": ResearchFinding(item="ucc_search", result="found_ok", finding="Texas SOS UCC search: one active filing by Lone Star Community Bank.", checked_on=AUDIT_DATE),
    }
    return Case(id="demo0001", intake=intake, documents=docs, identity_sources=sources, consumer_credit=[consumer],
                commercial_reports=[exp, dnb, efx], financials=fin, research=research,
                meta=ReportMeta(report_number="TLA-FRA-2609-0001", revision=0, stage="DRAFT", analyst="Demo Analyst", report_date=AUDIT_DATE))
