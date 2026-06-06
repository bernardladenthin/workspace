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
| SpotBugs `effort=Max` + `threshold=Low` | ✅ `76fd1a7` — permanent flip; clean at the gate. Full chain: USBR-Lombok `6ddd69e` + CRLF layout `bd723f0` + WEM 3-batch `c2c3d62` / `4677831` / `dcee87d` + THROWS A/B/C `bd71766` + THROWS Group D `40d3f09` + DRE `5b72265` + 3× MDM structural refactors (AbstractProducer `892b76a`, ConsumerJava `99f390f`, ProducerOpenCL `09c5d52`) + MDM narrow suppression `cb02c70` + OPM project-wide suppression pending package refactor `52c8c95` + final 36-finding sweep `76fd1a7` (7 source fixes + 29 narrow `<Match>` suppressions with rationale). | ❌ pom both `Default`; **90** findings at Max+Low (USBR-Lombok suppression in `ce8b466` already applied). Top patterns: OPM 25 (now suppressed `07109cc` — pending package refactor), DRE 20, WEM 14. | ✅ `0bddf2a` — permanent flip; clean at the gate with documented suppression chain (Lombok-USBR, HelpMojo auto-gen family, Maven `@Parameter` SPP, identity-IMC, prompt-template FORMAT_STRING, fb-contrib flow-coarseness sites, NPE→MojoExecutionException bridge) plus source fixes (Lombok adoption, `Objects.requireNonNull` fail-fast in support ctors, enriched WEM messages, presized HashMaps). | ✅ `4374dea` + `e7e254a` — flipped to Max+Low, all findings fixed at source (added `toString()`, contextful exception messages), no project-wide suppressions |
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
- **SpotBugs `effort=Max` + `threshold=Low`** — ✅ sb (`4374dea` + `e7e254a`), ✅ plugin (`0bddf2a`), ✅ BAF (`76fd1a7` — final 36-finding sweep landed; gate now enforces zero unsuppressed findings). ❌ open in jllama (**90** at last snapshot — OPM project-wide suppression `07109cc` already applied, leaves ~65 to attack via the same playbook). The BAF/sb/plugin pattern: flip pom config, run `spotbugs:check`, fix each finding at source where reasonable, suppress narrowly with rationale where structural (Lombok-generated equals/hashCode, generator-emitted Mojo bytecode, Maven `@Parameter` reflection contract, CRLF-injection sanitised at the Logback PatternLayout layer, generic-erasure CHECKCAST in keyproducer hierarchy, etc.). See the [**SpotBugs Max+Low remaining findings tracker**](#spotbugs-maxlow-remaining-findings-tracker) below for the per-pattern breakdown.
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

### SpotBugs Max+Low remaining findings tracker

> **Lifecycle note.** This section is a transient working table. **Delete it once
> all four repos either fix every finding at source or carry a documented
> suppression in their respective `spotbugs-exclude.xml`.** After that the only
> remaining row in the table above is the green "✅ Max+Low enforced" cell per
> repo.

> **Status this session:** plugin and sb are green at the gate. BAF and
> jllama still carry findings — the table below is the live state after
> running `mvn spotbugs:check` with `<effort>Max</effort> +
> <threshold>Low</threshold>` temporarily set in each repo's pom (then
> reverted). BAF and jllama already carry the Lombok-USBR suppression
> (commits `6ddd69e` and `ce8b466` respectively); those 48 findings are
> already excluded from the totals below.

Snapshot taken with the per-repo SpotBugs effort temporarily flipped to
`Max` + `Low` (then reverted) on top of the Lombok-migration commits:

| Repo | Total | Δ vs initial snapshot | Effort/Threshold (pom default) |
|---|---:|---:|---|
| BAF | **86** | −129 | Default+Default (lift pending) |
| jllama | **90** | −18 | Default+Default (lift pending) |
| plugin | **0** | −32 | ✅ Max+Low enforced (`0bddf2a`) |
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
5. Plugin fail-fast pass on `@Parameter`-list ingestion (`086d8c2`):
   - `AiPromptSupport` / `AiModelDefinitionSupport` constructors
     replace silent-skip `if (... != null)` with
     `Objects.requireNonNull(field, Supplier<String>)` carrying a
     rich message (list index + bad entry via Lombok `@ToString`).
   - `AbstractAiIndexMojo.buildPromptSupport` /
     `buildAiModelDefinitionSupport` wrap construction with
     `try/catch (NullPointerException)` and rethrow as
     `MojoExecutionException` so Maven reports user-config errors
     under the framework's "fix your POM" framing instead of as a
     plugin bug.
   - `Objects.requireNonNull` is not pattern-matched by fb-contrib's
     RCN (it's a method call, not a syntactic `x != null` check), so
     the 3 RCN findings clear without any project-wide suppression.
     Single DCN suppression for the deliberate NPE catch in the Mojo
     bridge, with the full rationale recorded inline.
   - Test rewrite:
     `getConfig_definitionWithNullKey_ignoredDuringConstruction` →
     `constructor_definitionWithNullKey_throwsWithIndexAndBadEntry`.
   - Two pattern regressions surfaced and fixed in the same commit:
     `PSC_PRESIZE_COLLECTIONS` (now both ctors presize their HashMap
     with a load-factor-corrected formula) and `POTENTIAL_XML_INJECTION`
     (dropped the `<configuration>` literal from the wrapped message).
   Total cleared by step 5: 3 RCN + 2 secondary = **5 findings to 0**.
6. Plugin pom permanently flipped to
   `<effort>Max</effort> + <threshold>Low</threshold>` (`0bddf2a`).
   Plugin row in the top table goes ✅. Second repo green at the gate
   after sb. The load-factor presize formula was later extracted into
   `Java8CompatibilityHelper.hashMapCapacityFor(int)` (`b987f3c`) — same
   value as JDK 19+'s `HashMap.newHashMap(int)`, no duplication left
   across the two support ctors.

**Per-pattern matrix** (counts at Max+Low; entries marked `—` are zero on
that repo). Patterns are grouped by remediation approach so a single
session can take down a whole group across multiple repos.

| Pattern | BAF | jllama | plugin | Group / fix approach |
|---|---:|---:|---:|---|
| **Logging / I/O safety** | | | | |
| `CRLF_INJECTION_LOGS` | ~~68~~ **0** | — | — | ✅ **BAF cleared in `bd723f0`** by adding `src/main/resources/logback.xml` with a `%replace(%msg){'[\r\n]+', ' \| '}` PatternLayout wrap on every appender (and same on `examples/logbackConfiguration.xml`); project-wide `<Match>` in `spotbugs-exclude.xml` with full rationale + OWASP/SEI CERT/find-sec-bugs references. Zero source edits; the security control lives at the appender layer and covers every `LOGGER.*` call (including transitive dependency logs and future contributor additions). |
| **Method-shape hygiene** | | | | |
| `OPM_OVERLY_PERMISSIVE_METHOD` | **suppressed** (was 33) | **suppressed** (was 25) | ~~2~~ **0** | **BAF + jllama suppressed project-wide** (BAF `52c8c95`, jllama `07109cc`) until the planned package-architecture refactor lands — current single-root package layout would mass-flag tomorrow's correctly-`public` methods as "should be package-private" today. Re-enable once layers split. Plugin's 2 sites already done in `dbfe742`. See "OPM scope-tightening — after package refactor" entry below. |
| `UPM_UNCALLED_PRIVATE_METHOD` | 7 | — | — | Delete unused private methods. |
| `SPP_FIELD_COULD_BE_STATIC` | — | 1 | ~~9~~ **0** | jllama site needs case-by-case judgement. Plugin's were structural false positives on Maven `@Parameter` fields plus the auto-generated `HelpMojo.goal`; suppressed in plugin `049c1ae`. |
| `MS_SHOULD_BE_FINAL` | 1 | — | — | Mark mutable static `final`. |
| `URF_UNREAD_FIELD` | 1 | — | — | Delete the unused field. |
| **Exception messaging** | | | | |
| `WEM_WEAK_EXCEPTION_MESSAGING` | ~~26~~ **0** | 14 | ✅ 0 | ✅ **BAF cleared** via 3-batch source pass: Batch 1 (`c2c3d62`) enriched 8 leaf-utility / validator sites with in-scope state. Batch 2 (`4677831`) extended `AddressFormatNotAcceptedException` with new `(reason, detail)` and `(reason, detail, cause)` ctor overloads that preserve the `getReason()` aggregation contract while enriching `getMessage()` — same design now becomes the cross-repo recommendation per the typed-exception-unification audit row. 8 throw sites in `AddressTxtLine.fromLine` switched to the new ctors. Batch 3 (`dcee87d`) enriched 10 remaining mixed sites (`AddressTxtLine:248`, `AbstractProducer` ×2, `AbstractKeyProducerQueueBuffered` ×4, `BIP39KeyProducer`, `OpenClTask` ×2). Plugin: 1 `HelpMojo` site suppressed in `049c1ae`; 5 source sites enriched in `629d145` + `95ec43a`. |
| `DRE_DECLARED_RUNTIME_EXCEPTION` | ~~10~~ **0** | 20 | — | ✅ **BAF cleared in `5b72265`**: dropped `throws NoMoreSecretsAvailableException` / `throws RuntimeException` from 10 signatures where every declared exception is unchecked (JDK convention — advertise via Javadoc `@throws` only). Sites: `KeyProducer`/`SecretSupplier` interfaces, `AbstractKeyProducerQueueBuffered`, `KeyProducerJavaBip39`/`Incremental`/`Random`, `KeyUtility.createSecrets`, `BIP39KeyProducer.nextKey`, `KeyProducerJava.verifyWorkSize` (bonus: dropped misleading Javadoc tag — method throws `IllegalArgumentException` — and enriched message from "Unreasonable work size: <n>" to "overallWorkSize=<n> out of range [0, <max>]"), `Finder.getKeyProducer` (replaced generic `throws RuntimeException` with `@throws KeyProducerIdUnknownException` Javadoc on the typed exception already thrown). 459 tests green. |
| `THROWS_METHOD_THROWS_RUNTIMEEXCEPTION` | ~~15~~ **0** | 4 | — | ✅ **BAF cleared.** Groups A/B/C landed in `bd71766` (13 of 15 — `UncheckedIOException` ×2, `IllegalStateException` ×9, new `InterruptedRuntimeException` ×2). Group D landed in `40d3f09` (2 catch+cleanup+rethrow sites — narrow suppression with rationale + lifecycle TODO). Group D investigation rejected three custom-exception wrappers as semantically worse than suppression — see "Cross-repo open items" entry below for the documented "what NOT to do" so future maintainers do not re-derive it. |
| `THROWS_METHOD_THROWS_CLAUSE_BASIC_EXCEPTION` | 3 | 1 | — | Narrow `throws Exception` to a specific subclass. |
| **Type / null hygiene** | | | | |
| `BC_UNCONFIRMED_CAST` | 9 | — | — | Add `instanceof` guards or explicit `@SuppressWarnings` with rationale. |
| `RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE` | — | 3 | ✅ 0 | Delete the redundant null check (NullAway already proves non-null). (Plugin: `PackageIndexer:246` cleared in `629d145` by hardening the `AiGenerationResult` ctor with `Objects.requireNonNull`. The 3 sites on `@Parameter`-list ingestion ctors cleared in `086d8c2` by switching to the fail-fast `Objects.requireNonNull(field, Supplier<String>)` pattern with `NullPointerException` → `MojoExecutionException` translation in the Mojo bridge.) |
| `OI_OPTIONAL_ISSUES_CHECKING_REFERENCE` | — | 2 | — | `if (opt != null)` → `if (opt.isPresent())`. |
| `AI_ANNOTATION_ISSUES_NEEDS_NULLABLE` | — | 1 | ~~3~~ **0** | Add `@Nullable` on the documented-nullable returns. (Plugin's 2 `HelpMojo` sites suppressed in `049c1ae`; the `GenerateMojo.resolveFileExtensions` site suppressed in `41d6141` after a source restructure attempt didn't satisfy fb-contrib.) |
| `FORMAT_STRING_MANIPULATION` | — | 1 | ~~1~~ **0** | Use parameterised `String.format` instead of `+` concatenation in format args. (Plugin's site suppressed in `f56940c` — configurable prompt templates from POM are the plugin's feature.) |
| `NP_LOAD_OF_KNOWN_NULL_VALUE` | 1 | — | — | Remove the redundant load. |
| **Lombok-skip residue** | | | | |
| `IMC_IMMATURE_CLASS_NO_EQUALS` | — | 2 | — | jllama: `CancellationToken` (lifecycle handle, identity-by-design) and `ChatRequest` (mutable builder, identity-by-design) — both deliberately got `@ToString` only during the Lombok migration. Either flip to value-equality or add a narrow `<Match>` per class with rationale (BAF pattern). |
| `IMC_IMMATURE_CLASS_WRONG_FIELD_ORDER` | — | 2 | — | jllama: `LlamaModel` (native `ctx` field before the static parser-collaborator fields) and `ModelParameters` (same pattern). Move the static fields above the instance fields, or suppress (the native-handle placement is conventional). |
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
4. ~~Plugin RCN + WEM source pass.~~ ✅ **Done** (`629d145` + `95ec43a`).
   6 findings cleared (1 RCN + 5 WEM).
5. ~~Plugin's final 3 RCN findings on `@Parameter`-list ingestion
   constructors.~~ ✅ **Done** (`086d8c2`) — chose the
   fail-fast-with-rich-error answer: `Objects.requireNonNull(field, ()
   -> "list[i].field is required (bad entry: ...)")` in the support
   ctors, `try/catch (NullPointerException)` in the Mojo helpers
   rethrowing as `MojoExecutionException`. One DCN suppression for the
   deliberate NPE catch; rationale recorded in `spotbugs-exclude.xml`.
   The associated test was rewritten to assert the new fail-fast
   contract (`constructor_definitionWithNullKey_throwsWithIndexAndBadEntry`).
6. ~~Plugin pom flip to permanent Max+Low.~~ ✅ **Done** (`0bddf2a`).
   Plugin is the second repo green at the gate after sb. The
   load-factor presize formula was later extracted to
   `Java8CompatibilityHelper.hashMapCapacityFor(int)` (`b987f3c`) to
   remove duplication across the two support ctors.
7. **`RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE`** — remaining 3 sites
   in jllama. Mechanical fix per site, or apply the same fail-fast
   pattern plugin landed in step 5.
8. ~~`WEM_WEAK_EXCEPTION_MESSAGING` on BAF.~~ ✅ **Done** (BAF 3-batch
   source pass `c2c3d62` / `4677831` / `dcee87d`). 26 → 0 on BAF.
   The Batch 2 design — new `(reason, detail)` and
   `(reason, detail, cause)` constructor overloads on
   `AddressFormatNotAcceptedException` that preserve the `getReason()`
   aggregation contract — became the precedent for the cross-repo
   typed-exception unification audit row added above. Still open:
   jllama (14 sites) — same pattern applies.
9. ~~`OPM_OVERLY_PERMISSIVE_METHOD` — tighten visibility.~~ ✅ **Suppressed
   project-wide in BAF (`52c8c95`) and jllama (`07109cc`)** pending the
   package-architecture refactor. Plugin's 2 sites already done in
   `dbfe742`. Re-enable the rule (delete each repo's project-wide
   `<Match>` block) the week the layered package structure stabilises;
   at that point genuine "method exposed beyond its actual call site"
   findings become stable, fixable signals. Full rationale + per-category
   breakdown in the "OPM scope-tightening — after package refactor"
   entry below.
10. ~~`CRLF_INJECTION_LOGS` (BAF only, 68 sites).~~ ✅ **Done** (BAF
    `bd723f0`). Chose layout-level mitigation: bundled
    `src/main/resources/logback.xml` ships a `%replace(%msg){'[\r\n]+', ' | '}`
    PatternLayout wrap so every `LOGGER.*` call is sanitised at the
    appender layer. Per-site wrapping rejected (68 mechanical edits,
    fragile against future contributors); `org.owasp:security-logging-logback`
    rejected (unmaintained since 2021-12-15 — equivalent function is
    ~20 lines of regex wrapped as a `CompositeConverter`). Project-wide
    suppression in `spotbugs-exclude.xml` documents the layout pattern
    as the security control with OWASP / SEI CERT / find-sec-bugs
    references inline. BAF total dropped 191 → 123.
11. Remaining low-count categories — fix or suppress with rationale.

Once a repo reaches zero outstanding findings at Max+Low, **flip the
pom.xml `<effort>` to `Max` and `<threshold>` to `Low` in the same
commit** and update the "SpotBugs `effort=Max` + `threshold=Low`" row in
the top table. When all four repos are green here, **delete this entire
"SpotBugs Max+Low remaining findings tracker" section**.

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
