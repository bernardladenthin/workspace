# Coverage measurement

## How

No build file needs changing — `src/Makefile` appends `TC_EXTRA_*` to the compiler and
linker flags:

```bash
make NOGUI=1 NOTEST=1 -j"$(nproc)" \
     TC_EXTRA_CFLAGS="--coverage -O0" \
     TC_EXTRA_CXXFLAGS="--coverage -O0" \
     TC_EXTRA_LFLAGS="--coverage"
./Main/veracrypt --test
cd Volume && gcov -n EncryptionModeXTS.cpp
```

`NOTEST=1` keeps the build from running the self-tests itself, so the measured run is the
one you control.

## Use `gcov` — `lcov` and `gcovr` are wrong here

Each subproject is built through `make -C <dir>`, so the working directory recorded in the
`.gcno` files cannot be resolved afterwards. The consequences:

- **`gcovr`** silently drops the entire C++ layer (`Volume/`, `Core/`, `Main/`, `Platform/`)
  and reports only the files it can resolve, without saying that it skipped anything.
- **`lcov`** mis-attributes counts across the phantom paths it invents
  (`/build/src/Core/Volume/…`, `/build/src/Main/Volume/…`) and produces nonsense —
  including per-file percentages above 100 %.

`lcov` reported `EncryptionModeXTS.cpp` at **8.7 %**; the true figure from `gcov` is
**91.39 %**. That is not a rounding difference, it is a wrong conclusion.

**The tell:** merged coverage can only ever be greater than or equal to each individual
run. `lcov` reported `EncryptionAlgorithm.cpp` at 23.5 % and 22.9 % for two runs and
**21.6 %** for both combined. Any time a union is smaller than a part, stop and change tool.

Second pitfall: merging `.gcda` from **two different binaries** into the same files
inflates the result. A standalone test binary linking `Volume.a` appeared to add
"+7 percentage points" this way; a clean A/B inside one binary showed the true delta was
zero. Compare by commenting the call out, not by running a second executable.

## Real figures — from `veracrypt --test` alone

| File | Lines executed |
|---|---|
| `Volume/EncryptionModeXTS.cpp` | 91.39 % |
| `Volume/EncryptionAlgorithm.cpp` | 78.28 % |
| `Volume/Cipher.cpp` | 73.24 % |
| `Volume/Pkcs5Kdf.cpp` | 64.7 % |

The block encryption path is **well covered**, not weak.

## Two experiments — one useless, one that worked

Both on 2026-08-01, same codebase, same measurement method. The only difference is the
order of operations, and it decided the outcome.

### Attempt 1 — write first, measure after → **zero gain**

A `TestBlockRoundTrip()` over every available algorithm: sector round-trip, tweak
dependence on the data unit number, wrong-sector-index rejection, `BufferPtr` round-trip,
sensitivity to a single flipped key bit. Built and passed — 105 assertions, 15 algorithms.
Discarded anyway:

- **Coverage delta: exactly zero** on all three files, measured A/B in one binary.
- **Two injected defects were both caught by the existing KATs first:** forcing the XTS
  data unit number to `0` → `TestXtsAES`; making
  `EncryptionAlgorithm::Encrypt(const BufferPtr&)` a no-op → `TestPkcs5`.

Every property it asserted was already implied by the known-answer vectors. A test that
*reads* sensible is not evidence that it adds anything.

### Attempt 2 — measure first, then target → **+15 pp**

Read the never-executed lines out of the `.gcov` files, then write only against those:

```bash
cd Volume && gcov -b EncryptionAlgorithm.cpp Cipher.cpp EncryptionModeXTS.cpp
grep -n '#####' EncryptionAlgorithm.cpp.gcov      # '#####' = line never executed
```

| File | before | after | Δ |
|---|---|---|---|
| `EncryptionAlgorithm.cpp` | 78.28 % | **93.43 %** | **+15.15 pp** |
| `Cipher.cpp` | 73.24 % | **83.57 %** | **+10.33 pp** |
| `EncryptionModeXTS.cpp` | 91.39 % | **93.38 %** | +1.99 pp |
| `EncryptionMode.cpp` | 38.71 % | 38.71 % | 0 — dead code, see [`code-findings.md`](code-findings.md) |

It covers only rejection paths and accessors, which the KATs never reach because they
always take the success path:

- block operations on an **uninitialised** cipher → `NotInitialized`
  (`EncryptBlock` / `DecryptBlock` / `EncryptBlocks` / `DecryptBlocks`, all five ciphers)
- `EncryptionModeXTS::GetKeySize()` with no ciphers → `NotInitialized`
- `SetKey` with a key **one byte short** and **one byte long** → `ParameterIncorrect`,
  then confirming the correct length is still accepted
- `GetMinBlockSize` / `GetMaxBlockSize` / `GetName()` / `GetName(true)` — never called before

Shape of it (~85 lines in `EncryptionTest.cpp`):

```cpp
foreach_ref (Cipher &cipher, Cipher::GetAvailableCiphers())
{
    Buffer block (cipher.GetBlockSize());
    bool rejected = false;
    try { cipher.EncryptBlock (block); } catch (NotInitialized&) { rejected = true; }
    if (!rejected)
        throw TestFailed (SRC_POS);
    // ... same for DecryptBlock / EncryptBlocks / DecryptBlocks
}

foreach_ref (EncryptionAlgorithm &ea, EncryptionAlgorithm::GetAvailableAlgorithms())
{
    Buffer tooShort (ea.GetKeySize() - 1);
    rejected = false;
    try { ea.SetKey (tooShort); } catch (ParameterIncorrect&) { rejected = true; }
    if (!rejected)
        throw TestFailed (SRC_POS);
    // ... one byte too long, then the correct size must still be accepted
}
```

### Negative tests — the part that actually proves it

Disable one validation at a time by turning its `throw` into a `return`. Keep the
surrounding branch, so nothing executes on an invalid state and a red suite can only mean
the assertion fired, not that something crashed:

| Disabled validation | Reported by |
|---|---|
| `Cipher::EncryptBlock` accepts an uninitialised cipher | `TestFailed at TestEdgeCases:106` |
| `EncryptionAlgorithm::SetKey` accepts a wrong-length key | `TestFailed at TestEdgeCases:160` |

This is the decisive difference from attempt 1, where the *existing* tests caught both
injected defects first. Here the new test reports them itself.

### Windows

`src/Volume/**` appears in **no `.vcxproj`**, so neither changed file affects any Windows
build. Confirmed anyway: all seven user- and kernel-mode compile checks stayed green.

### The rule that falls out of this

Measure the uncovered lines *before* writing anything. If a proposed test cannot name the
`#####` lines it will turn green, it probably adds nothing — no matter how reasonable its
assertions look. Then pair it with a negative test and check **which** test reports the
failure; if an older test gets there first, the new one is redundant.

**But coverage is the screening criterion, not the verdict.** `ExceptionTransportTest` moved
`Platform/Exception.cpp` by exactly **0.00 pp** — the existing `SerializerTest` already runs
those lines — and yet it is the only thing that catches a dropped exception subject on the
path the privileged service uses to report failures. Lines *executed* is not the same as
behaviour *asserted*.

Two tests with an identical coverage delta, opposite verdicts, decided by the negative test:

| Test | coverage delta | unique detection | verdict |
|---|---|---|---|
| `TestBlockRoundTrip` | 0.00 pp | none — the existing KATs caught both injected defects first | **discarded** |
| `ExceptionTransportTest` | 0.00 pp | yes — dropped subject caught nowhere else | **kept** |

Use coverage to *find* candidates; use the negative test to *decide*.

**Status:** submitted as [#1850](https://github.com/veracrypt/VeraCrypt/pull/1850) from branch
`encryption-edge-case-tests`. The findings in [`code-findings.md`](code-findings.md) and
[`concurrency-findings.md`](concurrency-findings.md) were **not** reported upstream — this
repository is their only record.

## What a self-test addition does need

If a check is added to `Common/Tests.c` (the Windows suite), guard it with
`#ifndef TC_WINDOWS_DRIVER` — around **both** the call and the function definition:

- the call, because a failing self-test in a boot-start driver reaches `TC_BUG_CHECK`
  (`Driver/Ntdriver.c`) and would leave a system-encrypted machine unbootable;
- the definition, because an unreferenced static function trips C4505 and the driver
  builds with `TreatWarningAsError`.

And when writing a test that probes alignment, keep probe buffers **smaller** than the
alignment under test — the x86-64 ABI already aligns objects of 16 bytes or more by
itself, which makes such a test pass vacuously. Measured:

```
with attribute,    64 bytes : addr % 16 = 0
without attribute, 64 bytes : addr % 16 = 0    <-- vacuous
without attribute,  4 bytes : addr % 16 = 1    <-- meaningful
```

Always pair a new test with a negative test that breaks the thing under test and confirms
the suite goes red.
