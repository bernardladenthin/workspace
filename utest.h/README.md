# utest.h

Contributions to [sheredom/utest.h](https://github.com/sheredom/utest.h), the
single-header test framework that [`../subprocess.h/`](../subprocess.h/) vendors.
Everything here surfaced through subprocess.h work — four defects while porting
it to AIX, the filter defect while writing a regression test for something else
entirely — but none of it is specific to that work.

> **Scope note.** utest.h is a **topic** folder like [`../AIX/`](../AIX/), not a
> tracked repository. No entry in [`../crossrepostatus.md`](../crossrepostatus.md).

## Pull requests

| PR | Title | Size | State |
|---|---|---|---|
| [#188](https://github.com/sheredom/utest.h/pull/188) | Fix 32-bit builds under `-Wpedantic` | +45/-17 | **merged 2026-08-17**, `3097e2c` |
| [#190](https://github.com/sheredom/utest.h/pull/190) | Fix the test filter dropping tests it should run | +68/-46 | **merged 2026-08-18**, `8db1cbd` |
| [#189](https://github.com/sheredom/utest.h/pull/189) | Support AIX in `utest_ns()` | +7 | **merged 2026-08-18**, `b6230bc` |
| [#191](https://github.com/sheredom/utest.h/pull/191) | Do not assume the `PRI` macros are still available | +62/-5 | **merged 2026-08-19**, `59f3f13` |
| [#192](https://github.com/sheredom/utest.h/pull/192) | Add a portability workflow beside the existing matrix | +569/-35 | **merged 2026-08-21**, `de17c92` |

**All five are merged. Nothing is open here.** #189 went in at 19:44:57 on
2026-08-18, three minutes after subprocess.h#117 and #118 — the maintainer
cleared the queue in one sitting after eight days of silence. Every one landed
**verbatim**, patch-id identical in each case.

That check was not ceremonial for #190 and #189: both still sat on `ebb62ed`,
from before #188, so `git diff <head> <main>` is *not* empty for either and a
tree diff would have suggested edits that never happened. The patch-id is what
answers the question.

**#192 is the first one whose CI actually ran before the merge.** The fork gate
that had held every earlier PR on `conclusion: action_required` lifted once #191
was merged — GitHub stops gating once a contributor has something in. So #188
through #191 were all merged without a single CI run on the head that landed,
and #192 arrived with Portability and CMake both green.

Since #192, **this repository runs the portability matrix on `main`**, and it is
green there.

The fork branches `fix-32bit-builds`, `fix-filter-trailing-wildcard`,
`aix-support`, `harden-format-macros`, `portability-matrix` and
`test-portability` have all served their purpose.

**#190 was merged verbatim too, and checking that took one step more than it
looks.** `git diff ec68e74 8db1cbd` is *not* empty — 45+/17- separate them —
because the PR still sat on `ebb62ed`, from before #188. The comparison that
answers the question is the patch itself, and both sides give patch-id
`1a6b7a13`: the rewrite landed unchanged and rebased cleanly onto #188. A plain
tree diff would have suggested an edit that never happened.

**And this one drew a reply**, three seconds before the merge:

> Great find!

The first substantive word from the maintainer in the whole series. Worth
recording next to the two silent merges rather than reading anything into
either — #188 got no comment and was equally accepted.

**CI here is gated.** Unlike subprocess.h, fork PRs in `sheredom/utest.h` land
on `conclusion: action_required` and wait for the maintainer to approve the
workflow. **All three went in without their CI ever having run** on the merged
head — the gate was never opened for any of them. Whatever convinced the
maintainer here, it was not this repository's CI.

**#188 was merged verbatim, and how it was merged is the part worth keeping.**
Rebase-merged, so all three commits survive on `main` — `d213ceb`, `a0180d1`,
`3097e2c` — and `git diff 6663b21 3097e2c` is empty: nothing was changed on the
way in. No approving review, no comment; the merge is the entire answer.

What moved it was the reply, not the code. The code had been pushed on
2026-08-16 (`6663b21`) and then sat untouched; the thread still read as an
unanswered review until a short *"Done — `PRId64`/`PRIu64` stay the normal
path…"* was posted. #113 had behaved the same way. **With this maintainer a
reworked PR stays invisible until you say so in one paragraph** — now observed
twice, not once.

## 5. The `PRI` macros can be gone before this header is read — `#191`

`__STDC_FORMAT_MACROS` only works if nothing has reached `<inttypes.h>` first.
On NetBSD the macros come from `<sys/inttypes.h>`, which gates them and sits
behind a one-shot include guard, so whichever header arrives first decides for
the whole translation unit. A consumer including its own headers before this one
is enough — and subprocess.h#112 became exactly that consumer, by adding
`<sys/param.h>`, which pulls that file in.

The fix is a **capability test instead of a proxy**: require `PRId64` and
`PRIu64` to actually be defined before using them, and take the existing
`double` fallback otherwise. Include order then stops mattering.
`test/inttypes_include.cpp` covers it the way `stdint_include.c` covers the
`stdint` case.

Verified against a stub `<inttypes.h>` exposing no `PRI` macros: this branch
compiles, `main` gives `error: expected ')' before 'PRIu64'`. **The first
attempt at that control was worthless** — a text substitution matched nothing,
so "it compiles without the hardening" came from an unmodified header. Redone
via `git show b6230bc:utest.h`, where it bit.

The PR carried a second, unrelated commit: `test20.cpp` was compiled with
`-std=c++20` unconditionally, which GCC 8 and clang 9 reject in favour of
`-std=c++2a` and GCC 7 rejects outright. It was offered for splitting off; the
maintainer kept it.

## The portability matrix — `#192`

Mirrors subprocess.h's, added beside `cmake.yml`. Measured on a fork before
opening: **14 of 14 green**, including the four emulated architectures running
the **full** suite. subprocess.h needs `--filter=*divzero` there because
qemu-user does not propagate the errno a failed `posix_spawn` reports; utest.h
only spawns on the success path, so it is unaffected — checked rather than
assumed, since that was the expected failure.

`netbsd 9.4` passing is the row worth keeping: GCC 7.5.0, the exact combination
that had broken subprocess.h twice. It works only because #191 had landed.

**Two fixes it needed first.** `main` did not build against modern glibc: the
vendored `subprocess.h` calls `pipe2` and
`posix_spawn_file_actions_addchdir_np`, which glibc declares only under
`_GNU_SOURCE`, and most units here compile at strict `-std=`. `cmake.yml` never
saw it because it pins gcc-10 and clang and excludes the default compiler on
Ubuntu. And the vendored copy was `subprocess.h@8671cee`, twelve commits behind;
it is a pristine snapshot again now.

**The one review comment in the whole series worth quoting**, on the first form
of that `_GNU_SOURCE` fix:

> Hm not sure about this. This means we aren't ever testing with `_GNU_SOURCE`
> not defined on Linux. Seems sketchy 🤔

He was right, and the asymmetry is the point: in subprocess.h a directory-wide
define is harmless because subprocess.h *is* the library under test. Here it is
a test helper, and defining it globally would have meant utest.h itself was
never compiled without it. Narrowed to `main.c`, the only unit that includes
subprocess.h — confirmed in the generated `flags.make`, where the define appears
once, on `main.c.o`, and nowhere else.

## This repository's CI cannot see its own 32-bit defect

Worth knowing before reading anything into a green run: utest.h builds with
`-Wall -Wextra -Werror` and **no `-Wpedantic`**. The oversized constants and
the `ll` modifier therefore never trip it, at any word size. The defect
`#188` fixes surfaces in **subprocess.h**, which vendors this header and does
compile its C++ files with `-Wpedantic` at fixed standards.

Consequence for measuring: to check whether a change to these constants still
fixes ILP32, build *subprocess.h's* suite at `-m32` with this header swapped
in. Adding `-Wpedantic` to utest.h's own build instead just lights up unrelated
pre-existing diagnostics in its `gnu89` sources — all three revisions then fail
for the same wrong reason, which was the first thing that happened when trying
it.

## The four defects

### 1. No AIX branch — `#189`

`utest_ns()` enumerates Windows, Apple, Linux, FreeBSD, OpenBSD, NetBSD,
DragonFly, Solaris, Haiku and Emscripten. `_AIX` appears nowhere, so AIX stops at
`#error Unsupported platform!`.

**Do not fix it by adding `_AIX` to the Linux/BSD list.** That branch calls
`timespec_get(&ts, TIME_UTC)` when `__STDC_VERSION__ >= 201112L`, and AIX 7.2
does not have it — from `/usr/include/time.h`, `clock_gettime` is declared at
line 238 while `timespec_get` and `TIME_UTC` do not appear at all. Adding `_AIX`
there would compile under C89 and C99 and fail under C11, which is the kind of
defect that surfaces months later.

### 2 and 3. 32-bit — `#188`

Both stem from one fact: `uint64_t` is `unsigned long` on LP64 and
`unsigned long long` on ILP32, and `long long` is not part of C90 or C++98.

```
utest.h:1446: error: integer constant is too large for 'unsigned long' [-Werror=long-long]
utest.h:      error: ISO C++98 does not support the 'll' gnu_printf length modifier
```

The constants `0x7fffffffffffffffu` and `0x7ff0000000000000u` need the wider
type; `UTEST_PRIu64` expands to `PRIu64`, which is `"lu"` on LP64 but `"llu"` on
ILP32.

**The first version** fixed this by building the constants in the target type
and printing *everything* through `double` with `"%.0f"`: integers below 2^53
print exactly — 104 days in nanoseconds — so nothing this framework reports can
be truncated, and the MSVC `"I64d"` special case fell away too. The review
rejected that reach; what shipped is below. **Each fix alone still blocks the
build**, which is why they are one PR.

Alternatives rejected: a `#pragma GCC diagnostic` is compiler-specific;
`"lu"`/`"ld"` with a cast truncates, since 2^32 ns is 4.3 s.

**@sheredom objected to this on 2026-08-14**, and he is right in principle:

> Eh this is trying to print integers with floats? Won't large integer values
> that are converted to doubles not be represented correctly and thus print
> wrong?

The answer given concedes the principle and argues the bound: everything
printed through these macros is a test count, a test index or a nanosecond
duration; `double` is exact below 2^53, which is ~104 days for one test case;
and the obvious alternative breaks after 4.3 seconds. The `PRIu64`-on-NetBSD
argument below is the stronger half, because it removes "just keep `PRIu64`"
as an option entirely.

The reply also **offers the lossless alternative rather than building it**:
formatting the 64-bit value into a small buffer by hand and printing it with
`%s` — no length modifier, so still C90/C++98 clean, no `PRI` dependency, no
precision limit, roughly 15 lines. Deliberately offered as a choice. Arriving
with a finished rewrite reads as working around the review rather than
answering it, and this maintainer had already asked three times for *less*
code.

**He chose neither, and his answer is better than both:**

> I think I'd rather you have a fallback for platforms that don't support
> 64-bit integer printing (they are the minority), and keep the code as is
> otherwise.

That inverts the PR. The original changed how *every* target prints in order to
fix a minority; the fallback keeps `PRId64`/`PRIu64` as the normal path and
diverts only where `ll` is genuinely unavailable — ILP32 under C90 or C++98.
Call sites pass integers again, through `UTEST_INT64_ARG`/`UTEST_UINT64_ARG`,
which expand to nothing on the normal path and to a `double` cast on the
fallback, so there is still one call site per message.

**NetBSD then needs no fallback at all.** Defining `__STDC_FORMAT_MACROS` before
`<inttypes.h>` restores the `PRI` macros for C++98, which is exactly what that
header documents. Checked that it draws no `-Wreserved-macro-identifier` under
clang, since it is a reserved identifier.

Re-measured 2026-08-16, clang 18, `-std=gnu++98`: clean under
`-Wreserved-id-macro`, `-Wreserved-macro-identifier` **and** `-Weverything
-Werror` — for the branch and for upstream alike. The negative control is what
makes that worth anything: `#define __MY_RESERVED 1` in the same translation
unit *does* fail, so the flag was live; clang simply whitelists
`__STDC_FORMAT_MACROS`. Upstream wraps its own define in
`#pragma clang diagnostic ignored "-Wreserved-id-macro"`, which is therefore
belt-and-braces — **#188 needs no equivalent**, and the question was worth
settling because #188's CI is gated and has not run since the rework.

### Which branch is live, measured rather than assumed

A fallback that triggers everywhere also builds everywhere, so "it compiles" is
not evidence. `UTEST_PRIu64` is a string literal either way, so comparing it
against `".0f"` at runtime says which arm is active:

| target | branch |
|---|---|
| x86_64, C gnu89/c99 and C++ gnu++98/c++17 | native `"lu"`/`"ld"` |
| i386, C gnu89 and C++ gnu++98 | **fallback** `".0f"` |
| i386, C c99 and C++ c++11 | native `"llu"`/`"lld"` |
| MSVC 19.44, x86 and x64, C and C++ | native `"llu"`/`"lld"` |
| AIX 7.3 POWER10, 32- and 64-bit | native `"llu"` / `"lu"` |

**Two of those rows are corrections, not confirmations.**

`_MSC_VER` had to be named explicitly in the condition. Windows is LLP64, so
`unsigned long` is 32 bits even on x64, and MSVC reports `__cplusplus` as
`199711L` without `/Zc:__cplusplus`. Neither of the other tests recognises it,
and before the fix MSVC took the fallback in **all four** of x86/x64 × C/C++ —
precisely the silent behaviour change the review asked to avoid. Docker cannot
see this; only a local MSVC run did.

AIX was expected to be the fallback case, because GCC defaults to 32-bit there.
It is not — GCC 13 defaults to `-std=gnu17`, so the native path wins. The
fallback is still exercised on AIX, but through subprocess.h's suite, which
compiles some translation units at `-std=gnu89` and `-std=gnu++98`. See
[`../AIX/7.3/`](../AIX/7.3/) for that run.

**A second defect in #188 itself, found by its own CI.** Three macOS jobs were
red the whole time, and not because of the double question: AppleClang compiles
the C++ sources with `-Weverything -Werror`, which includes `-Wold-style-cast`,
and the three C casts this PR introduced trip on it. Fixed by using the
existing `UTEST_CAST`. Reproduced on Linux with plain clang and the project's
own flags — AppleClang is not needed, the diagnostic is the same one.

Read the CI of your own PR before defending its design.

### 4. `PRIu64` undefined on NetBSD in C++98 — also `#188`

Found by CI on [subprocess.h#113](https://github.com/sheredom/subprocess.h/pull/113),
not by us. NetBSD 10.1 fails with `expected ')' before 'PRIu64'` on a 64-bit
machine. From NetBSD's own `sys/inttypes.h`:

```c
#if !defined(__cplusplus) || defined(__STDC_FORMAT_MACROS) || \
    (__cplusplus >= 201103L)
```

The `PRI` macros are only visible in C++ when `__STDC_FORMAT_MACROS` is defined
or the standard is C++11 or later. utest.h includes `<inttypes.h>` without
either, so `test98.cpp` at `-std=gnu++98` loses them. glibc and libc++ stopped
enforcing this years ago, which is why it never showed up on the usual runners.

The header **already defines `__STDC_FORMAT_MACROS`** — and it still fails,
which is the part worth understanding. Upstream's define sits at line 274,
**65 lines after** the file's single `#include <inttypes.h>` at line 209, and
is wrapped in `#if defined(__linux__)`. Two independent reasons it cannot help:
it arrives after the include it would have to precede, and NetBSD never reaches
it. `#188` defines it *before* the include and without the Linux guard.

The reworked `#188` therefore fixes NetBSD **directly**, not as a side effect —
the earlier claim that printing through `double` removed the `PRIu64`
dependency described the *first* version of the PR, which the review replaced.

## Verification

**Which PR fixes what, measured one variant at a time.** Each branch was applied
to upstream `main` on its own and built on real AIX 7.3 / POWER10, so the rows
below state what each PR achieves *alone* rather than what the combination
achieves. #190 is not in this matrix — it is a filter defect, orthogonal to
platform support, and measured separately in its own section:

| utest.h | AIX 64-bit | AIX 32-bit |
|---|---|---|
| upstream `main` | `#error Unsupported platform!` | `#error Unsupported platform!` |
| **`aix-support` (#189) only** | **441 / 441** | oversized constants, `ll` modifier |
| **`fix-32bit-builds` (#188) only** | `#error Unsupported platform!` | `#error Unsupported platform!` |
| both | **441 / 441** | **441 / 441** |

Two things follow, and both matter when reading the PR descriptions:

- **On AIX, #188 alone achieves nothing.** The platform is rejected before the
  32-bit problems are reached, so #189 gates everything there.
- **#189 alone is enough for 64-bit AIX** but not for 32-bit, which is GCC's
  default on that platform.

Away from AIX the two are independent: on i386 Linux, #188 alone takes the build
from failing to 441 / 441, because nothing there needs a platform branch.

**Re-measured 2026-08-16 on the same instance**, after the review rework and
with subprocess.h at `eadfac5` rather than `27fe772`:

| utest.h | word size | result |
|---|---|---|
| #189 + reworked #188 | 32-bit | **443 / 443** |
| #189 alone | 32-bit | build fails — the control still bites |
| #189 + #188 + #190 | 32-bit | **443 / 443** |
| #189 + #188 + #190 | 64-bit | **443 / 443** |

443 rather than 441 because subprocess.h has grown two tests since, one of them
the fd-0 regression test — and AIX takes the fork path natively, so this is the
only place it runs unforced. Details in [`../AIX/7.3/`](../AIX/7.3/).

**The merge of #188 on 2026-08-17 turned both matrices into history**, and that
is worth being explicit about rather than quietly leaving them to be misread.
Every row above was measured against a `main` that did not yet contain #188, so
"#189 alone" meant *#189 without the 32-bit fixes*. On current `main` it no
longer can: #188 is the base now, and #189 alone should therefore reach 443 /
443 at **both** word sizes.

**Should — not does.** That has not been measured, and the whole point of the
one-variant-at-a-time matrix was to stop inferring AIX results from reasoning.
It is a fresh run on the POWER10 instance, not a deduction. Until it exists,
#189's own text must not claim a 32-bit AIX result it no longer has evidence
for; the honest form is that #189 is now the *only* remaining blocker on AIX,
which is a weaker and true statement.

Where nothing was broken to begin with, nothing changed:

| Target | before | after |
|---|---|---|
| x86_64 Linux, glibc and musl | 441 / 441 | 441 / 441 |
| Windows MSVC 19.44, x86 and x64, both CRTs | 387 / 387 | 387 / 387 |
| clang, ASan and UBSan | 441 / 441 | 441 / 441 |
| NetBSD 9.4 and 10.1, OpenBSD 7.9, FreeBSD 14.3 | compile clean (cross) | compile clean |

Test counts come from subprocess.h's suite, which vendors this header.

**A correction worth recording.** The first version of this table, and of #188's
description, listed AIX rows going from "build fails" to 441 / 441 under #188.
That was wrong: those measurements had been taken with **both** fixes applied and
were attributed to one of them. The per-variant matrix above was run specifically
to settle it. Combined results must never be reported against a single change.

## The filter defect — `#190`

Not from the AIX work. It surfaced while writing a regression test in
subprocess.h: `--filter=*<name>*` matched nothing, and the verification script
reported "0 tests" for a test that demonstrably existed.

`utest_should_filter_test` gets two things wrong, and both fail the same way —
the test is silently skipped and nothing is reported. A filter that matches
nothing looks exactly like a filter that matched and passed.

**A trailing wildcard never matches the empty remainder.** Once the name is
exhausted, a `*` still left in the filter is treated as a mismatch instead of
standing for nothing. In two places: when the inner wildcard loop runs out of
name, and when the outer loop does.

```
--filter=*bar    runs foo.bar
--filter=*ba*    runs foo.bar
--filter=*bar*   does not
```

**A wildcard cannot give characters back.** On a mismatch the filter position
resets to the wildcard but the name position does not, so the retry resumes
partway through the name rather than one character on from where the attempt
began. Not an edge case: `--filter=*o.b*` does not match `foo.bar`.

Measured over 21 filter/name pairs: the shipped implementation answers **6
wrongly**. A targeted patch for the trailing-wildcard case alone still leaves
3 wrong, which is why #190 replaces the function with the usual iterative glob
match — remember the wildcard and the resume position, and on a mismatch let it
swallow one more character. **0 wrong, and 24 lines shorter than what it
replaces.**

Six tests added, calling the function directly rather than spawning a binary,
so unlike the `utest_cmdline` suite they also run under MinGW. Five of the six
fail against the old implementation — checked, not assumed. Suite goes from
2161 to 2167, all green.

The shape of this one is worth remembering: **the first fix was wrong and the
comparison table is what caught it.** Patching the symptom looked right until
three implementations were run side by side against the same case list.

## One more defect, not submitted

MinGW g++ with `-Wpedantic` does not build utest.h in C++98 at all:

```
utest.h:151: error: ISO C++ prohibits anonymous structs
utest.h:660: error: ISO C++ 1998 does not support 'long long'
utest.h:    error: ISO C++98 does not support the '%lld' ms_printf format
```

Verified pre-existing — the unmodified header fails identically, so `#188` does
not cause it and does not fix it either: those are literal `"%lld"` uses in the
C++ overloads, not the `PRI` macros. Scoping this properly needs more work than
the other four, so it is recorded here rather than reported half-understood.

The C sources compile cleanly under MinGW for both 32- and 64-bit, so
`subprocess.h` itself is unaffected.
