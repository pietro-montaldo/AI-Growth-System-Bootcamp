#!/usr/bin/env python3
"""Read and update the GTM context CSV banks (customers, objections, competitors).

Read only the rows you need, and change rows without breaking the file.
Standard library only, so it runs anywhere Python 3 does.

  gtm_csv.py init FILE --cols "Company,Website,Size"
  gtm_csv.py query FILE [filters] [--cols A,B] [--limit N]
  gtm_csv.py count FILE --by COL [filters]
  gtm_csv.py upsert FILE --key COL (--row '{"Company": "Acme"}' | --rows rows.json)

Filters (combine as many as needed, all must match, case-insensitive):
  --where COL=VALUE        exact match
  --contains COL=TEXT      text appears in the cell
  --any COL=V1|V2|V3       exact match on any of the values
  --min COL=NUMBER         number in the cell is at least NUMBER
"""
import argparse
import csv
import json
import os
import sys


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
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
            if float(cell(col) or "nan") < float(number):
                return False
        except ValueError:
            return False
    return True


def filter_cols(args):
    return [split(p, "")[0] for p in args.where + args.contains + args.any + args.min]


def cmd_init(args):
    if os.path.exists(args.file):
        sys.exit(f"{args.file} already exists, not overwriting")
    write(args.file, [c.strip() for c in args.cols.split(",")], [])
    print(f"created {args.file}")


def cmd_query(args):
    cols, rows = read(args.file)
    check_cols(cols, filter_cols(args))
    show = [c.strip() for c in args.cols.split(",")] if args.cols else cols
    check_cols(cols, show)
    hits = [r for r in rows if matches(r, args)]
    print(f"{len(hits)} of {len(rows)} rows match")
    hits = hits[: args.limit] if args.limit else hits
    if not hits:
        return
    clean = lambda v: (v or "").replace("|", "/").replace("\n", " ")
    print("| " + " | ".join(show) + " |")
    print("|" + "---|" * len(show))
    for r in hits:
        print("| " + " | ".join(clean(r.get(c)) for c in show) + " |")


def cmd_count(args):
    cols, rows = read(args.file)
    check_cols(cols, filter_cols(args) + [args.by])
    counts = {}
    for r in rows:
        if matches(r, args):
            key = (r.get(args.by) or "").strip() or "(empty)"
            counts[key] = counts.get(key, 0) + 1
    for key, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"{key}: {n}")


def cmd_upsert(args):
    cols, rows = read(args.file)
    if args.row:
        new = [json.loads(args.row)]
    else:
        with open(args.rows, encoding="utf-8") as f:
            new = json.load(f)
    check_cols(cols, [args.key] + [c for r in new for c in r])
    index = {(r.get(args.key) or "").strip().lower(): r for r in rows}
    updated = added = 0
    for item in new:
        key = str(item.get(args.key, "")).strip().lower()
        if not key:
            sys.exit(f"a row is missing its {args.key}")
        if key in index:
            index[key].update({k: str(v) for k, v in item.items() if str(v) != "" and k != args.key})
            updated += 1
        else:
            row = {c: "" for c in cols}
            row.update({k: str(v) for k, v in item.items()})
            rows.append(row)
            index[key] = row
            added += 1
    write(args.file, cols, rows)
    print(f"updated {updated}, added {added}, total {len(rows)}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("init", "query", "count", "upsert"):
        s = sub.add_parser(name)
        s.add_argument("file")
        if name in ("query", "count"):
            for flag in ("--where", "--contains", "--any", "--min"):
                s.add_argument(flag, action="append", default=[])
    sub.choices["init"].add_argument("--cols", required=True)
    sub.choices["query"].add_argument("--cols")
    sub.choices["query"].add_argument("--limit", type=int)
    sub.choices["count"].add_argument("--by", required=True)
    sub.choices["upsert"].add_argument("--key", required=True)
    group = sub.choices["upsert"].add_mutually_exclusive_group(required=True)
    group.add_argument("--row")
    group.add_argument("--rows")
    args = p.parse_args()
    {"init": cmd_init, "query": cmd_query, "count": cmd_count, "upsert": cmd_upsert}[args.command](args)


if __name__ == "__main__":
    main()
