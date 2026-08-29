# subprocess.h

Knowledge base for work on [sheredom/subprocess.h](https://github.com/sheredom/subprocess.h)
via the fork [`bernardladenthin/subprocess.h`](https://github.com/bernardladenthin/subprocess.h),
checked out at [`../../subprocess.h`](../../subprocess.h).

> **Scope note.** subprocess.h is a **C/C++** project and belongs to the non-Java tier of
> this workspace — it is listed in [`../crossrepostatus.md`](../crossrepostatus.md), but the
> parity and history tables there compare Maven, PIT and SpotBugs and therefore have no rows
> for it. None of the Java guides or policies apply. This folder is where its hard-won,
> non-obvious findings survive between sessions.

## Contents

| File | Topic |
|---|---|
| [`contributions.md`](contributions.md) | **Start here** — all twelve PRs, how each landed, and what was learned on the way |
| [`platform-boundaries.md`](platform-boundaries.md) | The version boundaries the library must respect, each with primary-source evidence |
| [`verification-playbook.md`](verification-playbook.md) | How to test a platform you do not own — Docker matrices, Apple SDKs, osxcross, forced code paths |
| [`../utest.h/`](../utest.h/) | The vendored test framework. Six defects found through this work — two blocked AIX and 32-bit outright, one silently skips tests a `--filter` should have run |

## The one structural fact worth knowing first

**It is a single header, vendored by others.** llama.cpp carries it as
`vendor/sheredom/subprocess.h`, and jllama reaches it through llama.cpp. A change here does
not ship as a library upgrade that downstreams opt into — it lands in their tree on the next
vendor sync, compiled by whatever toolchain they happen to use.

That is why nearly every issue in this repo has the same shape:

> A POSIX function was called unconditionally. It does not exist on some platform someone
> actually builds on. The build breaks for people who never asked for the feature.

`posix_spawn_file_actions_addchdir_np` alone produced three of them — glibc, macOS
([#108](https://github.com/sheredom/subprocess.h/issues/108)) and AIX
([#109](https://github.com/sheredom/subprocess.h/pull/109)) — because it was added by
[#83](https://github.com/sheredom/subprocess.h/pull/83) with no availability guard at all.

The answer that has worked so far is a **capability probe**: a macro named after what the
user wants (`SUBPROCESS_HAVE_CWD`), not after the symbol that implements it; defined on
every platform; overridable; and **fail-closed**, so a toolchain the probe cannot recognise
gets "feature unavailable" rather than a link error. See
[`platform-boundaries.md`](platform-boundaries.md) for the boundaries themselves and
[`verification-playbook.md`](verification-playbook.md) for how each one was established.

## Repository facts that keep mattering

- **CI on fork PRs differs between the two repositories, and it changed here.** Through
  #104 no PR in subprocess.h got check runs at all — including
  [#104](https://github.com/sheredom/subprocess.h/pull/104) at the moment it was merged, so
  a green or absent result was not a signal about the change. As of 2026-08-15 fork PRs in
  subprocess.h **do** run automatically (#113 and #117 both did). `sheredom/utest.h` still
  gates them: runs land on `conclusion: action_required` and wait for the maintainer, which
  is where #188, #189 and #190 sit. Check which regime applies before reading anything into
  a missing run.
- **Green CI is not evidence.** Twice in one session a real defect sat behind a fully green
  matrix: the fd-0 case in #112 (442/442 with the bug present) and the 32-bit Windows break
  from #116 (`cmake.yml` builds x64 only). Both are written up in
  [`contributions.md`](contributions.md). Ask what dimension a matrix *cannot* reach before
  trusting it.
- **…and red CI sometimes is the only instrument.** The same session's third defect — the
  posix_spawn half of the `FD_CLOEXEC` problem — cannot be reproduced on Linux at all,
  because glibc clears the flag on a self-duplication where Apple does not. No local
  measurement could have found it or confirmed its fix. A pull request **inside the fork**
  runs the whole matrix, macOS included, for free and without touching upstream; see
  [`verification-playbook.md`](verification-playbook.md). Use it before pushing a guess to a
  real PR.
- **The maintainer squash-merges.** Local branches are therefore never ancestors of `main`
  afterwards; `git branch -d` refuses and `-D` is correct — but verify content equality
  first (`git diff <branch> <upstream-main>` must be empty).
- **The maintainer wants brevity.** Verbatim, on [#104](https://github.com/sheredom/subprocess.h/pull/104):
  *"Your LLM should be made to be succinct, that is a wall of text with about 1/100 useful
  words."* Full reasoning belongs in this folder; PR comments get a tl;dr and the actionable
  part.
