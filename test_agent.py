import re

import pytest

import agent
from ledger import grams
from test_ledger import job_with_gap

# Written separately from agent.BLAME on purpose, so a weakened list in agent.py is still caught here.
BLAMING = ["fault", "stole", "steal", "theft", "thief", "cheat", "blame", "guilty", "liar", "fraud",
           "चोर", "चोरी", "गलती", "दोष", "धोखा", "ಕಳ್ಳ", "ಕಳವು", "ತಪ್ಪು", "ಮೋಸ"]


def situations():
    """(name, reconcile, findings, chain_ok) for every state the demo can reach."""
    out = []
    L = job_with_gap()  # 0.500 g gap, scrap without a photo
    out.append(("gap", L.reconcile("J1"), L.investigate("J1"), True))
    L.record("J1", "scrap", 3000, "karigar", corrects=6, evidence="scale3.jpg")  # re-weighed, not yet confirmed
    out.append(("pending", L.reconcile("J1"), L.investigate("J1"), True))
    L.confirm(8, "jeweller")
    out.append(("settled", L.reconcile("J1"), L.investigate("J1"), True))
    L.entries[4]["mg"] = 97000  # someone quietly edits the return weight
    out.append(("tampered", L.reconcile("J1"), L.investigate("J1"), L.verify() is None))
    return out


def everything(answer):
    return " ".join([answer["summary"], *answer["points"], answer["next"]])


@pytest.fixture(autouse=True)
def no_key(monkeypatch):
    monkeypatch.delenv("SUVARNA_LLM_API_KEY", raising=False)
    monkeypatch.delenv("SUVARNA_LLM_MODEL", raising=False)
    agent._llm.cache_clear()


@pytest.mark.parametrize("lang", agent.LANGS)
def test_works_without_a_key_in_every_language(lang):
    for name, r, f, ok in situations():
        a = agent.explain(r, f, lang, ok)
        assert a["source"] == "template" and a["summary"] and a["next"], name
        assert len(a["points"]) == len(f)


@pytest.mark.parametrize("lang", agent.LANGS)
def test_never_states_a_weight_that_is_not_in_its_input(lang):
    for name, r, f, ok in situations():
        given = set(re.findall(r"\d+\.\d{3}", " ".join(f))) | {grams(v)[:-2] for v in r.values() if isinstance(v, int)}
        said = set(re.findall(r"\d+\.\d{3}", everything(agent.explain(r, f, lang, ok))))
        assert said <= given, (name, said - given)


@pytest.mark.parametrize("lang", agent.LANGS)
def test_never_blames_anyone(lang):
    for name, r, f, ok in situations():
        text = everything(agent.explain(r, f, lang, ok)).lower()
        assert not [w for w in BLAMING if w in text], name


@pytest.mark.parametrize("lang", ["hi", "kn"])
def test_every_ledger_finding_is_translated(lang):
    for name, r, f, ok in situations():
        assert not any(p in f for p in agent.explain(r, f, lang, ok)["points"]), name


def test_next_step_follows_the_records():
    steps = {name: agent.explain(r, f, "en", ok)["next"] for name, r, f, ok in situations()}
    assert "scale photo" in steps["gap"]
    assert "the jeweller checks the waiting entry" in steps["pending"]
    assert "approve" in steps["settled"]
    assert "No payment" in steps["tampered"]


def with_llm(monkeypatch, reply):
    monkeypatch.setenv("SUVARNA_LLM_API_KEY", "test-key")
    monkeypatch.setenv("SUVARNA_LLM_MODEL", "test-model")

    def fake(facts, lang):
        if isinstance(reply, Exception):
            raise reply
        return {"summary": reply[0], "points": [], "next": reply[1], "source": "llm"}
    monkeypatch.setattr(agent, "_ask_llm", fake)
    _, r, f, ok = situations()[0]
    return agent.explain(r, f, "en", ok)


def test_a_good_llm_answer_is_used(monkeypatch):
    a = with_llm(monkeypatch, ("0.500 g is not explained yet; the scrap of 2.500 g has no photo.", "Re-weigh it together."))
    assert a["source"] == "llm"


def test_an_llm_answer_with_an_invented_weight_is_replaced(monkeypatch):
    assert with_llm(monkeypatch, ("About 0.5 g is missing.", "Re-weigh."))["source"] == "template"


def test_an_llm_answer_that_blames_is_replaced(monkeypatch):
    assert with_llm(monkeypatch, ("The karigar may have stolen 0.500 g.", "Ask him."))["source"] == "template"


def test_an_api_error_falls_back_to_the_templates(monkeypatch):
    assert with_llm(monkeypatch, OSError("network down"))["source"] == "template"
