# Contributions and open items

Upstream: [sheredom/subprocess.h](https://github.com/sheredom/subprocess.h), vendored by
llama.cpp as `vendor/sheredom/subprocess.h` and therefore reaching jllama through it.

Status as of **2026-08-10**. Three PRs merged, **two open**, plus two in
[sheredom/utest.h](https://github.com/sheredom/utest.h) — see
[`../utest.h/`](../utest.h/).

## Open

| PR | Content | CI |
|---|---|---|
| [#112](https://github.com/sheredom/subprocess.h/pull/112) | AIX support. Continues @mehendarkarprajwal's [#109](https://github.com/sheredom/subprocess.h/pull/109), whose commit `e6cec1b` is included unchanged; conflict resolved additively (+183/-7 against `main` where #109 is +227/-97). Adds `SUBPROCESS_ADDCHDIR_IS_POSIX` and extends `SUBPROCESS_SPAWN_VIA_FORK` to OpenBSD and NetBSD < 10, plus the PowerPC/RISC-V guard for `subprocess_fail_divzero`. 4 commits, +220/-10 | — |
| [#113](https://github.com/sheredom/subprocess.h/pull/113) | `portability.yml` beside `cmake.yml`: capability paths, 32-bit, musl, four foreign architectures, four BSD VMs, three macOS deployment targets. +154 | **red on purpose** |

A follow-up comment on #109 reports the AIX results and answers both of
@sheredom's questions there; #112 is offered explicitly as a continuation rather
than a replacement.

### #113 is red, and that is the point

Every failing job is a real defect on current `main`, each fixed by an open PR:

| Job | fails because | fixed by |
|---|---|---|
| `linux-32-bit`, `linux armv7` | `utest.h` 32-bit: oversized constants and the `ll` modifier | utest.h#188 |
| `netbsd 10.1` | `PRIu64` undefined — NetBSD gates the `PRI` macros for pre-C++11 | utest.h#188 |
| `netbsd 9.4` | no `addchdir` under either spelling before 10.0; #102's guard has no version test | #112 |
| `openbsd 7.9` | no `addchdir` at all, but the probe's `#else` claims otherwise | #112 |
| `linux ppc64le`, `linux riscv64` | `subprocess_fail_divzero` asserts a trap that does not happen | #112 |

`linux s390x` passes, which is what makes the last row meaningful rather than
noise: the same assertion is correct on a 64-bit architecture that does trap.

Two corrections were needed after the first run, both caught by CI rather than by
reasoning:

- The `foreign-arch` jobs originally ran the whole suite and failed on **all
  four** architectures, s390x included, because qemu-user does not propagate the
  errno `posix_spawn` uses to report a failed exec. A permanently red job is
  worse than none; they now build everything and run `--filter=*divzero` only,
  with the reason in a comment so it does not read as hiding failures.
- The PR text claimed `armv7` passes. It does not — armv7 is ILP32 and fails in
  the build for the same reason as `linux-32-bit`, never reaching a test. The
  guess that ARM's `__aeabi_idiv0` might differ by libc was wrong and unnecessary.

## Merged

Upstream `main` is at `9ce0d70`. Everything below was squash-merged, so local branches were
never ancestors of `main` — `git branch -d` refuses and `-D` is correct, after verifying the
content arrived.

| PR | Merged | Commit | Content |
|---|---|---|---|
| [#104](https://github.com/sheredom/subprocess.h/pull/104) | 2026-08-09 | `e329358` | `SUBPROCESS_HAVE_CWD` probe; `ENOSYS` where `posix_spawn_file_actions_addchdir_np` is missing. Covers **glibc < 2.29**, **macOS < 10.15** and **iOS/tvOS/watchOS**. 3 files, +30 |
| [#105](https://github.com/sheredom/subprocess.h/pull/105) | 2026-08-09 | `907d50c` | `check_cxx_compiler_flag` instead of the CMake feature, falling back to `-std=c++2a` for GCC 8. 1 file, +8/−1 |
| [#106](https://github.com/sheredom/subprocess.h/pull/106) | 2026-08-09 | `f455031` | `SUBPROCESS_SPAWN_REPORTS_EXEC_ERRORS` probe; `access(X_OK)` pre-check where `posix_spawn` cannot report a failed exec (**glibc < 2.24**). 1 file, +25 |

#104 also closed [#108](https://github.com/sheredom/subprocess.h/issues/108) (MacPorts,
PowerPC, `-mmacosx-version-min=10.6`), reported by `barracuda156` while the PR was open. The
macOS arm was added in response and the PR was retitled from "Fix building against glibc
older than 2.29" to **"Fix building where posix_spawn_file_actions_addchdir_np is
unavailable"**.

**The repaired version of #106 is what landed** — `SUBPROCESS_SPAWN_REPORTS_EXEC_ERRORS`
occurs 5 times in `9ce0d70`, not once. See the next section for why that mattered.

## The near-miss worth remembering

Merging `main` into #106 after #104 landed produced four conflicts. Three belong to `main`
(the `SUBPROCESS_HAVE_CWD` comment, the Darwin arm, the README paragraph). The fourth is the
branch's **own** new probe block, where `main` has nothing — and it was resolved the wrong
way, deleting the definition while keeping its use site:

```c
#if !SUBPROCESS_SPAWN_REPORTS_EXEC_ERRORS   /* macro now undefined -> folds to 0 */
    if (0 != access(commandLine[0], X_OK)) {   /* -> !0 -> always compiled in */
```

The build stayed green, the tests stayed green, and the `access()` pre-check silently became
unconditional on **every** platform — the opposite of what the PR promised. Caught only
because the merge stat showed 19 deletions where a merge should have added lines.

**Rule for the next merge:** in a conflict between a capability probe and its use site,
verify the macro is still *defined*, not just used. `grep -c` on the macro name is enough —
one occurrence means the definition is gone.

## Follow-up by the maintainer

[#110](https://github.com/sheredom/subprocess.h/pull/110) (`9ce0d70`, sheredom, AI-assisted)
closed the one review thread #104 left open — *"Don't we need to make
`subprocess_error_from_errno` handle `ENOSYS` too?"*:

```c
  subprocess_error_spawn = -8,
+ subprocess_error_not_supported = -9
...
+ case ENOSYS:
+   return subprocess_error_not_supported;
```

That is the resolution predicted here: a new enum value rather than remapping an existing
one. The `ENOSYS` path introduced by #104 now surfaces as "platform cannot do this" instead
of "spawn failed".

Two other third-party PRs landed alongside: [#102](https://github.com/sheredom/subprocess.h/pull/102)
(NetBSD build) and [#101](https://github.com/sheredom/subprocess.h/pull/101) (Windows
argument quoting).

## Third-party PR worth tracking

[#109](https://github.com/sheredom/subprocess.h/pull/109) — "Initial port for AIX" by
`mehendarkarprajwal`, prompted by the same llama.cpp vendoring. Replaces `posix_spawn` with
`fork()` + `chdir()` + `exec` plus an `FD_CLOEXEC` pipe carrying `errno`, under
`#if defined(_AIX)`. Still open, `mergeable_state: dirty`, based on `8671cee` — five upstream
commits behind, so it needs a rebase regardless.

`sheredom` asked on it: *"Does #104 not 'solve' the cwd issue?"* — **no**, and the two
interact:

- #104 *detects* absence and degrades to `ENOSYS`. #109 *implements* the capability. For
  llama.cpp on AIX, `ENOSYS` is not a substitute.
- #104's probe answers `SUBPROCESS_HAVE_CWD = 1` on AIX, because AIX defines neither
  `__GLIBC__` nor `__APPLE__` and falls through to the `#else`. Without #109, AIX needs the
  override `-DSUBPROCESS_HAVE_CWD=0`. With #109 merged, the `1` becomes correct.
- They conflict textually: #109 restructures the whole POSIX branch of
  `subprocess_create_ex`.

**Defect reported 2026-08-09:** #109 as submitted does not build on the non-AIX path under
the project's own warning settings — `actions_created`, `posix_error` and `actions` are still
declared at function scope (lines 1137–1139) but redeclared in the new inner scope, and the
`if (actions_created)` cleanup was removed. Three `-Werror=unused-variable` errors. Nobody
noticed because no CI ran.

The AIX path itself is sound: forced with `-D_AIX` on Linux it builds and passes **432/432**,
`chdir` takes effect in the child, and a missing binary reports `subprocess_error_not_found`.
See [`verification-playbook.md`](verification-playbook.md).

## CI that would have caught these

Answering the maintainer's *"Is there anyway we can test this in CI? I'd love not to regress
y'all in future!"*, in order of cost:

| Check | Cost | Would have caught |
|---|---|---|
| Linux Docker matrix over glibc 2.17 / 2.28 / 2.29 / 2.31 + musl | low | #104 and #106 entirely |
| macOS runner, `-mmacosx-version-min=10.13 -Werror=unguarded-availability-new` | trivial, no extra SDK | the macOS half of #104 — verified to fail before and pass after |
| Any Linux runner, `-D_AIX` | trivial | the #109 build error |

Not CI-able: SDKs older than 10.15 (third-party mirrors — inappropriate for a public repo)
and real AIX (no hosted runners; the GCC Compile Farm is interactive, not a build runner).

Offered but not built. If it is ever taken up, this is the shortest path.

## Known limitations still standing

| Item | Why left alone |
|---|---|
| #106 covers `posix_spawn` only, not `posix_spawnp` | closing it means reimplementing the `PATH` search, including empty entries meaning "current directory" and the `ENOEXEC` shell fallback. Measured on glibc 2.17: explicit path returns `-4`, `PATH` search still returns `0` |
| #106 has a TOCTOU window between `access` and `posix_spawn` | on a platform whose `posix_spawn` cannot report the failure at all, a best-effort check beats none. Gated to those platforms only |
| musl older than 1.1.24 still fails to link | musl exposes no version macro, so it cannot be detected. This is what the override is for; `-DSUBPROCESS_HAVE_CWD=0` builds cleanly there |
| The #108 toolchain was never reproduced | no usable PowerPC-Darwin cross toolchain exists, and old `AvailabilityMacros.h` gates `MAC_OS_X_VERSION_MIN_REQUIRED` on `__APPLE_CC__`, which MacPorts GCC does not define. The Darwin arm is fail-closed precisely so this case lands on `ENOSYS`. `barracuda156` was asked to confirm; no answer |
| macOS 26 non-`_np` branch from #99 unverified | `posix_spawn_file_actions_addchdir` is absent from `spawn.h` **and** `libSystem.B.tbd` in every SDK up to 15.5, and no SDK 26 was obtainable. If Apple does not ship it, that branch is a latent link error. Pre-existing, not ours |

The clean fix for the first two is to drop `posix_spawn` on the affected platforms and use
`fork` + `exec` + a `O_CLOEXEC` pipe carrying `errno` — what glibc 2.24 itself does, closing
the race *and* the `posix_spawnp` gap, and reporting failures `access` cannot see (missing
interpreter, `ENOEXEC`). **#109 is exactly that construction, for AIX.** If it lands, the
mechanism is there to reuse rather than propose from scratch. Roughly 60–100 lines of the
most delicate code in the file; the maintainer's call, not offered unsolicited.
