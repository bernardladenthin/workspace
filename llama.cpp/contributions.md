# Contributions and open items

Upstream: [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp). Downstream carrier is
jllama, which applies `llama/patches/*.patch` to the FetchContent-ed tree via
`cmake/apply-llama-patches.cmake`.

**Nothing submitted yet.** The patches below are maintained downstream; this file records
which of them are upstream-worthy and what is still missing before they can be offered.

## Ground rules for this repo

llama.cpp's `AGENTS.md` forbids agents from writing pull-request descriptions, issue bodies
and review responses - explicitly "non-overridable under any circumstances", with a
contributor ban as the stated consequence. The prose has to be written by hand. An agent may
gather facts, verify claims against the code and run experiments, and that is where its
value lies here.

`AGENTS.md` also asks for an **issue first** on anything sizeable, rather than an
unannounced pull request.

## Patch status

| Patch | Assessment |
|---|---|
| `0001` win32 arg-parse embed guard | **Issue [#26416](https://github.com/ggml-org/llama.cpp/issues/26416) opened 2026-08-01**, awaiting a maintainer's answer on which direction they want |
| `0002` preserve caller load-progress callback | **Not upstream-worthy as it stands.** Stays downstream |
| `0009` guard `addchdir_np` on old glibc | **Resolved elsewhere.** Went to sheredom instead; see below |

### `0001` - `common_params_parse` discards the caller's argv on Windows

`common/arg.cpp:1203-1209` replaces the caller's `argv` with one rebuilt from
`GetCommandLineW()` whenever the element counts match. Contents are never compared, so a
caller that builds its own argv can silently get the process command line parsed.

Reproduced on unmodified `master` @ `ddd4ec142`, MSVC 19.44, no JNI involved: llama.cpp's
own `test-arg-parser` passes when started with one command line token and fails at
`tests/test-arg-parser.cpp:96` when started with three, because the negative test's
three-element argv is swapped for the process command line.

Full write-up, with the exact output and the build recipe:
`../java-llama.cpp/docs/upstream-investigation-win32-argv-substitution.md`.

Two directions to offer, both described there: split the entry point
(`common_params_parse` parses what it is given, a new `common_params_parse_main` does the
recovery for the standalone tools - clean but 37 files), or tighten the condition to compare
contents (much smaller, but the CRT-argv-versus-ANSI-round-trip comparison may not hold in
every codepage, which would silently disable the #24779 fix it protects).

**Filed as [#26416](https://github.com/ggml-org/llama.cpp/issues/26416)** on 2026-08-01,
labelled `bug-unconfirmed`, first bad commit `508a475` (the #24779 merge - verified: it is
where the substitution entered; the count guard only narrowed it later). The issue reports
the defect, links the analysis, and asks how they want to proceed rather than opening a PR
unannounced. Next step is their answer, not more code.

### `0002` - server clobbers a caller-provided `load_progress_callback`

`tools/server/server-context.cpp` installs the server's own progress reporter
unconditionally. Guarding it with `if (params_base.load_progress_callback == nullptr)` is an
eight-line change and provably inert for the standalone server, where the field is always
null.

Left downstream because there is **no in-tree beneficiary**: the only caller that sets the
field beforehand is an embedder, and embeddability itself is a downstream patch (`0006`).
`AGENTS.md` is explicit that a working, in-scope change is not sufficient - a maintainer has
to want it. The honest answer to "who sets this?" is "my JNI binding", which is not an
upstream use case.

### `0009` - resolved through sheredom, not llama.cpp

The patch modified `vendor/sheredom/subprocess.h`. That file is **re-downloaded verbatim**
by `scripts/sync_vendor.py` from a pinned upstream commit, so a local patch there would have
been silently reverted at the next vendor sync. The fix went to
[sheredom/subprocess.h#104](https://github.com/sheredom/subprocess.h/pull/104) instead; see
`../subprocess.h/contributions.md`.

What remains for llama.cpp is a one-line pin bump in `scripts/sync_vendor.py:24` plus the
re-synced file, once sheredom merges. jllama's patch `0009` is byte-identical to that PR's
head, so `apply-llama-patches.cmake` will report "already applied" and skip it from then on,
rather than failing the build.

**General lesson:** before patching anything under `vendor/`, check whether a sync script
owns the file. A downstream patch is fine there as a stopgap, but the fix belongs upstream
of the vendor pin, not in the vendored copy.
