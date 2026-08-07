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

Recurring per-repo audits (mostly cross-repo by nature but living per-repo today) are documented in [`policies/code-quality-todos.md`](policies/code-quality-todos.md).

Repos — **Java tier** (shared Maven/JUnit toolchain, governed by the guides and policies here):
- **BAF** = `/home/user/BitcoinAddressFinder`
- **jllama** = `/home/user/java-llama.cpp`
- **srcmorph** = `/home/user/srcmorph` (a 3-module reactor: `srcmorph` core + `srcmorph-cli` + `srcmorph-maven-plugin`; formerly `llamacpp-ai-index-maven-plugin`)
- **sb** = `/home/user/streambuffer`

**Other tracked repos** — no shared Java toolchain, each with its own conventions and its own
knowledge folder here:
- **VeraCrypt** (C/C++) = `/home/user/VeraCrypt` — see [`VeraCrypt/`](VeraCrypt/): build and coverage tooling, submitted PRs, local-only findings
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
| Tool versions | Identical across all 4: Checker 4.2.2, fb-contrib 7.7.4, findsecbugs 1.14.0, spotbugs 4.10.3.0, spotless 3.9.0, palantir 2.96.0, errorprone 2.50.0, nullaway 0.13.8, surefire 3.5.6, archunit 1.5.0, junit-jupiter 6.1.3, hamcrest 3.0, pitest-maven 1.25.9 (pitest-junit5-plugin 1.2.3). **All latest stable** — this row is the **canonical cross-repo tool-version matrix** (policy files point here rather than re-pinning). See "Dependency / plugin freshness" below for how this is kept current. |
| `dependencyConvergence` pinning convention | All 4 Maven repos (+ srcmorph's 3 reactor modules) enable maven-enforcer's `<dependencyConvergence/>`. Convention, the `excludedScopes=[test,provided]` default gotcha, and merge-discipline guidance are in [`policies/dependency-convergence-pinning.md`](policies/dependency-convergence-pinning.md). |
| Maven Enforcer `bannedDependencies` | Identical 7-entry list |
| `<parameters>true</parameters>` javac arg | All 4 ✅ |
| PIT `<mutationThreshold>100</mutationThreshold>` | All 4 wired at a 100% gate: **sb** whole-package · **jllama** an explicit class list (`value.*`/`exception.*`/`args.*`/`json.*` parsers) — **not fully hermetic, see "Deliberate non-parity"** · **srcmorph** (reactor core module) an explicit class list · **BAF** an explicit class list. Scope grows incrementally toward whole-package per repo (the sb model is the end state — see "Standing goals" below). Exact mutation counts drift with the code; treat any number as a snapshot, never a contract — the 100% gate is the contract. Canonical command + invocation rule live in [`policies/pit-mutation-testing.md`](policies/pit-mutation-testing.md). |
| Checker Framework as 2nd nullness pass | All 4 ✅ |
| JPMS `module-info.java` present | All 4 ✅. The module-mode-javadoc trap this creates (and how each repo avoids or resolved it) is documented once in [`policies/jpms-module-descriptor.md`](policies/jpms-module-descriptor.md) — read that before touching javadoc binding/phase order or raising a Java-8 repo's javadoc `<source>` to ≥ 9. |
| ArchUnit standard set (`noSystemExit` / `noNewRandom` / `Thread.sleep` / sun-com.sun-jdk.internal bans / public-fields-final / `noTestFrameworksInProduction` / `noPackageCycles`) | All 4 ✅ |
| `javac -Werror` + `-Xlint:all,-serial,-options,-classfile,-processing` | All 4 ✅ |
| Full `layeredArchitecture()` + per-module banned-imports | BAF/jllama/srcmorph ✅ (flat root package split into layered packages, strict rule enforced per repo — see each repo's own `TODO.md` "Done"); sb ➖ (single package) |
| GPG signing-key preflight (gpg + Gradle/BouncyCastle) | All 4 wired byte-identically in `publish.yml`: two standalone jobs (no `needs:`, run in parallel at pipeline start, `environment: maven-central`) reproduce what `maven-gpg-plugin` and Gradle's `signing` plugin do at deploy/publish time, so a bad/expired key or wrong passphrase reds in seconds instead of failing the publish stage. Prints only public key metadata; red-by-design on refs without the secret (fork PRs). The `.github/signing-selftest/` Gradle project used by the second job is byte-identical across all 4 (checksums below). |

### Cross-repo byte-identical files — checksum drift check

Files kept **byte-identical across repos** (sync any edit to every copy AND the hash here):

| File | SHA-256 | Copies |
|---|---|---|
| `.github/signing-selftest/build.gradle.kts` | `ab45f5c102b47dd16c325d4d9c283d158ba90c05f484eac45b2767885c4462f9` | all 4 repos |
| `.github/signing-selftest/settings.gradle.kts` | `9b2ea5b5ff8d48607e26e4e211ad6d496f7660e71c84e42caaa82b84f7001710` | all 4 repos |
| `.github/sign-fatjars.sh` | `3a240faac46c35d3ac4a11dc2969648e2134906b90a79b990ce2b713c7a96b36` | jllama + srcmorph (see [`policies/fat-jar-release-assets.md`](policies/fat-jar-release-assets.md)) |
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
- **`jar-with-dependencies` (fat/uber JAR) = GitHub-Release asset only, never Central, signed
  `.asc` — BAF + jllama + srcmorph (not sb).** Convention + per-repo shapes live in
  [`policies/fat-jar-release-assets.md`](policies/fat-jar-release-assets.md). sb ships no fat
  jar (single-class `Closeable` library, no runnable entry point).
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

- **Test-JVM diagnostics + memory standard** ([`policies/ci-test-diagnostics.md`](policies/ci-test-diagnostics.md)):
  🚧 in progress across BAF/jllama/srcmorph/sb — the `-Xmx2g`/no-eager-`-Xms`/crash-dump-upload
  standard is landed in all 4; some repos still carry repo-specific extras by design (BAF's
  `reuseForks`/`forkCount` tuning, the pocl job's memory steps).
- **PIT mutation coverage → 100% on ALL classes** (📌 all-time goal, ❌ open, never-finished
  quality ratchet). End state is the streambuffer model: `targetClasses` covering the *whole*
  production package, not a curated subset. Today only sb is whole-package; the other three gate
  a verified-100% subset that should keep growing — add tests for a class, then widen the scope
  to include it, never the other way around. Track per-repo progress in each repo's `TODO.md`.
- **SonarQube local build check — per repo** (❌ open). Add an opt-in, locally-runnable
  `org.sonarsource.scanner.maven:sonar-maven-plugin` analysis (behind a `sonar` profile, off the
  default build) to all four repos, with a JaCoCo XML report so Sonar ingests coverage, and a
  documented local-run recipe (`sonar:sonar -Dsonar.host.url=... -Dsonar.token=...`) in each
  repo's `CLAUDE.md`. Deliberately kept out of CI for now — local/opt-in only.
- **Fat-jar signing — unverified in production for BAF and srcmorph** (❌ open). jllama's is
  confirmed working (GitHub Release assets present with matching `.asc`/`.sha256`). BAF's fix is
  applied and verified locally but not yet exercised by a live `workflow_dispatch
  publish_to_central=true` run. srcmorph's fat-jar step is wired up (mirrors jllama's proven
  pattern) but has never once run in CI, success or failure — its last real release predates the
  step, and the one dispatch since then had `publish_to_central` unset. Don't call either
  "confirmed working" until a real dispatch proves it.
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
(Error Prone, NullAway, Checker). The only version updates ever on offer are pre-releases
(Maven 4 betas/RCs, `slf4j-api` 2.1.0-alpha1, `protobuf-javalite` RC, `kotlin` beta,
`maven-surefire-plugin` milestone) or `jqwik` past the banned 1.9.3 — none adopted. See
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
| `com.google.protobuf:protobuf-javalite` | 4.35.1 | BAF | 4.36.0-RC2 | Latest **stable**; newer is RC only. |
| `org.slf4j:slf4j-api` | 2.0.18 | all | 2.1.0-alpha1 | Latest **stable**; newer is alpha only. |
| `org.jetbrains.kotlin` | 2.4.10 | jllama (`llama-kotlin`) | 2.4.20-Beta2 | Latest **stable**; newer is beta only. |
| Maven-4 plugin line / surefire `3.6.0-M1` | — | all | `4.0.0-beta-*` / `-M1` | Maven-3 toolchain; Maven-4 betas + milestones deliberately not adopted. |

**Standing policy:** DO NOT UPGRADE jqwik past 1.9.3 — 📌 active in all 4 repos (see [`policies/jqwik-prompt-injection.md`](policies/jqwik-prompt-injection.md)).

**Standing policy:** run `mvn spotless:apply` before every commit that touches `.java` — 📌 active in all 4 repos ([`policies/spotless-formatting.md`](policies/spotless-formatting.md); `spotless:check` gates an early CI job in all 4, not just publish).

**Dependabot note:** the `github-actions` ecosystem has no `versioning-strategy` config knob —
when it opens a bump PR against a floating major-version pin (`@v5`), it rewrites the reference
to the exact release tag it's bumping to, and there is no way to configure it to preserve the
floating alias. Decide per-repo whether to standardize on exact pins (matches Dependabot's
default) or keep re-floating drifted lines manually; no config change prevents the drift from
recurring either way.
