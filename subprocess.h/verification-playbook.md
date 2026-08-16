# Verification playbook

How to test a platform you do not own. Everything here was actually run; the traps listed
are ones that produced a wrong answer first.

## The rule that governs all of it

**Every matrix needs a negative control.** A harness that reports "all green" is worthless
until you have watched it report red for a case you deliberately broke. Two runs in this
project passed for the wrong reason before a control exposed them — see "Traps" below.

Three refinements, each learned by getting it wrong first:

**A control can pass for the wrong reason too.** A path typo made the test binary
unreachable, so the run exited 127 — and the check "exit status is non-zero" went green
while nothing had executed. Assert on what the run *said*, not only on how it ended.

**Verify the control's premise before trusting its verdict.** A control built on
`-DSUBPROCESS_HAVE_CWD=0` expected the test count to drop, and reported a false red when it
did not. The suite substitutes `subprocess_cwd_not_supported` through an `#else`
(`test_shared.h:1176`), so the count is deliberately invariant and only the test *names*
move. The trap the playbook already recorded — 423 instead of 432 — came from an older
header where that `#else` did not exist.

**Test the merge, not the branch.** A `pull_request` run builds `refs/pull/N/merge`, and
`mergeable: MERGEABLE` only means git found no textual conflict. Two upstream commits landed
under #112 mid-review and produced a defect that neither side had alone, through a clean
merge, with the suite green. Build the merge locally in a scratch clone — the working tree
stays untouched and the result is the thing CI will actually compile.

## Proving a change touched only comments

Reviewers ask for comment trimming often enough that this is worth automating.
**Grepping the patch does not work**: the continuation lines of a block comment
are plain indented text, and no pattern separates them from code. A first
attempt reported "non-comment changes" for a diff that was pure prose.

Ask the compiler instead — strip comments from both revisions and diff the
result:

```sh
gcc -fpreprocessed -dD -E -P -x c old.h | sed '/^$/d' > old.stripped
gcc -fpreprocessed -dD -E -P -x c new.h | sed '/^$/d' > new.stripped
diff -q old.stripped new.stripped
```

`-fpreprocessed` keeps directives and macros intact but drops comments. **`-P`
is not optional**: without it the output carries `# 129 "file"` linemarkers,
which differ on the filename alone and on every line number the edit shifted,
so the diff is never empty.

Used on the #112 comment trimming: 1563 lines of code identical either side.
The same tool doubles as a precise diff viewer when a change *is* meant to
touch code — it showed the `SUBPROCESS_EXEC_FAILURE_STATUS` removal as exactly
two changes and nothing else.

## Getting sources onto a Unix box from Windows

Two traps, both about line endings, and the second one hides the first.

**`git archive` applies the `core.autocrlf` filter.** A tarball built on Windows
left with 2151 CR bytes in `subprocess.h` even though git stores LF. Reaching for
`git archive` specifically to avoid the working tree does not help.

**Git Bash cannot verify it.** MSYS translates in text mode, so `grep -c $'\r'`
reported ~1900 CRs in files that had none — and reported the same count after
`tr -d '\r'` had run over them. Both the stripping and the check belong in a
Linux container, counting CR *bytes*:

```sh
tr -cd '\r' < file | wc -c
```

The headers in that episode were clean the whole time; only the archive was not.
Time spent "fixing" the wrong artefact is the cost of trusting the checker.

## Compiler defaults decide more than the platform does

Two probes in one week selected the wrong branch because the *language dialect*,
not the operating system, drove the condition:

- **AIX.** GCC defaults to 32-bit there, so a probe keyed on word size was
  expected to take the ILP32 path. It did not: GCC 13 also defaults to
  `-std=gnu17`, so `__STDC_VERSION__` is modern and the C99-and-newer arm wins.
- **MSVC.** Windows is LLP64, so `unsigned long` is 32 bits even on x64, and MSVC
  reports `__cplusplus` as `199711L` unless `/Zc:__cplusplus` is passed. A
  condition written in terms of word size and language version misses it twice
  over and silently selects the wrong arm on every Windows build.

Ask a probe which branch it took, on the machine, rather than deriving it. When
the branches differ in a string literal, `strcmp` at runtime answers it in one
line; when they do not, `cl /EP` or `gcc -E` shows the expansion without needing
to compile or link anything.

## 32-bit Windows, locally

Nothing exotic is needed and it is the only way to see a whole class of defect:
`cmake.yml` builds Windows x64 only, so anything that is wrong on Win32 alone
is invisible to it.

```
cmake -S test -B build -A Win32
cmake --build build --config RelWithDebInfo
cmake --build build --config RelWithDebInfo --target RUN_TESTS
```

VS Build Tools ship their own cmake, found via `vswhere`; no full Visual Studio
install is required. This reproduced #116's break exactly — same four
diagnostics, same lines as the CI log — before anything was changed, and
confirmed the fix afterwards on both `-A Win32` and `-A x64`.

**Trap: `unsigned long` and `unsigned int` are distinct types of the same
width.** On Win32 `SIZE_T` is `ULONG_PTR` (`unsigned long`) while `size_t` is
`unsigned int`. In C++ that is enough to reject a redeclaration outright, so
the failure appears at the *declaration*, not at the call. On Win64 the two
coincide and everything compiles.

## Linux, glibc and musl

Plain Docker, one container per libc. Pin the sanitizer probes off, or numbers are not
comparable between runs:

```
-DSUBPROCESS_SAN_{thread,memory,address,undefined}_RUNS=FALSE
```

The project's `test/CMakeLists.txt` probes each sanitizer with `try_run` at configure time,
but the real test runs later in a different process with a fresh ASLR draw. Whether
`subprocess_thread_test` exists at all varied between identical runs under WSL2.

Environments that carry their weight: manylinux2014 (glibc 2.17), AlmaLinux 8 (2.28),
Fedora 30 (2.29), Debian 11 (2.31), Ubuntu 24.04 (2.39), Alpine 3.10 (musl 1.1.22) and
Alpine 3.20 (musl 1.2).

## The probe in isolation, without any platform

Extract the probe block **from the header itself** — never a hand-copied duplicate, or the
test drifts from the code — and drive it with faked platform macros:

```sh
awk '/^\/\* Whether subprocess_create_ex can honour process_cwd/,/^#if defined\(_WIN32\)$/' \
    subprocess.h | head -n -2 > probe_block.h
```

Then one compile per scenario with `/DEXPECTED=<n>` and an `#error` on mismatch. Runs
anywhere, including MSVC on Windows; it is pure preprocessor arithmetic.

**Trap: MSVC `/D` cannot define function-like macros.** Faking `__GLIBC_PREREQ(a,b)` on the
command line yields warning C4067 and a wrong answer. Put the fake in a header and force it
in with `/FI`:

```c
#define __GLIBC__ 2
#define __GLIBC_MINOR__ 24
#define __GLIBC_PREREQ(maj, min) \
  ((__GLIBC__ << 16) + __GLIBC_MINOR__ >= ((maj) << 16) + (min))
```

**Trap: get the fake versions right.** Generating `__GLIBC_MINOR__ 223` while meaning glibc
2.23 tests glibc 2.223 — which passes the boundary check for the wrong reason.

## Reaching a macOS runner without owning a Mac

The section below cross-compiles for macOS. That settles header and link
questions and nothing else — **runtime behaviour needs a real Mac**, and some
defects live only there. The cheapest one available is the fork's own CI:

1. Push a branch to your fork. On its own this runs nothing: `cmake.yml`
   triggers on `pull_request: branches: [main]`, not on arbitrary pushes.
2. Open a PR **inside your fork**, base `main`, head your branch. The full
   matrix runs, macOS included, in your repository. Public repos have unmetered
   Actions minutes, so iteration is free and invisible to upstream.
3. Close it when answered.

Give such branches a `test-` prefix and say in the commit message that they are
not for upstream — they will collect combinations that no single PR should
contain.

**That is the point: one branch can carry what five PRs carry separately.** The
run that confirmed the `FD_CLOEXEC` fix — branch `test-macos-lowfd`, fork PR #1
— combined subprocess.h #112, the low-fd fix, both regression tests, and a
`test/utest.h` vendored from three utest.h PRs at once. Nothing upstream has that shape, and the interaction only appears
when all of it is present.

Paid alternatives exist — Scaleway rents Apple silicon by the hour, MacinCloud
and MacStadium rent whole machines, AWS EC2 Mac needs a dedicated host with a
24-hour minimum — but for *a CI answer* rather than an interactive session,
none of them beats a pull request against your own fork.

**Trap: a monitor that cannot report failure.** The poll loop watching that run
used standalone `jq`, which is absent here — `gh --jq` works only because gh
embeds it. Forty iterations produced no output and exited 0, which is
indistinguishable from "still running". Whatever watches a job must be able to
emit on every terminal state, and is worth testing against a known-failing case
before being trusted.

## macOS without a Mac

clang knows every Apple target natively; only the SDK is missing. Extract real SDKs into a
Linux image and point `-isysroot` at them.

SDK tarballs: `alexey-lysiuk/macos-sdk` (up to 15.5) and `phracker/MacOSX-SDKs` (up to 11.3).
These are third-party redistributions of Apple IP — fine for a local check, **not** something
to wire into a public repo's CI.

```
clang -target x86_64-apple-macos10.13 -isysroot /sdk/MacOSX15.5.sdk -fsyntax-only ...
```

This settles header questions from the primary source: what `spawn.h` actually declares,
what `libSystem.B.tbd` actually exports, what the `__API_AVAILABLE` annotation actually says.

**Trap: test in C++.** clang 14 treats an implicit function declaration in C as a warning, so
a broken header compiles green and the failure only appears at link time. C++ has no implicit
declarations and reproduces the real error. For C runs add
`-Werror=implicit-function-declaration`.

**Trap: `-Werror` alone is not the test.** Without `-stdlib=libc++` the run dies on
`-Wstdlibcxx-not-found` and every variant "fails" identically. Promote the single warning you
care about instead: `-Werror=unguarded-availability-new`.

**Trap: do not grep preprocessed output for a macro.** `X_OK` is itself a macro and expands
to `1`, so `clang -E | grep X_OK` can never match — the check silently reports "not compiled
in" for both variants. Ask the object file instead:

```sh
clang -c t.c -o t.o && nm -u t.o | grep -w access
```

An undefined symbol appears if and only if the call was really compiled in.

### Linking Mach-O: osxcross

Needed only to inspect what a finished binary imports. Four attempts to build it, three of
them wasted on avoidable causes:

| Attempt | Failure | Cause |
|---|---|---|
| 1 | ~20 min in `tar cJf` | xz on a 730 MB SDK, for a tarball osxcross unpacks immediately. Use `gzip -1` |
| 2 | libc++ headers unparseable | Debian clang 14 is too old for the 15.5 SDK's libc++ |
| 3 | `cannot find libc++ headers` | the 10.14 and 10.15 SDK tarballs contain **no** libc++ at all — only 15.5 does |
| 4 | success | clang-19 **and** `ln -sf /usr/bin/clang-19 /usr/bin/clang` — the generated `*-clang++` wrapper resolves plain `clang` from `PATH`, so `CC`/`CXX` alone do nothing |

The payoff is one decisive table, via `nm -m`:

| Deployment target | with the fix | without |
|---|---|---|
| 10.13 | no reference to the symbol | `(undefined) weak external _posix_spawn_file_actions_addchdir_np` |
| 10.15 | strong reference | strong reference |

## Exercising a platform's code path without the platform

If a port is guarded by a handful of `#if defined(PLATFORM)` blocks, force them on Linux.
[#109](https://github.com/sheredom/subprocess.h/pull/109) has exactly three, so:

```
cc -D_AIX ...        # AIX fork/exec path
```

builds and runs the full suite on ordinary Linux — **432/432**, with `chdir` verified to take
effect in the child (`/bin/pwd` reports the requested directory) and a missing binary
reporting `subprocess_error_not_found`.

This validates *logic*: descriptor handling, ordering, error propagation, zombie reaping. It
cannot validate platform-specific claims (whether `execvpe` really is undeclared on AIX,
whether AIX's `posix_spawn` behaves as assumed). It is nevertheless the cheapest CI answer
available, and it found a build error in #109 that no amount of AIX access would have
surfaced faster.

**Trap: mixing header and test-suite vintages.** Compiling #109's header (based on
pre-#104 `main`) against the current `test_shared.h` yielded 423 instead of 432 tests. The
9 cwd tests are gated behind `#if SUBPROCESS_HAVE_CWD`, the macro does not exist in that
header, folds to `0` — and precisely the tests that matter for an AIX cwd implementation
were skipped without a word. Add `-DSUBPROCESS_HAVE_CWD=1` when pairing old headers with the
current suite.

## Foreign architectures

Docker's QEMU binfmt covers ppc64le, s390x, riscv64, arm64 out of the box:

```
docker run --platform linux/ppc64le ...
```

Useful for architecture-dependent behaviour — this is how the PowerPC division-by-zero
finding was established. **Not** useful as a stand-in for a foreign OS: it is still Linux and
glibc.

**Trap: the emulator has its own bugs.** Under ppc64le user-mode emulation, glibc's
`posix_spawn` failed to report a missing binary (`rc=0`), while the `fork`/`exec` path in the
same container reported it correctly. That is almost certainly QEMU's incomplete
`CLONE_VM|CLONE_VFORK` handling, not a POWER property — so it must not be quoted as a finding
about the code. Contrast with the division-by-zero result, which reproduces from first
principles and *is* real.

## AIX under QEMU — what actually works

No container can run AIX (containers share the host kernel), but **full system emulation
can**: `qemu-system-ppc64 -machine pseries`. The blocker is media, not emulation.

**It works, but only with one specific AIX release.** TCG emulation on x86 is sufficient —
KVM on POWER hardware is not required. What decides success is the AIX version, not the
QEMU command line: **7.2 TL04 SP02 (2020) boots; 7.2 TL05 SP09 (2024), 7.1 and 7.3 do not.**

The full setup, the version matrix with each failure signature, the four things that turned
out **not** to matter, and how to pass boot arguments live in
[`../AIX/qemu-setup.md`](../AIX/qemu-setup.md) — it is platform knowledge, not
subprocess.h knowledge.

For this project the conclusion is short: getting a compiler onto emulated AIX costs hours,
and `cfarm119` (real POWER8, AIX 7.3, GCC preinstalled, free for free-software developers)
is the faster route. The `-D_AIX` technique above already covers the logic and found the
#109 build error without any of it.

**What an OVA is not.** IBM's AIX OVAs are not disk images. The descriptor declares
`ovf:format=".../power.aix.mksysb"` and the payload is an AIX `backup` archive — the first
bytes carry the `6b ea` magic and the string `by name`. There is no boot record and nothing
`qemu-img` can convert; deployment goes through NIM onto an existing AIX system. Install
media is the only route from a cold start.

## Coverage actually achieved

Everything below was run or compiled for the reworked AIX port, not inferred.

> **Counts are from the 441-test era.** The suite has since grown — 442 after
> upstream #115, 443 with the fd-0 regression test — and the branch has moved on
> to `eadfac5`. The rows still say what was covered; for current numbers see
> [`contributions.md`](contributions.md) and [`../AIX/7.3/`](../AIX/7.3/), where
> the 2026-08-16 round records 443/443 on real POWER10 at both word sizes.

**Full suite, executed:**

| Target | Toolchain | Result |
|---|---|---|
| AIX 7.2 TL04, POWER8, real system | GCC 13.3.0, `-maix64` | **441 / 441** |
| Linux x86_64, glibc | GCC 14 | 441 / 441 |
| Linux x86_64, **musl** | GCC 15.2 (Alpine) | 441 / 441 |
| Linux, **fork path forced** | `-DSUBPROCESS_SPAWN_VIA_FORK=1` | 441 / 441 |
| Linux, **fail-closed forced** | `-DSUBPROCESS_HAVE_CWD=0 -DSUBPROCESS_SPAWN_REPORTS_EXEC_ERRORS=0` | 441 / 441 |
| **Windows x64**, dynamic CRT | MSVC 19.44 | **387 / 387** |
| **Windows x64**, static CRT | MSVC 19.44, `subprocess_mt_test` | 387 / 387 |

The fail-closed row matters more than it looks: those are the paths added by #104 and #106,
which until now had never been *executed* anywhere, only compiled. Forcing both macros to 0 on
a modern system runs them without needing an ancient glibc.

**Sanitizers, clang 14 with `-Weverything -Werror`,** both implementations:

| | plain | ASan | UBSan | MSan | TSan |
|---|---|---|---|---|---|
| `posix_spawn` path | 441 | 441 | 441 | 441 | probe skipped it |
| **fork path** | 441 | 441 | 441 | 441 | probe skipped it |

MSan is the interesting one: the fork path reads the child's `errno` out of a pipe, and an
incomplete read there would surface as an uninitialised value. It does not. TSan is skipped by
the suite's own `try_run` probe (`run=66`) — that mechanism working as designed.

**Compiled, not executed:** NetBSD 9.4 and 10.1, OpenBSD 7.9, FreeBSD 14.3 — clang with a
sysroot built from each vendor's own `comp`/`base` sets; and macOS 10.13 through 14.0 via
osxcross against a real MacOSX15.5 SDK. The macOS run confirms #104's boundary by compilation:
`SUBPROCESS_HAVE_CWD` is 0 at 10.13 and 10.14 and 1 from 10.15, all compiling cleanly.

**Known failure, reproduced twice:** 32-bit builds fail in `utest.h`, not in `subprocess.h`:

```
utest.h:1420: error: integer constant is too large for 'unsigned long' [-Werror=long-long]
utest.h:1705: error: ISO C++98 does not support the 'll' gnu_printf length modifier
```

First seen on AIX with the default 32-bit GCC, then reproduced independently on **i386 Linux**.
That second data point settles it: a portability bug in `utest.h` for 32-bit targets under
`-Wpedantic`, not an AIX quirk. On AIX the workaround is `-maix64`; on i386 there is none short
of fixing `utest.h`.

## CI as a verification channel, and what it caught that we did not

The matrix above was assembled by hand, locally. Putting the same dimensions into
a GitHub workflow — [subprocess.h#113](https://github.com/sheredom/subprocess.h/pull/113) —
found two things the local work had missed, and corrected one thing it had got
wrong.

**Found: NetBSD 10.1 does not build in C++98 at all.** `PRIu64` is undefined
there, on a 64-bit machine, because NetBSD makes the `PRI` macros visible in C++
only with `__STDC_FORMAT_MACROS` or from C++11 on. Our cross-compilation had only
checked the C sources strictly, so it never reached `test98.cpp`. **Lesson: a
cross-compile that skips part of the build is not equivalent to a build.**

**Corrected: armv7 fails for a completely different reason than assumed.** Local
Docker measurements showed armv7 traps on integer division by zero, so the PR
text claimed that job would pass. It fails — armv7 is ILP32 and never reaches its
tests, dying in the build on the same `utest.h` errors as i386. The tempting
explanation, that ARM's `__aeabi_idiv0` might behave differently under glibc than
under musl, was invented to fit a failure whose cause had not been read yet.

**And a design error of our own.** The first version of the foreign-architecture
jobs ran the whole suite and failed on **all four** architectures, s390x included.
The cause was documented in this very playbook — qemu-user does not propagate
`posix_spawn`'s exec errno — and the job was written anyway. A job that can never
be green is worse than no job. They now build everything and run
`--filter=*divzero` only.

The useful residue: `linux s390x` passes while `ppc64le` and `riscv64` fail. Four
red architectures prove nothing; two red and one green is evidence.

## What no amount of tooling reaches

- **Real AIX hardware.** The realistic free route is the GCC Compile Farm, which grants
  accounts to free-software developers; it is interactive, not a CI runner. Note also that
  AIX media is IBM-licensed — relevant if a result is to be quoted in a public PR.
- **PowerPC Darwin (macOS 10.6, the #108 configuration).** No usable cross toolchain exists.
- **macOS SDK 26**, needed to settle whether Apple ships the non-`_np`
  `posix_spawn_file_actions_addchdir`. Mirrors stop at 15.5.

## Housekeeping

This work leaves several GB behind. Measured afterwards: `docker system df` reported ~40.7 GB
live (13.77 images + 15.24 volumes + 11.66 build cache) while `docker_data.vhdx` was
45.89 GB.

- The vhdx **never shrinks on its own**. Pruning frees space inside the VM only; Windows sees
  nothing until the disk is compacted (`wsl --manage docker-desktop --set-sparse true`).
- **`docker volume prune` is the dangerous one.** Volumes show `LINKS 0` whenever no
  container is currently running, which does not mean disposable — a 15.1 GB kernel tree and
  a Maven cache sat in exactly that state here.
- If the CLI hangs, check `wsl -l -v` first. A `Stopped` `docker-desktop` distro makes every
  command block on a daemon that no longer exists; the fix is a restart, not patience.
