# Bhumika: Kannada on the karigar phone, interviews, UI polish

## Rule for everyone: never name the tools we used to build this
Do not name any assistant, chatbot or code tool used to build this project anywhere: commits, co-author lines,
code comments, README, docs, the form, the deck, screenshots or videos. No `Co-Authored-By` lines for tools.
Describing the product's own agent is fine. Before you push: `git log --format=%B | grep -i co-authored` prints nothing.
Branch: `<yourname>/<task>` → pull request into `main`. Run `python -m pytest -q` before every push.

## 1. Kannada on the karigar phone (by 12 Nov, 9:00 PM)
The event is in Karnataka and the organisers ask for vernacular, voice-first apps. Today the karigar phone
has Hindi and English only.
- Files: `web/index.html` (the `T` and `KIND_HI` tables, the language buttons, `hiG`).
- [ ] Add a third language button ಕನ್ನಡ with every karigar label, the read-aloud sentence and the
      grams/milligrams wording (speech language `kn-IN`).
- [ ] Get a native Kannada speaker to check every line. Write who checked it in your pull request (first name only).
- [ ] Test "Read it to me" in Chrome on a phone. If the phone has no Kannada voice, say so on screen.
- Done when: switching to ಕನ್ನಡ changes every karigar label, and the page still has 0 accessibility problems.

## 2. One interview with Ayush (by 12 Nov)
- [ ] Use `docs/FIELD.md`. Show the demo in the last 5 minutes and write down what confused them.

## 3. Polish from what people said (by 14 Nov)
- [ ] Fix the top 2 things the interviews say are confusing on the karigar phone.
- [ ] Bigger tap targets and numbers for older eyes; check it on the cheapest phone in the team.
