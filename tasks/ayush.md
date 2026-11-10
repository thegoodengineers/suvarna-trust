# Ayush: lead the interviews, deck, screenshots

## Rule for everyone: never name the tools we used to build this
Do not name any assistant, chatbot or code tool used to build this project anywhere: commits, co-author lines,
code comments, README, docs, the form, the deck, screenshots or videos. No `Co-Authored-By` lines for tools.
Describing the product's own agent is fine. Before you push: `git log --format=%B | grep -i co-authored` prints nothing.
Branch: `<yourname>/<task>` → pull request into `main`. Run `python -m pytest -q` before every push.

## 1. Lead the field interviews (by 12 Nov, 9:00 PM) - most important task in the team
- Kit to print and send: `docs/INTERVIEW_KIT.md` (one-page script in English, Hindi and Kannada, consent line,
  WhatsApp message for jeweller contacts, short form for karigars who can't meet). Full guide: `docs/FIELD.md`.
- [ ] Send the WhatsApp message to family and market contacts today. Goal: at least 3 jewellers and 3 karigars.
- [ ] Go in pairs. Consent first. No real names, shop names or customer details unless they say yes.
- [ ] Show the demo on a phone in the last 5 minutes (setup in `CONTRIBUTING.md`).
- [ ] Fill one row per interview in `docs/FIELD.md` the same day, numbers exactly as said.
- [ ] 12 Nov night: fill "What we learned" and send the 3 best quotes and numbers to Chirag.

## 2. Deck (by 14 Nov, 9:00 PM)
- [x] Six slides built in the app's style: `docs/deck/SUVARNA_TRUST.pdf` (source `docs/deck/deck.html`).
- [ ] After the interviews, fill the gold dashed "TO FILL AFTER INTERVIEWS" boxes on slides 1, 2 and 5 in
      `deck.html` with what people actually said, then `python docs/deck/build.py` and look at `slide-*.png`.
      If there are no interview numbers by 14 Nov, we don't upload the deck: placeholder boxes must never be submitted.

## 3. Screenshots
- [x] Desktop and phone screenshots in `docs/screenshots/` (gap, re-weigh, paid, broken seal, agent, late order,
      karigar phone in Hindi and Kannada). `python docs/screenshots/take.py` retakes them if the demo changes.
