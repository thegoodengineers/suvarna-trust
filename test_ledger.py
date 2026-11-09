import datetime

import pytest

from ledger import Ledger, grams

RATE = 50000  # Rs 500 per gram labour, in paise


def job_with_gap():
    """The example from our idea submission: 100 g issued, 96 g jewellery + 2.5 g scrap back, 1 g agreed wastage."""
    L = Ledger()
    for kind, mg, by, ev in [("issue", 100000, "jeweller", "scale1.jpg"), ("wastage", 1000, "jeweller", None),
                             ("return", 96000, "karigar", "scale2.jpg"), ("scrap", 2500, "karigar", None)]:
        e = L.record("J1", kind, mg, by, evidence=ev)
        L.confirm(e["n"], "karigar" if by == "jeweller" else "jeweller")
    return L


def test_grams_never_uses_floats():
    assert grams(96000) == "96.000 g" and grams(500) == "0.500 g" and grams(-1) == "-0.001 g"


def test_reconciliation_to_the_milligram():
    r = job_with_gap().reconcile("J1")
    assert (r["issue"], r["return"], r["scrap"], r["wastage"], r["unexplained"]) == (100000, 96000, 2500, 1000, 500)


def test_unconfirmed_entries_do_not_count_and_are_explained():
    L = job_with_gap()
    L.record("J1", "scrap", 500, "karigar", note="found in the polishing dust")
    r = L.reconcile("J1")
    assert r["unexplained"] == 500 and len(r["pending"]) == 1
    assert any("not yet confirmed by the jeweller" in f for f in L.investigate("J1"))


def test_only_the_other_party_can_confirm():
    L = Ledger()
    e = L.record("J1", "issue", 1000, "jeweller")
    with pytest.raises(ValueError):
        L.confirm(e["n"], "jeweller")
    L.confirm(e["n"], "karigar")
    with pytest.raises(ValueError):
        L.confirm(e["n"], "karigar")


def test_weights_must_be_whole_milligrams():
    L = Ledger()
    for bad in (95.5, -1, "100", True):
        with pytest.raises(ValueError):
            L.record("J1", "issue", bad, "jeweller")


def test_tampering_with_history_is_detected():
    L = job_with_gap()
    assert L.verify() is None
    L.entries[4]["mg"] = 98000  # someone quietly edits the return weight (entry 4)
    assert L.verify() == 4


def test_correction_replaces_without_erasing():
    L = job_with_gap()
    fix = L.record("J1", "scrap", 3000, "karigar", corrects=6, note="re-weighed together")  # entry 6 is the scrap
    L.confirm(fix["n"], "jeweller")
    assert L.reconcile("J1")["unexplained"] == 0
    assert L.entries[6]["mg"] == 2500  # the old entry is still there
    assert any("corrected from 2.500 g to 3.000 g" in f for f in L.investigate("J1"))


def test_no_payment_until_both_approve_the_same_settlement():
    L = job_with_gap()
    s = L.settlement("J1", RATE)
    assert not s["ready"] and "0.500 g is unexplained" in s["blocked"]
    with pytest.raises(PermissionError):
        L.approve("J1", "jeweller", RATE, s["hash"])  # can't approve while gold is unexplained
    with pytest.raises(PermissionError):
        L.pay("J1", RATE)
    fix = L.record("J1", "scrap", 3000, "karigar", corrects=6)
    L.confirm(fix["n"], "jeweller")
    s = L.settlement("J1", RATE)
    assert s["labour_paise"] == 96000 * RATE // 1000 == 4800000  # Rs 48,000 for 96 g
    L.approve("J1", "jeweller", RATE, s["hash"])
    assert L.settlement("J1", RATE)["blocked"] == "waiting for karigar to approve"
    with pytest.raises(PermissionError):
        L.pay("J1", RATE)
    L.approve("J1", "karigar", RATE, s["hash"])
    pay = L.pay("J1", RATE)
    assert pay["mock"] and pay["paise"] == 4800000
    with pytest.raises(PermissionError):
        L.pay("J1", RATE)  # never twice
    assert L.verify() is None


def test_approval_lapses_if_anything_changes():
    L = job_with_gap()
    fix = L.record("J1", "scrap", 3000, "karigar", corrects=6)
    L.confirm(fix["n"], "jeweller")
    s = L.settlement("J1", RATE)
    L.approve("J1", "jeweller", RATE, s["hash"])
    with pytest.raises(ValueError):
        L.approve("J1", "karigar", RATE, "stale-hash")  # karigar was shown an old version
    L.approve("J1", "karigar", RATE + 1000, L.settlement("J1", RATE + 1000)["hash"])  # rate changed
    assert L.settlement("J1", RATE + 1000)["blocked"] == "waiting for jeweller to approve"


def test_a_tampered_ledger_cannot_be_settled():
    L = job_with_gap()
    fix = L.record("J1", "scrap", 3000, "karigar", corrects=6)
    L.confirm(fix["n"], "jeweller")
    s = L.settlement("J1", RATE)
    L.approve("J1", "jeweller", RATE, s["hash"])
    L.approve("J1", "karigar", RATE, s["hash"])
    L.entries[0]["mg"] = 99000  # the issue weight is quietly lowered after both approved
    assert "entry 0 was changed" in L.settlement("J1", RATE)["blocked"]
    with pytest.raises(PermissionError):
        L.pay("J1", RATE)


def test_missing_scale_photo_is_pointed_out_without_blame():
    found = job_with_gap().investigate("J1")
    assert found == ["The scrap of 2.500 g has no scale photo. Re-weighing together and recording it with a photo would settle it."]


def wedding_order(due):
    """The second demo order: 40 g for wedding bangles, due on a date, nothing back yet."""
    L = job_with_gap()
    e = L.record("J2", "issue", 40000, "jeweller", evidence="scale4.jpg", note="Wedding bangles, 22K")
    L.confirm(e["n"], "karigar")
    L.set_due("J2", due, "jeweller")
    return L


def test_deadline_risk_for_a_late_wedding_piece():
    today = datetime.date(2026, 11, 9)
    assert wedding_order("2026-11-20").deadline("J2", today) == {"due": "2026-11-20", "days_left": 11, "status": "on time"}
    assert wedding_order("2026-11-12").deadline("J2", today)["status"] == "at risk"  # 3 days left
    assert wedding_order("2026-11-09").deadline("J2", today)["status"] == "at risk"  # due today
    assert wedding_order("2026-11-08").deadline("J2", today) == {"due": "2026-11-08", "days_left": -1, "status": "late"}
    assert job_with_gap().deadline("J1", today) is None  # no date agreed, no warning


def test_a_new_due_date_is_a_new_entry_and_the_latest_counts():
    L = wedding_order("2026-11-08")
    L.set_due("J2", "2026-11-25", "jeweller")
    assert L.deadline("J2", datetime.date(2026, 11, 9))["status"] == "on time"
    assert [e["due"] for e in L.entries if e["type"] == "due"] == ["2026-11-08", "2026-11-25"]
    assert L.verify() is None


def test_only_a_confirmed_return_ends_the_deadline_warning():
    L = wedding_order("2026-11-08")
    today = datetime.date(2026, 11, 9)
    e = L.record("J2", "return", 39000, "karigar", evidence="scale5.jpg")
    assert L.deadline("J2", today)["status"] == "late"  # recorded but not yet confirmed
    L.confirm(e["n"], "jeweller")
    assert L.deadline("J2", today)["status"] == "returned"


def test_bad_due_dates_are_refused():
    L = Ledger()
    for bad in ("2026-02-30", "next week", ""):
        with pytest.raises(ValueError):
            L.set_due("J2", bad, "jeweller")


def test_two_orders_in_one_ledger_do_not_mix():
    L = wedding_order("2026-11-12")
    r1, r2 = L.reconcile("J1"), L.reconcile("J2")
    assert (r1["issue"], r1["unexplained"]) == (100000, 500)
    assert (r2["issue"], r2["return"], r2["unexplained"]) == (40000, 0, 40000)
    assert L.investigate("J2") == []  # work still out with the karigar: nothing to explain yet
