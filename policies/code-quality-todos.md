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
