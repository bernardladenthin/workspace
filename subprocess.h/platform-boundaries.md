# Platform boundaries

Every version number the library has to respect, with the evidence that established it.
Recorded because guessing these wrong is silent: the wrong side of a boundary compiles
cleanly and fails at link or run time on a machine nobody here owns.

## `posix_spawn_file_actions_addchdir_np`

| Platform | Available from | How it was established |
|---|---|---|
| glibc | **2.29** | Documented; reproduced on manylinux2014 (2.17) and AlmaLinux 8 (2.28) |
| macOS | **10.15** | SDK headers and `libSystem.B.tbd`, quoted below |
| iOS / tvOS / watchOS | **never** | `__API_UNAVAILABLE(ios, tvos, watchos)`, quoted below |
| musl | **1.1.24** | Documented; Alpine 3.10 (1.1.22) fails to link. musl exposes no version macro, so this is undetectable |
| AIX | **never** | Reported in [#109](https://github.com/sheredom/subprocess.h/pull/109) |

Verbatim from `usr/include/spawn.h`, byte-identical in `MacOSX10.15.sdk` and
`MacOSX15.5.sdk`:

```c
int     posix_spawn_file_actions_addchdir_np(posix_spawn_file_actions_t *,
    const char * __restrict) __API_AVAILABLE(macos(10.15)) __API_UNAVAILABLE(ios, tvos, watchos);
```

**It is macOS-only.** Despite the naming convention, it is *not* available on iOS 13 — a
claim that survived one round of research before the SDK header refuted it. This matters for
the probe's shape: see "Fail-closed" below.

It is a real symbol boundary, not merely a declaration one. From `usr/lib/libSystem.B.tbd`:

| SDK | declared in `spawn.h` | exported by libSystem |
|---|---|---|
| 10.14 | no | no |
| 10.15 | yes | yes |
| 15.5 | yes | yes |

### The two macOS failure modes

Only the first is a compile error, which is why the second went unnoticed for so long.

**SDK older than 10.15** — symbol neither declared nor exported. Hard error in C++,
implicit-declaration in C, link error in `gnu89`. This is [#108](https://github.com/sheredom/subprocess.h/issues/108).

**SDK 10.15+, deployment target older** — the header declares it, so the build succeeds.
clang emits `-Wunguarded-availability-new` **by default** and fails under
`-Werror=unguarded-availability-new`; otherwise the warning is easy to miss. Linking then
produces:

```
(undefined) weak external _posix_spawn_file_actions_addchdir_np (from libSystem)
```

A *weak* import does not stop the binary from loading — dyld binds a missing weak symbol to
null — so the failure surfaces as a **crash at the call site**, not at load time. Building
with deployment target ≥ 10.15 instead produces a **strong** reference, which is what turns
into the `dyld: Symbol not found` reports seen in the wild. Both shapes disappear once no
reference is emitted at all.

### Fail-closed, and why the `defined()` guard was removed

The Darwin arm is deliberately flat, with **no** `defined(MAC_OS_X_VERSION_MIN_REQUIRED)`
guard:

```c
#elif defined(__APPLE__) && MAC_OS_X_VERSION_MIN_REQUIRED < 101500
#define SUBPROCESS_HAVE_CWD 0
```

An absent macro folds to `0`, and `0 < 101500` is true — so any Apple toolchain that does not
supply the macro answers "no cwd" instead of optimistically claiming the capability. Two
consequences fall out for free:

- **iOS/tvOS/watchOS get the right answer**, because the macro is undefined there and the
  function does not exist either.
- **Toolchains without availability macros** — the #108 case, MacPorts GCC on PowerPC, where
  old `AvailabilityMacros.h` gates the macro on `__APPLE_CC__` — land on `ENOSYS` rather than
  a missing symbol.

A `defined()` guard was added first, on the mistaken belief that iOS *had* the function and
needed protecting from a false negative. It made the probe wrong on iOS and fail-open on
unrecognised toolchains. Removing it fixed both.

`AvailabilityMacros.h` is included for Apple targets at the top of the POSIX block (added by
[#99](https://github.com/sheredom/subprocess.h/pull/99)), so on real macOS the macro *is*
present and correctly valued — measured at the probe point: `1090`, `101300`, `101400`,
`150000`.

## `posix_spawn` reporting a failed `exec`

| glibc | Behaviour with a missing binary |
|---|---|
| 2.17 | `rc=0`, child exits 127 |
| 2.23 | `rc=0`, child exits 127 |
| **2.24** | `rc=2` (`ENOENT`) |
| 2.28 | `rc=2` (`ENOENT`) |

Before 2.24 the caller is simply not told. `subprocess_create` therefore returns success for
an executable that does not exist. This is what [#106](https://github.com/sheredom/subprocess.h/pull/106)
addresses, and it only became observable once #104 made the library build there at all.

**AlmaLinux 8 is the control that matters.** glibc 2.28 is the only tested version sitting
*between* the two boundaries — below 2.29, so no `addchdir_np`; at or above 2.24, so exec
failures are reported. It is the one environment where the two probes must **disagree**, and
therefore the only one where a mixed-up version number would show.

## Reporting "the platform cannot do this"

Since [#110](https://github.com/sheredom/subprocess.h/pull/110) (upstream `9ce0d70`) the
enum carries a dedicated value, and `ENOSYS` maps onto it:

```c
  subprocess_error_spawn = -8,
  subprocess_error_not_supported = -9
```

Before that, the `ENOSYS` path introduced by #104 fell into `default:` →
`subprocess_error_unknown` → rewritten to `subprocess_error_spawn` at the call site, i.e. a
capability gap was indistinguishable from a spawn failure. Anything added to the
fail-closed side of a probe should now return `ENOSYS` and inherit `-9` automatically.

## AIX

`posix_spawn_file_actions_addchdir_np` does not exist there at all, and the probe **gets
this wrong**: AIX defines neither `__GLIBC__` nor `__APPLE__`, so it falls through to the
`#else` and answers `1`. Until [#109](https://github.com/sheredom/subprocess.h/pull/109)
lands, AIX needs `-DSUBPROCESS_HAVE_CWD=0`; after it lands, the `1` is correct because the
`fork`/`exec` path provides the capability.

AIX 7.1 is additionally constrained by hardware. From the
[AIX 7.1 release notes](https://www.ibm.com/docs/en/aix/7.1.0?topic=notes-aix-710-release):

> Only 64-bit Common Hardware Reference Platform (CHRP) machines running selected
> PowerPC 970, POWER4, POWER5, POWER6, and POWER7 processors that implement the POWER
> architecture Platform Requirements (PAPR) are supported.

**POWER7 is the ceiling for 7.1** — anything newer is out of spec. Minimum memory is 512 MB.
This matters for emulation; see [`verification-playbook.md`](verification-playbook.md).

## AIX is not the exception — the `#else` was wrong on three OS families

> **Resolved.** The probe has since been split in two and now answers correctly on all of
> them; see the end of this section. The measurements below are what drove that change.

The probe's `#else` hands `SUBPROCESS_HAVE_CWD 1` to every platform that is neither glibc nor
Apple. AIX was the first platform measured where that is wrong. It is not the only one.

Taken from each release's own `spawn.h` and `libc`, streamed from the vendors' mirrors:

| Platform | `spawn.h` declares | `libc` exports | `subprocess.h` builds |
|---|---|---|---|
| FreeBSD 13.1, 13.2, 14.3, 15.0 | `..._addchdir_np` | `..._addchdir_np` | **yes** |
| NetBSD 9.3, 9.4 (`__NetBSD_Version__` 904000000) | nothing | — | **no** |
| NetBSD 10.0, 10.1 (1000000000, 1001000000) | `..._addchdir` — no `_np` | `..._addchdir` | yes, since #102 |
| OpenBSD 7.7, 7.8, 7.9 | nothing | — | **no** |
| AIX 7.2 TL04 | nothing | nothing | **no** (measured on a running system) |

A prior version of this table claimed NetBSD 10 was broken too. That was wrong — the call site
already selects the POSIX spelling for `__NetBSD__`. Corrected above.

**NetBSD 10 is already handled upstream** — [#102](https://github.com/sheredom/subprocess.h/pull/102),
"Fix build on NetBSD" by Thomas Klausner, selects the POSIX spelling there:

```c
#if defined(__NetBSD__) || (defined(__APPLE__) && MAC_OS_X_VERSION_MIN_REQUIRED >= 260000)
    posix_error = posix_spawn_file_actions_addchdir(&actions, process_cwd);
```

But that guard carries **no version test**, and the function only appeared in NetBSD 10.0.
On 9.4 and older neither spelling exists, so the call resolves to nothing:

- up to 9.4 the function does not exist under either name, yet the code calls the POSIX one;
- from 10.0 the POSIX name exists and the upstream guard is correct.

So the live NetBSD defect is narrower than it first appeared: it is **NetBSD 9 and older**,
not NetBSD in general.

```
$ grep -n addchdir usr/include/spawn.h          # NetBSD 10.1
59:int posix_spawn_file_actions_addchdir(posix_spawn_file_actions_t * __restrict,

$ strings lib/libc.so.12 | grep addchdir
posix_spawn_file_actions_addchdir
```

The codebase already knows this spelling exists — it selects it for macOS 26 and newer:

```c
#if defined(__APPLE__) && MAC_OS_X_VERSION_MIN_REQUIRED >= 260000
      posix_error = posix_spawn_file_actions_addchdir(&actions, process_cwd);
#else
      posix_error = posix_spawn_file_actions_addchdir_np(&actions, process_cwd);
```

so NetBSD 10+ needs the same branch rather than anything new.

**Method note.** The first pass reported "none" for NetBSD and OpenBSD alike. Only for OpenBSD
was that real: the NetBSD sets are named `comp.tar.xz`, not `comp.tgz`, so nothing had been
downloaded and the script could not tell an empty header from a missing one. Always prove the
artefact arrived before reporting an absence — here by printing its size and checking that a
symbol known to be present (`posix_spawn(`) is found:

```
NetBSD-10.1   HEADER NICHT GEHOLT -- Ergebnis wertlos
OpenBSD-7.9   spawn.h  4130 Bytes | posix_spawn: 1 | addchdir: 0
```

See [`../AIX/pitfalls.md`](../AIX/pitfalls.md) rule 11 for the general form of this and of the
harness bug that followed it.

### The resolution: two questions instead of one

```c
/* the POSIX 2024 spelling exists */
#if (defined(__APPLE__) && MAC_OS_X_VERSION_MIN_REQUIRED >= 260000) ||        \
    (defined(__NetBSD__) && __NetBSD_Version__ >= 1000000000)
#define SUBPROCESS_ADDCHDIR_IS_POSIX 1

/* neither spelling exists, so fork()+exec() */
#if defined(_AIX) || defined(__OpenBSD__) ||                                  \
    (defined(__NetBSD__) && (__NetBSD_Version__ < 1000000000))
#define SUBPROCESS_SPAWN_VIA_FORK 1
```

`__NetBSD_Version__` is not a compiler predefine — it comes from `<sys/param.h>`, which the
header therefore includes on NetBSD before the probes run. If it is ever absent the version
folds to `0`, every NetBSD takes the fork path, and the result is heavier than necessary but
never wrong. Fail-closed, like the rest of the design.

The call site no longer names platforms; it asks `SUBPROCESS_ADDCHDIR_IS_POSIX`. That also
fixes the version-less `defined(__NetBSD__)` guard from #102, which was right for NetBSD 10
and wrong for 9 and older.

### Verification

Each branch is exercised against a real vendor sysroot, built from the release sets and
targeted with `clang --target=... --sysroot=...`, not simulated:

| Branch | Taken on | Compiles |
|---|---|---|
| fork | NetBSD 9.4, OpenBSD 7.9, AIX 7.2 | yes |
| `posix_spawn` + POSIX name | NetBSD 10.1 | yes |
| `posix_spawn` + `_np` name | FreeBSD 14.3, glibc ≥ 2.29 | yes |

Every C source of the test suite compiles for all four BSD targets under the flags
`CMakeLists.txt` actually assigns. Simulating NetBSD on Linux with `-D__NetBSD__` does **not**
work — GCC's own `stddef.h` then goes looking for `machine/ansi.h` — which is why the sysroot
route was necessary; AIX and OpenBSD can be simulated that way, NetBSD cannot.

End state: **AIX 441/441** with no override beyond `-maix64`, **Linux 441/441**, and **Linux
with `-DSUBPROCESS_SPAWN_VIA_FORK=1` also 441/441**, which is how the fork path was validated
before it ever ran on AIX.

## PowerPC does not trap on integer division by zero

Measured directly, same program, same compiler:

```
amd64:    exit=136                    -> SIGFPE
ppc64le:  no trap, result=1, exit=0
```

x86's `div` raises `#DE`; PowerPC's `divw` yields an undefined result and no exception.
Consequence for this repo: `create_subprocess_fail_divzero` **cannot pass on POWER**, in all
9 language modes, because the child never dies from `SIGFPE`.

This is architecture, not emulation and not a library defect — and since AIX runs on POWER,
it will fail on real AIX hardware too. Anyone running the suite there should expect exactly
those 9 failures and not go hunting.

## Preprocessor traps that bit here

- **`__GLIBC_PREREQ` must not appear in a flat `#if ... && ...`.** The preprocessor replaces
  unknown identifiers with `0` *before* evaluating, so
  `#if defined(__GLIBC__) && !__GLIBC_PREREQ(2, 29)` becomes `0 (2, 29)` on macOS, musl and
  Windows — a syntax error. `&&` does not help; this fails at parse time, not evaluation
  time. Nest the checks. Object-like macros such as `MAC_OS_X_VERSION_MIN_REQUIRED` are
  safe flat, which is why the Darwin arm may be written that way.
- **An undefined macro is `0` inside `#if`.** A capability macro defined only under
  `#if !defined(_WIN32)` silently evaluates to "not available" on Windows. Define it on
  every platform. The same rule is what makes fail-closed possible — and what made the
  broken #106 merge invisible.
- **`TARGET_OS_OSX` does not exist in SDKs older than ~10.12.** A probe keyed on it falls
  through to its `#else` on exactly the old systems it was meant to catch. Measured: an
  alternative Darwin arm using it answered `1` for macOS 10.9 and 10.14 against old SDKs.
- **A workaround must be gated to the platforms that need it.** `access()` uses the *real*
  UID while `exec` uses the *effective* one, and it cannot see `ENOEXEC`. Unconditional, it
  would change behaviour on healthy platforms; gated, the claim "unchanged everywhere else"
  stays true and reviewable.
