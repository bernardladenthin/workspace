# Pull Request Workflow

> Canonical workspace workflow for any sibling repo that uses `gh` for PRs.
> Each sibling repo's `CLAUDE.md` points to this file instead of duplicating
> the steps.

> **Remote-execution note.** In some sandboxed sessions `gh` is not on the
> PATH. When that is the case, use the GitHub MCP tools (`mcp__github__*`)
> instead of the `gh` invocations below — the workflow shape is identical.

## Step 1 — Detect whether `gh` is available

```bash
gh --version 2>/dev/null && echo "gh available" || echo "gh not available"
```

If `gh` is **not** available (e.g. local proxy remote, restricted sandbox),
inform the user and either stop or switch to the MCP github tools. Do not
attempt the remaining `gh` steps in that case.

## Step 2 — Create the PR

Always create a PR immediately after the first push to a feature branch
(only when the user explicitly asks for a PR — do not auto-create):

```bash
gh pr create \
  --title "<concise summary, ≤70 chars>" \
  --body "$(cat <<'EOF'
## Summary
- <bullet: what changed>
- <bullet: why>

## Test plan
- [ ] Affected test classes pass
- [ ] Full CI matrix passes

<session URL>
EOF
)"
```

Note the PR number printed — you need it in the next steps.

## Step 3 — Wait for all checks to complete

```bash
gh pr checks <PR-number> --watch --interval 30
```

If `--watch` is unavailable in the installed `gh` version, poll manually
(do not chain `sleep` to bypass the long-leading-sleep block):

```bash
while gh pr checks <PR-number> | grep -qE "pending|in_progress|queued"; do
  sleep 30
done
gh pr checks <PR-number>
```

## Step 4 — Triage failures

For each failing check, fetch the log:

```bash
gh run list --branch <branch-name> --limit 10
gh run view <run-id> --log-failed
```

For **CodeQL annotation** failures, pull structured annotations directly
(avoids parsing raw logs):

```bash
# get the annotations URL for the CodeQL check on the latest commit
gh api repos/{owner}/{repo}/commits/<sha>/check-runs \
  --jq '.check_runs[] | select(.name | test("CodeQL")) | .output.annotations_url'

# fetch the annotations (path, line number, message)
gh api <annotations-url> \
  --jq '.[] | {path: .path, line: .start_line, message: .message}'
```

## Step 5 — Fix, commit, push, repeat

1. Read the failure message or annotation.
2. Apply the fix.
3. Commit and push:
   ```bash
   git add <files>
   git commit -m "Fix <check-name>: <short description>"
   git push
   ```
4. Return to **Step 3** and wait for the re-run.
5. Repeat until `gh pr checks <PR-number>` shows every check as ✅ pass.

## Step 6 — Report to the user

Once all checks pass, summarise what was fixed and why. If a failure
**cannot** be fixed automatically (e.g. requires a large refactor, changes
public API, or disabling a security check) stop, explain the situation,
and ask for direction instead of silently suppressing or working around it.
