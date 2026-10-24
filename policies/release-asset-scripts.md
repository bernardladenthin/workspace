<!--
SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# Shared release-asset scripts

The four Java repositories use byte-identical Python entry points, library code and tests,
listed in each `.github/shared-files.sha256`. Python 3.9+ and the standard library are sufficient;
only the snapshot uploader additionally needs `gh` and `GH_TOKEN`. CI checks out the scripts from
the same commit as the artifacts. Repository-specific paths and classifiers live in
`.github/release-assets.json`, which is deliberately **not** shared.

Release-upload checkouts use `persist-credentials: false`; the GitHub API receives its token
explicitly. See [git-checkout-credentials.md](git-checkout-credentials.md) for the cross-repo
authentication policy and Git's separate-token pattern.

## Collect and check the expected deliverables

```bash
python3 .github/collect-release-assets.py signed-snapshot-assets
python3 .github/collect-release-assets.py signed-release-assets --config .github/release-assets.json
```

The destination must be empty. The collector discovers the root POM and recursively declared
modules, requiring one literal, consistent version. Supported packaging: `pom`, `jar`,
`maven-plugin`. Each module contributes its signed `target/<artifactId>-<version>.pom`; jar and
plugin modules additionally contribute the plain, sources and javadoc jars. Maven profile modules,
custom final names, expression-based versions and other packaging require an explicit extension
of the contract before adoption. No `target/**/*.jar` scan: stale versions, unconfigured fat jars
and third-party plugin dependencies do not become release assets.

Every expected artifact and `.asc` must exist and be nonempty. Missing files fail the collector,
but all available expected files are copied first. `complete=true|false` is written to
`GITHUB_OUTPUT` even on a collection error; the publish job exports
`assets_complete: ${{ steps.collect.outputs.complete }}`. The publication handoff upload runs only after the final preflight succeeds. Central transfer
is a later independent job, so a Central failure cannot remove that already secured handoff.

Minimal configuration for a plain Maven library:

```json
{"schema": 1}
```

Optional settings, illustrated with generic names:

```json
{
  "schema": 1,
  "maven": {"standalone": ["tools/agent"], "cyclonedx": true},
  "files": [
    {"source": "app/target/app-{version}-{classifier}.jar",
     "classifiers": {"csv": ".github/classifiers.csv", "column": "classifier"}},
    {"source": "mobile/build/publications/main/pom-default.xml",
     "name": "mobile-{version}.pom"},
    {"source": "mobile/build/mobile-{version}-{classifier}.jar",
     "classifiers": ["sources", "javadoc"]},
    {"source": "archives/upstream-*-{version}-src.tar.gz"}
  ]
}
```

- `schema` is required and currently `1`. Unknown keys cause validation to fail, which catches configuration typos.
- `maven.standalone` adds separately published Maven projects with the same version.
- `maven.cyclonedx` defaults to false. When true, every reactor module's `target/bom.json` and
  `.asc` are renamed to `<artifactId>-<version>-cyclonedx.json[.asc]`. Standalone projects are
  excluded. Enable this only where the Maven build actually attaches that BOM.
- Each `files` rule names **one** required artifact per classifier. `central: true` marks an extra
  for Central staging verification; it defaults to false. `source` is relative to the
  repository and may contain a glob, which must match exactly one path. `name` optionally renames
  the artifact; its signature is copied with the same name plus `.asc`.
- The only template parameters are `{version}` and `{classifier}`. `classifiers` defaults to
  `[""]`, or is a nonempty, unique list, or a CSV path/column. Blank/comment CSV lines are skipped.
- Output names must be unique, flat artifact names. Paths outside the repository are rejected.

| Repository | Explicit extras |
|---|---|
| java-llama.cpp | Standalone agent, reactor CycloneDX BOMs, native classifiers from `natives.csv`, Android publications and renamed documentation jars, one signed upstream source archive |
| BitcoinAddressFinder | One required fat jar; signed by the second Maven `verify` invocation |
| srcmorph | Default CLI fat jar plus 14 GPU variants, signed separately; plain Maven artifacts staged before the rebuild |
| streambuffer | None; POM and three jars discovered from the root POM |

### Preserve signed Maven output before rebuilding (srcmorph)

```bash
python3 .github/collect-release-assets.py central-assets --maven-only
python3 .github/collect-release-assets.py --list-classifiers 1 > fatjar-classifiers.txt
mapfile -t CLASSIFIERS < fatjar-classifiers.txt
# Build, sign and structurally check fat jars in fatjar-assets/ using CLASSIFIERS.
python3 .github/collect-release-assets.py signed-snapshot-assets --maven-assets central-assets
```

The first command skips extra-file rules. The last reads every required Maven output from the
staged directory under its final filename, rather than a subsequently overwritten `target/`.
Missing staged files still fail the final collection. `--list-classifiers` takes a zero-based
file-rule index and lets the build and verifier consume one classifier list. The CPU build
remains last; the structural native-content checks and signing stay in srcmorph.

## Gate publication before uploading

The publication workflow stages and signs locally, then uses `publication.py prepare` to
cryptographically verify and freeze the complete contract. Central and GitHub Release consume
that same GitHub-Actions handoff independently. See [publication-preflight.md](publication-preflight.md)
for the shared CLI, configuration, checksums and asynchronous Central transfer.

`report-asset-signatures.py` remains a diagnostic presence/size reporter; it is not the
publication gate. Publish jobs no longer attach unsigned files and fail afterwards.

## Update the rolling snapshot

```bash
ASSETS_COMPLETE=true python3 .github/update-snapshot.py snapshot-assets
# Optional for another rolling channel: --tag nightly --title 'Nightly build'
```

CI supplies `GITHUB_REPOSITORY`, `GITHUB_SHA`, `GITHUB_RUN_ID`, `GITHUB_RUN_ATTEMPT` and passes the
successful preflight result through `ASSETS_COMPLETE`. The complete job is serialized by
`snapshot-release-${{ github.repository }}` with `cancel-in-progress: false` in all four repos.
If another channel is introduced, give it a distinct but stable serialization group.

The helper compares commit ancestry and the recorded run/attempt before any upload. Superseded
runs are skipped; divergent histories fail. The workflow calls it only with a complete, preflight-verified collection. Its legacy direct-call
partial-upload path is not used by publishing workflows. Only a complete signed upload advances the source tag and release notes,
then prunes assets outside the uploaded set. Existing release IDs are retained. All asset pages
are read before deletion, HTTP 404 is tolerated for already removed assets, other failures are
reported after trying the remaining deletions. Versioned releases are never pruned.

## Maintenance and checks

Change shared code, entry points and tests in every consumer, then run
`python3 .github/check-shared-files.py --write` in each. The config's `.license` sidecar is shared;
the JSON itself differs. `github-snapshot` is a shared job across all four; `github-release` is
shared across the three Maven-only repositories. The Central transfer jobs and publication helper
are identical across all four consumers. Keep job-level changes synchronized too.

Run `python3 -m unittest discover -s .github/buildcheck/tests -t .github`, the offline shared-file
check, release-gate and run-script checks, and actionlint in each checkout. The common tests cover
generic fixtures, each checkout's real POM/config contract, staged Maven output, partial assets,
signature gaps, CLI outputs and snapshot ordering using a fake GitHub client. They do not publish
anything. Native dependency, Android packaging, bytecode and CLI smoke checks remain specialized
where their artifact semantics require it. See [fat-jar-release-assets.md](fat-jar-release-assets.md)
for signing and release policy.
