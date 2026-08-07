# Code findings

Observations about upstream VeraCrypt made while working on the encryption layer.
**Nothing here has been reported upstream** — this is a local record only.

Verified against `upstream/master` @ `b48e31f5` (1.26.29).

## 1. `EncryptionMode::ValidateParameters` is dead code

`src/Volume/EncryptionMode.cpp:59` and `:65` define two overloads:

```cpp
void EncryptionMode::ValidateParameters (uint8 *data, uint64 length) const
{
    if ((Ciphers.size() > 0 && (length % Ciphers.front()->GetBlockSize()) != 0))
        throw ParameterIncorrect (SRC_POS);
}

void EncryptionMode::ValidateParameters (uint8 *data, uint64 sectorCount, size_t sectorSize) const
{
    if (sectorCount == 0 || sectorSize == 0 || (sectorSize % EncryptionDataUnitSize) != 0)
        throw ParameterIncorrect (SRC_POS);
}
```

Neither has a single caller anywhere in the tree — not even under `if_debug`. Searched
across `src/Volume/*.cpp`; only the definitions come up.

The checks themselves are sensible (length must be a whole number of cipher blocks; a
sector count or size of zero, or a sector size that is not a multiple of
`ENCRYPTION_DATA_UNIT_SIZE`, is nonsense). They simply never run.

Consequence: `EncryptionMode.cpp` sits at **38.71 %** coverage and cannot be improved
honestly. Calling the functions from a test would paint the line green while leaving the
actual defect — that production code never validates these parameters — untouched.

## 2. `ValidateState()` is compiled out of Release builds

Every call site is wrapped in `if_debug(...)`:

```
src/Volume/EncryptionAlgorithm.cpp:31, 42, 48, 59
src/Volume/EncryptionModeXTS.cpp:57, 236
src/Volume/EncryptionModeWolfCryptXTS.cpp:16, 60
src/Volume/Volume.cpp:63, 69, 310, 352, 379
```

and `src/Platform/PlatformBase.h` defines:

```c
#  define if_debug(...) __VA_ARGS__      // line 108, only when DEBUG is defined
#  define if_debug(...)                  // line 126, otherwise
```

`DEBUG` is set only via `make DEBUG=1` (`src/Makefile:75, 122`). CI and releases build
without it, so none of these state checks exist in a shipped binary. They protect
developer builds only.

This is presumably deliberate (they are assertions, not error handling), but it is worth
knowing before treating them as a safety net — or before writing tests for them, which
would require a `DEBUG=1` build and would prove nothing about the shipped product.

## 3. Uncovered-but-reachable paths in the encryption API

These *are* compiled into Release and were simply never exercised by the test suite,
because the known-answer tests only ever take the success path:

| Location | Path |
|---|---|
| `EncryptionAlgorithm.cpp:200` | `SetMode` with an unsupported mode → `ParameterIncorrect` |
| `EncryptionAlgorithm.cpp:209` | `SetKey` with no ciphers → `NotInitialized` |
| `EncryptionAlgorithm.cpp:212` | `SetKey` with a wrong-length key → `ParameterIncorrect` |
| `EncryptionAlgorithm.cpp:113-132` | `GetMaxBlockSize` / `GetMinBlockSize` — never called |
| `EncryptionAlgorithm.cpp:143-172` | `GetName` — never called |
| `EncryptionModeXTS.cpp:215-226` | `GetKeySize` with no ciphers → `NotInitialized` |
| `Cipher.cpp:52-90` | `EncryptBlock` / `DecryptBlock` / `EncryptBlocks` / `DecryptBlocks` on an uninitialised cipher → `NotInitialized` |
| `Cipher.cpp:92-100` | `GetAvailableCiphers` — never called |

Targeting exactly these lines raised coverage substantially — see
[`coverage-measurement.md`](coverage-measurement.md) for the numbers and the method.

## 4. Audited and cleared — 2026-08-02

A systematic hunt across five defect classes. One real finding came out of it (the RNG race,
see [`concurrency-findings.md`](concurrency-findings.md)); everything below was checked and is
sound. Recorded so the same ground is not covered twice.

**Secret erasure on exception paths — clean.** Production code uses `SecureBuffer` for key
material throughout (`CoreBase.cpp` 9 uses, `VolumeCreator.cpp` 14, `Volume.cpp` 3,
`VolumeHeader.cpp` 2, `Keyfile.cpp` 2). Its destructor calls `Free()`, which calls `Erase()`
before releasing, so an exception mid-derivation still wipes. The only plain `Buffer` holding
key-shaped data is in test code.

**Integer overflow in header arithmetic — not exploitable.** `Volume.cpp:224-228` adds two
unvalidated `uint64` fields from the header:

```cpp
if (partitionStartOffset < header->GetEncryptedAreaStart()
    || partitionStartOffset >= header->GetEncryptedAreaStart() + header->GetEncryptedAreaLength())
    throw PasswordIncorrect (SRC_POS);
EncryptedDataSize -= partitionStartOffset - header->GetEncryptedAreaStart();
```

For the sum to wrap, `EncryptedAreaLength` must be close to 2⁶⁴; the wrapped value is then
*small*, so the second comparison fires and the code throws. The overflow makes the check
**stricter**, not weaker. The subtraction below is guarded by the first comparison, so it
cannot underflow. `partitionStartOffset` comes from the OS, not the header. And the whole path
is only reached after the header decrypted with the user's password and passed two CRC32
checks. `SectorSize` *is* explicitly range-checked at `VolumeHeader.cpp:309`.

**`XtsKeyVulnerable` — correctly implemented end to end.** Detected in `VolumeHeader.cpp:76`
and `:345`, exposed via `IsMasterKeyVulnerable()`, carried across the IPC boundary in
`VolumeInfo`, and surfaced to the user at six call sites (`GraphicUserInterface.cpp:474, 1840`,
`TextUserInterface.cpp:493, 1910`, `ChangePasswordDialog.cpp:371`,
`UserInterface.cpp:780, 875, 914`).

**Swallowed exceptions in the privileged service — defensible.** Four representative
`catch (...) { }` sites examined: package detection with a fallback (`CoreService.cpp:186`),
best-effort reconstruction of a child exception from stderr (`:586`), cleanup inside an error
path (`:1070`), and the forked child before `_exit(1)` (`:1156`), where the parent still sees
the non-zero exit status. None hides a security-relevant failure.

## 5. `VolumeLayout` dereferences its header without a guard

`Volume/VolumeLayout.cpp:131, 136, 180, 185` — the V2 normal and V2 hidden layouts:

```cpp
uint64 VolumeLayoutV2Normal::GetDataOffset (uint64 volumeHostSize) const
{
    return Header->GetEncryptedAreaStart();      // Header may be null
}
```

`Header` is a `shared_ptr <VolumeHeader>` that is empty until `SetHeader()` is called, so
calling these accessors on a fresh layout is a null dereference. Found by writing a test that
did exactly that — it segfaulted.

Two things make this an inconsistency rather than a latent crash:

- The class already has a lazy accessor: `VolumeLayout::GetHeader()` creates a header on
  demand if none is set. `GetDataOffset`/`GetDataSize` bypass it and touch `Header` directly.
- The rest of the code base guards this kind of precondition and throws `NotInitialized`
  (`Cipher::EncryptBlock`, `Buffer::Free`, `EncryptionAlgorithm::SetKey`, and the RNG).

Not reachable in production: `Volume.cpp:197` calls `SetHeader()` before `:204` reads the
offset. So this is a robustness gap, not a live defect.

Related, and deliberate: `VolumeLayoutV1Normal` and `VolumeLayoutSystemEncryption` throw
`NotApplicable` from `GetMaxDataSize` and `GetBackupHeaderOffset` (`VolumeLayout.h:73, 76,
125, 128`). That *is* the guarded style, and it is now covered by a test.

## 6. Numeric parsing of user input — lenient, but caught downstream

`Platform/StringConverter.cpp`. Measured behaviour of `ToUInt32`/`ToUInt64`:

| input | result |
|---|---|
| `"123abc"` | `123` — trailing garbage discarded, not rejected |
| `"-1"` | wraps to all-ones, then rejected by the explicit guard |
| `"-2"` | **accepted** as 4294967294 |
| `"4294967296"` | rejected (`failbit`) |

The all-ones guard is **not** redundant overflow detection: `CommandLineInterface.cpp:646`
uses `ArgSize = (uint64)-1` as its "maximum available size" marker, and the guard stops user
input from ever producing that value. Worth preserving deliberately — there is now a test
pinning it.

Impact of the leniency is limited, and was checked rather than assumed:

- **PIM** is safe — `CommandLineInterface.cpp:556` range-checks `ArgPim < 0 || > MAX_PIM_VALUE`.
- **`--size=-2`** produces a huge value that `VolumeCreator.cpp:306` rejects against the real
  host size.
- **`--size=123abc`** silently becomes 123 bytes and then fails the FAT minimum — a confusing
  error message, not a defect.

## 7. Notes on the merged constants work

- The commit message of [#1525](https://github.com/veracrypt/VeraCrypt/pull/1525) names
  `TC_HEADER_MAGIC` while the code defines `TC_HEADER_MAGIC_NUMBER` — message and code
  permanently disagree in history.
- The same PR describes the added `ULL` suffix as being "for 64-bit safety". The value
  `0x5645524142455854` = 6,215,741,063,806,013,012 < 2⁶³, so C's hex-literal typing
  already selects `long long`. The suffix documents intent; it fixes nothing.
