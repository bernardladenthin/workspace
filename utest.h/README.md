# utest.h

Contributions to [sheredom/utest.h](https://github.com/sheredom/utest.h), the
single-header test framework that [`../subprocess.h/`](../subprocess.h/) vendors.
Everything here surfaced while porting subprocess.h to AIX; none of it is
specific to that work.

> **Scope note.** utest.h is a **topic** folder like [`../AIX/`](../AIX/), not a
> tracked repository. No entry in [`../crossrepostatus.md`](../crossrepostatus.md).

## Open pull requests

| PR | Title | Size |
|---|---|---|
| [#188](https://github.com/sheredom/utest.h/pull/188) | Fix 32-bit builds under `-Wpedantic` | +22/-18 |
| [#189](https://github.com/sheredom/utest.h/pull/189) | Support AIX in `utest_ns()` | +7 |

Branches `fix-32bit-builds` and `aix-support` in the fork, each one commit off
`main` at `ebb62ed`, independent of one another.

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

Fixed by building the constants in the target type and printing through `double`
with `"%.0f"`. Integers below 2^53 print exactly — 104 days in nanoseconds — so
nothing this framework reports can be truncated, and the MSVC `"I64d"` special
case falls away too. **Each fix alone still blocks the build**, which is why they
are one PR.

Alternatives rejected: a `#pragma GCC diagnostic` is compiler-specific;
`"lu"`/`"ld"` with a cast truncates, since 2^32 ns is 4.3 s.

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

`#188` fixes it as a side effect: printing through `double` removes the
dependency on `PRIu64` entirely.

## Verification

**Which PR fixes what, measured one variant at a time.** Each branch was applied
to upstream `main` on its own and built on real AIX 7.3 / POWER10, so the rows
below state what each PR achieves *alone* rather than what the combination
achieves:

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

## A fifth defect, not submitted

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
