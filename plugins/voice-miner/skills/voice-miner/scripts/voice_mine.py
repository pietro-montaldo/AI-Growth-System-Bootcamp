#!/usr/bin/env python3
"""Mine a person's writing and speaking voice from sent emails and call transcripts.

Standard library only. Five subcommands:

  clean        Strip quoted replies, forwards and repeated signatures from sent emails,
               drop auto-replies, invites, templates and near-empty mails.
  score        Score every cleaned email for the likelihood it was AI-written.
               Uses the person's own pre-ChatGPT emails as a baseline when there are enough.
  fingerprint  Measure the voice of the emails that passed (lengths, greetings, sign-offs,
               punctuation, signature phrases), split by language and by email kind.
  transcript   Pull one speaker's turns out of call transcripts and measure how they talk.
  check        Check a new draft for AI tells and for drift from the person's own numbers.

Email input is JSONL, one object per line:
  {"id": "...", "date": "2024-03-01", "to": "a@b.com", "subject": "...",
   "kind": "reply|new|cold|followup" (optional), "body": "..."}

Example:
  python3 voice_mine.py clean emails.jsonl -o clean.jsonl
  python3 voice_mine.py score clean.jsonl -o scored.jsonl
  python3 voice_mine.py fingerprint scored.jsonl -o fingerprint.json
  python3 voice_mine.py transcript calls/ --speaker "Jane Doe" -o speech.json
  python3 voice_mine.py check draft.txt --fingerprint fingerprint.json --kind cold
"""

import argparse
import collections
import hashlib
import json
import math
import os
import re
import statistics
import sys

CHATGPT_LAUNCH = "2022-11-30"  # emails before this date are treated as human-written
MIN_BASELINE = 20               # pre-ChatGPT emails needed before the baseline is trusted
MIN_WORDS = 15                  # shorter mails only count toward greeting/sign-off stats

# ---------------------------------------------------------------------------
# Language detection: crude stopword vote, good enough to split a mailbox.

STOPWORDS = {
    "en": "the and to of is that it for you with this be on are have not we i will can just".split(),
    "es": "el la de que y en los las por con para una es lo como pero más te muy si".split(),
    "it": "il di che e la per non un una sono è mi ti ci con ma anche come se della".split(),
    "fr": "le la les de et des un une est pas que pour vous nous avec dans ce sur je".split(),
    "de": "der die und das ist nicht ich sie mit den zu ein eine auf für sie wir auch".split(),
    "pt": "o a de que e do da em um uma para com não os as se mas você muito por".split(),
}


def detect_lang(text):
    words = re.findall(r"[a-zà-ÿ]+", text.lower())
    if not words:
        return "unknown"
    counts = {lang: sum(1 for w in words if w in set(sw)) for lang, sw in STOPWORDS.items()}
    lang, best = max(counts.items(), key=lambda kv: kv[1])
    return lang if best >= 2 else "unknown"


# ---------------------------------------------------------------------------
# Cleaning

QUOTE_MARKERS = [
    r"^>",
    r"^On .{0,200}wrote:\s*$",
    r"^On .{0,120}\n?.{0,120}wrote:\s*$",
    r"^El .{0,200}escribió:\s*$",
    r"^Il .{0,200}ha scritto:\s*$",
    r"^Le .{0,200}a écrit\s*:\s*$",
    r"^Am .{0,200}schrieb .{0,100}:\s*$",
    r"^Em .{0,200}escreveu:\s*$",
    r"^-{2,}\s*Original Message\s*-{2,}",
    r"^-{2,}\s*Forwarded message\s*-{2,}",
    r"^From:\s.+$",
    r"^De:\s.+$",
    r"^Da:\s.+$",
    r"^_{10,}\s*$",
]
QUOTE_RE = re.compile("|".join(QUOTE_MARKERS), re.MULTILINE | re.IGNORECASE)

SKIP_SUBJECT = re.compile(
    r"^(invitation|updated invitation|accepted|declined|tentative|canceled|cancelled|"
    r"automatic reply|auto(matic)?[- ]reply|out of (the )?office|read:|delivery status)",
    re.IGNORECASE,
)
SIG_DELIM = re.compile(r"^--\s*$", re.MULTILINE)
MOBILE_FOOTER = re.compile(r"^(Sent from my .+|Get Outlook for .+|Enviado desde .+|Inviato da .+)$",
                           re.MULTILINE | re.IGNORECASE)


def strip_quotes(body):
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    m = QUOTE_RE.search(body)
    if m:
        body = body[: m.start()]
    body = SIG_DELIM.split(body)[0]
    body = MOBILE_FOOTER.sub("", body)
    return body.strip()


def find_signature_lines(bodies, min_share=0.02, min_count=5):
    """Lines that recur near the end of many emails are a signature, not voice.

    Sign-offs ("Best,", "Talk soon,"), the bare name the person signs with ("Jane.")
    and short sentences they repeat ("Let me know!") are voice, so they stay.
    """
    tail_counts = collections.Counter()
    for b in bodies:
        tail = [ln.strip() for ln in b.splitlines() if ln.strip()][-8:]
        for ln in set(tail):
            tail_counts[ln] += 1
    floor = max(min_count, min_share * max(len(bodies), 1))
    recurring = {ln: c for ln, c in tail_counts.items() if c >= floor}
    names = {ln: c for ln, c in recurring.items() if re.fullmatch(r"[A-ZÀ-Ý][a-zà-ÿ]+\.?", ln)}
    top_name = max(names.values(), default=0)
    sig = set()
    for ln, c in recurring.items():
        if ln.endswith(","):
            continue                                   # sign-off
        if ln in names and c >= 0.1 * top_name:
            continue                                   # the name they sign with
        if (len(ln.split()) <= 8 and re.search(r"[.!?)]$", ln) and not ln.startswith("*")
                and not re.search(r"[@|]|www\.|https?:|\(\.\)", ln)):
            continue                                   # a short sentence they like to repeat
        sig.add(ln)
    return sig


def norm_for_dupes(text):
    t = re.sub(r"\b[A-Z][a-z]+\b", "X", text)        # names
    t = re.sub(r"\d+", "0", t)
    t = re.sub(r"\s+", " ", t).lower()
    return hashlib.md5(t[:300].encode()).hexdigest()


def cmd_clean(args):
    rows = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]
    for r in rows:
        r["body"] = strip_quotes(r.get("body", ""))
    sig = find_signature_lines([r["body"] for r in rows if r["body"]])
    dupes = collections.Counter(norm_for_dupes(r["body"]) for r in rows if r["body"])
    out, stats = [], collections.Counter()
    for r in rows:
        subj = r.get("subject", "") or ""
        lines = [ln for ln in r["body"].splitlines() if ln.strip() not in sig]
        body = "\n".join(lines).strip()
        r["body"] = body
        words = len(body.split())
        if SKIP_SUBJECT.search(subj):
            r["skip"] = "auto/invite"
        elif not body:
            r["skip"] = "empty (forward or attachment only)"
        elif dupes[norm_for_dupes(body)] >= 3:
            r["skip"] = "template (sent 3+ times nearly identical)"
        elif words < MIN_WORDS:
            r["skip"] = "short (kept for greeting/sign-off only)"
        stats[r.get("skip", "kept")] += 1
        r["lang"] = detect_lang(body)
        r["words"] = words
        out.append(r)
    write_jsonl(out, args.output)
    print(json.dumps({"total": len(rows), "signature_lines_removed": sorted(sig), **stats},
                     ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# AI scoring

# Weighted tells. Weight 3 = strong on its own, 2 = medium, 1 = weak (needs company).
# Tells the person already used before ChatGPT existed are neutralised by the baseline.
AI_WORDS = {
    3: ["delve", "delving", "tapestry", "testament to", "seamless", "seamlessly", "elevate your",
        "unlock the", "unleash", "game-changer", "game changer", "in today's fast-paced",
        "ever-evolving", "ever-changing landscape", "navigate the complexities", "embark",
        "realm", "bustling", "meticulous", "meticulously", "underscore", "underscores",
        "load-bearing", "earns its keep", "doing the heavy lifting", "every single"],
    2: ["leverage", "leveraging", "robust", "streamline", "streamlined", "pivotal", "foster",
        "fostering", "holistic", "synergy", "synergies", "cutting-edge", "transformative",
        "empower", "empowering", "comprehensive", "landscape", "resonate", "resonates",
        "intricate", "nuanced", "multifaceted", "paramount", "showcase", "showcasing",
        "invaluable", "harness", "spearhead", "elevate", "unlock", "journey", "actionable insights",
        "deep dive", "dive into", "quietly", "genuinely", "crucial", "vital", "interplay",
        "dependable", "deliberate", "enormously", "immense", "remarkably", "incredibly",
        "supercharge", "game-changing", "paradigm", "trajectory"],
    1: ["enhance", "ensure", "ensuring", "utilize", "facilitate", "optimize", "insights",
        "valuable", "tailored", "align with", "aligned with", "additionally", "furthermore",
        "moreover", "key takeaways", "in summary", "ultimately", "notably", "truly",
        "honestly", "personally", "steady", "practical", "prioritize", "core", "framework",
        "ecosystem", "absolutely"],
}
AI_PHRASES = {
    3: [r"i hope this (e-?mail|message|note) finds you (well|great|in good health)",
        r"i hope you('| a)re (doing )?well\.? i wanted to",
        r"i trust this (e-?mail|message) finds you",
        r"(great|excellent|fantastic) question",
        r"you('| a)re absolutely right",
        r"i'?d be (more than )?happy to (help|assist)",
        r"please don'?t hesitate to",
        r"thank you for (reaching out|your patience)[^.]*\. i (understand|appreciate)",
        r"here'?s the (thing|kicker|truth)",
        r"let'?s dive in", r"without further ado",
        r"(sent|written|drafted|generated) (with|by|using) (superhuman|copilot|gemini|chatgpt|ai\b|lavender|grammarly)",
        r"as an ai\b",
        r"the distinction matters",
        r"the honest answer is", r"here'?s the part that", r"the (trap|catch) is",
        r"rather than (merely|simply|relying)", r"\bnot simply\b", r"less like an? [^.]{1,30} and more like",
        r"(want me to|if you want, i can also|would you like me to)",
        r"utm_source=chatgpt|oaicite|contentreference",
        r"\{\{\s*first_?name\s*\}\}|\[(company|first name|name)\]",
        r"(impressive|inspiring) work at", r"truly inspired by",
        r"i'?m (thrilled|humbled|excited) to (announce|share)"],
    2: [r"i wanted to (reach out|touch base|follow up)",
        r"(just )?(circling|looping) back",
        r"i came across your (profile|company|post)",
        r"i noticed (that )?(you|your company)",
        r"i('d| would) love to (connect|learn more|explore)",
        r"(it'?s|that'?s) (not just|not only|more than just) [^.]{1,60}(it'?s|but)",
        r"isn'?t (just )?about [^.]{1,60}\. it'?s about",
        r"at the end of the day", r"when it comes to", r"in today'?s",
        r"it'?s worth noting", r"it is important to note",
        r"looking forward to (connecting|hearing your thoughts)",
        r"feel free to (reach out|let me know)",
        r"let me know if you have any (other |further )?questions",
        r"i appreciate you (taking the time|reaching out)",
        r"best of luck with", r"hope this helps",
        r"\b(this|that) matters\.", r"matters because",       # common in speech, so medium only
        r"without (requiring|sacrificing|losing)", r"worth stating plainly", r"full stop\.",
        r"let that sink in", r"read that again", r"unpopular opinion",
        r"here'?s what (nobody|no one) tells you", r"let'?s unpack",
        r"i noticed (that )?\w+ (is|has|recently)", r"i saw (that )?you (recently )?(raised|launched|posted)",
        r"congrat(s|ulations) on the (funding|new role|raise)",
        r"(agree|thoughts)\?\s*$", r"let me be direct", r"that'?s a fair concern",
        r"despite these challenges", r"the future looks bright"],
}
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")
FUNCTIONAL_EMOJI_RE = re.compile("[\u2705\u2714\u274C\U0001F680\U0001F9E0\U0001F539\U0001F4A1\U0001F449\u26A0]|[1-9]\ufe0f?\u20e3")


def sentences(text):
    parts = []
    for line in text.splitlines():                     # greetings and sign-offs sit on their own lines
        parts += re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý¿¡\"'(])", line.strip())
    return [p for p in parts if len(p.split()) >= 2]


def features(body):
    low = body.lower()
    words = re.findall(r"\b[\w'’-]+\b", body)
    n = max(len(words), 1)
    sents = sentences(body)
    slen = [len(s.split()) for s in sents]
    f = {
        "words": len(words),
        "em_dash": body.count("—"),
        "en_dash_spaced": body.count(" – "),
        "curly": len(re.findall("[“”‘’]", body)),
        "straight": len(re.findall("[\"']", body)),
        "markdown": len(re.findall(r"\*\*[^*]+\*\*|^#{1,3} |^\s*[-*] \*\*", body, re.MULTILINE)),
        "bullets": len(re.findall(r"^\s*([-*•]|\d+[.)])\s", body, re.MULTILINE)),
        "arrows": body.count("→") + body.count("➡") + body.count("≈") + body.count("─"),
        "functional_emoji": len(FUNCTIONAL_EMOJI_RE.findall(body)),
        "emoji": len(EMOJI_RE.findall(body)),
        "invisible": len(re.findall("[\u200b\u200c\u200d\u2060\ufeff\u202f]", body)),
        "exclaim": body.count("!"),
        "triads": len(re.findall(r"\b\w+(?: \w+)?, \w+(?: \w+)?,? and \w+", body)),
        "sent_mean": statistics.mean(slen) if slen else 0,
        "sent_cv": (statistics.pstdev(slen) / statistics.mean(slen)) if len(slen) >= 6 else None,
        "word_hits": [], "phrase_hits": [],
    }
    for w, terms in AI_WORDS.items():
        for t in terms:
            if re.search(r"\b" + re.escape(t) + r"\b", low):
                f["word_hits"].append((t, w))
    for w, pats in AI_PHRASES.items():
        for p in pats:
            if re.search(p, low):
                f["phrase_hits"].append((p, w))
    f["per100"] = 100.0 / n
    return f


def baseline_from(rows):
    """What the person did before AI writing tools existed."""
    base = [r for r in rows if r.get("date", "9999") < CHATGPT_LAUNCH and not r.get("skip")]
    if len(base) < MIN_BASELINE:
        return None, len(base)
    feats = [features(r["body"]) for r in base]
    used_words = collections.Counter(t for f in feats for t, _ in f["word_hits"])
    used_phrases = collections.Counter(p for f in feats for p, _ in f["phrase_hits"])
    k = len(feats)
    return {
        "n": k,
        "em_dash_share": sum(1 for f in feats if f["em_dash"]) / k,
        "curly_share": sum(1 for f in feats if f["curly"]) / k,
        "markdown_share": sum(1 for f in feats if f["markdown"]) / k,
        "bullet_share": sum(1 for f in feats if f["bullets"]) / k,
        "emoji_share": sum(1 for f in feats if f["emoji"]) / k,
        # A tell the person used in 10%+ of their own pre-AI mail is their voice, not AI.
        "own_words": {t for t, c in used_words.items() if c / k >= 0.1},
        "own_phrases": {p for p, c in used_phrases.items() if c / k >= 0.1},
        "sent_mean": statistics.mean(f["sent_mean"] for f in feats),
        "sent_mean_sd": statistics.pstdev([f["sent_mean"] for f in feats]) or 1.0,
    }, len(base)


def score_one(r, base):
    f = features(r["body"])
    score, reasons = 0.0, []

    def add(points, why):
        nonlocal score
        score += points
        reasons.append(f"+{points:g} {why}")

    em_ok = base and base["em_dash_share"] >= 0.1
    if f["em_dash"] and not em_ok:
        add(min(2.5, 0.5 * f["em_dash"] + (1 if f["em_dash"] >= 3 else 0)), f"{f['em_dash']} em dash(es)")
    if f["en_dash_spaced"] >= 2 and not em_ok:
        add(1, "spaced en dashes used as em dashes")
    if f["curly"] and f["straight"] and not (base and base["curly_share"] >= 0.3):
        add(2, "mixed curly and straight quotes (pasted text)")
    if f["invisible"]:
        add(2, "invisible/non-breaking characters (pasted text)")
    if f["markdown"] and not (base and base["markdown_share"] >= 0.1):
        add(3, "markdown bold or headers")
    if f["bullets"] >= 3 and f["words"] < 250 and not (base and base["bullet_share"] >= 0.2):
        add(1, "bullet list in a short email")
    if f["arrows"]:
        add(1, "arrow or symbol characters (→ ≈ ─)")
    if f["functional_emoji"] and not (base and base["emoji_share"] >= 0.1):
        add(1.5, "functional emoji (✅ 🚀 1️⃣ 👉)")
    if f["emoji"] >= 2 and f["bullets"] and not (base and base["emoji_share"] >= 0.1):
        add(2, "emoji used as bullets")
    own_w = base["own_words"] if base else set()
    own_p = base["own_phrases"] if base else set()
    hits = [t for t, _ in f["word_hits"]]
    for t, w in f["word_hits"]:
        if any(t != h and t in h for h in hits):   # 'unlock' inside 'unlock the' counts once
            continue
        if t not in own_w:
            add(w * 0.5, f"AI-typical word '{t}'")
    for p, w in f["phrase_hits"]:
        if p not in own_p:
            add(w, f"AI-typical phrase /{p}/")
    if f["triads"] >= 2 and f["words"] < 300:
        add(1, f"{f['triads']} lists of three")
    if f["sent_cv"] is not None and f["sent_cv"] < 0.3:
        add(1, "very uniform sentence lengths")
    if base and base.get("sent_mean") and f["sent_mean"]:
        z = (f["sent_mean"] - base["sent_mean"]) / base["sent_mean_sd"]
        if z > 2.5:
            add(1.5, f"sentences much longer than your pre-AI norm (z={z:.1f})")

    verdict = "ai" if score >= 4 else "suspect" if score >= 2 else "human"
    return round(score, 1), verdict, reasons


def cmd_score(args):
    rows = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]
    base, nbase = baseline_from(rows)
    counts = collections.Counter()
    for r in rows:
        if r.get("skip"):
            r["verdict"] = "skipped"
        elif r.get("date", "9999") < CHATGPT_LAUNCH:
            r["ai_score"], r["verdict"], r["ai_reasons"] = 0, "human-preAI", []
        else:
            r["ai_score"], r["verdict"], r["ai_reasons"] = score_one(r, base)
        counts[r["verdict"]] += 1
    write_jsonl(rows, args.output)
    suspects = sorted((r for r in rows if r["verdict"] in ("suspect", "ai")),
                      key=lambda r: -r["ai_score"])
    report = {
        "baseline": f"{nbase} pre-ChatGPT emails" + ("" if base else
                    f" (fewer than {MIN_BASELINE}: scoring without a personal baseline)"),
        "baseline_habits": None if not base else {
            "uses_em_dashes": base["em_dash_share"] >= 0.1,
            "uses_curly_quotes": base["curly_share"] >= 0.3,
            "own_ai_looking_words": sorted(base["own_words"]),
        },
        "verdicts": counts,
        "top_suspects": [{"id": r.get("id"), "date": r.get("date"), "subject": r.get("subject"),
                          "score": r["ai_score"], "reasons": r["ai_reasons"][:5]}
                         for r in suspects[:15]],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, default=list))


# ---------------------------------------------------------------------------
# Fingerprint

GREETING_RE = re.compile(r"^(hi|hey|hello|dear|good (morning|afternoon)|hola|buenas|ciao|salve|"
                         r"buongiorno|bonjour|hallo|olá|oi|morning|yo)\b[^\n]{0,40}$", re.IGNORECASE)
CONTRACTION_RE = re.compile(r"\b\w+'(s|re|ve|ll|d|m|t)\b|\bcan't\b|\bwon't\b", re.IGNORECASE)
EXPANDABLE_RE = re.compile(r"\b(i am|you are|we are|it is|do not|does not|did not|i have|"
                           r"we have|i will|we will|cannot|is not|are not|that is|let us)\b", re.IGNORECASE)
HEDGES = ["i think", "maybe", "perhaps", "probably", "i guess", "sort of", "kind of", "just",
          "i feel", "might", "not sure", "honestly"]
INTENSIFIERS = ["really", "very", "super", "so much", "totally", "absolutely", "definitely",
                "extremely", "incredibly", "quite"]


def mask_names(line):
    """Replace capitalised words after the first one, so 'Hi Anna,' and 'Hi Tom,' count as one habit."""
    first, _, rest = line.partition(" ")
    rest = re.sub(r"\b[A-ZÀ-Ý][a-zà-ÿ]+\b", "{name}", rest)
    return (first + " " + rest).strip()


def first_last_lines(body):
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    if not lines:
        return None, None
    greet = mask_names(lines[0]) if GREETING_RE.match(lines[0]) else "(no greeting, straight in)"
    signoff = None
    for ln in reversed(lines[-3:]):
        bare_name = re.fullmatch(r"[-–—]?\s*[A-ZÀ-Ý][a-zà-ÿ]*\.?( [A-ZÀ-Ý][a-zà-ÿ]*\.?)?", ln)
        if bare_name and signoff is None:
            signoff = "{name}"          # last line is just the name; look one line up for the closing word
            continue
        if len(ln.split()) <= 5 and "?" not in ln:
            signoff = mask_names(ln.rstrip(",")) + (" / {name}" if signoff == "{name}" else "")
        break
    return greet, signoff


def ngrams(words, n):
    return zip(*(words[i:] for i in range(n)))


def signature_phrases(texts, lang_stop, top=40):
    """Phrases used across many separate emails: a person's verbal tics in writing."""
    df = collections.Counter()
    for t in texts:
        ws = re.findall(r"[a-zà-ÿ']+", t.lower())
        seen = set()
        for n in (2, 3, 4):
            for g in ngrams(ws, n):
                if all(w in lang_stop for w in g):
                    continue
                seen.add(" ".join(g))
        df.update(seen)
    k = max(len(texts), 1)
    floor = max(3, int(0.04 * k))
    items = [(g, c) for g, c in df.items() if c >= floor]
    # Prefer longer phrases when they cover their shorter parts.
    items.sort(key=lambda gc: (-gc[1], -len(gc[0])))
    keep = []
    for g, c in items:
        if any(g in kg and abs(c - kc) <= max(1, 0.2 * c) for kg, kc in keep):
            continue
        keep.append((g, c))
        if len(keep) >= top:
            break
    return [{"phrase": g, "emails": c, "share": round(c / k, 2)} for g, c in keep]


def pct(counter, total, top=6):
    return [{"value": v, "share": round(c / total, 2)} for v, c in counter.most_common(top)] if total else []


def profile(rows, short_rows):
    bodies = [r["body"] for r in rows]
    k = len(bodies)
    allw = [len(b.split()) for b in bodies]
    sents = [s for b in bodies for s in sentences(b)]
    slen = [len(s.split()) for s in sents] or [0]
    paras = [p for b in bodies for p in re.split(r"\n\s*\n", b) if p.strip()]
    text = "\n".join(bodies)
    low = text.lower()
    nwords = max(len(text.split()), 1)
    greet, sign = collections.Counter(), collections.Counter()
    for r in rows + short_rows:
        g, s = first_last_lines(r["body"])
        if g:
            greet[g] += 1
        if s:
            sign[s] += 1
    starters = collections.Counter(" ".join(s.split()[:2]).lower().strip(",.") for s in sents
                                   if not GREETING_RE.match(s))
    contr = len(CONTRACTION_RE.findall(text))
    expd = len(EXPANDABLE_RE.findall(text))
    lang_stop = set(sum(STOPWORDS.values(), [])) | {"a", "an", "in", "at", "of", "or", "so", "if",
                                                     "my", "me", "your", "our", "us", "do", "was"}
    q = lambda xs, p: sorted(xs)[int(p * (len(xs) - 1))] if xs else 0
    return {
        "emails": k,
        "length_words": {"p25": q(allw, .25), "median": q(allw, .5), "p75": q(allw, .75), "p90": q(allw, .9)},
        "sentence_words": {"mean": round(statistics.mean(slen), 1), "median": q(slen, .5),
                           "share_6_or_less": round(sum(1 for x in slen if x <= 6) / len(slen), 2),
                           "share_25_or_more": round(sum(1 for x in slen if x >= 25) / len(slen), 2)},
        "paragraphs_per_email": round(len(paras) / max(k, 1), 1),
        "one_sentence_paragraph_share": round(sum(1 for p in paras if len(sentences(p)) <= 1) / max(len(paras), 1), 2),
        "greetings": pct(greet, sum(greet.values())),
        "signoffs": pct(sign, sum(sign.values())),
        "per_100_words": {
            "exclamation": round(100 * text.count("!") / nwords, 2),
            "question": round(100 * text.count("?") / nwords, 2),
            "ellipsis": round(100 * (text.count("...") + text.count("…")) / nwords, 2),
            "em_dash": round(100 * text.count("—") / nwords, 2),
            "spaced_hyphen_as_dash": round(100 * text.count(" - ") / nwords, 2),
            "parentheses": round(100 * text.count("(") / nwords, 2),
            "semicolon": round(100 * text.count(";") / nwords, 2),
            "colon": round(100 * text.count(":") / nwords, 2),
            "emoji": round(100 * len(EMOJI_RE.findall(text)) / nwords, 2),
            "all_caps_words": round(100 * len(re.findall(r"\b[A-Z]{3,}\b", text)) / nwords, 2),
        },
        "contraction_rate": round(contr / max(contr + expd, 1), 2),
        "emails_with_bullets": round(sum(1 for b in bodies if re.search(r"^\s*([-*•]|\d+[.)])\s", b, re.M)) / max(k, 1), 2),
        "emails_ending_with_question": round(sum(1 for b in bodies if "?" in "\n".join(b.strip().splitlines()[-3:])) / max(k, 1), 2),
        "lowercase_sentence_starts": round(sum(1 for s in sents if s[:1].islower()) / max(len(sents), 1), 2),
        "i_vs_we": {"i": len(re.findall(r"\bi\b", low)), "we": len(re.findall(r"\bwe\b", low))},
        "hedges_per_1000": {h: round(1000 * len(re.findall(r"\b" + h + r"\b", low)) / nwords, 1)
                            for h in HEDGES if re.search(r"\b" + h + r"\b", low)},
        "intensifiers_per_1000": {h: round(1000 * len(re.findall(r"\b" + h + r"\b", low)) / nwords, 1)
                                  for h in INTENSIFIERS if re.search(r"\b" + h + r"\b", low)},
        "top_sentence_starters": [{"start": s, "count": c} for s, c in starters.most_common(15)],
        "signature_phrases": signature_phrases(bodies, lang_stop),
    }


def cmd_fingerprint(args):
    rows = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]
    good = [r for r in rows if r.get("verdict") in ("human", "human-preAI")]
    short = [r for r in rows if (r.get("skip") or "").startswith("short")]
    out = {"source_counts": collections.Counter(r.get("verdict", "unscored") for r in rows),
           "by_language": {}}
    for lang in sorted({r.get("lang", "unknown") for r in good}):
        lr = [r for r in good if r.get("lang", "unknown") == lang]
        if len(lr) < 5:
            continue
        block = {"all": profile(lr, [r for r in short if r.get("lang") == lang])}
        for kind in sorted({r.get("kind") for r in lr if r.get("kind")}):
            kr = [r for r in lr if r.get("kind") == kind]
            if len(kr) >= 5:
                block[kind] = profile(kr, [])
        out["by_language"][lang] = block
    ref = [r for r in good if r["verdict"] == "human-preAI"] or good
    feats = [features(r["body"]) for r in ref]
    k = max(len(feats), 1)
    words = collections.Counter(t for f in feats for t, _ in set(f["word_hits"]))
    phrases = collections.Counter(p for f in feats for p, _ in set(f["phrase_hits"]))
    out["own_habits"] = {
        "from": "pre-ChatGPT emails" if ref and ref[0]["verdict"] == "human-preAI" else "emails that passed the AI filter",
        "em_dash": sum(1 for f in feats if f["em_dash"]) / k >= 0.1,
        "bullets": sum(1 for f in feats if f["bullets"]) / k >= 0.2,
        "emoji": sum(1 for f in feats if f["emoji"]) / k >= 0.1,
        "words": sorted(t for t, c in words.items() if c / k >= 0.1),
        "phrases": sorted(p for p, c in phrases.items() if c / k >= 0.1),
    }
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"wrote {args.output}: {len(good)} emails across {list(out['by_language'])}")


# ---------------------------------------------------------------------------
# Draft check: AI tells plus distance from the person's own numbers

def cmd_check(args):
    text = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    fp = json.load(open(args.fingerprint, encoding="utf-8")) if args.fingerprint else {}
    own = fp.get("own_habits", {})
    base = None
    if own:
        base = {"em_dash_share": 1 if own.get("em_dash") else 0, "curly_share": 0, "markdown_share": 0,
                "bullet_share": 1 if own.get("bullets") else 0, "emoji_share": 1 if own.get("emoji") else 0,
                "own_words": set(own.get("words", [])), "own_phrases": set(own.get("phrases", [])),
                "sent_mean": None, "sent_mean_sd": 1}   # length drift is checked below instead
    score, verdict, reasons = score_one({"body": text}, base)
    notes = []
    lang = args.lang or detect_lang(text)
    prof = fp.get("by_language", {}).get(lang, {})
    p = prof.get(args.kind) or prof.get("all")
    n = len(text.split())
    if p and n < 25:
        notes.append(f"{n} words: one-liner, so rates and greeting checks are skipped.")
        p = None                                   # per-100-word rates are noise on a one-liner
    if p:
        lw = p["length_words"]
        if n > lw["p90"]:
            notes.append(f"{n} words; you rarely go past {lw['p90']} (median {lw['median']}). Cut.")
        elif n < lw["p25"] // 2:
            notes.append(f"{n} words; much shorter than usual (median {lw['median']}).")
        sl = [len(x.split()) for x in sentences(text)]
        if sl:
            m = statistics.mean(sl)
            target = p["sentence_words"]["mean"]
            if abs(m - target) / max(target, 1) > 0.3:
                notes.append(f"average sentence {m:.0f} words; yours is {target}.")
        per = p["per_100_words"]
        words = max(n, 1)
        for key, ch in (("exclamation", "!"), ("em_dash", "—"), ("semicolon", ";")):
            got = 100 * text.count(ch) / words
            if got > 2 * per[key] + 0.3:
                notes.append(f"too many '{ch}' ({got:.1f}/100 words, you use {per[key]}).")
        g, sgn = first_last_lines(text)
        known_g = [x["value"] for x in p.get("greetings", [])]
        if g and known_g and g not in known_g:
            notes.append(f"greeting '{g}' isn't one you use. Yours: {', '.join(known_g[:3])}.")
        known_s = [x["value"] for x in p.get("signoffs", [])]
        if sgn and known_s and sgn not in known_s:
            notes.append(f"sign-off '{sgn}' isn't one you use. Yours: {', '.join(known_s[:3])}.")
        contr = len(CONTRACTION_RE.findall(text))
        expd = len(EXPANDABLE_RE.findall(text))
        if lang == "en" and expd >= 2 and p["contraction_rate"] >= 0.6 and contr / max(contr + expd, 1) < 0.5:
            notes.append("too formal: you normally use contractions (I'll, don't, it's).")
    print(json.dumps({"ai_score": score, "verdict": verdict, "ai_tells": reasons,
                      "off_voice": notes or ["none found"]}, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Transcripts

FILLERS = ["um", "uh", "erm", "like", "you know", "i mean", "basically", "actually", "literally",
           "right?", "okay?", "ok?", "so", "kind of", "sort of", "to be honest", "honestly",
           "fundamentally", "at the end of the day", "et cetera"]
TURN_RE = re.compile(r"^\s*(?:\[?\(?\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\)?\]?(?:\([^)]*\))?\s*[-–]?\s*)?"
                     r"(?:<v\s+)?([A-Za-zÀ-ÿ][\w.@'À-ÿ +-]{0,60}?)(?:>|:)\s*(.*)$")  # names, 'Speaker 2' or emails


def read_turns(path):
    """Parse 'Name: text', '[00:01] Name: text', VTT '<v Name>text' and 'Name\\ntext' blocks."""
    raw = open(path, encoding="utf-8", errors="ignore").read()
    raw = re.sub(r"^WEBVTT.*?\n\n", "", raw, flags=re.S)
    raw = re.sub(r"^\d+\n\d\d:\d\d:\d\d[.,]\d+ --> .*\n", "", raw, flags=re.M)
    turns, cur = [], None
    for line in raw.splitlines():
        m = TURN_RE.match(line)
        if m and m.group(2).strip():
            cur = [m.group(1).strip(), m.group(2).strip()]
            turns.append(cur)
        elif m and not m.group(2).strip():
            cur = [m.group(1).strip(), ""]
            turns.append(cur)
        elif cur and line.strip() and not re.match(r"^[\d:.,\->\s]+$", line):
            cur[1] += " " + line.strip()
    return [(s, t.strip()) for s, t in turns if t.strip()]


def cmd_transcript(args):
    paths = []
    for p in args.inputs:
        if os.path.isdir(p):
            paths += [os.path.join(p, f) for f in sorted(os.listdir(p))
                      if f.lower().endswith((".txt", ".vtt", ".srt", ".md"))]
        else:
            paths.append(p)
    want = [s.lower() for s in args.speaker]
    mine, others, per_call = [], 0, []
    for p in paths:
        turns = read_turns(p)
        me = [t for s, t in turns if any(w in s.lower() for w in want)]
        other_words = sum(len(t.split()) for s, t in turns if not any(w in s.lower() for w in want))
        my_words = sum(len(t.split()) for t in me)
        per_call.append({"file": os.path.basename(p), "my_turns": len(me),
                         "talk_share": round(my_words / max(my_words + other_words, 1), 2)})
        mine += me
        others += other_words
    text = " ".join(mine)
    low = text.lower()
    nwords = max(len(text.split()), 1)
    sents = sentences(text)
    starters = collections.Counter(" ".join(s.split()[:2]).lower().strip(",.") for s in sents)
    lang_stop = set(sum(STOPWORDS.values(), [])) | {"a", "an", "in", "at", "of", "or", "so", "if",
                                                     "my", "me", "your", "our", "us", "do", "was",
                                                     "um", "uh", "like", "yeah", "okay", "know"}
    out = {
        "calls": per_call,
        "words_spoken": nwords,
        "avg_turn_words": round(nwords / max(len(mine), 1), 1),
        "fillers_per_1000": {f: round(1000 * len(re.findall(r"\b" + re.escape(f.rstrip("?")) + r"\b"
                                                            + (r"\?" if f.endswith("?") else ""), low)) / nwords, 1)
                             for f in FILLERS},
        "questions_per_1000": round(1000 * text.count("?") / nwords, 1),
        "top_sentence_starters": [{"start": s, "count": c} for s, c in starters.most_common(20)],
        "signature_phrases": signature_phrases(mine, lang_stop, top=60),
    }
    if not mine:
        out["warning"] = ("No turns matched the speaker name. Check the speaker label used in the "
                          "transcripts (e.g. 'Speaker 1') and pass it with --speaker.")
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    if args.turns_out:
        with open(args.turns_out, "w", encoding="utf-8") as fh:
            fh.write("\n\n".join(mine))
    print(f"wrote {args.output}: {len(mine)} turns, {nwords} words from {len(paths)} files")


# ---------------------------------------------------------------------------

def write_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("clean", cmd_clean), ("score", cmd_score), ("fingerprint", cmd_fingerprint)):
        p = sub.add_parser(name)
        p.add_argument("input")
        p.add_argument("-o", "--output", required=True)
        p.set_defaults(fn=fn)
    p = sub.add_parser("check", help="check a draft for AI tells and off-voice numbers")
    p.add_argument("input", help="draft text file, or - for stdin")
    p.add_argument("--fingerprint", help="fingerprint.json from the voice profile")
    p.add_argument("--lang", help="language code; detected when omitted")
    p.add_argument("--kind", help="email kind to compare against, e.g. cold, reply")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("transcript")
    p.add_argument("inputs", nargs="+", help="transcript files or folders")
    p.add_argument("--speaker", action="append", required=True,
                   help="speaker label(s) for the person, repeatable (e.g. --speaker 'Jane Doe' --speaker 'Speaker 1')")
    p.add_argument("-o", "--output", required=True)
    p.add_argument("--turns-out", help="also write the person's raw turns here, for reading")
    p.set_defaults(fn=cmd_transcript)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
