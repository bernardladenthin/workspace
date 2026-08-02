# Contributions and open items

Upstream: [sheredom/subprocess.h](https://github.com/sheredom/subprocess.h), vendored by
llama.cpp as `vendor/sheredom/subprocess.h` and therefore reaching jllama through it.

## Submitted 2026-08-01, awaiting review

Base for all three is `8671cee` (`Fix strict builds with current toolchains (#99)`).

| PR | Branch | Content |
|---|---|---|
| [#104](https://github.com/sheredom/subprocess.h/pull/104) | `fix/addchdir-np-old-glibc` | overridable `SUBPROCESS_HAVE_CWD` probe; `ENOSYS` where `posix_spawn_file_actions_addchdir_np` is missing (glibc < 2.29). 2 commits, head `620ce44`, 3 files, +25 |
| [#105](https://github.com/sheredom/subprocess.h/pull/105) | `fix/test-cxx20-flag-fallback` | `check_cxx_compiler_flag` instead of the CMake feature, falling back to `-std=c++2a`. 1 commit `3370251`, 1 file |
| [#106](https://github.com/sheredom/subprocess.h/pull/106) | `fix/spawn-exec-errors-old-glibc` | `access(X_OK)` pre-check where `posix_spawn` cannot report a failed exec (glibc < 2.24). 1 commit `71c3516`, 1 file, **depends on #104** |

#105 is deliberately based on `main` rather than stacked on #104: it only touches
`test/CMakeLists.txt` and was demonstrated on Ubuntu 20.04 (glibc 2.31 + GCC 8), where the
library builds without #104. #106 could not be separated - every glibc old enough to show
its symptom is also too old to build without #104.

**No CI has run on any of them.** Fork PRs from a first-time contributor need the
maintainer to approve the workflow. Not a signal about the changes: the repo's last commit
is 2026-07-20, and #101 (2026-07-25) and #102 (2026-07-28) are likewise untouched.

## Verification carried out

Container matrix per change, sanitizer probes pinned off for reproducibility, Windows built
natively with MSVC 19.44:

glibc 2.17 / 2.28 / 2.29 / 2.31 / 2.39, musl 1.1.22 and 1.2, GCC 8/9/10/13, clang 18 and 21,
tcc 0.9.27, mingw-w64, MSVC. macOS was not reachable locally; upstream CI covers it.

The single most useful control was **AlmaLinux 8**: glibc 2.28 is the only tested version
that sits *between* the two boundaries (< 2.29, so no `addchdir_np`; >= 2.24, so exec
failures are reported). It is the one environment where the two probes must disagree, and
therefore the only one where a mixed-up version number would show.

## Known limitations, deliberately left in

| Item | Why left alone |
|---|---|
| #106 covers `posix_spawn` only, not `posix_spawnp` | closing it means reimplementing the `PATH` search, including empty entries meaning "current directory" and the `ENOEXEC` shell fallback. Measured on glibc 2.17: explicit path returns `-4`, `PATH` search still returns `0` |
| #106 has a TOCTOU window between `access` and `posix_spawn` | on a platform whose `posix_spawn` cannot report the failure at all, a best-effort check beats none. Gated to those platforms only, so nothing else inherits the race |
| musl older than 1.1.24 still fails to link (#104) | musl exposes no version macro, so it cannot be detected. This is what the override in #104 is for; `-DSUBPROCESS_HAVE_CWD=0` builds cleanly there |

The clean fix for the first two is to drop `posix_spawn` on the affected platforms and use
`fork` + `exec` + a `O_CLOEXEC` pipe carrying `errno` - which is what glibc 2.24 itself
does, closes the race *and* the `posix_spawnp` gap, and would also report failures `access`
cannot see (missing interpreter, `ENOEXEC`). It replaces the library's central mechanism on
a whole platform class and is roughly 60-100 lines of the most delicate code in the file.
Not offered unsolicited; the maintainer's call.

## Cautionary notes worth carrying forward

- **`__GLIBC_PREREQ` must not appear in a flat `#if ... && ...`.** The preprocessor replaces
  unknown identifiers with `0` before evaluating, so `#if defined(__GLIBC__) && !__GLIBC_PREREQ(2, 29)`
  becomes `0 (2, 29)` on macOS, musl and Windows - a syntax error. `&&` does not help; this
  fails at parse time, not evaluation time. Nest the checks.
- **An undefined macro is `0` inside `#if`.** A capability macro defined only under
  `#if !defined(_WIN32)` silently evaluates to "not available" on Windows. Define it on
  every platform, or the guard quietly removes code where it should not.
- **A workaround must be gated to the platforms that need it.** `access()` uses the *real*
  UID while `exec` uses the *effective* one, and it cannot see `ENOEXEC`. Unconditional, it
  would change behaviour on healthy platforms; gated, the claim "unchanged everywhere else"
  stays true and reviewable.
- **The project's sanitizer detection is not deterministic under WSL2.** `test/CMakeLists.txt`
  probes each sanitizer with `try_run` at configure time, but the real test runs later in a
  different process with a fresh ASLR draw. Whether `subprocess_thread_test` exists at all
  varied between identical runs. Pin the probes
  (`-DSUBPROCESS_SAN_{thread,memory,address,undefined}_RUNS=FALSE`) before comparing numbers.
