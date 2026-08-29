# Release Process (canonical, cross-repo)

Maintainer-facing release procedure shared by all sibling repos
(BitcoinAddressFinder, java-llama.cpp, streambuffer, srcmorph).
End users should consult each repo's `CHANGELOG.md`.

Each sibling's `docs/RELEASE.md` points here and adds only **repo-specific** notes
(e.g. a multi-module reactor's all-poms bump, or a tag-prefix policy). Keep the common
procedure below; put anything that is true for only one repo in that repo's supplement.

> Paste this prompt into a new Claude Code session, fill in the placeholders, and send it to perform a release.

```
Release `{PROJECT}` to Maven Central.

**Step 1 — Prepare the release (do immediately):**
1. Read the current version from `pom.xml` on `main` — it will be `{VERSION}-SNAPSHOT`.
2. Set the release version to `{VERSION}` (strip `-SNAPSHOT`). In a **single-module** repo this is
   the root `pom.xml` `<version>`. In a **multi-module reactor** every module pom must move in
   lockstep — use `mvn -q versions:set -DnewVersion={VERSION} -DgenerateBackupPoms=false` and see
   the repo's `docs/RELEASE.md` supplement.
3. In `README.md`, set every **release** dependency example to `{VERSION}` and verify the
   **snapshot** example stays `{VERSION}-SNAPSHOT`. (Some repos have more than one README carrying a
   dependency snippet — the repo supplement lists them.)
4. Finalize `CHANGELOG.md`: rename the `[Unreleased]` heading to `[{VERSION}] - {DATE}`, add a fresh
   empty `[Unreleased]` above it, and update the compare-link footer — add
   `[{VERSION}]: .../compare/v{PREV}...v{VERSION}` and repoint
   `[Unreleased]: .../compare/v{VERSION}...HEAD`.
5. Commit the changes on a branch and open a PR; merge/fast-forward it into `main`. Do **not** commit
   release changes directly to `main` — branch protection and the PR-CI gates run there.

**Step 2 — Wait for manual confirmation:**
I will (a) create the `v{VERSION}` tag + GitHub release on the merged commit and (b) run the
**Publish** workflow via `workflow_dispatch` with `publish_to_central=true`. That input gates the
Central deploy: `publish-release` requires it **and** a `v*` tag, and `publish-snapshot` requires it
too — so a `main` push (even carrying a release version) never auto-publishes on its own. Wait for me
to confirm the release is live on Maven Central before proceeding.

**Step 3 — Post-release snapshot bump (after my confirmation):**
On a fresh branch off the updated `main`:
- Bump the version to `{NEXT_VERSION}-SNAPSHOT` (same single-pom / `mvn versions:set` rule as Step 1.2).
- `README.md` snapshot dependency example → `{NEXT_VERSION}-SNAPSHOT`
  (the release dependency examples stay at the just-released `{VERSION}`).
Commit and open a PR.

**Placeholders:**

| Placeholder      | Value                                        |
|------------------|----------------------------------------------|
| `{PROJECT}`      | *(project name)*                             |
| `{VERSION}`      | *(release version, e.g. `1.3.0`)*           |
| `{PREV}`         | *(previous release, e.g. `1.2.0`)*          |
| `{NEXT_VERSION}` | *(next snapshot base, e.g. `1.3.1`)*        |
```

---

## What actually gets missed (derived from real releases, 2026-08-29)

The steps above are the procedure; this section is the **audit of two shipped releases**
(BitcoinAddressFinder `v1.7.0`, java-llama.cpp `v5.0.6`) plus a pre-check of streambuffer and
srcmorph. Everything here is a gap that survived a release, so treat it as the checklist that
matters rather than a restatement of Step 1.

### Step 4 (the CHANGELOG footer) is the most-missed step

It is invisible: nothing builds, tests or renders the compare-link footer, so an omission ships and
then compounds.

- **BAF `v1.7.0` skipped it entirely** — the `## [1.7.0]` heading was written, but no
  `[1.7.0]: …/compare/v1.6.1...v1.7.0` link was ever added and `[Unreleased]` still pointed at
  `v1.6.1`. Found and repaired during the 1.8.0 prep, one release later.
- **srcmorph is worse: `v1.1.0` is tagged and released but has no CHANGELOG section at all** — the
  chain jumps `1.0.2 → 1.1.1`, so a shipped version is undocumented. Not repaired here (srcmorph is
  not releasing); recorded in `crossrepostatus.md`.

**Mechanical post-check — run it before opening the release PR.** Released headings, footer links
and tags must be the same set:

```bash
echo "headings: $(grep -oE '^## \[[0-9.]+\]' CHANGELOG.md | tr -d '#[] ' | tr '\n' ' ')"
echo "links   : $(grep -oE '^\[[0-9.]+\]'   CHANGELOG.md | tr -d '[]'   | tr '\n' ' ')"
echo "tags    : $(git tag -l 'v*' | sort -V | tr '\n' ' ')"
```

A version present in one line and absent from another is the defect. (A rolling `snapshot`
pre-release tag is expected and is not a version.)

### The version lives in more places than `pom.xml` and `README.md`

Step 1.3 says "some repos have more than one README". In practice the drift is wider, and it is
**per-repo** — each repo's supplement must list its own sites. Observed:

| Repo | Sites beyond the pom(s) |
|---|---|
| java-llama.cpp | 4 poms in lockstep, `README.md` (7 occurrences), `llama-langchain4j/README.md`, `llama-android/README.md`, `llama-kotlin/README.md` |
| BitcoinAddressFinder | `pom.xml`, `CLAUDE.md` (2), `README.md`, `docs/tuning-your-gpu.md` (2), **24 `examples/run_*.{sh,bat}` launcher scripts** |
| streambuffer | `pom.xml`, `README.md` (2) |
| srcmorph | 4 poms in lockstep, `README.md`, `srcmorph-maven-plugin/README.md` |

BAF's 24 launcher scripts are the instructive case: `v1.7.0` shipped them correctly at `1.7.0`, so
they *are* release-tracking, and a bump that forgets them leaves every documented run command
pointing at a jar that does not exist.

### Prefer a guard over a checklist item

Two repos have already solved the launcher-script class of drift, in opposite ways, and both beat
remembering:

- **BAF has a test.** `ExampleRunScriptJarVersionTest` reads the first `<version>` from `pom.xml` and
  asserts every `…-<version>-jar-with-dependencies.jar` reference under `examples/` and `docs/`
  matches. Bumping the pom **reds the build** until the scripts follow — the checklist is enforced,
  not documented. This is the model to copy.
- **srcmorph needs no guard.** Its `examples/run_*.sh` resolve the jar with a glob
  (`srcmorph-cli-*-jar-with-dependencies.jar`), so the name cannot go stale; the version in the
  surrounding comment is illustrative only. Structural immunity beats a test.

A repo that hardcodes jar names and has **neither** is the one to fix.

### Version jumps that are not a plain `-SNAPSHOT` strip

Step 1.2 assumes `{VERSION}-SNAPSHOT → {VERSION}`. When the release skips the snapshot base — e.g.
java-llama.cpp went `5.0.7-SNAPSHOT → 5.1.0` because the range added API — Step 1.3's "verify the
snapshot example stays `{VERSION}-SNAPSHOT`" no longer parses. The README's snapshot snippet then
names a version that will never be published. Leave it for Step 3 (which sets it to
`{NEXT_VERSION}-SNAPSHOT`), but **say so in the release PR**, or a reader will read it as an
oversight.

