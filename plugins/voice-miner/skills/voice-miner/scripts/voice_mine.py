#!/usr/bin/env python3
"""Mine a person's writing and speaking voice from sent emails and call transcripts.

Standard library only. Seven subcommands:

  extract      Read .mbox and .eml exports (plain text or HTML mail, any charset) and
               write the email JSONL the other commands expect.
  clean        Strip quoted replies, forwards and repeated signatures from sent emails,
               drop auto-replies, invites, templates and near-empty mails.
  score        Score every cleaned email for the likelihood it was AI-written.
               Uses the person's own pre-ChatGPT emails as a baseline when there are enough.
  fingerprint  Measure the voice of the emails that passed (lengths, greetings, sign-offs,
               punctuation, signature phrases), split by language and by email kind.
  redact       Replace client names, companies, emails and amounts in a fingerprint before
               it goes into the personal skill, and print what's left for review.
  transcript   Pull one speaker's turns out of call transcripts and measure how they talk.
  check        Check a new draft for AI tells and for drift from the person's own numbers.

Email input is JSONL, one object per line:
  {"id": "...", "date": "2024-03-01", "to": "a@b.com", "subject": "...",
   "kind": "cold|followup|reply|new" (optional), "body": "..."}
Kinds: cold (first message to someone who never wrote to them), followup (they wrote
again with no reply in between), reply (answering someone), new (first message in a
thread to someone they already know). Confirmed LinkedIn posts and DMs may be added
with kind post or dm. A missing or null date means the email is scored, never baseline.

Example (call the script by its full path):
  python3 voice_mine.py extract Sent.mbox -o emails.jsonl --from jane@acme.com
  python3 voice_mine.py clean emails.jsonl -o clean.jsonl
  python3 voice_mine.py score clean.jsonl -o scored.jsonl
  python3 voice_mine.py fingerprint scored.jsonl -o fingerprint.json
  python3 voice_mine.py redact fingerprint.json -o fingerprint.redacted.json --term Acme
  python3 voice_mine.py transcript calls/ --speaker "Jane Doe" -o speech.json
  python3 voice_mine.py check draft.txt --fingerprint fingerprint.json --kind cold
"""

import argparse
import collections
import email
import email.parser
import email.policy
import email.utils
import hashlib
import html
import html.parser
import json
import mailbox
import os
import re
import statistics
import sys

CHATGPT_LAUNCH = "2022-11-30"  # emails before this date are treated as human-written
MIN_BASELINE = 20               # pre-ChatGPT emails needed before the baseline is trusted
MIN_WORDS = 15                  # shorter mails only count toward greeting/sign-off stats
EMAIL_KINDS = ("cold", "followup", "reply", "new")
OTHER_KINDS = ("post", "dm", "comment")   # not email: email numbers never apply to these


def straighten(text):
    """Curly apostrophes and quotes to straight ones, so word and phrase matching sees one form."""
    return (text or "").translate({0x2019: "'", 0x2018: "'", 0x02BC: "'", 0x201C: '"', 0x201D: '"'})


def email_date(r):
    """ISO date string, or '' when missing or null. Never guessed."""
    d = r.get("date")
    return d.strip() if isinstance(d, str) else ""


def is_pre_ai(r):
    d = email_date(r)
    return bool(d) and d < CHATGPT_LAUNCH


def read_jsonl(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    for r in rows:
        if not isinstance(r.get("body"), str):
            r["body"] = ""
    return rows

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
# Extract: .mbox and .eml exports to JSONL

class _HTMLText(html.parser.HTMLParser):
    """HTML mail to plain text. Drops quoted history (gmail_quote, blockquote, Outlook's reply
    header and everything after it), styles and scripts. Keeps line and paragraph breaks."""
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "table", "ul", "ol",
             "blockquote", "pre", "hr"}
    VOID = {"br", "img", "hr", "meta", "input", "link", "wbr", "col", "area", "base", "source"}
    QUOTE_CLASSES = ("gmail_quote", "gmail_extra", "moz-cite-prefix", "yahoo_quoted", "protonmail_quote",
                     "apple-mail-quote")
    STOP_IDS = ("divrplyfwdmsg", "appendonsend", "mail-editor-reference-message-container")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.stopped = [], [], False

    def handle_starttag(self, tag, attrs):
        if self.stopped:
            return
        a = {k: (v or "") for k, v in attrs}
        if a.get("id", "").lower() in self.STOP_IDS:
            self.stopped = True                        # Outlook: the rest is the quoted thread
            return
        if self.skip:
            if tag == self.skip[0] and tag not in self.VOID:
                self.skip[1] += 1
            return
        cls = a.get("class", "").lower()
        if tag in ("style", "script", "head", "title", "blockquote") or any(c in cls for c in self.QUOTE_CLASSES):
            if tag not in self.VOID:
                self.skip = [tag, 1]
            return
        if tag in self.BLOCK:
            self.out.append("\n")
        if tag == "li":
            self.out.append("- ")

    def handle_endtag(self, tag):
        if self.stopped:
            return
        if self.skip:
            if tag == self.skip[0]:
                self.skip[1] -= 1
                if self.skip[1] <= 0:
                    self.skip = []
            return
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.stopped and not self.skip:
            self.out.append(re.sub(r"\s+", " ", data.replace("\xa0", " ")))

    def text(self):
        t = "".join(self.out)
        lines = [ln.strip() for ln in t.split("\n")]
        return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def html_to_text(markup):
    p = _HTMLText()
    try:
        p.feed(markup)
        p.close()
    except Exception:                                  # broken markup: keep what was parsed
        pass
    return p.text()


def decode_part(part):
    raw = part.get_payload(decode=True) or b""
    charset = part.get_content_charset() or "utf-8"
    for enc in (charset, "utf-8", "cp1252"):
        try:
            return raw.decode(enc), enc
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("latin-1"), "latin-1"


def leaf_parts(msg):
    """Body parts in order, without going into attached emails (message/rfc822)."""
    if msg.is_multipart():
        for sub in msg.get_payload():
            if sub.get_content_type() == "message/rfc822" or sub.get_content_disposition() == "attachment":
                continue
            yield from leaf_parts(sub)
    else:
        yield msg


def message_body(msg):
    """Prefer text/plain, fall back to text/html converted to text. Returns (body, source, charset)."""
    plain = htm = None
    for part in leaf_parts(msg):
        ct = part.get_content_type()
        if ct == "text/plain" and plain is None:
            plain = decode_part(part)
        elif ct == "text/html" and htm is None:
            htm = decode_part(part)
    if plain and plain[0].strip():
        return plain[0], "text", plain[1]
    if htm:
        return html_to_text(htm[0]), "html", htm[1]
    return "", "none", None


def iter_messages(paths):
    parser = email.parser.BytesParser(policy=email.policy.default)
    for path in paths:
        if os.path.isdir(path):
            subs = sorted(os.path.join(path, f) for f in os.listdir(path)
                          if f.lower().endswith((".eml", ".mbox")))
            yield from iter_messages(subs)
        elif path.lower().endswith(".eml"):
            with open(path, "rb") as fh:
                yield path, parser.parse(fh)
        else:                                          # .mbox, Google Takeout and Apple Mail exports
            box = mailbox.mbox(path, create=False)
            for key in box.iterkeys():
                yield path, parser.parsebytes(box.get_bytes(key))


def cmd_extract(args):
    want = [a.strip().lower() for a in args.sender]
    seen, rows, stats = set(), [], collections.Counter()
    senders, charsets = collections.Counter(), collections.Counter()
    for path, msg in iter_messages(args.inputs):
        stats["read"] += 1
        try:
            sender = (email.utils.parseaddr(str(msg.get("From", "")))[1] or "").lower()
        except Exception:
            sender = ""
        senders[sender] += 1
        if want and not any(w in sender for w in want):
            stats["skipped: not sent by the person"] += 1
            continue
        mid = str(msg.get("Message-ID", "") or "").strip().strip("<>")
        if mid and mid in seen:
            stats["skipped: duplicate"] += 1
            continue
        seen.add(mid)
        body, source, cs = message_body(msg)
        if not body.strip():
            stats["skipped: no text body"] += 1
            continue
        try:
            date = email.utils.parsedate_to_datetime(str(msg.get("Date", ""))).date().isoformat()
        except Exception:
            date = None                                # never guess a date
        try:
            to = [a for _, a in email.utils.getaddresses([str(msg.get("To", "") or "")]) if a]
        except Exception:
            to = []
        subject = str(msg.get("Subject", "") or "")
        is_reply = bool(msg.get("In-Reply-To") or msg.get("References")) or bool(
            re.match(r"^\s*(re|r|aw|sv|rif|res)\s*:", subject, re.IGNORECASE))
        rows.append({"id": mid or hashlib.md5(body.encode()).hexdigest()[:16], "date": date,
                     "to": to[0] if to else "", "subject": subject,
                     "thread": "reply" if is_reply else "first", "body": body})
        stats[f"body from {source}"] += 1
        charsets[cs] += 1
    write_jsonl(rows, args.output)
    report = {"written": len(rows), **stats, "charsets": charsets,
              "undated": sum(1 for r in rows if not r["date"])}
    if not want:
        report["senders"] = dict(senders.most_common(5))
        report["note"] = "No --from given, so every message was kept. Rerun with --from <their address> if others are mixed in."
    print(json.dumps(report, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Cleaning

# "On <date>, <name> <email> wrote:" in every supported language. Gmail and Apple Mail
# often wrap it over two lines, usually inside the <email>, so each also has a wrapped form
# whose first line must hold a digit (the date) to avoid eating a normal sentence.
ATTRIBUTIONS = [("On", r"wrote:"), ("El", r"escribió:"), ("Il", r"ha scritto:"),
                ("Le", r"a écrit\s*:"), ("Am", r"schrieb\b[^:]{0,100}:"), ("Em", r"escreveu:")]
HEADER_WORDS = r"From|De|Da|Von"          # Outlook reply header, en/es/fr/pt/it/de
QUOTE_MARKERS = [r"^>"]
for _start, _end in ATTRIBUTIONS:
    QUOTE_MARKERS.append(rf"^{_start} .{{0,200}}{_end}\s*$")
    QUOTE_MARKERS.append(rf"^{_start} (?=[^\n]*\d)[^\n]{{0,200}}\n[^\n]{{0,200}}{_end}\s*$")
QUOTE_MARKERS += [
    r"^-{2,}\s*(Original Message|Messaggio originale|Mensaje original|Message d'origine|"
    r"Ursprüngliche Nachricht|Mensagem original)\s*-{2,}",
    r"^-{2,}\s*(Forwarded message|Messaggio inoltrato|Mensaje reenviado|Message transféré|"
    r"Weitergeleitete Nachricht|Mensagem encaminhada)\s*-{2,}",
    r"^(Begin forwarded message|Inizio messaggio inoltrato|Comienzo del mensaje reenviado|"
    r"Début du message réexpédié|Anfang der weitergeleiteten Nachricht|Início da mensagem reencaminhada):",
    rf"^\*{{0,2}}(?:{HEADER_WORDS})\s*:\*{{0,2}}\s.+$",   # From: x, *From:* x, **Da:** x
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
    body = (body or "").replace("\r\n", "\n").replace("\r", "\n")
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
    rows = read_jsonl(args.input)
    for r in rows:
        r["body"] = strip_quotes(r["body"])
    sig = find_signature_lines([r["body"] for r in rows if r["body"]])
    for r in rows:                                     # drop the signature before looking for templates,
        lines = [ln for ln in r["body"].splitlines() if ln.strip() not in sig]
        r["body"] = "\n".join(lines).strip()          # or a shared signature hides every repeat
    dupes = collections.Counter(norm_for_dupes(r["body"]) for r in rows if r["body"])
    out, stats = [], collections.Counter()
    odd_kinds = collections.Counter(r.get("kind") for r in rows
                                    if r.get("kind") and r.get("kind") not in EMAIL_KINDS + OTHER_KINDS)
    for r in rows:
        subj = r.get("subject") or ""
        body = r["body"]
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
    report = {"total": len(rows), "signature_lines_removed": sorted(sig), **stats}
    if odd_kinds:
        report["warning"] = (f"unknown kind values {dict(odd_kinds)}. Use one of "
                             f"{', '.join(EMAIL_KINDS + OTHER_KINDS)}.")
    print(json.dumps(report, ensure_ascii=False, indent=2))


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
# Unfilled merge fields and [placeholders]. In a SENT email they mean a pasted template or
# AI draft. In a new draft they are deliberate, so check lists them instead of scoring them.
PLACEHOLDER_RE = re.compile(r"\{\{\s*[\w .-]{1,30}\s*\}\}|\[[^\]\n]{1,40}\]")
SENT_PLACEHOLDER_RE = re.compile(r"\{\{\s*first_?name\s*\}\}|\[(company|first name|name)\]", re.IGNORECASE)
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")
FUNCTIONAL_EMOJI_RE = re.compile("[\u2705\u2714\u274C\U0001F680\U0001F9E0\U0001F539\U0001F4A1\U0001F449\u26A0]|[1-9]\ufe0f?\u20e3")


def sentences(text):
    parts = []
    for line in text.splitlines():                     # greetings and sign-offs sit on their own lines
        parts += re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý¿¡\"'(])", line.strip())
    return [p for p in parts if len(p.split()) >= 2]


def features(body):
    body = body or ""
    low = straighten(body).lower()                     # curly apostrophes must not hide a tell
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
    base = [r for r in rows if is_pre_ai(r) and not r.get("skip")]
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


def score_one(r, base, draft=False):
    """draft=True for a new draft from check: [placeholders] there are on purpose."""
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
    if not draft and SENT_PLACEHOLDER_RE.search(r["body"] or ""):
        add(3, "unfilled placeholder like [name] or {{first_name}} (template or AI draft)")
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
    rows = read_jsonl(args.input)
    base, nbase = baseline_from(rows)
    counts = collections.Counter()
    for r in rows:
        if r.get("skip"):
            r["verdict"] = "skipped"
        elif is_pre_ai(r):
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
    """Replace capitalised words after the first one, so 'Hi Anna,' and 'Hi Tom,' count as one habit.
    A [name] or {{first_name}} placeholder counts as a name too."""
    line = PLACEHOLDER_RE.sub("{name}", line)
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
    bodies = [straighten(r["body"]) for r in rows]
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
        g, s = first_last_lines(straighten(r["body"]))
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
    rows = read_jsonl(args.input)
    good = [r for r in rows if r.get("verdict") in ("human", "human-preAI")]
    short = [r for r in rows if (r.get("skip") or "").startswith("short")]
    out = {"source_counts": collections.Counter(r.get("verdict", "unscored") for r in rows),
           "by_language": {}}
    for lang in sorted({r.get("lang", "unknown") for r in good}):
        lr = [r for r in good if r.get("lang", "unknown") == lang]
        if len(lr) < 5:
            continue
        block = {}
        mail = [r for r in lr if r.get("kind") not in OTHER_KINDS]   # posts and DMs never set email numbers
        if len(mail) >= 5:
            block["all"] = profile(mail, [r for r in short if r.get("lang") == lang
                                          and r.get("kind") not in OTHER_KINDS])
        for kind in sorted({r.get("kind") for r in lr if r.get("kind")}):
            kr = [r for r in lr if r.get("kind") == kind]
            if len(kr) >= 5:
                block[kind] = profile(kr, [])
        if block:
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
    names = possible_names([r["body"] for r in good], out["by_language"])
    out["review"] = {
        "possible_names": names,
        "note": ("Capitalised words that also show up in signature_phrases, top_sentence_starters, "
                 "greetings or sign-offs. Ask the person which are clients, companies or people, "
                 "then run redact before this file goes into the personal skill."),
    }
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"wrote {args.output}: {len(good)} emails across {list(out['by_language'])}")
    print("possible names to review before redact: " + (", ".join(names) if names else "none found"))


# Capitalised words that are never a client: pronouns, days, months, common tools and roles.
COMMON_CAPS = set("""i i'm i'll i've i'd ok okay ps p.s ai ceo cto cmo coo cfo vp pm am b2b b2c saas crm
monday tuesday wednesday thursday friday saturday sunday mon tue wed thu fri sat sun
january february march april may june july august september october november december
lunedì martedì mercoledì giovedì venerdì sabato domenica gennaio febbraio marzo aprile maggio
giugno luglio agosto settembre ottobre novembre dicembre lunes martes miércoles jueves viernes
enero febrero abril mayo junio julio agosto septiembre octubre noviembre diciembre
linkedin google gmail outlook zoom teams slack notion chatgpt claude excel english italian
spanish french german italiano inglese""".split())


def fingerprint_texts(by_language):
    """Every phrase, sentence starter, greeting and sign-off string in a fingerprint."""
    for lang, block in by_language.items():
        for kind, prof in block.items():
            for key, field in (("signature_phrases", "phrase"), ("top_sentence_starters", "start"),
                               ("greetings", "value"), ("signoffs", "value")):
                for item in prof.get(key, []):
                    yield lang, kind, key, item, field


def possible_names(bodies, by_language):
    caps, lower = collections.Counter(), collections.Counter()
    for b in bodies:
        for sent in sentences(straighten(b)):
            ws = re.findall(r"[\wÀ-ÿ'-]+", sent)
            for i, w in enumerate(ws):
                lw = w.lower()
                if lw in COMMON_CAPS or len(w) < 3 or w.isdigit():
                    continue
                if i > 0 and (w[0].isupper()):
                    caps[lw] += 1
                elif w.islower():
                    lower[lw] += 1
    fp_words = set()
    for *_, item, field in fingerprint_texts(by_language):
        fp_words.update(re.findall(r"[\wÀ-ÿ'-]+", str(item.get(field, "")).lower()))
    return sorted(w for w, c in caps.items() if w in fp_words and lower[w] <= 0.25 * c)


# ---------------------------------------------------------------------------
# Redact a fingerprint before it goes into the personal skill

AUTO_REDACT = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[email]"),
    (re.compile(r"(https?://|www\.)\S+"), "[link]"),
    (re.compile(r"(?:[$€£]\s?\d[\d.,]*\s?[kKmM]?\b|\b\d[\d.,]*\s?(?:[kKmM]\b|€|eur\b|euro\b|usd\b|\$|dollars?\b))",
                re.IGNORECASE), "[amount]"),
    (re.compile(r"\+?\d[\d ()-]{7,}\d"), "[phone]"),
]


def cmd_redact(args):
    fp = json.load(open(args.input, encoding="utf-8"))
    terms = sorted({t.strip() for t in args.term if t.strip()}, key=len, reverse=True)
    term_res = [re.compile(r"(?<![\w])" + re.escape(straighten(t).lower()) + r"(?![\w])", re.IGNORECASE)
                for t in terms]
    drops = {straighten(d).strip().lower() for d in args.drop}
    changed, dropped = [], []
    for lang, block in fp.get("by_language", {}).items():
        for kind, prof in block.items():
            for key, field in (("signature_phrases", "phrase"), ("top_sentence_starters", "start"),
                               ("greetings", "value"), ("signoffs", "value")):
                keep = []
                for item in prof.get(key, []):
                    old = str(item.get(field, ""))
                    if straighten(old).strip().lower() in drops:
                        dropped.append(f"{lang}/{kind} {key}: {old}")
                        continue
                    new = straighten(old)
                    for rx, ph in AUTO_REDACT:
                        new = rx.sub(ph, new)
                    for rx in term_res:
                        new = rx.sub("[name]", new)
                    if new != old:
                        changed.append(f"{lang}/{kind} {key}: {old!r} -> {new!r}")
                        item[field] = new
                    keep.append(item)
                if key in prof:
                    prof[key] = keep
    review = fp.pop("review", {}) or {}
    left = [n for n in review.get("possible_names", [])
            if not any(rx.search(n) for rx in term_res)]
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(fp, fh, ensure_ascii=False, indent=2)
    print(f"wrote {args.output}: {len(changed)} entries redacted, {len(dropped)} dropped")
    for line in changed + [f"dropped {d}" for d in dropped]:
        print("  " + line)
    if left:
        print("possible names NOT redacted (confirm they are fine): " + ", ".join(left))
    print("\nWhat will go into the skill. Show this to the person and get a yes:")
    for lang, kind, key, item, field in fingerprint_texts(fp.get("by_language", {})):
        if kind == "all" and key in ("signature_phrases", "top_sentence_starters"):
            print(f"  {lang} {key}: {item.get(field)}")


# ---------------------------------------------------------------------------
# Draft check: AI tells plus distance from the person's own numbers

def pick_profile(fp, lang, kind):
    """Return (profile or None, warnings). Never silently compare against the wrong data."""
    warnings = []
    if not fp:
        return None, ["no --fingerprint given: only AI tells were checked, not your own numbers."]
    langs = fp.get("by_language", {})
    if lang not in langs:
        have = ", ".join(langs) or "none"
        return None, [f"no profile for language '{lang}' (the fingerprint has: {have}). Only AI tells "
                      f"were checked. Length, greeting, sign-off and punctuation were NOT checked. "
                      f"Compare by hand with examples.md, or pass --lang if the language was misread."]
    block = langs[lang]
    if kind and kind in block:
        return block[kind], warnings
    if kind in OTHER_KINDS:
        return None, [f"no '{kind}' numbers in the fingerprint, so email length, greeting and "
                      f"punctuation checks were skipped. Use the {kind} rules in formats.md instead."]
    if not block.get("all"):
        return None, [f"fewer than 5 {lang} emails in the fingerprint, so length, greeting and "
                      f"punctuation checks were skipped. Only AI tells were checked."]
    if kind:
        warnings.append(f"no '{kind}' profile in {lang} (fewer than 5 such emails), so this was "
                        f"compared against all your {lang} emails.")
    return block.get("all"), warnings


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
    score, verdict, reasons = score_one({"body": text}, base, draft=True)
    placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
    flat = straighten(text)                            # curly apostrophes count as contractions too
    notes = []
    lang = args.lang or detect_lang(text)
    p, warnings = pick_profile(fp, lang, args.kind)
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
        sl = [len(x.split()) for x in sentences(flat)]
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
        g, sgn = first_last_lines(flat)
        known_g = [x["value"] for x in p.get("greetings", [])]
        if g and known_g and g not in known_g:
            notes.append(f"greeting '{g}' isn't one you use. Yours: {', '.join(known_g[:3])}.")
        known_s = [x["value"] for x in p.get("signoffs", [])]
        if sgn and known_s and sgn not in known_s:
            notes.append(f"sign-off '{sgn}' isn't one you use. Yours: {', '.join(known_s[:3])}.")
        contr = len(CONTRACTION_RE.findall(flat))
        expd = len(EXPANDABLE_RE.findall(flat))
        if lang == "en" and expd >= 2 and p["contraction_rate"] >= 0.6 and contr / max(contr + expd, 1) < 0.5:
            notes.append("too formal: you normally use contractions (I'll, don't, it's).")
    if not notes:
        notes = ["none found"] if p else ["not checked: see warnings"]
    result = {"ai_score": score, "verdict": verdict, "ai_tells": reasons, "off_voice": notes}
    if warnings:
        result["warnings"] = warnings
    if placeholders:
        result["fill_in_before_sending"] = placeholders
    print(json.dumps(result, ensure_ascii=False, indent=2))
    for w in warnings:                                 # also say it in plain text, so it isn't missed
        print("WARNING: " + w, file=sys.stderr)


# ---------------------------------------------------------------------------
# Transcripts

FILLERS = ["um", "uh", "erm", "like", "you know", "i mean", "basically", "actually", "literally",
           "right?", "okay?", "ok?", "so", "kind of", "sort of", "to be honest", "honestly",
           "fundamentally", "at the end of the day", "et cetera"]
TS = r"\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d+)?"
# 'Name: text', '[00:01] Name: text', '00:01:02 - Name: text', 'Name (00:01): text'
INLINE_RE = re.compile(r"^\s*(?:[\[(]?" + TS + r"[\])]?\s*[-–]?\s*)?"
                       r"([^\s:<>\[\]()][^:<>\[\]()]{0,59}?)\s*(?:[\[(]" + TS + r"[\])])?\s*:\s*(.*)$")
VTT_VOICE_RE = re.compile(r"^\s*<v(?:\.[\w.-]+)?\s+([^>]+)>(.*)$")
# Otter and similar: 'Jane Doe  0:03' or 'Speaker 1  1:02:07' on its own line, text below.
HEADER_TS_RE = re.compile(r"^\s*([^\d:<>\[\]()][^:<>\[\]()]{0,59}?)\s+[\[(]?" + TS + r"[\])]?\s*$")
CUE_LINE_RE = re.compile(r"-->|^\s*\d+\s*$|^\s*[0-9a-f]{8}-[0-9a-f-]{20,}(?:/\d+-\d+)?\s*$|^\s*(WEBVTT|NOTE)\b",
                         re.IGNORECASE)
NOT_SPEAKER = set("""next note notes nota nb n.b ps p.s step steps subject oggetto asunto betreff objet re fwd
action actions agenda todo summary riassunto update question answer q example esempio important
importante warning tip recap takeaway takeaways key bottom result results goal goals problem
solution price prezzo budget timeline total totale date data time ora attenzione also and but then
poi quindi ok okay yes no si sì thanks thank grazie hello hi ciao bye perfect perfetto great right
sure exactly esatto step source link pros cons option opzione phase fase day giorno week settimana
call meeting""".split())
PARTICLES = {"de", "da", "di", "del", "della", "van", "von", "der", "den", "la", "le", "dos", "das",
             "du", "y", "e", "bin", "al", "ten", "ter"}


def name_like(label):
    """Does a label look like a speaker: a name, 'Speaker 2' or an email, not 'Next step'?"""
    s = label.strip()
    if re.fullmatch(r"(speaker|participant|unknown speaker|relatore|orador|sprecher|interlocutor)\s*\w{0,3}",
                    s, re.IGNORECASE):
        return True
    if re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.-]+", s):
        return True
    words = s.split()
    if not 1 <= len(words) <= 4 or words[0].lower().strip(".") in NOT_SPEAKER:
        return False
    return all(w.lower() in PARTICLES or (w[0].isupper() and re.fullmatch(r"[\w'’.-]+", w)) for w in words)


def read_text(path):
    """utf-8 (with or without BOM) first, then Windows/Latin-1, so accents survive."""
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")


def strip_tags(text):
    return re.sub(r"</?[a-zA-Z][^>]*>", "", text).strip()


def read_turns(path, wanted=()):
    """Parse 'Name: text', '[00:01] Name: text', VTT '<v Name>text</v>', SRT cues,
    Otter 'Name  0:03' headers and plain 'Name' header lines followed by text.

    A label only counts as a speaker if it looks like a name and is not a common
    sentence opener ('Next step:', 'Nota bene:'). A one-word label must recur in the file
    or be one of the wanted speakers. Bare 'Name' lines with no colon or timestamp only
    count in files with no 'Name: text' turns, where at least one of them recurs.
    """
    lines = read_text(path).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    wanted = {w.strip().lower() for w in wanted}
    parsed = []                                        # (kind, label, text) per line
    for i, line in enumerate(lines):
        if CUE_LINE_RE.search(line):
            parsed.append(("cue", None, None))
            continue
        m = VTT_VOICE_RE.match(line)
        if m:
            parsed.append(("voice", m.group(1).strip(), strip_tags(m.group(2))))
            continue
        m = HEADER_TS_RE.match(line)
        if m:
            parsed.append(("header", m.group(1).strip(), ""))
            continue
        m = INLINE_RE.match(line)
        if m:
            parsed.append(("inline", m.group(1).strip(), strip_tags(m.group(2))))
            continue
        prev_blank = i == 0 or not lines[i - 1].strip() or CUE_LINE_RE.search(lines[i - 1])
        if prev_blank and line.strip() and len(line.split()) <= 4 and not re.search(r"[.!?,;]\s*$", line):
            parsed.append(("bare", line.strip(), ""))
            continue
        parsed.append(("text", None, strip_tags(line)))
    counts = collections.Counter(lab.lower() for k, lab, _ in parsed if lab)

    def is_speaker(kind, label):
        low = label.lower()
        if kind == "voice" or low in wanted:
            return True
        if not name_like(label):
            return False
        return len(label.split()) > 1 or counts[low] >= 2

    has_inline = any(k in ("inline", "voice") and is_speaker(k, lab) for k, lab, _ in parsed)
    bare_format = not has_inline and any(k == "bare" and name_like(lab) and counts[lab.lower()] >= 2
                                         for k, lab, _ in parsed)
    turns, cur = [], None
    for (kind, label, text), line in zip(parsed, lines):
        if kind == "cue":
            continue
        if kind == "bare" and not bare_format:
            kind, text = "text", strip_tags(line)
        if kind in ("voice", "inline", "header", "bare") and is_speaker(kind, label):
            cur = [label, text or ""]
            turns.append(cur)
        elif cur and kind != "cue":
            t = text if kind == "text" else strip_tags(line)
            if t and t.strip():
                cur[1] += " " + t.strip()
    return [(s, t.strip()) for s, t in turns if t.strip()]


def cmd_transcript(args):
    paths = []
    for p in args.inputs:
        if os.path.isdir(p):
            paths += [os.path.join(p, f) for f in sorted(os.listdir(p))
                      if f.lower().endswith((".txt", ".vtt", ".srt", ".md"))]
        else:
            paths.append(p)
    want = {s.strip().lower() for s in args.speaker}   # exact label, any case: 'Speaker 1' is not 'Speaker 10'
    mine, others, per_call, labels = [], 0, [], collections.Counter()
    for p in paths:
        turns = read_turns(p, want)
        labels.update(s for s, _ in turns)
        me = [t for s, t in turns if s.strip().lower() in want]
        other_words = sum(len(t.split()) for s, t in turns if s.strip().lower() not in want)
        my_words = sum(len(t.split()) for t in me)
        per_call.append({"file": os.path.basename(p), "my_turns": len(me),
                         "talk_share": round(my_words / max(my_words + other_words, 1), 2)})
        mine += me
        others += other_words
    text = straighten(" ".join(mine))
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
        "signature_phrases": signature_phrases([straighten(t) for t in mine], lang_stop, top=60),
    }
    if not mine:
        found = ", ".join(f"'{s}'" for s, _ in labels.most_common(8)) or "none"
        out["warning"] = (f"No turns matched the speaker name. Speaker labels found: {found}. "
                          "Pass the person's exact label with --speaker (repeat it for several).")
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    if args.turns_out:
        with open(args.turns_out, "w", encoding="utf-8") as fh:
            fh.write("\n\n".join(mine))
    print(f"wrote {args.output}: {len(mine)} turns, {nwords if mine else 0} words from {len(paths)} files")
    if not mine:
        print("WARNING: " + out["warning"])


# ---------------------------------------------------------------------------

def write_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn, hlp in (("clean", cmd_clean, "strip quotes and signatures, drop templates and auto-replies"),
                          ("score", cmd_score, "score each cleaned email for AI writing"),
                          ("fingerprint", cmd_fingerprint, "measure the voice of the emails that passed")):
        p = sub.add_parser(name, help=hlp)
        p.add_argument("input")
        p.add_argument("-o", "--output", required=True)
        p.set_defaults(fn=fn)
    p = sub.add_parser("extract", help="read .mbox and .eml exports into the email JSONL")
    p.add_argument("inputs", nargs="+", help=".mbox files, .eml files, or folders of them")
    p.add_argument("-o", "--output", required=True)
    p.add_argument("--from", dest="sender", action="append", default=[],
                   help="keep only mail sent from this address (repeatable)")
    p.set_defaults(fn=cmd_extract)
    p = sub.add_parser("redact", help="replace names, companies, emails and amounts in a fingerprint")
    p.add_argument("input", help="fingerprint.json")
    p.add_argument("-o", "--output", required=True)
    p.add_argument("--term", action="append", default=[],
                   help="a client, company or person name to replace with [name] (repeatable)")
    p.add_argument("--drop", action="append", default=[],
                   help="a phrase, sentence starter, greeting or sign-off to remove entirely (repeatable)")
    p.set_defaults(fn=cmd_redact)
    p = sub.add_parser("check", help="check a draft for AI tells and off-voice numbers")
    p.add_argument("input", help="draft text file, or - for stdin")
    p.add_argument("--fingerprint", help="fingerprint.json from the voice profile")
    p.add_argument("--lang", help="language code; detected when omitted")
    p.add_argument("--kind", help="what the draft is: cold, followup, reply, new (email), or post, dm, comment")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("transcript", help="pull one speaker's turns out of call transcripts")
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
