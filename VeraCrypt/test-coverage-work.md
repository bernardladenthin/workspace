# Coverage work on the security-critical paths

Record of an extended session against `upstream/master` @ `b48e31f5` (1.26.29), submitted as
[**#1850**](https://github.com/veracrypt/VeraCrypt/pull/1850) from branch
`encryption-edge-case-tests` — 14 blocks, 1133 lines, additions only.

> #1850 asks for [#1844](https://github.com/veracrypt/VeraCrypt/pull/1844) to be merged first;
> both touch `src/Volume/EncryptionTest.{cpp,h}` at different points. See
> [`contributions.md`](contributions.md) for the verified merge-order detail.

The **findings** uncovered along the way — see [`code-findings.md`](code-findings.md) and
[`concurrency-findings.md`](concurrency-findings.md) — were deliberately **not** reported
upstream. #1850 contains tests only.

For how to measure at all, and why `lcov`/`gcovr` must not be used here, see
[`coverage-measurement.md`](coverage-measurement.md).

## Method — the part that decides success

1. **Measure first.** Build with coverage, run `veracrypt --test`, then read the lines
   marked `#####` out of the `.gcov` files. Write only against those.
2. **A/B in one binary.** Comment the test call out and rebuild; never compare two
   different executables (that inflates results — see `coverage-measurement.md`).
3. **Negative test every block.** Break the property under test, confirm the suite goes red,
   and check **which** test reports it. If an older test gets there first, the new one is
   redundant.

Step 1 is what separates this session from the earlier failed attempt, where a test was
written first and turned out to add exactly zero coverage.

## Result — 14 test blocks

The table below lists the first eight, written in the initial pass. Six more followed:
`TestVolumeInfoSerialization` and `TestVolumeLayouts` (`Volume/EncryptionTest.cpp`),
`TestMountOptionsSerialization` (`Main/UserInterface.cpp`), and `StringConverterTest`,
`FileTest`, `ExceptionTransportTest` (`Platform/PlatformTest.cpp`). Final figures are in
[`coverage-measurement.md`](coverage-measurement.md); the numbers in the two tables below are
from the intermediate state and are lower than the final ones.

### The first eight

| Block | File | Covers |
|---|---|---|
| `TestEdgeCases` | `Volume/EncryptionTest.cpp` | rejection paths of the cipher/algorithm API |
| `TestHashClasses` | same | the C++ hash wrappers and both parameter checks |
| `TestKdfSelection` | same | KDF lookup by name and by hash, unknown-name rejection |
| `TestVolumeHeaderRejection` | same | empty password, malformed header creation options |
| `TestPasswordHandling` | same | password serialisation round trip, bounded cache |
| `TestKeyfileApplication` | same | keyfile CRC32 mixing into the password |
| `BufferTest` | `Platform/PlatformTest.cpp` | Buffer/SecureBuffer erase and bounds, `Memory::Compare` |
| `TestRandomNumberGenerator` | `Main/UserInterface.cpp` | the RNG, including its own built-in self-test |

553 added lines, **no deletions**, no existing test touched.

## Coverage, measured A/B

| File | before | after | Δ |
|---|---|---|---|
| `Volume/Hash.cpp` | 0.00 % | 96.88 % | **+96.88** |
| `Volume/VolumePasswordCache.cpp` | 0.00 % | 94.44 % | **+94.44** |
| `Core/RandomNumberGenerator.cpp` | 0.00 % | 83.80 % | **+83.80** |
| `Volume/VolumePassword.cpp` | 45.83 % | 100.00 % | **+54.17** |
| `Platform/Memory.cpp` | 41.18 % | 91.18 % | **+50.00** |
| `Volume/Keyfile.cpp` | 0.00 % | 47.37 % | **+47.37** |
| `Volume/Pkcs5Kdf.cpp` | 50.48 % | 70.48 % | **+20.00** |
| `Volume/EncryptionAlgorithm.cpp` | 78.28 % | 93.43 % | **+15.15** |
| `Volume/Cipher.cpp` | 73.24 % | 83.57 % | **+10.33** |
| `Platform/Buffer.cpp` | 75.76 % | 83.84 % | +8.08 |
| `Volume/EncryptionModeXTS.cpp` | 91.39 % | 93.38 % | +1.99 |
| `Volume/VolumeHeader.cpp` | 81.37 % | 82.35 % | +0.98 |

`VolumeHeader` barely moves: its remaining uncovered part is the decrypt-attempt loop,
which needs a real encrypted volume. That was predicted before writing anything and is not
reachable without fixtures.

## Detection proof — 17 injected defects

Every block was verified by breaking the property it asserts:

| Injected defect | Reported by |
|---|---|
| block op on an uninitialised cipher accepted | `TestEdgeCases` |
| `SetKey` accepts a wrong-length key | `TestEdgeCases` |
| `GetData` returns constant bytes | `TestRandomNumberGenerator` |
| `GetData` works before `Start()` | `TestRandomNumberGenerator` |
| oversized RNG request not rejected | `TestRandomNumberGenerator` |
| `Buffer::Erase` no longer wipes | `BufferTest` |
| `Buffer::GetRange` skips bounds check | `BufferTest` |
| `Memory::Compare` ordering inverted | `BufferTest` |
| hash accepts empty input | `TestHashClasses` |
| KDF lookup matches any name | `TestKdfSelection` |
| oversized password truncated, not refused | `TestPasswordHandling` |
| password cache grows without bound | `TestPasswordHandling` |
| password cache stops deduplicating | `TestPasswordHandling` |
| keyfile contributes nothing to the pool | `TestKeyfileApplication` |
| empty keyfile silently accepted | `TestKeyfileApplication` |
| base password dropped from the keyfile pool | `TestKeyfileApplication` |
| header accepts an empty password | ⚠️ suite red, but via `Pkcs5Kdf::ValidateParameters` |

16 of 17 are attributed to the new test itself. The last one still fails the suite, but the
exception escapes instead of being reported as `TestFailed` — see *Weaknesses* below.

## What the negative tests exposed about the tests themselves

Two blocks were wrong on the first attempt and only the negative test showed it:

- **Cache dedup was untestable as written.** Checking size and front element could not detect
  a broken dedup, because the capacity trim immediately hid the duplicate again. Fixed by
  counting how often the repeated password occurs in the cache.
- **`RandomNumberGenerator::Test()` was misread as dead code.** A grep for `Test ();` (with a
  space) missed the real call `Test();` in `Start()`. The correct finding is weaker: the
  self-test does run in production, but never under CI, because `--test` never starts the RNG.

A third case is a property of the code rather than the test: disabling the header's
`PasswordEmpty` check does not go unnoticed, because the KDF layer refuses an empty password
as a second line of defence.

## Weaknesses that remain

- `TestVolumeHeaderRejection` relies on `catch (PasswordEmpty&)`; if the code starts throwing
  a different type the suite still fails, but the attribution is unclear.
- Breaking the `Running` check in `RandomNumberGenerator::AddToPool` goes **undetected** —
  covered by line coverage, not by any assertion. Coverage is not detection.
- `Keyfile.cpp` stops at 47 %: the security-token and directory-enumeration branches need a
  token or a populated directory.

## Verification status

- Linux build + `veracrypt --test`: green, repeatable, temporary keyfiles cleaned up
- Windows user-mode `/W4` and kernel-mode `/W4 /WX`: 7/7 green — none of the touched files
  appears in any `.vcxproj`, so Windows cannot be affected by construction
