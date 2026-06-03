# Cross-Repo Status Table — VERIFIED

> **For a future session**: this file is the consolidated cross-repo status snapshot
> at end of the previous session (2026-06-03). All changes referenced by commit
> hash below are landed. The recommended next-task list lives in the
> **"Quick prioritisation (cheapest → biggest)"** section near the bottom — start
> there to pick up work. The richer per-repo design context lives in each repo's
> own `CLAUDE.md` Open-TODOs section (especially BAF's persistence/GPU TODOs and
> jllama's strictness-ladder commit ledger).

Repos:
- **BAF** = `/home/user/BitcoinAddressFinder`
- **jllama** = `/home/user/java-llama.cpp`
- **plugin** = `/home/user/llamacpp-ai-index-maven-plugin`
- **sb** = `/home/user/streambuffer`

Legend: ✅ done · ❌ open · ➖ N/A · 📌 standing policy

> **Audit method**: each row verified by reading `pom.xml`, source files, and `git rev-parse` against the working tree on the current branch. Seed claims that were wrong are flagged with → and the corrected state. See `/home/user/cross-repo-status-AUDIT-LOG.md` for the per-row evidence trail.

---

## VERIFIED TABLE

| TODO item | BAF | jllama | plugin | sb |
|---|:--:|:--:|:--:|:--:|
| **Strictness ladder** | | | | |
| Error Prone bug patterns → ERROR (12 patterns) | ✅ verified (was seed ❌) | ✅ `855f447` | ✅ `034b553` | ✅ `ad95d66` |
| `javac -Werror` + `-Xlint:all,-serial,-options` | ❌ not yet flipped (items 1–6 cleared; ready) | ✅ `3e2efbb` | ✅ | ✅ `7a4fbf0` |
| `-parameters` javac arg | ✅ `pom.xml:315` (was seed ❌) | ✅ `4350cf2` | ✅ `7ae3279` | ✅ `912f14b` |
| `--release N` instead of `-source`/`-target` | ❌ main still `<source>21</source>/<target>21>`; module-info uses `--release 9` | ✅ `4350cf2` | ✅ `7ae3279` | ✅ `912f14b` |
| PIT mutation threshold enforced (100%) | ✅ `BitHelper` (`pom.xml:711-717`) | ✅ `Pair` (`62f8a00`) | ✅ `AiResponseNormalizer` | ✅ whole package |
| Checker Framework 2nd nullness pass | ✅ NullnessChecker + `objects.astub` | ✅ `c63870b` | ✅ | ✅ `5a9be1b` |
| JPMS `module-info.java` | ✅ `src/main/java9/module-info.java` | ✅ `0fd066a`/`9528e79` (module-level `@NullMarked`) | ✅ — and module-level `@NullMarked` IS set (CLAUDE.md note "intentionally NOT added" is **stale**) | ✅ |
| Banned-API enforcement (Enforcer + ArchUnit) | ✅ Enforcer @ `pom.xml:268-283`; ArchUnit `noSystemExit`/`noNewRandom`/`Thread.sleep` (was seed ❌) | ✅ `8baae0c`/`329d764`/`e6069da` | ✅ `d654442`/`fd8cf80`/`ad37355` | ✅ `c0148c8`/`eaf4337` |
| ArchUnit public-fields-final | ✅ `ArchitectureTest:120-130` (was seed ❌) | ✅ `7b6667d` | ✅ `d2b1af9` | ✅ `5dd816d` |
| ArchUnit ban internal-JDK imports (`sun.*`/`com.sun.*`/`jdk.internal.*`) | ✅ `ArchitectureTest:90-97` | ✅ `e6069da` | ✅ `ad37355` | ✅ `de29bd4` |
| ArchUnit `layeredArchitecture()` | ❌ | ❌ | ❌ | ➖ single-package |
| ArchUnit per-module banned-imports | ❌ | ❌ | ❌ | ➖ single-package |
| SpotBugs `effort=Max` + `threshold=Low` | ❌ both `Default` | ❌ both `Default` | ❌ both `Default` | ❌ both `Default` |
| **Logging / observability** | | | | |
| LogCaptor smoke test | ✅ LogCaptor 2.12.6 + used in 5 tests (was seed ➖) | ✅ `3cedc6e` (this session) | ➖ no logging | ➖ no logging |
| **This session's additions (sb)** | | | | |
| `getAvailableBytesExact()` public long getter | ➖ | ➖ | ➖ | ✅ `aa5c6b8` — closes the >2 GB live-count API gap; verified across 441-commit upstream history that no equivalent ever existed before |
| **Code-quality audits (continuous)** | | | | |
| `@VisibleForTesting` audit (count) | 19 usages × 6 files | 0 | 0 | 0 |
| `@VisibleForTesting` design-fit review | ✅ done this session — see "BAF @VisibleForTesting site-by-site audit" below | ➖ no usages | ➖ no usages | ➖ no usages |
| Null-safety follow-up review | ✅ deep scan this session — 53 `@Nullable` sites all legitimate; no actionable changes | ✅ deep scan — 43 sites all legitimate, no TIGHTEN candidates | ✅ 17 sites all legitimate | ✅ zero `@Nullable` in production (verified) |
| Package hierarchy review | ❌ | ❌ | ❌ | ❌ |
| Class / method naming review | ❌ | ❌ | ❌ | ❌ |
| **Cross-repo refactors** | | | | |
| Workspace-shared guidelines layer (Java code/test conventions) | ❌ | ❌ | ❌ | ❌ |
| Standardised `CLAUDE.md` template | ❌ | ❌ | ❌ | ❌ |
| **BAF-specific big items** | | | | |
| `-Werror` items 1–6 (BAF-internal pre-`-Werror` list) | ✅ all six cleared (`6eadc6f`) | ➖ | ➖ | ➖ |
| Persistence-backends research/implementation | ✅ refresh DONE in `5b16c77` (this session) — TODO now reflects shipped state per plan item: HashSet snapshot, BloomFilterAccelerator extraction, TRUNCATED_LONG_64, AddressLookupBackend config enum, AddressPresence/AddressLookup chain contract, AddressLookupBenchmarkTest — all marked DONE. Remaining open: 3 stale example JSON `loadToMemoryCacheOnInit` lines, JMH migration of the benchmark, open-addressing hash table backend, standalone Bloom-only backend. | ➖ | ➖ | ➖ |
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
- `--release N` for main compile (still uses `<source>21</source>/<target>21>`)
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
- `@VisibleForTesting` audit + design-fit review
- Package hierarchy review
- Class / method naming review
- Workspace-shared guidelines layer (canonical conventions in one place)
- Standardised CLAUDE.md template

### BAF-only
- `javac -Werror` flip (next obvious move — blockers cleared)
- `--release N` for main compile (not module-info only)
- ArchUnit `layeredArchitecture()` + per-module banned-imports
- CLAUDE.md staleness refresh (Persistence-backends TODO is partly done; per-repo strictness items are stale)
- 3 large GPU design TODOs (Pre-compute HASHSET hash on GPU, Push TRUNCATED_LONG_64 into OpenCL, End-to-end GPU vision)

### jllama-only
- `setSkipDownload(boolean)` plumbing
- `setSpecDraftBackendSampling(boolean)` plumbing (deferred — "add only on real user request")
- ArchUnit `layeredArchitecture()` + per-module banned-imports

### plugin-only
- ArchUnit `layeredArchitecture()` + per-module banned-imports
- Fix stale CLAUDE.md bullet about module-level `@NullMarked`

### sb-only
- (none beyond universal items)

---

## BAF `@VisibleForTesting` site-by-site audit (19 sites, this session)

Project's own stated rule (BAF CLAUDE.md): *"@VisibleForTesting should be the last resort, not the first."* Audit applies that rule per site.

### REFACTOR-VIA-INJECTION — 7 sites (mutable static / executor injection)

| File:Line | Entity | Current visibility | Why refactor |
|---|---|---|---|
| `Finder.java:43` | `static Duration AWAIT_DURATION_TERMINATE` | pkg-private static (**mutable!**) | FinderTest reassigns the static at runtime — test-order hazard. Inject via config. |
| `ConsumerJava.java:47` | `static Duration AWAIT_DURATION_QUEUE_EMPTY` | pkg-private static (**mutable!**) | Same shared-mutable-static anti-pattern. |
| `Finder.java:60` | `final ExecutorService producerExecutorService` | pkg-private | Test only calls `.isTerminated()`. Inject executor → field becomes `private`. |
| `ConsumerJava.java:94` | `ScheduledExecutorService scheduledExecutorService` | pkg-private **non-final** | Test reads `.isShutdown()`. Inject; field becomes `private final`. |
| `ConsumerJava.java:129` | `final ExecutorService consumeKeysExecutorService` | pkg-private | Same — inject. |
| `ProducerOpenCL.java:25` | `final ThreadPoolExecutor resultReaderThreadPoolExecutor` | pkg-private | Same — inject. |
| `ProducerOpenCL.java:28` | `@Nullable OpenCLContext openCLContext` | pkg-private (lifecycle handle) | Test only asserts init/close ran; expose `boolean isInitialized()` instead. |

### REFACTOR-EXTRACT-HELPER — 2 sites (observable through narrower API)

| File:Line | Entity | Current visibility | Why refactor |
|---|---|---|---|
| `ConsumerJava.java:126` | `final AtomicBoolean shouldRun` | pkg-private | Tests call `.get()`. Expose `boolean isRunning()` getter; keep field truly private. |
| `BIP39KeyProducer.java:51` | `final AtomicInteger counter` | pkg-private | Test sets `counter.set(Integer.MAX_VALUE)` to force overflow. Replace with constructor parameter for starting value. |

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

### Recommended cleanup order (cheapest → most invasive)

1. ~~**Trivial (5 min)**: delete the 4 dead `FILE_EXTENSION_*` annotations~~ → **Resolved differently** in `63ef722` + `c4eed5e` (this session): extracted `Main.loadConfiguration(Path)`, then in follow-up created focused `cli/MainConfigurationLoadingTest.java` with 6 round-trip + syntax-probe tests that reference the constants symbolically (constants stay package-private and `@VisibleForTesting` is now semantically honest — same package as `Main`).
2. **Small (15 min)**: ✅ Partially done in `05d9ddf` — dropped misapplied annotations on `OpenClTask.getPrivateKeySourceArgument` + `ProducerOpenCL.waitTillFreeThreadsInPool` + `ProducerOpenCL.getFreeThreads`. **Still open**: make `Main.runLatch` field `private` (keep public getter); consider widening `ConsumerJava.keysQueueSize` to `public` or dropping the annotation.
3. **Medium (30–60 min)**: replace `ConsumerJava.shouldRun` and `BIP39KeyProducer.counter` direct-field exposure with `isRunning()` getter / constructor parameter respectively.
4. **Bigger (1–2 h)**: inject the 5 executor services via constructor; fields become `private final`. Tests pass their own executors and assert on them.
5. **Biggest (carries semantic risk)**: kill the two mutable static `AWAIT_DURATION_*` fields. Convert to constructor-injected configuration; this is the highest-value cleanup but touches the most call sites.

### Net story (updated this session)

Of the 19 sites: **2 groups resolved this session** — (1) 4 `FILE_EXTENSION_*` constants via the `loadConfiguration` extraction + `cli/MainConfigurationLoadingTest.java`; (2) 3 misapplied annotations dropped in `05d9ddf` (`OpenClTask.getPrivateKeySourceArgument`, `ProducerOpenCL.waitTillFreeThreadsInPool`, `ProducerOpenCL.getFreeThreads`). 10 genuine "widen access for tests" smells remain; 2 are still KEEP.

---

## Naming audit — per repo (this session)

Goal stated by owner: *"not perfect, but at least good enough and clear"* — flag names that are definitely wrong or misleading, not nits. CRITICAL = a reader could write a bug because of the name; MODERATE = confusing/typo; MINOR = worth flagging.

### BAF — 6 findings (2 CRITICAL, 3 MODERATE, 1 MINOR)

| File:Line | Current | What it actually does | Suggested | Severity |
|---|---|---|---|---|
| ~~`Bech32Helper.java:134`~~ | ~~`getWitnessPrograms(Bech32Data)`~~ | Returns a **single** witness program (`byte[]`) — bitcoinj upstream uses singular `witnessProgram()` | `getWitnessProgram` | ✅ **FIXED** in `cc37a5d` (this session) |
| ~~`CKeyProducerJavaIncremental.java`~~ (fields + getters) | ~~`startAddress`/`endAddress`/`getStartAddress`/`getEndAddress`~~ | Return **private-key** range bounds (`BigInteger`); javadoc itself said "private-key range". In Bitcoin "address" = derived public hash — opposite end of the pipeline | `startPrivateKey` / `endPrivateKey` / `getStartPrivateKey` / `getEndPrivateKey` | ✅ **FIXED** in `83ada00` (this session — 6 files: POJO, impl, 2 tests, README, example JSON; no back-compat shim per direction) |
| `BitHelper.java:35` | `getKillBits(int bits)` | Returns low-bits bitmask `2^bits - 1` (e.g. `0xFF` for `bits=8`) — used to mask, not "kill" | `getLowBitMask` | MODERATE |
| `LMDBPersistence.java:388` (+ `Persistence` interface) | `getAllAmountsFromAddresses(List<ByteBuffer>)` | Returns the **sum** of all amounts as a single `Coin` — plural name implies a collection | `sumAmountsForAddresses` | MODERATE |
| `opencl/OpenCLBuilder.java:229` | `isOpenCLnativeLibraryLoadable` | Reads a `nativeLibraryLoaded` boolean; (1) mid-word lowercase `n` in `CLn` violates Java conventions, (2) verb is `-able` but value is post-fact `-ed` | `isOpenClNativeLibraryLoaded` | MODERATE |
| `PrivateKeyValidator.java:89` | `returnValidPrivateKey(secret)` | Returns input if valid, else the replacement constant — **coerces/sanitises**, not just returns | `coerceToValidPrivateKey` / `sanitizePrivateKey` | MINOR |

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
| `LlamaCppJniAiSummaryProvider.java:20` | `LlamaCppJniAiSummaryProvider` | Implements `AiGenerationProvider`; produces summary AND keywords AND body via `generate(...)` — the "Summary" predates the generalization | `LlamaCppJniAiGenerationProvider` (mirrors `MockAiGenerationProvider`) | MODERATE |
| `AiGenerationResult.java:18` | `AiGenerationResult` | Carries **only** a `body` string; CLAUDE.md describes it as "summary + keywords + body" — either name overpromises or shape is stale | `AiBodyResult` (if shape correct), or restore the missing fields (if name correct) | MODERATE |
| ~~`AiChecksumSupport.java:13`~~ | `AiChecksumSupport` | Computes CRC32 (always has — `git log -S MessageDigest` empty). Class Javadoc + `c` field doc in `AiMdHeader` are correct; only CLAUDE.md was stale | docs fixed; class name kept (CRC32 is the right choice for change-detection) | ✅ **FIXED** in `8930e4d` (this session — CLAUDE.md line 196 corrected) |
| `AiMdHeaderSupport.java:11` | `AiMdHeaderSupport` | Two unrelated operations: `shouldWrite(...)` rewrite-decision + `buildChecksumLine(...)` parent-checksum formatter; not "header manipulation" | Split into `AiMdRewriteDecision` + `AiMdChildChecksumLineFormatter` | MODERATE |
| ~~`AiResponseNormalizer.java:65`~~ (class + method) | ~~`AiResponseNormalizer.normalize(String)`~~ | Strips `<thinking>` blocks **and throws `IOException`** if budget exhausted inside one — a parser with typed failure, not a pure normalizer | class → `AiCompletionParser`, method → `parseCompletion` (escalated from MINOR after deeper review confirmed class-name drift too) | ✅ **FIXED** in `6567b9e` (this session — class + method + test class + 4 PIT/README ref locations) |
| `AiSummaryResponse.java:11` | `AiSummaryResponse` | Carries `summary` + `keywords` only; not a provider wire response (providers return `String`) | `AiSummaryAndKeywords` / `AiHeaderFields` | MINOR |
| `AiPromptSupport.java:11` | `AiPromptSupport` | Registry of prompt templates + `buildPrompt(...)` renderer — concretely a template registry | `AiPromptTemplateRegistry` (or `AiPromptRenderer`) | MINOR |

Top-priority for action in plugin: (1) `LlamaCppJniAiSummaryProvider` rename — affects the public Mojo configuration surface (`summaryProvider` parameter); (2) `AiGenerationResult` shape-or-name reconciliation; (3) `AiChecksumSupport` / `c` field — fix the algorithm/docs mismatch (CRC32 vs SHA-256) since that's worse than the naming itself.

### jllama — 1 finding (1 MODERATE)

| File:Line | Current | What it actually does | Suggested | Severity |
|---|---|---|---|---|
| ~~`ModelParameters.java:1427`~~ | ~~`isDefault(String key)`~~ | Returns `true` only when the key is **absent** from the map — a key explicitly set to its default value still returns `false`. Name implies value comparison; implementation is presence check. | `isUnset` | ✅ **FIXED** in `ffbc06c` (this session — public API rename, no `@Deprecated` shim) |

No class-drift, no typos, no plurality mismatches, no cryptic names. The 5 `handle*` methods on `LlamaModel` (`handleCompletions`, `handleInfill`, etc.) deliberately mirror upstream llama.cpp server endpoint names (`/handle_completions`) — intentional traceability, keep as-is.

### Naming audit — totals across 4 repos

| Repo | CRITICAL | MODERATE | MINOR | Total | Fixed this session |
|---|:--:|:--:|:--:|:--:|:--:|
| BAF | 2 | 3 | 1 | 6 | 2 (Bech32Helper plural→singular `cc37a5d`; CKeyProducerJavaIncremental startAddress/endAddress→startPrivateKey/endPrivateKey `83ada00`) |
| sb | 0 | 4 | 3 | 7 | 7 (all closed: typo `966595c` + 3 method renames `cf2b5fd` + final 3 cleanups `16f1df7`) |
| plugin | 0 | 4 | 3 | 7 | 2 (CRC32 docs `8930e4d` + AiResponseNormalizer→AiCompletionParser rename `6567b9e`) |
| jllama | 0 | 1 | 0 | 1 | 1 (isDefault → isUnset `ffbc06c`) |
| **All** | **2** | **12** | **7** | **21** | **12 fixed, 9 remain** (both CRITICAL done; sb fully cleared) |

**Top 5 to fix first (CRITICAL + highest-impact MODERATE):**
1. ✅ BAF `CKeyProducerJavaIncremental.startAddress/endAddress` → `startPrivateKey/endPrivateKey` — public JSON config field rename. **Fixed in `83ada00`.**
2. ✅ BAF `Bech32Helper.getWitnessPrograms` — plural name returns a single value. **Fixed in `cc37a5d`.**
3. ✅ plugin `AiChecksumSupport` — turned out to be **docs-only drift** (`CLAUDE.md` was wrong; implementation has always been correct CRC32). **Fixed in `8930e4d`.**
4. plugin `AiGenerationResult` — name says "summary + keywords + body" but the class carries only `body`. Either restore the missing fields or rename to `AiBodyResult`. (**Still open**)
5. plugin `LlamaCppJniAiSummaryProvider` → `LlamaCppJniAiGenerationProvider` — predates generalization to `AiGenerationProvider`; rename to mirror `MockAiGenerationProvider` sibling. (**Still open** — earlier table mistakenly conflated this with the `AiResponseNormalizer` rename in `6567b9e`; that commit was a *different* plugin rename and did NOT touch this class)

**This session's additional renames (not in the top-5 list)**:
- ✅ sb `validateOffsetAndLength*` + `shouldTrim` bundle (`cf2b5fd`) — 3 MODERATE
- ✅ plugin `AiResponseNormalizer` → `AiCompletionParser` + `normalize` → `parseCompletion` (`6567b9e`) — escalated from MINOR after class-name-drift verification confirmed the broader rename
- ✅ jllama `isDefault` → `isUnset` (`ffbc06c`) — MODERATE

**Top-5 progress: 2 of 5 fixed (#2, #3). Open: 1 CRITICAL + 2 MODERATE.**

---

## CLAUDE.md TODO list staleness — recommended actions

| Repo | What is stale | Suggested fix |
|---|---|---|
| **BAF** | ✅ Fully refreshed in `05d9ddf` + `5b16c77` (this session) — Error Prone → ERROR, `-parameters`, Banned-API enforcement, ArchUnit public-fields-final all marked DONE; the Persistence-backends entry has been rewritten to reflect shipped state (HashSet + TRUNCATED_LONG_64 backends, BloomFilterAccelerator extraction, AddressLookupBackend config enum, chain contract — all DONE). Remaining open in the Persistence entry: 3 stale example JSON `loadToMemoryCacheOnInit` lines + JMH migration + open-hash backend + standalone Bloom backend. | — |
| **plugin** | ✅ **FIXED** in `9be6f17` (this session) — the bullet now correctly says module-level `@NullMarked` IS set with `requires static org.jspecify;`. | — |
| **jllama** | Nothing material out of date. | — |
| **sb** | Nothing material out of date. | — |
