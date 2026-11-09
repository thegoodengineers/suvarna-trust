"""SUVARNA TRUST agent: turns the ledger's reconcile() and investigate() output into a short, polite
explanation in English, Hindi or Kannada, plus one suggested next step.

It explains; it never computes. Every weight it says is copied from its input, it never says who is at
fault, and it cannot move money or close a dispute (it has no access to the ledger's write methods).

A language model is used only when SUVARNA_LLM_API_KEY and SUVARNA_LLM_MODEL are set (any OpenAI-compatible
chat endpoint, SUVARNA_LLM_URL). Its answer is checked against the same rules as the templates; if it
states a number that is not in the input, uses blaming words, or the call fails, the templates are used.
"""
import functools
import json
import os
import re
import urllib.request

from ledger import grams

LANGS = ("en", "hi", "kn")
# Words the agent must never use: it explains records, it does not accuse anyone.
BLAME = re.compile(r"fault|stol|steal|theft|thief|cheat|blame|guilty|liar|\blie[sd]?\b|dishonest|fraud|"
                   r"चोर|चुरा|गलती|ग़लती|दोष|धोखा|बेईमान|ಕಳ್ಳ|ಕದ್ದ|ಕಳವು|ತಪ್ಪು|ಮೋಸ|ದೋಷ", re.I)

W = r"(-?\d+\.\d{3} g)"  # a weight as ledger.grams() writes it
KIND = {"en": {"issue": "issue", "return": "returned piece", "scrap": "scrap", "wastage": "wastage"},
        "hi": {"issue": "दिया गया सोना", "return": "वापस किया गहना", "scrap": "स्क्रैप", "wastage": "तय घटत"},
        "kn": {"issue": "ಕೊಟ್ಟ ಚಿನ್ನ", "return": "ವಾಪಸ್ ಕೊಟ್ಟ ಆಭರಣ", "scrap": "ಸ್ಕ್ರ್ಯಾಪ್", "wastage": "ಒಪ್ಪಿದ ಸವಕಳಿ"}}
WHO = {"en": {"jeweller": "the jeweller", "karigar": "the karigar"},
       "hi": {"jeweller": "ज्वैलर", "karigar": "कारीगर"},
       "kn": {"jeweller": "ಜ್ಯುವೆಲ್ಲರ್", "karigar": "ಕಾರಿಗರ್"}}

# The five sentence shapes ledger.investigate() writes, and how each reads in each language.
SHAPES = [
    ("pending", re.compile(rf"The (\w+) of {W} recorded by the (\w+) is not yet confirmed by the (\w+), so it is not counted\.")),
    ("photo", re.compile(rf"The (\w+) of {W} has no scale photo\.")),
    ("corrected", re.compile(rf"The (\w+) was corrected from {W} to {W} by the (\w+)\.")),
    ("unaccounted", re.compile(rf"{W} is unaccounted for and every record is confirmed with evidence\.")),
    ("extra", re.compile(rf"More gold came back than was issued \({W} extra\)\.")),
]
SAY = {
    "en": {
        "pending": lambda k, w, by, o: f"The {k} of {w} recorded by {by} is waiting for {o} to confirm it, so it is not counted yet.",
        "photo": lambda k, w: f"The {k} of {w} has no scale photo yet.",
        "corrected": lambda k, old, new, by: f"The {k} was re-weighed: {by} recorded {new} in place of {old}. The old entry stays visible.",
        "unaccounted": lambda w: f"Every record is confirmed with evidence, but {w} is still not accounted for.",
        "extra": lambda w: f"More gold came back than the records show as issued ({w} extra).",
        "zero": "Every gram is accounted for.", "gap": lambda w: f"{w} of gold is not explained yet.",
        "uneven": "The records do not balance yet.",
        "sealed": "An old entry was changed after it was recorded, so these numbers cannot be relied on until it is restored.",
        "next": {"pending": lambda o: f"Next: {o} checks the waiting entry and confirms it if it is right.",
                 "photo": lambda k: f"Next: re-weigh the {k} together and record it with a scale photo.",
                 "unaccounted": "Next: re-weigh the returned pieces and the scrap together.",
                 "extra": "Next: check together whether an issue of gold is missing from the records.",
                 "sealed": "Next: compare with the copy on both phones. No payment until the history matches its seal.",
                 "done": "Next: both of you can look at the settlement and approve it."}},
    "hi": {
        "pending": lambda k, w, by, o: f"{by} ने {k} {w} दर्ज किया है; {o} की पुष्टि बाकी है, इसलिए यह अभी गिना नहीं गया।",
        "photo": lambda k, w: f"{k} {w} के साथ अभी तराज़ू की फ़ोटो नहीं है।",
        "corrected": lambda k, old, new, by: f"{k} फिर से तौला गया: {by} ने {old} की जगह {new} दर्ज किया। पुरानी एंट्री भी दिखती रहेगी।",
        "unaccounted": lambda w: f"हर रिकॉर्ड पुष्टि और सबूत के साथ है, फिर भी {w} का हिसाब नहीं मिला।",
        "extra": lambda w: f"रिकॉर्ड में जितना सोना दिया गया, उससे ज़्यादा वापस आया ({w} ज़्यादा)।",
        "zero": "पूरा हिसाब मिल गया, हर ग्राम का।", "gap": lambda w: f"{w} सोने का हिसाब अभी नहीं मिला।",
        "uneven": "हिसाब अभी बराबर नहीं है।",
        "sealed": "एक पुरानी एंट्री दर्ज होने के बाद बदली गई है, इसलिए जब तक वह ठीक न हो, इन आंकड़ों पर भरोसा नहीं किया जा सकता।",
        "next": {"pending": lambda o: f"अगला कदम: {o} बाकी एंट्री देखें और सही हो तो पुष्टि करें।",
                 "photo": lambda k: f"अगला कदम: {k} साथ बैठकर फिर से तौलें और तराज़ू की फ़ोटो के साथ दर्ज करें।",
                 "unaccounted": "अगला कदम: लौटे गहने और स्क्रैप साथ बैठकर फिर से तौलें।",
                 "extra": "अगला कदम: साथ में देखें कि कोई 'दिया गया सोना' रिकॉर्ड छूटा तो नहीं।",
                 "sealed": "अगला कदम: दोनों फ़ोन की कॉपी से मिलाएं। जब तक रिकॉर्ड मुहर से मेल न खाए, भुगतान नहीं होगा।",
                 "done": "अगला कदम: दोनों भुगतान का हिसाब देखकर मंज़ूरी दें।"}},
    "kn": {
        "pending": lambda k, w, by, o: f"{by} ದಾಖಲಿಸಿದ {k} {w} ಅನ್ನು {o} ಇನ್ನೂ ದೃಢೀಕರಿಸಿಲ್ಲ, ಹಾಗಾಗಿ ಅದನ್ನು ಇನ್ನೂ ಲೆಕ್ಕಕ್ಕೆ ತೆಗೆದುಕೊಂಡಿಲ್ಲ.",
        "photo": lambda k, w: f"{k} {w} ಗೆ ಇನ್ನೂ ತಕ್ಕಡಿಯ ಫೋಟೋ ಇಲ್ಲ.",
        "corrected": lambda k, old, new, by: f"{k} ಮತ್ತೆ ತೂಕ ಮಾಡಲಾಗಿದೆ: {by} {old} ಬದಲು {new} ದಾಖಲಿಸಿದ್ದಾರೆ. ಹಳೆಯ ದಾಖಲೆಯೂ ಕಾಣುತ್ತಲೇ ಇರುತ್ತದೆ.",
        "unaccounted": lambda w: f"ಎಲ್ಲಾ ದಾಖಲೆಗಳು ದೃಢೀಕರಣ ಮತ್ತು ಸಾಕ್ಷಿ ಸಹಿತ ಇವೆ, ಆದರೂ {w} ಇನ್ನೂ ಲೆಕ್ಕಕ್ಕೆ ಸಿಕ್ಕಿಲ್ಲ.",
        "extra": lambda w: f"ದಾಖಲೆಯಲ್ಲಿ ಕೊಟ್ಟದ್ದಕ್ಕಿಂತ ಹೆಚ್ಚು ಚಿನ್ನ ವಾಪಸ್ ಬಂದಿದೆ ({w} ಹೆಚ್ಚು).",
        "zero": "ಪ್ರತಿ ಗ್ರಾಂ ಚಿನ್ನದ ಲೆಕ್ಕ ಸರಿಯಾಗಿದೆ.", "gap": lambda w: f"{w} ಚಿನ್ನ ಇನ್ನೂ ಲೆಕ್ಕಕ್ಕೆ ಸಿಕ್ಕಿಲ್ಲ.",
        "uneven": "ಲೆಕ್ಕ ಇನ್ನೂ ಸರಿಹೊಂದಿಲ್ಲ.",
        "sealed": "ಹಳೆಯ ದಾಖಲೆಯೊಂದು ದಾಖಲಿಸಿದ ನಂತರ ಬದಲಾಗಿದೆ, ಅದನ್ನು ಸರಿಪಡಿಸುವವರೆಗೆ ಈ ಸಂಖ್ಯೆಗಳನ್ನು ನಂಬಲು ಆಗುವುದಿಲ್ಲ.",
        "next": {"pending": lambda o: f"ಮುಂದಿನ ಹೆಜ್ಜೆ: {o} ಬಾಕಿ ಇರುವ ದಾಖಲೆಯನ್ನು ನೋಡಿ, ಸರಿ ಇದ್ದರೆ ದೃಢೀಕರಿಸಲಿ.",
                 "photo": lambda k: f"ಮುಂದಿನ ಹೆಜ್ಜೆ: {k} ಅನ್ನು ಇಬ್ಬರೂ ಸೇರಿ ಮತ್ತೆ ತೂಕ ಮಾಡಿ, ತಕ್ಕಡಿಯ ಫೋಟೋ ಸಹಿತ ದಾಖಲಿಸಿ.",
                 "unaccounted": "ಮುಂದಿನ ಹೆಜ್ಜೆ: ವಾಪಸ್ ಬಂದ ಆಭರಣ ಮತ್ತು ಸ್ಕ್ರ್ಯಾಪ್ ಅನ್ನು ಇಬ್ಬರೂ ಸೇರಿ ಮತ್ತೆ ತೂಕ ಮಾಡಿ.",
                 "extra": "ಮುಂದಿನ ಹೆಜ್ಜೆ: ಯಾವುದಾದರೂ 'ಕೊಟ್ಟ ಚಿನ್ನ' ದಾಖಲೆ ಬಿಟ್ಟುಹೋಗಿದೆಯೇ ಎಂದು ಒಟ್ಟಿಗೆ ನೋಡಿ.",
                 "sealed": "ಮುಂದಿನ ಹೆಜ್ಜೆ: ಎರಡೂ ಫೋನ್‌ಗಳಲ್ಲಿರುವ ಪ್ರತಿಯೊಂದಿಗೆ ಹೋಲಿಸಿ. ದಾಖಲೆ ಮುದ್ರೆಗೆ ಹೊಂದುವವರೆಗೆ ಪಾವತಿ ಇಲ್ಲ.",
                 "done": "ಮುಂದಿನ ಹೆಜ್ಜೆ: ಇಬ್ಬರೂ ಪಾವತಿ ವಿವರ ನೋಡಿ ಒಪ್ಪಿಗೆ ನೀಡಿ."}},
}
NEXT_ORDER = ("pending", "photo", "unaccounted", "extra")  # the first open question is the one to settle first


def template(reconcile, findings, lang="en", chain_ok=True):
    """Deterministic explanation. Restates the ledger's facts; computes nothing."""
    say, kind, who = SAY[lang], KIND[lang], WHO[lang]
    gap = reconcile["unexplained"]
    if not chain_ok:
        summary = say["sealed"]
    else:
        summary = say["zero"] if gap == 0 else say["gap"](grams(gap)) if gap > 0 else say["uneven"]
    points, seen = [], {}
    for f in findings:
        for name, rx in SHAPES:
            m = rx.match(f)
            if m:
                g = m.groups()
                if name == "pending":
                    points.append(say[name](kind[g[0]], g[1], who[g[2]], who[g[3]]))
                    seen.setdefault(name, who[g[3]])
                elif name == "photo":
                    points.append(say[name](kind[g[0]], g[1]))
                    seen.setdefault(name, kind[g[0]])
                elif name == "corrected":
                    points.append(say[name](kind[g[0]], g[1], g[2], who[g[3]]))
                else:
                    points.append(say[name](g[0]))
                    seen.setdefault(name, None)
                break
        else:
            points.append(f)  # a sentence shape this file does not know yet: show the ledger's own words
    nxt = say["next"]
    if not chain_ok:
        step = nxt["sealed"]
    else:
        open_ = [n for n in NEXT_ORDER if n in seen]
        step = (nxt[open_[0]](seen[open_[0]]) if open_ and open_[0] in ("pending", "photo")
                else nxt[open_[0]] if open_ else nxt["done"])
    return {"summary": summary, "points": points, "next": step, "source": "template"}


def numbers(text):
    """Every number in a text, with Devanagari and Kannada digits read as ASCII."""
    text = text.translate(str.maketrans("०१२३४५६७८९೦೧೨೩೪೫೬೭೮೯", "01234567890123456789"))
    return set(re.findall(r"\d+(?:[.,]\d+)?", text))


def allowed_numbers(reconcile, findings):
    """The numbers the agent may say: those in its input, and weights in the ledger's own grams() form."""
    mgs = [v for v in reconcile.values() if isinstance(v, int)] + [e["mg"] for e in reconcile.get("pending", [])]
    return numbers(json.dumps(reconcile, default=str) + " ".join(findings) + " ".join(grams(v) for v in mgs))


def safe(answer, reconcile, findings):
    text = " ".join([answer["summary"], *answer["points"], answer["next"]])
    return not BLAME.search(text) and numbers(text) <= allowed_numbers(reconcile, findings)


PROMPT = ("You help a jeweller and a karigar (goldsmith) understand their shared gold record. Rewrite the draft "
          "explanation so it is short, warm and polite, in the language code given ({lang}). Rules: copy every "
          "weight exactly as written in the draft, never add, round or calculate a number; never say or hint that "
          "anyone is at fault; keep the next step. Answer only with JSON: {{\"text\": \"...\", \"next\": \"...\"}}")


def _ask_llm(facts, lang):
    url = os.environ.get("SUVARNA_LLM_URL", "https://api.openai.com/v1/chat/completions")
    body = {"model": os.environ["SUVARNA_LLM_MODEL"], "temperature": 0,
            "messages": [{"role": "system", "content": PROMPT.format(lang=lang)}, {"role": "user", "content": facts}]}
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json",
                                                                    "Authorization": "Bearer " + os.environ["SUVARNA_LLM_API_KEY"]})
    with urllib.request.urlopen(req, timeout=8) as r:
        content = json.load(r)["choices"][0]["message"]["content"]
    reply = json.loads(content.strip().removeprefix("```json").removesuffix("```"))
    return {"summary": str(reply["text"]), "points": [], "next": str(reply["next"]), "source": "llm"}


@functools.lru_cache(maxsize=256)
def _llm(facts, lang):
    """One call per distinct situation and language; a failure is remembered too, so a dead API costs one timeout."""
    try:
        return _ask_llm(facts, lang)
    except Exception:  # any API, network or format problem: the templates answer instead
        return None


def explain(reconcile, findings, lang="en", chain_ok=True):
    """The explanation one phone shows under "What the records show"."""
    if lang not in LANGS:
        raise ValueError(f"unknown language {lang!r}")
    draft = template(reconcile, findings, lang, chain_ok)
    if os.environ.get("SUVARNA_LLM_API_KEY") and os.environ.get("SUVARNA_LLM_MODEL"):
        facts = json.dumps({"draft": draft, "findings": findings, "chain_ok": chain_ok}, ensure_ascii=False, sort_keys=True)
        answer = _llm(facts, lang)
        if answer and safe(answer, reconcile, findings):
            return answer
    return draft
