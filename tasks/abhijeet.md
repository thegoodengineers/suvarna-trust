# Abhijeet: the agent that explains gaps, and the architecture

## Rule for everyone: never name the tools we used to build this
Do not name any assistant, chatbot or code tool used to build this project anywhere: commits, co-author lines,
code comments, README, docs, the form, the deck, screenshots or videos. No `Co-Authored-By` lines for tools.
Describing the product's own agent is fine. Before you push: `git log --format=%B | grep -i co-authored` prints nothing.
Branch: `<yourname>/<task>` → pull request into `main`. Run `python -m pytest -q` before every push.

## 1. Agent spike: explain a gap in plain language (by 13 Nov, 9:00 PM)
Today `ledger.investigate()` returns fixed English sentences. The agent's job is to turn those facts into a
short, polite explanation each side can understand, in Hindi or Kannada, and suggest the next step.
- New file: `agent.py`. Input: the output of `reconcile()` and `investigate()` as JSON. Output: text.
- [ ] Check our Lyzr AI credits (the event's AI partner) and build the agent there if it fits; any LLM API
      read from environment variables is fine for the spike. Never commit a key.
- [ ] The agent may only restate numbers it was given. Add a test that fails if its text contains a weight
      that isn't in the input (it must never compute a balance).
- [ ] It never says who is at fault. Add a test for that too (no "you stole", "your fault", etc.).
- [ ] If the API isn't set or fails, fall back to the plain sentences from `investigate()`.
- Done when: the jeweller and karigar phones show the agent's explanation under "What the records show",
  and the tests pass with and without a key.

## 2. Architecture note (by 14 Nov)
- New file: `docs/ARCHITECTURE.md`, one page, for the form's architecture question:
- [ ] Offline-first: how a phone saves entries without network and syncs later without breaking the seal
      (each phone keeps its own entries; the server orders them; conflicts become entries both confirm).
- [ ] Where the agent sits, what tools it may call, and what it may never do (move money, close a dispute).
- [ ] Assisted path: how a JanAI Café operator helps a karigar with no smartphone, with his own voice confirmation.
