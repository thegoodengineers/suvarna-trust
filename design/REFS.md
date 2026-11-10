# Design references (researched before any UI, 9 Nov)

| Site | What we took | Where we use it |
|---|---|---|
| recent.design (via godly.website) | One big number in a dark pill ("17" card): a single figure as the hero | Every weight is a scale-style readout, the largest thing on screen |
| landdding.com, Kuda card | Plain, bold money headline over quiet UI | Settlement card: amount first, explanation under it |
| posts.design, launch posts (10 Nov, for the deck) | One object on a dark field, one line of type, lots of empty space (`refs/posts.jpg`) | Deck: each slide has one hero (a readout or a screenshot) on velvet |
| godly.website | Redirects to recent.design now; same takeaway as above | Deck and app |
| mobbin.com | Blocked to automated browsers (403); check real UPI app flows by hand in the prototype round | Approve-and-pay step |

## Vibe
- Place/object: a jeweller's velvet tray beside a digital weighing scale.
- First 3 seconds: "nothing here can be quietly changed".
- Two influences: the bahi-khata account book (ruled, numbered, signed) and a scale's segment readout.
- Never mistaken for: a crypto wallet, a generic SaaS dashboard.

Palette: velvet #123129, velvet deep #0B211C, scale readout #E9F5B8 on #1B2420, gold #C8A24A (only for
confirmed entries), paper #FFFFFF, ink #16201D, warning #B5502E.
Type: Hanken Grotesk (UI), Martian Mono (weights only), Noto Sans Devanagari (Hindi).

Deck (`docs/deck/deck.html` → `SUVARNA_TRUST.pdf` via `docs/deck/build.py`): same palette and type as the app; gold
dashed boxes mark lines the team fills after interviews, so no placeholder can pass as data.
