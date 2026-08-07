# Verify upstream sync before analysing anything

## The incident

On 2026-08-01 a full review of "hardcoded magic numbers" in
[`../VeraCrypt`](../VeraCrypt) was produced, complete with file:line evidence and a
value assessment per proposed change. Every single finding was already fixed upstream —
by the repo owner's own merged PRs
[#1525](https://github.com/veracrypt/VeraCrypt/pull/1525) and
[#1526](https://github.com/veracrypt/VeraCrypt/pull/1526), a year earlier.

Cause: the local `master` sat at `2f8161af` (2025-03-29), **394 commits / ~16 months**
behind `upstream/master`. The clone had **no `upstream` remote at all**, so nothing
signalled the drift. `git status` was clean and `git log` looked plausible.

## Check first, always

```bash
git remote -v                                   # is there an upstream at all?
git fetch upstream
git rev-list --count master..upstream/master    # how far behind?
git rev-list --count upstream/master..master    # anything unique locally?
```

The remote is now configured:

```
origin    git@github.com:bernardladenthin/VeraCrypt.git   (SSH)
upstream  https://github.com/veracrypt/VeraCrypt.git      (HTTPS)
```

Syncing is a fast-forward when the fork has no unique commits:

```bash
git checkout master && git merge --ff-only upstream/master
```

## Two traps around this

**1. GitHub reports merged PRs as `state: closed`.** Searching for prior work and seeing
"closed" does *not* mean rejected. The reliable check is whether the commit is an
ancestor of `upstream/master`:

```bash
git log upstream/master --oneline --author="<name>"
```

**2. Pushing needs a workaround.** `origin` is SSH, the key is passphrase-protected and
the `ssh-agent` service is stopped, so non-interactive pushes fail with
`Permission denied (publickey)`. Use `gh`'s existing auth as a one-off credential helper —
no persistent config change, no token on the command line:

```bash
git -c credential.helper='!gh auth git-credential' \
    push https://github.com/bernardladenthin/VeraCrypt.git <branch>
```

The same applies to `git fetch origin`; the remote-tracking refs otherwise go stale after
a push and silently misreport the branch state.

## Deleting stale branches

Deleting a remote-tracking ref locally (`git branch -rd origin/x`) is cosmetic — the next
`git fetch` brings it straight back. Only `git push origin --delete <branch>` removes it
for real.
