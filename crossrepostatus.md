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
| Lombok 1.18.46 `@ToString` / `@EqualsAndHashCode` adoption (clears IMC_NO_TOSTRING + IMC_NO_EQUALS at SpotBugs Max+Low) | ✅ (BAF Lombok loop — 56 classes, 0 handwritten Object methods left) | ✅ `9be73a3` (this session) — 23 classes annotated; OSInfo / exceptions / enums / interfaces / non-instantiable utilities intentionally skipped | ✅ `39e1a59` + `6955357` (this session) — 6 `@ConvertToRecord` value types migrated, 19 service/codec/Mojo classes annotated, IMC_NO_EQUALS suppressed for identity-semantic Mojos / JavaBeans / service classes with rationale | ➖ excluded by design (user choice) |
| **Standing policies** | | | | |
| DO NOT UPGRADE jqwik past 1.9.3 | 📌 active | 📌 active | 📌 active | 📌 active |

---

## Cross-repo open items (compact summary)

Items that affect ≥ 2 repos. Single-repo items are in each repo's `TODO.md`.

### Affects all 4 repos
- **SpotBugs `effort=Max` + `threshold=Low`** — open in BAF, jllama, plugin. **sb done** (`4374dea` + `e7e254a`). Path that worked for sb: flip pom config, run `spotbugs:check`, fix each finding at source rather than suppressing the pattern globally (`waitForAtLeast` assertion → IllegalArgumentException; 7 weak-exception-messaging sites gain state-dependent context in the message; explicit `toString()` snapshotting state under `bufferLock`). 290 tests pass; zero project-wide suppressions added. See the [**SpotBugs Max+Low remaining findings tracker**](#spotbugs-maxlow-remaining-findings-tracker) below for the per-pattern breakdown.
- **Package hierarchy review** (recurring; centralised at [`policies/code-quality-todos.md`](policies/code-quality-todos.md)).

### SpotBugs Max+Low remaining findings tracker

> **Lifecycle note.** This section is a transient working table. **Delete it once
> all four repos either fix every finding at source or carry a documented
> suppression in their respective `spotbugs-exclude.xml`.** After that the only
> remaining row in the table above is the green "✅ Max+Low enforced" cell per
> repo.

Snapshot taken with the per-repo SpotBugs effort temporarily flipped to
`Max` + `Low` (then reverted) on top of the Lombok-migration commits:

| Repo | Total | Δ vs initial snapshot | Effort/Threshold (pom default) |
|---|---:|---:|---|
| BAF | **191** | −24 | Default+Default (lift pending) |
| jllama | **90** | −18 | Default+Default (lift pending) |
| plugin | **3** | −29 | Default+Default (lift pending) |
| sb | 0 | — | ✅ Max+Low enforced |

**Δ source so far:**
1. Lombok-USBR suppression in all three Lombok-using repos
   (BAF `6ddd69e`, jllama `ce8b466`, plugin `4bd4dc0`). Single
   `<Match>` per `spotbugs-exclude.xml` matching the
   `USBR_UNNECESSARY_STORE_BEFORE_RETURN` bug pattern on the four method
   names Lombok can emit (`equals`, `hashCode`, `canEqual`, `toString`).
   Cleared **48 findings**, no source change.
2. Plugin HelpMojo class-scoped exclude extended from 3 to 7 patterns
   (`AI_ANNOTATION_ISSUES_NEEDS_NULLABLE`, `WEM_WEAK_EXCEPTION_MESSAGING`,
   `UI_INHERITANCE_UNSAFE_GETRESOURCE`, `SPP_FIELD_COULD_BE_STATIC`) plus
   a new SPP suppression for the eight `@Parameter` instance fields on
   `GenerateMojo` / `AggregatePackagesMojo` (Maven's plugin contract
   requires INSTANCE fields for reflection-based per-execution
   injection; static would skip injection). Plugin commit `049c1ae`.
   Cleared **13 findings** (5 on HelpMojo + 8 on the project Mojos).
3. Plugin tail cleanup landed as three independently-revertible commits:
   - `dbfe742` — drop `AiMdDocumentCodec.read(List)` and
     `write(AiMdDocument)` to package-private (test-seam overloads;
     production reaches them through the `Path` forms). Source fix,
     clears 2 × `OPM_OVERLY_PERMISSIVE_METHOD`.
   - `41d6141` — scoped suppression for
     `AI_ANNOTATION_ISSUES_NEEDS_NULLABLE` on
     `GenerateMojo.resolveFileExtensions`. Tried a source restructure
     (hoist field to local) first; fb-contrib's analyzer is too coarse
     to track the narrowing. Rationale: method provably cannot return
     null, so adding `@Nullable` would lie about the contract.
   - `f56940c` — scoped suppression for `FORMAT_STRING_MANIPULATION`
     on the prompt-template pipeline (`Java8CompatibilityHelper` +
     `AiPromptSupport`). Rationale: configurable prompt templates
     from POM `<configuration>` ARE the plugin's feature; a malformed
     template raises `IllegalFormatException` at build time.
4. Plugin RCN + WEM source pass landed as two commits:
   - `629d145` — harden `AiGenerationResult` ctor with
     `Objects.requireNonNull(body)` so the `@NonNull` contract is
     enforced at the boundary; delete the now-redundant
     `(result.body() == null)` check at `PackageIndexer:246`. Also
     incidentally enriches `PackageIndexer.writePackageFile`'s
     `IllegalArgumentException` with the offending `directory`.
     Cleared 1 RCN + 1 WEM.
   - `95ec43a` — 4 more WEM enrichments following the same pattern
     (static prefix + the relevant in-scope value): `AggregatePackagesMojo`,
     `GenerateMojo`, `SourceFileIndexer`, `AiCompletionParser`.
   Total cleared by step 4: 1 RCN + 5 WEM = **6 findings**.

**Per-pattern matrix** (counts at Max+Low; entries marked `—` are zero on
that repo). Patterns are grouped by remediation approach so a single
session can take down a whole group across multiple repos.

| Pattern | BAF | jllama | plugin | Group / fix approach |
|---|---:|---:|---:|---|
| **Logging / I/O safety** | | | | |
| `CRLF_INJECTION_LOGS` | 68 | — | — | Sanitise log inputs (strip `\r\n`); BAF-only because it carries the most logger calls. |
| **Method-shape hygiene** | | | | |
| `OPM_OVERLY_PERMISSIVE_METHOD` | 33 | 25 | ~~2~~ **0** | Tighten visibility (`public`→package-private) where no external caller exists. Cross-repo refactor. (Plugin's 2 sites done in `dbfe742`.) |
| `UPM_UNCALLED_PRIVATE_METHOD` | 7 | — | — | Delete unused private methods. |
| `SPP_FIELD_COULD_BE_STATIC` | — | 1 | ~~9~~ **0** | jllama site needs case-by-case judgement. Plugin's were structural false positives on Maven `@Parameter` fields plus the auto-generated `HelpMojo.goal`; suppressed in plugin `049c1ae`. |
| `MS_SHOULD_BE_FINAL` | 1 | — | — | Mark mutable static `final`. |
| `URF_UNREAD_FIELD` | 1 | — | — | Delete the unused field. |
| **Exception messaging** | | | | |
| `WEM_WEAK_EXCEPTION_MESSAGING` | 26 | 14 | ~~6~~ **0** | Add state-dependent context to `throw new …Exception("…")` sites (sb's pattern). Cross-repo. (Plugin: 1 `HelpMojo` site suppressed in `049c1ae`; 5 source sites enriched in `629d145` + `95ec43a`.) |
| `DRE_DECLARED_RUNTIME_EXCEPTION` | 10 | 20 | — | Remove `@throws RuntimeException` from Javadoc / `throws` clauses; replace with the actual subclass or drop. |
| `THROWS_METHOD_THROWS_RUNTIMEEXCEPTION` | 15 | 4 | — | Same family; signature cleanup. |
| `THROWS_METHOD_THROWS_CLAUSE_BASIC_EXCEPTION` | 3 | 1 | — | Narrow `throws Exception` to a specific subclass. |
| **Type / null hygiene** | | | | |
| `BC_UNCONFIRMED_CAST` | 9 | — | — | Add `instanceof` guards or explicit `@SuppressWarnings` with rationale. |
| `RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE` | — | 3 | ~~4~~ **3** | Delete the redundant null check (NullAway already proves non-null). (Plugin: `PackageIndexer:246` cleared in `629d145` by hardening the `AiGenerationResult` ctor with `Objects.requireNonNull`. 3 remaining sites on `@Parameter`-list ingestion constructors awaiting design call — runtime checks may be legitimate against Maven reflection injection.) |
| `OI_OPTIONAL_ISSUES_CHECKING_REFERENCE` | — | 2 | — | `if (opt != null)` → `if (opt.isPresent())`. |
| `AI_ANNOTATION_ISSUES_NEEDS_NULLABLE` | — | 1 | ~~3~~ **0** | Add `@Nullable` on the documented-nullable returns. (Plugin's 2 `HelpMojo` sites suppressed in `049c1ae`; the `GenerateMojo.resolveFileExtensions` site suppressed in `41d6141` after a source restructure attempt didn't satisfy fb-contrib.) |
| `FORMAT_STRING_MANIPULATION` | — | 1 | ~~1~~ **0** | Use parameterised `String.format` instead of `+` concatenation in format args. (Plugin's site suppressed in `f56940c` — configurable prompt templates from POM are the plugin's feature.) |
| `NP_LOAD_OF_KNOWN_NULL_VALUE` | 1 | — | — | Remove the redundant load. |
| **Concurrency / threading** | | | | |
| `MDM_THREAD_YIELD` | 5 | — | — | Replace `Thread.yield()` with `LockSupport.parkNanos` or document the busy-wait rationale. |
| `MDM_WAIT_WITHOUT_TIMEOUT` | — | 4 | — | Add timeout to `Object.wait()` calls. |
| `MDM_RANDOM_SEED` | 2 | — | — | Avoid seeded `new Random()`; use `ThreadLocalRandom.current()` or `SecureRandom`. |
| **Misc Java idioms** | | | | |
| `UVA_USE_VAR_ARGS` | 3 | 5 | — | Convert array-parameter overloads to varargs where source-compatible. |
| `DLS_DEAD_LOCAL_STORE` | 4 | 1 | — | Remove the dead assignment. |
| `PRMC_POSSIBLY_REDUNDANT_METHOD_CALLS` | 1 | 1 | — | Hoist invariant method calls out of loops. |
| `BIT_PRIMITIVE` | 1 | — | — | Replace `byteVal & 0xFF` style with explicit `Byte.toUnsignedInt(b)`. |
| `LO_SUSPECT_LOG_CLASS` | — | 1 | — | Pass the correct `Class` to `LoggerFactory.getLogger`. |
| `REC_CATCH_EXCEPTION` | — | 1 | — | Replace `catch (Exception)` with the specific subclasses. |
| `CWO_CLOSED_WITHOUT_OPENED` | — | 1 | — | Close-without-open false positive likely; suppress with rationale or restructure. |
| `UI_INHERITANCE_UNSAFE_GETRESOURCE` | — | — | ~~1~~ **0** | Inside auto-generated `HelpMojo`; suppressed in plugin `049c1ae`. |
| **Crypto / security** | | | | |
| `HARD_CODE_KEY` | 1 | — | — | Likely the BAF secp256k1 generator constant; suppress with rationale (public curve parameter, not a key). |

**Suggested execution order** (lowest-risk → highest):

1. ~~Apply the `USBR_UNNECESSARY_STORE_BEFORE_RETURN` Lombok suppression
   in all three repos.~~ ✅ **Done** (BAF `6ddd69e`, jllama `ce8b466`,
   plugin `4bd4dc0`). 48 findings cleared.
2. ~~Extend plugin's `HelpMojo` class-scoped exclude (4 patterns) and
   suppress `SPP_FIELD_COULD_BE_STATIC` on the project's own
   `@Parameter` Mojos.~~ ✅ **Done** (plugin `049c1ae`). 13 findings
   cleared (5 on HelpMojo + 8 structural false positives on Maven
   `@Parameter` instance fields). Plugin is now at 13 total.
3. ~~Plugin tail cleanup: 2 × `OPM`, 1 × `AI_ANNOTATION`,
   1 × `FORMAT_STRING_MANIPULATION`.~~ ✅ **Done** (plugin `dbfe742`,
   `41d6141`, `f56940c`). 4 findings cleared. Plugin now at 9 total —
   in striking distance of flipping the pom to `Max+Low` permanently.
4. ~~Plugin RCN + WEM source pass.~~ ✅ **Mostly done** (`629d145`
   + `95ec43a`). 6 findings cleared (1 RCN + 5 WEM). Plugin now at
   3 total. **Remaining 3** on plugin are all the same shape:
   `RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE` on `@Parameter`-list
   ingestion constructors (`AiModelDefinitionSupport`,
   `AiPromptSupport`). Awaiting a design call — runtime checks may
   be legitimate against Maven reflection injection, in which case
   the answer is a scoped suppression with rationale; if the call
   instead is to enforce the contract upstream (Mojo validation),
   the source pass continues.
5. After step 4 lands, plugin flips `<effort>Max</effort>` +
   `<threshold>Low</threshold>` in pom.xml permanently and the
   plugin row in the top table goes ✅.
6. **`RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE`** — delete the redundant
   null checks. Mechanical fix; remaining 3 sites in jllama.
7. **`WEM_WEAK_EXCEPTION_MESSAGING`** — add contextful messages following
   sb's pattern. ~40 sites across BAF+jllama; the highest-impact source
   change.
8. **`OPM_OVERLY_PERMISSIVE_METHOD`** — tighten visibility. Careful: any
   `public` method that genuinely is part of the public API gets a
   per-method `@SuppressFBWarnings` instead.
9. **`CRLF_INJECTION_LOGS`** (BAF only, 68 sites) — sanitisation at the
   logger boundary. Either a wrapping helper or a project-wide
   pattern-match exclusion if the inputs are demonstrably trusted.
10. Remaining low-count categories — fix or suppress with rationale.

Once a repo reaches zero outstanding findings at Max+Low, **flip the
pom.xml `<effort>` to `Max` and `<threshold>` to `Low` in the same
commit** and update the "SpotBugs `effort=Max` + `threshold=Low`" row in
the top table. When all four repos are green here, **delete this entire
"SpotBugs Max+Low remaining findings tracker" section**.

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
