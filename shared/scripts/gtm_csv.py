#!/usr/bin/env python3
"""Read and update the GTM context CSV banks (customers, objections, competitors).

Read only the rows you need, and change rows without breaking the file.
Standard library only, so it runs anywhere Python 3 does.

  gtm_csv.py init FILE --cols "Company,Website,Size"
  gtm_csv.py add-cols FILE --cols "Offer,Seniority"   add missing columns, empty, keep every row
  gtm_csv.py query FILE [filters] [--cols A,B] [--limit N]
  gtm_csv.py count FILE --by COL [filters]
  gtm_csv.py upsert FILE --key COL[,COL | COL|COL] [--merge COL] (--row '{"Company": "Acme"}' | --rows rows.json)

upsert: a row matches when every key column matches (ignoring case), so
--key "Objection,Offer" keeps the same objection about two offers apart.
--key "Email|LinkedIn URL|Customer" tries each column in turn (that the new
row has a value for) and takes the first match. A matched row keeps its
values in those columns; empty ones are filled in.
--merge "Offer" adds new "; " values to the cell instead of replacing it.
JSON null is written as an empty cell, true/false as yes/no, a list as "a; b".

Filters (combine as many as needed, all must match, case-insensitive):
  --where COL=VALUE        exact match
  --contains COL=TEXT      text appears in the cell
  --any COL=V1|V2|V3       exact match on any of the values
  --min COL=NUMBER         number in the cell is at least NUMBER (a blank or
                           non-numeric cell doesn't match)
"""
import argparse
import csv
import json
import os
import sys


def read(path):
    if not os.path.isfile(path):
        sys.exit(f"{path} doesn't exist. Create it first with: init {path} --cols \"...\"")
    # utf-8-sig drops the byte-order mark Excel adds, so the first column keeps its name.
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def write(path, cols, rows):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


def split(pair, flag):
    if "=" not in pair:
        sys.exit(f"{flag} needs COL=VALUE, got: {pair}")
    col, value = pair.split("=", 1)
    return col.strip(), value.strip()


def names(text):
    """Split "A, B,A" into ["A", "B"]: trimmed, no blanks, no repeats."""
    out = []
    for c in text.split(","):
        c = c.strip()
        if c and c not in out:
            out.append(c)
    return out


def cell_text(v):
    """Turn a JSON value into cell text: null -> "", true/false -> yes/no, list -> "a; b"."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, list):
        return "; ".join(cell_text(x) for x in v if cell_text(x))
    return str(v)


def check_cols(cols, wanted):
    missing = [c for c in wanted if c not in cols]
    if missing:
        sys.exit(f"unknown column(s): {', '.join(missing)}. Columns are: {', '.join(cols)}")


def matches(row, args):
    cell = lambda c: (row.get(c) or "").strip().lower()
    for col, value in (split(p, "--where") for p in args.where):
        if cell(col) != value.lower():
            return False
    for col, text in (split(p, "--contains") for p in args.contains):
        if text.lower() not in cell(col):
            return False
    for col, values in (split(p, "--any") for p in args.any):
        if cell(col) not in [v.strip().lower() for v in values.split("|")]:
            return False
    for col, number in (split(p, "--min") for p in args.min):
        try:
            limit = float(number)
        except ValueError:
            sys.exit(f"--min needs a number, got: {number}")
        try:
            value = float(cell(col))
        except ValueError:
            return False  # blank or not a number: it doesn't meet the minimum
        if value != value or value < limit:  # value != value catches "nan"
            return False
    return True


def filter_cols(args):
    return [split(p, "")[0] for p in args.where + args.contains + args.any + args.min]


def cmd_init(args):
    if os.path.exists(args.file):
        sys.exit(f"{args.file} already exists, not overwriting")
    cols = names(args.cols)
    if not cols:
        sys.exit("--cols needs at least one column")
    write(args.file, cols, [])
    print(f"created {args.file}")


def cmd_add_cols(args):
    cols, rows = read(args.file)
    new = [c for c in names(args.cols) if c not in cols]
    if not new:
        print("no new columns")
        return
    write(args.file, cols + new, rows)
    print(f"added {', '.join(new)} to {args.file}")


def cmd_query(args):
    cols, rows = read(args.file)
    check_cols(cols, filter_cols(args))
    show = names(args.cols) if args.cols else cols
    check_cols(cols, show)
    if args.limit is not None and args.limit < 0:
        sys.exit("--limit can't be negative")
    hits = [r for r in rows if matches(r, args)]
    print(f"{len(hits)} of {len(rows)} rows match")
    if args.limit is not None:
        hits = hits[: args.limit]
    if not hits:
        return
    print("| " + " | ".join(show) + " |")
    print("|" + "---|" * len(show))
    for r in hits:
        print("| " + " | ".join(clean(r.get(c)) for c in show) + " |")


def clean(v):
    """One table cell on one line: no pipes, no line breaks (Excel adds \\r)."""
    return " ".join((v or "").replace("|", "/").replace("\r", " ").replace("\n", " ").split())


def cmd_count(args):
    cols, rows = read(args.file)
    check_cols(cols, filter_cols(args) + [args.by])
    counts = {}
    for r in rows:
        if matches(r, args):
            key = clean(r.get(args.by)) or "(empty)"
            counts[key] = counts.get(key, 0) + 1
    for key, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"{key}: {n}")


def merged(old, new):
    """Add the "; " values of new to old, keeping old's order and skipping repeats."""
    items = [x.strip() for x in (old or "").split(";") if x.strip()]
    seen = {x.lower() for x in items}
    for x in new.split(";"):
        x = x.strip()
        if x and x.lower() not in seen:
            items.append(x)
            seen.add(x.lower())
    return "; ".join(items)


def cmd_upsert(args):
    cols, rows = read(args.file)
    if args.row:
        new = [json.loads(args.row)]
    else:
        if not os.path.isfile(args.rows):
            sys.exit(f"{args.rows} doesn't exist")
        with open(args.rows, encoding="utf-8-sig") as f:
            new = json.load(f)
    if isinstance(new, dict):
        new = [new]
    if not isinstance(new, list) or not all(isinstance(r, dict) for r in new):
        sys.exit("rows must be a JSON object or a list of objects, one per row")
    alts = names(args.key.replace("|", ",")) if "|" in args.key else []
    if alts and "," in args.key:
        sys.exit('--key takes either "A,B" (all must match) or "A|B" (first one with a value), not both')
    keys = alts or names(args.key)
    merge = names(args.merge or "")
    if not keys:
        sys.exit("--key needs at least one column")
    check_cols(cols, keys + merge + [c for r in new for c in r])
    if set(keys) & set(merge):
        sys.exit("a key column can't also be a --merge column")
    norm = lambda r, k: cell_text(r.get(k)).strip().lower()
    keyof = lambda r: tuple(norm(r, k) for k in keys)
    index = {}

    def remember(r):
        if alts:
            for k in alts:
                if norm(r, k):
                    index[(k, norm(r, k))] = r
        else:
            index[keyof(r)] = r

    def find(r):
        if alts:
            for k in alts:
                if norm(r, k) and (k, norm(r, k)) in index:
                    return index[(k, norm(r, k))]
            return None
        return index.get(keyof(r))

    for r in rows:
        remember(r)
    updated = added = 0
    for item in new:
        item = {k: cell_text(v) for k, v in item.items()}
        if alts:
            if not any(norm(item, k) for k in alts):
                sys.exit(f"a row needs one of {', '.join(alts)}: {json.dumps(item)}")
        else:
            missing = [k for k, part in zip(keys, keyof(item)) if not part]
            if missing:
                sys.exit(f"a row is missing its {', '.join(missing)} (key: {', '.join(keys)}): {json.dumps(item)}")
        row = find(item)
        if row is not None:
            for k, v in item.items():
                if v == "" or (k in keys and row.get(k, "").strip()):
                    continue
                row[k] = merged(row.get(k), v) if k in merge else v
            updated += 1
        else:
            row = {c: "" for c in cols}
            row.update(item)
            rows.append(row)
            added += 1
        remember(row)
    write(args.file, cols, rows)
    print(f"updated {updated}, added {added}, total {len(rows)}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("init", "add-cols", "query", "count", "upsert"):
        s = sub.add_parser(name)
        s.add_argument("file")
        if name in ("query", "count"):
            for flag in ("--where", "--contains", "--any", "--min"):
                s.add_argument(flag, action="append", default=[])
    sub.choices["init"].add_argument("--cols", required=True)
    sub.choices["add-cols"].add_argument("--cols", required=True)
    sub.choices["query"].add_argument("--cols")
    sub.choices["query"].add_argument("--limit", type=int)
    sub.choices["count"].add_argument("--by", required=True)
    sub.choices["upsert"].add_argument("--key", required=True, help='one column; several that must all match: "Objection,Offer"; or alternatives: "Email|Customer"')
    sub.choices["upsert"].add_argument("--merge", help='columns whose "; " values are added to, not replaced: "Offer"')
    group = sub.choices["upsert"].add_mutually_exclusive_group(required=True)
    group.add_argument("--row")
    group.add_argument("--rows")
    args = p.parse_args()
    {"init": cmd_init, "add-cols": cmd_add_cols, "query": cmd_query, "count": cmd_count, "upsert": cmd_upsert}[args.command](args)


if __name__ == "__main__":
    main()
