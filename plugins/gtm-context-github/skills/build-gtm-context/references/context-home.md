# Where the GTM context lives: ~/gtm-context

Every student gets the same fixed home for their GTM context, outside any project: the folder `gtm-context` in their home directory. Never ask the user where to save it. Projects come and go; the context has to be findable from all of them, by every later course system and by scheduled refreshes.

## What goes there

| Version | `~/gtm-context/` holds |
|---|---|
| Notion | `gtm-hub.md`: links, IDs, sources and refresh settings. The context itself stays in Notion. |
| GitHub | The student's private `gtm-context` repository, cloned here. The context is in `gtm/` inside it. |
| Both | A private folder for raw exports while working, deleted when done: `.private/` for Notion, `gtm/.private/` for GitHub (gitignored). |

A student who switches from Notion to GitHub, or back, keeps the same folder and pointer. Only what's inside changes.

## The pointer in Claude's memory

So every session finds the context without searching, the setup adds a short block to Claude's global memory file (`~/.claude/CLAUDE.md`, loaded by Claude Code in every project and by scheduled tasks). It holds the Notion Hub link or the repo name, and the path. Nothing else.

Show the user the block (`gtm_home.py pointer ... --print`) and write it after one OK, because it's their global settings. It sits between two marker lines, so later runs update it in place instead of adding a second copy.

## Reading the folder from any project

Reading files outside the current project can make Claude Code ask for permission each time. With the user's OK, `gtm_home.py allow` adds the folder to `permissions.additionalDirectories` in `~/.claude/settings.json` (it keeps a backup), so reads stop asking. Notion users mostly don't need it, because the Hub link is already in memory, but it keeps refreshes smooth.

## Cowork and other surfaces

The Claude app's Cowork only sees folders the user has shared with it. If a student works in Cowork, ask them once to share `~/gtm-context` with it. If memory isn't loaded there, read `~/gtm-context/gtm-hub.md` (or `gtm/README.md`) directly at the start of a GTM task.

## The helper script

`scripts/gtm_home.py` in the skill's folder, run with `python3` by its full path:

| Command | What it does |
|---|---|
| `status` | JSON: the folder, whether it exists, Notion or GitHub mode, whether the pointer and permission are in place, and old links files in the current folder |
| `init` | Creates `~/gtm-context/` and `.private/` |
| `pointer --notion-hub URL` or `pointer --repo OWNER/NAME` | Writes or updates the pointer block (`--print` previews it) |
| `allow` | Adds the folder to Claude Code's allowed folders |
| `migrate --from PATH` | Moves an old `gtm-hub.md` from a project folder into `~/gtm-context/`. It never overwrites. |

## Older setups

A links file or `gtm/` folder found in the current project folder is from before this rule. Say so in one line. Move the Notion links file with `migrate`. For a `gtm/` folder, offer to move it into the `gtm-context` repo, and only on a clear yes, since it changes their repository.
