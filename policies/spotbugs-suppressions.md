# SpotBugs Suppressions

> Canonical workspace policy. Each sibling repo's `CLAUDE.md` points to this
> file instead of duplicating the rules.

`spotbugs-exclude.xml` at each repo root contains documented suppressions for
findings that are by-design or false positives. **When refactoring or renaming
code referenced in that file, re-check the affected `<Match>` blocks:**

- `<Class>`, `<Method>`, and `<Field>` filters use exact string matches — a
  rename silently disables the suppression and may either un-suppress a real
  bug or leave a stale entry behind.
- After refactors, run `mvn -B -ntp -DskipTests -Dgpg.skip=true verify` and
  confirm the BugInstance count is unchanged. A drop means a suppression is
  now stale and should be deleted; an increase means a new finding needs its
  own decision (fix vs. suppress).
- Keep the rationale comment on each `<Match>` accurate — if the original
  justification no longer applies to the post-refactor code, remove the
  suppression rather than leave outdated reasoning in place.
- Never use `--` inside `<!-- ... -->` comment bodies in
  `spotbugs-exclude.xml` — XML forbids it and the entire filter file silently
  stops loading (every previously suppressed finding reappears).

**Where/when SpotBugs runs in CI.** `spotbugs:check` is bound to the Maven `verify` phase, but in
all four repos it also runs **early** in the fast `code-style` CI job
(`mvn -DskipTests -Denforcer.skip=true compile spotbugs:check`), which the `publish-snapshot` /
`publish-release` jobs depend on. So a finding fails a PR/push instead of surfacing for the first
time at release — the same fail-fast pattern `spotless-formatting.md` documents for Spotless (a
`verify`-bound check is otherwise only reached by the publish `deploy` goal). Validate suppression
changes locally with that same command (or the full `mvn -DskipTests -Dgpg.skip=true verify`) and
confirm the BugInstance count is unchanged.
