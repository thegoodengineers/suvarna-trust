# SUVARNA TRUST architecture (one page)

What exists today is marked **built**; the rest is the prototype-round plan.

```
 Karigar phone (Android Go, offline)        Jeweller phone / shop PC            JanAI Café kiosk
 ├ voice + Kannada/Hindi UI                 ├ same UI, English                  ├ operator's screen
 ├ local outbox of signed entries           ├ local outbox                      └ karigar's own voice "yes"
 └ local copy of the sealed chain           └ local copy of the chain
               │  sync when there is any network (SMS fallback for a single confirm)  │
               ▼                                                                      ▼
        Sync server ── orders entries, seals them ──> Ledger core (ledger.py, built)
                                                      │ read-only facts
                                                      ▼
                                              Agent (agent.py, built) ──> explanation + next step
                                                      │ proposes, never executes
                                                      ▼
                                       Settlement: both approve → payment (mock UPI, built)
```

## 1. The ledger core (built: `ledger.py`, `test_ledger.py`)
Append-only list of entries: weights in whole milligrams, confirmations, approvals, payment. Each entry
carries the hash of the one before it, so changing any old entry breaks every seal after it. An entry counts
only when the other party confirms it. A correction is a new entry pointing at the old one. Payment needs
both approvals of the exact settlement hash, nothing unexplained, and an intact chain. **This is the only
place a gold balance is ever computed.**

## 2. Offline-first sync that keeps the seal intact (plan)
Karigar workshops often have weak network, so a phone must record a return or a confirmation with none.
- **Each phone signs its own entries.** On first use the phone makes a key pair; the public key is
  registered with the jeweller's shop. An offline entry is `{job, kind, mg, evidence, device, local_seq,
  signature}`. Nobody, the server included, can change it without the signature failing.
- **Phones do not seal; the server does.** Offline entries wait in the phone's outbox. On sync the server
  checks the signature, appends the entry to the job's chain in arrival order and returns the new seal.
  Each phone keeps a copy of the sealed chain and re-verifies it, so a server that rewrote history would be
  caught by either phone.
- **Conflicts never overwrite.** If both sides recorded the same thing differently while offline (e.g.
  2.500 g and 3.000 g of scrap), both are appended. Neither is confirmed by the other side, so neither counts,
  and the agent says so. The parties settle it with one more entry that both confirm, exactly like a
  correction today. No "last write wins".
- **Smallest link.** A single confirm or approve can go by SMS (job, entry number, first 8 hex characters
  of the seal, signature) when there is no data at all.

## 3. Where the agent sits, and what it may never do (built: `agent.py`, `test_agent.py`)
The agent reads `reconcile()`, `investigate()` and whether the chain is intact, and writes a short,
polite explanation in Kannada, Hindi or English with one suggested next step ("re-weigh the scrap together
with a scale photo"). It can use a language model, but every answer is checked: a number that is not in its
input, or a blaming word, and the answer is replaced by fixed templates. The same happens if the model is
unreachable, so the demo works with no key and no network.

### Switching on Lyzr (the event's AI partner)
`agent.py` calls a Lyzr agent through Lyzr's documented Agent API (`POST
https://agent-prod.studio.lyzr.ai/v3/inference/chat/`, header `x-api-key`, body `user_id`, `agent_id`,
`session_id`, `message`). It needs a Lyzr Studio account, so it is off until someone with our credits does this:
1. Sign in at studio.lyzr.ai with the team account, create an agent (any model; role "explains a shared gold
   record politely"), and copy its agent ID and the account's API key.
2. Before starting the server: `SUVARNA_LYZR_API_KEY=<key>` and `SUVARNA_LYZR_AGENT_ID=<id>` (PowerShell:
   `$env:SUVARNA_LYZR_API_KEY="<key>"`). Never commit the key.
3. Run the demo; the explanation's `source` in `/api/state` says `lyzr` when its answer was used.
The rules are sent in every message, so the agent's Studio instructions cannot loosen them, and every answer
still passes the same check (no new numbers, no blame) or the templates are used. If both Lyzr and
`SUVARNA_LLM_*` are set, Lyzr is used. Tests (`test_agent.py`) check the request shape without a network.

Tools it may use (prototype round): read a job's facts; draft a reminder for the jeweller or karigar to
send themselves; read a scale photo and *propose* a weight that the person then records and the other
party confirms; warn about a deadline.

It may **never**: compute or change a balance, record or confirm a weight in anyone's name, approve a
settlement, move money, decide who is right, or close a dispute. It is never given the ledger object, only
read-only facts, so these are not just rules but things it has no way to do.

## 4. The JanAI Café assisted path (plan)
For a karigar with no smartphone. A JanAI Café operator logs in with their own operator ID and opens the
job by the karigar's phone number. The screen reads the entry aloud in Kannada or Hindi; the karigar says
"yes" (or presses 1 on a call from the shop's number) and that voice clip's hash is stored as the evidence
on the karigar's confirm entry, with the operator's ID beside it. The operator can help record and read, never approve
a payment alone: approval still needs the karigar's own voice "yes" or OTP on their basic phone. The
karigar's history then works as a Trust Passport they can show the next jeweller.

## 5. Running on cheap hardware
Plain HTML and a few kilobytes of script, no framework; the voice uses the phone's built-in speech engine.
The server is a single Python process (FastAPI). The ledger is a list in memory in the demo; in the
prototype it becomes one SQLite file per shop, backed up daily.
