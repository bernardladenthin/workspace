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
