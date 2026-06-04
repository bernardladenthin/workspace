# Cross-Repo Status Table

This file tracks **only items that span ≥ 2 of the four sibling repos**. Single-repo open work has been moved into each repo's own `TODO.md`:

- [`../BitcoinAddressFinder/TODO.md`](../BitcoinAddressFinder/TODO.md)
- [`../java-llama.cpp/TODO.md`](../java-llama.cpp/TODO.md)
- [`../llamacpp-ai-index-maven-plugin/TODO.md`](../llamacpp-ai-index-maven-plugin/TODO.md)
- [`../streambuffer/TODO.md`](../streambuffer/TODO.md)

Recurring per-repo audits (mostly cross-repo by nature but living per-repo today) are documented in [`policies/code-quality-todos.md`](policies/code-quality-todos.md).

Repos:
- **BAF** = `/home/user/BitcoinAddressFinder`
- **jllama** = `/home/user/java-llama.cpp`
- **plugin** = `/home/user/llamacpp-ai-index-maven-plugin`
- **sb** = `/home/user/streambuffer`

Legend: ✅ done · ❌ open · ➖ N/A · 📌 standing policy

---

## In parity across all 4 repos (no action needed)

| Dimension | Status |
|---|---|
| Error Prone `-Xep:<Name>:ERROR` promotions | Identical 13-pattern set in all 4 poms |
| NullAway `-XepOpt` options | Identical 6 standard options (`CheckOptionalEmptiness`, `AcknowledgeRestrictiveAnnotations`, `AcknowledgeAndroidRecent`, `AssertsEnabled`, `OnlyNullMarked`, strict JSpecify). Plugin additionally has `ExcludedFieldAnnotations=…@Parameter,@Component` — correct repo-local exception for Mojo POJOs. |
| Tool versions | Identical: Checker 4.2.0, fb-contrib 7.7.4, spotless 3.6.0, palantir 2.91.0, errorprone 2.49.0, nullaway 0.13.4, surefire 3.5.6 |
| Maven Enforcer `bannedDependencies` | Identical 7-entry list |
| `<parameters>true</parameters>` javac arg | All 4 ✅ |
| PIT `<mutationThreshold>100</mutationThreshold>` | All 4 wired (sb whole-package; BAF/jllama/plugin narrowed to one class as documented staging) |
| Checker Framework as 2nd nullness pass | All 4 ✅ |
| JPMS `module-info.java` present | All 4 ✅ |
| ArchUnit standard set (`noSystemExit` / `noNewRandom` / `Thread.sleep` / sun-com.sun-jdk.internal bans / public-fields-final / `noTestFrameworksInProduction` / `noPackageCycles`) | All 4 ✅ |
| `javac -Werror` + `-Xlint:all,-serial,-options,-classfile,-processing` | All 4 ✅ |

## Deliberate non-parity (NOT drift)

- Plugin's NullAway `ExcludedFieldAnnotations` extension — repo-correct (Mojo POJOs).
- BAF's lack of module-level `@NullMarked` — documented intentional (per-package `@NullMarked` covers the same scope, avoids `requires JSpecify`).
- sb keeps per-package `@NullMarked` — by design.
- The PIT "narrow targetClasses" pattern in 3 of 4 repos — documented intentional staging.

---

## VERIFIED TABLE (cross-repo rows only)

| TODO item | BAF | jllama | plugin | sb |
|---|:--:|:--:|:--:|:--:|
| **Strictness ladder** | | | | |
| Error Prone bug patterns → ERROR (12+ patterns) | ✅ | ✅ `855f447` | ✅ `034b553` | ✅ `ad95d66` |
| `javac -Werror` + `-Xlint:all,-serial,-options,-classfile,-processing` | ✅ `2881c96` (this session) | ✅ `3e2efbb` | ✅ `f7cf748` | ✅ `7a4fbf0` |
| `-parameters` javac arg | ✅ `pom.xml:315` | ✅ `4350cf2` | ✅ `7ae3279` | ✅ `912f14b` |
| `--release N` instead of `-source`/`-target` | ✅ `<release>21</release>` (`c2470b7` + `1b67ad0`) | ✅ `4350cf2` | ✅ `7ae3279` | ✅ `912f14b` |
| PIT mutation threshold enforced (100%) | ✅ `BitHelper` | ✅ `Pair` (`62f8a00`) | ✅ `AiCompletionParser` | ✅ whole package |
| Checker Framework 2nd nullness pass | ✅ | ✅ `c63870b` | ✅ | ✅ `5a9be1b` |
| JPMS `module-info.java` | ✅ `src/main/java9/` | ✅ `0fd066a` / `9528e79` | ✅ | ✅ |
| Banned-API enforcement (Enforcer + ArchUnit) | ✅ | ✅ `8baae0c` / `329d764` / `e6069da` | ✅ `d654442` / `fd8cf80` / `ad37355` | ✅ `c0148c8` / `eaf4337` |
| ArchUnit public-fields-final | ✅ | ✅ `7b6667d` | ✅ `d2b1af9` | ✅ `5dd816d` |
| ArchUnit ban internal-JDK imports (`sun.*` / `com.sun.*` / `jdk.internal.*`) | ✅ | ✅ `e6069da` | ✅ `ad37355` | ✅ `de29bd4` |
| ArchUnit `noTestFrameworksInProduction` | ✅ | ✅ | ✅ | ✅ `bbdb505` (this session) |
| ArchUnit `noPackageCycles` | ✅ | ✅ | ✅ `26a4f7b` (this session) | ✅ `bbdb505` (this session) |
| ArchUnit `loggersArePrivateStaticFinal` | ✅ | ✅ | ➖ uses Maven `Log` | ➖ no logging |
| ArchUnit leaf-layer rules | ✅ (3 rules: `constantsPackageIsALeaf`, `configurationDoesNotDependOnRuntimeLayers`, `cliIsEntryPointOnly`) | ✅ (`argsPackageIsALeaf`) | ➖ single-package | ➖ single-package |
| ArchUnit full `layeredArchitecture()` | ❌ — needs DTO/orchestration split; touches public-API FQNs | ❌ — needs DTO split into `value/` package; breaks public-API FQNs | ➖ single-package | ➖ single-package |
| ArchUnit per-module banned-imports | ❌ | ❌ | ➖ single-package | ➖ single-package |
| SpotBugs `effort=Max` + `threshold=Low` | ❌ both `Default` | ❌ both `Default` | ❌ both `Default` | ✅ `4374dea` + `e7e254a` — flipped to Max+Low, all findings fixed at source (added `toString()`, contextful exception messages), no project-wide suppressions |
| **Logging / observability** | | | | |
| LogCaptor smoke test | ✅ LogCaptor 2.12.6 (7 tests) | ✅ `3cedc6e` | ➖ no logging | ➖ no logging |
| **Code-quality audits (continuous)** | | | | |
| `@VisibleForTesting` audit | ✅ 10 sites all legitimate per design-fit review | ➖ no usages | ➖ no usages | ➖ no usages |
| Null-safety follow-up review | ✅ 50 sites all legitimate | ✅ 43 sites all legitimate | ✅ 17 sites all legitimate | ✅ zero `@Nullable` in production |
| Package hierarchy review | ❌ | ❌ | ❌ | ❌ |
| Class / method naming review (21-item cross-repo audit) | ✅ 6/6 | ✅ 1/1 | ✅ 7/7 | ✅ 7/7 |
| **Cross-repo refactors** | | | | |
| Workspace-shared guidelines layer | ✅ | ✅ | ✅ | ✅ |
| Standardised `CLAUDE.md` template | ✅ | ✅ | ✅ | ✅ |
| Versioned workspace guide chain (`guides/src/-8.md` + `-21.md`, `guides/test/-8.md` + `-21.md`) | ✅ | ✅ | ✅ | ✅ |
| Audit-driven SKILL.md rewrite | ✅ | ✅ | ✅ | ✅ |
| Safe dependency / plugin bumps | ✅ `59f7ff1` | ✅ `0a97ae7` | ✅ `93c7c84` | ✅ `3ccb426` |
| Per-repo `TODO.md` extraction (open work moved out of `CLAUDE.md`) | ✅ (this session) | ✅ (this session) | ✅ (this session) | ✅ (this session) |
| **Standing policies** | | | | |
| DO NOT UPGRADE jqwik past 1.9.3 | 📌 active | 📌 active | 📌 active | 📌 active |

---

## Cross-repo open items (compact summary)

Items that affect ≥ 2 repos. Single-repo items are in each repo's `TODO.md`.

### Affects all 4 repos
- **SpotBugs `effort=Max` + `threshold=Low`** — open in BAF, jllama, plugin. **sb done** (`4374dea` + `e7e254a`). Path that worked for sb: flip pom config, run `spotbugs:check`, fix each finding at source rather than suppressing the pattern globally (`waitForAtLeast` assertion → IllegalArgumentException; 7 weak-exception-messaging sites gain state-dependent context in the message; explicit `toString()` snapshotting state under `bufferLock`). 290 tests pass; zero project-wide suppressions added. The 3 remaining repos have larger surface (plugin ~49, jllama ~105, BAF ~238 findings at Max+Low); each will need the same per-site treatment.
- **Package hierarchy review** (recurring; centralised at [`policies/code-quality-todos.md`](policies/code-quality-todos.md)).

### Affects BAF + jllama (multi-package repos)
- **ArchUnit `layeredArchitecture().consideringAllDependencies()`** — both repos have leaf-package rules instead of the full form. BAF needs DTO/orchestration split (`Finder`, `Producer*`, `Consumer*`); jllama needs DTOs in a `value/` package. Both moves break public-API FQNs.
- **ArchUnit per-module banned-imports** — not implemented in either.

---

## Naming audit — totals (closed)

The 21-item cross-repo naming audit completed this session. Distribution:

| Repo | CRITICAL | MODERATE | MINOR | Total | Status |
|---|:--:|:--:|:--:|:--:|---|
| BAF | 2 | 3 | 1 | 6 | ✅ 6/6 fixed |
| sb | 0 | 4 | 3 | 7 | ✅ 7/7 fixed |
| plugin | 0 | 4 | 3 | 7 | ✅ 7/7 fixed |
| jllama | 0 | 1 | 0 | 1 | ✅ 1/1 fixed |
| **All** | **2** | **12** | **7** | **21** | ✅ **complete** |

The two CRITICAL fixes were both in BAF: `CKeyProducerJavaIncremental.startAddress`/`endAddress` → `startPrivateKey`/`endPrivateKey` (public JSON config field, was actively misleading operators) and `Bech32Helper.getWitnessPrograms` (plural name returned a single value).
