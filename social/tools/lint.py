"""Mechanical lint for social posts: catches AI-sounding patterns and rule violations
BEFORE a human or the reviewer agent reads the post.

Run from repo root:   python social/tools/lint.py 2026-W48
Exit code: 0 = no errors (warnings allowed), 1 = at least one ERROR, 2 = bad usage.

ERROR = hard rule from brand-voice.md / facts.md (must fix).
WARN  = common AI tell or weak writing (fix unless there is a reason).
The reviewer agent (social/reviewer.md) handles what a script cannot judge.
"""
import json
import re
import sys
from collections import Counter

DIVIDER = "—————"
FLAG = "🇺🇸"

# Phrases that read as generic marketing / machine copy.
STOCK_ES = [
    "sueña con", "día perfecto", "día soñado", "boda de ensueño", "momento mágico", "momentos mágicos",
    "el día más especial", "el día más importante de tu vida", "hacer realidad", "en el mundo de",
    "no solo", "no es solo", "más que una", "inolvidable", "convierte tu", "descubre cómo",
    "sumérgete", "desbloquea", "eleva tu", "te mereces",
]
STOCK_EN = [
    "dream wedding", "dream day", "perfect day", "magical", "unforgettable", "make your dream",
    "special day", "not just", "more than just", "whether you're", "look no further",
    "elevate", "unlock", "dive into", "game-changer", "stress-free", "seamless",
    "in today's", "let us handle", "embark",
]
# Not-X-but-Y construction.
NOT_JUST_RE = re.compile(r"\b(not just|isn't just|no es solo|no solo|más que solo)\b", re.I)
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⬆✅✨]")
HASHTAG_RE = re.compile(r"#\w+")
TU_RE = re.compile(r"\b(tu|tus|te|ti|contigo|tuyo|mándaselo|guarda|cuéntanos|llámanos)\b", re.I)
USTEDES_RE = re.compile(r"\b(ustedes|su|sus|les|llámenos|cuéntennos|estén|quieran|necesitan)\b", re.I)


def split_caption(caption):
    if DIVIDER not in caption or FLAG not in caption:
        return None, None
    es, en = caption.split(DIVIDER, 1)
    return es.strip(), en.strip()


def sentences(text):
    body = HASHTAG_RE.sub("", text)
    body = re.sub(r"^[📍🔗].*$", "", body, flags=re.M)
    parts = re.split(r"(?<=[.!?…])\s+|\n+", body)
    return [p.strip() for p in parts if len(p.strip()) > 3]


def words(text):
    return re.findall(r"[\wáéíóúüñÁÉÍÓÚÜÑ']+", text)


def lint_post(p, issues):
    pid = p["id"]

    def add(level, msg):
        issues.append((level, pid, msg))

    es, en = split_caption(p["caption"])
    if es is None:
        add("ERROR", f"caption must be Spanish, then a line '{DIVIDER}', then '{FLAG}' English")
        return
    if p["caption"].index(FLAG) < p["caption"].index(DIVIDER):
        add("ERROR", "English flag appears before the divider: Spanish must come first")

    full = p["caption"]
    es_body = HASHTAG_RE.sub("", es)
    en_body = HASHTAG_RE.sub("", en)

    # ---- hard rules ----
    if re.search(r"\bnotari[oa]s?\b", full, re.I):
        add("ERROR", "never write notario/notaria in Spanish: use 'notary public'")
    if re.search(r"\$\s?\d", full):
        add("ERROR", "a price/fee is in the caption: no prices are approved for posts")
    if re.search(r"100\s?%|garantiz|guarantee", full, re.I):
        add("ERROR", "guarantee/100% claim: Betty can't stand behind absolutes")
    if re.search(r"últim[oa]s? (lugares|fechas|días)|only \d+ (spots|dates)|hurry|date will sell", full, re.I):
        add("ERROR", "false/pressure urgency")
    if not re.search(r"492-3054|link (en la )?bio|link in (our )?bio", full, re.I):
        add("ERROR", "no call to action (phone or link in bio)")
    if len(full) > 2200:
        add("ERROR", f"caption is {len(full)} characters (Instagram limit 2,200)")

    # ---- AI-tell warnings ----
    if "—" in es_body.replace(DIVIDER, "") or "—" in en_body or "–" in en_body:
        add("WARN", "em/en dash in the text: a common AI tell, use a period or comma")
    for ph in STOCK_ES:
        if re.search(r"\b" + re.escape(ph) + r"\b", es_body.lower()):
            add("WARN", f"stock Spanish phrase: '{ph}'")
    for ph in STOCK_EN:
        if re.search(r"\b" + re.escape(ph) + r"\b", en_body.lower()):
            add("WARN", f"stock English phrase: '{ph}'")
    if NOT_JUST_RE.search(es_body) or NOT_JUST_RE.search(en_body):
        add("WARN", "'not just X but Y' construction")

    emoji_es, emoji_en = len(EMOJI_RE.findall(es_body)), len(EMOJI_RE.findall(en_body))
    emoji_en -= en_body.count(FLAG)  # the flag divider does not count
    if emoji_es > 3 or emoji_en > 3:
        add("WARN", f"emoji heavy (ES {emoji_es}, EN {emoji_en}): keep to 1–3 per language")
    excl = es_body.count("!") + en_body.count("!")
    if excl > 2:
        add("WARN", f"{excl} exclamation marks: sounds like an ad, keep to 1–2 total")
    tags = HASHTAG_RE.findall(full)
    if len(tags) > 10:
        add("WARN", f"{len(tags)} hashtags: keep to 10 or fewer")

    # Three-item bullet lists / triads
    for label, txt in (("ES", es_body), ("EN", en_body)):
        bullets = re.findall(r"^\s*[•\-\*]\s", txt, re.M)
        if len(bullets) == 3:
            add("WARN", f"{label}: a three-bullet list (rule-of-three feel); fine for real steps, otherwise vary")

    # Mirror translation: same sentence count AND most sentence pairs have near-equal length
    s_es, s_en = sentences(es_body), sentences(en_body)
    if len(s_es) == len(s_en) and len(s_es) >= 3:
        close = sum(
            1 for a, b in zip(s_es, s_en)
            if abs(len(words(a)) - len(words(b))) <= 0.2 * max(len(words(a)), len(words(b)))
        )
        if close / len(s_es) >= 0.7:
            add("WARN", "English is a sentence-by-sentence mirror of the Spanish: adapt it, don't translate it")

    # Tú vs ustedes mixing in the Spanish
    if TU_RE.search(es_body) and re.search(r"\b(ustedes|su|sus)\b", es_body, re.I):
        add("WARN", "Spanish mixes 'tú' and 'ustedes' forms: pick one address (brand-voice.md)")

    # Hook length: first line should be short enough to show before '...more'
    first = es.split("\n", 1)[0]
    if len(first) > 125:
        add("WARN", f"Spanish hook is {len(first)} characters; ~125 show before '...more'")
    long_sent = [s for s in s_es + s_en if len(words(s)) > 32]
    if long_sent:
        add("WARN", f"{len(long_sent)} very long sentence(s) (>32 words): hard to read on a phone")

    # Image text
    for key in ("image_text_es", "image_text_en"):
        t = p.get(key, "")
        if not t:
            add("WARN", f"missing {key}: record the text that is printed on the image")
        elif len(words(t)) > 14:
            add("WARN", f"{key} is {len(words(t))} words: image text should be a short headline")
    if p.get("image_text_es") and p.get("image_text_en"):
        cap_l = full.lower()
        for key in ("image_text_es", "image_text_en"):
            t = p[key].strip(" .?!¿¡").lower()
            if t and t in cap_l:
                add("WARN", f"{key} is repeated verbatim in the caption: the caption should add something")

    # Alt text
    if not p.get("alt_es") or not p.get("alt_en"):
        add("ERROR", "missing alt text (ES and EN)")


def lint_week(posts, issues):
    # Repeated openers / closers / emojis across the week
    openers = Counter(split_caption(p["caption"])[0].split(" ")[0].lower() for p in posts if split_caption(p["caption"])[0])
    for w, n in openers.items():
        if n > 1:
            issues.append(("WARN", "week", f"{n} posts start with the same word: '{w}'"))
    cta = Counter("👉" in p["caption"] for p in posts)
    if cta.get(True, 0) == len(posts) and len(posts) > 2:
        issues.append(("WARN", "week", "every post uses the 👉 call-to-action marker: vary or drop it"))
    first_emoji = Counter(
        (EMOJI_RE.findall(split_caption(p["caption"])[0].split("\n", 1)[0]) or [""])[-1] for p in posts
        if split_caption(p["caption"])[0]
    )
    if first_emoji.get("", 0) == 0 and len(posts) > 2:
        issues.append(("WARN", "week", "every hook line ends with an emoji: a repeated pattern"))
    lens = [len(p["caption"]) for p in posts]
    if max(lens) - min(lens) < 150 and len(posts) > 2:
        issues.append(("WARN", "week", "all captions are nearly the same length: vary the rhythm"))
    pillars = Counter(p["pillar"] for p in posts)
    if len(posts) >= 3 and len(pillars) < 3:
        issues.append(("WARN", "week", "fewer than 3 content pillars this week"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    wk = sys.argv[1]
    cal = json.load(open(f"social/calendar/{wk}.json", encoding="utf-8"))
    issues = []
    for p in cal["posts"]:
        lint_post(p, issues)
    lint_week(cal["posts"], issues)
    errors = [i for i in issues if i[0] == "ERROR"]
    warns = [i for i in issues if i[0] == "WARN"]
    for lvl, pid, msg in sorted(issues, key=lambda i: (i[1], i[0])):
        print(f"{lvl:5}  {pid:12}  {msg}")
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s) across {len(cal['posts'])} posts")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
