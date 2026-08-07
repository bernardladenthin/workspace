# Contributions and open items

## Merged upstream

| PR | Content |
|---|---|
| [#1525](https://github.com/veracrypt/VeraCrypt/pull/1525) | `TC_HEADER_MAGIC_NUMBER` — replaced all hardcoded `0x56455241`; moved the boot-filter magic into `Common/Volumes.h` with a `ULL` suffix |
| [#1526](https://github.com/veracrypt/VeraCrypt/pull/1526) | `TC_DERIVED_KEY_BUFFER_ALIGNMENT` / `TC_KEY_INFO_BUFFER_ALIGNMENT` |

Two notes worth carrying forward from #1525, as cautionary examples:

- Its commit message names `TC_HEADER_MAGIC` / `..._MAGIC`, while the code defines
  `TC_HEADER_MAGIC_NUMBER`. **Message and code disagree, permanently, in history.**
- It describes the added `ULL` as being "for 64-bit safety". The value
  `0x5645524142455854` is `6,215,741,063,806,013,012` < 2⁶³, so C's hex-literal typing
  already picks `long long`. The suffix documents intent; it fixes nothing. Do not describe
  a no-op as a fix.

## Submitted 2026-08-01, awaiting review

All three branch off `b48e31f5`, carry exactly one commit, are independent of each other,
and passed `ubuntu-build` in upstream CI.

| PR | Branch | Content |
|---|---|---|
| [#1842](https://github.com/veracrypt/VeraCrypt/pull/1842) | `alignment-explicit-and-selftest` | comment documenting that `CRYPTOPP_ALIGN_DATA` has an empty fallback branch |
| [#1843](https://github.com/veracrypt/VeraCrypt/pull/1843) | `volumes-explicit-dk-alignment` | one line: `dk` in `CreateVolumeHeaderInMemory` gains the alignment attribute |
| [#1844](https://github.com/veracrypt/VeraCrypt/pull/1844) | `selftest-align-data` | `TC_IS_ALIGNED` + a self-test that `CRYPTOPP_ALIGN_DATA` actually delivers |
| [#1850](https://github.com/veracrypt/VeraCrypt/pull/1850) | `encryption-edge-case-tests` | 14 test blocks, 1133 lines, additions only — see [`test-coverage-work.md`](test-coverage-work.md) |

**Merge order.** #1850 asks for #1844 to go first. Both touch
`src/Volume/EncryptionTest.{cpp,h}` — the changes are independent (different functions, no
overlapping assertions), but #1844 declares `TestAlignment` *before* `TestCiphers` while #1850
inserts *after* it. Verified: a plain `git apply` of #1844 onto #1850's branch fails on the
header context; `git apply -3` succeeds, as does a normal merge or rebase. Merging #1844 first
avoids the question entirely.

#1843 is explicitly **not** a bug fix: the buffer was already 16-byte aligned because the
`KEY_INFO` object above it raises the section alignment (`dumpbin`: section align 16, `dk`
at offset `0x1F0` = 16 × 31), and the emitted `.obj` is byte-identical before and after.
It removes a dependence on that coincidence, nothing more.

## Open on upstream `master` — all assessed as not worth doing

| Item | Location | Why left alone |
|---|---|---|
| The `"VERA"` magic is also written byte-wise | `Volume/VolumeHeader.cpp:269`, `:445` | a 32-bit constant cannot be used at a byte-wise site; purely cosmetic. These are the only two such sites — everything else uses the constant |
| 70 hardcoded `CRYPTOPP_ALIGN_DATA(16)` vs 3 named | repo-wide | **43 of the 70 sit in `src/Crypto/`** (SM4, Kuznyechik, Whirlpool, SHA-2, ChaCha — third-party-derived). High review risk, no behavioural gain |
| Offset formula yields **16, not 0**, for an already-aligned address | `Common/Volumes.c:226` | correct as written (the allocation is `sizeof(KEY_INFO) + 16`, so offset 16 still leaves exactly `sizeof(KEY_INFO)`), just unusual. Wrapping it in a macro would enshrine the quirk |
| No Windows CI | `.github/workflows/` | real gap, but a much larger undertaking than anything above |

## Checked and dismissed — do not re-raise

- **`TCalloc` does not zero memory.** `ExAllocatePoolUninitialized` (kernel) / `malloc` /
  `VeraCryptMemAlloc` — despite the `calloc`-like name. Harmless in practice:
  `crypto_loadkey` burns and fills every `KEY_INFO` field before any read.
- **`size_t` narrowing at `Common/Volumes.c:226`.** Not an issue. The line compiles only
  for ARM64/x64 targets (the `Boot` project is Win32 but that line sits inside
  `#ifndef TC_WINDOWS_BOOT`, and the file is not built on Linux). Confirmed empirically:
  no `C4244`/`C4267` at `/W4`.
- **Secret erasure around `keyInfoBuffer`.** Correct. `Volumes.c:761` does
  `burn (keyInfo, sizeof (KEY_INFO))` before `VirtualUnlock`/`TCfree`; the thread-pool path
  burns the whole buffer in `Common/EncryptionThreadPool.c`.
- **`uintptr_t` instead of the `(uint64)` cast.** Rejected: `uintptr_t` appears only in
  user-mode files, while `Volumes.c` also builds for kernel, UEFI (EDK2 provides `UINTN`)
  and the bootloader.
