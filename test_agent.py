import datetime
import re

import pytest

import agent
from ledger import grams
from test_ledger import job_with_gap, wedding_order

# Written separately from agent.BLAME on purpose, so a weakened list in agent.py is still caught here.
BLAMING = ["fault", "stole", "steal", "theft", "thief", "cheat", "blame", "guilty", "liar", "fraud",
           "चोर", "चोरी", "गलती", "दोष", "धोखा", "ಕಳ್ಳ", "ಕಳವು", "ತಪ್ಪು", "ಮೋಸ"]


def situations():
    """(name, reconcile, findings, chain_ok, deadline) for every state the demo can reach."""
    out = []
    today = datetime.date(2026, 11, 9)
    for name, due in [("due-soon", "2026-11-11"), ("due-today", "2026-11-09"), ("overdue", "2026-11-05")]:
        W = wedding_order(due)
        out.append((name, W.reconcile("J2"), W.investigate("J2"), True, W.deadline("J2", today)))
    L = job_with_gap()  # 0.500 g gap, scrap without a photo
    out.append(("gap", L.reconcile("J1"), L.investigate("J1"), True, None))
    L.record("J1", "scrap", 3000, "karigar", corrects=6, evidence="scale3.jpg")  # re-weighed, not yet confirmed
    out.append(("pending", L.reconcile("J1"), L.investigate("J1"), True, None))
    L.confirm(8, "jeweller")
    out.append(("settled", L.reconcile("J1"), L.investigate("J1"), True, None))
    L.entries[4]["mg"] = 97000  # someone quietly edits the return weight
    out.append(("tampered", L.reconcile("J1"), L.investigate("J1"), L.verify() is None, None))
    return out


def everything(answer):
    return " ".join([answer["summary"], *answer["points"], answer["next"]])


@pytest.fixture(autouse=True)
def no_key(monkeypatch):
    monkeypatch.delenv("SUVARNA_LLM_API_KEY", raising=False)
    monkeypatch.delenv("SUVARNA_LLM_MODEL", raising=False)
    monkeypatch.delenv("SUVARNA_LYZR_API_KEY", raising=False)
    monkeypatch.delenv("SUVARNA_LYZR_AGENT_ID", raising=False)
    agent._llm.cache_clear()


@pytest.mark.parametrize("lang", agent.LANGS)
def test_works_without_a_key_in_every_language(lang):
    for name, r, f, ok, d in situations():
        a = agent.explain(r, f, lang, ok, d)
        assert a["source"] == "template" and a["summary"] and a["next"], name
        assert len(a["points"]) == len(f) + (d is not None and d["status"] in ("at risk", "late"))


@pytest.mark.parametrize("lang", agent.LANGS)
def test_never_states_a_weight_that_is_not_in_its_input(lang):
    for name, r, f, ok, d in situations():
        given = set(re.findall(r"\d+\.\d{3}", " ".join(f))) | {grams(v)[:-2] for v in r.values() if isinstance(v, int)}
        said = set(re.findall(r"\d+\.\d{3}", everything(agent.explain(r, f, lang, ok, d))))
        assert said <= given, (name, said - given)


@pytest.mark.parametrize("lang", agent.LANGS)
def test_never_blames_anyone(lang):
    for name, r, f, ok, d in situations():
        text = everything(agent.explain(r, f, lang, ok, d)).lower()
        assert not [w for w in BLAMING if w in text], name


@pytest.mark.parametrize("lang", ["hi", "kn"])
def test_every_ledger_finding_is_translated(lang):
    for name, r, f, ok, d in situations():
        assert not any(p in f for p in agent.explain(r, f, lang, ok, d)["points"]), name


def test_next_step_follows_the_records():
    steps = {name: agent.explain(r, f, "en", ok, d)["next"] for name, r, f, ok, d in situations()}
    assert "scale photo" in steps["gap"]
    assert "the jeweller checks the waiting entry" in steps["pending"]
    assert "approve" in steps["settled"]
    assert "record a new date" in steps["due-soon"] and "record a new date" in steps["overdue"]
    assert "No payment" in steps["tampered"]


def with_llm(monkeypatch, reply):
    monkeypatch.setenv("SUVARNA_LLM_API_KEY", "test-key")
    monkeypatch.setenv("SUVARNA_LLM_MODEL", "test-model")

    def fake(facts, lang):
        if isinstance(reply, Exception):
            raise reply
        return {"summary": reply[0], "points": [], "next": reply[1], "source": "llm"}
    monkeypatch.setattr(agent, "_ask_llm", fake)
    _, r, f, ok, d = [x for x in situations() if x[0] == "gap"][0]
    return agent.explain(r, f, "en", ok, d)


def test_a_good_llm_answer_is_used(monkeypatch):
    a = with_llm(monkeypatch, ("0.500 g is not explained yet; the scrap of 2.500 g has no photo.", "Re-weigh it together."))
    assert a["source"] == "llm"


def test_an_llm_answer_with_an_invented_weight_is_replaced(monkeypatch):
    assert with_llm(monkeypatch, ("About 0.5 g is missing.", "Re-weigh."))["source"] == "template"


def test_an_llm_answer_that_blames_is_replaced(monkeypatch):
    assert with_llm(monkeypatch, ("The karigar may have stolen 0.500 g.", "Ask him."))["source"] == "template"


def test_an_api_error_falls_back_to_the_templates(monkeypatch):
    assert with_llm(monkeypatch, OSError("network down"))["source"] == "template"


def test_the_wedding_piece_warning_reads_right():
    by = {name: agent.explain(r, f, "en", ok, d) for name, r, f, ok, d in situations()}
    assert by["due-soon"]["summary"] == "40.000 g of gold is with the karigar for this order; nothing has come back yet."
    assert by["due-soon"]["points"] == ["The piece is due on 2026-11-11, 2 days from now, and has not come back yet."]
    assert by["due-today"]["points"] == ["The piece is due on 2026-11-09 (today), and has not come back yet."]
    assert by["overdue"]["points"] == ["The piece was due on 2026-11-05 and has not come back yet."]


def with_lyzr(monkeypatch, response):
    """Lyzr switched on, with its HTTP call replaced: records what would be sent, answers with `response`."""
    monkeypatch.setenv("SUVARNA_LYZR_API_KEY", "lyzr-test-key")
    monkeypatch.setenv("SUVARNA_LYZR_AGENT_ID", "agent-123")
    monkeypatch.setenv("SUVARNA_LLM_API_KEY", "test-key")  # both configured: Lyzr wins
    monkeypatch.setenv("SUVARNA_LLM_MODEL", "test-model")
    sent = {}

    def fake_post(url, body, headers):
        sent.update(url=url, body=body, headers=headers)
        if isinstance(response, Exception):
            raise response
        return response
    monkeypatch.setattr(agent, "_post", fake_post)
    _, r, f, ok, d = [x for x in situations() if x[0] == "gap"][0]
    return agent.explain(r, f, "kn", ok, d), sent


def test_lyzr_is_called_the_documented_way(monkeypatch):
    reply = '{"text": "0.500 g ಚಿನ್ನ ಇನ್ನೂ ಲೆಕ್ಕಕ್ಕೆ ಸಿಕ್ಕಿಲ್ಲ.", "next": "ಮತ್ತೆ ತೂಕ ಮಾಡಿ."}'
    a, sent = with_lyzr(monkeypatch, {"response": reply})
    assert a["source"] == "lyzr" and a["summary"].startswith("0.500 g")
    assert sent["url"] == agent.LYZR_URL and sent["headers"] == {"x-api-key": "lyzr-test-key"}
    assert sent["body"]["agent_id"] == "agent-123" and "never add, round or calculate" in sent["body"]["message"]
    assert {"user_id", "session_id", "message"} <= set(sent["body"])


def test_a_lyzr_answer_is_checked_like_any_other(monkeypatch):
    bad = '{"text": "ಕಾರಿಗರ್ ಕದ್ದಿರಬಹುದು, ಸುಮಾರು 0.5 g.", "next": "ಕೇಳಿ."}'  # blames, and rounds the weight
    assert with_lyzr(monkeypatch, {"agent_response": bad})[0]["source"] == "template"
    agent._llm.cache_clear()
    assert with_lyzr(monkeypatch, OSError("no network"))[0]["source"] == "template"
    agent._llm.cache_clear()
    assert with_lyzr(monkeypatch, {"response": "Sure! Here is a friendly version."})[0]["source"] == "template"
