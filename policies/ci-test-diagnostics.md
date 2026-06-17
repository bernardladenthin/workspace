# CI Test Diagnostics & Memory Standard

> Canonical workspace policy. Each sibling repo's `CLAUDE.md` points to this
> file instead of duplicating the rules.

A single, shared contract for **test-JVM memory** and **failure diagnostics**
across all four sibling repos, so a crash (OOM, native SIGSEGV, fork-spawn
failure) leaves the same artifacts, captured in the same CI stages, everywhere.

## 1. Memory contract (surefire `<argLine>`)

Every repo caps the test fork heap and leaves the initial heap lazy:

```
-Xmx2g          # hard cap, deterministic across runner sizes
(no -Xms)       # forks are short-lived; an eager initial heap only inflates
                # the spawn-time footprint (it does not speed anything up)
```

Rationale for *not* using an eager `-Xms`: dropping it is what fixed BAF's
intermittent `SurefireBooterForkException: Error occurred in starting fork`
(an OS-level spawn failure under memory pressure on the pocl OpenCL job — **not**
a fork timeout; raising `forkedProcessTimeoutInSeconds` does nothing for it).

## 2. Diagnostic JVM flags (surefire `<argLine>`)

Appended to the same `<argLine>`:

```
-XX:+HeapDumpOnOutOfMemoryError   # write a heap dump on OOM …
-XX:HeapDumpPath=.                # … into the workspace root (*.hprof)
-XX:ErrorFile=hs_err_pid%p.log    # JVM crash log lands at a known path
```

### `@{argLine}` is mandatory where JaCoCo is active (all 4 repos)

The surefire `<argLine>` **must** begin with `@{argLine}` (late property
replacement) so the JaCoCo agent that `prepare-agent` injects into the
`argLine` *property* is preserved. Drop it and coverage silently breaks.

Two equivalent shapes are in use (both correct):

- **siblings** (jllama, sb, plugin): one surefire `<configuration>`:
  `<argLine>@{argLine} -Xmx2g -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=. -XX:ErrorFile=hs_err_pid%p.log</argLine>`
- **BAF**: the flags live in an `<argLine>` *property* (which also carries the
  lmdbjava `--add-opens`/`--add-exports` set), and surefire config consumes it
  via `<argLine>@{argLine}</argLine>`.

## 3. CI per test job (every `mvn test`/`verify` job in `publish.yml`)

```yaml
- name: Memory before tests        # free -h  (guard with runner.os == 'Linux'
  run: free -h                     #           in matrices that include Windows)
- name: <Test>
  run: mvn -e --batch-mode ...     # -e prints the underlying IOException errno
                                   # for "Error occurred in starting fork"
- name: Memory after tests
  if: always()                     # (+ '&& runner.os == Linux' in mixed matrices)
  run: free -h
- name: Upload crash & surefire dumps
  if: failure()
  uses: actions/upload-artifact@v7
  with:
    name: crash-dumps-<unique-per-job>
    path: |
      ${{ github.workspace }}/hs_err_pid*.log
      ${{ github.workspace }}/*.hprof
      ${{ github.workspace }}/target/surefire-reports/*.dump
      ${{ github.workspace }}/target/surefire-reports/*.dumpstream
      ${{ github.workspace }}/target/surefire-reports/*.txt
      ${{ github.workspace }}/target/surefire-reports/TEST-*.xml
    if-no-files-found: ignore
```

The artifact **name** must be unique within a run (suffix with `matrix.os` /
`matrix.java-version` / `github.job`); the **path set, trigger, and step
placement** are identical everywhere. `free -h` is Linux-only — guard it on any
job whose matrix includes Windows/macOS.

## 4. Deliberate divergences (NOT drift)

These differ on purpose because they are coupled to a repo's fork model or
dependencies; do **not** "synchronize" them blindly:

| Setting | Where | Why it must differ |
|---|---|---|
| `reuseForks=false`, `forkCount=1` | **BAF only** | Native-state isolation for LMDB (off-heap) + OpenCL + JPMS module-mode. Siblings keep Surefire's default `reuseForks=true` (one reused fork — faster, and no per-class spawn churn). |
| `forkedProcessTimeoutInSeconds=180` | **BAF only** | Safe *only* because `reuseForks=false` makes it a **per-class** budget. Copying it to a `reuseForks=true` repo turns it into a **whole-suite** cap that can kill a long run. Do not propagate without resizing per suite. |
| `--add-opens` / `--add-exports` block | **BAF only** | lmdbjava reflective off-heap access; enforced intra-repo by `JvmModuleFlagConsistencyTest`. Adding the `-XX` diagnostic flags does not change that set (the test's flag regex ignores `-XX`). |
| pocl resource snapshot + OpenCL-specific dump step | **BAF only** | Only repo with OpenCL. |
| Enable core dumps (`ulimit -c unlimited` + `core_pattern`, upload `core.*`) | **jllama** (native/JNI) | Worth it where native crashes happen (JNI, pocl). Optional for the pure-Java repos. |

## 5. Per-repo wiring (where the bytes live)

| Repo | surefire argLine | CI memory steps + crash upload |
|---|---|---|
| **BAF** | `<argLine>` property: `-Xmx2g … -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=. -XX:ErrorFile=hs_err_pid%p.log`; surefire `@{argLine}` | `test` matrix (Linux-guarded) + pocl job; uploads include `*.hprof` |
| **jllama** | `<argLine>@{argLine} -Xmx2g -XX:ErrorFile=… -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=.</argLine>` | already had memory steps + crash upload; `mvn -e` added |
| **sb** | new surefire `<argLine>@{argLine} -Xmx2g -XX:…</argLine>` (pluginManagement) | `test` job: memory before/after + crash upload added |
| **plugin** | new surefire `<argLine>@{argLine} -Xmx2g -XX:…</argLine>` (pluginManagement) | `test` job: memory before/after + crash upload added |

## Maintenance

When you touch any test-fork JVM flag or CI diagnostics step, change it **here
first**, then mirror it into all four `publish.yml` files and POMs, and bump the
corresponding row in [`../crossrepostatus.md`](../crossrepostatus.md). The
`-XX`/`-Xmx` flags are *not* covered by `JvmModuleFlagConsistencyTest` (that gate
only enforces the `--add-opens`/`--add-exports` set), so there is no automated
drift check for this policy yet — keep the four copies aligned by hand.
