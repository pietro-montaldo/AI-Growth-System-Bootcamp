# How every session finds the GTM context

Every later course system, every project and every scheduled update must find the same context without searching and without asking the user where it is. Never ask the user where to save it. The answer is fixed:

| Version | Where the context lives | What Claude needs to find it |
|---|---|---|
| Notion | Notion, under one GTM Hub page. The Hub is its own map: its links table and its "For agents" section hold every page, database ID, source and setting. | Only the Hub link. Nothing is saved on the computer. |
| GitHub | The student's private `gtm-context` repository, cloned at `~/gtm-context`. The context is in `gtm/` inside it, and `gtm/README.md` is the map. | The folder `~/gtm-context`, the same for every student and outside any project. |

Raw exports used while working go in a private folder and are deleted when done: `~/gtm-context/.private/` for Notion (`gtm_home.py init` creates it), `gtm/.private/` for GitHub (gitignored).

## The pointer in Claude's memory

The setup adds a short block to Claude's global memory file (`~/.claude/CLAUDE.md`, loaded by Claude Code in every project and by app scheduled tasks). It holds the Notion Hub link, or the repo name and the `~/gtm-context` path. Nothing else: the Hub page or `gtm/README.md` holds the rest.

Show the user the block (`gtm_home.py pointer ... --print`) and write it after one OK, because it's their global settings. It sits between two marker lines, so later runs update it in place instead of adding a second copy.

Because the Notion pointer is only a link, it works anywhere Notion is connected: another computer, Cowork, or a cloud routine. The student's scheduled update task has the Hub link written into its prompt, so scheduled updates find the context without local memory.

## Reading the folder from any project (GitHub version)

Reading files outside the current project can make Claude Code ask for permission each time. With the user's OK, `gtm_home.py allow` adds `~/gtm-context` to `permissions.additionalDirectories` in `~/.claude/settings.json` (it keeps a backup), so reads stop asking. Notion users don't need it.

## Cowork and other surfaces

The Claude app's Cowork only sees folders the user has shared with it. A GitHub-version student who works in Cowork shares `~/gtm-context` with it once. If memory isn't loaded on a surface, a Notion student pastes the Hub link once, and a GitHub student points to `~/gtm-context/gtm/README.md`.

## The helper script

`scripts/gtm_home.py` in the skill's folder, run with `python3` by its full path:

| Command | What it does |
|---|---|
| `status` | JSON: Notion or GitHub mode, the Hub link from the pointer, whether the pointer and folder permission are in place, and old setup files found |
| `init` | Creates `~/gtm-context/` and `.private/` |
| `pointer --notion-hub URL` or `pointer --repo OWNER/NAME` | Writes or updates the pointer block (`--print` previews it) |
| `allow` | Adds `~/gtm-context` to Claude Code's allowed folders |

## Older setups

`status` lists files from earlier versions under `old_setup_files`:
- **A `gtm-hub.md` links file** (in the project folder or `~/gtm-context/`): Notion version. Follow "Older setups" in build-gtm-context's `hub-structure.md`: its contents move onto the Hub page.
- **A `gtm/` folder in the current project:** GitHub version from before the fixed home. Say so in one line and offer to move it into the `gtm-context` repo, only on a clear yes, since it changes their repository.
