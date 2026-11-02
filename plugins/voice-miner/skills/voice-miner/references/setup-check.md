# Setup check

Some skills run a small script or use git. Students are non-technical and may not have these tools yet. This check finds what's missing and installs it with them, in the same session, before the first command that needs it.

## How to run it

- Check only the tools the skill lists (Python, git, GitHub CLI). When everything is there, say one line ("Setup check: all set") and go on.
- You run every check and install command yourself. Never ask the student to open Terminal or type a command.
- Before installing anything, ask once: what it is, who makes it, why the skill needs it, and about how long it takes. Install only on a clear yes.
- The student's part is clicking in windows that pop up and typing their computer password into the system's own password window. Never ask for a password, code or token in the chat, and never type one.
- Once a tool works, don't check it again in the same session.
- In a scheduled run, nobody is there to say yes or click. Never install anything. If a tool is missing, skip the steps that need it and say so in the run's summary.

You know the operating system from your environment. If not, run `uname`: `Darwin` is a Mac.

## Mac

### Python and git

Both come with Apple's free Command Line Tools. One install covers both.

1. Run `python3 --version`. Python 3.9 or newer is fine. If the skill needs git, also run `git --version`.
2. If either fails, or prints something about "command line developer tools", run `xcode-select --install`. Tell the student:
   "A window from Apple just opened. Click **Install**, then **Agree**. It takes 5 to 15 minutes. Tell me when it says the software was installed."
   If no window appears, it may be behind other windows. Ask them to check the Dock.
3. When they say it's done, run the checks again.

If `xcode-select --install` says the tools are already installed but `python3` still fails, ask the student to restart the Claude app and say "continue".

### GitHub CLI (only when the skill needs it)

1. Run `gh --version`. If it works, go to sign-in.
2. If Homebrew is installed (`brew --version` works), run `brew install gh`.
3. Otherwise use the official installer from GitHub:
   - Find it: `curl -sL https://api.github.com/repos/cli/cli/releases/latest | grep -oE 'https://[^"]*macOS_universal\.pkg' | head -1`
   - Ask before downloading. Name the file, the source (github.com/cli/cli, GitHub's own release page) and the size (about 50 MB).
   - Download it to `~/Downloads/` with `curl -L -o`, then run `open` on the file.
   - Tell the student: "The installer is open. Click **Continue** and **Install**. Your Mac will ask for your computer password in its own window. Tell me when it says the installation was successful."
4. Run `gh --version` again. It lives in `/usr/local/bin/gh`, so call it by that path if the name isn't found yet.

If anything fails, use the skill's own fallback (for example, keep the repo local and publish it later).

### GitHub sign-in

1. Run `gh auth status`. If it says logged in, you're done.
2. Otherwise run `gh auth login --web --hostname github.com --git-protocol https` in the background. It prints a one-time code and a link, then waits.
3. Show the student both: "Open github.com/login/device, sign in to GitHub, and enter this code: XXXX-XXXX. Tell me when GitHub says you're connected." Your browser may open the page by itself.
4. When they confirm, run `gh auth status` again.

### Git name and email (only before the first commit)

Run `git config --global user.email`. If it prints nothing, git can't commit yet. Ask which name and email to put on their commits. If they want their email private, offer the GitHub noreply address: run `gh api user -q '"\(.id)+\(.login)@users.noreply.github.com"'`. Set both with `git config --global user.name "..."` and `git config --global user.email "..."` after their OK.

## Windows

Windows has no Python or git by default. Install them with `winget`, which is built into Windows 10 and 11. Ask first, as above. Windows may show a "Do you want to allow this app to make changes" window. The student clicks **Yes**.

| Tool | Check | Install |
|---|---|---|
| Python | `python3 --version`, then `python --version`, then `py -3 --version` | `winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements` |
| git | `git --version` | `winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements` |
| GitHub CLI | `gh --version` | `winget install -e --id GitHub.cli --accept-package-agreements --accept-source-agreements` |

- Count a Python check as passed only if it prints "Python 3". A command that prints nothing or opens the Microsoft Store is a shortcut, not Python.
- A new install isn't found by name until the Claude app restarts. For this session, call it by its full path:
  - Python: `$env:LOCALAPPDATA\Programs\Python\Python312\python.exe`
  - git: `C:\Program Files\Git\cmd\git.exe`
  - GitHub CLI: `C:\Program Files\GitHub CLI\gh.exe`
- Sign-in and the git name and email work as on a Mac.

## Which Python command to use

The skills write `python3`. If a different command passed the check (`python`, `py -3`, or a full path), use that one wherever a skill says `python3`, for the rest of the session.
