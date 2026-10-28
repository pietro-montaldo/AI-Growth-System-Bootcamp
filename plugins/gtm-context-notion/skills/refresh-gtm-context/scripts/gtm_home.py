#!/usr/bin/env python3
"""Set up and check the fixed home of the GTM context: ~/gtm-context.

Every student gets the same folder, whatever project they work in, and a short
pointer in Claude's global memory so every session can find it without asking.
Standard library only.

  gtm_home.py status                      where things are, as JSON
  gtm_home.py init                        create ~/gtm-context if missing
  gtm_home.py pointer --notion-hub URL    write the pointer for the Notion version
  gtm_home.py pointer --repo OWNER/NAME   write the pointer for the GitHub version
  gtm_home.py pointer ... --print         show the pointer without writing it
  gtm_home.py allow                       let Claude Code read the folder without asking each time
  gtm_home.py migrate --from PATH         move an old gtm-hub.md into ~/gtm-context

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


def mode(path):
    if os.path.exists(os.path.join(path, "gtm", "README.md")):
        return "github"
    if os.path.exists(os.path.join(path, "gtm-hub.md")):
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
    legacy = [p for p in ("gtm-hub.md", os.path.join("gtm", "README.md")) if os.path.exists(p)]
    print(json.dumps({
        "home": h,
        "home_exists": os.path.isdir(h),
        "mode": mode(h),
        "is_git_repo": os.path.isdir(os.path.join(h, ".git")),
        "pointer_in_memory": START in read(memory),
        "memory_file": memory,
        "folder_allowed": allowed(h),
        "old_files_in_current_folder": [os.path.abspath(p) for p in legacy],
    }, indent=2))


def cmd_init(args):
    h = home()
    os.makedirs(os.path.join(h, ".private"), exist_ok=True)
    print(f"ready: {h}")


def pointer_text(args):
    h = home().replace(os.path.expanduser("~"), "~", 1)
    if args.notion_hub:
        where = f"- Notion GTM Hub: {args.notion_hub}\n- Links and settings: {h}/gtm-hub.md (links and IDs only)"
    else:
        where = f"- GitHub: private repo {args.repo}, cloned at {h}\n- Hub: {h}/gtm/README.md (links to every page and bank)"
    return (f"{START}\n## GTM context\n"
            f"My go-to-market context (product, ICP, messaging, objections, customers) lives in {h}.\n"
            f"{where}\n"
            "Before any GTM, sales, outreach or content task, read that file and open only the pages you need. "
            "Never search for them, and never copy the context into a project.\n"
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


def cmd_migrate(args):
    src = os.path.abspath(os.path.expanduser(args.source))
    dst = os.path.join(home(), "gtm-hub.md")
    if not os.path.exists(src):
        sys.exit(f"not found: {src}")
    if os.path.exists(dst):
        sys.exit(f"{dst} already exists, not overwriting. Compare the two files and keep one.")
    os.makedirs(home(), exist_ok=True)
    shutil.move(src, dst)
    print(f"moved {src} -> {dst}")


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
    pt.add_argument("--print", action="store_true")
    mg = sub.add_parser("migrate")
    mg.add_argument("--from", dest="source", required=True)
    args = p.parse_args()
    {"status": cmd_status, "init": cmd_init, "pointer": cmd_pointer, "allow": cmd_allow,
     "migrate": cmd_migrate}[args.command](args)


if __name__ == "__main__":
    main()
