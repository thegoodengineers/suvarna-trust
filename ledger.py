"""SUVARNA TRUST core: a shared, append-only gold ledger between a jeweller and a karigar.

Rules this file enforces (and test_ledger.py checks):
- Weights are whole milligrams (int). No floats anywhere near a gold balance.
- Nothing is ever edited or deleted. A correction is a new entry; agreeing is a new "confirm" entry.
- Every entry carries the hash of the one before it, so changing any old entry breaks the chain.
- Only entries BOTH parties confirmed count in the reconciliation.
- Money moves only after both approve the exact settlement; the payment step is a labelled mock.
The AI layer may explain these results; it never computes them.
"""
import datetime
import hashlib
import json
import time

PARTIES = ("jeweller", "karigar")
WEIGHT_KINDS = ("issue", "return", "scrap", "wastage")  # what reconciliation adds up
OTHER = {"jeweller": "karigar", "karigar": "jeweller"}
WARN_DAYS = 3  # a piece not back within this many days of its due date is "at risk"


def grams(mg):
    """Show milligrams as grams with three decimals, without ever going through a float."""
    sign = "-" if mg < 0 else ""
    return f"{sign}{abs(mg) // 1000}.{abs(mg) % 1000:03d} g"


class Ledger:
    def __init__(self):
        self.entries = []

    # --- writing -------------------------------------------------------------------------------------------
    def _append(self, **fields):
        prev = self.entries[-1]["hash"] if self.entries else "0" * 64
        entry = {"n": len(self.entries), "at": fields.pop("at", int(time.time())), "prev": prev, **fields}
        entry["hash"] = _hash(entry)
        self.entries.append(entry)
        return entry

    def record(self, job, kind, mg, by, evidence=None, note="", corrects=None, at=None):
        """One party records a weight. It counts only once the other party confirms it."""
        if kind not in WEIGHT_KINDS:
            raise ValueError(f"unknown kind {kind!r}")
        if by not in PARTIES:
            raise ValueError(f"unknown party {by!r}")
        if not isinstance(mg, int) or isinstance(mg, bool) or mg < 0:
            raise ValueError("weight must be a whole, non-negative number of milligrams")
        if corrects is not None:
            old = self.get(corrects)
            if old["job"] != job or old["type"] != "weight" or old["kind"] != kind:
                raise ValueError("a correction must replace an entry of the same job and kind")
        return self._append(type="weight", job=job, kind=kind, mg=mg, by=by, evidence=evidence, note=note,
                            corrects=corrects, **({"at": at} if at else {}))

    def confirm(self, ref, by):
        """The OTHER party agrees with an entry. Recording and confirming your own entry is refused."""
        old = self.get(ref)
        if old["type"] != "weight":
            raise ValueError("only weights are confirmed")
        if by != OTHER[old["by"]]:
            raise ValueError("an entry must be confirmed by the other party")
        if self.is_confirmed(ref):
            raise ValueError("already confirmed")
        return self._append(type="confirm", job=old["job"], ref=ref, by=by)

    def set_due(self, job, due, by):
        """Record the date a piece is promised for (YYYY-MM-DD). A new date is a new entry; the old one stays."""
        if by not in PARTIES:
            raise ValueError(f"unknown party {by!r}")
        datetime.date.fromisoformat(due)  # raises ValueError on anything that is not a real date
        return self._append(type="due", job=job, due=due, by=by)

    def approve(self, job, by, rate_paise_per_g, seen_hash):
        """Approve the exact settlement this party was shown (seen_hash). If anything changes afterwards, the
        settlement's hash changes and every earlier approval lapses."""
        if by not in PARTIES:
            raise ValueError(f"unknown party {by!r}")
        s = self.settlement(job, rate_paise_per_g)
        if seen_hash != s["hash"]:
            raise ValueError("the settlement changed since it was shown; show it again before approving")
        if s["blocked"] and not s["blocked"].startswith("waiting for"):
            raise PermissionError("cannot approve yet: " + s["blocked"])
        return self._append(type="approve", job=job, by=by, settlement=s["hash"])

    def pay(self, job, rate_paise_per_g):
        """MOCK UPI. Refused unless both parties approved the current settlement."""
        s = self.settlement(job, rate_paise_per_g)
        if not s["ready"]:
            raise PermissionError("payment refused: " + s["blocked"])
        return self._append(type="payment", job=job, paise=s["labour_paise"], settlement=s["hash"], mock=True)

    # --- reading -------------------------------------------------------------------------------------------
    def get(self, n):
        if not isinstance(n, int) or not 0 <= n < len(self.entries):
            raise ValueError(f"no entry {n}")
        return self.entries[n]

    def is_confirmed(self, n):
        return any(e["type"] == "confirm" and e["ref"] == n for e in self.entries)

    def verify(self):
        """Recompute every hash. Returns the number of the first broken entry, or None if the chain is intact."""
        prev = "0" * 64
        for e in self.entries:
            if e["prev"] != prev or _hash({k: v for k, v in e.items() if k != "hash"}) != e["hash"]:
                return e["n"]
            prev = e["hash"]
        return None

    def current(self, job):
        """The live weight entries of a job: corrected entries are replaced by their latest correction."""
        replaced = {e["corrects"] for e in self.entries if e["type"] == "weight" and e["corrects"] is not None}
        return [e for e in self.entries if e["type"] == "weight" and e["job"] == job and e["n"] not in replaced]

    def reconcile(self, job):
        """issued - returned - scrap - agreed wastage = unexplained, from entries BOTH parties confirmed."""
        totals = {k: 0 for k in WEIGHT_KINDS}
        pending = []
        for e in self.current(job):
            if self.is_confirmed(e["n"]):
                totals[e["kind"]] += e["mg"]
            else:
                pending.append(e)
        unexplained = totals["issue"] - totals["return"] - totals["scrap"] - totals["wastage"]
        return {"job": job, **totals, "unexplained": unexplained, "pending": pending}

    def investigate(self, job):
        """Facts that explain a gap, in plain language. It states what the records show; it never assigns blame."""
        r = self.reconcile(job)
        found = []
        for e in r["pending"]:
            found.append(f"The {e['kind']} of {grams(e['mg'])} recorded by the {e['by']} is not yet confirmed by "
                         f"the {OTHER[e['by']]}, so it is not counted.")
        for e in self.current(job):
            if e["kind"] in ("issue", "return", "scrap") and not e["evidence"]:
                found.append(f"The {e['kind']} of {grams(e['mg'])} has no scale photo. Re-weighing together "
                             f"and recording it with a photo would settle it.")
        corrections = [e for e in self.entries if e["type"] == "weight" and e["job"] == job and e["corrects"] is not None]
        for e in corrections:
            old = self.get(e["corrects"])
            found.append(f"The {e['kind']} was corrected from {grams(old['mg'])} to {grams(e['mg'])} by the {e['by']}.")
        if r["unexplained"] > 0 and not found and (r["return"] or r["scrap"]):  # nothing back yet is not a gap
            found.append(f"{grams(r['unexplained'])} is unaccounted for and every record is confirmed with evidence. "
                         f"Both parties should re-weigh the returned pieces and scrap together.")
        if r["unexplained"] < 0:
            found.append(f"More gold came back than was issued ({grams(-r['unexplained'])} extra). An issue may be "
                         f"missing from the records.")
        return found

    def deadline(self, job, today):
        """Days until the latest agreed due date, and whether the piece is at risk. Calendar maths only, no gold.
        A piece counts as back once a return for the job is confirmed by the other party."""
        dues = [e for e in self.entries if e["type"] == "due" and e["job"] == job]
        if not dues:
            return None
        due = datetime.date.fromisoformat(dues[-1]["due"])
        days = (due - today).days
        back = any(e["kind"] == "return" and self.is_confirmed(e["n"]) for e in self.current(job))
        status = "returned" if back else "late" if days < 0 else "at risk" if days <= WARN_DAYS else "on time"
        return {"due": due.isoformat(), "days_left": days, "status": status}

    def settlement(self, job, rate_paise_per_g):
        """The settlement both must approve. Labour is paid on the confirmed returned weight."""
        if not isinstance(rate_paise_per_g, int) or rate_paise_per_g < 0:
            raise ValueError("labour rate must be whole paise per gram")
        r = self.reconcile(job)
        labour = r["return"] * rate_paise_per_g // 1000
        body = {"job": job, "issue": r["issue"], "return": r["return"], "scrap": r["scrap"], "wastage": r["wastage"],
                "unexplained": r["unexplained"], "labour_paise": labour}
        h = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        approved = {e["by"] for e in self.entries if e["type"] == "approve" and e["job"] == job and e["settlement"] == h}
        paid = any(e["type"] == "payment" and e["job"] == job for e in self.entries)
        blocked = ""
        broken = self.verify()
        if broken is not None:
            blocked = f"entry {broken} was changed after it was recorded; the history no longer matches its seal"
        elif paid:
            blocked = "already paid"
        elif r["pending"]:
            blocked = f"{len(r['pending'])} record(s) still need the other party's confirmation"
        elif r["unexplained"] != 0:
            blocked = f"{grams(r['unexplained'])} is unexplained"
        elif approved != set(PARTIES):
            blocked = "waiting for " + " and ".join(p for p in PARTIES if p not in approved) + " to approve"
        return {**body, "hash": h, "approved_by": sorted(approved), "paid": paid, "ready": not blocked,
                "blocked": blocked}


def _hash(entry):
    return hashlib.sha256(json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
