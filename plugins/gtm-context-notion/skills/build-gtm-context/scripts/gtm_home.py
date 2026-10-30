#!/usr/bin/env python3
"""Point every Claude session at the student's GTM context, and check the setup.

Notion version: the Hub page is its own map, so the pointer only holds the Hub
link and nothing else is saved locally. GitHub version: the context is a
private gtm-context repo at ~/gtm-context. Either way, a short pointer in
Claude's global memory tells every session where it is. Standard library only.

  gtm_home.py status                      where things are, as JSON
  gtm_home.py init                        create ~/gtm-context (GitHub version, or for temporary exports)
  gtm_home.py pointer --notion-hub URL    write the pointer for the Notion version
  gtm_home.py pointer --repo OWNER/NAME   write the pointer for the GitHub version
  gtm_home.py pointer ... --updates URL   Notion: add the line that points to the review guide
  gtm_home.py pointer ... --print         show the pointer without writing it
  gtm_home.py allow                       let Claude Code read ~/gtm-context without asking each time

Environment (for testing): GTM_CONTEXT_HOME overrides ~/gtm-context,
CLAUDE_CONFIG_DIR overrides ~/.claude.
"""
import argparse
import json
import os
import shutil
import sys

START = "<!-- gtm-context:start (managed by the GTM context plugin, edit with care) -->"
END = "<!-- gtm-context:end -->"


def home():
    return os.path.abspath(os.path.expanduser(os.environ.get("GTM_CONTEXT_HOME", "~/gtm-context")))


def claude_dir():
    return os.path.abspath(os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude")))


def pointer_block():
    text = read(os.path.join(claude_dir(), "CLAUDE.md"))
    if START in text and END in text:
        return text.split(START, 1)[1].split(END, 1)[0]
    return ""


def notion_hub():
    for line in pointer_block().splitlines():
        if line.startswith("- GTM Hub (Notion): "):
            return line.split(": ", 1)[1].split(" ", 1)[0].rstrip(".")
    return None


def mode(path):
    if os.path.exists(os.path.join(path, "gtm", "README.md")):
        return "github"
    if notion_hub():
        return "notion"
    return "none"


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def settings_path():
    return os.path.join(claude_dir(), "settings.json")


def allowed(h):
    try:
        data = json.loads(read(settings_path()) or "{}")
    except json.JSONDecodeError:
        return False
    dirs = data.get("permissions", {}).get("additionalDirectories", [])
    return any(os.path.abspath(os.path.expanduser(d)) == h for d in dirs)


def cmd_status(args):
    h = home()
    memory = os.path.join(claude_dir(), "CLAUDE.md")
    candidates = ["gtm-hub.md", os.path.join("gtm", "README.md"), os.path.join(h, "gtm-hub.md")]
    if os.path.abspath("gtm") == os.path.join(h, "gtm"):
        candidates.remove(os.path.join("gtm", "README.md"))
    legacy = sorted({os.path.abspath(p) for p in candidates if os.path.exists(p)})
    print(json.dumps({
        "mode": mode(h),
        "notion_hub": notion_hub(),
        "pointer_in_memory": START in read(memory),
        "memory_file": memory,
        "home": h,
        "home_exists": os.path.isdir(h),
        "is_git_repo": os.path.isdir(os.path.join(h, ".git")),
        "folder_allowed": allowed(h),
        "old_setup_files": legacy,
    }, indent=2))


def cmd_init(args):
    h = home()
    os.makedirs(os.path.join(h, ".private"), exist_ok=True)
    print(f"ready: {h}")


def pointer_text(args):
    h = home().replace(os.path.expanduser("~"), "~", 1)
    if args.notion_hub:
        body = ("My go-to-market context (product, ICP, messaging, objections, customers) lives in Notion.\n"
                f"- GTM Hub (Notion): {args.notion_hub} . Its links table and its \"For agents\" section "
                "hold every page, database and setting.\n"
                "Before any GTM, sales, outreach or content task, fetch the Hub and open only the pages you need.")
        if args.updates:
            body += ("\nTo review GTM updates or change their settings, follow the guide on the "
                     f"Updates to review page: {args.updates}")
    else:
        body = (f"My go-to-market context (product, ICP, messaging, objections, customers) lives in {h}.\n"
                f"- GitHub: private repo {args.repo}, cloned at {h}\n"
                f"- Hub: {h}/gtm/README.md (links to every page and bank)\n"
                "Before any GTM, sales, outreach or content task, read the hub and open only the files you need.")
        if os.path.exists(os.path.join(home(), "gtm", "updates", "README.md")):
            body += f"\nTo review GTM updates or change their settings, follow {h}/gtm/updates/README.md"
    return (f"{START}\n## GTM context\n{body}\n"
            "Never search for the context, and never copy it into a project.\n"
            f"{END}")


def cmd_pointer(args):
    if not (args.notion_hub or args.repo):
        sys.exit("give --notion-hub URL or --repo OWNER/NAME")
    block = pointer_text(args)
    if args.print:
        print(block)
        return
    memory = os.path.join(claude_dir(), "CLAUDE.md")
    text = read(memory)
    if START in text and END in text:
        before, rest = text.split(START, 1)
        after = rest.split(END, 1)[1]
        text = before + block + after
        action = "updated"
    else:
        text = (text.rstrip() + "\n\n" if text.strip() else "") + block + "\n"
        action = "added"
    write(memory, text)
    print(f"{action} the GTM context pointer in {memory}")


def cmd_allow(args):
    h = home()
    path = settings_path()
    try:
        data = json.loads(read(path) or "{}")
    except json.JSONDecodeError:
        sys.exit(f"{path} isn't valid JSON, not touching it. Add {h} to permissions.additionalDirectories by hand.")
    if allowed(h):
        print(f"already allowed: {h}")
        return
    data.setdefault("permissions", {}).setdefault("additionalDirectories", []).append(h)
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")
    write(path, json.dumps(data, indent=2) + "\n")
    print(f"allowed {h} in {path} (backup: settings.json.bak)")



def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("init")
    sub.add_parser("allow")
    pt = sub.add_parser("pointer")
    group = pt.add_mutually_exclusive_group()
    group.add_argument("--notion-hub")
    group.add_argument("--repo")
    pt.add_argument("--updates", help="Notion only: link of the Updates to review page (adds a review line)")
    pt.add_argument("--print", action="store_true")
    args = p.parse_args()
    {"status": cmd_status, "init": cmd_init, "pointer": cmd_pointer, "allow": cmd_allow}[args.command](args)


if __name__ == "__main__":
    main()
