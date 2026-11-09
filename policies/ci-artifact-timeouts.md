# CI Artifact Timeouts

> Canonical workspace policy. Each sibling repo's `CLAUDE.md` points to this
> file instead of duplicating the rules. The check lives in
> [bernardladenthin/actions](https://github.com/bernardladenthin/actions)
> (`common/check-artifact-timeouts`, README section "Artifact timeouts").

## Why

An artifact transfer has no timeout of its own. In java-llama.cpp's Publish run
42675444364 (2026-11-09) an `actions/upload-artifact` step of the aarch64 Vulkan
build hung for hours after a build of a minute and a half. No step set
`timeout-minutes`, so GitHub's 360 minutes were the only limit, and every job
behind it waited that long. Measured over two complete runs of that pipeline,
the longest artifact transfer took 18 s.

A job-level `timeout-minutes` does not help here: it would have to cover the
job's build (hours for a cold native build) and would not catch the hang sooner.
The limit belongs on the transfer step.

## The rule

Every workflow that transfers artifacts reads the limit from a repository
variable, with a default, in its **top-level** `env`:

```yaml
env:
  ARTIFACT_TIMEOUT_MINUTES: ${{ vars.ARTIFACT_TIMEOUT_MINUTES || '20' }}
```

and every `actions/upload-artifact` / `actions/download-artifact` step says

```yaml
      - uses: actions/upload-artifact@<commit> # v7.x.y
        timeout-minutes: ${{ fromJSON(env.ARTIFACT_TIMEOUT_MINUTES) }}
```

- **Default 20 minutes**, at most 30 (`max-minutes` of the check). That is far
  above the 18 s measured, and far below 360.
- **The variable is optional.** Without it the default applies. To change the
  value without a commit, set it per repository: *Settings → Secrets and
  variables → Actions → Variables → New repository variable*, name
  `ARTIFACT_TIMEOUT_MINUTES`, a whole number of minutes
  (`https://github.com/bernardladenthin/<repo>/settings/variables/actions`).
  A personal account has no variables above the repository; an organization's
  variable of that name would apply to its repositories too.
- `fromJSON` turns the text into the number `timeout-minutes` needs, so a
  variable that is not a whole number fails the run loudly.
- **Exempt:** `scorecard.yml` (a template; scorecard-action refuses a workflow
  with a top-level `env`). Composite actions cannot set `timeout-minutes` on their
  own steps, so the four publication actions of bernardladenthin/actions that
  transfer artifacts are not covered; the step that calls one can carry a timeout.

## The check

`common/check-artifact-timeouts` runs in each repository's `repository-checks`
job and fails when a transfer step has no timeout, has one that is not the
expression above, or when its workflow lacks the `env` line or its default is
outside 1–30. Configuration: the `artifact-timeouts` section of
`.github/actions-config.json` (`patterns`, `exempt`, `max-minutes`).

## Status

| Repo | Steps | Workflows |
|---|---:|---|
| java-llama.cpp | 110 | `publish.yml`, `java-tests.yml`, `post-release.yml` |
| BitcoinAddressFinder | 11 | `publish.yml` |
| srcmorph | 7 | `publish.yml` |
| streambuffer | 9 | `publish.yml`, `formal-verification.yml` |

The workflows carry the timeouts since jllama #609, BAF #416, srcmorph #280 and
sb #206. The check joins `repository-checks` with the first actions release that
has it (bernardladenthin/actions#16).
