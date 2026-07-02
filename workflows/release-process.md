# Release Process (canonical, cross-repo)

Maintainer-facing release procedure shared by all sibling repos
(BitcoinAddressFinder, java-llama.cpp, streambuffer, llamacpp-ai-index-maven-plugin).
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
