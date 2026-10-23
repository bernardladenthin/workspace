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
otherwise a suitably scoped fine-grained PAT can supply the existing secret.

## A separate token for a Git push

java-llama.cpp's release-only `mirror-llama-source` is the only custom authenticated Git push
found in the four Java repositories. Both of its checkouts disable persisted credentials.
`LLAMA_MIRROR_TOKEN` is provided only to the push step and needs `contents: write` on
`bernardladenthin/llama.cpp`. The workflow's own token remains `contents: read`.

The script scopes its HTTP authorization header to the exact mirror URL and passes its value
through `--config-env` (Git 2.31+), not through a token-bearing URL or command-line value:

```bash
# MIRROR_URL is a validated https://github.com/owner/repo.git URL.
# JLLAMA_MIRROR_AUTH_HEADER is exported from the step's mirror secret.
GIT_TERMINAL_PROMPT=0 git -C "$SRC" \
  -c "credential.$MIRROR_URL.helper=" \
  -c "http.$MIRROR_URL.extraheader=" \
  --config-env="http.$MIRROR_URL.extraheader=JLLAMA_MIRROR_AUTH_HEADER" \
  push "$MIRROR_URL" "$HEAD_COMMIT:$REF"
```

An empty header resets inherited values for that URL before adding the intended one, including
an existing exact-URL header. The URL-specific empty credential helper prevents fallback to an
unrelated stored identity. There are no persistent Git-config writes; the raw/encoded secret is
absent from Git's argv. In Actions the encoded value is masked; outside Actions the script never
prints it. An unsuccessful remote tag lookup fails the step instead of being mistaken for an
absent tag. Existing matching tags remain idempotent; different tags are never force-updated.

The repository-specific mirror regression tests create a temporary Git repository with included
checkout credentials and stale mirror credentials. Real Git resolves the effective configuration;
network reads/writes are intercepted. The tests check the chosen identity, argv, unchanged config,
lookup/push failures and idempotency without using real tokens or contacting GitHub.

## Sources and scope of the cross-repository check

- [`actions/checkout` README at the pinned action commit](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/README.md):
  credential persistence, opt-out, least permissions and repository scope of `github.token`.
- [Git `--config-env` documentation](https://git-scm.com/docs/git#Documentation/git.txt---config-envnameenvvar):
  explicitly describes passing sensitive `http.extraHeader` values through the environment.
- [Git URL-specific HTTP configuration](https://git-scm.com/docs/git-config#Documentation/git-config.txt-httplturlgt):
  specificity of URL matching; `http.extraHeader` supports clearing inherited headers with an empty value.

The audit covered workflows, composite actions and shell scripts in java-llama.cpp,
BitcoinAddressFinder, srcmorph and streambuffer, plus workspace automation. The three other Java
repositories use explicit API tokens for release uploads and contain no corresponding custom
Git push/header override. Public upstream fetches in java-llama.cpp do not require its mirror token.
