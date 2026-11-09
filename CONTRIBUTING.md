# Working on SUVARNA TRUST

Tech4Bharat 2026, problem statement 2.2. Team: The Good Engineers.

## Dates (IST)
| By | What |
|---|---|
| 10 Nov, 11:59 PM | Registration closes: all four of us on the team page on HackCulture |
| 12 Nov, 9:00 PM | Field interviews done: at least 3 jewellers and 3 karigars, notes in `docs/FIELD.md` |
| 14 Nov, 9:00 PM | Form answers updated with what we learned; deck ready (optional) |
| 15 Nov, 11:59 PM | Idea submission closes. We submit on 14 Nov night |
| 23 Nov | Shortlist. If we're in: prototype round until 15 Dec, finale 27 Dec in Bengaluru |

## Setup (once)
```
git clone https://github.com/thegoodengineers/suvarna-trust.git
cd suvarna-trust
python -m pip install -r requirements.txt
python -m pytest -q                          # must pass before you start
python -m uvicorn server:app --port 8770     # demo at http://localhost:8770
```
To show the demo on your phone at an interview: run the server on a laptop with
`--host 0.0.0.0`, connect the phone to the same Wi-Fi, and open `http://<laptop-ip>:8770`.

## Rules
- **Never name any tool, assistant or chatbot used to build this project**: not in commits, co-author lines,
  comments, docs, the form, the deck, screenshots or videos. Before you push,
  `git log --format=%B | grep -i co-authored` must print nothing.
- Describing the product's own agent (what it does for the jeweller and karigar) is fine and expected.
- Branch per task: `yourname/short-task`, pull request into `main`. Run `python -m pytest -q` first.
- **Gold maths stays in `ledger.py`, in whole milligrams, with a test for every rule.** Nothing else
  computes a balance. The agent explains and coordinates; it never decides a balance or a dispute.
- **No invented numbers.** Every number in the form or deck comes from the organisers' brochure, our
  interviews (`docs/FIELD.md`), or is labelled "illustrative".
- **Interview consent first.** No real names, shop names, customer details or gold stock photos without a yes.

## Who owns what
| Part | Files | Owner |
|---|---|---|
| Ledger core, reviews, submission | `ledger.py`, `test_ledger.py`, `docs/FORM_ANSWERS.md` | Chirag |
| Karigar phone, Kannada, design | `web/index.html` | Bhumika |
| Interviews lead, deck, screenshots | `docs/FIELD.md`, `docs/deck/` | Ayush |
| Agent layer and sync plan | `agent.py` (new), `docs/ARCHITECTURE.md` (new) | Abhijeet |

## Your tasks: one file each
| Who | File | Main job this week |
|---|---|---|
| Chirag | [`tasks/chirag.md`](tasks/chirag.md) | Registration, ledger, final form, submit |
| Bhumika | [`tasks/bhumika.md`](tasks/bhumika.md) | Kannada on the karigar phone, interviews, UI polish |
| Ayush | [`tasks/ayush.md`](tasks/ayush.md) | Lead the interviews, deck, screenshots |
| Abhijeet | [`tasks/abhijeet.md`](tasks/abhijeet.md) | Agent that explains gaps in plain language; architecture |

**Everyone** does at least one interview (in pairs: one asks, one writes). That evidence is the
single biggest thing missing from our submission.

## How we win (the organisers' two judging dimensions)
| Dimension | What wins it | Who |
|---|---|---|
| Problem relevance | Real interview numbers and quotes, not assumptions | Everyone, led by Ayush |
| Quality of AI / agentic | An agent that investigates and explains, asks both for approval, never decides money | Abhijeet |
| Working prototype | The demo already runs end to end; keep it green and add Kannada | Chirag, Bhumika |
| Built for the users | Voice, Kannada and Hindi, works on a cheap phone, assisted path | Bhumika |
| Business model, scale, jobs | Price from what jewellers said; karigar record as an asset | Ayush, Chirag |
