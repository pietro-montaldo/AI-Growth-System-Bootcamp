#!/usr/bin/env python3
"""Clean, merge and check a do-not-contact list.

The list has these columns, in this order:
  Email, LinkedIn URL, Company domain, Scope, Reason, Until, Source, Added, Note

Standard library only, so it runs anywhere Python 3 does.

  dnc.py clean VALUE [VALUE ...]           show the matching key for an email, LinkedIn URL or website
  dnc.py normalize IN.csv -o OUT.csv        clean the keys and values of new rows
  dnc.py merge NEW.csv --existing LIST.csv -o ADD.csv
                                            keep only new rows that aren't on the list yet
  dnc.py keys LEADS.csv                     the cleaned keys of a lead list, as JSON (for a filtered query)
  dnc.py check LEADS.csv --list LIST.csv --out-dir DIR
                                            split a lead list into keep.csv and drop.csv
  dnc.py blocklist LIST.csv -o OUT.csv      emails and domains to upload to a sending tool

Rows with an Until date in the past are ignored by check and blocklist.
Use --today YYYY-MM-DD to test with another date.
"""
import argparse
import csv
import datetime
import json
import os
import re
import sys
from urllib.parse import unquote, urlsplit

COLUMNS = ["Email", "LinkedIn URL", "Company domain", "Scope", "Reason", "Until", "Source", "Added", "Note"]
KEYS = ["Email", "LinkedIn URL", "Company domain"]
REASONS = [
    "said no", "not now", "unsubscribed", "bounced", "customer", "open deal",
    "partner", "competitor", "personal", "erasure request", "other",
]
SOURCES = ["inbox", "CRM", "sequencer", "course platform", "LinkedIn", "manual", "other"]
SCOPES = ["person", "company"]

# Personal email providers. Their domains are never blocked company-wide.
FREE_MAIL = {
    "gmail.com", "googlemail.com", "icloud.com", "me.com", "mac.com", "aol.com", "msn.com",
    "live.com", "proton.me", "protonmail.com", "pm.me", "zoho.com", "fastmail.com", "hey.com",
    "web.de", "libero.it", "virgilio.it", "tiscali.it", "alice.it", "tin.it", "orange.fr",
    "free.fr", "laposte.net", "wanadoo.fr", "t-online.de", "mail.ru", "qq.com", "163.com",
    "126.com", "naver.com", "rediffmail.com", "btinternet.com", "comcast.net", "verizon.net",
}
FREE_MAIL_PREFIXES = ("yahoo.", "ymail.", "hotmail.", "outlook.", "gmx.", "yandex.")


# ---------- cleaning ----------

def clean_email(value):
    v = (value or "").strip().strip("<>").lower()
    if v.startswith("mailto:"):
        v = v[7:]
    v = v.split("?")[0].strip()
    if not v:
        return ""
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z0-9-]{2,}", v):
        raise ValueError(f"not an email: {value}")
    return v


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
    if len(path) >= 2 and path[0] in ("in", "pub", "company"):
        return f"linkedin.com/{path[0]}/{path[1]}"
    # Sales Navigator and other links can't be turned into a profile link. Keep the path.
    return "linkedin.com/" + "/".join(path)


def clean_domain(value):
    v = (value or "").strip().lower()
    if not v:
        return ""
    if "@" in v:
        v = v.split("@")[-1]
    if "://" not in v:
        v = "https://" + v
    host = urlsplit(v).netloc.split(":")[0].strip(".")
    if host.startswith("www."):
        host = host[4:]
    if "." not in host or not re.fullmatch(r"[a-z0-9.-]+", host):
        raise ValueError(f"not a domain: {value}")
    return host


def is_free_mail(domain):
    return domain in FREE_MAIL or domain.startswith(FREE_MAIL_PREFIXES)


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


def clean_row(row, today):
    """Return a cleaned list row, or raise ValueError with the reason."""
    out = {c: (row.get(c) or "").strip() for c in COLUMNS}
    out["Email"] = clean_email(out["Email"])
    out["LinkedIn URL"] = clean_linkedin(out["LinkedIn URL"])
    out["Company domain"] = clean_domain(out["Company domain"])
    out["Scope"] = pick(out["Scope"], SCOPES, "Scope")
    if not out["Scope"]:
        out["Scope"] = "person" if (out["Email"] or out["LinkedIn URL"]) else "company"
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
    until = (row.get("Until") or "").strip()[:10]
    return not until or until >= today


# ---------- files ----------

def read(path, schema=True):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = [c.strip() for c in (reader.fieldnames or [])]
        rows = [{(k or "").strip(): v for k, v in r.items()} for r in reader]
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


def list_index(rows, today):
    """Keys on the list: emails and LinkedIn URLs of person rows, domains of company rows."""
    index = {"Email": {}, "LinkedIn URL": {}, "Company domain": {}}
    for r in rows:
        if not active(r, today):
            continue
        scope = (r.get("Scope") or "").strip().lower() or "person"
        try:
            keys = {
                "Email": clean_email(r.get("Email")),
                "LinkedIn URL": clean_linkedin(r.get("LinkedIn URL")),
                "Company domain": clean_domain(r.get("Company domain")),
            }
        except ValueError:
            continue
        cols = ["Company domain"] if scope == "company" else ["Email", "LinkedIn URL"]
        for c in cols:
            if keys[c]:
                index[c].setdefault(keys[c], r)
    return index


def find(row, index):
    """Return (column, list row) for the first key of a cleaned row that is already listed."""
    cols = ["Company domain"] if row["Scope"] == "company" else ["Email", "LinkedIn URL"]
    for c in cols:
        if row[c] and row[c] in index[c]:
            return c, index[c][row[c]]
    return None, None


# ---------- lead lists ----------

def lead_columns(cols, args):
    """Find the email, LinkedIn and website columns of any lead list."""
    used = set()

    def guess(flag, words):
        if flag:
            if flag not in cols:
                sys.exit(f"no column called {flag}. Columns are: {', '.join(cols)}")
            used.add(flag)
            return flag
        free = [c for c in cols if c not in used]
        exact = [c for c in free if c.lower() in words]
        loose = [c for w in words for c in free if w in c.lower()]
        for c in exact + loose:
            used.add(c)
            return c
        return None
    found = {}
    found["LinkedIn URL"] = guess(args.linkedin_col, ["linkedin url", "linkedin", "profile url"])
    found["Email"] = guess(args.email_col, ["email", "work email", "e-mail", "mail"])
    found["Company domain"] = guess(args.domain_col, ["domain", "company domain", "website", "company url", "url"])
    return found


def lead_keys(row, found):
    keys = {}
    for c, col in found.items():
        raw = (row.get(col) or "") if col else ""
        try:
            keys[c] = {"Email": clean_email, "LinkedIn URL": clean_linkedin, "Company domain": clean_domain}[c](raw)
        except ValueError:
            keys[c] = ""
    if not keys["Company domain"] and keys["Email"]:
        keys["Company domain"] = clean_domain(keys["Email"])
    if keys["Company domain"] and is_free_mail(keys["Company domain"]):
        keys["Company domain"] = ""
    return keys


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
    add, listed, bad = [], 0, []
    for n, r in enumerate(new, start=2):
        try:
            row = clean_row(r, args.today)
        except ValueError as e:
            bad.append(f"line {n}: {e}")
            continue
        col, _ = find(row, index)
        if col:
            listed += 1
            continue
        add.append(row)
        for c in (["Company domain"] if row["Scope"] == "company" else ["Email", "LinkedIn URL"]):
            if row[c]:
                index[c][row[c]] = row
    write(args.out, COLUMNS, add)
    counts = {}
    for r in add:
        counts[r["Reason"]] = counts.get(r["Reason"], 0) + 1
    print(f"new {len(add)}, already listed {listed}, skipped {len(bad)}")
    for reason, k in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {reason}: {k}")
    for b in bad:
        print("  " + b)


def cmd_keys(args):
    cols, rows = read(args.file, schema=False)
    found = lead_columns(cols, args)
    if not any(found.values()):
        sys.exit("found no email, LinkedIn or website column. Name one with --email-col, --linkedin-col or --domain-col")
    out = {"columns": found, "Email": set(), "LinkedIn URL": set(), "Company domain": set()}
    for r in rows:
        for c, v in lead_keys(r, found).items():
            if v:
                out[c].add(v)
    print(json.dumps({k: sorted(v) if isinstance(v, set) else v for k, v in out.items()}, indent=2))


def cmd_check(args):
    cols, leads = read(args.file, schema=False)
    found = lead_columns(cols, args)
    if not any(found.values()):
        sys.exit("found no email, LinkedIn or website column. Name one with --email-col, --linkedin-col or --domain-col")
    _, listed = read(args.list)
    index = list_index(listed, args.today)
    keep, drop = [], []
    for r in leads:
        keys = lead_keys(r, found)
        hit = None
        for c in ("Email", "LinkedIn URL", "Company domain"):
            if keys[c] and keys[c] in index[c]:
                hit = (c, keys[c], index[c][keys[c]])
                break
        if hit:
            c, key, entry = hit
            drop.append({**r, "DNC reason": entry.get("Reason") or "other", "DNC match": f"{c}: {key}"})
        else:
            keep.append(r)
    write(os.path.join(args.out_dir, "keep.csv"), cols, keep)
    write(os.path.join(args.out_dir, "drop.csv"), cols + ["DNC reason", "DNC match"], drop)
    no_key = sum(1 for r in leads if not any(lead_keys(r, found).values()))
    reasons = {}
    for d in drop:
        reasons[d["DNC reason"]] = reasons.get(d["DNC reason"], 0) + 1
    print(json.dumps({
        "leads": len(leads), "keep": len(keep), "drop": len(drop),
        "drop_by_reason": reasons, "leads_without_any_key": no_key, "columns_used": found,
    }, indent=2))


def cmd_blocklist(args):
    _, rows = read(args.file)
    index = list_index(rows, args.today)
    items = sorted(index["Email"]) + sorted(index["Company domain"])
    write(args.out, ["Blocklist"], [{"Blocklist": i} for i in items])
    linkedin_only = sum(1 for k, r in index["LinkedIn URL"].items() if not (r.get("Email") or "").strip())
    print(f"wrote {len(index['Email'])} email(s) and {len(index['Company domain'])} domain(s) to {args.out}")
    if linkedin_only:
        print(f"{linkedin_only} LinkedIn-only row(s) can't go in an email blocklist. They are still checked by check.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--today", default=datetime.date.today().isoformat(), help=argparse.SUPPRESS)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("clean")
    s.add_argument("values", nargs="+")

    s = sub.add_parser("normalize")
    s.add_argument("file")
    s.add_argument("-o", "--out", required=True)

    s = sub.add_parser("merge")
    s.add_argument("file")
    s.add_argument("--existing", help="the current list, or its key columns (leave out for a new list)")
    s.add_argument("-o", "--out", required=True)

    for name in ("keys", "check"):
        s = sub.add_parser(name)
        s.add_argument("file")
        s.add_argument("--email-col")
        s.add_argument("--linkedin-col")
        s.add_argument("--domain-col")
    sub.choices["check"].add_argument("--list", required=True)
    sub.choices["check"].add_argument("--out-dir", required=True)

    s = sub.add_parser("blocklist")
    s.add_argument("file")
    s.add_argument("-o", "--out", required=True)

    args = p.parse_args()
    {
        "clean": cmd_clean, "normalize": cmd_normalize, "merge": cmd_merge,
        "keys": cmd_keys, "check": cmd_check, "blocklist": cmd_blocklist,
    }[args.command](args)


if __name__ == "__main__":
    main()
