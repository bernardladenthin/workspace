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
-XX:+EnableDynamicAgentLoading    # silence the JDK 21 dynamic-agent warning (see § 2.1)
```

### § 2.1 `-XX:+EnableDynamicAgentLoading` — dynamic-agent warning guard (all 4 repos)

On **JDK 21+** the JVM prints a 3-line `WARNING: A Java agent has been loaded
dynamically (…byte-buddy-agent-*.jar)` the first time a test **self-attaches** a
Java agent at runtime (JEP 451; no static `-javaagent` configured). The trigger
differs per repo but is always **byte-buddy-agent**:

- **BAF** — Mockito's inline mock maker self-attaches byte-buddy on first mock.
- **jllama / sb / plugin** — **Lincheck** self-attaches byte-buddy for its
  model-checking bytecode instrumentation (`*LincheckTest` runs in the default
  `mvn test`).

The warning is written to the fork's **native stderr**, *outside* Surefire's
wrapped `System.err`. Harmless on its own — but the native write can
**intermittently corrupt Surefire's encoded fork channel**, surfacing as
`Corrupted channel by directly writing to native stream` followed by a **bogus**
`There was a timeout in the fork` (a fully green test run reported as a build
failure). `-XX:+EnableDynamicAgentLoading` pre-authorizes the attach, so the
native write — and the race — disappear.

Frequency: the **warning** appears on essentially every run (frequent); the
**channel corruption** is a rare race — BAF hit it under Mockito across 2000+
tests, while the Lincheck repos print the warning but rarely corrupt — so the
flag is both log-hygiene and cheap insurance. It is a test-fork `-XX` flag only
and is **not** part of the `--add-opens`/`--add-exports` set enforced by BAF's
`JvmModuleFlagConsistencyTest`.

### `@{argLine}` is mandatory where JaCoCo is active (all 4 repos)

The surefire `<argLine>` **must** begin with `@{argLine}` (late property
replacement) so the JaCoCo agent that `prepare-agent` injects into the
`argLine` *property* is preserved. Drop it and coverage silently breaks.

Two equivalent shapes are in use (both correct):

- **siblings** (jllama, sb, plugin): one surefire `<configuration>`:
  `<argLine>@{argLine} -Xmx2g -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=. -XX:ErrorFile=hs_err_pid%p.log -XX:+EnableDynamicAgentLoading</argLine>`
- **BAF**: the flags live in an `<argLine>` *property* (which also carries the
  lmdbjava `--add-opens`/`--add-exports` set), and surefire config consumes it
  via `<argLine>@{argLine} -XX:+EnableDynamicAgentLoading</argLine>`.

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
- name: Print crash logs (on failure)   # § 3.1 — MUST precede the upload
  if: failure()
  shell: bash
  run: |
    shopt -s nullglob
    found=0
    for f in <repo's hs_err glob>; do
      found=1
      echo "===== $f (first 200 lines; full file in the uploaded artifact) ====="
      sed -n '1,200p' "$f"
    done
    for f in <repo's *.dumpstream and *.dump globs>; do
      found=1
      echo "===== $f ====="
      cat "$f"
    done
    if [ "$found" = 0 ]; then
      echo "No hs_err_pid*.log and no surefire dump/dumpstream was written."
      echo
      echo "For an ordinary test failure that is EXPECTED, not a finding: this step runs on"
      echo "any job failure, and an assertion failure, a timeout or a compile error writes no"
      echo "crash log. Read the surefire output above for the real cause."
      echo
      echo "It points at a JVM-level abort only if the log ALSO shows a fork ending abnormally"
      echo "- 'The forked VM terminated without properly saying goodbye', or an exit with no"
      echo "test results. In that case the abort bypassed the JVM error handler (a native"
      echo "exit()/terminate() rather than a raised signal), which is why no file was written."
    fi
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

> **Why the no-file branch is worded so defensively.** The step is `if: failure()`, so it fires on
> *every* job failure — and the overwhelming majority of those are ordinary assertion failures, which
> never write a crash log. An earlier version asserted "The fork died without the JVM writing a crash
> log" unconditionally, so a plain red test printed a confident claim that the JVM had aborted, under
> a heading that also echoed perfectly healthy server logs. That cost real debugging time. State the
> observation, then name the one signature that would actually justify the conclusion; never assert
> the conclusion from the absence of a file alone.

The artifact **name** must be unique within a run (suffix with `matrix.os` /
`matrix.java-version` / `github.job`); the **path set, trigger, and step
placement** are identical everywhere. `free -h` is Linux-only — guard it on any
job whose matrix includes Windows/macOS.

### § 3.1 Echo the crash log into the job log, don't only upload it

**An uploaded artifact is not a readable diagnostic.** GitHub serves artifact
bytes only from Azure Blob Storage (`*.blob.core.windows.net`) via a signed
redirect — the API never proxies them. So a crash log that exists *only* in an
artifact is out of reach for anyone who cannot fetch from that host: a phone, a
restricted corporate network, and any agent sandbox whose egress policy denies
it. Diagnosing then depends on someone downloading and unzipping ~8 MB to read
40 lines.

This is not hypothetical — it blocked a real investigation: `TtsIntegrationTest`
aborts the forked JVM on all six of jllama's Java test platforms, and the
aborting frame was unreachable for exactly this reason while every other avenue
(local reproduction) was also closed.

The step above therefore **precedes** the upload and echoes the same files. It
is `shell: bash` on every platform including Windows (GitHub's Windows runners
ship Git Bash), so one snippet covers the whole matrix. Two deliberate details:

- **hs_err is truncated to 200 lines, the dumps are not.** An hs_err's
  diagnostic core (fatal-error line, signal, problematic frame, Java frames,
  registers) is at the top; the tail is thread dumps and the memory map, which
  for a JNI project loading a multi-MB native library runs to thousands of
  lines and would bury the job log. The untruncated file stays in the artifact.
  Surefire dumps are small — print them whole.
- **The `found = 0` branch is load-bearing, not politeness.** `if-no-files-found`
  is `warn`/`ignore`, so an upload succeeds with an empty glob and the artifact
  looks the same either way. Only this line distinguishes *"the JVM crashed and
  here is the frame"* from *"the fork died without writing a crash log at all"* —
  which is itself a strong signal (a native `exit()`/`terminate` rather than a
  signal). Without it, an absent hs_err is indistinguishable from one you failed
  to find.

**Prior art:** BAF's `test-opencl` job already did this (`Dump native crash logs
(on failure)`), for the pocl SIGSEGV, with the same rationale in its comment. It
was never promoted to this policy or mirrored, so the other jobs and the three
sibling repos kept the upload-only shape. This section generalises it; BAF's
Linux-only `free -m` / `ps -eL` preamble stays in that job as a local extra.

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
| **BAF** | `<argLine>` property: `-Xmx2g … -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=. -XX:ErrorFile=hs_err_pid%p.log`; surefire `@{argLine} -XX:+EnableDynamicAgentLoading` | `test` matrix (Linux-guarded) + pocl job; uploads include `*.hprof` |
| **jllama** | `<argLine>@{argLine} -Xmx2g -XX:ErrorFile=… -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=. -XX:+EnableDynamicAgentLoading</argLine>` | already had memory steps + crash upload; `mvn -e` added |
| **sb** | surefire `<argLine>@{argLine} -Xmx2g -XX:… -XX:+EnableDynamicAgentLoading</argLine>` | `test` job: memory before/after + crash upload added |
| **plugin** (srcmorph reactor) | surefire `<argLine>@{argLine} -Xmx2g -XX:… -XX:+EnableDynamicAgentLoading</argLine>` in each module pom (`srcmorph`, `srcmorph-cli`, `srcmorph-maven-plugin`) | `test` job: memory before/after + crash upload added |

## Maintenance

When you touch any test-fork JVM flag or CI diagnostics step, change it **here
first**, then mirror it into all four `publish.yml` files and POMs, and bump the
corresponding row in [`../crossrepostatus.md`](../crossrepostatus.md). The
`-XX`/`-Xmx` flags are *not* covered by `JvmModuleFlagConsistencyTest` (that gate
only enforces the `--add-opens`/`--add-exports` set), so there is no automated
drift check for this policy yet — keep the four copies aligned by hand.
