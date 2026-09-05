# Cross-Repo Status Table

This file is the status index for **every repository tracked in this workspace**, covering the
**current state** of items that span ≥ 2 repos. It is a
status snapshot, not a history log — dated incident narratives, commit-hash trails, and closed
audits have been pruned; that detail lives in each repo's own `git log` if it's ever needed again.
What stays here: what's true today, and — where the reasoning isn't obvious from the code — why.

Single-repo open work lives in each repo's own `TODO.md`:

- [`../BitcoinAddressFinder/TODO.md`](../BitcoinAddressFinder/TODO.md)
- [`../java-llama.cpp/TODO.md`](../java-llama.cpp/TODO.md)
- [`../srcmorph/TODO.md`](../srcmorph/TODO.md)
- [`../streambuffer/TODO.md`](../streambuffer/TODO.md)
- [`VeraCrypt/TODO.md`](VeraCrypt/TODO.md) — **kept here, not in the repo**: the fork is used to
  prepare upstream PRs, and these items are a local record that must not reach upstream.

Recurring per-repo audits (mostly cross-repo by nature but living per-repo today) are documented in [`policies/code-quality-todos.md`](policies/code-quality-todos.md).

Repos — **Java tier** (shared Maven/JUnit toolchain, governed by the guides and policies here):
- **BAF** = `/home/user/BitcoinAddressFinder`
- **jllama** = `/home/user/java-llama.cpp`
- **srcmorph** = `/home/user/srcmorph` (a 3-module reactor: `srcmorph` core + `srcmorph-cli` + `srcmorph-maven-plugin`; formerly `llamacpp-ai-index-maven-plugin`)
- **sb** = `/home/user/streambuffer`

**Other tracked repos** — no shared Java toolchain, each with its own conventions and its own
knowledge folder here:
- **VeraCrypt** (C/C++) = `/home/user/VeraCrypt` — see [`VeraCrypt/`](VeraCrypt/): build and coverage tooling, submitted PRs, local-only findings.
  Status: 4 PRs pending upstream, and **one reproduced defect (RNG check-then-lock race) that is deliberately unfixed and unreported** — fix designed, see [`VeraCrypt/TODO.md`](VeraCrypt/TODO.md)
- **llama.cpp** (C/C++) = `/home/user/llama.cpp` — see [`llama.cpp/`](llama.cpp/)
- **subprocess.h** (C) = `/home/user/subprocess.h` — see [`subprocess.h/`](subprocess.h/)

> **Scope note:** the **parity table** below compares Maven, PIT, SpotBugs and release plumbing, so
> it applies to the **Java tier only** (BAF, jllama, srcmorph, sb) — a C/C++ repo has no rows there,
> and a blank is a non-applicability rather than a gap. The **do-not-bump registry** under
> "Dependency / plugin freshness" additionally covers **BroomCabinet** pins, because a cross-repo
> dependency audit needs one reference for every deliberate pin regardless of which repo owns it.

Legend: ✅ done · 🚧 in progress · ❌ open · ➖ N/A · 📌 standing policy

**Badge resources:** [inttter/md-badges](https://github.com/inttter/md-badges?tab=readme-ov-file) — searchable index of badge syntax for shields.io, Simple Icons, and more (used across all four repo READMEs).

---

## In parity across all 4 repos

| Dimension | Status |
|---|---|
| Error Prone `-Xep:<Name>:ERROR` promotions | Identical 13-pattern set in all 4 poms |
| NullAway `-XepOpt` options | Identical 6 standard options (`CheckOptionalEmptiness`, `AcknowledgeRestrictiveAnnotations`, `AcknowledgeAndroidRecent`, `AssertsEnabled`, `OnlyNullMarked`, strict JSpecify). Plugin additionally has `ExcludedFieldAnnotations=…@Parameter,@Component` — correct repo-local exception for Mojo POJOs. |
| Tool versions | Identical across all 4 (re-derived from every pom on `origin/main` 2026-09-05, not copied forward): Checker 4.2.3, fb-contrib 7.7.4, findsecbugs 1.14.0, spotbugs-maven-plugin 4.10.4.1, spotless 3.10.2, palantir 2.97.0, errorprone 2.50.0, nullaway 0.14.1, surefire 3.6.0, archunit 1.5.0, junit-jupiter 6.1.3, hamcrest 3.0, pitest-maven 1.30.0 (pitest-junit5-plugin 1.2.3). **All latest stable** — this row is the **canonical cross-repo tool-version matrix** (policy files point here rather than re-pinning). See "Dependency / plugin freshness" below for how this is kept current. **This row has now gone stale twice, the same way both times, and the note added after the first occurrence did not prevent the second — so treat the numbers here as evidence only when the audit date above is recent.** 2026-08-29: spotless 3.10.0, palantir 2.96.0, pitest-maven 1.25.9 and nullaway 0.13.8 were behind while the row claimed "all latest stable". 2026-09-05: Checker 4.2.2, spotbugs 4.10.4.0, spotless 3.10.1, nullaway 0.14.0 and surefire 3.5.6 were behind, again under the same claim. Both times the *identity* half held (all four repos really did carry the same values) and only the recorded numbers lagged. The mechanism is the same each time: a per-repo Dependabot bump lands in one repo, the other three are brought back in step by a follow-up commit, and nothing in that sequence touches this file. **What would actually fix it is a check that derives this row from the poms rather than a reminder to update it by hand** — until that exists, re-derive before citing (the loop under "Dependency / plugin freshness" does it in one command). Every value above was additionally cross-checked against Maven Central's own `maven-metadata.xml` on 2026-09-05 and is the latest **stable** release of its artifact. |
| Release hygiene (CHANGELOG footer + version sites) | Audited 2026-08-29 while preparing java-llama.cpp 5.1.0 and BAF 1.8.0. **jllama ✅ / streambuffer ✅** — released headings, footer compare-links and `v*` tags are the same set in both. **BAF ➖ → fixed**: `v1.7.0` shipped with no `[1.7.0]` compare-link at all and `[Unreleased]` still pointing at `v1.6.1`; both repaired in the 1.8.0 prep. **srcmorph ➖ → fixed**: `v1.1.0` was tagged and released with **no CHANGELOG section and no link** — the chain jumped `1.0.2 → 1.1.1`, so a shipped version was undocumented. Repaired in the 1.2.0 prep (`ff68cfc`): the section was reconstructed, the compare-link added, and `[1.1.1]` re-pointed to compare from `v1.1.0`. Re-verified 2026-08-31 on srcmorph `main` — release headings and footer links are now the same set (`1.0.0`…`1.2.0`), with `[Unreleased]` kept as the anchor for the next cycle. The footer is the most-missed step because nothing builds or renders it — the mechanical headings/links/tags check and the per-repo table of version sites now live in [`workflows/release-process.md`](workflows/release-process.md) under "What actually gets missed". Related: BAF enforces its 24 launcher-script jar names with `ExampleRunScriptJarVersionTest` (a pom bump reds the build until they follow) and srcmorph is structurally immune via a glob — a repo that hardcodes jar names with neither guard is the gap to close. |
| `dependencyConvergence` pinning convention | All 4 Maven repos (+ srcmorph's 3 reactor modules) enable maven-enforcer's `<dependencyConvergence/>`. Convention, the `excludedScopes=[test,provided]` default gotcha, and merge-discipline guidance are in [`policies/dependency-convergence-pinning.md`](policies/dependency-convergence-pinning.md). |
| Maven Enforcer `bannedDependencies` | Identical 7-entry list |
| `<parameters>true</parameters>` javac arg | All 4 ✅ |
| PIT `<mutationThreshold>100</mutationThreshold>` | All 4 wired at a 100% gate: **sb** whole-package · **jllama** an explicit class list (`value.*`/`exception.*`/`args.*`/`json.*` parsers) — **not fully hermetic, see "Deliberate non-parity"** · **srcmorph** an explicit class list in **all three** reactor modules (core + `srcmorph-cli` + `srcmorph-maven-plugin`, gated reactor-wide since 2026-08-31) · **BAF** an explicit class list. Scope grows incrementally toward whole-package per repo (the sb model is the end state — see "Standing goals" below). Exact mutation counts drift with the code; treat any number as a snapshot, never a contract — the 100% gate is the contract. Canonical command + invocation rule live in [`policies/pit-mutation-testing.md`](policies/pit-mutation-testing.md). |
| Checker Framework as 2nd nullness pass | All 4 ✅ |
| JPMS `module-info.java` present | All 4 ✅. The module-mode-javadoc trap this creates (and how each repo avoids or resolved it) is documented once in [`policies/jpms-module-descriptor.md`](policies/jpms-module-descriptor.md) — read that before touching javadoc binding/phase order or raising a Java-8 repo's javadoc `<source>` to ≥ 9. |
| ArchUnit standard set (`noSystemExit` / `noNewRandom` / `Thread.sleep` / sun-com.sun-jdk.internal bans / public-fields-final / `noTestFrameworksInProduction` / `noPackageCycles`) | All 4 ✅ |
| `javac -Werror` + `-Xlint:all,-serial,-options,-classfile,-processing` | All 4 ✅ |
| Full `layeredArchitecture()` + per-module banned-imports | BAF/jllama/srcmorph ✅ (flat root package split into layered packages, strict rule enforced per repo — see each repo's own `TODO.md` "Done"); sb ➖ (single package) |
| GPG signing-key preflight (gpg + Gradle/BouncyCastle) | All 4 wired byte-identically in `publish.yml`: two standalone jobs (no `needs:`, run in parallel at pipeline start, `environment: maven-central`) reproduce what `maven-gpg-plugin` and Gradle's `signing` plugin do at deploy/publish time, so a bad/expired key or wrong passphrase reds in seconds instead of failing the publish stage. Prints only public key metadata; **red-by-design on every `pull_request` run, not just fork PRs** — the jobs declare `environment: maven-central` and GitHub withholds environment secrets from any PR context, including a branch pushed to the repo itself. Verified on BAF run 33866409744, where both preflight jobs failed within a second on a same-repository Dependabot branch. Green evidence therefore only ever comes from a `push`/dispatch run. The `.github/signing-selftest/` Gradle project used by the second job is byte-identical across all 4 (checksums below). |
| Class-file floor on the built jars (`verify-bytecode-version.sh`) | All 4 wired in `publish.yml` with the **byte-identical** `.github/verify-bytecode-version.sh` (checksums below). `maven.compiler.release` governs only the code *we* compile; a dependency built for a newer Java lands in the jar untouched and surfaces as `UnsupportedClassVersionError` on a consumer's JVM. It has happened twice: **checker-qual 4.x** (Java 11, `@Retention(RUNTIME)`, so any reflection over an annotated element loads it) and **logback-classic 1.4.0+**, whose `LogbackServiceProvider` SLF4J's `ServiceLoader` loads at startup. `--max-major` is passed from the workflow so the ceiling lives next to the release it belongs to: **52** in jllama/srcmorph/sb, **65** in BAF (Java 21). Placement is per-repo, on whatever job first has the jars: jllama `package` + `smoke-fatjar-linux` (module jars *and* the reassembled all-backends asset), srcmorph/BAF `smoke-fatjar`, sb `smoke-jar` (its deliverable is the plain jar, not a fat jar). `module-info.class` and `META-INF/versions/**` are skipped unconditionally — a classpath JVM never loads either. Exit 2 on an empty scan, so a build that produced no jars cannot read as a pass. |

### Cross-repo byte-identical files — checksum drift check

Files kept **byte-identical across repos** (sync any edit to every copy AND the hash here):

| File | SHA-256 | Copies |
|---|---|---|
| `.github/signing-selftest/build.gradle.kts` | `ab45f5c102b47dd16c325d4d9c283d158ba90c05f484eac45b2767885c4462f9` | all 4 repos |
| `.github/signing-selftest/settings.gradle.kts` | `9b2ea5b5ff8d48607e26e4e211ad6d496f7660e71c84e42caaa82b84f7001710` | all 4 repos |
| `.github/sign-fatjars.sh` | `3a240faac46c35d3ac4a11dc2969648e2134906b90a79b990ce2b713c7a96b36` | jllama + srcmorph (see [`policies/fat-jar-release-assets.md`](policies/fat-jar-release-assets.md)) |
| `.github/verify-bytecode-version.sh` | `88555f1ebe2ab52418b5ef628ffc078f132473b8000a3340b5bb73460a0b185d` | all 4 repos (class-file floor on the built jars; `--max-major` comes from the workflow, so the value lives next to the release it belongs to: 52 in the three Java 8 repos, 65 in BAF) |
| `.github/smoke-fatjar-cli.sh` | `4d1cc65cbd84a38f0d2015f55c0b2ba9027c72794b2c2ed578693a58d702efd2` | BAF + srcmorph (the two CLI fat jars; jllama's server/native smokes are repo-specific — see [`policies/fat-jar-release-assets.md`](policies/fat-jar-release-assets.md) "No release asset is attached that CI has not run") |
| `lombok.config` (jllama: `llama/lombok.config`) | `42f1842270af691bdfe561355bee4eb9ae326383f1852db19763abb888d6b90e` | the 3 Lombok repos: jllama + BAF + srcmorph (sb has no Lombok). Canonical content in [`policies/lombok-config.md`](policies/lombok-config.md) |
| `.github/ISSUE_TEMPLATE/bug_report.md` | `7232b092d3ba49b97bee7b539aaf6ee4c698e86bd3d4dd256e8ae2f85f653ee9` | all 4 repos |
| `.github/ISSUE_TEMPLATE/feature_request.md` | `0f08122e597f93dbbdc9c80e88984b4bf4738951d5902813df3d4640cdb11bac` | all 4 repos |
| `.github/PULL_REQUEST_TEMPLATE.md` | `ebfcc0adf59f5858bbe4dc077c906304a197f72a55256f0d5aac669bee5e871f` | all 4 repos |

Verify from the `workspace` repo root (siblings checked out alongside):

```bash
# Repo names are listed explicitly in each {…} — bash runs brace expansion BEFORE
# variable expansion, so a $var inside {…} would not expand into the repo list.
sha256sum ../{java-llama.cpp,BitcoinAddressFinder,srcmorph,streambuffer}/.github/signing-selftest/build.gradle.kts \
          ../{java-llama.cpp,BitcoinAddressFinder,srcmorph,streambuffer}/.github/signing-selftest/settings.gradle.kts \
          ../{java-llama.cpp,srcmorph}/.github/sign-fatjars.sh \
          ../{BitcoinAddressFinder,srcmorph}/.github/smoke-fatjar-cli.sh \
          ../{java-llama.cpp,BitcoinAddressFinder,srcmorph,streambuffer}/.github/verify-bytecode-version.sh \
          ../java-llama.cpp/llama/lombok.config ../{BitcoinAddressFinder,srcmorph}/lombok.config \
          ../{java-llama.cpp,BitcoinAddressFinder,srcmorph,streambuffer}/.github/ISSUE_TEMPLATE/bug_report.md \
          ../{java-llama.cpp,BitcoinAddressFinder,srcmorph,streambuffer}/.github/ISSUE_TEMPLATE/feature_request.md \
          ../{java-llama.cpp,BitcoinAddressFinder,srcmorph,streambuffer}/.github/PULL_REQUEST_TEMPLATE.md
# each file's copies must all show the hash in the table above; a mismatch = drift (re-sync) or an
# intentional edit (update every copy AND this table in the same change set).
```

## Deliberate non-parity (NOT drift)

Differences below are intentional design decisions, not gaps to close.

- Plugin's NullAway `ExcludedFieldAnnotations` extension — repo-correct (Mojo POJOs).
- **SLF4J binding: `slf4j-simple` in jllama + srcmorph, logback in BAF, none in sb.** Not drift —
  the split follows the Java floor. Every logback release from 1.4.0 on is Java 11 bytecode, so
  `LogbackServiceProvider` cannot load on the Java 8 artifacts: SLF4J's `ServiceLoader` finds it at
  startup and the JVM throws `UnsupportedClassVersionError` before a line is logged. The Java 8
  logback line (1.3.x) is EOL with unbackported CVEs, so it is not an option either. BAF is Java 21
  and keeps logback; sb has no logger at all. **The shipped binding is a fat-jar concern, not a
  library one** — jllama's and srcmorph-cli's fat jars are applications and may choose a binding;
  their published library jars impose nothing, and srcmorph excludes the binding
  `net.ladenthin:llama` brings transitively so the Maven plugin does not end up with two providers
  alongside Maven's own `maven-slf4j-provider`.
- **`checker-qual` scope: `provided` in jllama + srcmorph, `compile` in BAF, `optional` in sb.**
  Same reason. Its annotations are class-file major 55 from 4.0.0 on and `@Retention(RUNTIME)`, so
  anything reflecting over an annotated element (Jackson) loads them. Pinning the *shipped* copy to
  the last Java 8 line (3.55.1) looks like the fix and is not: the Nullness Checker resolves its own
  qualifiers through javac's symbol table — the compile classpath — so a 3.x checker-qual under the
  4.x processor fails every build with `Could not load type:
  org.checkerframework.framework.qual.DoesNotUnrefineReceiver`. Processor and qualifiers must share
  a major version; `provided` keeps 4.2.3 where the checker needs it while shipping none of it
  (`jar-with-dependencies` filters on scope, so `<optional>true</optional>` alone would not have).
  BAF is Java 21, so major 55 is simply legal there.
- BAF's lack of module-level `@NullMarked` — per-package `@NullMarked` covers the same scope
  without requiring `requires JSpecify`. sb keeps per-package `@NullMarked` too, by design.
- PIT `targetClasses` scope differs (sb whole-package; the other three an explicit list of
  classes verified at 100%) — each repo gates exactly what's proven to reach 100%, expanded
  incrementally; the only permitted exclusions are genuinely unkillable mutants (equivalent or
  native/model-dependent), each with its rationale recorded where the exclusion lives.
- **jllama's PIT gate is environment-conditional, not fully hermetic.** It reaches 100% only
  with the audio test fixture present; without it, 4 `NO_COVERAGE` mutants remain in
  `value.ContentPart.audioFile(Path)` (the only exerciser, `AudioInputIntegrationTest`,
  self-skips without a committed audio clip). Contrast the sibling `imageFile(Path)`, which is
  hermetic via temp-file unit tests. The other three gates are fully hermetic. See
  [`policies/pit-mutation-testing.md`](policies/pit-mutation-testing.md) §4.
- **BAF's Coveralls/Codecov coverage source is the `test-opencl` (pocl) job, not the ubuntu
  `test` matrix.** BAF-only, since it's the only repo with OpenCL code: the plain ubuntu job has
  no OpenCL ICD, so `@OpenCLTest` classes self-skip there and would show 0% coverage for the
  whole GPU pipeline; `test-opencl` installs pocl so those classes actually execute.
- **Depot/`sccache` shared compiler cache — java-llama.cpp only.** `sccache` caches *compiler*
  output (C/C++/CUDA) and jllama is the only sibling with a native (C++/JNI) build; the three
  pure-Maven siblings already cache Maven deps via `setup-java`'s `cache: maven` instead. The
  `DEPOT_TOKEN` org secret exists in all repos but is inert outside jllama.
- **Multi-artifact native-library merge (`pattern: "*-libraries"` + collision guard) —
  java-llama.cpp only.** jllama is the only sibling whose release JAR is assembled from ~20 native
  build artifacts produced on different runners, so it is the only one that globs artifacts into one
  resource tree. The three pure-Maven siblings each build their single jar in one job and download
  artifacts only by explicit name — nothing to port, and no sibling workflow uses `merge-multiple` or
  a `pattern:` glob at all (verified). The failure mode that made the guard necessary is worth
  knowing cross-repo even though the code isn't: **an artifact name says nothing about which path the
  job wrote**, so a glob merge can drop two artifacts onto one file and yield a byte-level hybrid of
  both. That shipped a macOS `libjllama.dylib` whose ad-hoc signature no longer matched its own
  `__TEXT` pages — macOS SIGKILLed every process that loaded it — through 5.0.6 and several 5.0.7
  snapshots with a fully green pipeline. jllama now downloads the glob unmerged and merges via
  `.github/merge-native-artifacts.sh`, which fails loud on any path claimed by two artifacts. Note
  the check *must* run before the merge: afterwards the collision leaves exactly one (corrupt) file,
  so a "one library per `{OS}/{ARCH}`" assertion on the merged tree cannot detect it. Details in
  jllama's `CLAUDE.md`, "macOS arm64: three build jobs, one shipped dylib".
- **`jar-with-dependencies` (fat/uber JAR) = GitHub-Release asset only, never Central, signed
  `.asc` — BAF + jllama + srcmorph (not sb).** Convention + per-repo shapes live in
  [`policies/fat-jar-release-assets.md`](policies/fat-jar-release-assets.md). sb ships no fat
  jar (single-class `Closeable` library, no runnable entry point). Note what does **not** follow
  from that: the *release-asset* rules — the pre-release smoke and the unsigned-asset guard — are
  about the attached artifact, not about the fat-jar shape, and both are landed in sb as well (see
  "Open cross-repo items"). Only the fat jar itself is sb-exempt.
- **Actual Gradle-based *publishing* (the `llama-android` AAR) — java-llama.cpp only.** The
  signing-key preflight harness is byte-identical in all 4 (kept as a "prepared for Gradle"
  canary), but only jllama has a real Gradle-published artifact today.
- **OPM (fb-contrib `OPM_OVERLY_PERMISSIVE_METHOD`) suppressed project-wide — BAF + jllama.**
  Both repos' package-layout refactors (single root package → layered packages) have landed, so
  the suppression's original justification (single-package code flags everything same-package-
  only as "should be package-private") no longer strictly applies and re-enabling is technically
  unblocked in both. Left suppressed **by choice, not by blocker**: visibility minimisation isn't
  a project goal, and the suppression was silencing refactor-era noise, not a real defect class.

---

## Open cross-repo items

- **srcmorph's corrupt-macOS-dylib exposure — bump landed, the proof run has not** (➖ mostly
  closed). srcmorph used to pin `<llama.version>5.0.6</llama.version>`, and 5.0.6 is one of the
  releases explicitly verified to carry the hybrid `Mac/aarch64/libjllama.dylib` (see the macOS
  entry under "Deliberate non-parity"), so every srcmorph fat-jar release asset built against it
  embedded a dylib that macOS SIGKILLs on load — srcmorph inherited the defect without having done
  anything wrong. Only srcmorph was affected: BAF and sb do not depend on `net.ladenthin:llama`.
  **Resolved by the bump:** jllama never released a `5.0.7` — 5.1.0 superseded it and carries the
  fix (its CHANGELOG documents the `merge-native-artifacts.sh` collision guard and the new
  `smoke-fatjar-macos` `codesign --verify --strict` + JVM-load gate, #390). srcmorph moved to
  `5.1.0` in `fcfc9cb`, and has since moved past it — `srcmorph/srcmorph/pom.xml` reads
  `<llama.version>5.2.0</llama.version>` as of 2026-09-05 (see the separate blocking item below;
  that is a *forward* pin on a version Central does not carry yet, not a regression to a pre-fix
  release). **What is still open is only the proof:** nobody has yet run the srcmorph CLI against a
  real model on macOS arm64. The bump is the fix, that run is the evidence — and until it happens
  the claim rests on jllama's own gate rather than on srcmorph's artifact. Blast radius if it were
  still broken is unchanged: the `LlamaCppJniAiGenerationProvider` path only (the `mock` provider
  never loads the native library), so `Plan`/mock runs and the whole test suite say nothing either
  way.
- **No release asset is attached that CI has not run** (✅ landed in **all four** repos).
  Every repo that attaches a release asset now launches it in a `smoke-*` job that gates both
  publish jobs: BAF (`config_AddressFilesToLMDB.json`, also exercises the lmdbjava natives),
  srcmorph (`config_Plan.json`, mock provider), jllama (`smoke-fatjar-linux`/`-windows` server
  smokes, plus `smoke-fatjar-macos` closing the gap that let a corrupt dylib ship), and — since
  2026-09-01 — **sb (`smoke-jar`)**. BAF and srcmorph share a byte-identical
  `.github/smoke-fatjar-cli.sh` (in the checksum table above); jllama keeps its own scripts because
  its Main-Class is a server that never exits and the macOS assertion is native loadability, not a
  CLI exit code. Rule, rationale and the per-repo assertion table live in
  [`policies/fat-jar-release-assets.md`](policies/fat-jar-release-assets.md). Each smoke is
  model-free, GPU-free and network-free by design (~1 min): an expensive smoke gets made
  non-gating and then the gap reopens. **Observed green in CI, per repo — nothing is pending any more** (re-checked
  2026-09-05 by opening each run, not from a doc): **jllama first, 2026-08-29** — the v5.1.0 release
  dispatch (run 33275073456, conclusion `success`) has `Package JARs` green *including* its
  `Merge native libraries into the default resource tree (collision-checked)` step, plus
  `Smoke test packaged natives (macOS)` and `Smoke test all-backends fat jar` on both Linux and
  Windows. **srcmorph, 2026-08-31** — `Smoke test fat jar` on `main` (`ec3cf5e`, run 33410263937).
  **BAF, 2026-09-04** — `Smoke test fat jar` green in run 33866409744; note the *run* is red, for
  unrelated test-job failures, so the evidence is the job, not the run. **sb, 2026-09-05** — `Smoke test packaged jar` green in run
  33962076725, bytecode-gate step included; that run's only red jobs are the two GPG preflights,
  which are red by design on any PR (see the parity table). An earlier revision of this entry
  crowned srcmorph first and called BAF and jllama "pending"; both halves were wrong.
  **sb was the last gap, and it was a gap in the rule's wording, not an exemption:** the rule was
  written around fat jars, sb ships none, so it read as N/A — while sb still attached and deployed
  a jar nothing in its pipeline had ever loaded (everything runs off `target/classes`). Its
  `smoke-jar` job puts the packaged jar on a classpath and does a real write/read/EOF round-trip
  through the API via the JDK single-file source launcher, and additionally asserts the jar carries
  `module-info.class` (compiled in a separate `release 9` execution, so it can be dropped without
  failing anything else). Repo-specific script (`.github/smoke-jar.sh`), not a shared one: there is
  no second no-Main-Class repo to share it with.
- **Unsigned-asset guard on the attach jobs** (✅ landed in **all four** repos, 2026-09-01). The
  attach jobs collect `target/*.jar.asc` with `|| true`, so a signing step that produced nothing
  yielded an attach that looked complete and was not. The guard cannot simply refuse to attach:
  both attach jobs deliberately run when the publish job *failed*, because when Central is
  unreachable the GitHub assets are the only way to get the build output at all. So it reports
  before the upload (non-blocking, one `::error::` per unsigned jar, count to `$GITHUB_OUTPUT`),
  uploads unconditionally, and fails the job afterwards — assets always land, an unsigned release
  is loudly red instead of quietly wrong. The two steps are byte-identical in all four repos
  (only the asset directory name differs); sync any edit everywhere. Rationale in
  [`policies/fat-jar-release-assets.md`](policies/fat-jar-release-assets.md), "Attach first, then
  go red".
- **Test-JVM diagnostics + memory standard** ([`policies/ci-test-diagnostics.md`](policies/ci-test-diagnostics.md)):
  🚧 in progress across BAF/jllama/srcmorph/sb — the `-Xmx2g`/no-eager-`-Xms`/crash-dump-upload
  standard is landed in all 4; some repos still carry repo-specific extras by design (BAF's
  `reuseForks`/`forkCount` tuning, the pocl job's memory steps).
  **§ 3.1 (echo the crash log into the job log, not only upload it) added 2026-08-26** and
  mirrored into all 4 `publish.yml` — jllama 6 sites, BAF 2 new + its pre-existing `test-opencl`
  step aligned, sb 1, srcmorph 1. It generalises what BAF's `test-opencl` job already did for the
  pocl SIGSEGV. Trigger: an artifact-only crash log is unreachable wherever Azure Blob egress is
  denied, which blocked the jllama `TtsIntegrationTest` investigation outright. The step also
  states explicitly when *no* crash log was written — `if-no-files-found` makes an empty upload
  indistinguishable from a populated one otherwise.
  **Out of scope, deliberately:** BAF's `issue50-lmdb-crash-repro.yml` (built never to fail on a
  reproduced crash, so a `failure()`-gated step could not fire) and **BroomCabinet's
  `java-ci.yml`** — that repo is not on this standard at all (no `-Xmx2g`, no `-XX:ErrorFile` in
  any of its ~15 project poms, and its upload takes only `surefire-reports/`), so a print step
  there would only ever emit the "nothing was written" line. Bringing BroomCabinet in means doing
  the pom side first; tracked as open, not silently half-done.
- **PIT mutation coverage → 100% on ALL classes** (📌 all-time goal, ❌ open, never-finished
  quality ratchet). End state is the streambuffer model: `targetClasses` covering the *whole*
  production package, not a curated subset. Today only sb is whole-package; the other three gate
  a verified-100% subset that should keep growing — add tests for a class, then widen the scope
  to include it, never the other way around. Track per-repo progress in each repo's `TODO.md`.
- **srcmorph `main` cannot resolve its dependencies, by design, until jllama releases 5.2.0**
  (❌ open, blocked on another repo — the only such state in the workspace). `srcmorph/srcmorph/pom.xml`
  pins `<llama.version>5.2.0</llama.version>`; Central's newest `net.ladenthin:llama` release is
  `5.1.0` and jllama `main` is `5.2.0-SNAPSHOT`, so `mvn -pl srcmorph dependency:resolve` ends in
  `Could not find artifact net.ladenthin:llama:jar:5.2.0`. **This is deliberate and is documented in
  a 22-line comment above the property — do not "fix" it.** The provider calls
  `setFlashAttn(FlashAttn)` and `setLazyMode(LazyMode)`, neither of which exists in 5.1.0, so a
  downgrade does not compile; and naming `5.2.0-SNAPSHOT` would need a `<repositories>` entry the
  repo deliberately does not declare **and** would block every future srcmorph release, since
  Central rejects a release with a `-SNAPSHOT` dependency. The pin goes green with no further edit
  the moment 5.2.0 is published.
  **What is *not* covered by that rationale, and is the reason this is an open item rather than a
  footnote: srcmorph has had no green CI of any kind since it landed.** The pin arrived in `5b4abeb`,
  merged as **PR #198 on 2026-09-01**; since then **8 PRs (#198–#205) have been merged with a red
  pipeline**, and it is not only `main` — every one of those *`pull_request`* runs is `failure` too
  (33491348847 … 33963628772 for CodeQL; 33493864690 … 33962068246 for Publish). Resolution fails
  before the first test compiles, so for that whole window srcmorph's tests, SpotBugs, spotless,
  PIT and bytecode gates have been asserting nothing. Each of those PRs was verified locally against
  a `mvn install`-ed jllama snapshot, which is what makes the arrangement workable at all — but a
  local build is the developer's evidence, not the repo's. **The single resolving step is a jllama
  5.2.0 release**; nothing is open on the srcmorph side, and jllama has no open PR blocking one.
- **"Did CI ever actually run this?" is not answerable from a run's presence in any of these repos**
  (📌 standing caveat, worth re-reading before citing any run as evidence). Two mechanisms suppress
  completed runs, and both were mistaken for green at least once: **(1)** a push to `main` is
  cancelled in the start-gate abort window in all four repos, so a `cancelled` run on `main` says
  nothing about health; **(2)** merging a PR promptly cancels that PR's own in-flight run. jllama is
  the live example — **every** run after the one that fixed its PIT gate is `cancelled` (898, 900,
  901, 902, 903, 904, 905), so the newest **completed** jllama run is 897, a `workflow_dispatch` from
  2026-09-04 at pin b10797 that failed. Nothing on jllama's current `main` (`ad2e3db`, pin b10819)
  has been validated by CI at all. The corollary for this file: green evidence comes only from
  `pull_request` runs that were allowed to finish and from `workflow_dispatch` releases — cite those,
  by run id, and never a bare "CI is green".
- **SonarQube local build check — per repo** (❌ open). Add an opt-in, locally-runnable
  `org.sonarsource.scanner.maven:sonar-maven-plugin` analysis (behind a `sonar` profile, off the
  default build) to all four repos, with a JaCoCo XML report so Sonar ingests coverage, and a
  documented local-run recipe (`sonar:sonar -Dsonar.host.url=... -Dsonar.token=...`) in each
  repo's `CLAUDE.md`. Deliberately kept out of CI for now — local/opt-in only.
- **Fat-jar signing — proven in production in all three fat-jar repos** (✅ closed 2026-09-05).
  Each was closed by a real release, not by a local check: **jllama** (assets carry matching
  `.asc` *and* `.sha256`), **BAF `v1.8.0`** (2026-08-29 — `bitcoinaddressfinder-1.8.0-jar-with-dependencies.jar`
  plus its `.asc`, uploaded by `github-actions[bot]`), and **srcmorph `v1.2.0`** (2026-09-01 — 52
  assets: the default fat jar plus 16 classifier fat jars, **every one** with a matching `.asc`,
  same uploader). One shape difference worth knowing rather than closing over: only jllama attaches
  a `.sha256` alongside; srcmorph's 52 assets contain none, so "`.asc`/`.sha256`" describes jllama,
  not the convention. sb is ➖ (ships no fat jar).
- **Central-publish pipeline current mechanism** (informational, not open, but non-obvious):
  publishing to Maven Central requires an explicit `workflow_dispatch` with
  `publish_to_central=true` — nothing publishes from an automatic push or tag anymore, and a
  version guard aborts the snapshot path unless `project.version` ends in `-SNAPSHOT`. The
  Central Portal wait condition is `waitUntil=validated` (not `published`) with a 6 h
  `waitMaxTime` — validation is where real errors surface (bad signature, missing javadoc,
  coordinate conflicts) and completes in minutes; waiting for full replication caused false-alarm
  timeouts on a working release. GitHub Release asset upload runs on publish success *or*
  failure (`if: ${{ !cancelled() }}`) so a failed-but-signed run still gets its assets attached.
  Identical across all 4 repos.

## Dependency / plugin freshness

All four repos are on the **newest stable** version of every dependency and build plugin,
checked with `versions:display-dependency-updates` + `display-plugin-updates` against Maven
Central plus direct `maven-metadata.xml` probes for paths the versions plugin doesn't scan
(Error Prone, NullAway, Checker). **One exception as of 2026-09-05:** jllama's
`llama-langchain4j/pom.xml` pins `<langchain4j.version>1.19.0</langchain4j.version>` while Central's
release is `1.20.0` — the only dependency in the workspace genuinely behind a stable upstream. It is
confined to that one module (which is `release 17`; the core stays Java 8), so it affects no other
artifact, and it is a plain lag rather than a deliberate pin — no rationale comment accompanies it,
and it does not belong in the do-not-bump registry below. The only version updates ever on offer are pre-releases
(Maven 4 betas/RCs, `slf4j-api` 2.1.0-alpha1, `kotlin` 2.4.20-RC, `maven-surefire-plugin`
milestone) or `jqwik` past the banned 1.9.3 — none adopted. See
[`policies/dependency-convergence-pinning.md`](policies/dependency-convergence-pinning.md) for
the pinning convention and the `DependencyConvergence` `excludedScopes` gotcha this surfaced.

#### Pinned dependencies — do-not-bump registry (cross-repo audit reference)

The single place a dependency audit should consult before "upgrading" any of these. The
**detailed rationale stays in the one repo that owns each pin** (this table only registers it so
a cross-repo sweep does not mistake a deliberate pin for a stale dependency). "Newer available"
= what `versions:display-*` offers and why it is rejected.

| Pinned dep | Version | Repos | Newer available | Why pinned — authoritative source |
|---|---|---|---|---|
| `net.jqwik:jqwik` | 1.9.3 | BAF, jllama, srcmorph | 1.10.1 | 📌 prompt-injection incident — [`policies/jqwik-prompt-injection.md`](policies/jqwik-prompt-injection.md) |
| `com.h2database:h2` | 2.2.224 | BroomCabinet (`JOracleRowSetGetRowBug`) | 2.4.240 | **Last Java-8-compatible line** (2.3.x+ needs Java 11); module is `<release>8</release>`. Rationale in that module's `pom.xml` comment. |
| `com.oracle.database.jdbc:ojdbc8` | 21.21.0.0 | BroomCabinet (`JOracleRowSetGetRowBug`) | 23.26.3.0.0 | The `oracle.jdbc.rowset.OracleCachedRowSet` class the bug reproducer needs exists **only in the 19.x/21.x ojdbc8 lines — Oracle removed the package in 23.x**. Rationale in that module's `pom.xml` comment + `BUG.md`. |
| `org.bouncycastle:bcprov-jdk15to18` | 1.85.2 | BAF | — (already latest stable) | Pins the bitcoinj-transitive bcprov to patch GHSA-c3fc-8qff-9hwx / GHSA-p93r-85wp-75v3. Rationale in BAF `CLAUDE.md` deps table. |
| `org.apache.logging.log4j:log4j-api` + `log4j-to-slf4j` | 2.26.1 | BAF, jllama | — (already latest stable 2.x) | **Was a security pin; is now a floor guard — the CVE it was written for is no longer reachable.** Both arrive only as **test-scope** transitives of `io.github.hakky54:logcaptor`. When the pin was added, logcaptor 2.12.6 requested log4j 2.25.3, affected by CVE-2026-49844 / GHSA-qv9r-c865-cp47 (moderate), and Dependabot reported "cannot update to the required version" — so a `dependencyManagement` pin was the fix. **Both repos are now on logcaptor 2.12.7, whose own pom declares `<version.log4j>2.26.1</version.log4j>`**, i.e. exactly what the pin forces; it therefore changes nothing today and only prevents a silent regression if logcaptor ever falls back. Harmless to keep, and **the pom comments in both repos still say "logcaptor … requests 2.25.3", which is now false** — either reword them to "floor guard" or drop the pin and this row (dropping means removing **both** artifacts together and re-confirming `mvn validate`, since the enforcer's `DependencyConvergence` is what the pair also satisfies). Pinned **as a pair** because `log4j-to-slf4j` requires a matching `log4j-api`. Neither reaches a published artifact. |
| `org.slf4j:slf4j-api` (and `slf4j-simple` where shipped) | 2.0.19 | BAF, jllama, srcmorph (sb has no logger) | 2.1.0-alpha1 | Latest **stable**; newer is alpha only. Central's `<release>` element points at the alpha, so read the `<version>` list, not `<release>`, when re-checking this one. |
| `org.jetbrains.kotlin` | 2.4.10 | jllama (`llama-kotlin`) | 2.4.20-RC | Latest **stable**; newer is an RC only. |
| Maven-4 plugin line / surefire `3.6.0-M1` | — | all | `4.0.0-beta-*` / `-M1` | Maven-3 toolchain; Maven-4 betas + milestones deliberately not adopted. |

**Standing policy:** DO NOT UPGRADE jqwik past 1.9.3 — 📌 active in all 4 repos (see [`policies/jqwik-prompt-injection.md`](policies/jqwik-prompt-injection.md)).

**Standing policy:** run `mvn spotless:apply` before every commit that touches `.java` — 📌 active in all 4 repos ([`policies/spotless-formatting.md`](policies/spotless-formatting.md); `spotless:check` gates an early CI job in all 4, not just publish).

#### GitHub Actions freshness

**Pin style is now uniform across all four repos** — the "two pin styles coexist" split this
section used to describe is gone. sb and BAF unpinned `github/codeql-action/*` from `v4.37.8`, and sb
unpinned `gradle/actions/setup-gradle` from `v6.3.0`, both on 2026-08-29 (sb `32b6e3c`, BAF `c01a95e`);
those pins were accidental, not deliberate. Enumerated from every `uses:` in
`.github/workflows/` on `origin/main`, 2026-09-05:

| Pin style | Actions | Repos |
|---|---|---|
| **floating major** | `github/codeql-action/{init,analyze,upload-sarif}@v4`, `gradle/actions/setup-gradle@v6`, `actions/{checkout@v7,setup-java@v6,cache@v6,upload-artifact@v7,download-artifact@v8,setup-python@v7,setup-node@v7}`, `codecov/codecov-action@v7`, `coverallsapp/github-action@v2`, `fsfe/reuse-action@v6`, `softprops/action-gh-release@v3`, `advanced-security/maven-dependency-submission-action@v5`, `anthropics/claude-code-action@v1`, and jllama's `ilammy/msvc-dev-cmd@v1` + `reactivecircus/android-emulator-runner@v2` | all 4 (where used) |
| **exact** | `google/osv-scanner-action` reusable `@v2.5.1`, `ossf/scorecard-action@v2.4.4` | all 4 |
| **exact, jllama-only** | `Jimver/cuda-toolkit@v0.2.36`, `jakoch/install-vulkan-sdk-action@v1.6.0` | jllama |

`actions/setup-java` is on **`v6`** in all four (bumped from `v5`). v6 is an ESM rewrite that drops
only the legacy **`adopt`** distributions and renames `jdkFile` → `jdk-file` (deprecated alias kept);
every job here uses `temurin` (or `zulu` in `sonarqube.yml`), both still supported, so the major bump
is a no-op for these pipelines.

The four exact-pinned actions were verified as already-latest at the 2026-08-29 sweep.
**They could NOT be re-verified on 2026-09-05** and are therefore unconfirmed since: this workspace's
egress proxy answers `403` for both `github.com/<owner>/<repo>/releases/latest` and `api.github.com`,
and the session's GitHub tooling is scoped to `bernardladenthin/*`, so a third-party repo's releases
are unreachable from here. Re-check them from an unrestricted environment; do not read the
2026-08-29 date as current.

**Not GitHub Actions but checked in the same sweep** (jllama's Gradle side): AGP **9.3.0** is the
newest stable, and CI's `gradle-version: "9.6.1"` already exceeds AGP 9.3.0's minimum/default Gradle
of 9.5.0. Gradle 9.7.1 exists but is **deliberately not adopted** — it is untested against AGP 9.3.0
and buys nothing; see jllama `CLAUDE.md` for the AGP/Gradle pin history.

**Dependabot note:** the `github-actions` ecosystem has no `versioning-strategy` config knob —
when it opens a bump PR against a floating major-version pin (`@v5`), it rewrites the reference
to the exact release tag it's bumping to, and there is no way to configure it to preserve the
floating alias. Decide per-repo whether to standardize on exact pins (matches Dependabot's
default) or keep re-floating drifted lines manually; no config change prevents the drift from
recurring either way.

## 2026-08-27 — CI hygiene sweep across all four Java repos

Two changes applied identically to `java-llama.cpp`, `BitcoinAddressFinder`, `streambuffer` and
`srcmorph`, plus the canonical policy they derive from.

**1. The "fork died" crash diagnostic no longer asserts a conclusion it cannot support** (10 call
sites: 6 in jllama, 2 in BAF, 1 each in sb and srcmorph, and
[`policies/ci-test-diagnostics.md`](policies/ci-test-diagnostics.md) §3.1). The step is
`if: failure()`, so it fires on *every* red job — and an ordinary assertion failure never writes a
crash log. It nonetheless printed "The fork died without the JVM writing a crash log", under a
heading that also echoed perfectly healthy server logs. It now states the observation, says plainly
that no file is the expected case for a normal test failure, and names the one signature ("The
forked VM terminated without properly saying goodbye", or an exit with no test results) that would
actually justify the JVM-abort conclusion. The policy carries a note explaining why it is worded
defensively, so it does not get "simplified" back.

**2. `publish.yml` gained a `concurrency:` group.** Every push previously started a full parallel
pipeline while the superseded ones kept draining — four were live at once in one session, which
makes "what is CI saying right now" genuinely ambiguous and wastes runner time on results nobody
reads. `cancel-in-progress` is scoped to `pull_request` **only**: a push to `main` or a `v*` tag is
a release path, and cancelling one midway could leave a partially published artifact set.

**`cancel-in-progress: false` does not, on its own, protect a release run** — the first version of
this sweep assumed it did, and that assumption was wrong. GitHub cancels a *pending* run whenever a
newer run joins the same group behind an in-progress one, and that rule is **independent of**
`cancel-in-progress`. With a plain `${{ github.workflow }}-${{ github.ref }}` group, a queued
`publish_to_central` dispatch on `main` could therefore be dropped silently by a later push to
`main`, both sharing `Publish-refs/heads/main`. The group expression now appends the unique
`github.run_id` for every non-PR run:

```yaml
group: ${{ github.workflow }}-${{ github.ref }}-${{ github.event_name == 'pull_request' && 'pr' || github.run_id }}
```

so a release run is never queued behind a sibling and can never be cancelled, while PR runs still
share a group per ref and supersede each other as intended.

Changing the expression has a **one-time** effect worth expecting rather than debugging: GitHub reads
`concurrency` from the workflow file at each run's *own* ref, so a run started before the change sits
in the old group and one started after it sits in the new one. They are different groups, so the new
push does not supersede the in-flight old run — exactly once, on the commit that lands it. It
self-heals from the next push on.

Verified: all four workflow files parse (`yaml.safe_load`) with the expected `concurrency` mapping,
and the corrected expression was confirmed empirically in java-llama.cpp — the next push cancelled
all 62 jobs of the previous PR run.
