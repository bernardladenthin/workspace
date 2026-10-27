<!--
SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# Fat-jar (jar-with-dependencies) release assets

Cross-repo convention for the runnable **fat jars** (`*-jar-with-dependencies*.jar`) that the
sibling repos ship. It captures one invariant and the per-repo shapes that implement it, so the
repos that ship a fat jar stay conceptually aligned even though the *artifacts* differ. One repo
ships one today (BAF); **jllama stopped with its modular natives** (5.2.0) and **srcmorph with
1.4.0** (see their rows below), and sb never did -- for those three, the rule that survives is the
release-asset gating ("no release asset is attached that CI has not run"), applied to the
artifacts they do attach.

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

## Verify locally, then publish independently

All intended artifacts must be built and signed before publication. The shared preflight
verifies the complete local contract, every detached signature and Central/GitHub byte equality,
then freezes a checksummed handoff. Missing or invalid local output fails before either upload.

Central and GitHub Release then consume the same checked files independently. Neither waits
for the other. A Central error cannot hide the signed GitHub files, and slow Portal validation
must not hold a build open: release uploads request automatic publication and return after
upload acceptance. Never rebuild or re-sign between the gate and either consumer.

This supersedes the earlier attach-unsigned-then-fail procedure. See
[publication-preflight.md](publication-preflight.md) for the complete sequence and shared tools,
and [release-asset-scripts.md](release-asset-scripts.md) for the collector contract.

## The `snapshot` pre-release holds exactly the current upload

`snapshot` is a rolling "latest" pre-release, and `gh release upload --clobber` replaces same-named
assets but never removes any other. Measured 2026-10-12: java-llama.cpp's `snapshot` held **208**
assets, 109 of them from 5.0.0–5.0.7 and 43 in shapes that no longer existed (`msvc-windows`,
`all-*-jar-with-dependencies`); srcmorph (16 assets, all stale, from the old
`llamacpp-ai-index-maven-plugin` coordinates), streambuffer (11, 5 stale) and java-llama.cpp each
still carried `fb-contrib-7.6.4.jar`, `fb-contrib-7.7.4.jar` and `findsecbugs-plugin-1.14.0.jar`,
SpotBugs plugin jars an older collect step uploaded from `target/spotbugs/` in 2026-05/06; BAF (14)
carried the previous version's six jars.

So `github-snapshot` uses the common snapshot update (`java/publish-github` of bernardladenthin/actions) in all four repositories.
The whole upload/tag/notes/prune operation is serialized with a stable job concurrency group;
older commits or older runs/attempts of the same commit cannot overwrite a promoted snapshot.
After a **complete signed collection and successful upload**, the helper moves the source tag
to the build commit, updates notes with the commit and run, and deletes every asset outside the
upload set. An incomplete collection never reaches the job (`github-snapshot` runs only on the
publication gate's `assets_complete=true`), and the helper itself refuses one before any change:

- the **keep-set is the asset directory the run uploaded**, never a version pattern -- a pattern has
  to be re-taught at every classifier added or dropped, which is how the 43 stale shapes arose;
- **after a successful complete upload**, so failed/incomplete uploads do not prune the release;
- **the first snapshot of a repository is a draft until its upload is complete**: no public
  pre-release and no `snapshot` tag naming a build whose assets are not there yet; a draft that a
  failed first upload left behind is reused by the next run;
- **every deletion is printed by name**, so the job log is the audit trail;
- `github-release` **never deletes**, and the helper refuses a `v<digit>...` tag as the rolling
  tag: a versioned `v*` release is history.

Nothing is deleted by hand; the next snapshot run clears each repo's backlog by itself.

### Asset by asset, after the upload -- what the May 2026 runs taught

The step has three guards, and they come from the job's own history rather than from caution:

- **An empty upload is refused** (`::error`, exit 1): with nothing in the asset directory every
  asset of the release would count as stale and the step would empty it. Unreachable today -- the
  attach job fails at `download-artifact` when the publish job collected nothing (no artifact is
  uploaded from an empty directory; BAF, 2026-07-12, dispatched on a non-`SNAPSHOT` version) and `gh
  release upload snapshot snapshot-assets/*` fails on the unexpanded glob -- but the guard makes the
  invariant explicit instead of a consequence of step order.
- **An asset that is already gone counts as removed.** An API deletion returning HTTP 404 is
  tolerated; authentication and other API failures remain errors. Every asset page is read before
  deleting anything, so deletions cannot shift a later page and make stale files disappear from
  the scan.
- **A failed deletion is reported and the rest are still tried**; the step fails afterwards. The
  assets of this upload are on the release either way, so a failed prune leaves extra assets, never
  missing ones. Nothing is swallowed with `|| true` -- that is what hid the GitHub Packages
  failures below for a day.

**The history, from the four repos' `git log` and the Actions API (job logs expire after 90 days,
the step results do not).** The first snapshot job (2026-05-07, all four repos, `release.yaml` /
`snapshot.yml`) cleaned up on two levels, both by delete-and-recreate: `gh release delete snapshot
--yes --cleanup-tag || true` followed by `gh release create snapshot <jars>`, and for GitHub
Packages `actions/delete-package-versions` with `min-versions-to-keep: 0`, replaced the same evening
by `gh api --method DELETE /user/packages/maven/<package> || true` because the action cannot remove
the last version of a package. On 2026-05-10, 22:30-22:45 UTC, bursts of dependabot merges put
several main-push runs minutes apart on each sibling; their snapshot jobs started within seconds of
each other and deleted the release under one another: BAF 4 of 5, srcmorph 4 of 6, streambuffer 5 of
6 jobs failed in the step "Publish rolling snapshot release" **with the artifact download green**,
and per repo exactly the job whose `create` came last survived. java-llama.cpp (2026-05-07, run
25521091023) and streambuffer (2026-05-10 22:44 UTC) also failed that step once each with no
concurrent job. The Central migration of 2026-05-11 (07:50 UTC) dropped the GitHub Releases and
GitHub Packages snapshots altogether, and the same day `github-snapshot` came back as `gh release
view || gh release create` plus `gh release upload --clobber`: idempotent, never deleting, which is
why the backlog above could grow; no commit or PR named the failures, so the reason was lost. The
case remembered as "no artifacts, so no cleanup" is a different one: the attach job dying at
`download-artifact` after a publish job that collected nothing (BAF, 2026-07-12), which is the
intended fail-loud path and never reaches the upload or the prune. Since 2026-06-18
`publish-snapshot` -- and with it `github-snapshot` -- runs only on a manual dispatch with
`publish_to_central`, so two attach jobs overlap only when two dispatches do.

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
| srcmorph | `smoke-jar` (since 1.4.0; `smoke-fatjar` before) | `mvn install` of the reactor, then `examples/build-your-own-jar` with the reactor's versions → `target/srcmorph.jar` (the jar a user builds) → `config_Plan.json`; bytecode ≤ 52 over it and the plugin jar first | exit 0 + `Main#run end.`; `mock` provider, so no GGUF/GPU/network |
| jllama | `smoke-natives` (matrix, one row per desktop platform) | `smoke-test-natives.{sh,ps1}` → `java -cp '<smoke set>/*'` server on the published jars (classes + runtime deps + the platform's library jar + every GPU module jar of the platform) | `/health` 200 + a `/v1/chat/completions` choice + the loader line naming every GPU module of the platform (each skipped by ggml on the GPU-less runner) + the HTTPS round |
| jllama | `smoke-natives-macos` | `smoke-native-macos.sh` → `codesign` + `NativeLoadSmoke.java` on the `metal-macos-aarch64` jar | signature matches its own pages + the JVM loads the dylib and crosses JNI |
| jllama | `smoke-agent-linux` | `smoke-agent.sh` → the published agent's thin jar + its dependencies on one classpath with the Linux x86-64 smoke set | bytecode ≤ 65 + the agent alone fails for the missing core + `--help` + a one-shot answer + a `read_file` round surfacing a marker (cached tool model) + `--web` + `--acp` |
| sb | `smoke-jar` | `smoke-jar.sh` → `java -cp <jar> StreamBufferSmoke.java` | jar carries `module-info.class` + a real write/read/EOF round-trip through the API, exit 0 + marker |

BAF and srcmorph (on the user-built jar) run the **`java/smoke-fatjar-cli` action of bernardladenthin/actions** (inputs
`jar-dir`, `jar-glob`, `work-dir`, `marker`, `args`; plain `java -jar`, no extra JVM flags — the
contract under test is that the published artifact runs as-is). Both CLIs derive from the same `cli.Main` pattern
and log `Main#run end.`, which is what lets the marker be identical too. jllama needs
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
| **srcmorph** (`srcmorph-cli`) | ➖ **None since 1.4.0** (#249). Users build the runnable jar with `examples/build-your-own-jar/pom.xml`: `srcmorph-cli` from Central with `llama-platform` excluded, the one natives jar of the OS/arch an OS-activated profile picks (`-Dnatives=` overrides), an optional GPU module jar via `-Dgpu=<classifier>`, packed by `jar-with-dependencies` into `target/srcmorph.jar` -- there are too many OS/CPU/GPU combinations to release one jar each. The thin `srcmorph-cli` jar names its `Main-Class`, so `jbang` can run it too. Up to 1.3.0 the publish jobs built one fat jar per desktop GPU module jar of `net.ladenthin:llama` (15 per release, `<attach>false</attach>`, signed by `.github/sign-fatjars.sh`, never on Central). | The GitHub Release attaches the Maven artifacts with the `.asc` maven-gpg wrote for Central, and nothing else | — (`sign-fatjars.sh`, `verify-classifier-fatjars.sh` and the runtime-license collector went with the fat jars) |
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
mechanism (incident: 2026-08-02). It never applied to the classifier-loop shape srcmorph (until
1.3.0) and jllama (until 5.2.0) used (javadoc `<source>` resolves to 8 there); neither builds a fat
jar any more.

## Keep-in-sync notes

- **jllama natives classifiers.** The natives jars are declared once, in
  `java-llama.cpp/.github/natives.csv` (a `kind` column since 5.2.0: `library` jars and additive GPU
  `module` jars); jllama's pom executions, `llama-platform`, workflow artifacts, smoke sets and the
  loader's backend lists are checked against it (`check-natives.py`), and `package-smoke-sets.sh`
  reads it. srcmorph's classifier list in `.github/release-assets.json` went with its fat jars
  (1.4.0; the file is `{"schema": 1}` now). What still names classifiers there is the OS profiles of
  `examples/build-your-own-jar/pom.xml` (one natives jar per OS/arch, `metal-macos-aarch64` on
  macOS) -- **on a `net.ladenthin:llama` bump that adds or renames a library jar, re-check them
  against `natives.csv`**; the `smoke-jar` job builds that pom only on the Linux runner.
- **Signing.** BAF's single fat jar is an *attached* Maven artifact, so `maven-gpg-plugin` signs it
  directly during the `verify` run. `.github/sign-fatjars.sh`, which signed loose fat jars, is gone
  from every repository (jllama 5.2.0, srcmorph 1.4.0).
- **Signature convention.** New fat-jar-shipping surfaces should sign with a detached armored
  `.asc` using the `maven-central`-scoped key, in a dispatch-gated job -- preferably as an attached
  artifact that maven-gpg signs, as BAF does.

## `sign-fatjars.sh` — retired

The script was **byte-identical** in both repos (jllama + srcmorph) while both shipped fat jars;
jllama's copy went with its fat jars (5.2.0), srcmorph's with its own (1.4.0). Should a repository
need to sign loose jars again, it becomes an action of bernardladenthin/actions rather than a
copy.
