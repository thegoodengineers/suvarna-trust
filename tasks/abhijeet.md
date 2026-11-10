# Abhijeet: the agent that explains gaps, and the architecture

## Rule for everyone: never name the tools we used to build this
Do not name any assistant, chatbot or code tool used to build this project anywhere: commits, co-author lines,
code comments, README, docs, the form, the deck, screenshots or videos. No `Co-Authored-By` lines for tools.
Describing the product's own agent is fine. Before you push: `git log --format=%B | grep -i co-authored` prints nothing.
Branch: `<yourname>/<task>` → pull request into `main`. Run `python -m pytest -q` before every push.

## 1. Agent (`agent.py`)
Built: explanations in English, Hindi and Kannada with one next step, checked so a model can never add a number
or blame anyone; an OpenAI-compatible model or a **Lyzr agent** (Lyzr's Agent API) when configured, templates otherwise.
What needs you (a real account and a real person):
- [ ] Sign in to Lyzr Studio with our event credits, create an agent, and switch it on as described in
      `docs/ARCHITECTURE.md` ("Switching on Lyzr"). Never commit the key.
- [ ] Try it on all four demo states (gap, re-weighed, paid, broken seal) and J-1043 in all three languages.
      Paste one good and one rejected answer into a pull request.
- [ ] Get Bhumika's Kannada checker to read the `kn` templates in `SAY`, the same way as the karigar phone.
- Standing rule: if `ledger.investigate()` gains a new sentence, add its shape to `SHAPES` and a line in each
  language; `test_every_ledger_finding_is_translated` fails until you do. The agent explains and suggests; it never
  computes a balance, moves money, approves, or closes a dispute.

## 2. Architecture note
- [x] `docs/ARCHITECTURE.md`: offline-first sync, where the agent sits and what it may never do, assisted path,
      and how to switch on Lyzr.
