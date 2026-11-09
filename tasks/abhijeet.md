# Abhijeet: the agent that explains gaps, and the architecture

## Rule for everyone: never name the tools we used to build this
Do not name any assistant, chatbot or code tool used to build this project anywhere: commits, co-author lines,
code comments, README, docs, the form, the deck, screenshots or videos. No `Co-Authored-By` lines for tools.
Describing the product's own agent is fine. Before you push: `git log --format=%B | grep -i co-authored` prints nothing.
Branch: `<yourname>/<task>` → pull request into `main`. Run `python -m pytest -q` before every push.

## 1. Agent: extend `agent.py`, don't start from zero (by 13 Nov, 9:00 PM)
A first version is merged. `agent.explain(reconcile, findings, lang, chain_ok)` turns the ledger's facts into a
short, polite explanation in `en`, `hi` or `kn` plus one next step, and both phones show it under
"What the records show". Read `agent.py` and `test_agent.py` first (about 150 lines together).
What is already there:
- Fixed templates for every sentence `ledger.investigate()` writes, in three languages. These work with no key.
- An optional language model (any OpenAI-compatible endpoint) when `SUVARNA_LLM_API_KEY` and `SUVARNA_LLM_MODEL`
  are set. Its answer is thrown away, and the templates used, if it states a number not in the input, uses a
  blaming word, or the call fails. Never commit a key.
- Tests: no invented weights, no blame, works without a key, every finding translated, bad model answers replaced.

What is left for you:
- [ ] Check our Lyzr AI credits (the event's AI partner). If it fits, point `SUVARNA_LLM_URL` at it or add a small
      `_ask_lyzr()` beside `_ask_llm()`; the safety checks in `safe()` must stay in front of whatever you call.
- [ ] Try it with a real key on all four demo states (gap, re-weighed, settled, tampered) in all three languages.
      Paste one good and one rejected answer into your pull request.
- [ ] Get Bhumika's Kannada checker to read the `kn` templates in `SAY`, the same way as the karigar phone.
- [ ] If `ledger.investigate()` gains a new sentence, add its shape to `SHAPES` and a line in each language;
      `test_every_ledger_finding_is_translated` fails until you do.
- [ ] Stretch: let the karigar ask "why?" by voice and get the same explanation read aloud.
- Rule that does not change: the agent explains and suggests. It never computes a balance, moves money, approves,
  or closes a dispute. It only gets read-only facts, not the ledger object.

## 2. Architecture note (by 14 Nov)
- New file: `docs/ARCHITECTURE.md`, one page, for the form's architecture question:
- [ ] Offline-first: how a phone saves entries without network and syncs later without breaking the seal
      (each phone keeps its own entries; the server orders them; conflicts become entries both confirm).
- [ ] Where the agent sits, what tools it may call, and what it may never do (move money, close a dispute).
- [ ] Assisted path: how a JanAI Café operator helps a karigar with no smartphone, with his own voice confirmation.
