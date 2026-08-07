# VeraCrypt — open items

Status as of **2026-08-07**, verified against `upstream/master` @ `b48e31f5` (1.26.29).

> **Why this file lives here and not in the repo.** The other tracked repos keep their
> open work in their own `TODO.md`. VeraCrypt cannot: the fork is used to prepare
> upstream pull requests, and the findings below are a **local record that must not reach
> upstream**. A `TODO.md` inside the working copy would sooner or later be swept into a
> branch. So it stays in the workspace.

## Open — waiting on upstream maintainers

Nothing to do on our side; these are submitted and out of our hands.

| PR | Subject | Since |
|---|---|---|
| [#1842](https://github.com/veracrypt/VeraCrypt/pull/1842) | Document that `CRYPTOPP_ALIGN_DATA` can expand to nothing | 2026-08-01 |
| [#1843](https://github.com/veracrypt/VeraCrypt/pull/1843) | Explicit derived-key alignment in `CreateVolumeHeaderInMemory` | 2026-08-01 |
| [#1844](https://github.com/veracrypt/VeraCrypt/pull/1844) | Verify `CRYPTOPP_ALIGN_DATA` delivers the requested alignment | 2026-08-01 |
| [#1850](https://github.com/veracrypt/VeraCrypt/pull/1850) | 14 test blocks covering the crypto and platform layers | 2026-08-07 |

**Merge order matters:** #1850 asks for **#1844 to land first** — both touch
`src/Volume/EncryptionTest.{cpp,h}` at different points. `git apply` fails, `git apply -3`
succeeds. The note is already in the #1850 description; no follow-up needed unless a
maintainer merges them the other way round.

## Open — decided against reporting, fix designed but not applied

### 1. Check-then-lock race in `RandomNumberGenerator` — the one real defect

Reproduced on unmodified source; a two-thread driver segfaults. Full analysis, the
standalone reproducer and the three-step fix are in
[`concurrency-findings.md`](concurrency-findings.md#suggested-fix).

Fix in short — smallest step first:

1. move the `Running` guard **inside** `ScopeLock` in `AddToPool` and `GetData`
2. make `Running` a `std::atomic<bool>` (`volatile` does not help)
3. join the creation thread — this is the root cause; 1 and 2 only make it unreachable

**Blocked by a decision, not by missing knowledge.** Deliberately not reported upstream.
Applying it would mean opening a production-code PR, which is out of scope for now.

**If it is ever picked up:** verify with the reproducer (unpatched segfaults, patched must
print `survived N rounds`) *and* re-run `veracrypt --test` — `TestRandomNumberGenerator`
catches a "fix" that deletes the guard instead of moving it.

### 2. `VolumeCreator` thread is neither joined nor detached

`Core/VolumeCreator.cpp:436` — the only `Thread::Start` in the tree with no matching
`Join()` or `Detach()`. `Abort()` only sets a flag, `~VolumeCreator` is empty. This is what
makes item 1 constructible. Same decision applies.

## Open — robustness, no live defect

| Item | Where | Status |
|---|---|---|
| `VolumeLayout` dereferences `Header` unguarded | `Volume/VolumeLayout.cpp:131, 136, 180, 185` | Not reachable in production (`Volume.cpp:197` sets the header first). Inconsistent with the `NotInitialized` style used elsewhere. |
| `EncryptionMode::ValidateParameters` has no callers | `Volume/EncryptionMode.cpp:59, 65` | Production never validates these parameters. Coverage stuck at 38.71 % and **cannot be raised honestly** — calling it from a test would paint the line green and hide the point. |
| `ValidateState()` compiled out of Release | 13 sites, all `if_debug(...)` | Presumably deliberate. Do not treat as a safety net; do not write tests for it. |

## Open — coverage gaps that need fixtures

Both were predicted before writing anything and are not reachable without new
infrastructure:

- **`Volume/Keyfile.cpp` stops at 47 %** — the security-token and directory-enumeration
  branches need a PKCS#11 token or a populated directory.
- **`Volume/VolumeHeader.cpp` barely moves (82 %)** — the remaining part is the
  decrypt-attempt loop, which needs a real encrypted volume.

A fixture volume created once and checked in would unlock both, at the cost of a binary
test asset. Not attempted.

## Known weakness in the tests we submitted

Recorded so it is not rediscovered as a surprise — details in
[`test-coverage-work.md`](test-coverage-work.md#weaknesses-that-remain):

- Breaking the `Running` check in `AddToPool` goes **undetected** by the suite. It is
  covered by line coverage but asserted by nothing. Coverage is not detection.
- `TestVolumeHeaderRejection` relies on `catch (PasswordEmpty&)`; a change of exception
  type still fails the suite, but the attribution becomes unclear.

## Done

- Fork brought up to date — it had drifted 16 months (394 commits). See
  [`upstream-sync.md`](upstream-sync.md); **check this before analysing anything.**
- Coverage measurement method established, including why `lcov`/`gcovr` report wrong
  numbers here — [`coverage-measurement.md`](coverage-measurement.md).
- 14 test blocks written, each verified by injecting a defect — 16 of 17 injected defects
  attributed to the new test itself.
