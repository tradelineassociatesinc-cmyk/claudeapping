from datetime import date

from fra.demo import AUDIT_DATE, demo_case
from fra.engine.audit import run_audit
from fra.engine.guarantor import mid_score
from fra.engine.identity import compare_address, compare_entity, compare_names
from fra.models import Address, Status


def test_mid_score():
    assert mid_score([700, 750, 720]) == 720
    assert mid_score([700, 750]) == 700
    assert mid_score([690]) == 690
    assert mid_score([]) is None


def test_name_comparison():
    assert compare_names("Northwind Example LLC", "NORTHWIND EXAMPLE, L.L.C.") == "EQUIVALENT"
    assert compare_names("Acme Inc", "Acme Corp") == "VARIANT"
    assert compare_names("Acme LLC", "Apex LLC") == "CONFLICT"
    assert compare_names("Acme LLC", "") == "BLANK"


def test_entity_comparison():
    assert compare_entity("Limited Liability Company", "LLC") == "EQUIVALENT"
    assert compare_entity("Limited Liability Company", "S corporation") == "EQUIVALENT"  # tax classification
    assert compare_entity("Limited Liability Company", "Corporation") == "CONFLICT"


def test_address_comparison():
    a = Address(line1="2200 Meridian Boulevard", line2="Suite 140", city="Austin", state="TX", zip="78741")
    b = Address(line1="2200 Meridian Blvd", line2="Ste 140", city="Austin", state="TX", zip="78741-1234")
    assert compare_address(a, b) == "EQUIVALENT"
    c = Address(line1="2200 Meridian Blvd", line2="", city="Austin", state="TX", zip="78741")
    assert compare_address(a, c) == "VARIANT"


def test_demo_audit_key_findings():
    r = run_audit(demo_case(), AUDIT_DATE)
    f = {x.number: x for x in r.findings}
    assert f[1].status == Status.AR          # TIN conflict on bank certification
    assert f[15].status == Status.AR         # two address candidates, none designated
    assert f[8].status == Status.AR          # free-mail with a domain owned
    assert f[10].status == Status.PEND       # statements outstanding
    assert f[16].status == Status.NA         # Texas entity operating in TX
    assert f[18].status == Status.NI         # blanket UCC + lien-taking goal
    assert f[17].status == Status.AR         # Experian blank legal name / wrong type
    assert not r.composite.issued            # withheld on an incomplete file
    assert len(r.first_three) == 3


def test_ranges_capped_at_request():
    r = run_audit(demo_case(), AUDIT_DATE)
    for p in r.products:
        if p.range_high:
            assert p.range_high <= 150_000
            assert p.range_low <= p.range_high


def test_card_stack_blocked_by_recent_late():
    r = run_audit(demo_case(), AUDIT_DATE)
    bc = next(p for p in r.products if p.code == "BC")
    assert bc.fit == "NOT YET"
    assert bc.earliest_ready == date(2027, 2, 1)


def test_override_applies():
    case = demo_case()
    from fra.models import PointOverride
    case.overrides["6"] = PointOverride(status=Status.PASS, finding="Verified by analyst", note="411 confirmed by phone")
    r = run_audit(case, AUDIT_DATE)
    f6 = r.findings[5]
    assert f6.status == Status.PASS and f6.overridden
