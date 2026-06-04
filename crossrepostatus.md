# Cross-Repo Status Table — VERIFIED

> **Last full source verification:** 2026-06-04 (this session). Every
> ✅ / ❌ in the universal-strictness section and the naming-audit
> section was re-checked against actual `pom.xml`, source files, and
> `ArchitectureTest` content on the current `claude/vigilant-gauss-7jXfW`
> branch in each of the four sibling repos. The "fresh-verification
> deltas" subsection just below lists what changed since the previous
> session's snapshot.
>
> **For a future session**: the recommended next-task list lives in the
> **"Quick prioritisation (cheapest → biggest)"** section near the bottom
> — start there to pick up work. The richer per-repo design context lives
> in each repo's own `CLAUDE.md` Open-TODOs section (especially BAF's
> persistence/GPU TODOs and jllama's strictness-ladder commit ledger).

Repos:
- **BAF** = `/home/user/BitcoinAddressFinder`
- **jllama** = `/home/user/java-llama.cpp`
- **plugin** = `/home/user/llamacpp-ai-index-maven-plugin`
- **sb** = `/home/user/streambuffer`

Legend: ✅ done · ❌ open · ➖ N/A · 📌 standing policy

> **Audit method**: each row verified by reading `pom.xml`, source files, and `git rev-parse` against the working tree on the current branch. Seed claims that were wrong are flagged with → and the corrected state. See `/home/user/cross-repo-status-AUDIT-LOG.md` for the per-row evidence trail.

---

## Fresh-verification deltas (this session, 2026-06-04)

Each item below was re-scanned against actual source code today; the
status table further down has been updated accordingly.

**Audit-count drift** (counts moved since the last snapshot):

| Metric | Last snapshot | Actual today | Why it moved |
|---|---|---|---|
| BAF `@VisibleForTesting` usages | 19 sites × 6 files | **10 sites × 5 files** | 9 sites cleared this session: 3 misapplied annotations dropped (`05d9ddf`); 5 executor / lifecycle sites converted to test-friendly constructors (`dda12e3`, `1855f8e`×2, `4e83f88`, `98aab98`); `Main.runLatch` made `private` and annotation dropped (`2d99c4a`); `ConsumerJava.shouldRun` field replaced by getter (`dc839bd` + `85cc8ae`); `BIP39KeyProducer.counter` replaced by ctor parameter (`ece579f`); the 2 mutable-static `AWAIT_DURATION_*` fields migrated to config (`51ac43c`). The 10 remaining sites are **all legitimate**: 4 test-friendly constructors (intended use), 4 `Main.FILE_EXTENSION_*` constants referenced symbolically by same-package tests, `Main.getRunLatch()` (public, annotation = pure doc), `ConsumerJava.keysQueueSize()` (single-line getter). |
| BAF LogCaptor test files | 5 | **7** | Two LogCaptor users added since the snapshot. |
| BAF `@Nullable` sites in production | 53 | **50** | 3 sites removed as types tightened (no regressions; deep scan still finds the remainder legitimate). |
| BAF stale `loadToMemoryCacheOnInit` example JSONs | 3 | **0 — RESOLVED** | Original list was 3, actual was 4 (`config_AddressFilesToLMDB.json` was the missed one); all 4 lines deleted this session, JSON validity verified. Default backend remains `BLOOM` per `CLMDBConfigurationReadOnly.java:43`. |
| BAF `Find` example configs surface await-duration knobs | hidden behind defaults | **all 4 explicit** | `d199ad7` (this session). Each of `config_Find_1OpenCLDevice.json`, `config_Find_1OpenCLDeviceAnd2CPUProducer.json`, `config_Find_8CPUProducer.json`, `config_Find_SecretsFile.json` now lists both `awaitTerminateSeconds: 31536000000` and `awaitQueueEmptySeconds: 60` (production defaults preserved byte-for-byte). Guard test `cli/ConfigFixturesParseTest` fails-loud if anyone strips them back out. |
| sb `@Nullable` "zero in production" claim | 0 | **0 actual annotations** (2 grep hits are in Javadoc text, not annotations) — claim **stays accurate**. |

**Items confirmed unchanged (still open, no source movement):**

- ~~BAF: `Finder.AWAIT_DURATION_TERMINATE` and `ConsumerJava.AWAIT_DURATION_QUEUE_EMPTY` are still package-private, non-final, mutable statics~~ ✅ **FIXED** this session (BAF commit `51ac43c`) — both mutable statics removed; replaced with `CFinder.awaitTerminateSeconds` (long, default ~100 k years) and `CConsumerJava.awaitQueueEmptySeconds` (long, default 60). Tests now inject the shortened timeout via the config POJO they construct anyway. `java.time.Duration` / `java.time.temporal.ChronoUnit` imports dropped from both production classes; `@VisibleForTesting` dropped from the call sites. Test-order hazard eliminated.
- ~~BAF: `Main.runLatch` is still package-private~~ ✅ **FIXED** this session (`2d99c4a`) — field is now `private final`, `@VisibleForTesting` annotation dropped; tests reach state via the public `getRunLatch()` getter at `Main.java:84`.
- ~~BAF: All five executor / lifecycle fields flagged for constructor injection~~ ✅ **ALL 5 CLOSED** this session via the audit-recommended test-friendly-constructor pattern (and an `isInitialized()` getter for the lifecycle handle):
  - `Finder.producerExecutorService` — `dda12e3` (3 FinderTest sites now construct an injected `ExecutorService`)
  - `ConsumerJava.scheduledExecutorService` + `consumeKeysExecutorService` — `1855f8e` (both injected via a new 5-arg constructor; `ConsumerJavaTest` 2 methods + `LMDBPersistencePerformanceTest` 1 method updated)
  - `ProducerOpenCL.resultReaderThreadPoolExecutor` — `4e83f88`
  - `ProducerOpenCL.openCLContext` — `98aab98` (different pattern: exposed `isInitialized()` boolean rather than full injection, since it is a lifecycle handle not an executor)
- ~~BAF: `ConsumerJava.shouldRun` direct field access~~ ✅ **FIXED** this session — first added an `isRunning()` getter (`dc839bd`), then corrected to `shouldRun()` (`85cc8ae`) after realising the field is a cancellation-request flag, not a thread-liveness observation.
- ~~BAF: `BIP39KeyProducer.counter` field-mutation seam~~ ✅ **FIXED** this session (`ece579f`) — counter is now constructor-injected via the new `startingIndex` parameter; the test no longer mutates the field directly to force overflow.
- ~~BAF: 4 naming-audit MODERATE/MINOR findings still in source: `BitHelper.getKillBits` (`:35`), `LMDBPersistence.getAllAmountsFromAddresses` (interface + impl), `OpenCLBuilder.isOpenCLnativeLibraryLoadable` (`:229`), `PrivateKeyValidator.returnValidPrivateKey` (`:89`).~~ ✅ **ALL 4 FIXED this session** — commits `2509988`, `8ff90c9`, `81dd95b`, `a6531c9`.
- ~~plugin: `LlamaCppJniAiSummaryProvider` file still present~~ ✅ RESOLVED this session — renamed to `LlamaCppJniAiGenerationProvider` (`3007f03`); Mojo `@Parameter` field and Maven property renamed too. ~~`AiGenerationResult` shape/name~~ ✅ confirmed correct — body-only is the deliberate final state of a 2-step refactor; CLAUDE.md drift was the actual bug (fixed in `371faa6` + `09067a2`).
- jllama: `setSpecDraftBackendSampling` — zero matches in `src/main/java` — confirmed still ❌ (deferred by policy).
- All four repos: SpotBugs is on `effort=Default`, `threshold=Default` (BAF `:648-649`, jllama `:572-573`, plugin `:551-552`, sb `:541-542`) — confirmed ❌.
- All four repos: zero `layeredArchitecture()` references in any `ArchitectureTest.java` — confirmed ❌.

**Items confirmed DONE in source (matches the ✅ rows below):**

- All four repos have 13 distinct `-Xep:<Name>:ERROR` patterns wired (table seed said 12; actual count is 13 because one earlier rename happened upstream — minor; the substance is correct).
- `-Werror`: jllama, plugin, sb have it set in `<arg>-Werror</arg>` (jllama `pom.xml:366`, plugin `:341`, sb `:351`); BAF has comments saying "intentionally NOT set yet" (BAF `:320`) — matches "❌ not yet flipped" status.
- `<parameters>true</parameters>`: present in all four `pom.xml`.
- `<release>` for main compile: ✅ jllama `:347`, ✅ plugin `:323`, ✅ sb `:328`, ✅ BAF (closed in this session: `pom.xml:313` is now `<release>21</release>`; blocker was `ByteBufferUtility.java`'s `jdk.internal.misc.Unsafe` import, resolved by migrating to reflectively-resolved `sun.misc.Unsafe` with `@Nullable UNSAFE` field for non-HotSpot JVM portability — BAF commits `c2470b7` + `1b67ad0`).
- PIT `<mutationThreshold>100</mutationThreshold>` wired in all four.
- Checker Framework wired in all four.
- `module-info.java` present in all four; module-level `@NullMarked` confirmed on jllama, plugin, sb (line `@org.jspecify.annotations.NullMarked` before `module ...`); BAF deliberately omits it (BAF `module-info.java:26` has no `@NullMarked` — matches the "intentionally NOT added" stance documented in BAF CLAUDE.md).
- Maven Enforcer rules wired in all four; ArchUnit `ArchitectureTest.java` present in all four with `noSystemExit` / `noNewRandom` / `Thread.sleep` / sun/com.sun/jdk.internal bans + public-fields-final rule.
- BAF persistence implementations all in place: `HashSetAddressPresence`, `TruncatedLong64SortedArrayPresence`, `BloomFilterAccelerator`, `AddressLookupBackend` enum, `AddressPresence` + `AddressLookup` interfaces, `AddressLookupBenchmarkTest`. The benchmark is still under `persistence/` (JUnit timing test) — NOT migrated to JMH `benchmark/` module. `HashSetPrecomputedHashAddressPresence` does NOT exist yet. `GridSizeSweepBenchmark` IS present in `benchmark/`.
- jllama: `setSkipDownload` (`ModelParameters.java:1448`), `ModelUnavailableException`, `SkipDownloadFailureTranslator`, `LoggingSmokeTest`, `docs/feature-investigation-similar-projects.md`, README platform badge + similar-projects section — all confirmed in place.
- sb: `getAvailableBytesExact()` at `:236` confirmed. All 7 naming-audit fixes confirmed (`validateOffsetAndLength*`, `shouldTrim`, `getBufferElementCount`-only, `waitForAtLeast`/`waitForAnyData`, `hasNoMissingBytes`, "unsecure" typo, `getBufferSize` deletion).
- plugin: `AiCompletionParser.java` present (rename from `AiResponseNormalizer` done); `AiChecksumSupport` correctly uses CRC32 (`import java.util.zip.CRC32` at line 10).
- jllama: `isUnset` (was `isDefault`) confirmed at `ModelParameters.java:1463`.

**This session's new wins (already in the table below):**

- Workspace shared layer (canonical guides, skill, policies, workflows, template) ✅
- Versioned guide chain (`guides/src/{-8,-21}.md`, `guides/test/{-8,-21}.md`) ✅
- Audit-driven SKILL.md rewrite (replaced 961 lines of fictional JUnit 4 content with Jupiter-first content matching BAF + sb actual conventions) ✅
- Safe dependency bumps (logback patch, checker 4.2.0, fb-contrib 7.7.4, spotless 3.6.0, palantir 2.91.0, pitest 1.25.3 + surefire 3.5.6 for sb) ✅
- BAF naming-audit follow-up renames beyond the original 4-item table:
  - `KeyUtility.killBits` → `alignDown` (`cd72083`) + comprehensive Javadoc rewrite explaining the batch-alignment use case
  - `OpenCLPlatformAssume.assumeOpenCLLibraryLoadable*` → `assumeOpenClLibraryAvailable*` (`15279d4`) — 31 references / 8 files; resolves the post-rename inconsistency between assume name and underlying `isOpenClNativeLibraryLoaded` check
- BAF compile fix: stale `killBits` variable reference inside the trace-log branch of `AbstractProducer.createSecretBase` (`7180ea2`) — missed in the earlier `getKillBits` → `getLowBitMask` rename because the variable rename only updated the `keyUtility.killBits(...)` call line, not the `LOGGER.trace("killBits: " + killBits.toByteArray())` reference 8 lines below.

---

## VERIFIED TABLE

| TODO item | BAF | jllama | plugin | sb |
|---|:--:|:--:|:--:|:--:|
| **Strictness ladder** | | | | |
| Error Prone bug patterns → ERROR (12 patterns) | ✅ verified (was seed ❌) | ✅ `855f447` | ✅ `034b553` | ✅ `ad95d66` |
| `javac -Werror` + `-Xlint:all,-serial,-options` | ❌ not yet flipped (items 1–6 cleared; ready) | ✅ `3e2efbb` | ✅ | ✅ `7a4fbf0` |
| `-parameters` javac arg | ✅ `pom.xml:315` (was seed ❌) | ✅ `4350cf2` | ✅ `7ae3279` | ✅ `912f14b` |
| `--release N` instead of `-source`/`-target` | ✅ `<release>21</release>` at `pom.xml:313` (BAF commits `c2470b7` + `1b67ad0`). Blocker was `ByteBufferUtility.java:9` directly importing `jdk.internal.misc.Unsafe`; resolved by migrating to reflectively-resolved `sun.misc.Unsafe` (always-exported via `jdk.unsupported`). Defensive design: `@Nullable Unsafe UNSAFE` field — static initializer wraps reflective lookup in try/catch so non-HotSpot JVMs (OpenJ9, GraalVM Native Image, Android) get `UNSAFE == null` rather than `ExceptionInInitializerError`; `freeByteBuffer` gains a null guard so it becomes a no-op on those platforms (JVM Cleaner handles the buffer naturally). `default-testCompile` overrides back to `<source>/<target>` so tests can keep importing `jdk.internal.ref.Cleaner` and `sun.nio.ch.DirectBuffer` to assert Cleaner invocation. | ✅ `4350cf2` | ✅ `7ae3279` | ✅ `912f14b` |
| PIT mutation threshold enforced (100%) | ✅ `BitHelper` (`pom.xml:711-717`) | ✅ `Pair` (`62f8a00`) | ✅ `AiCompletionParser` (renamed from `AiResponseNormalizer` in `6567b9e`) | ✅ whole package |
| Checker Framework 2nd nullness pass | ✅ NullnessChecker + `objects.astub` | ✅ `c63870b` | ✅ | ✅ `5a9be1b` |
| JPMS `module-info.java` | ✅ `src/main/java9/module-info.java` | ✅ `0fd066a`/`9528e79` (module-level `@NullMarked`) | ✅ — module-level `@NullMarked` set in module-info; CLAUDE.md note corrected in `9be6f17` | ✅ |
| Banned-API enforcement (Enforcer + ArchUnit) | ✅ Enforcer @ `pom.xml:268-283`; ArchUnit `noSystemExit`/`noNewRandom`/`Thread.sleep` (was seed ❌) | ✅ `8baae0c`/`329d764`/`e6069da` | ✅ `d654442`/`fd8cf80`/`ad37355` | ✅ `c0148c8`/`eaf4337` |
| ArchUnit public-fields-final | ✅ `ArchitectureTest:120-130` (was seed ❌) | ✅ `7b6667d` | ✅ `d2b1af9` | ✅ `5dd816d` |
| ArchUnit ban internal-JDK imports (`sun.*`/`com.sun.*`/`jdk.internal.*`) | ✅ `ArchitectureTest:90-97` | ✅ `e6069da` | ✅ `ad37355` | ✅ `de29bd4` |
| ArchUnit `layeredArchitecture()` | ✅ `bd58221` + `ca75527` (this session) — 4 rules: `constantsPackageIsALeaf`, `configurationDoesNotDependOnRuntimeLayers`, `eckeyIsLowLevelCrypto`, `cliIsEntryPointOnly`. The full `Architectures.layeredArchitecture()` form was deferred: after extracting `Secp256k1Constants` into the new `constants/` leaf package and inlining `CProducer.getOverallWorkSize(BitHelper)`, only one `configuration → root` edge remains (`CKeyProducerJava.maxWorkSize` → `PublicKeyBytes.BIT_COUNT_FOR_MAX_CHUNKS_ARRAY`, a Java array-size cap that is a producer-layer concern, not a secp256k1 spec value). Eliminating that edge requires extracting producer-layer constants into another leaf — captured in `policies/code-quality-todos.md` §4 as the cross-repo package-architecture refactor TODO. | ✅ `e673471` (this session) — as `argsPackageIsALeaf` (narrower). `json` parsers/serializers and root API are peers (each side depends on the other via DTOs / parser usage), not stackable. Full layered form requires splitting DTOs into a dedicated `value/` package, which breaks published public-API FQNs — see `policies/code-quality-todos.md` §4. | ➖ single-package (all production code in `aiindex`) | ➖ single-package |
| ArchUnit per-module banned-imports | ❌ | ❌ | ➖ single-package | ➖ single-package |
| SpotBugs `effort=Max` + `threshold=Low` | ❌ both `Default` | ❌ both `Default` | ❌ both `Default` | ❌ both `Default` |
| **Logging / observability** | | | | |
| LogCaptor smoke test | ✅ LogCaptor 2.12.6 + used in 7 tests (re-verified 2026-06-04; up from 5) | ✅ `3cedc6e` | ➖ no logging | ➖ no logging |
| **This session's additions (sb)** | | | | |
| `getAvailableBytesExact()` public long getter | ➖ | ➖ | ➖ | ✅ `aa5c6b8` — closes the >2 GB live-count API gap; verified across 441-commit upstream history that no equivalent ever existed before |
| **Code-quality audits (continuous)** | | | | |
| `@VisibleForTesting` audit (count, re-verified 2026-06-04) | **10 usages × 5 files** (down from 19×6 — 9 sites cleared this session; remaining 10 are all legitimate per the site-by-site audit below) | 0 | 0 | 0 |
| `@VisibleForTesting` design-fit review | ✅ done this session — all REFACTOR-VIA-INJECTION (7 sites) + REFACTOR-EXTRACT-HELPER (2 sites) closed. Remaining sites are the 4 `FILE_EXTENSION_*` constants (legitimate same-package access), the public `getRunLatch()`/`keysQueueSize()` getters (annotation = pure doc, no access widening), and 4 test-friendly constructors (textbook `@VisibleForTesting` usage). | ➖ no usages | ➖ no usages | ➖ no usages |
| Null-safety follow-up review (re-verified 2026-06-04) | ✅ 50 `@Nullable` sites (down from 53), all legitimate | ✅ 43 sites all legitimate | ✅ 17 sites all legitimate | ✅ zero `@Nullable` annotations in production (2 grep hits are Javadoc text only) |
| Package hierarchy review | ❌ | ❌ | ❌ | ❌ |
| Package-architecture refactor + full `layeredArchitecture()` rule (see `policies/code-quality-todos.md` §4) | ❌ — much smaller after `ca75527`: only `BIT_COUNT_FOR_MAX_CHUNKS_ARRAY` producer-layer constant remains in the root package; extracting it into a new `producer-constants` (or similar) leaf would close the last config→root edge. Root-package split into `core`/`orchestration` still pending. | ❌ — needs DTO split into `value/` package (breaks public-API FQNs) | ➖ single-package | ➖ single-package |
| Class / method naming review (21-item cross-repo audit) | ✅ 6/6 + 2 follow-ups (`alignDown`, `assumeOpenClLibraryAvailable*`) — see "BAF section" below | ✅ 1/1 (`isDefault` → `isUnset` `ffbc06c`) | ✅ 7/7 — see "plugin section" below | ✅ 7/7 (typo `966595c` + bundle `cf2b5fd` + cleanups `16f1df7`) |
| **Cross-repo refactors** | | | | |
| Workspace-shared guidelines layer (Java code/test conventions) | ✅ (this session) | ✅ (this session) | ✅ (this session) | ✅ (this session) |
| Standardised `CLAUDE.md` template | ✅ (this session) | ✅ (this session) | ✅ (this session) | ✅ (this session) |
| Versioned workspace guide chain (`guides/src/-8.md` + `-21.md`, `guides/test/-8.md` + `-21.md`) | ✅ (this session) | ✅ (this session) | ✅ (this session) | ✅ (this session) |
| Audit-driven SKILL.md rewrite (replaced fictional JUnit 4 / `DataProviderRunner` content with actual Jupiter + Hamcrest + `@MethodSource` stack) | ✅ (this session) | ✅ (this session) | ✅ (this session) | ✅ (this session) |
| Safe dependency / plugin bumps (logback patch, checker 4.2.0, fb-contrib 7.7.4, spotless 3.6.0, palantir 2.91.0, pitest 1.25.3 + surefire 3.5.6 for sb) | ✅ `59f7ff1` | ✅ `0a97ae7` | ✅ `93c7c84` | ✅ `3ccb426` |
| **Naming audit follow-ups (this session)** | | | | |
| BAF naming-audit MODERATE/MINOR (4-item set) | ✅ all 4 fixed: `getKillBits` → `getLowBitMask` `2509988`; `getAllAmountsFromAddresses` → `sumAmountsForAddresses` `8ff90c9`; `isOpenCLnativeLibraryLoadable` → `isOpenClNativeLibraryLoaded` `81dd95b`; `returnValidPrivateKey` → `coerceToValidPrivateKey` `a6531c9` | ➖ | ➖ | ➖ |
| BAF naming-audit follow-ups (deeper review) | ✅ `KeyUtility.killBits` → `alignDown` + Javadoc rewrite explaining the GPU batch-alignment use case (`cd72083`); `OpenCLPlatformAssume.assumeOpenCLLibraryLoadable*` → `assumeOpenClLibraryAvailable*` (31 references / 8 files, `15279d4`); compile fix for stale variable reference in `AbstractProducer` trace-log branch (`7180ea2`) | ➖ | ➖ | ➖ |
| Plugin naming-audit MODERATE/MINOR (5-item set) | ➖ | ➖ | ✅ all 5 closed (deep git-history investigation): `AiSummaryResponse` DELETED `f11eb6b` (stillborn DTO, never constructed in 266 commits); CLAUDE.md `s`/`k` header-field drift fixed `371faa6` + `09067a2` (refactor 3 months old, docs were stale); `AiMdHeaderSupport` split → `AiMdChildEntryLineFormatter` `856c085`; `AiGenerationResult` shape confirmed correct (body-only is final state of 2-step refactor); `LlamaCppJniAiSummaryProvider` → `LlamaCppJniAiGenerationProvider` `3007f03` (incl. Mojo `@Parameter summaryProvider` → `generationProvider` + Maven property + `pom.xml:672` self-test + README + TEST_WRITING_GUIDE + CLAUDE.md). `AiPromptSupport` kept after sibling-pattern review with `AiModelDefinitionSupport`. | ➖ |
| BAF README documentation: `batchSizeInBits` section + Full-DB backend warning + drop phantom `SORTED_ARRAY` reference | ✅ `8540157` (this session) + `4a49ea7` (Full-DB ⚠ hint + SORTED_ARRAY drop) + `eab518b` (explicit `addressLookupBackend: BLOOM` in 3 Find configs) + `3c4d558` (deleted dead `loadToMemoryCacheOnInit` from 4 example JSONs) | ➖ | ➖ | ➖ |
| BAF `@VisibleForTesting` design-fit follow-ups: small cleanups | ✅ `Main.runLatch` field-to-private + `-Werror` comment refresh `2d99c4a`; `ConsumerJava.shouldRun()` getter `dc839bd` + naming correction `85cc8ae` | ➖ | ➖ | ➖ |
| BAF `@VisibleForTesting` executor / lifecycle injection (5 audit rows) | ✅ all 5 closed via test-friendly-constructor pattern: `Finder.producerExecutorService` `dda12e3`; `ConsumerJava.scheduledExecutorService` + `consumeKeysExecutorService` `1855f8e`; `ProducerOpenCL.resultReaderThreadPoolExecutor` `4e83f88`; `ProducerOpenCL.openCLContext` → `isInitialized()` getter `98aab98` (lifecycle handle, not an executor) | ➖ | ➖ | ➖ |
| BAF `BIP39KeyProducer.counter` constructor injection | ✅ `ece579f` — test no longer mutates the field directly to force overflow | ➖ | ➖ | ➖ |
| BAF mutable-static `AWAIT_DURATION_*` → config fields | ✅ `51ac43c` — `Finder.AWAIT_DURATION_TERMINATE` + `ConsumerJava.AWAIT_DURATION_QUEUE_EMPTY` migrated to `CFinder.awaitTerminateSeconds` / `CConsumerJava.awaitQueueEmptySeconds` (long). Test-order hazard eliminated. `java.time.Duration` import dropped from both production classes. Plus `d199ad7`: all 4 `config_Find_*.json` example fixtures now carry the fields explicitly (production defaults preserved) so operators see them in the file; `cli/ConfigFixturesParseTest` guards against silent regression. | ➖ | ➖ | ➖ |
| **BAF-specific big items** | | | | |
| `-Werror` items 1–6 (BAF-internal pre-`-Werror` list) | ✅ all six cleared (`6eadc6f`) | ➖ | ➖ | ➖ |
| Persistence-backends research/implementation | ✅ HashSet snapshot, BloomFilterAccelerator extraction, TRUNCATED_LONG_64, AddressLookupBackend config enum, AddressPresence/AddressLookup chain contract, AddressLookupBenchmarkTest, 4 stale `loadToMemoryCacheOnInit` example JSONs cleaned up (`3c4d558`). Remaining open: JMH migration of the benchmark; open-addressing hash table backend; standalone Bloom-only backend; `HashSetPrecomputedHashAddressPresence` (Pre-compute HASHSET hash item). | ➖ | ➖ | ➖ |
| Pre-compute HASHSET hash on GPU | ❌ design captured (CLAUDE.md) | ➖ | ➖ | ➖ |
| End-to-end GPU scan north star | ❌ vision captured | ➖ | ➖ | ➖ |
| Push TRUNCATED_LONG_64 presence check into OpenCL | ❌ design captured | ➖ | ➖ | ➖ |
| GraalVM Native Image evaluation (CLI / serverless / fast-startup target) | ➖ | ❌ design captured in `23f8756` (this session) | ➖ | ➖ |
| README polish: platform badge + pure-Java sibling-projects subsection | ➖ | ✅ `23f8756` (this session) | ➖ | ➖ |
| Feature investigation across 6 similar projects (5 pure-Java + llamacpp4j) | ➖ | ✅ `7b8cf74` (this session) — ships `docs/feature-investigation-similar-projects.md`; 18 candidate items with effort × priority backlog. Recommended first batch: UTF-8 boundary decoder + per-run timing line + jbang example + system-properties README table. | ➖ | ➖ |
| GPU grid-size JMH benchmark (idea from cjherm/BAF23 fork) | ✅ **DONE** in `b9f475a` + `11c8868` (this session). `GridSizeSweepBenchmark` ships under `src/test/java/.../benchmark/` (compile-clean; runs on the owner's GPU host). The fork's companion **context-reuse / init-cost-amortisation sweep** (`CtxRoundsIteratorBenchmark`) was inspected and **explicitly rejected as inapplicable** to BAF — `ProducerOpenCL` creates one `OpenCLContext` for the lifetime of a scan session (10⁶+ launches per init), so the amortisation curve has no operator-actionable value. Rationale recorded in CLAUDE.md to prevent future re-import. | ➖ | ➖ | ➖ |
| **jllama-specific** | | | | |
| Expose `common_params::skip_download` | ➖ | ✅ `37754d4` — `ModelFlag.SKIP_DOWNLOAD` + `ModelParameters.setSkipDownload(boolean)` + `hasFlag` helper + new public `ModelUnavailableException` (extends now-public `LlamaException`) + Java-side heuristic translator. 104 tests pass. No JNI rebuild needed because upstream catches `common_skip_download_exception` inside its own arg-parser and surfaces it as a `false` return. | ➖ | ➖ |
| Expose `--spec-draft-backend-sampling` | ➖ | ❌ no `setSpecDraft*` in `src/main/java` ("add only on real user request") | ➖ | ➖ |
| **This session's deltas** | | | | |
| Enum typo `DUMPED_RIVATE_KEY` → `DUMPED_PRIVATE_KEY` | ✅ `23a3053` | ➖ | ➖ | ➖ |
| `Main.run` switch → arrow form | ✅ `27c2ace` | ➖ | ➖ | ➖ |
| `KeyProducerJavaRandom` switch → expression form (`yield`) | ✅ `2cdfcc5` | ➖ | ➖ | ➖ |
| LogCaptor smoke tests (`LoggingSmokeTest`) | ➖ | ✅ `3cedc6e` | ➖ | ➖ |
| CLAUDE.md TODO refresh (mark already-solved DONE) | ✅ `6eadc6f` | ✅ `fcb77b8` | ✅ `485f9cf` | ✅ `fcac664` |
| **Standing policies** | | | | |
| DO NOT UPGRADE jqwik past 1.9.3 | 📌 active | 📌 active | 📌 active | 📌 active |

---

## What materially changed vs. the seed

**BAF column had the most drift** (its CLAUDE.md TODO list is stale relative to the actual `pom.xml` on this branch):

1. **Error Prone → ERROR** — was claimed ❌ "~30 warnings remain"; actually ✅ — 12 patterns are at ERROR in `pom.xml:344`, same as the other 3 repos. Only items NOT yet at ERROR are the long tail of EP warnings tracked separately.
2. **`-parameters`** — was ❌; actually ✅ at `pom.xml:315` (set for main compile; off only for default-testCompile by design).
3. **Banned-API enforcement** — was ❌; actually ✅ — Enforcer `bannedDependencies`/`dependencyConvergence` at `pom.xml:268-283`, plus ArchUnit `noSystemExit`/`noNewRandom`/`Thread.sleep` rules in `BitcoinAddressFinderArchitectureTest`.
4. **ArchUnit public-fields-final** — was ❌; actually ✅ at `ArchitectureTest:120-130`.
5. **LogCaptor smoke test** — was ➖ "logback different"; actually ✅ — LogCaptor 2.12.6 declared at `pom.xml:84,847` and exercised in 5 test files. Already done long before the jllama work this session.
6. **Persistence-backends TODO** — self-labels "research-only / out of scope" but `BloomFilterAccelerator`, `HashSetAddressPresence`, `TruncatedLong64SortedArrayPresence` are all already implemented. CLAUDE.md needs a status refresh.

**Stays open in BAF** (real remaining work):
- `javac -Werror` flip (items 1–6 are clear, just hasn't been flipped)
- ArchUnit `layeredArchitecture()` (not yet)
- ArchUnit per-module banned-imports
- SpotBugs `effort=Max`/`threshold=Low`
- `@VisibleForTesting` audit + design-fit review (19 usages to walk)
- Package hierarchy + naming reviews
- BAF-specific GPU TODOs (3 large design docs in CLAUDE.md)

**jllama column** — all seed claims correct. Refined null-safety from "no actionable" to "43 sites all verified legitimate". Module-level `@NullMarked` confirmed.

**plugin column** — all seed claims correct. **NEW**: module-info DOES carry `@NullMarked` at module level — the CLAUDE.md bullet saying "intentionally NOT added" contradicts the actual file. Flag for correction.

**sb column** — all seed claims correct. Zero `@Nullable` in production confirmed.

---

## Genuinely-open items across all 4 repos (compact summary)

### Universal (all 4 repos)
- SpotBugs `effort=Max` + `threshold=Low` — one-off triage experiment
- `@VisibleForTesting` audit + design-fit review (now centralised at `workspace/policies/code-quality-todos.md`)
- Package hierarchy review (centralised at `workspace/policies/code-quality-todos.md`)
- Class / method naming review (centralised at `workspace/policies/code-quality-todos.md`)
- ~~Workspace-shared guidelines layer~~ ✅ **DONE this session** — canonical guides at `workspace/guides/`, canonical TDD skill at `workspace/.claude/skills/java-tdd-guide/SKILL.md`, jqwik / Javadoc / SpotBugs policies at `workspace/policies/`, PR workflow at `workspace/workflows/`
- ~~Standardised CLAUDE.md template~~ ✅ **DONE this session** — `workspace/templates/CLAUDE.md.template`

### BAF-only
- `javac -Werror` flip — blockers cleared; the stale 6-item warning list in `pom.xml:319-326` was refreshed to point at the Error Prone long-tail TODO as the remaining gate (`2d99c4a`). The actual `<arg>-Werror</arg>` is still off.
- ~~`--release 21` for main compile~~ ✅ **DONE** (BAF commits `c2470b7` + `1b67ad0`, this session). The `jdk.internal.misc.Unsafe` import in `ByteBufferUtility.java:9` was migrated to reflectively-resolved `sun.misc.Unsafe` (always-exported via `jdk.unsupported`) with a `@Nullable Unsafe UNSAFE` field; the static initializer wraps the reflective lookup in try/catch so non-HotSpot JVMs (OpenJ9, GraalVM Native Image, Android) get `UNSAFE == null` rather than `ExceptionInInitializerError`; `freeByteBuffer` gained a null guard so it becomes a no-op on those platforms (JVM Cleaner handles the buffer naturally). The duplicate system-module `--add-opens`/`--add-exports` in main `<compilerArgs>` were removed (runtime `<argLine>` keeps them for surefire). `default-testCompile` overrides the inherited `<release>` back to `<source>21</source><target>21</target>` so tests can keep importing `jdk.internal.ref.Cleaner` + `sun.nio.ch.DirectBuffer` to assert Cleaner invocation in `ByteBufferUtilityTest`. Verified end-to-end: clean `mvn compile` succeeds under `--release 21`; all 38 `ByteBufferUtilityTest` cases pass.
- ArchUnit `layeredArchitecture()` + per-module banned-imports
- 3 large GPU design TODOs (Pre-compute HASHSET hash on GPU, Push TRUNCATED_LONG_64 into OpenCL, End-to-end GPU vision)
- Persistence follow-ups (re-verified 2026-06-04): ~~4 stale `loadToMemoryCacheOnInit` example JSONs~~ ✅ DONE this session; JMH migration of `AddressLookupBenchmarkTest` (still under `persistence/`, NOT in `benchmark/` JMH module); open-addressing hash table backend; standalone `BloomFilterPersistence`; `HashSetPrecomputedHashAddressPresence` (Pre-compute HASHSET hash item). Default backend remains `BLOOM`.
- ~~`@VisibleForTesting` site-by-site cleanup~~ ✅ **DESIGN-FIT REVIEW COMPLETE this session.** Of the 19 original sites: **9 were dropped or refactored** (3 misapplied annotations dropped `05d9ddf`; 5 executor/lifecycle sites converted to test-friendly constructors; 2 mutable-static `AWAIT_DURATION_*` migrated to config in `51ac43c`); **10 legitimate sites remain** — all justified per the BAF audit's "KEEP" verdict (4 test-friendly constructors, 4 `FILE_EXTENSION_*` constants with same-package symbolic references, public `getRunLatch()` + `keysQueueSize()` getters where the annotation is documentation-only). No further cleanup recommended.
- ~~4 naming-audit MODERATE/MINOR findings still in source~~ ✅ ALL 4 FIXED this session: `BitHelper.getKillBits` → `getLowBitMask`; `LMDBPersistence.getAllAmountsFromAddresses` → `sumAmountsForAddresses`; `OpenCLBuilder.isOpenCLnativeLibraryLoadable` → `isOpenClNativeLibraryLoaded`; `PrivateKeyValidator.returnValidPrivateKey` → `coerceToValidPrivateKey`

### jllama-only
- ~~`setSkipDownload(boolean)` plumbing~~ ✅ DONE (`37754d4`)
- `setSpecDraftBackendSampling(boolean)` plumbing — confirmed ❌ (zero matches in src/main/java; deferred policy)
- ArchUnit `layeredArchitecture()` + per-module banned-imports
- GraalVM Native Image evaluation (design captured `23f8756`; implementation not started)
- Feature-investigation first batch (UTF-8 boundary decoder + per-run timing line + jbang example + system-properties README table) — ~1-2 days, no JNI changes

### plugin-only
- ArchUnit `layeredArchitecture()` + per-module banned-imports
- ~~Fix stale CLAUDE.md bullet about module-level `@NullMarked`~~ ✅ DONE (`9be6f17`; re-verified — `module-info.java` carries `@org.jspecify.annotations.NullMarked` immediately before `module net.ladenthin.maven.llamacpp.aiindex`)
- ~~Naming follow-ups (5 items)~~ ✅ **ALL 5 RESOLVED this session** — `LlamaCppJniAiSummaryProvider` renamed (`3007f03`), `AiGenerationResult` confirmed correct (CLAUDE.md drift fixed `371faa6` + `09067a2`), `AiMdHeaderSupport` split (`856c085`), `AiSummaryResponse` deleted as stillborn DTO (`f11eb6b`), `AiPromptSupport` kept after sibling-pattern review. Plugin column of the cross-repo naming audit is now 7/7 complete.

### sb-only
- (none beyond universal items)

---

## BAF `@VisibleForTesting` site-by-site audit (19 sites, this session)

Project's own stated rule (BAF CLAUDE.md): *"@VisibleForTesting should be the last resort, not the first."* Audit applies that rule per site.

### REFACTOR-VIA-INJECTION — 7 sites (mutable static / executor injection) — ✅ ALL CLOSED THIS SESSION

| File:Line | Entity | Current visibility | Status |
|---|---|---|---|
| ~~`Finder.java:43`~~ | ~~`static Duration AWAIT_DURATION_TERMINATE`~~ | pkg-private static (**mutable!**) | ✅ **FIXED** in `51ac43c` — migrated to `CFinder.awaitTerminateSeconds` (long, default ~100 k years). Tests inject via config POJO; static gone; `java.time.Duration` import dropped from `Finder`. Test-order hazard eliminated. |
| ~~`ConsumerJava.java:47`~~ | ~~`static Duration AWAIT_DURATION_QUEUE_EMPTY`~~ | pkg-private static (**mutable!**) | ✅ **FIXED** in `51ac43c` — migrated to `CConsumerJava.awaitQueueEmptySeconds` (long, default 60). Same pattern, same hazard eliminated. |
| ~~`Finder.java:60`~~ | ~~`final ExecutorService producerExecutorService`~~ | pkg-private | ✅ **FIXED** in `dda12e3` — test-friendly constructor accepts the executor; field is now `private final`. |
| ~~`ConsumerJava.java:94`~~ | ~~`ScheduledExecutorService scheduledExecutorService`~~ | pkg-private **non-final** | ✅ **FIXED** in `1855f8e` — 5-arg test-friendly constructor; field is `private final`. |
| ~~`ConsumerJava.java:129`~~ | ~~`final ExecutorService consumeKeysExecutorService`~~ | pkg-private | ✅ **FIXED** in `1855f8e` (same constructor pair). |
| ~~`ProducerOpenCL.java:25`~~ | ~~`final ThreadPoolExecutor resultReaderThreadPoolExecutor`~~ | pkg-private | ✅ **FIXED** in `4e83f88` — injected. |
| ~~`ProducerOpenCL.java:28`~~ | ~~`@Nullable OpenCLContext openCLContext`~~ | pkg-private (lifecycle handle) | ✅ **FIXED** in `98aab98` — `isInitialized()` getter exposes lifecycle state; field is now `private`. |

### REFACTOR-EXTRACT-HELPER — 2 sites (observable through narrower API) — ✅ ALL CLOSED THIS SESSION

| File:Line | Entity | Current visibility | Status |
|---|---|---|---|
| ~~`ConsumerJava.java:126`~~ | ~~`final AtomicBoolean shouldRun`~~ | pkg-private | ✅ **FIXED** — first `dc839bd` (`isRunning()` getter added), then naming corrected in `85cc8ae` to `shouldRun()` matching the flag semantics (cancellation-request flag, not thread-liveness). Field is now `private final`. |
| ~~`BIP39KeyProducer.java:51`~~ | ~~`final AtomicInteger counter`~~ | pkg-private | ✅ **FIXED** in `ece579f` — test-friendly constructor accepts `int startingIndex`; field is now `private final` again, no longer mutated by tests. |

### MAKE-PRIVATE — 1 site (annotation is noise / dead)

| File:Line | Entity | Current visibility | Why |
|---|---|---|---|
| ~~`cli/Main.java:39,47,55,61`~~ | ~~4× `FILE_EXTENSION_*` constants~~ | pkg-private | ✅ **RESOLVED** in `63ef722` + `c4eed5e` (this session). Owner correctly pointed out the constants ARE used by production — they drive the extension dispatch at `Main.main()`. Final state: extracted `Main.loadConfiguration(Path)` and added focused new test class `cli/MainConfigurationLoadingTest.java` (same package as `Main`) with 6 round-trip + syntax-probe tests that reference the constants symbolically via `Main.FILE_EXTENSION_JSON`/`_JS`/`_YAML`/`_YML`. `@VisibleForTesting` is now semantically honest — tests are in the same package and DO reach the package-private constants. |
| `cli/Main.java:71` | `final CountDownLatch runLatch` | pkg-private | Test reads via `getRunLatch()`; the field never needs widening. Make field `private`. |

### KEEP — 2 sites (genuinely justified)

| File:Line | Entity | Current visibility | Why keep |
|---|---|---|---|
| `cli/Main.java:82` | `public CountDownLatch getRunLatch()` | **public** | Already public — annotation is pure documentation, fine. |
| `ConsumerJava.java:481` | `int keysQueueSize()` | pkg-private method | Single-line getter — a legit observable property; could just be `public`. |

### ANNOTATION-DROPPED — 3 sites (visibility was correct, annotation misapplied — resolved this session)

| File:Line | Entity | Current visibility | Status |
|---|---|---|---|
| ~~`OpenClTask.java:287`~~ | `public SourceArgument getPrivateKeySourceArgument()` | **public** | ✅ **FIXED** in `05d9ddf` — annotation dropped, unused `VisibleForTesting` import removed, misleading "(visible for testing)" suffix removed from the Javadoc |
| ~~`ProducerOpenCL.java:139`~~ | `void waitTillFreeThreadsInPool()` | pkg-private | ✅ **FIXED** in `05d9ddf` — real production helper, annotation was misapplied |
| ~~`ProducerOpenCL.java:147`~~ | `int getFreeThreads()` | pkg-private | ✅ **FIXED** in `05d9ddf` — called from `waitTillFreeThreadsInPool()` in production |

### Recommended cleanup order — ✅ ALL TIERS COMPLETE

1. ~~**Trivial (5 min)**: delete the 4 dead `FILE_EXTENSION_*` annotations~~ → **Resolved differently** in `63ef722` + `c4eed5e` (this session): extracted `Main.loadConfiguration(Path)`, then in follow-up created focused `cli/MainConfigurationLoadingTest.java` with 6 round-trip + syntax-probe tests that reference the constants symbolically (constants stay package-private and `@VisibleForTesting` is now semantically honest — same package as `Main`).
2. ~~**Small (15 min)**: dropped misapplied annotations + `Main.runLatch`~~ ✅ DONE — `05d9ddf` + `2d99c4a`. `keysQueueSize()` annotation kept on a pkg-private single-line getter; widening to public is a stylistic preference not a correctness fix, so leaving as-is.
3. ~~**Medium (30–60 min)**: replace `ConsumerJava.shouldRun` and `BIP39KeyProducer.counter` direct-field exposure~~ ✅ DONE — `dc839bd`/`85cc8ae` + `ece579f`.
4. ~~**Bigger (1–2 h)**: inject the 5 executor services via constructor~~ ✅ DONE — `dda12e3`, `1855f8e`, `4e83f88`, `98aab98`.
5. ~~**Biggest (carries semantic risk)**: kill the two mutable static `AWAIT_DURATION_*` fields.~~ ✅ **DONE** in `51ac43c` — both migrated to `long` seconds config fields on `CFinder` / `CConsumerJava`. `Duration` chosen against because Jackson lacks jsr310 in this project; `long` matches existing convention (`delayEmptyConsumer = 100`). Follow-up `d199ad7`: all 4 `config_Find_*.json` example fixtures now carry the new fields explicitly with production-default values so operators discover them in the config file.

### Net story (updated this session)

Of the 19 original sites: **9 cleared (cleanup tiers 1–5 all complete) + 10 legitimate sites remain**. The 10 that stay are not "smells" — they are all justified:
- **4 test-friendly constructors** (BIP39KeyProducer, Finder, ConsumerJava 5-arg, ProducerOpenCL) — this is the *intended* `@VisibleForTesting` usage pattern documented in the BAF CLAUDE.md.
- **4 `Main.FILE_EXTENSION_*` constants** — production constants exercised by same-package `MainConfigurationLoadingTest`; annotation is semantically honest.
- **2 public/observable getters** (`Main.getRunLatch()`, `ConsumerJava.keysQueueSize()`) — the annotation is pure documentation since the methods are already accessible.

**The BAF `@VisibleForTesting` design-fit review is complete.** Further passes would only churn doc comments without changing behaviour.

---

## Naming audit — per repo (this session)

Goal stated by owner: *"not perfect, but at least good enough and clear"* — flag names that are definitely wrong or misleading, not nits. CRITICAL = a reader could write a bug because of the name; MODERATE = confusing/typo; MINOR = worth flagging.

### BAF — 6 findings (2 CRITICAL, 3 MODERATE, 1 MINOR)

| File:Line | Current | What it actually does | Suggested | Severity |
|---|---|---|---|---|
| ~~`Bech32Helper.java:134`~~ | ~~`getWitnessPrograms(Bech32Data)`~~ | Returns a **single** witness program (`byte[]`) — bitcoinj upstream uses singular `witnessProgram()` | `getWitnessProgram` | ✅ **FIXED** in `cc37a5d` (this session) |
| ~~`CKeyProducerJavaIncremental.java`~~ (fields + getters) | ~~`startAddress`/`endAddress`/`getStartAddress`/`getEndAddress`~~ | Return **private-key** range bounds (`BigInteger`); javadoc itself said "private-key range". In Bitcoin "address" = derived public hash — opposite end of the pipeline | `startPrivateKey` / `endPrivateKey` / `getStartPrivateKey` / `getEndPrivateKey` | ✅ **FIXED** in `83ada00` (this session — 6 files: POJO, impl, 2 tests, README, example JSON; no back-compat shim per direction) |
| ~~`BitHelper.java:35`~~ | ~~`getKillBits(int bits)`~~ | Returns low-bits bitmask `2^bits - 1` (e.g. `0xFF` for `bits=8`) — used to mask, not "kill" | `getLowBitMask` | ✅ **FIXED** in this session (`BitHelper`, `AbstractProducer`, `BitHelperTest`, `BitcoinAddressProperties`, `BitHelperBenchmark`, `ProbeAddressesOpenCLTest`, `CommonDataProvider.DATA_PROVIDER_KILL_BITS`→`DATA_PROVIDER_LOW_BIT_MASK`) |
| ~~`LMDBPersistence.java:388` (+ `Persistence` interface)~~ | ~~`getAllAmountsFromAddresses(List<ByteBuffer>)`~~ | Returns the **sum** of all amounts as a single `Coin` — plural name implies a collection | `sumAmountsForAddresses` | ✅ **FIXED** in this session (`Persistence.java`, `LMDBPersistence.java`; no other callers existed) |
| ~~`opencl/OpenCLBuilder.java:229`~~ | ~~`isOpenCLnativeLibraryLoadable`~~ | Reads a `nativeLibraryLoaded` boolean; (1) mid-word lowercase `n` in `CLn` violates Java conventions, (2) verb is `-able` but value is post-fact `-ed` | `isOpenClNativeLibraryLoaded` | ✅ **FIXED** in this session (`OpenCLBuilder`, `OpenCLBuilderTest`, `OpenCLPlatformAssume`, `spotbugs-exclude.xml`). The broader `assumeOpenCLLibraryLoadable` helper rename across 8 test files / 31 call sites is intentionally out of scope. |
| ~~`PrivateKeyValidator.java:89`~~ | ~~`returnValidPrivateKey(secret)`~~ | Returns input if valid, else the replacement constant — **coerces/sanitises**, not just returns | `coerceToValidPrivateKey` | ✅ **FIXED** in this session (`PrivateKeyValidator` definition + in-file caller in `replaceInvalidPrivateKeys`, `PrivateKeyValidatorTest`, plus doc updates in `CLAUDE.md` line 181 and `skills/tdd.md` line 134) |

The two CRITICAL findings are the highest-value: `getStartAddress`/`getEndAddress` is a public JSON config field that actively misleads operators about what they're configuring (they think it's a Bitcoin address range; it's actually a private-key range).

### streambuffer — 7 findings (4 MODERATE, 3 MINOR)

| File:Line | Current | What it actually does | Suggested | Severity |
|---|---|---|---|---|
| ~~`StreamBuffer.java:368`~~ | ~~`correctOffsetAndLengthToRead(...)`~~ | Validates only — never mutates/corrects anything; throws or returns boolean | `validateOffsetAndLengthToRead` | ✅ **FIXED** in `cf2b5fd` (this session) |
| ~~`StreamBuffer.java:389`~~ | ~~`correctOffsetAndLengthToWrite(...)`~~ | Same — validates, never corrects | `validateOffsetAndLengthToWrite` | ✅ **FIXED** in `cf2b5fd` (this session) |
| ~~`StreamBuffer.java:589`~~ | ~~`isTrimShouldBeExecuted()`~~ | Grammatically broken — mixes `is` + `should be` | `shouldTrim` | ✅ **FIXED** in `cf2b5fd` (this session — also renames the linked `EXCEPTION_MESSAGE_*` constant) |
| ~~`StreamBuffer.java:275` vs `:1064`~~ | ~~`getBufferElementCount()` vs `getBufferSize()`~~ | **Two public methods, identical implementation** (`buffer.size()` under `bufferLock`) — name drift | Delete `getBufferSize`; external callers migrate to `getBufferElementCount` | ✅ **FIXED** in `16f1df7` (this session) |
| ~~`StreamBuffer.java:170` Javadoc~~ | ~~"Set a secure or **unsercure** write operation"~~ | Typo in Javadoc | "unsecure" | ✅ **FIXED** in `966595c` (this session) |
| ~~`StreamBuffer.java:420`~~ | ~~`blockDataAvailable()`~~ | **Deeper bug uncovered during investigation**: Javadoc pointed to private `tryWaitForEnoughBytes` — external callers had no public alternative. Cleanup also promoted `tryWaitForEnoughBytes` → public `waitForAtLeast(long)` and added convenience `waitForAnyData()`. Internal `read()` site also adopts the convenience. | DELETED + replacement public API (`waitForAtLeast` + `waitForAnyData`) | ✅ **FIXED** in `16f1df7` (this session) |
| ~~`StreamBuffer.java:932`~~ | ~~`noMoreMissingBytes(int)`~~ | Returns `missingBytes == 0` — predicate written in negative phrasing | `hasNoMissingBytes` (private rename, 3 sites) | ✅ **FIXED** in `16f1df7` (this session) |

### plugin — 7 findings (4 MODERATE, 3 MINOR)

| File:Line | Current | What it actually does | Suggested | Severity |
|---|---|---|---|---|
| ~~`LlamaCppJniAiSummaryProvider.java:20`~~ | ~~`LlamaCppJniAiSummaryProvider`~~ | Implements `AiGenerationProvider`; the "Summary" predated the generalization. Confirmed inconsistent **from initial commit a1df3e0 (2026-03-19)**, not refactoring residue — the interface, factory, and `MockAiGenerationProvider` sibling all already used "Generation" while only this JNI implementation and the operator-facing Mojo `@Parameter summaryProvider` used "Summary". | `LlamaCppJniAiGenerationProvider` (mirrors `MockAiGenerationProvider`); Mojo `@Parameter summaryProvider` → `generationProvider` + Maven property `aiIndex.summaryProvider` → `aiIndex.generationProvider` + `pom.xml:672` self-test config + README + TEST_WRITING_GUIDE updated | ✅ **FIXED** in `3007f03` (this session) |
| ~~`AiGenerationResult.java:18`~~ | ~~`AiGenerationResult`~~ shape-or-name reconciliation | After deep git-history investigation: the body-only shape is the **deliberate final state of a multi-step refactor** (`5b799b9` created it with 3 fields, `87013e9` removed the `summary` field, `7916b15` removed `keywords` — `git log --follow` confirms). The class name and the body-only shape are both correct. The "shape mismatch" was actually CLAUDE.md documentation drift. | Keep class + shape; fix CLAUDE.md `s`/`k` + "summary + keywords + body" drift instead | ✅ **DOCS FIXED** in `371faa6` + `09067a2` (this session — CLAUDE.md header-field rows + project-tree drift cleared) |
| ~~`AiChecksumSupport.java:13`~~ | `AiChecksumSupport` | Computes CRC32 (always has — `git log -S MessageDigest` empty). Class Javadoc + `c` field doc in `AiMdHeader` are correct; only CLAUDE.md was stale | docs fixed; class name kept (CRC32 is the right choice for change-detection) | ✅ **FIXED** in `8930e4d` (this session — CLAUDE.md line 196 corrected) |
| ~~`AiMdHeaderSupport.java:11`~~ | ~~`AiMdHeaderSupport`~~ — two unrelated operations | `shouldWrite(...)` rewrite-decision (used by both Indexers) + `buildChecksumLine(...)` package-child line formatter (used only by `PackageIndexer`). Git history confirmed both methods co-located since the **initial commit a1df3e0** by design — split is a code-cleanliness improvement, not a bug fix. | Keep `AiMdHeaderSupport` for `shouldWrite`; extract `buildChecksumLine` to new `AiMdChildEntryLineFormatter` (single caller, narrow purpose) | ✅ **FIXED** in `856c085` (this session) |
| ~~`AiResponseNormalizer.java:65`~~ (class + method) | ~~`AiResponseNormalizer.normalize(String)`~~ | Strips `<thinking>` blocks **and throws `IOException`** if budget exhausted inside one — a parser with typed failure, not a pure normalizer | class → `AiCompletionParser`, method → `parseCompletion` (escalated from MINOR after deeper review confirmed class-name drift too) | ✅ **FIXED** in `6567b9e` (this session — class + method + test class + 4 PIT/README ref locations) |
| ~~`AiSummaryResponse.java:11`~~ | ~~`AiSummaryResponse`~~ — proposed rename | Carries `(summary, keywords)` from the pre-refactor multi-output AI design. Git history confirmed the class was created in the initial commit (a1df3e0) but **never constructed in ANY of the 266 commits** — `git log -S 'new AiSummaryResponse'` returns zero hits. Stillborn DTO. | ~~Rename to `AiHeaderFields`~~ → **delete entirely** (not just rename). | ✅ **DELETED** in `f11eb6b` (this session) — file + 4 doc references (CLAUDE.md ×2, CODE_WRITING_GUIDE.md ×3 including replacing the illustrative GOOD/BAD record example with `AiPreparedPrompt` which actually exists) |
| `AiPromptSupport.java:11` — proposed rename | `AiPromptSupport` is both registry (`templates` map) AND renderer (`buildPrompt(...)`). Sibling-pattern check confirmed: `AiModelDefinitionSupport` does the same registry+lookup for `AiModelDefinition` and keeps the `*Support` suffix. Renaming `AiPromptSupport` to `AiPromptTemplateRegistry` would break the established sibling pattern. | **Keep `AiPromptSupport`** — sibling consistency outweighs precision gain. | ✅ **NO ACTION** (verdict: keep as-is after deep review). |

All five plugin naming-audit follow-ups closed this session. Deep git-history investigation (via fresh GitHub clone, walked all 266 commits) confirmed each verdict against actual code evolution rather than current-state-only reading:

- (1) `LlamaCppJniAiSummaryProvider` — RENAMED (`3007f03`) including Mojo `@Parameter summaryProvider` → `generationProvider` and `pom.xml:672` self-test
- (2) `AiGenerationResult` — DOCS FIXED only (`371faa6` + `09067a2`); body-only shape is intentional final state of a 2-step refactor, not a bug
- (3) `AiMdHeaderSupport` — SPLIT (`856c085`) extracting `buildChecksumLine` to new `AiMdChildEntryLineFormatter`
- (4) `AiSummaryResponse` — DELETED (`f11eb6b`); stillborn DTO never constructed in any of the 266 commits
- (5) `AiPromptSupport` — KEPT; sibling pattern argument with `AiModelDefinitionSupport`

### jllama — 1 finding (1 MODERATE)

| File:Line | Current | What it actually does | Suggested | Severity |
|---|---|---|---|---|
| ~~`ModelParameters.java:1427`~~ | ~~`isDefault(String key)`~~ | Returns `true` only when the key is **absent** from the map — a key explicitly set to its default value still returns `false`. Name implies value comparison; implementation is presence check. | `isUnset` | ✅ **FIXED** in `ffbc06c` (this session — public API rename, no `@Deprecated` shim) |

No class-drift, no typos, no plurality mismatches, no cryptic names. The 5 `handle*` methods on `LlamaModel` (`handleCompletions`, `handleInfill`, etc.) deliberately mirror upstream llama.cpp server endpoint names (`/handle_completions`) — intentional traceability, keep as-is.

### Naming audit — totals across 4 repos

| Repo | CRITICAL | MODERATE | MINOR | Total | Fixed this session |
|---|:--:|:--:|:--:|:--:|:--:|
| BAF | 2 | 3 | 1 | 6 | **6 (all fixed)** — Bech32Helper `cc37a5d`; CKeyProducerJavaIncremental `83ada00`; BitHelper.getKillBits→getLowBitMask `2509988`; LMDBPersistence.getAllAmountsFromAddresses→sumAmountsForAddresses `8ff90c9`; OpenCLBuilder.isOpenCLnativeLibraryLoadable→isOpenClNativeLibraryLoaded `81dd95b`; PrivateKeyValidator.returnValidPrivateKey→coerceToValidPrivateKey `a6531c9` |
| sb | 0 | 4 | 3 | 7 | 7 (all closed: typo `966595c` + 3 method renames `cf2b5fd` + final 3 cleanups `16f1df7`) |
| plugin | 0 | 4 | 3 | 7 | **7 (all closed)** — CRC32 docs `8930e4d`; AiResponseNormalizer→AiCompletionParser `6567b9e`; AiSummaryResponse DELETED `f11eb6b` (stillborn DTO, never constructed); CLAUDE.md s/k drift fixed `371faa6` + `09067a2`; AiMdHeaderSupport split `856c085` (extract `AiMdChildEntryLineFormatter`); LlamaCppJniAiSummaryProvider → LlamaCppJniAiGenerationProvider `3007f03` (+ Mojo @Parameter rename + pom.xml self-test + README + TEST_WRITING_GUIDE); AiPromptSupport KEPT (sibling pattern with AiModelDefinitionSupport) |
| jllama | 0 | 1 | 0 | 1 | 1 (isDefault → isUnset `ffbc06c`) |
| **All** | **2** | **12** | **7** | **21** | **21 fixed (cross-repo naming audit complete)** — both CRITICAL done; sb + BAF + jllama + plugin all fully cleared. |

**Top 5 to fix first (CRITICAL + highest-impact MODERATE):**
1. ✅ BAF `CKeyProducerJavaIncremental.startAddress/endAddress` → `startPrivateKey/endPrivateKey` — public JSON config field rename. **Fixed in `83ada00`.**
2. ✅ BAF `Bech32Helper.getWitnessPrograms` — plural name returns a single value. **Fixed in `cc37a5d`.**
3. ✅ plugin `AiChecksumSupport` — turned out to be **docs-only drift** (`CLAUDE.md` was wrong; implementation has always been correct CRC32). **Fixed in `8930e4d`.**
4. ✅ plugin `AiGenerationResult` — the "summary + keywords + body" claim was **CLAUDE.md documentation drift**, not a class-shape bug. Deep git-history investigation showed the body-only shape is the final state of a deliberate 2-step refactor (`5b799b9` created with 3 fields → `87013e9` removed `summary` → `7916b15` removed `keywords`). **Class kept; CLAUDE.md fixed in `371faa6` + `09067a2`.**
5. ✅ plugin `LlamaCppJniAiSummaryProvider` → `LlamaCppJniAiGenerationProvider` — confirmed naming inconsistent from initial commit `a1df3e0`, not refactor residue (interface, factory, mock all already said "Generation"). **Fixed in `3007f03`** (class + test class + Mojo `@Parameter summaryProvider` → `generationProvider` + Maven property + `pom.xml:672` self-test + README + TEST_WRITING_GUIDE + CLAUDE.md).

**This session's additional renames (not in the top-5 list)**:
- ✅ sb `validateOffsetAndLength*` + `shouldTrim` bundle (`cf2b5fd`) — 3 MODERATE
- ✅ plugin `AiResponseNormalizer` → `AiCompletionParser` + `normalize` → `parseCompletion` (`6567b9e`) — escalated from MINOR after class-name-drift verification confirmed the broader rename
- ✅ jllama `isDefault` → `isUnset` (`ffbc06c`) — MODERATE
- ✅ plugin `AiSummaryResponse` DELETED (`f11eb6b`) — never used in any commit (266-commit history checked)
- ✅ plugin `AiMdHeaderSupport` split (`856c085`) — extracted `buildChecksumLine` to new `AiMdChildEntryLineFormatter`

**Top-5 progress: 5 of 5 fixed. The full 21-item cross-repo naming audit is now COMPLETE.**

---

## CLAUDE.md TODO list staleness — recommended actions

| Repo | What is stale | Suggested fix |
|---|---|---|
| **BAF** | ✅ Fully refreshed in `05d9ddf` + `5b16c77` (this session) — Error Prone → ERROR, `-parameters`, Banned-API enforcement, ArchUnit public-fields-final all marked DONE; the Persistence-backends entry has been rewritten to reflect shipped state (HashSet + TRUNCATED_LONG_64 backends, BloomFilterAccelerator extraction, AddressLookupBackend config enum, chain contract — all DONE). Remaining open in the Persistence entry: 3 stale example JSON `loadToMemoryCacheOnInit` lines + JMH migration + open-hash backend + standalone Bloom backend. | — |
| **plugin** | ✅ **FIXED** in `9be6f17` (this session) — the bullet now correctly says module-level `@NullMarked` IS set with `requires static org.jspecify;`. | — |
| **jllama** | Nothing material out of date. | — |
| **sb** | Nothing material out of date. | — |
