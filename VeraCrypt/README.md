# VeraCrypt

Knowledge base for work on [VeraCrypt](https://github.com/veracrypt/VeraCrypt)
via the fork [`bernardladenthin/VeraCrypt`](https://github.com/bernardladenthin/VeraCrypt),
checked out at [`../VeraCrypt`](../VeraCrypt).

> **Scope note.** VeraCrypt is a **C/C++** project and is *not* one of the four Java
> sibling repos this workspace was originally built for. Nothing here feeds into
> `crossrepostatus.md`, and none of the Java guides or policies apply. The folder exists
> so that hard-won, non-obvious findings survive between sessions.

## Contents

| File | Topic |
|---|---|
| [`upstream-sync.md`](upstream-sync.md) | The fork drifts silently — verify before analysing anything |
| [`build-verification.md`](build-verification.md) | Building and compile-checking on Linux (Docker) and Windows (native MSVC) |
| [`coverage-measurement.md`](coverage-measurement.md) | Measuring coverage, why `lcov`/`gcovr` lie here, real figures, and which test attempts paid off |
| [`test-coverage-work.md`](test-coverage-work.md) | 14 test blocks raising coverage on the security-critical paths, with detection proof — submitted as [#1850](https://github.com/veracrypt/VeraCrypt/pull/1850) |
| [`concurrency-findings.md`](concurrency-findings.md) | Reproduced check-then-lock race in the RNG, plus the patterns worth hunting for |
| [`code-findings.md`](code-findings.md) | Dead code, `if_debug` in Release, uncovered-but-reachable paths — local record, **never reported upstream** |
| [`contributions.md`](contributions.md) | Submitted PRs, merged work, and items deliberately left alone |

## The one structural fact worth knowing first

**Different platforms compile different source files.** This trips up almost every
assumption about "where is this code used":

| Path | Linux / macOS / FreeBSD | Windows user mode | Windows driver | Bootloader | UEFI |
|---|---|---|---|---|---|
| `src/Common/Volumes.c` | ❌ not built | ✅ | ✅ | ✅ (guarded parts) | ✅ |
| `src/Common/Tests.c` | ❌ not built | ✅ | ✅ | ❌ | ✅ |
| `src/Common/Xts.c` | ❌ not built | ✅ | ✅ | ✅ | ✅ |
| `src/Volume/**` (incl. `EncryptionTest.cpp`) | ✅ | ❌ **in no `.vcxproj`** | ❌ | ❌ | ❌ |

The Linux build is driven by `src/Makefile`:

```
PROJ_DIRS := Platform Volume Driver/Fuse Core Main
```

`src/Common/` is **not** in that list; individual `Common/*.o` files are pulled in
explicitly by `src/Volume/Volume.make`. So a header under `Common/` may well reach the
Linux build while its `.c` neighbour does not.

Consequences that bite repeatedly:

- The C++ layer has **its own XTS implementation** (`Volume/EncryptionModeXTS.cpp`).
  `Common/Xts.c` is the Windows/driver path and is never exercised on Linux.
- The C++ layer has **its own volume-header parser** (`Volume/VolumeHeader.cpp`), which
  compares the `"VERA"` magic byte-wise rather than via `TC_HEADER_MAGIC_NUMBER`.
- There is **no Windows CI** — only `ubuntu-22.04` / `ubuntu-latest` in
  `.github/workflows/`. Anything Windows-only is verified by humans or not at all.
