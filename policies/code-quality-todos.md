# Cross-Repo Code-Quality TODOs

> Canonical workspace policy. Each sibling repo's `CLAUDE.md` points to this
> file instead of duplicating the three audit/review TODOs that apply to
> every Bernard-Ladenthin Java repo.

These three reviews are paired — they're cheap to do together and expensive
to do separately, because renames and visibility tweaks land much more
cleanly inside a package-restructure commit than as standalone follow-ups.
Do them in one IDE refactor pass per repo whenever a repo's turn comes up.

## 1. `@VisibleForTesting` audit + design-fit review

**Audit.** Walk the production tree for package-private/protected methods
or fields that exist purely so tests can reach them, and either annotate
(`com.google.common.annotations.VisibleForTesting`) or move into the test
source tree.

**Design-fit review.** For every existing or planned `@VisibleForTesting`
usage, ask whether widening access is the cleanest path to testability.
Prefer these alternatives when applicable:

- **(a)** inject the dependency through the constructor and have the test
  pass a stub or fake;
- **(b)** extract the tested behaviour into a separate testable helper
  class with public methods;
- **(c)** restructure the production API so what the test wants to verify
  is observable through normal public methods.

Only keep the annotation where these alternatives are materially worse.
`@VisibleForTesting` should be the last resort, not the first.

Per-repo audit counts (snapshot in `crossrepostatus.md`): BAF 19 usages,
the other three repos zero.

## 2. Package hierarchy review

Walk the full `src/main/java/.../` tree and assess whether the current
package layout still expresses the design intent. Look for:

- classes that have drifted into the wrong package as the codebase grew;
- flat "kitchen-sink" packages that should be split (high class count,
  mixed concerns);
- deeply nested packages that fragment cohesive components;
- circular dependencies between packages;
- missing seams where a sub-package boundary would prevent leaking
  implementation details.

Produce a **target tree** as a separate planning step BEFORE making any
moves — large package refactors are expensive to review and easy to do
twice if the target isn't clear up front.

## 3. Class and method naming review (pair with the package work)

While the package hierarchy review is in flight, also audit class and
method names for the same kinds of drift:

- stale names that no longer describe what the class actually does after
  years of growth;
- over-abbreviated or cryptic identifiers (`Utils`, `Helper`, `Mgr`,
  `do*`, `process*`) that hide responsibilities;
- method names whose verbs do not match the actual side effects (named
  `get*` but writes, named `is*` but mutates, etc.);
- name collisions across packages that force qualified imports everywhere.

Renames are far cheaper to do **inside** a package-restructure commit than
as standalone follow-ups (one IDE refactor pass touches both the move and
the rename), so capture name changes in the same target tree as the
package plan rather than as a separate later step.

A snapshot of cross-repo naming-audit findings (severity-ranked) lives in
`crossrepostatus.md`; that file is the working punch-list for this TODO.

## 4. Package-architecture refactor + matching ArchUnit `layeredArchitecture()`

This is a **separate task**, deliberately tracked apart from the three
above. The package-hierarchy review in (2) flags what *should* move;
this entry covers the actual restructure plus the ArchUnit rule that
locks the new layout in place.

### Scope

For each multi-package repo, produce a layered package design that
real `Architectures.layeredArchitecture()` can enforce — i.e. one
where layers are stackable (no peer-to-peer dependencies between
the would-be middle layers). Then express it as an ArchUnit rule
with `consideringAllDependencies()` so a future drift fails the
build, not a code review.

### Why it is its own task

The current per-repo arch-test state pins only the invariants the
**existing** layout supports. Where the layout does not cleanly
stack, the rule had to be narrowed:

| Repo | Real-world blocker | Current best rule |
|---|---|---|
| **BAF** | One residual `configuration → root` edge after the `Secp256k1Constants` extraction (commit `ca75527`): `CKeyProducerJava.maxWorkSize` reads `PublicKeyBytes.BIT_COUNT_FOR_MAX_CHUNKS_ARRAY` (Java array-size cap — a producer-layer concern, not a secp256k1 spec value). Root and `keyproducer` still touch many siblings, making "root" the orchestration layer by accident rather than design. | `constantsPackageIsALeaf` + `configurationDoesNotDependOnRuntimeLayers` + `eckeyIsLowLevelCrypto` + `cliIsEntryPointOnly` (4 narrower rules; commits `bd58221` + `ca75527`) |
| **jllama** | `json` parsers/serializers consume root-package DTOs (`Pair`, `ChatMessage`, `ContentPart`) AND the root API consumes `json` parsers — they are peers, not stackable | `argsPackageIsALeaf` (1 narrower rule; commit `e673471`) |
| **plugin** | single production package (`aiindex`) | ➖ no layering possible |
| **streambuffer** | single production class (`StreamBuffer`) | ➖ no layering possible |

In each case the structural fix is non-trivial &mdash; for BAF: extract
the remaining `BIT_COUNT_FOR_MAX_CHUNKS_ARRAY` producer-layer
constant into its own leaf (mirroring how
`Secp256k1Constants` was extracted in commit `ca75527`), then split
the root package into an explicit `core/` (DTOs) + `orchestration/`
(Finder, Producer*, Consumer*) layer. For jllama: split DTOs out
of the root API package into a dedicated `value/` package, which
breaks the published public-API FQNs (`net.ladenthin.llama.Pair`
becomes `net.ladenthin.llama.value.Pair`) and therefore counts as
a breaking change. Neither of those is a small commit.

**Worked example &mdash; BAF `Secp256k1Constants` (commit `ca75527`).**
Five spec scalars (`MIN_VALID_PRIVATE_KEY`, `MIN_VALID_PRIVATE_KEY_HEX`,
`MAX_PRIVATE_KEY_HEX`, `MAX_PRIVATE_KEY`, `INVALID_PRIVATE_KEY_REPLACEMENT`)
plus `PRIVATE_KEY_MAX_NUM_BITS` were moved out of the producer-side
`PublicKeyBytes` DTO into a new
`net.ladenthin.bitcoinaddressfinder.constants.Secp256k1Constants` class
in a leaf package. Two `configuration → root` edges disappeared (the
hex-default reads in `CKeyProducerJavaIncremental`); the
`CProducer.getOverallWorkSize(BitHelper)` parameter was inlined in
the same commit to close a third edge. A new
`constantsPackageIsALeaf` ArchUnit rule was added to pin the new
package's leaf property at build time. Pattern to copy when
extracting the next leaf: (1) write the new class first with the
constants in their natural unit and `@NullMarked` package-info,
(2) update production callers to import from the new location,
(3) update the test callers (often 5&ndash;10 files), (4) delete the
originals, (5) add a `<name>PackageIsALeaf` ArchUnit rule.

### Procedure when a repo's turn comes up

1. **Plan the target tree first** — same discipline as (2). Write
   the layered design down (top → middle → bottom) and the
   directed-acyclic dependency graph between layers before any
   class moves. Include a strict invariant for each layer
   ("X must not be accessed by Y").
2. **Audit current cross-package edges** — `grep -rn "^import"` per
   sub-package against the target; every violation is either a
   class move, an extracted helper, or a redesigned API.
3. **Land the moves in coherent commits** — one commit per layer
   boundary fix is easier to review than a single mega-commit, but
   the ArchUnit `layeredArchitecture()` rule must be added in the
   **same series** so a half-done restructure does not silently
   leave the codebase in an inconsistent state.
4. **Replace the narrow rule(s)** — the existing
   `configurationDoesNotDependOnRuntimeLayers` /
   `argsPackageIsALeaf` etc. become redundant once the full
   `layeredArchitecture()` rule covers them. Delete them in the
   same commit that adds the full rule, with a Javadoc note
   pointing at the replacement.
5. **Update `crossrepostatus.md`** — flip the layered-architecture
   row from "narrower form ✅" to "full layered ✅".

### Non-goal

This is **not** an excuse to add layers for their own sake. If a
repo cannot produce a stackable design without inventing artificial
boundaries, the honest verdict (as recorded for jllama in commit
`e673471`) is "args stays a leaf, the rest is peers" — record that
in the test as a narrower rule and keep `noPackageCycles` as the
cycle guard.
