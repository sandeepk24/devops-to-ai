# Git commands cheatsheet

Beyond `add`, `commit`, `push`. The commands you need to actually work with Git in a team.

---

## The mental model

```
Working directory  →  git add  →  Staging area (index)  →  git commit  →  Local repo  →  git push  →  Remote
                  ←  git restore  ←                      ←  git reset  ←              ←  git pull  ←
```

A commit is a **snapshot** of the entire repository, not a diff. Git stores the diff to save space, but conceptually every commit is a complete picture of your project at that moment.

---

## Daily workflow

```bash
git status                          # what's changed?
git diff                            # what exactly changed (unstaged)
git diff --staged                   # what's staged and ready to commit
git diff main..feature-branch       # diff between branches

git add file.txt                    # stage a file
git add .                           # stage everything
git add -p                          # interactively stage chunks (very useful)

git commit -m "fix: correct health check endpoint"
git commit --amend                  # edit the last commit message (before pushing)
git commit --amend --no-edit        # add staged changes to last commit, keep message

git log                             # commit history
git log --oneline                   # compact one-line format
git log --oneline --graph --all     # visual branch graph
git log -p                          # history with diffs
git log --author="Sandeep"          # commits by author
git log --since="1 week ago"        # recent commits
git log -- path/to/file             # commits that touched a file
```

---

## Branching

```bash
git branch                          # list local branches
git branch -a                       # list all branches (including remote)
git branch feature/new-thing        # create branch
git switch feature/new-thing        # switch to branch (modern syntax)
git switch -c feature/new-thing     # create and switch in one command
git checkout -b feature/new-thing   # older equivalent of switch -c

git branch -d feature/done          # delete branch (safe — won't delete unmerged)
git branch -D feature/abandon       # force delete (even if unmerged)
git push origin --delete feature/done   # delete remote branch

git merge feature/new-thing         # merge branch into current (creates merge commit)
git merge --squash feature/new-thing    # squash all commits into one before merging
git merge --no-ff feature/new-thing    # always create merge commit even for fast-forward
```

---

## Rebasing

```bash
# Rebase: replay your commits on top of another branch
# Use instead of merge to keep history linear

git rebase main                     # rebase current branch onto main
git rebase -i HEAD~3                # interactive rebase — edit last 3 commits
git rebase -i origin/main           # interactive rebase onto remote main

# Interactive rebase commands (shown in editor):
# pick   — use commit as-is
# reword — use commit but edit the message
# squash — combine with previous commit (keep both messages)
# fixup  — combine with previous commit (discard this message)
# drop   — remove this commit entirely
# edit   — pause and amend this commit

# Squash last 3 commits into one
git rebase -i HEAD~3
# change 'pick' to 'squash' on the 2nd and 3rd lines, save and exit
# edit the combined commit message, save and exit

# The golden rule: never rebase commits that have been pushed to a shared branch
# Rebase rewrites history — if others have those commits, you'll cause conflicts

# When rebase hits a conflict:
git status                          # see conflicted files
# edit files to resolve conflicts
git add resolved-file.txt
git rebase --continue               # continue
git rebase --abort                  # give up and go back to before the rebase
```

---

## Undoing things

```bash
# Unstage a file (keep changes in working directory)
git restore --staged file.txt

# Discard changes in working directory (CANNOT be undone)
git restore file.txt
git restore .                       # discard all unstaged changes

# Undo last commit (keep changes staged)
git reset --soft HEAD~1

# Undo last commit (keep changes unstaged)
git reset --mixed HEAD~1            # this is the default

# Undo last commit and discard all changes (CANNOT be undone)
git reset --hard HEAD~1

# Undo a commit that has already been pushed (creates a new "undo" commit)
git revert abc1234                  # revert a specific commit
git revert HEAD                     # revert the last commit

# The difference:
# reset  → rewrites history (only for local commits)
# revert → adds a new commit that undoes the changes (safe for shared branches)
```

---

## Reflog — your safety net

```bash
# git reflog tracks every change to HEAD, even after resets and rebases
# If you accidentally delete a commit or branch, reflog can save you

git reflog                          # show all HEAD movements
git reflog show feature/my-branch   # reflog for a specific branch

# Recover a commit after accidental reset
git reflog                          # find the commit SHA
git reset --hard abc1234            # go back to it
# or
git checkout -b recovery-branch abc1234   # create new branch from that commit

# Recover a deleted branch
git reflog                          # find the last commit SHA of the deleted branch
git checkout -b recovered-branch abc1234
```

---

## Stashing

```bash
git stash                           # stash all unstaged changes
git stash push -m "wip: half done feature"   # stash with a message
git stash push -p                   # interactively choose what to stash
git stash --include-untracked       # include new untracked files

git stash list                      # show all stashes
git stash pop                       # apply most recent stash and remove it
git stash apply stash@{2}           # apply a specific stash (keep it in list)
git stash drop stash@{1}            # delete a specific stash
git stash clear                     # delete all stashes

# Common use case:
# You're mid-work and need to quickly switch branches
git stash
git switch hotfix/urgent-bug
# fix the bug, commit, push
git switch -
git stash pop
```

---

## Remote operations

```bash
git remote -v                       # show remotes
git remote add upstream https://...  # add another remote (e.g. original repo you forked)
git remote remove upstream          # remove a remote

git fetch                           # download remote changes (don't merge)
git fetch --all                     # fetch from all remotes
git fetch --prune                   # also delete remote-tracking branches that no longer exist

git pull                            # fetch + merge
git pull --rebase                   # fetch + rebase (keeps history cleaner)
git pull --rebase origin main       # explicit

git push -u origin feature/branch   # push and set upstream tracking
git push --force-with-lease         # force push safely (fails if remote has new commits)
# never use git push --force on shared branches
```

---

## Cherry-picking

```bash
# Apply a specific commit from another branch to the current branch
git cherry-pick abc1234             # apply a single commit
git cherry-pick abc1234 def5678     # apply multiple commits
git cherry-pick abc1234..def5678    # apply a range of commits

# If there's a conflict:
# resolve the conflict
git add resolved-file.txt
git cherry-pick --continue
# or give up:
git cherry-pick --abort
```

---

## Tags

```bash
# Tags mark specific points in history — used for releases

git tag                             # list all tags
git tag v1.2.3                      # create lightweight tag at current commit
git tag -a v1.2.3 -m "Release 1.2.3 — adds health check endpoint"  # annotated tag

git tag -a v1.2.3 abc1234           # tag a specific past commit

git push origin v1.2.3              # push a specific tag
git push origin --tags              # push all tags

git tag -d v1.2.3                   # delete local tag
git push origin --delete v1.2.3     # delete remote tag

# Annotated tags are preferred for releases:
# - they store the tagger name, date, and message
# - they can be signed with GPG
# - they show up separately in git describe
```

---

## Git hooks

```bash
# Hooks live in .git/hooks/ — they run automatically at certain points
# To activate: remove the .sample extension and make executable

# pre-commit — runs before every commit (use to lint, format, test)
# pre-push   — runs before every push (use to run tests)
# commit-msg — validates the commit message format

# Example pre-commit hook:
cat > .git/hooks/pre-commit << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "running linter..."
if ! shellcheck scripts/*.sh; then
  echo "shellcheck failed — fix errors before committing"
  exit 1
fi
EOF
chmod +x .git/hooks/pre-commit

# For team-wide hooks (not ignored by git), use pre-commit framework:
# https://pre-commit.com/
```

---

## Useful config

```bash
# Set identity
git config --global user.name "Sandeep K"
git config --global user.email "you@example.com"

# Better defaults
git config --global pull.rebase true          # always rebase on pull
git config --global push.default current      # push to matching branch name
git config --global init.defaultBranch main   # use main instead of master
git config --global core.autocrlf input       # fix line ending issues (mac/linux)
git config --global rebase.autoStash true     # auto stash before rebase

# Useful aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.lg "log --oneline --graph --all --decorate"
git config --global alias.unstage "restore --staged"
git config --global alias.undo "reset --soft HEAD~1"

# Show current config
git config --global --list
```

---

## Conventional commits — the standard format

```
<type>(<scope>): <short description>

type:
  feat      new feature
  fix       bug fix
  docs      documentation only
  style     formatting, whitespace (no logic change)
  refactor  code restructure (no feature or fix)
  test      adding or fixing tests
  chore     build process, tooling, dependencies
  ci        CI/CD changes
  perf      performance improvement

examples:
  feat(auth): add JWT refresh token endpoint
  fix(deploy): correct health check timeout value
  docs(phase-00): add SSH section to README
  chore(deps): update terraform to 1.7.0
  ci: add trivy vulnerability scan to pipeline
```

Using conventional commits enables automated changelogs and semantic versioning tools. It also makes `git log` readable by humans.

---

*Part of [devops-to-ai](../../README.md) — Phase 00: The Foundation*
