"""SUVARNA TRUST demo server: one shared ledger, two parties. Run: python -m uvicorn server:app --port 8770"""
import datetime
import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

import agent
from ledger import Ledger, grams

HERE = pathlib.Path(__file__).parent
app = FastAPI()
# Demo orders and their labour rates in paise per gram (Rs 500 and Rs 700).
JOBS = {"J-1042": {"rate": 50000, "title": "Bridal necklace"},
        "J-1043": {"rate": 70000, "title": "Wedding bangles"}}
JOB = "J-1042"
state = {"ledger": Ledger()}


def seed():
    """Two demo stories in one shared ledger.
    J-1042: 100 g issued for a bridal necklace, work returned with a 0.5 g gap and no photo on the scrap.
    J-1043: 40 g issued for wedding bangles 12 days ago, due in 2 days, nothing back yet: a deadline at risk."""
    L, today = Ledger(), datetime.date.today()
    e = L.record(JOB, "issue", 100000, "jeweller", evidence="scale-issue.jpg", note="Bridal necklace, 22K")
    L.confirm(e["n"], "karigar")
    e = L.record(JOB, "wastage", 1000, "jeweller", note="Agreed wastage, 1%")
    L.confirm(e["n"], "karigar")
    e = L.record(JOB, "return", 96000, "karigar", evidence="scale-return.jpg", note="Necklace finished")
    L.confirm(e["n"], "jeweller")
    e = L.record(JOB, "scrap", 2500, "karigar", note="Filings and cuttings")
    L.confirm(e["n"], "jeweller")
    e = L.record("J-1043", "issue", 40000, "jeweller", evidence="scale-issue-2.jpg", note="Wedding bangles, pair, 22K")
    L.confirm(e["n"], "karigar")
    L.set_due("J-1043", (today + datetime.timedelta(days=2)).isoformat(), "jeweller")
    state["ledger"] = L


seed()


def job_of(job):
    if job not in JOBS:
        raise HTTPException(404, f"no order {job}")
    return job


def view(job=JOB):
    L, rate = state["ledger"], JOBS[job]["rate"]
    s = L.settlement(job, rate)
    entries = [{**e, "grams": grams(e["mg"]) if "mg" in e else None, "confirmed": e["type"] == "weight" and L.is_confirmed(e["n"])}
               for e in L.entries if e["job"] == job]
    r, findings, chain_ok = L.reconcile(job), L.investigate(job), L.verify() is None
    due = L.deadline(job, datetime.date.today())
    return {"job": job, "jobs": JOBS, "rate_paise_per_g": rate, "entries": entries, "chain_ok": chain_ok,
            "all_entries": len(L.entries), "deadline": due,
            "reconcile": {k: (grams(v) if isinstance(v, int) else None) for k, v in r.items() if k not in ("job", "pending")}
                         | {"unexplained_mg": r["unexplained"]},
            "findings": findings, "agent": {lang: agent.explain(r, findings, lang, chain_ok, due) for lang in agent.LANGS},
            "settlement": s}


class Record(BaseModel):
    kind: str
    mg: int
    by: str
    evidence: str | None = None
    note: str = ""
    corrects: int | None = None
    job: str = JOB


class Act(BaseModel):
    by: str = ""
    ref: int | None = None
    seen_hash: str | None = None
    job: str = JOB


def guarded(job, fn):
    job = job_of(job)
    try:
        fn()
    except (ValueError, PermissionError) as e:
        raise HTTPException(400, str(e))
    return view(job)


@app.get("/")
def index():
    return FileResponse(HERE / "web" / "index.html")


@app.get("/api/state")
def get_state(job: str = JOB):
    return view(job_of(job))


@app.post("/api/record")
def record(r: Record):
    return guarded(r.job, lambda: state["ledger"].record(r.job, r.kind, r.mg, r.by, r.evidence, r.note, r.corrects))


@app.post("/api/confirm")
def confirm(a: Act):
    return guarded(a.job, lambda: state["ledger"].confirm(a.ref, a.by))


@app.post("/api/approve")
def approve(a: Act):
    return guarded(a.job, lambda: state["ledger"].approve(a.job, a.by, JOBS[a.job]["rate"], a.seen_hash))


@app.post("/api/pay")
def pay(a: Act):
    return guarded(a.job, lambda: state["ledger"].pay(a.job, JOBS[a.job]["rate"]))


@app.post("/api/tamper")
def tamper(a: Act):
    """Demo only: quietly edit an old entry the way a notebook can be edited, to show the chain catching it."""
    state["ledger"].entries[4]["mg"] = 97000
    return view(job_of(a.job))


@app.post("/api/reset")
def reset(a: Act):
    seed()
    return view(job_of(a.job))
