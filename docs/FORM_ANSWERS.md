# Tech4Bharat idea form: paste-ready answers

Plain text (the form doesn't render markdown). Built from docs/IDEA_SUBMISSION.md, with no invented field
data. If we have interview findings by then, add one line to "The problem" before saving.

## Theme
Theme 2: Jeweltech (problem statement 2.2, gold given to karigars for job-work)

## Project Title
SUVARNA TRUST: every gram accounted for, every karigar paid on time

## Brief about your idea
Small jewellers hand gold to karigars by weight and track it in notebooks. Wastage is agreed verbally, deadlines are chased by phone and accounts are settled at month end, so gold goes missing, disputes sour long relationships and artisans wait weeks to be paid. SUVARNA TRUST is a voice-first AI agent that both sides trust. It records every gram issued and returned with evidence, tracks each order against its occasion date, reconciles wastage to the milligram, investigates any gap without assigning blame, and pays the karigar only after both approve. Every completed job builds the karigar a verified work record he controls.

## Detailed explanation of the idea
THE PROBLEM
Jewellers issue gold to artisan goldsmiths (karigars) by weight and receive finished pieces with agreed wastage. Issue, return, wastage, deadlines and payment across many karigars and custom orders are tracked by hand. The result: unexplained gold losses, disputes, missed wedding dates and late payment to artisans. The karigar has the least power in any dispute and no record of his own that others accept.

OUR SOLUTION: one shared case per order, run by an agent
1. Issue: the jeweller speaks or types the weight while weighing; the agent reads the scale photo, checks it matches, and creates the job card (design, weight, purity, agreed wastage, due date). The karigar confirms receipt by voice or tap.
2. Track: the agent follows the order against the customer's occasion date, asks the karigar for progress by voice, and warns the jeweller early if the date is at risk.
3. Return: finished weight and recovered scrap are recorded with evidence; both confirm.
4. Reconcile: tested code, not AI, computes in whole milligrams: issued minus returned minus scrap minus agreed wastage = unexplained.
5. Investigate: if anything is unexplained, the agent gathers the evidence trail, points to the missing or inconsistent record and explains the gap to both in plain language. It never decides who is at fault.
6. Settle: the agent drafts the settlement (gold balance, labour due, each deduction explained), reads it out to each side, and pays the karigar through a clearly labelled mock UPI step only after BOTH approve.
7. Record: the verified job is added to the karigar's Trust Passport, which he controls.
Example (illustrative): 100.000 g issued; 96.000 g jewellery and 2.500 g scrap returned; 1.000 g agreed wastage; 0.500 g unexplained. Settlement is held, the agent shows the return-weighing photo is missing, both re-weigh and confirm, and settlement goes through.

WHY IT IS AGENTIC AI
It pursues one goal over many steps and weeks, acts (voice confirmations, reminders, job cards, settlements, mock payment), keeps memory of every case, recovers when something fails (a missing photo or silent karigar becomes a follow-up task, never a guess), and asks for human approval before anything involving money, disputes or personal data. The AI never computes a gold balance or decides a dispute.

ARCHITECTURE
Jeweller app and karigar app (light Android-friendly web app, offline-first) sync to an append-only ledger: each entry is hash-linked to the previous one and confirmed from the other party's phone, so neither side can quietly change history; corrections are new entries both confirm. Around it: a deterministic reconciliation service with tests, an agent layer (LLM with tools: read case, fetch evidence, draft settlement, request approval, send voice note), Indian-language speech-to-text and text-to-speech, an evidence store, and a mock UPI module.

BUILT FOR THE PEOPLE IN THE STATEMENT
Voice-first in Kannada and Hindi ("Maine 95 gram ka kaam complete kar diya"), numbers always read back before saving; icons and voice instead of forms for low literacy; works offline on entry-level Android; a JanAI Cafe assisted path for karigars without a smartphone; minimal data, consent first; every mock integration labelled.

WHAT MAKES IT DIFFERENT
Shop software keeps the jeweller's books. Ours keeps one shared record both sides confirm, with the weaker party given equal visibility. Disputes are investigated with evidence, not argued. The record becomes an asset for the artisan, not just an audit log for the shop.

BUSINESS MODEL AND SCALE
Jewellers pay a monthly subscription per shop; karigars use it free. Later, with the karigar's consent, his verified record helps lenders and new jewellers trust him (referral fee). JanAI Cafe operators earn per assisted transaction. We grow market by market: jewellers in one market share the same karigars, so each new jeweller makes the network more useful.

JOBS AND LIVELIHOODS
Karigars are paid faster and lose fewer disputes; a verified work record helps skilled karigars win work from new jewellers and credit for tools; assisted operators get a paid local role.

PROTOTYPE PLAN
One complete flow, built well: jeweller and karigar logins, issue with evidence, voice confirmation in two languages, order tracking, milligram reconciliation, dispute investigation, two-party settlement with mock UPI, and the Trust Passport. We will measure, not claim: discrepancies caught, time to settle, and settlements made without both approvals (target zero).

## Presentation Deck (optional)
Skip unless we have a deck ready; an empty optional field costs nothing, a weak deck does.

## Additional supporting links
https://github.com/thegoodengineers/suvarna-trust
