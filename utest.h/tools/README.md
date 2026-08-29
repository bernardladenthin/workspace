# Probes

## `msvc-probe.c` + `msvc-path.bat`

A preprocess-only probe for which branch of utest.h's format-macro selection is live under
MSVC. `cl /EP` expands without compiling or linking, so the last line of its output names the
chosen macro directly — no build, no test run, no guessing from a failure message.

```
PROBE_RESULT UTEST_PRIu64 UTEST_PRId64
```

Written while chasing the `PRIu64` portability problem documented in
[`../README.md`](../README.md): `UTEST_PRIu64` expands to `PRIu64`, which is `"lu"` on LP64 and
`"llu"` elsewhere, and the failure mode on the wrong branch is a confusing
`error: expected ')' before 'PRIu64'` rather than anything that names the real cause.

`msvc-path.bat` locates the compiler so the probe can be run from a plain shell.

Recovered 2026-08-22 from a session scratchpad. The investigation it belongs to is finished and
its conclusions are in `../README.md`; the probe is kept because the *technique* — ask the
preprocessor instead of the build — applies to the next macro question too.
