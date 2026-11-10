# Chirag: registration, ledger core, final form, submit

## Rule for everyone: never name the tools we used to build this
Do not name any assistant, chatbot or code tool used to build this project anywhere: commits, co-author lines,
code comments, README, docs, the form, the deck, screenshots or videos. No `Co-Authored-By` lines for tools.
Describing the product's own agent is fine. Before you push: `git log --format=%B | grep -i co-authored` prints nothing.
Branch: `<yourname>/<task>` → pull request into `main`. Run `python -m pytest -q` before every push.

## 1. Registration (by 10 Nov, 11:59 PM) - most urgent
- [ ] HackCulture team page shows all four of us and problem statement 2.2.
- [ ] Note the idea-form fields and any character limits in `docs/FORM_ANSWERS.md`.
- [ ] Read the IP terms on HackCulture before accepting (they differ from the GAVS site).

## 2. Keep the ledger core right (ongoing)
- Files: `ledger.py`, `test_ledger.py`. Every new rule gets a test first. Review every pull request that touches them.
- [x] Second demo order J-1043 (wedding bangles, due in 2 days) with deadline warnings and tests.

## 3. Final form (by 14 Nov, 9:00 PM)
- [ ] Put the interview numbers and one quote from each side into `docs/FORM_ANSWERS.md`
      ("The problem" and "Business model"). Only what people actually said.
- [ ] Remove anything we can't back up. No "first in India".
- [ ] One person reads it aloud start to finish; cut anything that sounds like filler.

## 4. Submit (14 Nov night, a day early)
- [ ] Paste each section into the HackCulture form and add the repo link. Add the deck only if Ayush has filled
      its interview boxes.
- [ ] Screenshot the confirmation into the team chat.
