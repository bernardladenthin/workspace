<!--
SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# Git credentials in release workflows

## Checkout and API authentication

Set `persist-credentials: false` when later steps do not need the checkout's Git authentication,
or when a Git operation uses a separate token. Checkout can still authenticate its initial fetch;
the option controls whether credentials remain available to later Git commands.

In all four Java repositories, `github-snapshot` and the versioned release-asset job use
`persist-credentials: false`. Their GitHub API clients receive tokens explicitly (`GH_TOKEN` for
`gh`, the release action's token input/default for uploads). Git's saved credentials are unnecessary
for these API operations. The shared `test_snapshot.py` checks both upload jobs in each repository;
update their shared-job hashes when changing the workflow text.

Retain checkout authentication when a job intentionally uses that same identity for subsequent
authenticated Git commands. Make the repository and required permissions explicit. The built-in
`GITHUB_TOKEN` is scoped to the workflow repository; pushing to another repository needs an
identity authorized for that destination. Use a token limited to the required repository and
permissions; a GitHub App installation token is suitable where an App is already provisioned,
otherwise a suitably scoped fine-grained PAT.

## A separate token for a Git push

None of the four Java repositories pushes with Git from a workflow. java-llama.cpp's
`mirror-llama-source`, which pushed each release's pinned llama.cpp commit to a fork with a token of
its own, was removed on 2026-10-25: the owner maintains that fork. Should a workflow need a Git
push to another repository again, give it a token scoped to that repository and to
`contents: write`, only in the push step, keep the checkouts at `persist-credentials: false`, and
pass the authorization header through `--config-env` scoped to the exact URL rather than in a
token-bearing URL or a command-line value (see the Git sources below).

## Sources and scope of the cross-repository check

- [`actions/checkout` README at the pinned action commit](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/README.md):
  credential persistence, opt-out, least permissions and repository scope of `github.token`.
- [Git `--config-env` documentation](https://git-scm.com/docs/git#Documentation/git.txt---config-envnameenvvar):
  explicitly describes passing sensitive `http.extraHeader` values through the environment.
- [Git URL-specific HTTP configuration](https://git-scm.com/docs/git-config#Documentation/git-config.txt-httplturlgt):
  specificity of URL matching; `http.extraHeader` supports clearing inherited headers with an empty value.

The audit covered workflows, composite actions and shell scripts in java-llama.cpp,
BitcoinAddressFinder, srcmorph and streambuffer, plus workspace automation. All four use explicit API
tokens for release uploads and contain no custom Git push or header override.
