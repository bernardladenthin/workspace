# Dependency-convergence pinning

> Canonical workspace policy. Each sibling repo's `CLAUDE.md` points to this
> file instead of duplicating the convention.

## Standing policy — pin, don't exclude or revert

Every sibling Maven repo enables maven-enforcer's `<dependencyConvergence/>`
rule. It fails at the `validate` phase — before compile, before tests —
whenever the same `groupId:artifactId` is reachable at two different
versions through two different declared paths in the tree, and **at least
one artifact is declared both directly and transitively**. Dependabot
routinely creates exactly this shape: it bumps a repo's *direct* version
declaration but has no way to also bump whatever upstream artifact still
requests the old version transitively, so the two diverge.

**The fix is always to pin the artifact in `<dependencyManagement>`** at the
version the repo wants (usually the newer one — see the section below on
when that's not automatically safe), forcing every path in the tree to
resolve to the same version. This is preferred over the two easy-looking
alternatives:

- **`<exclusions>` on the transitive path** — hides the artifact from that
  one path rather than resolving the version conflict; if the excluded
  artifact is genuinely needed at runtime by that dependency, this silently
  breaks it instead of failing loud at `validate`.
- **Relaxing or removing `dependencyConvergence`** — loses the guarantee
  entirely, for every dependency, not just the one that triggered the
  failure. Do not propose this to silence a single conflict.

Reverting the direct version bump instead of pinning is only correct when
the newer version is genuinely unwanted (e.g. a regression) — not as a
default response to a red `validate`, since the bump is often a security
fix worth keeping.

### Comment convention

Every managed entry added for this reason carries a one-line comment naming
the upstream artifact that brings the competing transitive version, so the
next person (or bump) can tell why the pin exists without re-running
`dependency:tree`:

```xml
<!-- jspecify: guava brings 1.0.0; we declare ${jspecify.version} directly. -->
<dependency>
    <groupId>org.jspecify</groupId>
    <artifactId>jspecify</artifactId>
    <version>${jspecify.version}</version>
</dependency>
```

In a Maven reactor (srcmorph), the pin belongs in the **parent's**
`dependencyManagement` so every child module shares one source of truth;
child modules should not redeclare an explicit `<version>` on a
parent-managed dependency (drop the version tag and any now-unused
`*.version` property, mirroring how `jackson.version` is already handled).

## The `excludedScopes` gotcha — read this before trusting a green `validate`

maven-enforcer's `DependencyConvergence` rule (enforcer-rules 3.6.3,
verified by bytecode inspection and empirical reproduction) **excludes
`test` and `provided` scope by default** (`excludedScopes = ["test",
"provided"]`), and a bare, unconfigured `<dependencyConvergence/>` tag never
overrides that default. Concretely:

- A direct-vs-transitive version mismatch where the conflicting transitive
  request is `test`-scoped **passes `validate` today even though the
  versions genuinely differ.** This is not "converged," it's invisible to
  the rule.
- The same mismatch, if either side ever moves to `compile`/`runtime`
  scope (a new library adds a compile-scope dependency on the same
  artifact, or a scope changes), **starts failing immediately** — with no
  warning beforehand, because nothing was actually checking it.
- This was independently confirmed by reproduction against both
  java-llama.cpp and streambuffer: both had real jspecify version mismatches
  passing `validate` purely because the colliding request lived in a
  test-scoped dependency chain (`junit-jupiter` → `junit-platform-commons`).
  BitcoinAddressFinder and srcmorph hit the *same* mismatch at compile
  scope and it failed for real.

**Practical consequence:** pin dependencies defensively even when
`validate` is currently green, if `dependency:tree -Dverbose` shows a real
version mismatch anywhere in the tree for an artifact you declare directly
— don't take a green `validate` as proof of convergence for that artifact.
If a repo wants `dependencyConvergence` to actually police test-scoped
conflicts, that's a deliberate, separate decision
(`<dependencyConvergence><excludedScopes><excludedScope>provided</excludedScope></excludedScopes></dependencyConvergence>`)
that must ship together with pins for every conflict it newly exposes, not
in isolation.

## Merge discipline — a red `Build` check on a Dependabot PR is not noise

Two convergence incidents were traced to their originating PRs
(BitcoinAddressFinder #331, srcmorph #169): in both, the PR's own `Build`
job — the job that runs `mvn validate`/`compile` — was already failing with
the exact `DependencyConvergence` error, *before* merge. Both were merged
anyway. This is not the "green PR, breaks later through a different
artifact's tree" failure mode; the failure was entirely visible on the PR
itself.

Both PRs also carried several *other* red checks that fail on essentially
every Dependabot PR for structural reasons (GPG-signing verification and
similar jobs that need secrets a bot-triggered run doesn't get,
`claude-review` needing an interactive context). That creates a habituation
risk: "Dependabot PRs are always red somewhere" makes it easy to merge past
the one check that is red for a real, content-relevant reason.

**Recommendation:** mark the job that runs `mvn validate`/`compile` (not the
structurally-red bot-context jobs) as a **required status check** in each
repo's branch protection rules, so GitHub blocks the merge button
technically rather than relying on a human noticing which red X matters.
This has not yet been verified as configured in any sibling repo — check
Settings → Branches → Protection rules before assuming it's in place.

## Current pin inventory (as of the 2026-08-07 audit)

All four Maven repos below pin `org.jspecify:jspecify` (1.0.1) in
`dependencyManagement` today; `org.checkerframework:checker-qual` (4.2.2)
is pinned defensively in all four for the same reason (currently converged
by coincidence, same latent shape jspecify had before it actually broke).

| Repo | Convergence-driven pins | Notes |
|---|---|---|
| BitcoinAddressFinder | `jspecify`, plus pre-existing `slf4j-api`, `guava`, `protobuf-javalite`, `bcprov-jdk15to18` | jspecify pin fixes a real, currently-merged red `main` |
| srcmorph (reactor parent) | `jspecify`, `checker-qual`, plus pre-existing `slf4j-api`, `logback-classic`, `jackson-databind`/`jackson-dataformat-yaml` | jspecify pin fixes a real, currently-merged red `main` (PR #169) |
| java-llama.cpp (`llama` module) | `jspecify`, `logback-classic`, plus pre-existing `slf4j-api` | both new pins are defensive (`excludedScopes` gotcha, see above) — no active failure |
| streambuffer | `jspecify`, `hamcrest` (repo's first `dependencyManagement` block — previously had none) | both new pins are defensive (`excludedScopes` gotcha, see above) — no active failure |
| BroomCabinet | n/a | none of its ~15 standalone poms enable `maven-enforcer-plugin` at all; this policy does not apply there |

Shared dependency versions are kept identical across all four repos where
the dependency is used by more than one of them (`jspecify` 1.0.1,
`checker-qual` 4.2.2, `junit-jupiter` 6.1.3, `archunit-junit5` 1.5.0,
`hamcrest` 3.0, `slf4j-api` 2.0.18, `logback-classic` 1.6.1, `jackson`
2.22.1 — all confirmed against Maven Central `maven-metadata.xml` as the
current release at audit time). When bumping any of these in one repo,
check whether the others should move in lockstep.
