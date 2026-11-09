# SUVARNA TRUST

Every gram accounted for, every karigar paid on time.

Jewellers hand gold to karigars (artisan goldsmiths) by weight and track it in notebooks. SUVARNA TRUST
keeps one shared record that both sides confirm, reconciles it to the milligram, explains any gap without
blaming anyone, and lets money move only when both approve.

Tech4Bharat 2026, problem statement 2.2 (Jeweltech). Team: The Good Engineers.

## The demo
Two phones and the record they share, side by side. The story it runs:
1. 100 g of 22K gold is issued for a bridal necklace, 1 g agreed wastage. Both confirm.
2. The karigar returns 96 g of jewellery and 2.5 g of scrap. **0.500 g is unexplained.**
3. The record shows why, without blame: the scrap has no scale photo.
4. The karigar re-weighs with a photo (3 g) by typing or by voice. It is a *new* entry that replaces the old
   one; the old one stays visible. The jeweller confirms. Unexplained: 0.
5. Both approve the exact settlement (₹48,000 labour on 96 g). Only then the mock UPI payment runs.
6. "Quietly edit an old entry" changes history the way a notebook can be changed. The seal breaks and
   payment is refused.

The karigar's phone works in Kannada, Hindi or English, reads the account aloud, and takes weights by voice
(browser speech features, best in Chrome), always reading the number back before it is saved.

## What the core guarantees (`ledger.py`, checked by `test_ledger.py`)
- Weights are whole milligrams. No floating point anywhere near a gold balance.
- Nothing is edited or deleted. Corrections and confirmations are new entries.
- Each entry is sealed with the hash of the one before it; any change to history is detected.
- Only entries the *other* party confirmed count. You can't confirm your own entry.
- An approval is for one exact settlement. If anything changes, earlier approvals lapse.
- Payment is refused unless both approved, nothing is unexplained, and the history is intact. Never twice.
- The AI layer (prototype round) explains and coordinates. It never computes a balance or decides a dispute.

## Run it
```
python -m pip install -r requirements.txt
python -m pytest -q                              # 11 checks on the ledger
python -m uvicorn server:app --port 8770         # open http://localhost:8770
```

## Next (prototype round, if shortlisted)
Separate jeweller and karigar logins, offline-first sync on entry-level Android, scale-photo reading,
the investigation agent explaining gaps in Kannada and Hindi, deadline alerts, the karigar's Trust
Passport, and an assisted JanAI Café path.

Demo data is illustrative, not field data. Payment is simulated and labelled.
Design references and choices: `design/REFS.md`.

## Team
How we work, dates and who owns what: [`CONTRIBUTING.md`](CONTRIBUTING.md). Each person's tasks: [`tasks/`](tasks/).
Field interview guide: [`docs/FIELD.md`](docs/FIELD.md). Form answers: [`docs/FORM_ANSWERS.md`](docs/FORM_ANSWERS.md).
