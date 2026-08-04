# Cross-Repo Status Table

This file tracks **only items that span ≥ 2 of the four sibling repos**. Single-repo open work has been moved into each repo's own `TODO.md`:

- [`../BitcoinAddressFinder/TODO.md`](../BitcoinAddressFinder/TODO.md)
- [`../java-llama.cpp/TODO.md`](../java-llama.cpp/TODO.md)
- [`../srcmorph/TODO.md`](../srcmorph/TODO.md)
- [`../streambuffer/TODO.md`](../streambuffer/TODO.md)

Recurring per-repo audits (mostly cross-repo by nature but living per-repo today) are documented in [`policies/code-quality-todos.md`](policies/code-quality-todos.md).

Repos:
- **BAF** = `/home/user/BitcoinAddressFinder`
- **jllama** = `/home/user/java-llama.cpp`
- **plugin** = `/home/user/srcmorph` (repo renamed `llamacpp-ai-index-maven-plugin` → **srcmorph**, now a 3-module reactor; the `plugin` shorthand is kept here for continuity with the historical rows below)
- **sb** = `/home/user/streambuffer`

> **Scope note:** the parity/history tables below track the **four sibling library repos**
> (BAF, jllama, srcmorph, sb). The **do-not-bump registry** under "Dependency / plugin
> freshness" additionally covers **BroomCabinet** pins, because a cross-repo dependency audit
> needs one reference for every deliberate pin regardless of which repo owns it.

Legend: ✅ done · 🚧 in progress · ❌ open · ➖ N/A · 📌 standing policy

**Badge resources:** [inttter/md-badges](https://github.com/inttter/md-badges?tab=readme-ov-file) — searchable index of badge syntax for shields.io, Simple Icons, and more (used across all four repo READMEs).

---

## In parity across all 4 repos (no action needed)

| Dimension | Status |
|---|---|
| Error Prone `-Xep:<Name>:ERROR` promotions | Identical 13-pattern set in all 4 poms |
| NullAway `-XepOpt` options | Identical 6 standard options (`CheckOptionalEmptiness`, `AcknowledgeRestrictiveAnnotations`, `AcknowledgeAndroidRecent`, `AssertsEnabled`, `OnlyNullMarked`, strict JSpecify). Plugin additionally has `ExcludedFieldAnnotations=…@Parameter,@Component` — correct repo-local exception for Mojo POJOs. |
| Tool versions | Identical across all 4: Checker 4.2.1, fb-contrib 7.7.4, findsecbugs 1.14.0, spotbugs 4.10.3.0, spotless 3.9.0, palantir 2.96.0, errorprone 2.50.0, nullaway 0.13.8, surefire 3.5.6, archunit 1.4.2, junit-jupiter 6.1.2, hamcrest 3.0, pitest-maven 1.25.8 (pitest-junit5-plugin 1.2.3). **All on latest stable** — this row is the **canonical cross-repo tool-version matrix** (the policy files point here rather than re-pinning). Verified 2026-07-29 against the poms + Maven Central; see "Dependency / plugin freshness" below. |
| Maven Enforcer `bannedDependencies` | Identical 7-entry list |
| `<parameters>true</parameters>` javac arg | All 4 ✅ |
| PIT `<mutationThreshold>100</mutationThreshold>` | All 4 wired at a 100% gate. Scope expanded 2026-06-07 from the original single-class staging: **sb** whole-package (179 mutations) · **jllama** `value.*`+`exception.*`+`args.*`+`json.TimingsLogger`+`json.RerankResponseParser`+`json.ChatResponseParser`+`json.CompletionResponseParser` (243 mutations as of 2026-06-25; **not fully hermetic — see "Deliberate non-parity" below**) · **srcmorph** (reactor core module) explicit 47-class list · **BAF** explicit 16-class list (65 mutations). All previously pointed at one class; jllama's/BAF's were silently matching nothing after the package restructure (`llama.Pair`→`value.Pair`, `bitcoinaddressfinder.BitHelper`→`util.BitHelper`) — fixed. Canonical command + the `@{argLine}`/jacoco invocation rule live in [`policies/pit-mutation-testing.md`](policies/pit-mutation-testing.md). |
| Checker Framework as 2nd nullness pass | All 4 ✅ |
| JPMS `module-info.java` present | All 4 ✅ |
| ArchUnit standard set (`noSystemExit` / `noNewRandom` / `Thread.sleep` / sun-com.sun-jdk.internal bans / public-fields-final / `noTestFrameworksInProduction` / `noPackageCycles`) | All 4 ✅ |
| `javac -Werror` + `-Xlint:all,-serial,-options,-classfile,-processing` | All 4 ✅ |
| GPG signing-key preflight (`verify-signing-key` job) | All 4 wired **byte-identically** in `publish.yml`: a standalone job (**no `needs:`**, runs in parallel at pipeline start on **every** trigger) under `environment: maven-central` that reproduces what **maven-gpg-plugin** does at deploy time — import the key into an ephemeral keyring, assert it is present / not expired / signing-capable, then a **passphrase-unlock → detached-sign → verify roundtrip** — so a bad/expired key or wrong passphrase reds in ~20s instead of failing the publish stage. **Prints only PUBLIC key metadata** (key id, fingerprint, owner UID, algo, created/expiry); passphrase fed on **fd 3** (never argv/logs), `set -x` never enabled, passphrase `::add-mask::`ed. **Red-by-design** on refs where the secret is not delivered (fork PRs / other contributors' branches — the `maven-central` environment gate rejects them *before a runner is assigned*, so `runner_id: 0` + ~2s failure is the gate, not a runner shortage). Verified green on jllamacpp-ai-index `main` 2026-07-09 (key `ED0D9440BF148ED2`, "Good signature"). Added 2026-07-09, branch `claude/android-signing-failure-q7zml9`. A companion **Gradle/BouncyCastle** preflight is likewise byte-identical in all 4 — see the next row. |
| GPG signing-key preflight — Gradle/BouncyCastle (`verify-signing-key-gradle` job) | All 4 wired **byte-identically** (same job + the throwaway `.github/signing-selftest/` Gradle project). Companion to the gpg row above: it drives **Gradle's `signing` plugin + `useInMemoryPgpKeys` (BouncyCastle)** — the path any Gradle-based publish (e.g. an Android AAR) uses — which is a **stricter** armored-key parser than gpg, so it catches key/format problems gpg tolerates (it is exactly what surfaced the primary-vs-signing-subkey `null PGPPrivateKey`). It signs a throwaway Zip (**no repo build involved**), so it runs even in repos that don't publish via Gradle yet — **"prepared for Gradle"**, uniform-by-choice (identical pipelines preferred over minimalism). Same standalone / no-`needs:` / parallel / `environment: maven-central` / red-by-design / no-secret-material properties as the gpg row; selects the signing subkey via `MAVEN_GPG_KEY_ID` (env secret `GPG_KEY_ID = 07D2D767`, a public key id). Added 2026-07-09, branch `claude/android-signing-failure-q7zml9`. **The `.github/signing-selftest/` `.kts` files are now *literally* byte-identical in all 4** (dual-licensed `MIT OR Apache-2.0`) — until 2026-07-24 the body matched but the SPDX header drifted (jllama `MIT`, the others `Apache-2.0`); unified + `streambuffer/LICENSES/MIT.txt` added. Checksums recorded in the drift-check below. |

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

- Plugin's NullAway `ExcludedFieldAnnotations` extension — repo-correct (Mojo POJOs).
- BAF's lack of module-level `@NullMarked` — documented intentional (per-package `@NullMarked` covers the same scope, avoids `requires JSpecify`).
- sb keeps per-package `@NullMarked` — by design.
- The PIT per-repo `targetClasses` scope differs (sb whole-package; the other three an explicit/glob list of classes verified at 100%) — intentional: each repo gates exactly the classes proven to reach 100% mutation parity, expanded incrementally. **No classes remain permanently excluded** — the four that previously could not reach 100% were all fixed 2026-06-07 by small refactors / contract tests rather than left out: BAF `model.Hash160` (→ branch-free `hashFast`/`hashSlow`, `hash()` delegates), plugin `support.AiPathSupport` (→ `relative.startsWith("src")`, drops the always-true `getNameCount()>0` guard), plugin `provider.AiGenerationProviderFactory` (→ lazy model load in `LlamaCppJniAiGenerationProvider` so the `llamacpp-jni` branch is constructible native-free), and jllama `json.RerankResponseParser` (→ a test pinning the documented *mutable*-empty-list contract, which kills the immutable-`emptyList()` mutant). All four are now gated.
- **jllama's PIT gate is environment-conditional (not fully hermetic).** It reaches 100% only when the **audio test fixture** is present; without it the run is **98%** (4 `NO_COVERAGE` mutants in `value.ContentPart.audioFile(Path)` — the null-name guard, the `.wav`/`.mp3` dispatch, and `Files.readAllBytes`). The only test exercising that method is the model-/fixture-gated `AudioInputIntegrationTest`, which self-skips (`Assume`) when no audio clip is supplied (`net.ladenthin.llama.audio.input` — no committed default). Contrast the sibling `value.ContentPart.imageFile(Path)`, which **is** hermetic via temp-file unit tests (PNG/JPG/GIF/WEBP). So a green jllama PIT gate requires the CI audio fixture; the hermetic fix (a temp-`.wav`/`.mp3` unit test mirroring the image tests) is tracked in jllama `TODO.md`. The other three gates are fully hermetic. See [`policies/pit-mutation-testing.md`](policies/pit-mutation-testing.md) §4.
- **BAF's Coveralls/Codecov coverage source is the `test-opencl` (pocl) job, not the ubuntu `test` matrix** — intentional, and only BAF has this distinction (it is the only repo with OpenCL code). The ubuntu `test` matrix has no OpenCL ICD installed, so `@OpenCLTest`-annotated classes (`OpenCLContext`, `OpenClTask`, `OpenCLGridResult`, `ProducerOpenCL`, etc.) self-skip via `OpenCLPlatformAssume`, producing 0% coverage for the entire GPU pipeline. The `test-opencl` job installs pocl (a conformant OpenCL 3.0 CPU implementation), so the full test suite — including all `@OpenCLTest` classes — actually executes there. Both jobs run on every push/PR; only the JaCoCo artifact consumed by Coveralls/Codecov changed source (`jacoco-report-opencl` from `test-opencl`, not `jacoco-report` from `test`). BAF `publish.yml` commit `5d5db1a`.
- **Depot / `sccache` shared compiler cache — java-llama.cpp only.** jllama's CI fronts the C/C++ compiler with `sccache` backed by **Depot Cache** over sccache's WebDAV backend (`SCCACHE_WEBDAV_ENDPOINT: https://cache.depot.dev`, `SCCACHE_WEBDAV_TOKEN: ${{ secrets.DEPOT_TOKEN }}`, plus `BUILD_JOBS` to bound macOS-runner memory) so its heavy native build (134 llama.cpp TUs + ggml + the 16.6k-line `httplib.cpp`, all `-O3`) recompiles only changed files and shares the cache across branches. Wiring lives in jllama `.github/build.sh` + `.github/workflows/publish.yml`; rationale in jllama `CLAUDE.md` "CI build cache & parallelism (sccache + Depot)". **This is jllama-only by nature, not drift:** `sccache` caches *compiler* output (C/C++/Rust/CUDA) and jllama is the only sibling with a native (C++/JNI) compile. The three pure-Maven siblings (BAF, sb, plugin) have no C/C++ to cache, run on **GitHub-hosted** runners (Depot's *GitHub Actions* cache backend activates only on **Depot-hosted** runners — see [Depot docs](https://depot.dev/docs/cache/integrations/github-actions)), and already cache Maven deps via `actions/setup-java`'s `cache: maven` (GitHub's per-branch cache). The `DEPOT_TOKEN` organization secret was added to **all** repos (2026-06-20) but is **inert** outside jllama. The README "Build cache by Depot" badge (jllama `README.md`) is therefore kept **jllama-only on purpose** — adding it to the Maven repos would advertise a capability they don't have. Same shape as the BAF-only pocl/OpenCL coverage entry above (a real per-repo capability difference, not a parity gap to close).
- **`jar-with-dependencies` (fat/uber JAR) = GitHub-Release asset only, never Central, signed `.asc` — BAF + jllama + srcmorph (not sb).** *(Updated 2026-07-24, branch `claude/bitcoinaddressfinder-jar-upload-k0tkj7` — supersedes the earlier "per-run CI artifact only" state.)* The full convention + per-repo shapes live in the canonical [`policies/fat-jar-release-assets.md`](policies/fat-jar-release-assets.md). Summary: the uber jar is **never deployed to Maven Central** (redundant + large +, where it bundles a native binary, platform-specific) and is **attached to the GitHub Release with a detached GPG `.asc`** (authenticity parity with the thin jars). Per-repo **shape differs by design** (deliberate non-parity, not drift): **BAF** — one fat jar (LWJGL's per-platform `natives-*` classifiers all coexist on one classpath), built off-Central via `mvn -P release,assembly verify` (stops before `deploy`), signed by `maven-gpg`. **jllama** — multi-backend `all-<os>-<arch>` jars (default CPU + per-backend subdirs, `LlamaLoader`-selected) via `package-fatjars.sh`, signed by `.github/sign-fatjars.sh` in the attach jobs (`.sha256` **and** `.asc`). **srcmorph** (`srcmorph-cli`, the repo the workspace still labels `plugin`) — one fat jar **per `net.ladenthin:llama` classifier** (default CPU + 16 GPU classifiers), kept off Central via `<attach>false</attach>`, built + `gpg`-signed in a `publish.yml` loop. **sb** — ➖ still **none** (single-class `Closeable` library, no runnable entry point). **Gating caveat (all repos):** assets attach only on the `workflow_dispatch` + `publish_to_central=true` path; a plain `v*` tag push attaches nothing (symptom: a release with `assets: []`, as jllama v5.0.6 showed). Original CI-artifact wiring was branch `claude/cool-curie-ym3acr`.
- **Actual Gradle-based *publishing* (the `llama-android` AAR) — java-llama.cpp only.** The `verify-signing-key-gradle` **harness** is now in parity across all 4 (see "In parity" above — kept byte-identical as a "prepared for Gradle" canary, a deliberate uniformity choice). What stays jllama-only is a real **Gradle publish**: the `llama-android` AAR (`publishAllPublicationsToCentralSnapshotsRepository` / `…StagingRepository`, `llama-android/build.gradle.kts`) signs with Gradle's `useInMemoryPgpKeys` (BouncyCastle), where the AAR snapshot signing originally failed with a **null `PGPPrivateKey`**. **Root cause** (2026-07-09, jllama `main` run 29012094281, reproduced in isolation by the harness): Gradle's **2-arg** `useInMemoryPgpKeys` selects the **primary** key, whose secret this BouncyCastle can't unlock, while `gpg`/maven-gpg-plugin auto-select the key's **4096-bit signing subkey** `07D2D767`. **Fix:** the **3-arg** `useInMemoryPgpKeys(keyId, key, passphrase)` when `MAVEN_GPG_KEY_ID` is set, driven by the **`GPG_KEY_ID`** env secret (`= 07D2D767`) added to the `maven-central` environment in all 4 repos — **consumed only by jllama** (the three Maven siblings' gpg agent already picks the subkey, so their shared harness reads it too but their Maven publish never needs it). Confirmed green: `verify-signing-key-gradle` on jllama `main`, so the identical-code AAR publish signs correctly. The harness project (`.github/signing-selftest/`) was also refactored from an opaque base64 blob to committed, readable `.kts` files. PRs: jllama #306 (preflights) / #307 (subkey fix); cross-repo harness sync on branch `claude/android-signing-failure-q7zml9`. Same shape as the Depot/sccache and pocl/OpenCL entries (a real per-repo capability difference — jllama is the only repo with a Gradle-published artifact — not a parity gap to close).

---

## Recently closed (compact)

Rows that landed across every applicable repo. Kept here as a paper trail; not action items.

**Release process (centralized 2026-07-02)**

- The maintainer-facing Maven Central release procedure now lives once in
  [`workflows/release-process.md`](workflows/release-process.md); each sibling's `docs/RELEASE.md` is
  a thin pointer + a repo-specific supplement. This de-staled the previously-duplicated per-repo copies,
  which still said "commit directly to `main` (no PR)", omitted the `CHANGELOG.md` finalization step,
  and never mentioned the `publish_to_central=true` deploy gate (all four repos carry it — see the
  "Maven Central publish gating" note under Open cross-repo items). Repo supplements: **jllama** —
  reactor all-three-poms bump via `mvn versions:set` + the extra `llama-langchain4j/README.md` snippet;
  **BAF** — the legacy tag-prefix policy; **sb**/**plugin** — pointer only (pure single-module baseline).

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
  - **`spotbugs-exclude.xml` FQN repair after the layered-package restructure (2026-06-07)** — a latent gate-breaker: the restructure moved classes into sub-packages but the exclude files kept the flat pre-restructure `<Class name="…">` FQNs, so the `<Match>` suppressions silently stopped applying and `mvn verify` resurfaced documented-suppressed findings. Fixed in **BAF** (20 entries), **jllama** (11 entries + the `OSInfo` regex) and **plugin** (8 entries); each verified `spotbugs:check` BUILD SUCCESS. Same failure mode as the stale PIT `targetClasses` — a reminder to re-validate every FQN-bearing config (`spotbugs-exclude.xml`, PIT targets, ArchUnit) after any package move.
  - **More restructure-FQN fallout in jllama, surfaced only once each PR ran CI / the native lib actually loaded (2026-06-07)** — three further references still pointed at the pre-restructure flat package, each invisible to a plain local `mvn test` (model-gated native tests self-skip before the lib loads) and to the pure-Java unit tests:
    1. `CMakeLists.txt` invoked `net.ladenthin.llama.OSInfo` for OS/arch detection, but the class moved to `…loader.OSInfo` → local `cmake -B build` could not resolve `OS_NAME`/`OS_ARCH` (CI hid it by passing `-DOS_NAME`/`-DOS_ARCH` explicitly). Fixed both `--os`/`--arch` invocations (jllama `78cfef1`).
    2. `LlamaLoader.getNativeResourcePath()` derived the native-library classpath root from the loader's **own** package (now `…loader`), so it looked under `/net/ladenthin/llama/loader/<os>/<arch>/` while CMakeLists + the publish workflow emit to the fixed `/net/ladenthin/llama/<os>/<arch>/` → `UnsatisfiedLinkError: No native library found`, failing 21 native tests. Fixed by anchoring to a `NATIVE_RESOURCE_BASE` constant independent of the Java package (jllama `811d614`), + a `LlamaLoaderTest` regression pinning the exact path.
    3. `jllama.cpp` `JNI_OnLoad` still `FindClass`-ed flat paths for `LlamaException` (→ `exception.`) and `LogLevel` (→ `value.`, incl. the four `GetStaticFieldID` `"L…;"` signatures) → once the lib loaded, `JNI_OnLoad` threw `NoClassDefFoundError`. Fixed the FQN strings (jllama `e26e1ea`).
    Added a model-free `NativeLibraryLoadSmokeTest` (forces `LlamaModel.<clinit>` → `System.load` → `JNI_OnLoad`; self-skips when the lib isn't on the classpath) + a documented recipe in jllama `CLAUDE.md` so this whole class is catchable locally without HuggingFace models (jllama `ed5a82a`). **Generalised lesson:** after a package move, re-validate every FQN/path-bearing artifact, not just Java imports — `spotbugs-exclude.xml`, PIT `targetClasses`, ArchUnit, **CMake build scripts, runtime resource-path derivation, and JNI `FindClass`/signature strings**.

**Logging / observability**

- LogCaptor smoke test: BAF ✅ (LogCaptor 2.12.6, 7 tests) · jllama `3cedc6e` · plugin ➖ · sb ➖.

**Code-quality audits**

- `@VisibleForTesting` audit: BAF ✅ (10 sites legitimate) · jllama ➖ · plugin ➖ · sb ➖.
- Null-safety follow-up review: BAF ✅ (50 sites) · jllama ✅ (43 sites) · plugin ✅ (17 sites) · sb ✅ (zero `@Nullable` in production).
- Class / method naming review (21-item cross-repo audit) — see closed totals at the bottom.
- `Enum.ordinal()` de-dependence (Error Prone `EnumOrdinal`, 2026-06-07): replaced fragile ordinal-index assertions with declaration-order checks over `values()` (`assertArrayEquals` / Hamcrest `arrayContaining`). jllama `value.LogLevelTest` + `parameters.ModelParametersExtendedTest` (`d45e352`, the latter now asserts the `MiroStat.getArgValue()` contract instead of `ordinal()`); BAF `producer.ProducerStateTest` + `model.AddressTypeTest` (`a92d7a9`). AddressType's ordinal was investigated and confirmed **not** load-bearing — referenced by name only across `src/main` and the OpenCL `.cl`/`.h` kernels — so its explicit ordinal tests were dropped rather than suppressed (`cb6ab10`). plugin ➖ · sb ➖ (no ordinal-dependent tests).

**Cross-repo refactors**

- Workspace-shared guidelines layer: all 4 ✅.
- Standardised `CLAUDE.md` template: all 4 ✅.
- Versioned workspace guide chain (`guides/src/-8.md` + `-21.md`, `guides/test/-8.md` + `-21.md`): all 4 ✅.
- Audit-driven SKILL.md rewrite: all 4 ✅.
- Safe dependency / plugin bumps (latest round): BAF `59f7ff1` · jllama `0a97ae7` · plugin `93c7c84` · sb `3ccb426`.
- GitHub Actions `codecov/codecov-action` v6→v7 (2026-06-07, Dependabot-proposed; applied on the shared branch so it rode each repo's open PR instead of a separate merge to `main`): BAF `5d8cace` · jllama `b4443b1` · plugin `e30735d` · sb `71671d0`. workspace ➖ (no workflow).
- Per-repo `TODO.md` extraction (open work moved out of `CLAUDE.md`): all 4 ✅.
- Lombok 1.18.46 `@ToString` / `@EqualsAndHashCode` adoption (clears IMC_NO_TOSTRING + IMC_NO_EQUALS at SpotBugs Max+Low): BAF ✅ (56 classes, 0 handwritten Object methods left) · jllama `9be73a3` (23 classes) · plugin `39e1a59` + `6955357` (6 records + 19 annotated) · sb ➖ (excluded by design).
- Canonical `lombok.config` content incl. `doNotUseGetters = true` (see [`policies/lombok-config.md`](policies/lombok-config.md)): BAF `61e7996` · jllama `6ddd225` · plugin `3c61b88` · sb ➖.

**Concurrency / interleaving analysis**

- **vmlens interleaving CI step parity (2026-06-14, branch `claude/focused-cray-mgzh1e`).**
  Previously only **sb** ran a dedicated `Test (vmlens interleavings)` job in `publish.yml`
  (`mvn -Pvmlens test` over the whole suite). The other three repos already carried the
  *plumbing* — `vmlens.version` (1.2.28), the managed `vmlens-maven-plugin`, a `vmlens`
  profile, and `com.vmlens:api` — but **never invoked it from CI** (they only ran
  `-P jcstress`), so vmlens interleaving analysis ran nowhere for BAF/jllama/plugin. Added
  the missing CI job to all three plus a minimal one-class example so the step actually runs
  green:
  - **New test** `…​.vmlens.VmlensInterleavingSmokeTest` (one per repo): two threads increment
    a shared `AtomicLong` inside an `AllInterleavings` loop, asserting the sum is always 2.
    Deterministic, agent-driven; the canonical vmlens "first test" shape.
  - **pom**: moved `com.vmlens:api` from the profile into the main `<dependencies>` (test
    scope; transitive-dep-free so `dependencyConvergence`-safe) so the smoke test compiles in
    every build; added a managed `maven-surefire-plugin` `<exclude>` for it (without the agent
    `AllInterleavings.hasNext()` is a vacuous pass that prints an "agent not configured"
    warning, so it stays out of the ordinary suite); narrowed the `vmlens` profile from a
    whole-suite `<excludes>` run to an `<includes>` of just the smoke test.
  - **CI**: a lightweight `vmlens` job (`needs: build`/`startgate`, ubuntu, no native
    lib/model/LMDB/OpenCL) runs `mvn -Pvmlens test -Dtest=VmlensInterleavingSmokeTest
    -DfailIfNoTests=false` and uploads `target/vmlens-report/`.
  - **Status**: BAF ✅ · jllama ✅ · plugin ✅ · sb ✅ (pre-existing, whole-suite). All four
    verified locally (`BUILD SUCCESS`, agent started, report written).
  - **Staged scope (📌 ongoing, mirrors the PIT staging model):** the three new jobs gate a
    single class for now; widen each `vmlens` profile's `<includes>` as real concurrency tests
    are added, the end state being sb's whole-suite run.

- **Smoke-test parity across all 4 repos (2026-06-14).** Added the same
  `…​.vmlens.VmlensInterleavingSmokeTest` to **sb** too (it previously had the whole-suite
  vmlens run but no dedicated smoke test), so the identical deterministic baseline now exists
  in BAF · jllama · plugin · sb. In sb it lives on the main test classpath (`com.vmlens:api`
  promoted out of the profile) and is surefire-excluded from the ordinary run like the others;
  sb's `vmlens` profile still runs the whole suite, so the smoke test is picked up there.
  Verified green under the agent. Rationale: a known-good, cross-repo-identical first test is a
  useful "is vmlens wired up?" canary independent of each repo's real concurrency surface.

- **vmlens expansion candidates — real targets per repo (investigated 2026-06-14, ✅ implemented
  2026-06-15 for sb/BAF/jllama).** Deep per-repo audit of the actual concurrency surface; one
  strong candidate each for three repos was graduated past the smoke test (each repo's `vmlens`
  profile/job now runs an `**/vmlens/*.java` package glob). The plugin honestly has none.
  - **sb — `StreamBuffer` reader-vs-writer accounting.** Exercise `SBInputStream.read(byte[],
    int,int)` (the blocking path through `waitForAtLeast`, which reads `availableBytes`/
    `streamClosed` *outside* `bufferLock`) concurrently with `SBOutputStream.write(...)`;
    assert the invariant `totalBytesWritten == totalBytesRead + availableBytes`. This
    interleaving class is **untested** today: Lincheck deliberately excludes `read` (can't
    progress past a parked reader) and the jcstress close/unblock races assert only
    *termination*, not the accounting/value. Tests the class directly (no helper).
    ✅ Implemented: `vmlens.StreamBufferReaderWriterInterleavingTest` (sb `abff69e`).
  - **BAF — `keyproducer/AbstractKeyProducerQueueBuffered`.** The only hand-rolled coordination
    in the repo: `createSecrets` (consumer parked on `secretQueue.take()`) vs `addSecret`
    (transport-reader thread) vs `signalShutdown` (sets `volatile shouldStop`, then offers a
    reference-identity `SHUTDOWN_SENTINEL`). Two interleaving-sensitive invariants worth vmlens:
    lost-wakeup/liveness (a parked consumer is **always** released by `signalShutdown` →
    `NoMoreSecretsAvailableException`) and drop-after-stop (a real key enqueued after the
    sentinel is never decoded as a key). Constructor already accepts an injected
    `BlockingQueue` for tests; no helper extraction needed. ✅ Implemented:
    `vmlens.KeyProducerQueueBufferedInterleavingTest` with both invariants — lost-wakeup/
    liveness (BAF `556c4ae`) and drop-after-stop (the sentinel is never decoded as a key;
    BAF `1b7e572`, a regression guard — the protocol is correct by construction). (Backups:
    `ConsumerJava` bounded-queue path; `AbstractProducer` `state`/`shouldRun`/`notRunningLatch`
    lifecycle.)
  - **jllama — `Session` stream-guard + transcript state machine** (`streamingActive` boolean +
    `ChatTranscript` two-phase commit). A *compound-atomicity* target (flag + list must move
    together; check-then-act), a different and untested class vs the single-`volatile`-boolean
    `CancellationToken` Lincheck/jcstress coverage. Because `Session.send/stream` call the native
    model (can't run model-free), this was the **"refactor a method into a short helper"** case.
    ✅ Implemented (jllama `5273f7e`): extracted a model-free public `SessionState` (root package,
    mirroring the testability extraction of `ChatTranscript`) owning `streamingActive` + the
    transcript transitions (`send`/`beginStream`/`commitStreamedReply`/`runWhenNotStreaming`/
    `runUnderLock`/`snapshot`); the native call is injected as a callback run under the lock, so
    `Session` keeps identical serialization/exception semantics (behaviour-preserving). Added
    `vmlens.SessionStateInterleavingTest` (send vs stream+commit → strict alternation, non-stuck
    guard) plus a model-free `SessionStateTest` (7 tests) pinning the contract in the ordinary
    suite (the model-gated `SessionConcurrencyTest` can't run without a GGUF). Verified compile
    (Error Prone/NullAway/Checker), javadoc, `spotbugs:check` 0 bugs. (Backup:
    `loader.LlamaLoader.initialize()` one-time lazy native-lib load.) Treat `CancellationToken`
    as **done** (already double-covered).
  - **plugin — none (by design).** Repo-wide search found **zero** `synchronized`/`volatile`/
    `Atomic*`/`Concurrent*`/`parallel()`/`ExecutorService`/`Thread` in `src/main/java`; the
    mojo + indexers are strictly sequential (`Files.walk`/`Files.list`, no `.parallel()`). The
    one lazy field (`LlamaCppJniAiGenerationProvider.model()`, an unsynchronized check-then-act)
    is never reached concurrently, and a faithful test would load a ~90 MB GGUF per
    interleaving — contrived. The smoke test is the right level; revisit only if indexing is
    ever parallelized.

---

## Open cross-repo items

| TODO item | BAF | jllama | plugin | sb |
|---|:--:|:--:|:--:|:--:|
| ArchUnit full `layeredArchitecture()` | ✅ — flat root package split into 10 layered packages; strict `layeredArchitecture()` rule enforced (Entry→Orchestration→Pipeline→Capabilities→InputOutput→Foundation→Config→Constants) | ✅ — flat root package split into layered packages (value/callback/exception/parameters/loader/json/args); strict `layeredArchitecture()` rule enforced (Api→Loader→Marshalling→Foundation) | ✅ — flat package split into 7 layered packages (mojo/indexer/provider/document/prompt/config/support); strict `layeredArchitecture()` rule enforced (Mojo→Indexer→Provider→Format→Foundation) | ➖ single-package |
| ArchUnit per-module banned-imports | ✅ — JOCL→opencl, ZeroMQ/WebSocket→keyproducer, LMDB→persistence+io | ✅ — Jackson banned from args/callback/exception/loader | ✅ — JNI→provider, Maven @Mojo/@Parameter→mojo, config+support Maven-free | ➖ single-package |
| Package hierarchy review | ✅ — layered package split landed (see BAF `TODO.md` "Done") | ✅ — layered package split landed (see jllama `TODO.md` "Done") | ✅ — layered package split landed (see plugin `TODO.md` "Done") | ➖ single-package |
| Typed-exception unification audit (constructor signatures + Javadoc shape consistent across every custom exception class) | ✅ — all 8 exceptions aligned: `AddressFormatNotAccepted` (precedent) + `InterruptedRuntimeException`; keyed exceptions (`KeyProducerIdIsNotUnique`/`Unknown`, `UnknownSecretFormat`, `PrivateKeyTooLarge`) gained the `(key…, cause)` matrix overload + tests; `KeyProducerIdNull` kept no-arg fixed-condition (bare `(Throwable)` would break the checklist's own rule); `NoMoreSecretsAvailable` already compliant; identity equality everywhere | ✅ — `LlamaException` / `ModelUnavailableException` already shape-compliant; added the missing `ModelUnavailableExceptionTest` | ➖ no custom exceptions (uses Maven `Mojo*Exception`) | ➖ no custom exceptions (uses `IOException`) |
| Test-JVM diagnostics + memory standard ([`policies/ci-test-diagnostics.md`](policies/ci-test-diagnostics.md)): `-Xmx2g`/no eager `-Xms`, `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=. -XX:ErrorFile=hs_err_pid%p.log`, `-XX:+EnableDynamicAgentLoading` (JDK 21 byte-buddy self-attach warning → flaky "Corrupted channel"/bogus fork-timeout; see § 2.1), CI `free -h` before/after + `mvn -e` + on-failure crash-dump upload (`hs_err`/`*.hprof`/surefire `*.dump`/`*.dumpstream`/`*.txt`/`TEST-*.xml`). Divergences kept by design: `reuseForks`/`forkCount`/`forkedProcessTimeoutInSeconds` (BAF), `--add-opens` set (BAF), pocl job (BAF), core dumps (jllama). | 🚧 argLine `-XX` flags appended; `test` matrix memory steps (Linux-guarded) + `*.hprof` in uploads; pocl `*.hprof`; `EnableDynamicAgentLoading` present (Mockito inline trigger) | 🚧 `-Xmx2g` added (already had `-XX` + memory steps + crash upload); `mvn -e` added; `+EnableDynamicAgentLoading` added (Lincheck trigger; branch `claude/jacoco-argline-sync-bfam2k`) | 🚧 surefire `<argLine>@{argLine} …>` + memory steps + crash upload; `+EnableDynamicAgentLoading` added across all 3 reactor module poms (Lincheck trigger; branch `claude/jacoco-argline-sync-bfam2k`) | 🚧 new surefire `<argLine>@{argLine} …>` + memory steps + crash upload; `+EnableDynamicAgentLoading` added (Lincheck trigger; branch `claude/jacoco-argline-sync-bfam2k`) |

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

> **Refresh 2026-06-25.** `pitest-maven` is now **1.25.5** (junit5-plugin 1.2.3). Live re-runs
> (CI-form `mvn test-compile org.pitest:pitest-maven:mutationCoverage`): **sb** 179/179 ✓ ·
> **BAF** 65/65 ✓ · **plugin** 146/146 ✓ · **jllama** 243 mutations — **100% only with the audio
> fixture**, else 239/243 (98%) from 4 `NO_COVERAGE` in `value.ContentPart.audioFile(Path)` (see
> "Deliberate non-parity" and [`policies/pit-mutation-testing.md`](policies/pit-mutation-testing.md)).
> The 2026-06-07 table below is the historical baseline; counts drift with code, the **100% gate**
> is the contract.

| Repo | Classes gated | Mutations | What's gated |
|---|:--:|:--:|---|
| sb | whole package | — | entire `net.ladenthin.streambuffer` (pre-existing) |
| jllama | 30 | 207 | `value.*` (16) + `exception.*` (2, 0 mutations) + `args.*` enums (10) + `json.TimingsLogger` + `json.RerankResponseParser` + `json.ChatResponseParser` + `json.CompletionResponseParser` |
| plugin | 21 | 146 | config/document/prompt/provider/support value + support classes |
| BAF | 16 | 63 | `util.BitHelper` + model (incl. refactored `Hash160`) + 8 exception classes + `statistics.*` + `CKeyProducerJavaIncremental` |

New tests added to reach 100% (no production code changed): jllama
`ChatChoiceTest`/`ToolCallTest`/`ToolDefinitionTest`/`ContinuationModeTest` + expanded
`ChatMessageTest`/`ServerMetricsTest`/`ModelMetaTest`/`TokenLogprobTest`/`ChatResponseTest`/`CompletionResultTest`;
jllama `json.ChatResponseParser`/`CompletionResponseParser` (the two near-100% parsers) reached
100% on 2026-06-07 via expanded `ChatResponseParserTest`/`CompletionResponseParserTest` (typed
`parseResponse`/`parseCompletionResult`/`parseLogprobs` paths incl. tool-calls and LogCaptor
timing-line tests) **plus** behaviour-preserving single-mutable-list refactors of the private
`parseChoices`/`parseToolCalls`/`parseLogprobs`/`parseLogprobEntry` helpers that removed the
equivalent empty-branch (`emptyList()` vs `ArrayList`) and `size()>0`/`size()==0` mutants — same
"refactor to kill the equivalent mutant" pattern as Hash160/AiPathSupport;
plugin `Java8CompatibilityHelperTest`/`MockAiGenerationProviderTest`/`AiPromptSupportTest`/`AiPathSupportTest`/`AiChecksumSupportTest`/`AiMdChildEntryLineFormatterTest`/`AiPreparedPromptTest`/`AiGenerationConfigTest`/`AiModelDefinitionTest`
+ expanded `AiModelDefinitionSupportTest`/`AiMdHeaderSupportTest`; BAF needed no new tests
(existing tests already gave 100%).

**Still open (optional, each needs more involved fixtures):** plugin `document.AiMdDocumentCodec`
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

### Dependency / plugin freshness (verified 2026-06-07, re-verified 2026-07-08, re-verified 2026-07-29)

All four repos are on the **newest stable** versions of every dependency and build plugin
(checked with `versions:display-dependency-updates` + `display-plugin-updates` against
Maven Central, and direct `maven-metadata.xml` probes for the annotation-processor paths the
versions plugin does not scan: Error Prone, NullAway, Checker). The only "updates" offered are
**pre-releases** — Maven 4 plugin `4.0.0-beta-*` (compiler/jar/source/resources/plugin),
`maven-surefire-plugin:3.6.0-M1`, `slf4j-api:2.1.0-alpha1`, `protobuf-javalite:4.36.0-RC1`,
`kotlin:2.4.20-Beta2`, Maven-core `4.0.0-rc-5` — which are deliberately **not** adopted, plus
**jqwik 1.10.1** which is 📌 **banned** (see policy). No action needed.

**2026-07-29 audit (branch `claude/dependency-updates-audit-vv4mz5`):** full sweep of all
sibling repos **plus** BroomCabinet (15 Maven modules) and the GitHub Actions / Gradle-Android
surface. Result: everything is on latest stable; nothing bumped. Two doc-sync fixes only —
the tool-version matrix above had drifted (spotbugs `4.10.2.0→4.10.3.0`, spotless
`3.8.0→3.9.0`, palantir `2.94.0→2.96.0`, nullaway `0.13.7→0.13.8`, junit-jupiter `6.1.1→6.1.2`,
pitest-maven `1.25.6→1.25.8` — the repos were already ahead of the doc) and the two policy
files that re-pinned those numbers now point at the matrix instead. **GitHub Actions:** every
`uses:` pin across all repos is at its latest release (floating `@vN` majors + version-pinned
ones alike — checkout v7, setup-java v5, upload-artifact v7, download-artifact v8, cache v6,
codeql v4, codecov v7, scorecard 2.4.4, osv-scanner 2.3.8, Jimver/cuda-toolkit 0.2.35,
jakoch/install-vulkan-sdk 1.6.0, reuse v6, gradle/actions v6, android-emulator-runner v2,
action-gh-release v3). **Gradle/Android (jllama):** Gradle 9.6.1 (latest stable; 9.7 is
pre-release), AGP 9.3.0, Compose BOM 2026.06.01, kotlinx-coroutines 1.11.0, kotlin 2.4.10 — all
current/deliberately pinned.

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
| `org.bouncycastle:bcprov-jdk15to18` | 1.85.1 | BAF | (transitive) | Pins the bitcoinj-transitive bcprov to patch GHSA-c3fc-8qff-9hwx / GHSA-p93r-85wp-75v3. Rationale in BAF `CLAUDE.md` deps table. |
| `com.google.protobuf:protobuf-javalite` | 4.35.1 | BAF | 4.36.0-RC1 | Latest **stable**; newer is RC only. |
| `org.slf4j:slf4j-api` | 2.0.18 | all | 2.1.0-alpha1 | Latest **stable**; newer is alpha only. |
| `org.jetbrains.kotlin` | 2.4.10 | jllama (`llama-kotlin`) | 2.4.20-Beta2 | Latest **stable**; newer is beta only. |
| Maven-4 plugin line / surefire `3.6.0-M1` | — | all | `4.0.0-beta-*` / `-M1` | Maven-3 toolchain; Maven-4 betas + milestones deliberately not adopted. |

**2026-07-08 bump round (branch `claude/build-timeout-config-nzli8l`):** pitest-maven
1.25.5→1.25.6 (all 4; every 100% gate re-run green on the new version — sb 179/179
whole-package, BAF 65/65, jllama 295/295, plugin 565/565 — and the pin updated in
[`policies/pit-mutation-testing.md`](policies/pit-mutation-testing.md)); jackson 2.22.0→2.22.1
(BAF + jllama); jllama-only: kotlin 2.2.21→**2.4.0** for the `llama-kotlin` module (bytecode
re-verified class-file major **52** / Java 8; consumer floor moves Kotlin 2.1+→2.3+ per the
metadata one-minor-back rule — README updated), langchain4j-core 1.17.1→1.17.2,
maven-jar-plugin 3.4.1→3.5.0 in `llama-kotlin` (drift fix — the other three repos and the
jllama core were already on 3.5.0). Kotlin 2.4.0 was found by direct
metadata probe — the versions plugin only offered `2.4.20-Beta1` and hid the stable 2.4.0.
Commits — **BAF** `f1a81af` · **sb** `d0c5f47` · **plugin** `ed16a76` · **jllama** `4db9edf`.

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

**CI SpotBugs early gate (done, all 4 repos, 2026-06-26):** same root cause as the code-style
gate above — `spotbugs:check` is bound to `verify`, which only the publish `deploy` goal reaches,
so in **jllama** and **BAF** SpotBugs ran **only at publish** (a `PATH_TRAVERSAL_IN` finding red a
jllama release *after* it had already built every jar — sources/javadoc/cuda/opencl/ninja). Fix:
extended the existing fast `code-style` job in all 4 repos to also run
`mvn -DskipTests -Denforcer.skip=true compile spotbugs:check` (after Spotless, before the
informational jdeps step). `publish-snapshot`/`publish-release` already `needs: code-style`, so
SpotBugs now gates publish **and** every PR/push with no `needs:` change. **sb** and **plugin**
already ran SpotBugs early via their `test` job's `mvn verify` (kept — it also gates javadoc in PR
CI); for them the new step is faster feedback + parity. jllama's `PATH_TRAVERSAL_IN` suppression was extended to
`OfflineModelGuard`/`ModelParameters` and then **reviewed (2026-06-26) and consolidated** with the
existing `LlamaLoader` block into one finalized `<Match>`: every flagged site reaches `Paths.get`
from the operator's own process configuration (the `--model` path, the `lib.path` property,
`java.library.path`), not untrusted input crossing a privilege boundary, and there is no allowed-root
to validate against (pointing at an arbitrary GGUF/lib dir is the whole point) — a settled false
positive for a JNI library, with no appropriate code fix. The jllama deep-check is therefore
**closed**; the consolidated block carries the full rationale. The early gate **also surfaced a pre-existing, already-merged** `CE_CLASS_ENVY` in
**plugin**: `PackageIndexer.appendPackageHeaderLines` hand-rendered a `.ai.md` header that
`AiMdHeaderCodec.write()` already produces byte-for-byte. **Resolved** by delegating to the codec
(no suppression — output byte-identical, `PackageIndexerTest` green), removing the duplicated
eight-field block. (That finding had slipped through the plugin's
own `verify`-bound gate — exactly the late-failure class this early gate is meant to catch.)
Where/when SpotBugs runs is now noted in
[`policies/spotbugs-suppressions.md`](policies/spotbugs-suppressions.md).

**Javadoc JPMS module-mode failure on BAF publish-snapshot (root-caused + fixed, 2026-06-07).**
Same *family* as the code-style gate above — a failure that **only the publish/deploy job
runs** (every other job passes `-Dmaven.javadoc.skip=true`; the deploy job runs `-P release
deploy`), so it slipped through PR CI and failed only after merge to `main`. Symptom:
`maven-javadoc-plugin:3.12.0:jar (attach-javadocs)` → `error: No source files for package
net.ladenthin.bitcoinaddressfinder.<X>` (exit 2), the package name **non-deterministic**
(`constants` on CI, `model`/others locally).

Root cause: BAF's javadoc switches into **JPMS module mode** because (a) javadoc is configured
`<source>21</source>` (module-aware) and (b) `target/classes/module-info.class` is present when
javadoc runs (the `module-info-compile` execution is bound to `prepare-package`, the
`attach-javadocs` execution defaulted to `package`, so the descriptor existed first). In module
mode the plugin stages a `--module-source-path`, but BAF's `module-info.java` lives in
`src/main/java9` (off javadoc's source path) and the module declares **no `requires`** — so
module-mode javadoc both mis-stages the package tree ("No source files…") *and*, if you naively
co-locate `module-info.java` to fix the staging, then can't see classpath deps (bitcoinj,
jspecify, slf4j → "package does not exist"). Module mode is therefore fundamentally unusable
here; **classpath mode is the only viable mode.** The layered-package refactor (19 packages /
14 `package-info.java`) is what made the latent bug bite — pre-refactor (one package) module-mode
javadoc had nothing to trip over.

**Cross-repo relevance — structural trap shared by all 4, only BAF trips it.** All four repos
are JPMS modules that compile `module-info.class` into `target/classes` via a dedicated
release-9 execution. The *only* reason the other three are immune is their javadoc `<source>`
is **8** (`jllama` `1.8`, `sb`/`plugin` resolve to `8`) → javadoc stays in **classpath mode**
regardless of the descriptor (proven: jllama builds javadoc green with `module-info.class`
present and >1 `package-info.java`). Two further BAF-only aggravators: javadoc must be `source
21` (to parse records/sealed/text-blocks — can't drop to 8), and BAF hides `module-info.java`
in `src/main/java9` (the other three keep it in `src/main/java`, co-located with the sources —
not a Java-8 leftover but a deliberate isolation so BAF's main compile stays in unnamed-module
mode for Error Prone/NullAway/Checker + the `--add-exports`/`--add-opens` internal-JDK test
access). **Latent risk:** the moment any Java-8 repo bumps its target to ≥9 and raises javadoc
`<source>` accordingly, it can hit the same class of failure — most likely `jllama`/`plugin`
(8 `package-info.java` each). If/when that happens, force classpath mode the same way.

**Fix (BAF, branch `claude/amazing-noether-p7THl`):** keep the descriptor out of
`target/classes` while javadoc runs, by binding `attach-javadocs` to **`prepare-package`** (after
`test`, before the descriptor is compiled) and ordering it **before** `module-info-compile` —
which is achieved by declaring the `maven-javadoc-plugin` block **before** the
`maven-compiler-plugin` block (Maven runs same-phase executions in plugin-declaration order).
`module-info-compile` stays at `prepare-package` so the jar still gets `module-info.class`
(binding it to `package` is unreliable — the lifecycle's `default-jar` runs before an explicit
`package` execution, dropping the descriptor from the jar). Verified: `-P release clean package`
→ BUILD SUCCESS, javadoc in classpath mode, `module-info.class` present at the jar root, and
`mvn test` still never triggers javadoc (both executions are after `test`). **Detection-gap
lesson (recurring):** publish-only steps (javadoc here, `spotless:check` previously) escape PR
CI — a future hardening is to run `mvn -P release ... package` (or at least the javadoc jar) in
a fast PR-CI job so this whole family fails *before* merge, not on the snapshot publish.

**CI `-Dmaven.javadoc.skip=true` cleanup (all 4 repos, 2026-06-14).** The four `publish.yml`
pipelines had accumulated **9** scattered `-Dmaven.javadoc.skip=true` flags. Audit found most
were either **dead no-ops** (on `test-compile` / `test` / `exec:java` commands that never reach
the `package` phase that `javadoc:jar` binds to) or **cargo-culted** copies of the genuine BAF
fix into repos that don't need it. Root cause of the idiom: `attach-javadocs` lives in the
**main `<build>`** of every pom (not the release profile), so any `mvn package`/`verify` builds
javadoc — and BAF's module-aware javadoc (`<source>21</source>` + `module-info.java` in
`src/main/java9`) can trip JPMS module mode there. The three Java-8 siblings are immune
(`<source>8>` → classpath mode regardless); their javadoc was verified to build clean.
Resolution: deleted **8** of the 9 flags. **Exactly one survived at the time — BAF `publish.yml`
`build` job** — because that job runs plain `mvn package` and would trip the module trap; it is
now annotated inline and in BAF's CLAUDE.md as the single intentional "skip for a reason," to be
removed only after a full `mvn package` proves BAF's javadoc clean (a standalone `mvn
javadoc:jar` cannot — always classpath mode, hides the trap). streambuffer and llamacpp-ai-index
now let javadoc build during their `verify` test job, so javadoc is gated in **PR CI** there
(the "future hardening" above); BAF and java-llama.cpp still validate javadoc only at publish.
Worked out on branch `claude/sweet-lamport-ugvqea`. **No longer "exactly one" — see the
2026-08-02 entry below, which adds two more BAF-only flags for a second, distinct trigger of the
same trap.**

**Javadoc JPMS module-mode failure, second trigger — BAF publish-snapshot fat-jar step
(root-caused + fixed, 2026-08-02).** A recurrence of the June 7 trap above via a *different*
mechanism, surfaced when CI run 30768800950 (`workflow_dispatch`, `main`) reached
`publish-snapshot` for what turned out to be the first time since the fat-jar-attach feature
was added: `Deploy snapshot` (`mvn -P release deploy`) succeeded, but the following step "Build
& sign fat jar" (`mvn -P release,assembly verify`, added by commit `6b0d37a`, 2026-07-24, in the
same job with **no `mvn clean` between the two invocations**) failed at `attach-javadocs`:
`error: No source files for package net.ladenthin.bitcoinaddressfinder.io` (exit 2) — same
error shape as June 7, but the June fix (javadoc's execution ordered before
`module-info-compile` *within one invocation*) does not protect against a *second* invocation
inheriting `target/classes/module-info.class` left behind by the *first* invocation's own
`module-info-compile`. Confirmed by local reproduction against BAF's actual `pom.xml`
(two-invocation sequence, no `clean`) and by CI run history: `publish-release` has never
executed with this step at all (no `v*` tag dispatched since `6b0d37a`), and `publish-snapshot`
had one prior opportunity that was manually cancelled — so the step had never completed
successfully before this incident, and the next tagged release would have hit it deterministically.
Also checked all three sibling repos: java-llama.cpp and streambuffer are structurally immune
(no equivalent second-invocation shape / classpath-mode javadoc regardless); srcmorph has the
same double-invocation shape in its per-classifier fat-jar loop but already carries
`-Dmaven.javadoc.skip=true` there (independently immune too, since its javadoc `<source>`
resolves to 8, but a useful precedent). **Fix (BAF, `.github/workflows/publish.yml`):** added
`-Dmaven.javadoc.skip=true` to the "Build & sign fat jar" step in both `publish-snapshot` and
`publish-release` — verified locally that the fat jar still builds/attaches correctly and the
already-signed javadoc jar from the `deploy` step survives untouched (byte-identical, correctly
signed, picked up by the same `Collect` step). Full write-up of the mechanism (with the exact
`@options`/`@packages` evidence javadoc staged) now lives in
[`policies/jpms-module-descriptor.md`](policies/jpms-module-descriptor.md) "A second trigger:
multiple Maven invocations sharing `target/`" — read that before adding a second Maven
invocation to any publish job in any of these repos.

**Maven Central publish gating — `publish_to_central` manual flag + `-SNAPSHOT` guard (all 4
repos, 2026-06-18, branch `claude/stoic-franklin-67klln`).** Same *publish-only-step-escapes-
PR-CI* family as the code-style gate and the javadoc trap above — surfaced when a release merge
to `main` kicked the "Publish Snapshot to Central" job and it started deploying a **release** to
Maven Central. Root cause: the `release` profile's `central-publishing-maven-plugin`
(`<extensions>true</extensions>` + `<autoPublish>true</autoPublish>` + `<waitUntil>published`
`</waitUntil>`) routes **purely by the POM `<version>`**, never by job name — and `publish-snapshot`
and `publish-release` run the *identical* `mvn -P release deploy`. So with `main` carrying a
release version (the `-SNAPSHOT` stripped at release time, e.g. BAF `1.6.0`/`1.6.1`), the
"snapshot" job staged + uploaded a **release** bundle and auto-published it; when the matching
`v*` tag fired `publish-release` concurrently, both deployments collided on the same coordinate
and **both runs failed** (BAF run `27765693018` publish-snapshot log: `Uploaded bundle …
deploymentId 8f9f27ba … Deployment will publish automatically` → `Component with coordinate
'net.ladenthin:bitcoinaddressfinder:1.6.0' is currently being published in another deployment`).
Two-layer fix applied identically to all four `publish.yml`:
- **Manual gate.** Generalised the release-only `publish_release` `workflow_dispatch` input into a
  single `publish_to_central` boolean and required it on **both** `publish-snapshot` and
  `publish-release` (`&& inputs.publish_to_central`, only truthy on `workflow_dispatch`). Nothing
  publishes to Central from any automatic `push`/tag anymore — only a deliberate "Run workflow"
  with the flag ticked. Snapshot = dispatch on `main` (a `-SNAPSHOT` version); release = dispatch
  on a `vX.Y.Z` tag.
- **Version guard.** A step before the snapshot deploy resolves `project.version` via
  `mvn help:evaluate` and **aborts unless it ends in `-SNAPSHOT`**, so a release-versioned `main`
  can never misroute through the snapshot path even when dispatched.

Behavioural change (now uniform): the three library repos previously auto-published a snapshot on
every push to `main`; publishing is now manual-only in all four. Commits — **BAF** flag `501a245`
+ guard `e6a57ba`; **sb** guard `12cb25b` + flag `a44fe1f`; **plugin** guard `bf57e4c` + flag
`a729f54`; **jllama** guard `53204f2` + flag `02c02d0`. Detection-gap lesson (recurring): the
misroute was invisible to PR CI because publish jobs run only on `main`/tag/dispatch — same
hardening direction as the javadoc/code-style traps (exercise the publish path earlier).

**Central publish polling timeout raised to 6 h + effective-POM debug step (all 4 repos,
2026-07-07, branch `claude/build-timeout-config-nzli8l`).** The jllama **5.0.6 release deploy
failed** with `Polling for <deploymentId> timed out before the deployment completed`: the
`central-publishing-maven-plugin` (0.11.0, latest) polls the Central Portal for the `PUBLISHED`
state (`<waitUntil>published</waitUntil>`) with a default **`waitMaxTime` of 1800 s (30 min)** —
verified from the plugin jar's `plugin.xml` (`waitMaxTime` default 1800, `waitPollingInterval`
default 5 s). On a slow portal day the bundle **uploads fine and publishes server-side anyway**
(`autoPublish=true` → "Deployment will publish automatically"); only the confirmation poll gives
up, redding the job after the release is effectively out. All four repos carry the identical
release-profile config, so the fix landed everywhere:
- **pom.xml** — added `<waitMaxTime>21600</waitMaxTime>` (6 h) next to `waitUntil` in the release
  profile's central-publishing configuration. The fail-loud `published` gate is kept; only the
  patience grew. Note: 6 h coincides with GitHub's default job limit, so a genuinely stuck
  deployment ends at the job ceiling — intended ("wait as long as the job can").
- **publish.yml** — an informational `Show effective POM (debug)` step (`help:effective-pom`
  with the same profile set as the adjacent deploy) inserted before the deploy step in both the
  `publish-snapshot` and `publish-release` jobs, so the resolved publishing configuration is
  visible in the job log. Nothing depends on it.
Operational note: after such a timeout, **check Central before re-running** — the artifact most
likely published despite the red job, and re-deploying an already-published release version
fails. Commits — **jllama** `5710d5e` · **BAF** `26e6b0e` · **sb** `415a6bd` · **plugin** `f180fa6`.

**Follow-up (same day, same branch): GitHub release assets no longer lost when the Central
publish job reds.** The jllama 5.0.6 timeout also exposed a second gap: the assets *did* publish
to Central but **never reached the GitHub release page**, because two layers both required
publish success — (1) `github-snapshot`/`github-release(-signed)` were gated
`if: needs.publish-*.result == 'success'`, and (2) inside the publish job the
`Collect signed artifacts` + `upload-artifact` steps run *after* the `mvn deploy` step, so a
deploy failure (even at the final poll, when all jars + `.asc` signatures already exist —
GPG signing happens at `verify`, long before the Central wait) skipped collection entirely.
Fixed identically in all four `publish.yml`: the collect + upload steps got
`if: ${{ !cancelled() }}`, and the GitHub jobs now run on publish **success OR failure** (never
on skipped/cancelled, so the `publish_to_central` manual gate still holds; jllama additionally
keeps its `package-fatjars.result == 'success'` condition). Fail-loud edge preserved: if the
deploy fails *before* signing, the collect step finds nothing, no artifact is uploaded
(`if-no-files-found: warn` default), and the GitHub job reds on its `download-artifact` —
nothing half-signed ever reaches the release page silently. Forward-looking only: for an
already-red run, attach the assets manually or re-run the workflow (the duplicate Central
deploy fails, but the GitHub job now still attaches the freshly built signed assets).
Commits — **jllama** `ad316cb` · **BAF** `4a8b9ac` · **sb** `ce2c08f` · **plugin** `84531d2`.

**Follow-up 2 (same day, same branch): `waitUntil` relaxed `published` → `validated` (all 4
repos).** The plugin supports `uploaded` / `validated` / `published` (enum `WaitUntilRequest`;
the plugin's own default is `VALIDATED`) — the strict `published` wait was an opt-in. Portal
**validation** is where every real error surfaces (bad signature, missing javadoc, POM rules,
coordinate conflicts) and completes in seconds–minutes; the subsequent publish/replication step
runs server-side via `autoPublish=true` and, after a passed validation, effectively only
"fails" through portal slowness — exactly the 5.0.6 false-alarm class. `validated` therefore
keeps the fail-loud gate for genuine errors while eliminating the multi-hour wait; the
`waitMaxTime=21600` stays as harmless headroom for the (fast) validation poll. `uploaded` was
rejected — it would leave the job green on a validation failure while nothing publishes.
Trade-off accepted: a green job now means "valid + will publish", not "confirmed live on
Central". Commits — **jllama** `52ca3af` · **BAF** `a111584` · **sb** `6bb9812` · **plugin** `2899d1b`.

**Standing policy:** DO NOT UPGRADE jqwik past 1.9.3 — 📌 active in all 4 repos (see [`policies/jqwik-prompt-injection.md`](policies/jqwik-prompt-injection.md)).

**Standing policy:** run `mvn spotless:apply` before every commit that touches `.java` — 📌 active in all 4 repos (versions in the canonical tool matrix above; `spotless:check` is bound to `verify` and the early `code-style` CI job. See [`policies/spotless-formatting.md`](policies/spotless-formatting.md)).

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
