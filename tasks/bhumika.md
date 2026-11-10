# Bhumika: Kannada on the karigar phone, interviews, UI polish

## Rule for everyone: never name the tools we used to build this
Do not name any assistant, chatbot or code tool used to build this project anywhere: commits, co-author lines,
code comments, README, docs, the form, the deck, screenshots or videos. No `Co-Authored-By` lines for tools.
Describing the product's own agent is fine. Before you push: `git log --format=%B | grep -i co-authored` prints nothing.
Branch: `<yourname>/<task>` → pull request into `main`. Run `python -m pytest -q` before every push.

## 1. Kannada on the karigar phone
- [x] ಕನ್ನಡ button with every karigar label, the read-aloud sentence and grams wording (`kn-IN`), and a message on
      screen when the phone has no Kannada voice.
- [ ] Get a native Kannada speaker to check every line: the karigar phone (`web/index.html`), the agent's `kn`
      templates (`agent.py`, `SAY`), and the Kannada lines in `docs/INTERVIEW_KIT.md`. Write who checked it in the
      pull request (first name only).
- [ ] Test "ಓದಿ ಹೇಳಿ" (read it to me) in Chrome on a real phone and note whether it has a Kannada voice.

## 2. One interview with Ayush (by 12 Nov)
- [ ] Use `docs/INTERVIEW_KIT.md`. Show the demo in the last 5 minutes and write down what confused them.

## 3. Polish from what people said (by 14 Nov)
- [ ] Fix the top 2 things the interviews say are confusing on the karigar phone.
- [ ] Check tap targets and number size on the cheapest phone in the team.
