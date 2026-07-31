# PIT Mutation Testing Standard

> Canonical workspace policy. Each sibling repo's `CLAUDE.md` points to this
> file instead of duplicating the rules.

A single, shared contract for **PIT (pitest) mutation testing** across all four
sibling Maven repos, so the plugin version, the 100% gate, and — crucially — the
**correct way to invoke PIT locally** are identical everywhere.

## 1. Canonical invocation (read this first)

Always run PIT with a **lifecycle phase prefix**:

```bash
mvn test-compile org.pitest:pitest-maven:mutationCoverage
```

**Do NOT run the bare `mvn org.pitest:pitest-maven:mutationCoverage`.** It fails
with:

```
java.nio.file.NoSuchFileException: {argLine}
```

Why: three of the four repos set surefire `<argLine>@{argLine} …</argLine>`, where
`@{argLine}` is a *late-replacement* token populated by **JaCoCo's
`prepare-agent`** goal (bound to the `initialize` phase). PIT reads surefire's
`argLine`; if no lifecycle phase has run, `prepare-agent` never fires, the
`argLine` property is undefined, and `@{argLine}` reaches PIT as the literal
string `{argLine}` — which it then treats as a file path. Prefixing `test-compile`
runs `initialize` first, so JaCoCo sets the property and PIT gets a resolved
`-javaagent:…` argLine. (BAF uses a literal `argLine` rather than `@{argLine}`,
but JaCoCo still attaches there, so the same prefix is correct and harmless.)

This is exactly the command every repo's CI uses in `publish.yml`:

```yaml
- name: Run PIT mutation tests
  run: mvn --batch-mode --no-transfer-progress test-compile org.pitest:pitest-maven:mutationCoverage
```

BAF additionally passes `-Dnet.ladenthin.bitcoinaddressfinder.disableLMDBTest=true`
in CI (its PIT `targetTests` are pure-Java, so LMDB tests are irrelevant, but the
flag keeps the run clean on hosts without the LMDB native lib).

## 2. Shared settings (identical across all 4 repos)

| Setting | Value |
|---|---|
| `pitest-maven` | **1.25.8** (canonical pin: the tool matrix in [`../crossrepostatus.md`](../crossrepostatus.md)) |
| `pitest-junit5-plugin` | **1.2.3** |
| `<mutationThreshold>` | **100** (CI-enforced gate) |
| `<timeoutConstant>` | **30000** |
| CI invocation | `mvn … test-compile org.pitest:pitest-maven:mutationCoverage` |

No repo sets `outputFormats`, `excludedClasses`, `excludedTestClasses`, or
`withHistory` — all PIT defaults. Keep it that way unless there is a documented
reason, recorded here.

## 3. Per-repo `targetClasses` scope (intentionally different)

The gate covers exactly the classes **proven to reach 100% mutation parity**,
expanded incrementally — not the whole tree, except where the whole tree already
passes. This divergence is deliberate.

| Repo | Scope | Mutations* | Hermetic? |
|---|---|---|---|
| streambuffer | whole package `net.ladenthin.streambuffer.*` | 179 | yes |
| BitcoinAddressFinder | explicit 16-class list (util/model/io/core/keyproducer/secret/configuration/statistics leaves + custom exceptions) | 65 | yes |
| srcmorph (reactor `srcmorph` core module) | explicit 47-class list (config / document / engine / indexer / prompt / provider / support) | see `srcmorph/pom.xml`† | yes |
| java-llama.cpp | `value.*` + `exception.*` + `args.*` + `json.{TimingsLogger,RerankResponseParser,ChatResponseParser,CompletionResponseParser}` | 243 | **no — see §4** |

\* Mutation counts verified 2026-06-25 (`pitest-maven 1.25.5`); all four gates
re-run green 2026-07-08 on `pitest-maven 1.25.6`. The pin has since bumped to
`1.25.8` (current). Counts drift as code changes — treat them as a snapshot, not a
contract; the **100% gate** is the contract.

† srcmorph became a 3-module reactor (rename from `llamacpp-ai-index-maven-plugin`); its
PIT gate now targets the framework-free **`srcmorph` core module** (47 classes, `mutationThreshold`
100), authoritative list in `srcmorph/pom.xml`. The `srcmorph-cli` / `srcmorph-maven-plugin`
modules are not PIT-gated yet. The exact mutation total for the 47-class set has not been
re-recorded here — the 100% gate is the contract.

## 4. Hermeticity caveat — java-llama.cpp audio path

java-llama.cpp's gate reaches 100% **only when the audio test fixture is present**.
Without it the run is **98%** (4 `NO_COVERAGE` mutants), and the gate **reds**.

The 4 survivors are all in `value.ContentPart.audioFile(Path)` — the null
file-name guard, the `.wav` / `.mp3` extension dispatch, and the
`Files.readAllBytes` call. The **only** test that exercises that method is
`AudioInputIntegrationTest`, which is model-/fixture-gated and self-skips (via
`Assume`) when no audio clip is supplied (`net.ladenthin.llama.audio.input` — no
committed default; audio is intentionally not committed). So in any environment
lacking the clip (e.g. a network-restricted sandbox), those lines are never
executed and PIT fails.

Contrast: the sibling method `value.ContentPart.imageFile(Path)` **is** hermetic —
it is covered by temp-file unit tests (PNG/JPG/GIF/WEBP magic bytes written to a
`@TempDir`), so its mutants are killed with no external fixture. The audio path has
no such unit test.

**Implication:** java-llama.cpp's "100% PIT" is environment-conditional today, not
fully hermetic. The hermetic fix (out of scope for this doc) is a temp-file unit
test for `audioFile(Path)` mirroring the `imageFile(Path)` tests. Until then, a
green PIT gate on java-llama.cpp requires the CI audio fixture.

## 5. The stale-`targetClasses` failure mode (recurring)

PIT `targetClasses` is an FQN-bearing config, so it shares the failure mode of
`spotbugs-exclude.xml`, ArchUnit rules, and JNI `FindClass` strings: after a
**package move**, a stale FQN/glob silently matches **nothing**, the gate passes
vacuously, and the regression is invisible. This actually happened
(`llama.Pair`→`value.Pair`, `bitcoinaddressfinder.BitHelper`→`util.BitHelper`).

After any package move, **re-validate every FQN/path-bearing artifact** — PIT
`targetClasses` and `targetTests` included — and confirm PIT still reports a
non-zero mutation count for the moved classes.

## 6. Expanding the gate

The all-time goal is 100% PIT on every class in every repo. Expand incrementally:
add tests until a candidate class holds 100% mutation parity, then add it to that
repo's `<targetClasses>` (and `<targetTests>` where the repo lists tests
explicitly). Track per-repo progress in each repo's `TODO.md` "Mutation-testing"
item and refresh the snapshot in
[`../crossrepostatus.md`](../crossrepostatus.md) when scope changes.
