# Contributions and open items

Upstream: [sheredom/subprocess.h](https://github.com/sheredom/subprocess.h), vendored by
llama.cpp as `vendor/sheredom/subprocess.h` and therefore reaching jllama through it.

Status as of **2026-08-16**. Three PRs merged, **four open**, plus three in
[sheredom/utest.h](https://github.com/sheredom/utest.h) — see
[`../utest.h/`](../utest.h/).

## Open

| PR | Head | Content | CI |
|---|---|---|---|
| [#112](https://github.com/sheredom/subprocess.h/pull/112) | `eadfac5` | AIX support. Continues @mehendarkarprajwal's [#109](https://github.com/sheredom/subprocess.h/pull/109), whose commit `e6cec1b` is included unchanged. Adds `SUBPROCESS_ADDCHDIR_IS_POSIX` and extends `SUBPROCESS_SPAWN_VIA_FORK` to OpenBSD and NetBSD < 10, plus the PowerPC/RISC-V guard for `subprocess_fail_divzero`. All four review comments addressed, merged with current `main`. 9 commits, +254/-10 | 2 macOS jobs red **until #118 lands** |
| [#113](https://github.com/sheredom/subprocess.h/pull/113) | `fc73817` | `portability.yml` beside `cmake.yml`: capability paths, 32-bit, musl, four foreign architectures, four BSD VMs, three macOS deployment targets. Review comment addressed. +137 | **red on purpose**, 8 jobs |
| [#117](https://github.com/sheredom/subprocess.h/pull/117) | `cf1ec55` | Fixes the 32-bit Windows build that [#116](https://github.com/sheredom/subprocess.h/pull/116) broke. +12/-4 | 24/24 green |
| [#118](https://github.com/sheredom/subprocess.h/pull/118) | `dc19c0d` | Keeps pipe ends off 0, 1 and 2, fixing the posix_spawn half of the `FD_CLOEXEC` problem #115 introduced. +97/-2 | green — and cannot prove itself, see below |

**Neither #117's nor #118's own CI can validate what it fixes.** #117's defect
is Win32-only and `cmake.yml` builds Windows x64; #118's is macOS-only and no
existing test runs with a standard descriptor closed. Both are green exactly as
they would have been without the fix. What carries them is a local MSVC
`-A Win32` run for #117, and for #118 a new test that fails without the change
plus a real macOS run — see
[`verification-playbook.md`](verification-playbook.md) for how that was reached
without a Mac.

Two branches also live in the fork without a PR — `utest_fix_msvc_push_pragma`
and `fix_null_compare`. **Both are @sheredom's**, mirrored by the fork, not ours;
all ten commits on the first carry his name and the second is his own
[#155](https://github.com/sheredom/utest.h/pull/155). Nothing to open there.

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
| `windows-x86` | `subprocess_size_t` is not `SIZE_T` on Win32 — **added by #116 on 2026-08-14**, not present when this PR was opened | #117 |

`linux s390x` passes, which is what makes the ppc64le/riscv64 row meaningful
rather than noise: the same assertion is correct on a 64-bit architecture that
does trap.

The `windows-x86` row is the strongest argument the PR has, because it was not
planned. That job was **green** on the previous run and went red on the merge
that brought `main` forward — every other job in the run unchanged. A defect
the maintainer introduced hours earlier, in his own repository, found within a
day by a job that exists only because of this PR. See below.

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


## The review round of 2026-08-14

@sheredom reviewed all three open PRs on the same day, six comments, all
"changes requested". Four of them are one complaint: the PRs carried
explanatory prose that repeated what the code already said. Verbatim, on #113:

> LLM has put unwarranted context in the yml. Please do a pass to remove
> comments like these.

That is the same objection as the *"wall of text with about 1/100 useful
words"* on #104, now aimed at code comments rather than PR bodies. **Treat it
as a standing constraint, not a one-off.** What survived the trimming, and the
rule that decided it: keep a comment only where deleting it invites a wrong
edit, not where it merely supplies background.

| Comment | Outcome |
|---|---|
| `portability.yml` prose | 32 comment lines → 5. Kept: why `foreign-arch` runs only `*divzero`, why NetBSD appears twice |
| `__NetBSD_Version__` paragraph | deleted outright |
| `SUBPROCESS_SPAWN_VIA_FORK` paragraph | 8 lines → 4 |
| *"Why do we even need this define?"* | `SUBPROCESS_EXEC_FAILURE_STATUS` removed, `_exit(127)` written directly |
| *"Could we only extern to this in a define block for AIX...?"* | moved above the function, but guarded on `SUBPROCESS_SPAWN_VIA_FORK`, **not** `_AIX` — see below |
| utest.h#188 double printing | answered, not changed — see [`../utest.h/`](../utest.h/) |

**The `execvpe` deviation is the one worth remembering.** Following the
suggestion literally breaks glibc: `execvpe` is a GNU extension there, so
`<unistd.h>` declares it only under `_GNU_SOURCE`, and anyone forcing the fork
path without that macro loses the declaration. Measured both ways with
`-Werror=implicit-function-declaration`. The suite cannot see it either way,
because `test/CMakeLists.txt` defines `_GNU_SOURCE` on Linux. musl hides it
identically. The suspicion that drove the check — that OpenBSD might lack
`execvpe` entirely and produce a link error — turned out to be **wrong**:
OpenBSD and NetBSD both have it.

## Three defects found by merging, not by reading

`main` moved on 2026-08-14 while #112 was under review —
[#115](https://github.com/sheredom/subprocess.h/pull/115) (POSIX pipes) and
[#116](https://github.com/sheredom/subprocess.h/pull/116) (Windows handle
inheritance), both by the maintainer. Neither is visible from the branch, and
`mergeable: MERGEABLE` says nothing about either: git merged both cleanly and
the suite stayed green.

**Two commits, three defects, and each surfaced through a different
instrument** — a local merge, a CI job that only exists because of #113, and a
regression test written for a different platform entirely. None of them would
have been found by reading the diffs.

### #115 × #112: the child loses its stdin

#115 now creates the stdio pipes close-on-exec. #112's forked child relies on
`dup2` to strip that flag when it installs them on 0, 1 and 2 — and `dup2` does
clear it, **except `dup2(fd, fd)`, which is a no-op**. With fd 0 free in the
parent, the stdin pipe's read end lands on 0, the child's
`dup2(stdinfd[0], STDIN_FILENO)` becomes `dup2(0, 0)`, and `exec` closes the
child's stdin.

Neither change causes it alone. Measured with a parent that closes fd 0 before
`subprocess_create`:

| | fd 0 open | fd 0 closed |
|---|---|---|
| #112 before the merge | ok | ok |
| `main` alone (posix_spawn) | ok | ok |
| merged | ok | **child loses stdin** |

Fixed by clearing `FD_CLOEXEC` on the three descriptors after the dup2s
(`fcntl` is async-signal-safe, so the child stays within what it may call
before `exec`), with a regression test that closes fd 0 around a
`subprocess_create` — using the `process_is_fd_open` helper #115 itself
introduced.

**The suite was 442/442 with the defect present**, in both implementations,
because nothing ran with a standard descriptor closed. Green CI was not
evidence of anything here.

Since 2026-08-16 the fix and its test are confirmed on **real AIX 7.3 /
POWER10**, at 32- and at 64-bit, 443/443 each. That matters more than another
Linux row: AIX reaches the fork path *natively*, so it is the only place the
regression test runs without `-DSUBPROCESS_SPAWN_VIA_FORK=1` forcing it.
Everywhere else it is a simulation of the path it guards. See
[`../AIX/7.3/`](../AIX/7.3/).

### #115 again, on macOS: the same defect on the posix_spawn path

The `FD_CLOEXEC` fix above covered the fork path, and every local target went
green. Then #112's macOS jobs failed — on **our own regression test**:

```
Expected : (1) == (return_code)
  Actual : 1 vs 0
 Message : exec closed the child's stdin
```

`return_code == 0` means the helper found fd 0 as `EBADF` in the child. Same
symptom, different implementation: the pipes are created by the shared
`subprocess_pipe_cloexec` *before* the fork/spawn split, and the posix_spawn
path installs them with `posix_spawn_file_actions_adddup2`. Apple documents
that as behaving "as if `dup2()` had been called" — with no special case for
equal descriptors, so the self-duplication is a no-op there too. glibc applies
the POSIX clarification and clears the flag, which is why Linux never showed it.

**This is upstream's, not #112's.** It exists on `main` without any of our work;
nothing there runs with a standard descriptor closed, so nobody had seen it.

[#118](https://github.com/sheredom/subprocess.h/pull/118) moves a pipe end off
0, 1 and 2 at creation time (`subprocess_fds_above_std`), which removes the
self-duplication for *both* implementations rather than patching each.

**Follow-up, once #118 is merged:** #112's `fcntl` fix becomes redundant, since
without a self-duplication `dup2` clears the flag by itself. Harmless to leave,
but removable — and **only after the merge**, or #112 loses its guard while
the defect is still on `main`.

**Confirmed on macOS**, which is the only place it can be: 24/24 green,
`100% tests passed out of 4`, on the run described under "Reaching a macOS
runner without owning a Mac" in
[`verification-playbook.md`](verification-playbook.md).

The local measurements could only show the fix does no harm. The new invariant
test — no pipe end may sit on a standard descriptor — is what carries locally:
red on unpatched `main`, green with the fix, because that precondition *is*
observable on Linux even though the symptom is not.

### #116: 32-bit Windows does not build

#116 declares `InitializeProcThreadAttributeList` and
`UpdateProcThreadAttribute` with `subprocess_size_t` where the SDK has
`SIZE_T`, `PSIZE_T` and `DWORD_PTR`. Those are `ULONG_PTR` — `unsigned long` on
Win32, while `subprocess_size_t` is `unsigned int` there. Same width, distinct
types in C++, so the **redeclaration itself** is rejected before any call is
reached: `C2733` on the declarations, `C2664` on the two call sites.

Win64 is unaffected because the two agree there, and `cmake.yml` builds Windows
x64 only — which is why nobody saw it. Reproduced locally with MSVC 19.44 and
SDK 10.0.26100; [#117](https://github.com/sheredom/subprocess.h/pull/117) adds
`subprocess_ulongptr_t`, deliberately outside the `_MSC_VER < 1920` split, or
newer MSVC keeps taking `size_t` from `<inttypes.h>` and stays broken.

**#117's own CI cannot validate #117.** It runs `cmake.yml`, x64 only, which
was never broken; the run is green exactly as it would have been without the
fix. The evidence is the local `-A Win32` measurement, nothing else.

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
