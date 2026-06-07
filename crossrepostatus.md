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
| Tool versions | Identical across all 4: Checker 4.2.0, fb-contrib 7.7.4, findsecbugs 1.14.0, spotbugs 4.9.8.3, spotless 3.6.0, palantir 2.91.0, errorprone 2.49.0, nullaway 0.13.6, surefire 3.5.6, archunit 1.4.2, junit-jupiter 6.1.0, hamcrest 3.0, pitest-maven 1.25.3. **All on latest stable** (verified 2026-06-07 against Maven Central — see "Dependency / plugin freshness" below). |
| Maven Enforcer `bannedDependencies` | Identical 7-entry list |
| `<parameters>true</parameters>` javac arg | All 4 ✅ |
| PIT `<mutationThreshold>100</mutationThreshold>` | All 4 wired at a 100% gate. Scope expanded 2026-06-07 from the original single-class staging: **sb** whole-package · **jllama** `value.*`+`exception.*`+`args.*`+`json.TimingsLogger` (27 classes, 163 mutations) · **plugin** explicit 19-class list (138 mutations) · **BAF** explicit 16-class list (63 mutations). All previously pointed at one class; jllama's/BAF's were silently matching nothing after the package restructure (`llama.Pair`→`value.Pair`, `bitcoinaddressfinder.BitHelper`→`util.BitHelper`) — fixed. |
| Checker Framework as 2nd nullness pass | All 4 ✅ |
| JPMS `module-info.java` present | All 4 ✅ |
| ArchUnit standard set (`noSystemExit` / `noNewRandom` / `Thread.sleep` / sun-com.sun-jdk.internal bans / public-fields-final / `noTestFrameworksInProduction` / `noPackageCycles`) | All 4 ✅ |
| `javac -Werror` + `-Xlint:all,-serial,-options,-classfile,-processing` | All 4 ✅ |

## Deliberate non-parity (NOT drift)

- Plugin's NullAway `ExcludedFieldAnnotations` extension — repo-correct (Mojo POJOs).
- BAF's lack of module-level `@NullMarked` — documented intentional (per-package `@NullMarked` covers the same scope, avoids `requires JSpecify`).
- sb keeps per-package `@NullMarked` — by design.
- The PIT per-repo `targetClasses` scope differs (sb whole-package; the other three an explicit/glob list of classes verified at 100%) — intentional: each repo gates exactly the classes proven to reach 100% mutation parity, expanded incrementally. A handful of classes are *deliberately excluded* because they cannot reach 100% (equivalent or native-dependent mutants): plugin `support.AiPathSupport` (`getNameCount()` is always ≥1 → `>0` boundary is equivalent) and `provider.AiGenerationProviderFactory` (the `llamacpp-jni` branch loads a real GGUF model); jllama `json.RerankResponseParser` (non-array branch returns an already-empty list → EmptyObjectReturnVals is equivalent). (BAF `model.Hash160` *was* on this list — its `if(useFast)` selector mutant was equivalent because both hash paths return identical bytes — but it was refactored 2026-06-07 into two branch-free methods `hashFast`/`hashSlow` with `hash()` delegating to the fast one, removing the selector entirely; it now reaches 100% and is gated.)

---

## Recently closed (compact)

Rows that landed across every applicable repo. Kept here as a paper trail; not action items.

**Strictness ladder**

- Error Prone bug patterns → ERROR (12+ patterns): BAF ✅ · jllama `855f447` · plugin `034b553` · sb `ad95d66`.
- `javac -Werror` + `-Xlint:all,-serial,-options,-classfile,-processing`: BAF `2881c96` · jllama `3e2efbb` · plugin `f7cf748` · sb `7a4fbf0`.
- `-parameters` javac arg: BAF `pom.xml:315` · jllama `4350cf2` · plugin `7ae3279` · sb `912f14b`.
- `--release N` instead of `-source`/`-target`: BAF `c2470b7` + `1b67ad0` (`<release>21</release>`) · jllama `4350cf2` · plugin `7ae3279` · sb `912f14b`.
- PIT mutation threshold enforced (100%): BAF `BitHelper` · jllama `Pair` (`62f8a00`) · plugin `AiCompletionParser` · sb whole package. **Scope then expanded 2026-06-07** — see "PIT mutation-coverage expansion" under Open cross-repo items for the per-repo class counts and the new value/exception/args/support tests added to get there.
- Checker Framework 2nd nullness pass: BAF ✅ · jllama `c63870b` · plugin ✅ · sb `5a9be1b`.
- JPMS `module-info.java`: BAF `src/main/java9/` · jllama `0fd066a` / `9528e79` · plugin ✅ · sb ✅.
- Banned-API enforcement (Enforcer + ArchUnit): BAF ✅ · jllama `8baae0c` / `329d764` / `e6069da` · plugin `d654442` / `fd8cf80` / `ad37355` · sb `c0148c8` / `eaf4337`.
- ArchUnit standard set — `public-fields-final`, ban internal-JDK imports (`sun.*` / `com.sun.*` / `jdk.internal.*`), `noTestFrameworksInProduction`, `noPackageCycles`: BAF ✅ · jllama ✅ (`7b6667d`, `e6069da`) · plugin ✅ (`d2b1af9`, `ad37355`, `26a4f7b`) · sb ✅ (`5dd816d`, `de29bd4`, `bbdb505`).
- ArchUnit `loggersArePrivateStaticFinal`: BAF ✅ · jllama ✅ · plugin ➖ (Maven `Log`) · sb ➖ (no logging).
- ArchUnit leaf-layer rules: BAF ✅ (3 rules: `constantsPackageIsALeaf`, `configurationDoesNotDependOnRuntimeLayers`, `cliIsEntryPointOnly`) · jllama ✅ (`argsPackageIsALeaf`) · plugin ➖ (single-package) · sb ➖ (single-package).
- **SpotBugs `effort=Max` + `threshold=Low`** — permanently green at the gate across all four repos:
  - BAF `76fd1a7` — USBR-Lombok `6ddd69e` + CRLF layout `bd723f0` + WEM 3-batch `c2c3d62` / `4677831` / `dcee87d` + THROWS A/B/C `bd71766` + THROWS Group D `40d3f09` + DRE `5b72265` + 3× MDM structural refactors (AbstractProducer `892b76a`, ConsumerJava `99f390f`, ProducerOpenCL `09c5d52`) + MDM narrow suppression `cb02c70` + OPM project-wide suppression pending package refactor `52c8c95` + final 36-finding sweep `76fd1a7`.
  - jllama `c3a26b9` — InferenceParameters wither refactor `4f1fbd7` + `doNotUseGetters` sync `6ddd225` + remaining-findings sweep `14091bf` + gate-flip cleanup `c3a26b9`.
  - plugin `0bddf2a` — Lombok-USBR / HelpMojo auto-gen / Maven `@Parameter` SPP / identity-IMC / prompt-template FORMAT_STRING suppression chain + Lombok adoption, `Objects.requireNonNull` fail-fast, enriched WEM messages, presized HashMaps.
  - sb `4374dea` + `e7e254a` — all findings fixed at source (added `toString()`, contextful exception messages), no project-wide suppressions.

**Logging / observability**

- LogCaptor smoke test: BAF ✅ (LogCaptor 2.12.6, 7 tests) · jllama `3cedc6e` · plugin ➖ · sb ➖.

**Code-quality audits**

- `@VisibleForTesting` audit: BAF ✅ (10 sites legitimate) · jllama ➖ · plugin ➖ · sb ➖.
- Null-safety follow-up review: BAF ✅ (50 sites) · jllama ✅ (43 sites) · plugin ✅ (17 sites) · sb ✅ (zero `@Nullable` in production).
- Class / method naming review (21-item cross-repo audit) — see closed totals at the bottom.

**Cross-repo refactors**

- Workspace-shared guidelines layer: all 4 ✅.
- Standardised `CLAUDE.md` template: all 4 ✅.
- Versioned workspace guide chain (`guides/src/-8.md` + `-21.md`, `guides/test/-8.md` + `-21.md`): all 4 ✅.
- Audit-driven SKILL.md rewrite: all 4 ✅.
- Safe dependency / plugin bumps (latest round): BAF `59f7ff1` · jllama `0a97ae7` · plugin `93c7c84` · sb `3ccb426`.
- Per-repo `TODO.md` extraction (open work moved out of `CLAUDE.md`): all 4 ✅.
- Lombok 1.18.46 `@ToString` / `@EqualsAndHashCode` adoption (clears IMC_NO_TOSTRING + IMC_NO_EQUALS at SpotBugs Max+Low): BAF ✅ (56 classes, 0 handwritten Object methods left) · jllama `9be73a3` (23 classes) · plugin `39e1a59` + `6955357` (6 records + 19 annotated) · sb ➖ (excluded by design).
- Canonical `lombok.config` content incl. `doNotUseGetters = true` (see [`policies/lombok-config.md`](policies/lombok-config.md)): BAF `61e7996` · jllama `6ddd225` · plugin `3c61b88` · sb ➖.

---

## Open cross-repo items

| TODO item | BAF | jllama | plugin | sb |
|---|:--:|:--:|:--:|:--:|
| ArchUnit full `layeredArchitecture()` | ✅ — flat root package split into 10 layered packages; strict `layeredArchitecture()` rule enforced (Entry→Orchestration→Pipeline→Capabilities→InputOutput→Foundation→Config→Constants) | ✅ — flat root package split into layered packages (value/callback/exception/parameters/loader/json/args); strict `layeredArchitecture()` rule enforced (Api→Loader→Marshalling→Foundation) | ✅ — flat package split into 7 layered packages (mojo/indexer/provider/document/prompt/config/support); strict `layeredArchitecture()` rule enforced (Mojo→Indexer→Provider→Format→Foundation) | ➖ single-package |
| ArchUnit per-module banned-imports | ✅ — JOCL→opencl, ZeroMQ/WebSocket→keyproducer, LMDB→persistence+io | ✅ — Jackson banned from args/callback/exception/loader | ✅ — JNI→provider, Maven @Mojo/@Parameter→mojo, config+support Maven-free | ➖ single-package |
| Package hierarchy review | ✅ — layered package split landed (see BAF `TODO.md` "Done") | ✅ — layered package split landed (see jllama `TODO.md` "Done") | ✅ — layered package split landed (see plugin `TODO.md` "Done") | ➖ single-package |
| Typed-exception unification audit (constructor signatures + Javadoc shape consistent across every custom exception class) | ✅ — all 8 exceptions aligned: `AddressFormatNotAccepted` (precedent) + `InterruptedRuntimeException`; keyed exceptions (`KeyProducerIdIsNotUnique`/`Unknown`, `UnknownSecretFormat`, `PrivateKeyTooLarge`) gained the `(key…, cause)` matrix overload + tests; `KeyProducerIdNull` kept no-arg fixed-condition (bare `(Throwable)` would break the checklist's own rule); `NoMoreSecretsAvailable` already compliant; identity equality everywhere | ✅ — `LlamaException` / `ModelUnavailableException` already shape-compliant; added the missing `ModelUnavailableExceptionTest` | ➖ no custom exceptions (uses Maven `Mojo*Exception`) | ➖ no custom exceptions (uses `IOException`) |

> **What is actually still open (as of the 2026-06-07 refresh):** the table above is
> **complete** across every applicable repo (kept as a paper trail). The genuinely
> open work now is:
>
> 1. **Workspace-meta TODOs** (cross-repo, in `CLAUDE.md` → "Open TODOs"): drift-detection
>    hook, skill-discovery validation, maintenance cadence. ❌ open.
> 2. **PIT mutation-coverage expansion → 100% on ALL classes** (📌 all-time goal) — the gate
>    now covers a verified-100% subset in each repo and grows toward whole-package coverage
>    (the streambuffer model). See "Standing / all-time cross-repo goals" + the expansion
>    block below.
> 2b. **SonarQube local build check — per repo** (❌ open) — add an opt-in, locally-runnable
>    Sonar analysis to all four repos (see "Standing / all-time cross-repo goals").
> 3. **Per-repo feature/enhancement work** (NOT quality-gate) tracked in each repo's
>    `TODO.md`: **BAF** — persistence backends (open-addressing hash table, standalone
>    `BloomFilterPersistence`) + GPU acceleration (precompute HASHSET hash on GPU, push
>    `TRUNCATED_LONG_64` check into OpenCL, grid-size sweep benchmark); **jllama** —
>    Android AAR packaging, GraalVM Native Image eval, upstream feature toggles
>    (`spec-draft-backend-sampling`, MTP — deferred by policy); **plugin / sb** — none
>    beyond the cross-cutting reviews.
> 4. **Never-ending follow-ups** (📌 review-as-you-add): null-safety precision review and
>    the `@VisibleForTesting` / package / naming reviews in `policies/code-quality-todos.md`.

### PIT mutation-coverage expansion (cross-repo, incremental)

Status 2026-06-07 — gate raised from the original one-class staging to a verified-100%
subset per repo. All numbers from real `pitest-maven 1.25.3` runs (the 100% threshold
fails the build otherwise).

| Repo | Classes gated | Mutations | What's gated |
|---|:--:|:--:|---|
| sb | whole package | — | entire `net.ladenthin.streambuffer` (pre-existing) |
| jllama | 27 | 163 | `value.*` (16) + `exception.*` (2, 0 mutations) + `args.*` enums (10) + `json.TimingsLogger` |
| plugin | 19 | 138 | config/document/prompt/provider/support value + support classes |
| BAF | 16 | 63 | `util.BitHelper` + model (incl. refactored `Hash160`) + 8 exception classes + `statistics.*` + `CKeyProducerJavaIncremental` |

New tests added to reach 100% (no production code changed): jllama
`ChatChoiceTest`/`ToolCallTest`/`ToolDefinitionTest`/`ContinuationModeTest` + expanded
`ChatMessageTest`/`ServerMetricsTest`/`ModelMetaTest`/`TokenLogprobTest`/`ChatResponseTest`/`CompletionResultTest`;
plugin `Java8CompatibilityHelperTest`/`MockAiGenerationProviderTest`/`AiPromptSupportTest`/`AiPathSupportTest`/`AiChecksumSupportTest`/`AiMdChildEntryLineFormatterTest`/`AiPreparedPromptTest`/`AiGenerationConfigTest`/`AiModelDefinitionTest`
+ expanded `AiModelDefinitionSupportTest`/`AiMdHeaderSupportTest`; BAF needed no new tests
(existing tests already gave 100%).

**Still open (optional, each needs more involved fixtures):** jllama `json.ChatResponseParser`
/ `CompletionResponseParser` (a few private-helper survivors); plugin `document.AiMdDocumentCodec`
/ `AiMdHeaderCodec` / `prompt.AiPromptPreparationSupport`; BAF config getters covered only by
producer/keyproducer integration tests, plus the larger orchestration classes (producer /
consumer / engine / opencl). Equivalent/native-dependent classes are excluded by design (see
"Deliberate non-parity").

### Standing / all-time cross-repo goals

**📌 All-time goal — drive every project to 100% PIT mutation coverage on ALL classes.**
❌ open (never-finished quality ratchet). The end state is the **streambuffer model**:
`<targetClasses>` covering the *whole* production package (not a curated subset) at
`<mutationThreshold>100</mutationThreshold>`. Today only **sb** is whole-package; **jllama**,
**plugin** and **BAF** gate a verified-100% subset that grows incrementally (see the
expansion block above). Reaching the goal means, per repo: add tests for every remaining
class until its mutants are killed, then widen `targetClasses` from the explicit list to the
full package glob. The *only* permitted exclusions are genuinely unkillable mutants
(equivalent or native/model-dependent — see "Deliberate non-parity"), and every exclusion
must be listed with its rationale. Any newly added class must reach 100% before/at merge so
the gap never regrows. Track per-repo progress in each repo's `TODO.md` "Mutation-testing
threshold expansion" item.

**❌ SonarQube local build check — per repo.** open. Add a locally-runnable SonarQube
analysis to all four repos so contributors can scan before pushing, mirroring the existing
local gates (spotless, spotbugs, pitest). Per-repo scope:
- Add `org.sonarsource.scanner.maven:sonar-maven-plugin` (pinned version) under an **opt-in
  `sonar` profile** in each `pom.xml` (kept off the default build — it needs a running
  server), plus a documented recipe in the repo `CLAUDE.md` "Build Commands" section.
- Ensure a **JaCoCo XML** report is produced so Sonar ingests line/branch coverage. BAF
  already emits JaCoCo (`./mvnw test jacoco:report`); confirm/add the `jacoco-maven-plugin`
  `report` (and `report-integration` where relevant) binding in jllama, plugin and sb.
- Document the local run: start SonarQube (Docker `sonarqube:lts-community`), create a token,
  then `mvn verify -Psonar sonar:sonar -Dsonar.host.url=http://localhost:9000 -Dsonar.token=…`.
- Leave Sonar **out of CI** for now (separate later step); this item is only the local,
  opt-in developer check.
- Lombok-using repos: the `@Generated`/`lombok.addLombokGeneratedAnnotation` skip is already
  documented in [`policies/lombok-config.md`](policies/lombok-config.md) so Sonar ignores
  synthetic getters/`equals`/`toString`.

### Dependency / plugin freshness (verified 2026-06-07)

All four repos are on the **newest stable** versions of every dependency and build plugin
(checked with `versions:display-dependency-updates` + `display-plugin-updates` against
Maven Central, and direct `maven-metadata.xml` probes for the annotation-processor paths the
versions plugin does not scan: Error Prone, NullAway, Checker). The only "updates" offered are
**pre-releases** — Maven 4 plugin `4.0.0-beta-*` (compiler/jar/source/resources/plugin),
`maven-surefire-plugin:3.6.0-M1`, `slf4j-api:2.1.0-alpha1`, Maven-core `4.0.0-rc-5` — which are
deliberately **not** adopted, plus **jqwik 1.10.1** which is 📌 **banned** (see policy). No
action needed.

**Layered-rule sharpening (jdeps fact-based audit, done):** the compiled package
graph of all three multi-package repos was audited with `jdeps` (bytecode, not
imports — Javadoc `{@link}` imports do not count). Findings: **BAF** had one latent
upward edge (`util.Bech32Helper` → `io.AddressTxtLine.BITCOIN_CASH_PREFIX`, hidden
from ArchUnit by `static final String` inlining) — fixed by moving the constant to
`constants.AddressConstants`, after which the `layeredArchitecture()` access lists
were tightened to the exact per-layer accessor set. **jllama** and **plugin** were
already exact (each layer's `mayOnlyBeAccessedByLayers` matched the real graph) — no
slack and no hidden edges found.

**One-package-per-layer strict layering (done):** BAF, jllama and plugin each replaced
their coarse-tier `layeredArchitecture()` with a maximally-strict version where every
package is its own layer and `mayOnlyBeAccessedByLayers` lists the exact accessor set
(from the bytecode graph) — intra-tier edges are now governed too (e.g. `model→util` but
not the reverse; `opencl`/`persistence` cannot reach each other).

**CI code-style gate (done, all 4 repos):** root-caused a publish-snapshot failure —
`spotless:check` is bound to `verify`, which only the publish `deploy` goal reaches, so
unformatted code passed every earlier job and failed only at publish. Added a fast
`code-style` job (`needs: startgate`) running `mvn spotless:check` early and made
`publish-snapshot`/`publish-release` depend on it. The same job also prints the internal
package graph via `jdeps` (informational, `continue-on-error`); the bytecode-level
layering itself is already enforced by the ArchUnit rules in `mvn test`.

**Standing policy:** DO NOT UPGRADE jqwik past 1.9.3 — 📌 active in all 4 repos (see [`policies/jqwik-prompt-injection.md`](policies/jqwik-prompt-injection.md)).

---

## Long-form references for open items

The open table above points here for the detailed rationale and checklists.

### Typed-exception unification audit (all 4 repos)

Every custom exception class
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

### Package-layout refactor side-effects (BAF + jllama)

The full `layeredArchitecture()` rule and the per-module banned-imports
rule (open rows above) both depend on splitting today's single-root
package into layered packages. **BAF: DONE** — the flat root package
(`Finder`, `Producer*`, `Consumer*`, and ~45 other classes) was split
into 10 layered packages and the strict `layeredArchitecture()` rule is
enforced (see BAF `TODO.md` "Done"). **jllama: DONE** — the flat root
package was split into `value`/`callback`/`exception`/`parameters`/`loader`
(+ existing `json`/`args`) and the strict `layeredArchitecture()` rule is
enforced (see jllama `TODO.md` "Done"). Both moves break public-API FQNs
and ship under a major-version bump.

**OPM scope-tightening — after package refactor.** fb-contrib
`OPM_OVERLY_PERMISSIVE_METHOD` is suppressed PROJECT-WIDE in both BAF
(`spotbugs-exclude.xml`) and jllama (`spotbugs-exclude.xml`). **BAF:
unblocked but optional** — the package refactor it waited on has landed,
so cross-layer call sites are now stable and OPM findings would be
actionable. Re-enabling is optional, not mandated: visibility
minimisation is NOT a project goal (the tightening pressure was
fb-contrib noise, not an owner requirement). **jllama: also unblocked**
— its package split has now landed too; re-enabling OPM is optional for
the same reason. Rationale for the original suppression: a
single-root package flags every method called only by same-package
callers as "should be package-private" — true today, false once layers
split because cross-layer calls need `public`. If BAF re-enables, delete
its project-wide `<Match>` and triage (~33 sites: Main CLI internal
helpers ~8, test-only public surface ~5, abstract-class constructors ~4,
concrete-class constructors ~5, internal helpers ~9, one enum.valueOf
false positive). jllama: 25 sites of similar shape, deferred until its
split.

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
