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

Legend: ✅ done · 🚧 in progress · ❌ open · ➖ N/A · 📌 standing policy

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
| SpotBugs `effort=Max` + `threshold=Low` | ✅ `76fd1a7` — permanent flip; clean at the gate. Full chain: USBR-Lombok `6ddd69e` + CRLF layout `bd723f0` + WEM 3-batch `c2c3d62` / `4677831` / `dcee87d` + THROWS A/B/C `bd71766` + THROWS Group D `40d3f09` + DRE `5b72265` + 3× MDM structural refactors (AbstractProducer `892b76a`, ConsumerJava `99f390f`, ProducerOpenCL `09c5d52`) + MDM narrow suppression `cb02c70` + OPM project-wide suppression pending package refactor `52c8c95` + final 36-finding sweep `76fd1a7` (7 source fixes + 29 narrow `<Match>` suppressions with rationale). | ✅ `c3a26b9` (this session) — permanent flip; clean at the gate. Full chain: InferenceParameters wither refactor `4f1fbd7` + Lombok `doNotUseGetters` cross-repo sync `6ddd225` + remaining-findings sweep `14091bf` (DLS source fix + USBR/OPM/ChatRequest-EI/LlamaModel-ctx-SPP suppressions) + gate-flip cleanup `c3a26b9` (2 IMC field-order source fixes + 6 narrow `<Match>` suppressions for identity-IMC / TimingsLogger public logger name / formatted-wrapper / ToolHandler-FI / requireNonNull precondition guard). | ✅ `0bddf2a` — permanent flip; clean at the gate with documented suppression chain (Lombok-USBR, HelpMojo auto-gen family, Maven `@Parameter` SPP, identity-IMC, prompt-template FORMAT_STRING, fb-contrib flow-coarseness sites, NPE→MojoExecutionException bridge) plus source fixes (Lombok adoption, `Objects.requireNonNull` fail-fast in support ctors, enriched WEM messages, presized HashMaps). | ✅ `4374dea` + `e7e254a` — flipped to Max+Low, all findings fixed at source (added `toString()`, contextful exception messages), no project-wide suppressions |
| **Logging / observability** | | | | |
| LogCaptor smoke test | ✅ LogCaptor 2.12.6 (7 tests) | ✅ `3cedc6e` | ➖ no logging | ➖ no logging |
| **Code-quality audits (continuous)** | | | | |
| `@VisibleForTesting` audit | ✅ 10 sites all legitimate per design-fit review | ➖ no usages | ➖ no usages | ➖ no usages |
| Null-safety follow-up review | ✅ 50 sites all legitimate | ✅ 43 sites all legitimate | ✅ 17 sites all legitimate | ✅ zero `@Nullable` in production |
| Package hierarchy review | ❌ | ❌ | ❌ | ❌ |
| Class / method naming review (21-item cross-repo audit) | ✅ 6/6 | ✅ 1/1 | ✅ 7/7 | ✅ 7/7 |
| Typed-exception unification audit (constructor signatures + Javadoc shape consistent across every custom exception class) | 🚧 BAF concrete entries: `AddressFormatNotAcceptedException` `(reason, detail)` overloads (`4677831`), new `InterruptedRuntimeException` per checklist (`bd71766`), and `UncheckedRuntimeException`-style wrapper rejected with rationale (`40d3f09`) — the "what NOT to do" precedent is recorded in the audit text below | ❌ | ❌ | ❌ |
| **Cross-repo refactors** | | | | |
| Workspace-shared guidelines layer | ✅ | ✅ | ✅ | ✅ |
| Standardised `CLAUDE.md` template | ✅ | ✅ | ✅ | ✅ |
| Versioned workspace guide chain (`guides/src/-8.md` + `-21.md`, `guides/test/-8.md` + `-21.md`) | ✅ | ✅ | ✅ | ✅ |
| Audit-driven SKILL.md rewrite | ✅ | ✅ | ✅ | ✅ |
| Safe dependency / plugin bumps | ✅ `59f7ff1` | ✅ `0a97ae7` | ✅ `93c7c84` | ✅ `3ccb426` |
| Per-repo `TODO.md` extraction (open work moved out of `CLAUDE.md`) | ✅ (this session) | ✅ (this session) | ✅ (this session) | ✅ (this session) |
| Lombok 1.18.46 `@ToString` / `@EqualsAndHashCode` adoption (clears IMC_NO_TOSTRING + IMC_NO_EQUALS at SpotBugs Max+Low) | ✅ (BAF Lombok loop — 56 classes, 0 handwritten Object methods left) | ✅ `9be73a3` (this session) — 23 classes annotated; OSInfo / exceptions / enums / interfaces / non-instantiable utilities intentionally skipped | ✅ `39e1a59` + `6955357` (this session) — 6 `@ConvertToRecord` value types migrated, 19 service/codec/Mojo classes annotated, IMC_NO_EQUALS suppressed for identity-semantic Mojos / JavaBeans / service classes with rationale | ➖ excluded by design (user choice) |
| Canonical `lombok.config` content (see [`policies/lombok-config.md`](policies/lombok-config.md)) including `doNotUseGetters = true` for `@EqualsAndHashCode`/`@ToString` | ✅ `61e7996` (this session) — full Lombok-class audit (56 files) found one Bucket 3 outlier (`CKeyProducerJavaIncremental` BigInteger-parsing getters) whose behavior shift to String-form equality is semantically more correct for a JSON-roundtrip config POJO; 71 surefire reports green | ✅ `6ddd225` (this session) — added `doNotUseGetters` after fb-contrib `OI_OPTIONAL_ISSUES_CHECKING_REFERENCE` audit on `ChatRequest`/`ChatMessage` Optional-wrapping getters; SpotBugs Max+Low 6 → 2 | ✅ `3c61b88` (this session) — Bucket 1 / Bucket 4 only (zero Optional-wrapping getters); 53 tests green | ➖ no Lombok dependency |
| **Standing policies** | | | | |
| DO NOT UPGRADE jqwik past 1.9.3 | 📌 active | 📌 active | 📌 active | 📌 active |

---

## Cross-repo open items (compact summary)

Items that affect ≥ 2 repos. Single-repo items are in each repo's `TODO.md`.

### Affects all 4 repos
- **SpotBugs `effort=Max` + `threshold=Low`** — ✅ ALL FOUR REPOS now permanently enforce Max+Low at the gate with zero unsuppressed findings: sb (`4374dea` + `e7e254a`), plugin (`0bddf2a`), BAF (`76fd1a7`), jllama (`c3a26b9` — this session, closing the last open row in this cluster). Cross-repo pattern: flip pom config, run `spotbugs:check`, fix each finding at source where reasonable, suppress narrowly with rationale where structural (Lombok-generated equals/hashCode, generator-emitted Mojo bytecode, Maven `@Parameter` reflection contract, CRLF-injection sanitised at the Logback PatternLayout layer, generic-erasure CHECKCAST in keyproducer hierarchy, identity-managed lifecycle handles, public logger contract names that intentionally differ from the enclosing class FQN, runtime-format-string backport wrappers, etc.).
- **Package hierarchy review** (recurring; centralised at [`policies/code-quality-todos.md`](policies/code-quality-todos.md)).
- **Typed-exception unification audit.** Every custom exception class
  across the four repos should follow one shared shape, so that
  ergonomics (`throw new …Exception(…)`), debugging (`getMessage()` /
  `getCause()` / any aggregation accessor like `getReason()`), and
  documentation (Javadoc on the class and on each constructor) are
  predictable for a contributor moving between repos. Concrete
  checklist for each `*Exception` class:
    1. **Constructor matrix.** At minimum: `(String message)` and
       `(String message, Throwable cause)`. Add `(…, String detail)`
       and `(…, String detail, Throwable cause)` overloads when the
       message has an aggregation key separate from the per-call
       runtime detail (BAF's `AddressFormatNotAcceptedException` is
       the precedent — `reason` is the aggregation key, `detail`
       is the offending input). Don't ship a single-arg `(Throwable)`
       form without a `(String, Throwable)` companion — operators lose
       the human-readable context.
    2. **Aggregation accessor naming.** If the exception participates
       in counter aggregation (like `incrementUnsupported(getReason())`),
       expose the key as `getReason()` (BAF convention). Don't reuse
       `getMessage()` for aggregation — `getMessage()` is the verbose
       human-readable form including the detail.
    3. **Class-level Javadoc shape.** First sentence states *when* the
       exception is thrown (the throwing condition, not "thrown when an
       exception occurs"). Second sentence describes what the recipient
       can do about it. List any aggregation contract explicitly.
    4. **Constructor Javadoc shape.** Every parameter described in
       terms of the exception's *contract* (what each value means for
       `getMessage()` / `getReason()` / cause chaining), not by
       restating the Java type.
    5. **Equality semantics.** Exceptions extend `Throwable`, which
       uses identity equality — keep it that way (don't add Lombok
       `@EqualsAndHashCode`). The BAF `spotbugs-exclude.xml` Match
       suppressing `IMC_IMMATURE_CLASS_NO_EQUALS` on the three BAF
       exception classes is the precedent.
    6. **Test class per exception.** Pattern: `<Name>ExceptionTest`
       with one test per constructor (verifies the message shape and
       any aggregation accessor) plus one round-trip via the throwing
       call site for non-trivial detail formatting.
  Triggering this audit now because the WEM cleanup on BAF surfaced
  the need to extend `AddressFormatNotAcceptedException` with a
  `(reason, detail)` overload — that's the right design across every
  custom exception in the four repos, not just one.

  **What NOT to do — `UncheckedRuntimeException`-style wrapper for
  catch-then-rethrow sites.** Recorded here so future maintainers do
  not re-derive the trade-off. When fb-contrib's
  `THROWS_METHOD_THROWS_RUNTIMEEXCEPTION` flags a
  `catch (RuntimeException e) { cleanup(); throw e; }` site,
  introducing a `class UncheckedRuntimeException extends RuntimeException`
  (or any other "I caught a RuntimeException for cleanup" wrapper)
  and rewriting the catch as `throw new UncheckedRuntimeException(e)`
  looks like a clean typed-exception solution but is strictly worse
  than the status quo for three reasons:
    1. **Breaks caller recovery.** Callers that catch specific subtypes
       (e.g. `NoMoreSecretsAvailableException`) see the wrapper
       instead and have to unwrap to handle the real type.
    2. **Adds stack-trace noise.** Every propagation through such a
       site now has a "caused by:" frame for the wrapper.
    3. **Violates SEI CERT ERR07-J** — the very rule the detector is
       enforcing. ERR07-J exists so callers can recover from typed
       exceptions; wrapping hides the type. The SpotBugs maintainers
       articulate this directly in
       [spotbugs/spotbugs#3918](https://github.com/spotbugs/spotbugs/issues/3918):
       "rethrowing an exception that would have been thrown anyway"
       is fine; constructing a new wrapping exception is not.
  The detector itself is acknowledged as a false positive on the
  catch-rethrow pattern upstream;
  [PR #4087](https://github.com/spotbugs/spotbugs/pull/4087) is open
  to fix it. The right interim answer is a narrow
  `spotbugs-exclude.xml` `<Match>` with a lifecycle TODO to drop the
  suppression after the SpotBugs upgrade. BAF commit `40d3f09`
  applies this and is the reference implementation.

### Affects BAF + jllama (multi-package repos)
- **ArchUnit `layeredArchitecture().consideringAllDependencies()`** — both repos have leaf-package rules instead of the full form. BAF needs DTO/orchestration split (`Finder`, `Producer*`, `Consumer*`); jllama needs DTOs in a `value/` package. Both moves break public-API FQNs.
- **ArchUnit per-module banned-imports** — not implemented in either.
- **OPM scope-tightening — after package refactor.** fb-contrib
  `OPM_OVERLY_PERMISSIVE_METHOD` is suppressed PROJECT-WIDE in both BAF
  (`spotbugs-exclude.xml`) and jllama (`spotbugs-exclude.xml`) until the
  package refactor above settles. Rationale: the current single-root
  package groups production code so that every method called only by
  same-package callers is flagged as "should be package-private" — true
  today, false tomorrow once layers split, because cross-layer calls
  will need `public`. Tightening every site now creates churn the
  refactor will revert. **Re-enable this rule (delete the project-wide
  `<Match>` from each repo's `spotbugs-exclude.xml`) the same week the
  package layout stabilises.** At that point genuine "method exposed
  beyond its actual call site" findings become stable, fixable signals.
  Per-category breakdown at the moment of suppression (BAF, 33 sites):
  Main CLI internal helpers (~8), test-only public surface (~5),
  abstract-class constructors (~4), concrete-class constructors needing
  per-class audit (~5), internal helpers (~9), one enum.valueOf false
  positive. jllama: 25 sites of similar shape (not categorised in
  detail; will re-categorise when the suppression is lifted).

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
