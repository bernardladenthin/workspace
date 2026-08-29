# Contributions and open items

Upstream: [sheredom/subprocess.h](https://github.com/sheredom/subprocess.h), vendored by
llama.cpp as `vendor/sheredom/subprocess.h` and therefore reaching jllama through it.

> **The series is finished.** Status as of **2026-08-22**: **all twelve pull
> requests are merged**, seven here and five in
> [sheredom/utest.h](https://github.com/sheredom/utest.h) — see
> [`../utest.h/`](../utest.h/). Nothing is open in either repository. What
> remains below is the record of how it went, kept for the next time.

## Merged, and how each one landed

| PR | merged | as | note |
|---|---|---|---|
| [#104](https://github.com/sheredom/subprocess.h/pull/104) | 2026-08-09 | `e329358` | `SUBPROCESS_HAVE_CWD` probe |
| [#105](https://github.com/sheredom/subprocess.h/pull/105) | 2026-08-09 | `907d50c` | `-std=c++2a` fallback |
| [#106](https://github.com/sheredom/subprocess.h/pull/106) | 2026-08-09 | `f455031` | `SUBPROCESS_SPAWN_REPORTS_EXEC_ERRORS` probe |
| [#118](https://github.com/sheredom/subprocess.h/pull/118) | 2026-08-18 19:40 | `6f54d85` | pipe ends off 0, 1, 2 |
| [#117](https://github.com/sheredom/subprocess.h/pull/117) | 2026-08-18 19:41 | `76cd934` | Win32 pointer-width sizes |
| [#112](https://github.com/sheredom/subprocess.h/pull/112) | 2026-08-19 11:52 | `0dccaa9` | AIX via `fork`/`exec` |
| [#113](https://github.com/sheredom/subprocess.h/pull/113) | 2026-08-19 20:22 | `8a4715c` | `portability.yml` |

utest.h#188, #189, #190, #191 and #192 are in
[`../utest.h/`](../utest.h/). **Every one of the twelve went in verbatim** —
patch-id identical in each case, checked rather than eyeballed. That check was
not ceremonial: several PRs sat on an older base, so a plain tree diff against
`main` is *not* empty for them and would have suggested edits that never
happened.

Both repositories now run the portability matrix on `main`, and both are green.

### What the pace looked like

Eight days of silence, then almost everything inside three minutes on the
evening of 2026-08-18, and the rest over the following three days. Two things
are worth carrying forward from that:

**A reworked PR stays invisible until you say so.** #188 was pushed on
2026-08-16 and sat untouched; the thread still read as an unanswered review
until one short paragraph was posted. #113 behaved identically. Observed twice,
so it is a property of this maintainer's workflow, not an accident.

**The evidence that moved things was never the green tick.** #117 and #118 were
both merged although neither one's CI could see the defect it fixed — #117's is
Win32-only against an x64 matrix, #118's is macOS-only with no test that closes
a standard descriptor. What carried them was a local MSVC `-A Win32` run and a
new test that goes red without the change. #188 through #191 were merged without
their CI having run at all, because the fork gate was never opened.

He did comment twice, both near the end: *"Great find!"* on utest.h#190, and
*"Very good work here!"* on #113.

**Neither #117's nor #118's own CI could validate what it fixed**, and both were
merged anyway. #117's defect is Win32-only and `cmake.yml` builds Windows x64;
#118's is macOS-only and no existing test runs with a standard descriptor
closed. Both were green exactly as they would have been without the fix. What
carried them is a local MSVC `-A Win32` run for #117, and for #118 a new test
that fails without the change plus a real macOS run — see
[`verification-playbook.md`](verification-playbook.md) for how that was reached
without a Mac. Worth remembering: the evidence that convinced a maintainer here
was never the green tick.

Two branches also live in the fork without a PR — `utest_fix_msvc_push_pragma`
and `fix_null_compare`. **Both are @sheredom's**, mirrored by the fork, not ours;
all ten commits on the first carry his name and the second is his own
[#155](https://github.com/sheredom/utest.h/pull/155). Nothing to open there.

A follow-up comment on #109 reports the AIX results and answers both of
@sheredom's questions there; #112 is offered explicitly as a continuation rather
than a replacement.

### Bringing #112 and #113 up to date, 2026-08-19

| Branch | Head | What was done | Pushed |
|---|---|---|---|
| `subprocess.h:main` | `76cd934` | fast-forwarded to upstream | — |
| `subprocess.h:aix-port` (#112) | `1695099` | `main` merged in, then the `fcntl` block removed | **yes** |
| `subprocess.h:ci-portability` (#113) | `227d073` | `main` merged in, `portability.yml` itself untouched | **yes** |
| `subprocess.h:refresh-vendored-utest` | `7ef8ab5` | `test/utest.h` → `utest.h@b6230bc`; later cherry-picked onto #113 rather than sent separately | never pushed |
| `utest.h:main` | `b6230bc` | fast-forwarded to upstream | — |

Both merges applied with **exit code 0 and zero conflicts**.

**Merged, not rebased, and that was deliberate.** @sheredom asked to *"rebase and
repush"*. A rebase onto `76cd934` conflicts on the first commit, `e6cec1b` — and
the conflict is the lesser problem, because rebasing *rewrites* that commit.
`e6cec1b` is @mehendarkarprajwal's, carried unchanged so that #112 reads as a
continuation of #109 rather than a replacement. The merge keeps it an ancestor,
verified with `git merge-base --is-ancestor`. The deviation is stated openly in
the PR comment rather than done quietly.

**#112 came back 24/24 green.** The two macOS jobs that were red for days went
green on their own, because #118 removed their cause — the outcome that had been
predicted, arriving without any action.

For #113 the body was rewritten and the **comment deliberately held back**: the
draft asserted `windows-x86` is green, and the Portability run had not finished.
The body edit alone sends no notification, so the comment had to follow with the
measured numbers rather than announce them in advance. It did, and the number
held.

**The rebase-versus-merge call turned out not to matter for the artefact.**
@sheredom squash-merged #112, so `e6cec1b` is not a commit on `main` at all;
what survived is the trailer, `Co-authored-by: mehendarkarprajwal`. A rebase
would very likely have produced the same trailer, since rebasing preserves the
author. The merge earned its keep during review, where the PR showed the commit
untouched, and nothing beyond that. Worth recording as it happened rather than
as vindication.

He closed [#109](https://github.com/sheredom/subprocess.h/pull/109) a minute
after asking for the update — *"Closing in favour of #112"* — which, had the
rebase happened, would have left no record of that contribution anywhere.

**The `fcntl` removal is exactly the 8 lines of `eadfac5`**, confirmed by
`git blame` before touching anything — the `> STDERR_FILENO` guards below it
look equally redundant now but come from `632bbed`, the core AIX work, and were
left alone. `eadfac5` also added a regression test to `test/test.c`; that
**stays**. #118 promised to drop the FD_CLOEXEC clearing, not the coverage, and
the test still earns its place:

| fd-zero test, fork path | result |
|---|---|
| block dropped, `fds_above_std` present | passes |
| block dropped, `fds_above_std` neutralised in place | **fails**, `exec closed the child's stdin` |

Without that second row the first proves nothing. Full suite under the project's
own `-Werror` flags: **444/444** with `posix_spawn` and 444/444 with
`-DSUBPROCESS_SPAWN_VIA_FORK=1`, which is the path the block lived in.

**The vendored filter defect, isolated within one branch.** Same `aix-port`
checkout, only `test/utest.h` swapped:

| filter | old vendored copy | refreshed |
|---|---|---|
| `*fd_zero_was_free` | 1 | 1 |
| `*fd_zero_was_free*` | **0** | 1 |
| `*keeps_pipe_ends*` | 1 | 1 |

The defect is **name-dependent**, which is why it survived so long and why the
third row matters: a filter picked at random makes a perfectly convincing
control that proves nothing. `*keeps_pipe_ends*` behaves identically either way.

### Open items that are not a pull request

**The OpenBSD branch has no version gate, and one day it will need one.**
`catap` raised this on #113 (2026-08-15), pointing at the
[openbsd-tech thread](https://marc.info/?l=openbsd-tech&m=178601904627458&w=2)
where `posix_spawn_file_actions_addchdir` is proposed — **not committed there
yet**, possibly in release 8.0. Answered on the PR the same day, after checking
rather than taking it on trust.

**Check it in CVS, not on GitHub.** `openbsd/src` on GitHub is a mirror, and
its code search needs an account. The authoritative source is the project's own
cvsweb, which needs neither:

| file | url |
|---|---|
| `include/spawn.h` | <https://cvsweb.openbsd.org/src/include/spawn.h> |
| `lib/libc/gen/posix_spawn.c` | <https://cvsweb.openbsd.org/src/lib/libc/gen/posix_spawn.c> |

**Read the release column, not just the file.** cvsweb lists, per revision,
which releases carry it — and that is the number the gate needs. As of
2026-08-22:

```
include/spawn.h          rev 1.3   2015-05-20   releases 58 … 79
lib/libc/gen/posix_spawn.c  rev 1.10  2019-06-28   releases 66 … 79
```

79 is 7.9, the current release. So both files sit in releases up to and
including today's in a revision that has not changed since 2015 and 2019
respectively, and no log message mentions `addchdir` at any point.

That is a stronger statement than grepping the tree. A grep says "not present
now"; the revision history says **never added**, without depending on a mirror
being awake. When a new revision appears whose log message does mention
`addchdir`, its release column gives the version to gate against directly.

The gate itself is already researched, so it is a one-liner when the time comes.
`<sys/param.h>` carries **both** forms:

```c
#define OpenBSD	202610		/* OpenBSD version (year & month). */
#define OpenBSD8_0 1		/* OpenBSD 8.0 */
```

The numeric `OpenBSD` (YYYYMM) is the one to compare against, mirroring
`__NetBSD_Version__`. Note that `OpenBSD8_0` is defined on **-current**, before
8.0 ships — it means "8.0-current or later", not "8.0 released", so it is the
weaker of the two for a capability gate. Today
`SUBPROCESS_SPAWN_VIA_FORK` claims *every* OpenBSD, which is correct but heavier
than necessary once the function exists — the fix would mirror the NetBSD gate
(`__NetBSD_Version__ >= 1000000000`) using `OpenBSD` from `<sys/param.h>`. **Not
actionable until a release actually carries it**; gating against a version that
does not exist yet is a guess. Answered on the PR at the time; **this is the one
item from the whole series that is still genuinely open**, and it is waiting on
OpenBSD, not on us.

**Cleanup — the code half is done, the branches are not.**

The one code item, #112's now-redundant `fcntl` block, was removed in `1695099`
and is on `main`. Everything left is branch housekeeping, all of it now
unblocked:

| Branches | Where |
|---|---|
| `aix-port`, `ci-portability`, `fix-low-fd-pipe-ends`, `fix-win32-procthreadattributelist` | subprocess.h, fork + local |
| `refresh-vendored-utest` | subprocess.h, local only — never pushed, superseded by the cherry-pick into #113 |
| `fix-32bit-builds`, `aix-support`, `fix-filter-trailing-wildcard`, `tmp-both`, `harden-format-macros`, `portability-matrix` | utest.h, fork + local |
| `test-macos-lowfd` + fork PR #1, `test-vendor-control`, `test-vendor-utest-refresh`, `test-portability` | forks only |

Two things to keep in mind when clearing them. **`-D` is required throughout**,
because everything was squash- or rebase-merged and no local branch is an
ancestor of `main`; the content was confirmed present by patch-id in each case,
which is what makes `-D` safe rather than reckless. And the four `test-*`
branches each carry a commit widening a workflow's `push:` trigger — useful for
measuring on a fork, **never** for upstream.

**The `fcntl` block, concretely.** It sat at `subprocess.h:1498-1504` after the
merge:

```c
/* dup2 clears FD_CLOEXEC, except dup2(fd, fd), which is a no-op. A pipe
   end already sitting on 0, 1 or 2 would otherwise stay close-on-exec. */
if ((-1 == fcntl(STDIN_FILENO, F_SETFD, 0)) ||
    (-1 == fcntl(STDOUT_FILENO, F_SETFD, 0)) ||
    (-1 == fcntl(STDERR_FILENO, F_SETFD, 0))) {
  goto child_failed;
}
```

It is dead because `subprocess_fds_above_std`, which #118 put on `main`, is
applied on **every** pipe-creation return path — both the `pipe2` path and the
`pipe` fallback. No pipe end can still be sitting on 0, 1 or 2 by the time the
child reaches `dup2`, so there is nothing left for this block to rescue. Checked
in the merged `main` rather than assumed from #118's description.

The condition really was "**#118 merged**", not "#118 decided". Had it been
closed, this block would have had to stay — it was then the fork path's only
guard against the `dup2(fd, fd)` no-op.

### #113 is red, and that is the point

Every failing job was a real defect on `main` at the time, each fixed by a PR
that was then open. The *today* column is the state as of the merge; all of them
have since gone green:

| Job | fails because | fixed by | today |
|---|---|---|---|
| `linux-32-bit`, `linux armv7` | `utest.h` 32-bit: oversized constants and the `ll` modifier | utest.h#188 | merged; green here once `test/utest.h` was re-vendored |
| `netbsd 10.1` | `PRIu64` undefined — NetBSD gates the `PRI` macros for pre-C++11 | utest.h#188 | merged; same |
| `netbsd 9.4` | no `addchdir` under either spelling before 10.0; #102's guard has no version test | #112 | merged `0dccaa9` |
| `openbsd 7.9` | no `addchdir` at all, but the probe's `#else` claims otherwise | #112 | merged `0dccaa9` |
| `linux ppc64le`, `linux riscv64` | `subprocess_fail_divzero` asserts a trap that does not happen | #112 | merged `0dccaa9` |
| `windows-x86` | `subprocess_size_t` is not `SIZE_T` on Win32 — **added by #116 on 2026-08-14**, not present when this PR was opened | #117 | merged `76cd934`; measured green on `227d073` |

**Both defects in the PR text were fixed on 2026-08-19.** The description used
to promise *"Once #112 and sheredom/utest.h#188 land, all of them go green"*.
#188 landed and three of those jobs stayed red, because the fix reaches this
repository only through the vendored `test/utest.h`. The claim was not wrong in
substance but incomplete in a way that reads as wrong — on the load-bearing
argument of the PR, at the moment a reader was most likely to check it.

The table also **never listed `windows-x86`**: it was written before #116
introduced that defect, and the connection lived on #117 instead. So the row
carrying this PR's strongest evidence — a defect the workflow caught in the
maintainer's own repository within a day — was missing from the PR that made the
case for the workflow. Both are now in the description.

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

### #113 ended green, and the path there is the useful part

Final run on `8d78bdb`: **17 of 17 portability jobs green**, `cmake.yml` 24/24.
Eight red jobs went to none in four steps, and only the last two were work on
this PR:

| Jobs | what fixed them |
|---|---|
| `windows-x86` | #117 merged |
| `netbsd 9.4`, `openbsd 7.9`, `ppc64le`, `riscv64` | #112 merged |
| `linux-32-bit`, `linux armv7` | refreshing the vendored `test/utest.h` |
| `netbsd 9.4`, `netbsd 10.1` | the two fixes below, which the refresh exposed |

The first two rows needed nothing from us — the fixes reached `main` and the
jobs turned by themselves. That is the workflow doing what it was built for,
and it is also the cleanest possible confirmation that the red-job table in the
PR body had attributed each failure correctly.


Measured on `227d073`, run `32194280591`:

| Job | before | after |
|---|---|---|
| `windows-x86` | fail | **pass** |
| `linux-32-bit`, `linux armv7`, `netbsd 10.1` | fail | fail — vendored `test/utest.h` |
| `netbsd 9.4`, `openbsd 7.9`, `linux ppc64le`, `linux riscv64` | fail | fail — #112 |
| the 9 green jobs | pass | pass |

Nothing in this PR changed; `portability.yml` is byte-identical, checked before
pushing. #117 landing on `main` was the entire cause. That is the workflow doing
exactly what it was built for, twice over: it found the defect and it recorded
the repair.

The remaining seven split cleanly — four wait on #112, three wait on a vendored
header refresh that has nothing to do with either PR.

### Two defects #113 found in `main` on its last lap

Both surfaced only once earlier fixes had landed and the NetBSD jobs got
*further* than ever before. Neither was reachable while they still died at the
link stage.

**#112 silently suppressed the `PRI` macros on NetBSD.** It added
`#include <sys/param.h>` for `__NetBSD_Version__`. NetBSD's `sys/param.h:104`
includes `<sys/inttypes.h>`, which is where the chain closes:

```c
#ifndef _SYS_INTTYPES_H_
#define _SYS_INTTYPES_H_
#if !defined(__cplusplus) || defined(__STDC_FORMAT_MACROS) || (__cplusplus >= 201103L)
#include <machine/int_fmtio.h>   /* PRIu64 lives here */
#endif
#endif
```

One-shot include guard: whichever header reaches it first settles the question
for the whole translation unit, and a `#define` afterwards cannot reopen it.
`test98.cpp` includes `subprocess.h` before `utest.h`, so in C++98 utest.h's own
`__STDC_FORMAT_MACROS` arrived too late and `PRIu64` was simply gone.

Read out of the NetBSD source tree rather than reasoned about. The reason it had
never bitten: subprocess.h's own `<inttypes.h>` sits inside a `_WIN32` block and
is **never reached** on NetBSD, so before #112 nothing pulled that family in at
all. The fix sets `__STDC_FORMAT_MACROS` before `<sys/param.h>`, restoring what
consumers had — this reached beyond the test suite, since anything including
subprocess.h first in C++98 lost the macros too, llama.cpp included.

**#105's `-std=c++2a` fallback had no third rung.** It assumed a compiler
without `-std=c++20` accepts `-std=c++2a` — true from GCC 8, false below.
NetBSD 9.4 ships GCC 7.5.0 and accepts neither, so the fallback handed it a flag
it rejects. Measured in a `gcc:7` container, with the control: both spellings
rejected, and the file compiles clean at the default `gnu++14` under the
project's own flags. `test20.cpp` now drops the standard flag entirely in that
case, matching what already happens for `test11.c` without `c_std_11` and on
MSVC.

The honest cost: on such a compiler the suite named `cpp20` runs at C++14. That
is the same compromise MSVC already had, and it is stated in the commit rather
than glossed.

### The utest.h merge unblocks three of #113's red jobs

`linux-32-bit`, `linux armv7` and `netbsd 10.1` do not fail in `subprocess.h`.
They fail inside `test/utest.h`, the **vendored** copy — confirmed at the log
level rather than by matching PR titles, run `31836045128`:

```
test/utest.h:1420:3: error: integer constant is too large for 'unsigned long'   (armv7, linux-32-bit)
test/utest.h:1705:38: error: expected ')' before 'PRIu64'                       (netbsd 10.1)
```

Those are exactly the lines utest.h#188 rewrites, and #188 is now on utest.h
`main`. The vendored copy here is stale by more than that one PR: `85156` bytes
against upstream's `89875`, five commits behind.

**And it is a pristine snapshot**, which is the fact that makes this cheap.
Its blob `5341a59` is byte-identical to utest.h at `f4610ee` (2026-07-20,
*Suppress intentional global constructor warning*) — checked by resolving the
blob inside the utest.h repository, not by eyeballing a diff. Nothing local was
ever carved into it, so there is nothing to preserve across the refresh: **the
fix is a file replacement, not a code change.**

**Measured on 2026-08-18, with a control.** Two branches were pushed to the
fork, differing by exactly one file — `git diff` between them is `test/utest.h`
alone, 118+/25-:

| branch | `test/utest.h` |
|---|---|
| `test-vendor-control` | as vendored today (`f4610ee`) |
| `test-vendor-utest-refresh` | upstream `main` (`8db1cbd`) |

Both sit on `ci-portability` **merged with upstream `main` `0d76f78`**, because
`ci-portability` is two commits behind and GitHub tests the merge ref, not the
branch. Skipping that would have compared against a different codebase than the
one #113's red jobs come from — `windows-x86` only went red through #116.

| Job | control | refreshed |
|---|---|---|
| `linux-32-bit` | fail | **pass** |
| `linux armv7` | fail | **pass** |
| `netbsd 10.1` | fail | **pass** |
| `netbsd 9.4`, `openbsd 7.9` | fail | fail |
| `linux ppc64le`, `linux riscv64` | fail | fail |
| `windows-x86` | fail | fail |
| the other 9 portability jobs | pass | pass |
| `cmake.yml`, 24 jobs | pass | pass |

**The control reproduced all eight failures**, job for job, identically to
upstream run `31836045128`. Without that the refreshed run would prove nothing —
a matrix that goes green can do so because the build stopped happening.

Three jobs flipped, and they built and ran the suite rather than skipping it:
`ctest` reports `100% tests passed` on both `linux-32-bit` and `netbsd 10.1`.
(The per-test counts are absent from the logs only because the workflow uses
`--output-on-failure`, which stays silent on success.)

The five that stayed red fail for **unchanged** reasons, checked in the logs
rather than assumed: `addchdir` missing on NetBSD 9.4 and OpenBSD 7.9, `C2733`/
`C2664` on `windows-x86`, `create_subprocess_fail_divzero` on ppc64le and
riscv64. The refresh moved nothing it should not have moved.

**The regression question is answered too.** The refresh carries five commits
besides #188 — `Restore caller MSVC warning state`, `Test custom-message
assertion variants`, `ASSERT_MEMEQ_MSG`, `Suppress intentional global
constructor warning`, and utest.h's own `subprocess.h` re-vendor. None disturbed
anything: `cmake.yml` is 24/24 on both branches and the nine already-green
portability jobs stayed green.

**#190 merged mid-measurement, which forced a re-run rather than an edit.** The
first pass vendored `3097e2c`; utest.h#190 landed as `8db1cbd` forty minutes
later, and it **rewrites the whole test-filter matcher**. The `foreign-arch`
jobs run `--filter=*divzero`, so that is not a change one may reason past —
they could silently have selected a different set. Re-vendored to `8db1cbd` and
re-run:

| | `@3097e2c` | `@8db1cbd` |
|---|---|---|
| `s390x`, `armv7` | 9 cases, 9 passed | 9 cases, 9 passed |
| `ppc64le`, `riscv64` | 9 cases, 0 passed | 9 cases, 0 passed |
| portability totals | 12 pass / 5 fail | 12 pass / 5 fail |
| `cmake.yml` | 24/24 | 24/24 |

**Nine selected either way** — the new matcher treats `*divzero` identically.
The result therefore holds for current `main`, which is what a PR would vendor,
and the counts are the evidence rather than the identical pass/fail totals: a
filter selecting *fewer* tests would also have shown 12 green.

**Where it went, in the end, was into #113 after all.** The plan had been a
separate one-file PR, on the argument that #113 stands or falls on *"every red
job is a real defect"* and a vendor bump mixes maintenance into that. What
changed it was @sheredom asking to *"see if we can't get it green"* — leaving
#113 red to protect a tidy scope would have been the wrong answer to a direct
request. Cherry-picked in, and two further fixes followed it for the same
reason.

**AIX is no longer a blocker either** — utest.h#189 was merged on 2026-08-18 —
though no CI job here runs on AIX, so it never touched this measurement.

The `test-` branches are disposable and carry one commit that must never
reach upstream: `test-**` added to both workflows' `push:` trigger, so the fork
runs the matrix without a pull request. Delete them once the decision above is
made.


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

**Follow-up, done on 2026-08-19:** #112's `fcntl` fix became redundant, since
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

## What each merged PR actually contains

Upstream `main` is at **`8a4715c`**. The summary table is at the top of this
file; this section keeps the detail.

| PR | Merged | Commit | Content |
|---|---|---|---|
| [#117](https://github.com/sheredom/subprocess.h/pull/117) | 2026-08-18 | `76cd934` | `ProcThreadAttributeList` declared with pointer-width sizes, fixing the 32-bit Windows build #116 broke. **Verbatim**, patch-id identical. +12/−4 |
| [#118](https://github.com/sheredom/subprocess.h/pull/118) | 2026-08-18 | `6f54d85` | `subprocess_fds_above_std` keeps pipe ends off 0, 1 and 2 on both pipe-creation paths. **Verbatim**. +97/−2 |
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
`#if defined(_AIX)`.

**Closed on 2026-08-18 at 19:43** — one minute after the maintainer asked #112 to
be brought up to date:

> Closing in favour of #112

That settles the question #112 was built around, and it raises the stakes on the
decision not to rebase. `e6cec1b` is now the **only** surviving record of
@mehendarkarprajwal's contribution: their own PR is closed, so if #112 rewrote
that commit the authorship would vanish from the project entirely. Merging keeps
it an ancestor. #112 is now the sole AIX path.

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
