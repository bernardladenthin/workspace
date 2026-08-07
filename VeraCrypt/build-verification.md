# Building and compile-checking VeraCrypt

Two independent harnesses cover the two worlds: a Docker container for Linux, and the
native MSVC toolchain for Windows (user mode **and** kernel mode).

## Linux — Docker

`ubuntu:24.04` plus the dependencies from `.github/workflows/build-linux.yml`, with the
distro's wxWidgets 3.2 instead of CI's static 3.2.5 build (much faster, same result for
compile checking):

```
build-essential pkg-config yasm make cmake libpcsclite-dev libfuse-dev
libgtk-3-dev libayatana-appindicator3-dev libwxgtk3.2-dev rsync fuse
```

Mount the repo **read-only** and `rsync` it into the container before building, so the
host tree never receives build artefacts:

```bash
rsync -a --exclude='.git' /src/ /build/
cd /build/src
make NOGUI=1 -j"$(nproc)"        # Release config runs ./veracrypt --text --test itself
./Main/veracrypt --test
```

`NOGUI=1` skips GTK entirely. A Release build runs the self-tests as part of the build
(`src/Main/Main.make`), so a green build already implies green self-tests; re-running
`--test` explicitly just makes it visible.

## Windows — native `cl.exe`, no full solution build

A complete `msbuild VeraCrypt.sln` is blocked by two prerequisites (see *Toolchain state*
below). Compile-checking single files sidesteps both. Take the flags from the owning
`.vcxproj` — and replicate these **four non-obvious mismatches**, or the check fails or,
worse, silently diverges from the real build:

| # | Trap | Fix |
|---|---|---|
| 1 | `UNICODE` / `_UNICODE` come from `<CharacterSet>Unicode</CharacterSet>`, **not** from `PreprocessorDefinitions` | add `/D UNICODE /D _UNICODE` — without them everything resolves to the `*A` Win32 APIs |
| 2 | `Format/InPlace.c` is compiled as **C++** (`<CompileAs>CompileAsCpp`) | `/TP` |
| 3 | `Common/BootEncryption.cpp` needs the MIDL-generated `FormatCom_h.h` | run `midl` **from `src/Format`** — the `.idl` includes `..\Common\Password.h` relative to the working directory |
| 4 | Kernel-mode files need `/kernel` plus the WDK `km` / `shared` / `km\crt` include paths | the WDK's Visual Studio integration is **not** installed, so `Driver.vcxproj` cannot be built — direct `cl.exe` works fine |

Since 1.26.29 both user- and kernel-mode also need Argon2:
`/D ARGON2_NO_THREADS` and `-I Crypto\Argon2\include -I Crypto\Argon2\src\blake2`
(`Common/Crypto.h` includes `argon2.h` unconditionally).

Use `/W4` for user mode and `/W4 /WX` for kernel mode — `Driver.vcxproj` sets
`TreatWarningAsError=true`, so a warning that is merely noisy in user mode breaks the
driver build. This is how an unreferenced-static-function warning (C4505) was caught
before it ever reached CI.

Files worth checking together, because they span every configuration:
`Common/Volumes.c` (user **and** kernel), `Format/InPlace.c`, `Common/BootEncryption.cpp`,
`Common/Tests.c` (user and kernel), `Driver/DriveFilter.c` (kernel).

## Byte-reproducible objects

`/Brepro` plus a **fixed** `/Fo` path yields byte-identical `.obj` files across runs. That
turns "did this edit change the generated code?" into a hash comparison — far stronger
evidence than any test for refactors that are supposed to be no-ops.

The `/Fo` path is embedded in the object. Comparing builds written to *different*
directories reports spurious differences; this trap is easy to fall into twice.

## Toolchain state (as configured 2026-08-01)

| Component | State |
|---|---|
| VS 2022 Community + Build Tools | 17.14.37, MSVC `14.44` — note the **directory** stays `14.44.35207` while `cl.exe` was patched to `14.44.35228`; check `cl.exe`'s `VersionInfo`, not the folder name |
| Windows SDK | `10.0.22621.0`, `10.0.26100.0` — `vcvars` selects 26100 |
| WDK | `10.0.26100` installed: `km` headers and libs present, **but** `WDKContentRoot` is empty and no VSIX/MSBuild driver targets → direct `cl.exe` only |
| MSVC Spectre-mitigated libs | installed (`MSB8040` otherwise blocks `Crypto.vcxproj`) |
| YASM | **missing** — still blocks a full solution build (`src/Crypto` `.asm` sources, `Aes_hw_cpu.obj`) |

Installer gotchas hit while setting this up: `vs_installer` fails with `5007` without
elevation, with `1` if the install path is passed unquoted through PowerShell's
`-ArgumentList` array, and with `8006` (`VSProcessesRunning`) if MSBuild node-reuse workers
are still alive. Pass `/nodeReuse:false` to MSBuild to avoid the last one.
