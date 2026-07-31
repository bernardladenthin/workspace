# Spotless Formatting

> Canonical workspace policy. Each sibling repo's `CLAUDE.md` points to this
> file instead of duplicating the rules.

All four sibling repos enforce Java code formatting with the Spotless Maven
plugin (`com.diffplug.spotless:spotless-maven-plugin`) configured for
**Palantir Java Format** (plus `removeUnusedImports`, `trimTrailingWhitespace`,
`endWithNewline`). The Spotless + Palantir-Java-Format versions are identical everywhere and
managed in each `pom.xml`; the pinned values live in the **canonical cross-repo tool-version
matrix** in [`../crossrepostatus.md`](../crossrepostatus.md) ("Tool versions" row) — kept in one
place there so they cannot drift between this file and the status doc.

`spotless:check` is bound to the `verify` phase, so a formatting violation
fails any `mvn verify` / `mvn package` and the CI `code-style` job (which runs
`mvn spotless:check` early — see `crossrepostatus.md`).

## Rule: run `mvn spotless:apply` before every commit that touches `.java` files

```bash
mvn spotless:apply   # reformat in place — run before committing
mvn spotless:check   # verify only (what CI runs); no changes written
```

Rationale and details:

- **It is always safe to apply.** Spotless only reformats — line wrapping,
  import ordering/removal, trailing whitespace, final newline. It never changes
  behavior, so there is no reason to commit unformatted code and let CI reject
  it.
- **It keeps the commit clean.** Applying before staging means the diff you
  commit is already canonical; the `verify`-phase `spotless:check` (and the fast
  `code-style` CI job) stays green without a follow-up formatting commit.
- **The check is uniform across all four repos** (same Spotless + Palantir
  versions), so a file formatted in one repo is formatted to the same rules in
  every repo.
- **If you already committed without applying:** run `mvn spotless:apply`, then
  either amend the commit or add a single follow-up "Apply Spotless formatting"
  commit. (The latter is what you do once the original commit is already pushed
  and you don't want to force-push.)

CI is the backstop, not the primary guard: `spotless:check` at `verify` and the
dedicated `code-style` job will catch a missed `apply`, but the point of this
rule is to keep that check from ever firing — formatting failures should be
fixed locally before the commit, not discovered in CI.
