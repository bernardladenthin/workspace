# JPMS module descriptor (`module-info.java`) handling

All four sibling repos ship a JPMS `module-info.java` and compile it in a **dedicated
`module-info-compile` execution at `release 9`**, separate from the main compile. This note
records the shared pattern, the latent **javadoc module-mode trap**, and what to do when a
Java-8 repo bumps to Java ≥ 9. The worked example is the BitcoinAddressFinder (BAF) incident —
see [`../crossrepostatus.md`](../crossrepostatus.md) ("Javadoc JPMS module-mode failure on BAF
publish-snapshot") and the comments on BAF's `attach-javadocs` / `module-info-compile` /
`default-testCompile` `pom.xml` executions.

## The shared pattern

| Repo | Java | `module-info.java` | compiled at | javadoc `<source>` | javadoc mode |
|---|:--:|---|---|:--:|---|
| streambuffer | 8 | `src/main/java` (excluded from default-compile) | `compile`, release 9 | 8 | classpath |
| java-llama.cpp | 8 | `src/main/java` (excluded) | `compile`, release 9 | 1.8 | classpath |
| llamacpp-ai-index-maven-plugin | 8 | `src/main/java` (excluded) | `compile`, release 9 | 8 | classpath |
| BitcoinAddressFinder | 21 | `src/main/java9` | `prepare-package`, release 9 | 21 | classpath (forced) |

Why a separate execution at all: a Java-8 main compile (`release 8`) literally cannot compile a
module descriptor (modules need `release ≥ 9`). BAF's reason differs — it keeps the main compile
in **unnamed-module mode** so Error Prone / NullAway / Checker Framework run and so the
system-module `--add-exports`/`--add-opens` the build relies on are allowed. Either way the
descriptor is **informational**: these jars run on the classpath; the descriptor only gives
module-path consumers a stable module name + directives.

## The latent trap: javadoc module mode

`maven-javadoc-plugin` switches into **JPMS module mode** when BOTH:

1. javadoc `<source>`/`<release>` ≥ 9 (module-aware), **AND**
2. a module descriptor is visible — `target/classes/module-info.class` is present when javadoc runs.

In module mode javadoc uses `--module-source-path` / `--patch-module`. That breaks for these repos
because the module declares **no `requires`** (dependencies resolve via the classpath), so
module-mode javadoc cannot see them (`error: package … does not exist`), and it mis-stages
packages when `module-info.java` is off the documented source path (`error: No source files for
package …`, the package named **non-deterministically** between runs). **Classpath mode is the
only viable mode for these repos.**

The three Java-8 repos are immune **today only because their javadoc `<source>` is 8** → javadoc
stays in classpath mode regardless of the descriptor. The bug is otherwise fully wired in: each
already compiles `module-info.class` into `target/classes` (at the `compile` phase) and has
multiple `package-info.java` files. BAF tripped it because it is the lone Java-21 repo with
javadoc `<source>21>`.

Detection gap that let it reach `main`: javadoc runs **only in the publish/deploy job** (every
other job passes `-Dmaven.javadoc.skip=true`), so the break is invisible to PR CI and fails only
on the snapshot publish. Consider running the javadoc jar in a fast PR-CI job.

## When you bump a Java-8 repo to Java ≥ 9

Raising the source level (and therefore javadoc `<source>`) arms the trap. Keep javadoc in
classpath mode — the BAF recipe:

1. **Run `attach-javadocs` while `target/classes/module-info.class` does not yet exist.** Bind it
   to `prepare-package` and declare the `maven-javadoc-plugin` block **before**
   `maven-compiler-plugin` so its execution wins the same-phase ordering and runs *before*
   `module-info-compile`. (These repos compile module-info at `compile` today — first move
   `module-info-compile` to `prepare-package`, then order javadoc ahead of it.)
2. Keep `module-info-compile` at a phase **before** the jar (`prepare-package`) so the descriptor
   still lands in the jar. Do **not** bind it to `package`: the lifecycle's `default-jar` runs
   before an explicitly-declared `package` execution and would drop the descriptor from the jar.
3. Verify with the **full lifecycle**, not a standalone goal:
   `mvn -P release clean package -DskipTests`. A bare `mvn javadoc:jar` runs with an empty
   `target/classes`, never reproduces module mode, and falsely passes.

Alternative (not recommended here): give `module-info.java` a complete `requires` graph so
module-mode javadoc can resolve dependencies — heavier, and it changes the descriptor's contract.

## BAF-only: the descriptor must also be absent during tests (do NOT copy blindly)

BAF *additionally* keeps `module-info.class` out of `target/classes` during **tests**: if present,
Maven Surefire runs the tests in JPMS module mode, where the `=ALL-UNNAMED` `--add-opens` flags no
longer apply to the (now named) main module, and **lmdbjava** (`LMDBPersistence` →
`org.lmdbjava.ByteBufferProxy`, which reflectively reaches `sun.nio.ch.DirectBuffer` /
`jdk.internal.ref.Cleaner`) fails with `IllegalAccessError` on `sun.nio.ch.DirectBuffer`. This is
why BAF binds `module-info-compile` to `prepare-package` (after `test`), not `compile`.

This test-timing concern is **BAF-specific** — the other three repos do no internal-JDK reflection
in tests and compile `module-info` at `compile` without issue. Don't carry the test rationale into
a repo that doesn't need it; for a Java-bump the javadoc recipe above is the only part that
generalises.
