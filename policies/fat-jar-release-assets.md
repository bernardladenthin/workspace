<!--
SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# Fat-jar (jar-with-dependencies) release assets

Cross-repo convention for the runnable **fat jars** (`*-jar-with-dependencies*.jar`) that the
sibling repos ship. It captures one invariant and the per-repo shapes that implement it, so the
three repos that ship a fat jar stay conceptually aligned even though the *artifacts* differ.

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

## Per-repo shapes

| Repo | Fat jar(s) | Kept off Central by | Built + signed by |
|---|---|---|---|
| **jllama** (`java-llama.cpp`) | Multi-backend **`all-<os>-<arch>`** jars (default CPU + every GPU backend of that OS/arch in `net/ladenthin/llama/<OS>/<ARCH>/<backend>/` subdirs, runtime-selected by `LlamaLoader` via the `jllama-backends.txt` manifest) + the default CPU fat jar | The Central `deploy` runs **without** the `assembly` profile; the fat jars are assembled by a separate `package-fatjars` job | `.github/package-fatjars.sh` assembles them; `.github/sign-fatjars.sh` GPG-signs each (`.asc`) in the `github-release-signed` / `github-snapshot` attach jobs (which declare `environment: maven-central` + `checkout`). `.sha256` **and** `.asc`. |
| **srcmorph** (`srcmorph-cli`) | One CLI fat jar **per `net.ladenthin:llama` classifier** (default all-platform CPU + one per GPU classifier: `cuda13-*`, `vulkan-*`, `opencl-*`, `rocm-*`, `sycl-*`, `openvino-*`, `msvc-windows`) named `srcmorph-cli-<v>-jar-with-dependencies[-<classifier>].jar` | `srcmorph-cli/pom.xml` sets `<attach>false</attach>` on the assembly execution → built into `target/` but never installed/deployed | The `publish-{release,snapshot}` jobs loop over the classifier set (`mvn -pl srcmorph-cli -am -Dllama.classifier=<c> package`), rename per classifier (default built **last** = unsuffixed CPU jar), collect them into the asset dir, then sign via `.github/sign-fatjars.sh`. `.asc` only. |
| **BAF** (`BitcoinAddressFinder`) | **Single** fat jar (LWJGL ships one `natives-*` classifier jar per platform, but they may all sit on one classpath — LWJGL picks the match at runtime — so there is still no classifier split) | The Central `deploy` runs `-P release` **without** `assembly`; the fat jar is built by a **second** invocation that stops at `verify` (never reaching `deploy`), so `central-publishing`'s deploy-bound publish goal never runs | `mvn -P release,assembly verify` in the `publish-{release,snapshot}` jobs; `maven-gpg-plugin` (bound to `verify`) signs the attached fat jar → `.asc`. |
| **sb** (`streambuffer`) | ➖ N/A — a pure library with no runnable entry point, so no fat jar is produced or shipped | — | — |

## Keep-in-sync notes

- **jllama / srcmorph classifier lists.** The set of GPU classifiers is defined by
  `java-llama.cpp/llama/pom.xml`'s `<classifier>` entries. jllama's `package-fatjars.sh`
  enumerates it from the pom and **fails loud** on any new classifier until it is consciously
  ranked/excluded. srcmorph's `publish.yml` hardcodes the classifier array — **on a
  `net.ladenthin:llama` version bump, re-check that list against the pom** (and confirm every
  classifier is actually published on Central for the pinned version).
- **Shared signing script (`.github/sign-fatjars.sh`).** jllama and srcmorph sign their loose fat
  jars with a **byte-identical** `.github/sign-fatjars.sh` (dual-licensed `MIT OR Apache-2.0`, the
  cross-repo-synced-file convention) — it imports the key into an ephemeral keyring and produces a
  verified detached armored `.asc` for every `*-jar-with-dependencies*.jar` in a directory. **Sync
  any edit to both copies, and update the recorded checksum below** (same discipline as the
  byte-identical `verify-signing-key` job).
  BAF does **not** use it: its single fat jar is an *attached* Maven artifact, so `maven-gpg-plugin`
  signs it directly during the `verify` run.
- **Signature convention.** New fat-jar-shipping surfaces should sign with a detached armored
  `.asc` using the `maven-central`-scoped key, in a dispatch-gated job, reusing `sign-fatjars.sh`.

## Drift check — `sign-fatjars.sh` checksum

The shared script must be **byte-identical** in both repos (jllama + srcmorph). Its canonical
SHA-256 and a one-line verify command live in the single consolidated drift-check table —
**"Cross-repo byte-identical files — checksum drift check"** in
[`../crossrepostatus.md`](../crossrepostatus.md) (alongside the `signing-selftest` `.kts` files).
On any intentional edit to `sign-fatjars.sh`, update both copies **and** that table in the same
change set.
