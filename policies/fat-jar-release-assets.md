<!--
SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# Fat-jar (jar-with-dependencies) release assets

Cross-repo convention for the runnable **fat jars** (`*-jar-with-dependencies*.jar`) that the
sibling repos ship. It captures one invariant and the per-repo shapes that implement it, so the
repos that ship a fat jar stay conceptually aligned even though the *artifacts* differ. Two repos
ship one today (BAF, srcmorph); **jllama stopped with its modular natives** (5.2.0, see its row
below) and sb never did -- for both, the rule that survives is the release-asset gating ("no
release asset is attached that CI has not run"), applied to the artifacts they do attach.

## The invariant

> A `jar-with-dependencies` (uber jar) is a **GitHub-Release download asset only** — it is
> **never deployed to Maven Central** — and it is attached **with a detached, armored GPG
> `.asc` signature**.

Why never Central:

- A jar-with-dependencies is **redundant** on Central: consumers depend on the *plain* jar and
  let Maven resolve the dependency graph; nobody `<dependency>`-references the uber jar.
- It is **large** (bundles every runtime dependency), and where it bundles a **native binary**
  (`net.ladenthin:llama`, LWJGL natives, …) it is also **platform-specific** — the wrong shape for a
  Central artifact that is meant to be portable coordinates.
- Not shipping it to Central also avoids any redistribution obligation for bundled vendor
  binaries.

Why signed (`.asc`): signature **parity** with the thin jars (which `maven-gpg-plugin` signs at
`deploy`) and with each other. A `.sha256` (integrity) may sit alongside it, but a checksum is not
a signature — the `.asc` provides **authenticity**. Keep both where both exist.

## Where the signing key lives (and why signing happens where it does)

The GPG signing secret (`GPG_PRIVATE_KEY` / `GPG_PASSPHRASE`) is scoped to the **`maven-central`
GitHub Environment**. That environment has **no approval gate** (the standalone
`verify-signing-key*` jobs use it on every push), so any job may declare
`environment: maven-central` to obtain the key without blocking the pipeline.

Fat-jar signing therefore happens in whatever job **both** (a) runs on the dispatch-gated publish
path where the key is delivered and (b) has the fat jar on disk — see the per-repo shapes below.
Signing is never done in a job that runs on fork PRs (the key is withheld there).

## The release-asset gating caveat (applies to all repos)

GitHub-Release assets — thin jars **and** fat jars — are attached **only** when the publish
workflow runs as a **`workflow_dispatch` with `publish_to_central=true`** (the release-attach jobs
`need` the `publish-{release,snapshot}` jobs, which are `if: … && inputs.publish_to_central`). A
plain `git push` of a `v*` tag does **not** attach any assets. To ship the fat jars on a tag, run
the publish workflow manually with that input set (the same way the thin jars have always been
attached). Symptom of forgetting: a tag release with `assets: []`.

## Attach first, then go red — never withhold assets over a missing signature

All repos that attach assets run their attach job (`github-release`, `github-snapshot`,
jllama's `github-release-signed`) even when the publish job **failed**:

```yaml
if: ${{ !cancelled() && (needs.publish-release.result == 'success'
                         || needs.publish-release.result == 'failure') }}
```

That is deliberate and load-bearing. A Central publish-poll timeout reds the publish job *after* the
artifacts were already uploaded, and if Central is unreachable the GitHub assets are the **only** way
to get the build output at all. Withholding them because something else went wrong is the worst
outcome available.

**So a signature check must not gate the upload.** Nothing upstream asserts that every attached jar
has its detached `.asc`: the collection steps skip a missing signature with `[ -e "$f" ] || continue`,
so a failed signing step yields an attach that looks complete and is not. The obvious fix — verify,
and refuse to attach if anything is unsigned — reintroduces exactly the failure mode the `if:`
condition exists to prevent.

The ordering that satisfies both:

1. **Report** (before the upload, `id: signatures`, never exits non-zero): emit one `::error::`
   annotation per unsigned jar, and one for the case where *no* jars were collected at all; write the
   count to `$GITHUB_OUTPUT`.
2. **Upload** — unconditionally, exactly as before.
3. **Assert** (after the upload, `if: always() && steps.signatures.outputs.missing != '0'`): fail the
   job, naming the count.

Assets always land. An unsigned release is still loudly red rather than quietly wrong. Use `-1` for
"nothing was collected", so an empty asset directory is distinguishable from a signing failure.

**Status:** landed in **all four repos** — srcmorph, jllama, BAF **and streambuffer**. The two steps
are byte-identical everywhere (the only per-repo difference is the asset directory name,
`snapshot-assets` / `release-assets`), so a change to one must be synced to all four. Note the scope:
this guard is about **release assets**, not about fat jars, so it applies to streambuffer too even
though streambuffer ships no fat jar — it attaches signed thin jars like everyone else.

## No release asset is attached that CI has not run

**Every repo that attaches a release asset runs it in CI first, in a `smoke-*` job that gates both
publish jobs.** This is a standing rule, not a per-repo nicety.

It was originally written for fat jars, and streambuffer was read as exempt because it ships none.
That reading was wrong: the artifact it attaches (and deploys) is still one nothing in the pipeline
had ever loaded. **The rule is about the attached artifact, not about the fat-jar shape** — a repo
without a `Main-Class` cannot satisfy `java -jar`, so it asserts what a real consumer does instead
(put the jar on a classpath, call the API). Same job shape, repo-appropriate assertion.

The reason it needs stating: **nothing else in a Maven build ever touches the assembled artifact.**
Unit tests, PIT, SpotBugs and ArchUnit all run off `target/classes`; `mvn package` only asserts that
the assembly plugin wrote a file. So an uber jar can be built and GPG-signed perfectly while being
unrunnable — a missing `Main-Class`, a shade-mangled or duplicated resource, an absent SLF4J
binding, a native library that will not load. Signing an artifact proves *who built it*, not that it
works. java-llama.cpp learned this the expensive way: a `libjllama.dylib` merged from three CI
artifacts into a byte-level hybrid — macOS SIGKILLs any process that loads it — was signed,
attached and shipped through 5.0.6 and several 5.0.7 snapshots with an all-green pipeline, because
no job had ever loaded the packaged copy.

**Job shape (synchronized).** One job named `smoke-fatjar*` (jllama, which attaches no fat jar:
`smoke-natives*`), `needs:` whatever job produced the jar,
downloads that artifact, launches it, and is listed in the `needs:` of `publish-snapshot` **and**
`publish-release`. Two assertions minimum: the process must succeed, **and** a marker from its own
output must be present — exit code 0 alone is satisfied by a JVM that starts and does nothing.
The `<jar-glob>` must match **exactly one** jar; an ambiguous match is an error, not a "pick the
first", because that is precisely how the wrong artifact gets tested.

**Assertions are repo-specific — the job shape is not.** Force-fitting one script onto all three
would be worse than the duplication it saves:

| Repo | Job | What it launches | Assertion |
|---|---|---|---|
| BAF | `smoke-fatjar` | `.github/smoke-fatjar-cli.sh` → `config_AddressFilesToLMDB.json` | exit 0 + `Main#run end.`; also exercises the **lmdbjava natives** out of the jar |
| srcmorph | `smoke-fatjar` | `.github/smoke-fatjar-cli.sh` → `config_Plan.json` | exit 0 + `Main#run end.`; `mock` provider, so no GGUF/GPU/network |
| jllama | `smoke-natives` (matrix, one row per desktop platform) | `smoke-test-natives.{sh,ps1}` → `java -cp '<smoke set>/*'` server on the published jars (classes + runtime deps + the platform's library jar + every GPU module jar of the platform) | `/health` 200 + a `/v1/chat/completions` choice + the loader line naming every GPU module of the platform (each skipped by ggml on the GPU-less runner) + the HTTPS round |
| jllama | `smoke-natives-macos` | `smoke-native-macos.sh` → `codesign` + `NativeLoadSmoke.java` on the `metal-macos-aarch64` jar | signature matches its own pages + the JVM loads the dylib and crosses JNI |
| jllama | `smoke-agent-linux` | `smoke-agent.sh` → the published agent's thin jar + its dependencies on one classpath with the Linux x86-64 smoke set | bytecode ≤ 65 + the agent alone fails for the missing core + `--help` + a one-shot answer + a `read_file` round surfacing a marker (cached tool model) + `--web` + `--acp` |
| sb | `smoke-jar` | `smoke-jar.sh` → `java -cp <jar> StreamBufferSmoke.java` | jar carries `module-info.class` + a real write/read/EOF round-trip through the API, exit 0 + marker |

BAF and srcmorph share a **byte-identical `.github/smoke-fatjar-cli.sh`** (`<jar-dir> <jar-glob>
<work-dir> <success-marker> [args…]`, plain `java -jar`, no extra JVM flags — the contract under
test is that the published artifact runs as-is). Both CLIs derive from the same `cli.Main` pattern
and log `Main#run end.`, which is what lets the marker be identical too. **Sync any edit to both
copies, then `check-shared-files.py --write` in each** (both list it in `.github/shared-files.sha256`). jllama needs
its own scripts: its Main-Class is a server that never exits, so "exit 0" is not a contract it can
satisfy, and on macOS the assertion that matters is native loadability rather than any CLI
behaviour.

**Artifacts that only run together are smoked together.** jllama's agent (the thin
`llama-atmosphere-agent` jar on Central) deliberately carries **no core**: its pom resolves it. Its
smoke therefore launches it the way a consumer gets it — the agent jar with its own dependencies on
one classpath with the published core jars of the same run — which is the only place a version
mismatch, or a dependency both sides assumed the other one bundles, can show up. It also asserts the
negative (started alone, it must fail with `NoClassDefFoundError` for the core), because "no core, no
natives of its own" is the property the artifact exists for. The job keeps its own name
(`smoke-agent-*`, not `smoke-fatjar*`): it tests a different artifact, and the name says which.

**Cheap beats thorough here.** Each of these runs in about a minute with no model, no GPU and no
network. That is deliberate: a smoke that is expensive gets skipped, made non-gating, or quietly
deleted, and then the gap reopens. Add depth only where a cheap check genuinely cannot reach the
failure class. (jllama's agent smoke is such a case: what it ships is a tool loop, which needs a
model — it uses the already-cached 1.5B tool model on CPU, no download.)

## Per-repo shapes

| Repo | Fat jar(s) | Kept off Central by | Built + signed by |
|---|---|---|---|
| **jllama** (`java-llama.cpp`) | ➖ **None since the modular natives (5.2.0).** The GPU backends are additive module jars (`net.ladenthin:llama:<v>:<backend>-<os>-<arch>`, each one ggml backend module) next to the platform's library jar (`cpu-<os>-<arch>` / `metal-macos-aarch64`, collected by the `llama-platform` pom), so a consumer's classpath is what Maven resolves and a jar of every backend of every platform would be the opposite of the point. Replacements: `jbang --deps net.ladenthin:llama:<v>:<classifier> net.ladenthin:llama:<v>` (the classes jar's `Main-Class` is the server launcher) and `examples/server/pom.xml` (`llama-platform` + one profile per GPU module jar, a local `-P assembly` for a machine without Maven). The agent is its thin jar on Central (`jbang net.ladenthin:llama-atmosphere-agent:<v>`). Until then it shipped the default CPU fat jar, four `all-<os>-<arch>` jars and the agent's core-less jar, signed by `sign-fatjars.sh`. | The GitHub Release attaches the Maven artifacts with the `.asc` maven-gpg wrote for Central, and nothing else | — (nothing is assembled or signed in the attach jobs; `verify-signing-key` still proves the key) |
| **srcmorph** (`srcmorph-cli`) | One CLI fat jar **per desktop GPU module jar of `net.ladenthin:llama`** (default all-platform CPU + 14: `cuda13-*`, `vulkan-*`, `opencl-*`, `rocm-*`, `sycl-*`, `openvino-*` per OS/arch -- every `module` row of `natives.csv` but the Android one; `msvc-*`, `sycl-fp*` and 32-bit jars no longer exist since llama 5.2.0), each the default jar **plus** that one ggml backend module (the CPU natives stay the fallback: ggml loads the module only when its runtime is installed), named `srcmorph-cli-<v>-jar-with-dependencies[-<classifier>].jar`. Whether srcmorph follows jllama and drops them for the thin jar + `jbang --deps` is an open owner's decision (srcmorph `TODO.md`) | `srcmorph-cli/pom.xml` sets `<attach>false</attach>` on the assembly execution → built into `target/` but never installed/deployed | The `publish-{release,snapshot}` jobs loop over the classifier set (`mvn -pl srcmorph-cli -am -Dllama.classifier=<c> package`), rename per classifier (default built **last** = unsuffixed CPU jar), collect them into the asset dir, then sign via `.github/sign-fatjars.sh`. `.asc` only. |
| **BAF** (`BitcoinAddressFinder`) | **Single** fat jar (LWJGL ships one `natives-*` classifier jar per platform, but they may all sit on one classpath — LWJGL picks the match at runtime — so there is still no classifier split) | The Central `deploy` runs `-P release` **without** `assembly`; the fat jar is built by a **second** invocation that stops at `verify` (never reaching `deploy`), so `central-publishing`'s deploy-bound publish goal never runs | `mvn -P release,assembly verify` in the `publish-{release,snapshot}` jobs; `maven-gpg-plugin` (bound to `verify`) signs the attached fat jar → `.asc`. |
| **sb** (`streambuffer`) | ➖ N/A — a pure library with no runnable entry point, so no fat jar is produced or shipped. Its **thin** jar is still smoke-tested before release (`smoke-jar`, see above) and still carries a `.asc` | — | — |

**BAF-only gotcha: the second invocation must skip javadoc.** BAF's "second invocation that
stops at `verify`" shares `target/` with the preceding `deploy` invocation in the same job step
sequence, with no `mvn clean` between them — the shape any future repo would reach for if it
adopts this "second Maven invocation for a fat jar" convention on a Java ≥ 9 / JPMS-aware-javadoc
repo. That second invocation must pass `-Dmaven.javadoc.skip=true` (BAF's `publish.yml` does),
or it inherits `target/classes/module-info.class` from the first invocation and trips the JPMS
javadoc module-mode trap — see
[`jpms-module-descriptor.md`](jpms-module-descriptor.md) "A second trigger" for the full
mechanism (incident: 2026-08-02). Not applicable to srcmorph/jllama's classifier-loop shape as
written (javadoc `<source>` resolves to 8 there), but worth checking again if either ever raises
its Java baseline.

## Keep-in-sync notes

- **jllama / srcmorph classifier lists.** The natives jars are declared once, in
  `java-llama.cpp/.github/natives.csv` (a `kind` column since 5.2.0: `library` jars and additive GPU
  `module` jars); jllama's pom executions, `llama-platform`, workflow artifacts, smoke sets and the
  loader's backend lists are checked against it (`check-natives.py`), and `package-smoke-sets.sh`
  reads it. srcmorph's `publish.yml` hardcodes its classifier array (the rows with `platform=no`
  except the Android ones) — **on a `net.ladenthin:llama` version bump, re-check that array against
  `natives.csv`**: with 5.2.0's modular natives the `cpu-windows-x86`, `msvc-windows-*` and
  `sycl-fp16`/`sycl-fp32` classifiers are gone and a GPU classifier is one module jar that needs the
  platform's library jar next to it -- srcmorph's loop names the 14 desktop module jars since its
  2026-10-10 update (and confirm every natives jar is actually published on Central
  for the pinned version); `verify-classifier-fatjars.sh` fails on an unmapped classifier shape.
- **Signing script (`.github/sign-fatjars.sh`).** srcmorph signs its loose fat jars with
  `.github/sign-fatjars.sh` (dual-licensed `MIT OR Apache-2.0`) — it imports the key into an
  ephemeral keyring and produces a verified detached armored `.asc` for every
  `*-jar-with-dependencies*.jar` in a directory. It was byte-identical with jllama's copy until
  jllama dropped its fat jars (5.2.0); srcmorph's `shared-files.sha256` still lists it, which is why
  its `shared-files` job warns about the sibling until the entry is removed there. BAF does **not**
  use it: its single fat jar is an *attached* Maven artifact, so `maven-gpg-plugin` signs it directly
  during the `verify` run.
- **Signature convention.** New fat-jar-shipping surfaces should sign with a detached armored
  `.asc` using the `maven-central`-scoped key, in a dispatch-gated job, reusing `sign-fatjars.sh`.

## Drift check — `sign-fatjars.sh`

The script was **byte-identical** in both repos (jllama + srcmorph) while both shipped fat jars;
jllama's copy is gone with its fat jars (5.2.0), srcmorph's remains. Both listed it in
`.github/shared-files.sha256`; each repo's `shared-files` job fails when its copy changed alone and
warns when the other repo's copy differs (see "Cross-repo byte-identical files" in
[`../crossrepostatus.md`](../crossrepostatus.md)). On an intentional edit, change both copies and run
`python3 .github/check-shared-files.py --write` in each.
