#!/usr/bin/env python3
"""Clean, merge and check a do-not-contact list.

The list has these columns, in this order:
  Email, LinkedIn URL, Company domain, Scope, Reason, Until, Source, Added, Note

Standard library only, so it runs anywhere Python 3 does.

  dnc.py clean VALUE [VALUE ...]           show the matching key for an email, LinkedIn URL or website
  dnc.py normalize IN.csv -o OUT.csv        clean the keys and values of new rows
  dnc.py merge NEW.csv --existing LIST.csv -o ADD.csv
                                            keep only new rows the list doesn't already cover
  dnc.py keys LEADS.csv                     the cleaned keys of a lead list, as JSON (for a filtered query)
  dnc.py check LEADS.csv --list LIST.csv --out-dir DIR
                                            split a lead list into keep.csv and drop.csv
  dnc.py blocklist LIST.csv -o OUT.csv      emails and domains to upload to a sending tool

Files can be CSV (comma, semicolon or tab, UTF-8 or Windows/Excel encoding)
or the JSON a connector returns: Google Sheets get_values ("values", first row
is the header) or Notion query results (a list of rows).

Rows with an Until date in the past are ignored by check and blocklist.
Use --today YYYY-MM-DD to test with another date.
"""
import argparse
import csv
import datetime
import io
import json
import os
import re
import sys
from urllib.parse import unquote, urlsplit

COLUMNS = ["Email", "LinkedIn URL", "Company domain", "Scope", "Reason", "Until", "Source", "Added", "Note"]
KEYS = ["Email", "LinkedIn URL", "Company domain"]
# Strongest first. When one key has several rows, the strongest one counts.
# agents/dnc-collector.md (rule 5) repeats this order. Change both together.
REASONS = [
    "erasure request", "unsubscribed", "said no", "bounced", "customer", "open deal",
    "partner", "competitor", "personal", "not now", "other",
]
SOURCES = ["inbox", "CRM", "sequencer", "course platform", "LinkedIn", "manual", "other"]
SCOPES = ["person", "company"]
# Notion returns date columns under these names unless the query renames them.
ALIASES = {"date:Until:start": "Until", "date:Added:start": "Added"}

# Personal email providers. Their domains are never blocked company-wide.
FREE_MAIL = {
    # global
    "gmail.com", "googlemail.com", "icloud.com", "me.com", "mac.com", "aim.com", "aol.com",
    "msn.com", "proton.me", "protonmail.com", "protonmail.ch", "pm.me", "zoho.com", "zohomail.com",
    "fastmail.com", "fastmail.fm", "hey.com", "tutanota.com", "tutanota.de", "tuta.io", "tutamail.com",
    "rocketmail.com", "mail.com", "email.com", "usa.com", "post.com", "inbox.com", "lycos.com",
    "hushmail.com", "duck.com", "mailbox.org", "gmx.com", "yandex.com", "ya.ru",
    # North America
    "att.net", "sbcglobal.net", "bellsouth.net", "comcast.net", "verizon.net", "cox.net",
    "charter.net", "earthlink.net", "optonline.net", "juno.com", "shaw.ca", "rogers.com",
    "sympatico.ca", "videotron.ca",
    # UK and Ireland
    "btinternet.com", "sky.com", "virginmedia.com", "ntlworld.com", "talktalk.net",
    "blueyonder.co.uk", "eircom.net",
    # Germany, Austria, Switzerland
    "web.de", "t-online.de", "freenet.de", "arcor.de", "posteo.de", "posteo.net",
    "bluewin.ch", "hispeed.ch", "gmx.ch", "chello.at",
    # Italy
    "libero.it", "virgilio.it", "tiscali.it", "alice.it", "tin.it", "email.it", "inwind.it",
    "fastwebnet.it", "tim.it",
    # France, Belgium, Netherlands
    "orange.fr", "free.fr", "laposte.net", "wanadoo.fr", "sfr.fr", "neuf.fr", "bbox.fr",
    "telenet.be", "skynet.be", "kpnmail.nl", "ziggo.nl", "planet.nl", "xs4all.nl", "home.nl",
    # Spain, Portugal, Latin America
    "telefonica.net", "terra.es", "terra.com.br", "uol.com.br", "bol.com.br", "sapo.pt",
    # Central and Eastern Europe
    "seznam.cz", "centrum.cz", "wp.pl", "o2.pl", "onet.pl", "interia.pl", "op.pl",
    "mail.ru", "bk.ru", "inbox.ru", "list.ru", "rambler.ru", "ukr.net",
    # Asia and Pacific
    "qq.com", "foxmail.com", "163.com", "126.com", "yeah.net", "sina.com", "sohu.com",
    "naver.com", "daum.net", "hanmail.net", "rediffmail.com", "bigpond.com",
    "optusnet.com.au",
}
# Providers with one domain per country, for example hotmail.co.uk or yahoo.com.br.
FREE_MAIL_NAMES = ("yahoo", "ymail", "hotmail", "outlook", "live", "msn", "windowslive", "aol", "gmx", "yandex", "mail")
FREE_MAIL_COUNTRY = re.compile(r"(" + "|".join(FREE_MAIL_NAMES) + r")\.[a-z]{2,3}(\.[a-z]{2})?")
# Gmail ignores dots in the name. Everyone ignores +tags.
DOTLESS = {"gmail.com", "googlemail.com"}


# ---------- cleaning ----------

def clean_domain(value):
    v = (value or "").strip().lower()
    if not v:
        return ""
    if "@" in v:
        v = v.split("@")[-1]
    if "://" not in v:
        v = "https://" + v
    try:
        host = urlsplit(v).netloc.split(":")[0].strip(".")
    except ValueError:
        raise ValueError(f"not a domain: {value}")
    if host.startswith("www."):
        host = host[4:]
    # Domains with accents (münchen.de) are kept in their ASCII form (xn--mnchen-3ya.de),
    # the one sending tools use, so both spellings match.
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        raise ValueError(f"not a domain: {value}")
    if "." not in host or not re.fullmatch(r"[a-z0-9-]+(\.[a-z0-9-]+)+", host):
        raise ValueError(f"not a domain: {value}")
    return host


def clean_email(value):
    v = (value or "").strip().strip("<>").lower()
    if v.startswith("mailto:"):
        v = v[7:]
    v = v.split("?")[0].strip()
    if not v:
        return ""
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s.]{2,}", v):
        raise ValueError(f"not an email: {value}")
    name, domain = v.rsplit("@", 1)
    try:
        return name + "@" + clean_domain(domain)
    except ValueError:
        raise ValueError(f"not an email: {value}")


def clean_linkedin(value):
    v = (value or "").strip()
    if not v:
        return ""
    if "://" not in v:
        v = "https://" + v
    parts = urlsplit(v)
    host = parts.netloc.lower().split(":")[0]
    if not (host == "linkedin.com" or host.endswith(".linkedin.com")):
        raise ValueError(f"not a LinkedIn URL: {value}")
    path = [p for p in unquote(parts.path).lower().split("/") if p]
    if not path or (path[0] in ("in", "pub", "company") and len(path) < 2):
        raise ValueError(f"not a LinkedIn profile link: {value}")
    if path[0] == "pub":
        # Old public links: /pub/jane-doe/12/345/678. The numbers are part of who it is.
        return "linkedin.com/" + "/".join(path[:5])
    if path[0] in ("in", "company"):
        return f"linkedin.com/{path[0]}/{path[1]}"
    # Sales Navigator and other links can't be turned into a profile link. Keep the path.
    return "linkedin.com/" + "/".join(path)


def match_email(email):
    """The form two emails are compared in: no +tag, and no dots for Gmail.
    The list keeps the email as written. Only matching uses this form."""
    if not email:
        return ""
    name, domain = email.rsplit("@", 1)
    name = name.split("+")[0] or name
    if domain in DOTLESS:
        name, domain = name.replace(".", ""), "gmail.com"
    return name + "@" + domain


def match_key(column, key):
    return match_email(key) if column == "Email" else key


def parent_domains(domain):
    """eu.customer.io, then customer.io. A company block covers its subdomains."""
    labels = domain.split(".")
    return [".".join(labels[i:]) for i in range(len(labels) - 1)]


def is_free_mail(domain):
    return domain in FREE_MAIL or bool(FREE_MAIL_COUNTRY.fullmatch(domain or ""))


def clean_value(value):
    """Guess what a value is and return its key, for the clean command."""
    v = value.strip()
    if "linkedin.com" in v.lower():
        return "LinkedIn URL", clean_linkedin(v)
    if "@" in v:
        return "Email", clean_email(v)
    return "Company domain", clean_domain(v)


def pick(value, allowed, column):
    v = (value or "").strip()
    if not v:
        return ""
    for a in allowed:
        if v.lower() == a.lower():
            return a
    raise ValueError(f"{column} must be one of: {', '.join(allowed)}. Got: {value}")


def clean_date(value, column):
    v = (value or "").strip()
    if not v:
        return ""
    try:
        return datetime.date.fromisoformat(v[:10]).isoformat()
    except ValueError:
        raise ValueError(f"{column} must be a date like 2026-12-31. Got: {value}")


def default_scope(keys):
    """A blank Scope: person when there is an email or LinkedIn URL, otherwise company."""
    return "person" if (keys.get("Email") or keys.get("LinkedIn URL")) else "company"


def scope_columns(scope):
    return ["Company domain"] if scope == "company" else ["Email", "LinkedIn URL"]


def clean_row(row, today):
    """Return a cleaned list row, or raise ValueError with the reason."""
    out = {c: (row.get(c) or "").strip() for c in COLUMNS}
    out["Email"] = clean_email(out["Email"])
    out["LinkedIn URL"] = clean_linkedin(out["LinkedIn URL"])
    out["Company domain"] = clean_domain(out["Company domain"])
    out["Scope"] = pick(out["Scope"], SCOPES, "Scope") or default_scope(out)
    if out["Scope"] == "person" and not (out["Email"] or out["LinkedIn URL"]):
        raise ValueError("a person row needs an Email or a LinkedIn URL")
    if out["Scope"] == "company":
        if not out["Company domain"] and out["Email"]:
            out["Company domain"] = clean_domain(out["Email"])
        if not out["Company domain"]:
            raise ValueError("a company row needs a Company domain")
        if is_free_mail(out["Company domain"]):
            raise ValueError(f"{out['Company domain']} is a personal email provider, it can't be blocked company-wide")
    out["Reason"] = pick(out["Reason"], REASONS, "Reason") or "other"
    out["Source"] = pick(out["Source"], SOURCES, "Source") or "manual"
    out["Until"] = clean_date(out["Until"], "Until")
    out["Added"] = clean_date(out["Added"], "Added") or today
    out["Note"] = " ".join(out["Note"].split())[:120]
    return out


def active(row, today):
    """False only for a readable Until date in the past. An unreadable date keeps blocking."""
    until = (row.get("Until") or "").strip()
    if not until:
        return True
    try:
        return datetime.date.fromisoformat(until[:10]).isoformat() >= today
    except ValueError:
        return True


def strength(row):
    """Smaller is stronger: the reason first, then no Until (forever) before a late Until before an early one."""
    reason = (row.get("Reason") or "").strip().lower()
    rank = REASONS.index(reason) if reason in REASONS else len(REASONS)
    try:
        until = datetime.date.fromisoformat((row.get("Until") or "").strip()[:10])
        return (rank, 1, -until.toordinal())
    except ValueError:
        return (rank, 0, 0)  # blank or unreadable: blocks forever


def unreadable_until(rows):
    n = 0
    for r in rows:
        until = (r.get("Until") or "").strip()
        if until:
            try:
                datetime.date.fromisoformat(until[:10])
            except ValueError:
                n += 1
    return n


# ---------- files ----------

def json_table(data):
    """Turn a connector's JSON output into (columns, rows)."""
    # A tool result saved as content blocks: [{"type": "text", "text": "<json>"}]
    if isinstance(data, list) and data and all(isinstance(b, dict) and "text" in b for b in data):
        return json_table(json.loads("".join(b["text"] for b in data)))
    if isinstance(data, dict):
        if "values" in data:
            return json_table(data["values"])
        if data.get("valueRanges"):
            return json_table(data["valueRanges"][0].get("values", []))
        for k in ("results", "rows", "data"):
            if isinstance(data.get(k), list):
                return json_table(data[k])
        raise ValueError("no \"values\" or \"results\" in the JSON")
    if not isinstance(data, list):
        raise ValueError("expected a list of rows")
    if not data:
        return [], []
    if all(isinstance(r, list) for r in data):
        # Google Sheets get_values: the first row is the header. Rows can be shorter than it.
        cols = [str(c) for c in data[0]]
        rows = [{c: (str(r[i]) if i < len(r) and r[i] is not None else "") for i, c in enumerate(cols)} for r in data[1:]]
        return cols, rows
    if all(isinstance(r, dict) for r in data):
        # Notion query results: one object per row, sometimes under "properties".
        rows = [r.get("properties", r) if isinstance(r.get("properties"), dict) else r for r in data]
        cols = []
        for r in rows:
            cols += [c for c in r if c not in cols]
        return cols, [{c: ("" if r.get(c) is None else str(r.get(c))) for c in cols} for r in rows]
    raise ValueError("expected rows as lists or objects")


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1")


def read(path, schema=True):
    text = read_text(path)
    if path.lower().endswith(".json") or text.lstrip()[:1] in ("{", "["):
        try:
            cols, rows = json_table(json.loads(text))
        except ValueError as e:
            sys.exit(f"{path}: can't read this JSON: {e}")
    else:
        first = text.split("\n", 1)[0]
        delimiter = max([",", ";", "\t"], key=first.count)
        reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=delimiter)
        cols = reader.fieldnames or []
        rows = [{(k or "").strip(): v for k, v in r.items()} for r in reader]
    cols = [ALIASES.get(c.strip(), c.strip()) for c in cols]
    rows = [{ALIASES.get(k, k): (v if isinstance(v, str) else "") for k, v in r.items()} for r in rows]
    if schema:
        unknown = [c for c in cols if c not in COLUMNS + ["Entry"]]  # Entry: Notion's title column
        if unknown:
            sys.exit(f"{path}: unknown column(s): {', '.join(unknown)}. Columns are: {', '.join(COLUMNS)}")
        if not any(c in cols for c in KEYS):
            sys.exit(f"{path}: needs at least one of: {', '.join(KEYS)}")
    return cols, rows


def write(path, cols, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


def list_keys(r):
    """The keys one list row blocks, as {column: cleaned key}. Same rules as clean_row,
    but a bad value only loses that key, so one typo never hides the rest of the row."""
    keys = {}
    for c, fn in (("Email", clean_email), ("LinkedIn URL", clean_linkedin), ("Company domain", clean_domain)):
        try:
            keys[c] = fn(r.get(c))
        except ValueError:
            keys[c] = ""
    scope = (r.get("Scope") or "").strip().lower()
    if scope not in SCOPES:
        scope = default_scope(keys)
    if scope == "company" and not keys["Company domain"] and keys["Email"]:
        keys["Company domain"] = clean_domain(keys["Email"])
    if scope == "company" and is_free_mail(keys["Company domain"]):
        return {}  # never block a personal email provider
    return {c: keys[c] for c in scope_columns(scope) if keys[c]}


def list_index(rows, today):
    """Keys on the list: emails and LinkedIn URLs of person rows, domains of company rows.
    Each key points to its strongest active row."""
    index = {"Email": {}, "LinkedIn URL": {}, "Company domain": {}}
    for r in rows:
        if not active(r, today):
            continue
        for c, key in list_keys(r).items():
            k = match_key(c, key)
            if k not in index[c] or strength(r) < strength(index[c][k]):
                index[c][k] = r
    return index


def list_rows_not_used(rows):
    """Rows that block nothing: no readable key, or a company row on a personal email provider."""
    return sum(1 for r in rows if not list_keys(r))


# ---------- lead lists ----------

LOOKS_LIKE = {
    "Email": lambda v: "@" in v and bool(clean_email(v)),
    "LinkedIn URL": lambda v: clean_linkedin(v).startswith(("linkedin.com/in/", "linkedin.com/pub/", "linkedin.com/sales/")),
    "Company domain": lambda v: "@" not in v and "linkedin.com" not in v.lower() and bool(clean_domain(v)),
}


def looks_right(rows, col, column, sample=50):
    """True when at least half of a column's first filled values are the right kind of key."""
    values = [(r.get(col) or "").strip() for r in rows]
    values = [v for v in values if v][:sample]
    good = 0
    for v in values:
        try:
            good += bool(LOOKS_LIKE[column](v))
        except ValueError:
            pass
    return bool(values) and good * 2 >= len(values)


def lead_columns(cols, rows, args):
    """Find the email, LinkedIn and website columns of any lead list."""
    used = set()

    def guess(flag, column, words):
        if flag:
            if flag not in cols:
                sys.exit(f"no column called {flag}. Columns are: {', '.join(cols)}")
            used.add(flag)
            return flag
        free = [c for c in cols if c not in used]
        # 1. a header that is exactly one of the words, 2. a header that contains one
        # and holds the right kind of values, 3. any column that holds them.
        exact = [c for w in words for c in free if c.lower().strip() == w]
        loose = [c for w in words for c in free if w in c.lower() and looks_right(rows, c, column)]
        anywhere = [c for c in free if looks_right(rows, c, column)]
        for c in exact + loose + anywhere:
            used.add(c)
            return c
        return None
    found = {}
    found["LinkedIn URL"] = guess(args.linkedin_col, "LinkedIn URL", ["linkedin url", "linkedin", "linkedin profile", "profile url"])
    found["Email"] = guess(args.email_col, "Email", ["email", "email address", "work email", "e-mail", "mail"])
    found["Company domain"] = guess(args.domain_col, "Company domain", ["company domain", "domain", "website", "company website", "company url", "url"])
    return found


def lead_keys(row, found):
    """Return (keys, problem). problem says why a filled value couldn't be read."""
    keys, problems = {}, []
    for c, col in found.items():
        raw = (row.get(col) or "").strip() if col else ""
        try:
            keys[c] = {"Email": clean_email, "LinkedIn URL": clean_linkedin, "Company domain": clean_domain}[c](raw)
        except ValueError:
            keys[c] = ""
            problems.append(f"can't read {c} '{raw[:60]}'")
    if not keys["Company domain"] and keys["Email"]:
        keys["Company domain"] = keys["Email"].rsplit("@", 1)[1]
    if keys["Company domain"] and is_free_mail(keys["Company domain"]):
        keys["Company domain"] = ""
    return keys, "; ".join(problems)


def covering(index, column, key):
    """Return (listed key, list row) for the row that covers a key, or (None, None).
    Emails match in their matching form. A domain is covered by itself or a parent,
    and the strongest of those rows counts."""
    if not key:
        return None, None
    found = [(k, index[column][k]) for k in (parent_domains(key) if column == "Company domain" else [match_key(column, key)])
             if k in index[column]]
    return min(found, key=lambda f: strength(f[1])) if found else (None, None)


def lead_hit(keys, index):
    """Return (column, key, list row) for the strongest list row that covers this lead, or None."""
    hits = []
    for c in KEYS:
        k, entry = covering(index, c, keys[c])
        if entry:
            hits.append((c, k if c == "Company domain" else keys[c], entry))
    return min(hits, key=lambda h: strength(h[2])) if hits else None


# ---------- commands ----------

def cmd_clean(args):
    for v in args.values:
        try:
            col, key = clean_value(v)
            print(f"{col}: {key}")
        except ValueError as e:
            print(f"error: {e}")


def cmd_normalize(args):
    _, rows = read(args.file)
    good, bad = [], []
    for n, r in enumerate(rows, start=2):
        try:
            good.append(clean_row(r, args.today))
        except ValueError as e:
            bad.append(f"line {n}: {e}")
    write(args.out, COLUMNS, good)
    print(f"cleaned {len(good)} row(s), skipped {len(bad)}")
    for b in bad:
        print("  " + b)


def cmd_merge(args):
    _, new = read(args.file)
    _, existing = read(args.existing) if args.existing else ([], [])
    # Expired "not now" rows don't block a new row for the same person.
    index = list_index(existing, args.today)
    add, kinds, listed, bad = [], {"new": 0, "stronger reason": 0, "new keys": 0}, 0, []
    for n, r in enumerate(new, start=2):
        try:
            row = clean_row(r, args.today)
        except ValueError as e:
            bad.append(f"line {n}: {e}")
            continue
        if not active(row, args.today):
            bad.append(f"line {n}: Until {row['Until']} has already passed, so it would block no one")
            continue
        keys = {c: match_key(c, row[c]) for c in scope_columns(row["Scope"]) if row[c]}
        covered = {c: covering(index, c, row[c])[1] for c in keys}
        missing = [c for c in keys if not covered[c]]
        stronger = [c for c in keys if covered[c] and strength(row) < strength(covered[c])]
        if len(missing) == len(keys):
            kind = "new"
        elif stronger:
            kind = "stronger reason"  # for example unsubscribed after "not now": add it, rows are never deleted
        elif missing:
            kind = "new keys"  # a listed person with an email or profile link the list doesn't have yet
        else:
            listed += 1
            continue
        kinds[kind] += 1
        add.append(row)
        for c in missing + stronger:
            index[c][keys[c]] = row
    write(args.out, COLUMNS, add)
    counts = {}
    for r in add:
        counts[r["Reason"]] = counts.get(r["Reason"], 0) + 1
    print(f"to add {len(add)} (new {kinds['new']}, stronger reason {kinds['stronger reason']}, "
          f"new keys {kinds['new keys']}), already listed {listed}, skipped {len(bad)}")
    for reason, k in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {reason}: {k}")
    for b in bad:
        print("  " + b)


def cmd_keys(args):
    cols, rows = read(args.file, schema=False)
    found = lead_columns(cols, rows, args)
    if not any(found.values()):
        sys.exit("found no email, LinkedIn or website column. Name one with --email-col, --linkedin-col or --domain-col")
    out = {"columns": found, "Email": set(), "LinkedIn URL": set(), "Company domain": set()}
    for r in rows:
        keys, _ = lead_keys(r, found)
        if keys["Email"]:
            # The email as written and its matching form, so a filtered query finds either.
            out["Email"].update({keys["Email"], match_email(keys["Email"])})
        if keys["LinkedIn URL"]:
            out["LinkedIn URL"].add(keys["LinkedIn URL"])
        if keys["Company domain"]:
            # The domain and its parents: a block on customer.io covers eu.customer.io.
            out["Company domain"].update(parent_domains(keys["Company domain"]))
    print(json.dumps({k: sorted(v) if isinstance(v, set) else v for k, v in out.items()}, indent=2))


def cmd_check(args):
    cols, leads = read(args.file, schema=False)
    found = lead_columns(cols, leads, args)
    if not any(found.values()):
        sys.exit("found no email, LinkedIn or website column. Name one with --email-col, --linkedin-col or --domain-col")
    _, listed = read(args.list)
    index = list_index(listed, args.today)
    keep, drop, unchecked = [], [], 0
    for r in leads:
        keys, problem = lead_keys(r, found)
        hit = lead_hit(keys, index)
        if hit:
            c, key, entry = hit
            drop.append({**r, "DNC reason": entry.get("Reason") or "other", "DNC match": f"{c}: {key}"})
        elif not any(keys.values()):
            unchecked += 1
            keep.append({**r, "DNC check": "unchecked: " + (problem or "no email, LinkedIn or website")})
        else:
            keep.append({**r, "DNC check": ""})
    extra = [c for c in ("DNC check",) if c not in cols]
    write(os.path.join(args.out_dir, "keep.csv"), cols + extra, keep)
    write(os.path.join(args.out_dir, "drop.csv"), cols + ["DNC reason", "DNC match"], drop)
    reasons = {}
    for d in drop:
        reasons[d["DNC reason"]] = reasons.get(d["DNC reason"], 0) + 1
    print(json.dumps({
        "leads": len(leads), "keep": len(keep), "drop": len(drop), "unchecked": unchecked,
        "drop_by_reason": reasons, "columns_used": found,
        "list_rows_with_unreadable_until": unreadable_until(listed),
        "list_rows_not_used": list_rows_not_used(listed),
    }, indent=2))


def cmd_blocklist(args):
    _, rows = read(args.file)
    emails, domains, linkedin_only = set(), set(), 0
    for r in rows:
        if not active(r, args.today):
            continue
        keys = list_keys(r)
        if keys.get("Email"):
            emails.add(keys["Email"])
        if keys.get("Company domain"):
            domains.add(keys["Company domain"])
        if keys.get("LinkedIn URL") and not keys.get("Email"):
            linkedin_only += 1
    items = sorted(emails) + sorted(domains)
    write(args.out, ["Blocklist"], [{"Blocklist": i} for i in items])
    print(f"wrote {len(emails)} email(s) and {len(domains)} domain(s) to {args.out}")
    if linkedin_only:
        print(f"{linkedin_only} LinkedIn-only row(s) can't go in an email blocklist. They are still checked by check.")
    not_used = list_rows_not_used(rows)
    if not_used:
        print(f"{not_used} row(s) block nothing: no readable key, or a company block on a personal email provider.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--today", default=datetime.date.today().isoformat(), help=argparse.SUPPRESS)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("clean", help="show the matching key for a value")
    s.add_argument("values", nargs="+")

    s = sub.add_parser("normalize", help="clean the keys and values of new rows")
    s.add_argument("file")
    s.add_argument("-o", "--out", required=True)

    s = sub.add_parser("merge", help="keep only new rows the list doesn't already cover")
    s.add_argument("file")
    s.add_argument("--existing", help="the current list's key columns, as CSV or the connector's JSON (leave out for a new list)")
    s.add_argument("-o", "--out", required=True)

    for name, text in (("keys", "the cleaned keys of a lead list, as JSON"), ("check", "split a lead list into keep.csv and drop.csv")):
        s = sub.add_parser(name, help=text)
        s.add_argument("file")
        s.add_argument("--email-col")
        s.add_argument("--linkedin-col")
        s.add_argument("--domain-col")
    sub.choices["check"].add_argument("--list", required=True, help="the list's key columns, as CSV or the connector's JSON")
    sub.choices["check"].add_argument("--out-dir", required=True)

    s = sub.add_parser("blocklist", help="emails and domains to upload to a sending tool")
    s.add_argument("file")
    s.add_argument("-o", "--out", required=True)

    args = p.parse_args()
    {
        "clean": cmd_clean, "normalize": cmd_normalize, "merge": cmd_merge,
        "keys": cmd_keys, "check": cmd_check, "blocklist": cmd_blocklist,
    }[args.command](args)


if __name__ == "__main__":
    main()
