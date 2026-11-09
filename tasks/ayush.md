# Ayush: lead the interviews, deck, screenshots

## Rule for everyone: never name the tools we used to build this
Do not name any assistant, chatbot or code tool used to build this project anywhere: commits, co-author lines,
code comments, README, docs, the form, the deck, screenshots or videos. No `Co-Authored-By` lines for tools.
Describing the product's own agent is fine. Before you push: `git log --format=%B | grep -i co-authored` prints nothing.
Branch: `<yourname>/<task>` → pull request into `main`. Run `python -m pytest -q` before every push.

## 1. Lead the field interviews (by 12 Nov, 9:00 PM) - most important task in the team
- Guide: `docs/FIELD.md`. Goal: at least 3 jewellers and 3 karigars.
- [ ] Find the shops: family contacts first, then a local jewellery market. Go in pairs.
- [ ] Ask consent first. No real names, shop names or customer details unless they say yes.
- [ ] Show the demo on a phone in the last 5 minutes (setup in `CONTRIBUTING.md`).
- [ ] Fill one row per interview in `docs/FIELD.md` the same day, numbers exactly as said.
- [ ] 12 Nov night: fill "What we learned" and send the 3 best quotes and numbers to Chirag.

## 2. Deck, optional field on the form (by 14 Nov, 9:00 PM)
- Put it in `docs/deck/`. 6 slides max, PDF:
  1. Problem in one sentence + one real quote. 2. What we heard (interview numbers).
  3. The demo story in 4 screenshots. 4. Why both sides trust it (seal, two approvals, milligrams).
  5. Business model and jobs. 6. Team and the prototype plan.
- [ ] Every number from the brochure, `docs/FIELD.md`, or labelled "illustrative".
- If it isn't good by 14 Nov, we skip it: an empty optional field beats a weak deck.

## 3. Screenshots (by 13 Nov)
- [ ] Desktop: the 0.500 g gap; after the re-weigh (0.000 g); paid; the broken seal after "quietly edit".
- [ ] Phone width: the karigar phone in Hindi (and Kannada once Bhumika's change is in).
- Save as `docs/screenshots/01-gap.png` and so on.
