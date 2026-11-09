"""SUVARNA TRUST demo server: one shared ledger, two parties. Run: python -m uvicorn server:app --port 8770"""
import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ledger import Ledger, grams

HERE = pathlib.Path(__file__).parent
app = FastAPI()
JOB, RATE = "J-1042", 50000  # demo order; labour Rs 500 per gram, in paise
state = {"ledger": Ledger()}


def seed():
    """The demo story: 100 g issued for a bridal necklace, work returned with a 0.5 g gap and no photo on the scrap."""
    L = Ledger()
    e = L.record(JOB, "issue", 100000, "jeweller", evidence="scale-issue.jpg", note="Bridal necklace, 22K")
    L.confirm(e["n"], "karigar")
    e = L.record(JOB, "wastage", 1000, "jeweller", note="Agreed wastage, 1%")
    L.confirm(e["n"], "karigar")
    e = L.record(JOB, "return", 96000, "karigar", evidence="scale-return.jpg", note="Necklace finished")
    L.confirm(e["n"], "jeweller")
    e = L.record(JOB, "scrap", 2500, "karigar", note="Filings and cuttings")
    L.confirm(e["n"], "jeweller")
    state["ledger"] = L


seed()


def view():
    L = state["ledger"]
    s = L.settlement(JOB, RATE)
    entries = [{**e, "grams": grams(e["mg"]) if "mg" in e else None, "confirmed": e["type"] == "weight" and L.is_confirmed(e["n"])}
               for e in L.entries]
    r = L.reconcile(JOB)
    return {"job": JOB, "rate_paise_per_g": RATE, "entries": entries, "chain_ok": L.verify() is None,
            "reconcile": {k: (grams(v) if isinstance(v, int) else None) for k, v in r.items() if k not in ("job", "pending")}
                         | {"unexplained_mg": r["unexplained"]},
            "findings": L.investigate(JOB), "settlement": s}


class Record(BaseModel):
    kind: str
    mg: int
    by: str
    evidence: str | None = None
    note: str = ""
    corrects: int | None = None


class Act(BaseModel):
    by: str
    ref: int | None = None
    seen_hash: str | None = None


def guarded(fn):
    try:
        fn()
    except (ValueError, PermissionError) as e:
        raise HTTPException(400, str(e))
    return view()


@app.get("/")
def index():
    return FileResponse(HERE / "web" / "index.html")


@app.get("/api/state")
def get_state():
    return view()


@app.post("/api/record")
def record(r: Record):
    return guarded(lambda: state["ledger"].record(JOB, r.kind, r.mg, r.by, r.evidence, r.note, r.corrects))


@app.post("/api/confirm")
def confirm(a: Act):
    return guarded(lambda: state["ledger"].confirm(a.ref, a.by))


@app.post("/api/approve")
def approve(a: Act):
    return guarded(lambda: state["ledger"].approve(JOB, a.by, RATE, a.seen_hash))


@app.post("/api/pay")
def pay():
    return guarded(lambda: state["ledger"].pay(JOB, RATE))


@app.post("/api/tamper")
def tamper():
    """Demo only: quietly edit an old entry the way a notebook can be edited, to show the chain catching it."""
    state["ledger"].entries[4]["mg"] = 97000
    return view()


@app.post("/api/reset")
def reset():
    seed()
    return view()
