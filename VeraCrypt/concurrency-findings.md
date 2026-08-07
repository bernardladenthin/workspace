# Concurrency findings

Local record only — **nothing reported upstream, nothing committed.**
Verified against `upstream/master` @ `b48e31f5` (1.26.29) on 2026-08-02.

## 1. Check-then-lock race in `RandomNumberGenerator`

### The pattern

`Core/RandomNumberGenerator.cpp`, in **both** `AddToPool` and `GetData`:

```c
void RandomNumberGenerator::AddToPool (const ConstBufferPtr &data)
{
    if (!Running)                     // (1) read without holding the lock
        throw NotInitialized (SRC_POS);

    ScopeLock lock (AccessMutex);     // (2) lock taken only here

    for (...)
        Pool[WriteOffset++] += data[i];   // (3) pool may already be gone
}
```

`Stop()` takes the lock, calls `Pool.Free()` — which sets `DataPtr = nullptr` — and then sets
`Running = false`. A thread that has passed (1) and is waiting at (2) proceeds to (3) with a
null pool pointer.

### Reproduced, on unmodified source

A two-thread driver linked against `Core.a`/`Volume.a`/`Platform.a` — one thread feeding
`AddToPool`, the other calling `Stop()` — segfaults without any patch:

```
Thread 2 "race" received signal SIGSEGV
#0  RandomNumberGenerator::AddToPool(ConstBufferPtr const&)
#1  feeder () at race.cpp:18
```

It is **not** a use-after-free: `Buffer::Free()` nulls `DataPtr`, and `Pool[i]` resolves via
`operator uint8 *`, so the access is a null dereference. (An earlier note in this repo claimed
use-after-free; that was wrong and is corrected here.)

### Second, independent problem

`Running` is a plain `static bool` (`RandomNumberGenerator.h:55`), not `atomic`, not
`volatile`. It is written under the lock in `Start()`/`Stop()` and read outside the lock in
`AddToPool`, `GetData` and `IsRunning()`. That is a data race in the C++ memory model —
undefined behaviour regardless of scheduling.

### Concurrency is real, not hypothetical

| Thread | Calls |
|---|---|
| creation thread — `VolumeCreator::CreationThread`, started at `VolumeCreator.cpp:435` | `GetData()` at 9 sites |
| UI thread — `VolumeCreationWizard.cpp:744` | `AddToPool()` with mouse events |

Both run during volume creation. Pool *access* is correctly serialised by `AccessMutex`; only
the guard in front of it is unsynchronised.

### Reachability

The dangerous interleaving needs a concurrent `Stop()`, which appears only in
`~GraphicUserInterface` and `~TextUserInterface` — i.e. at shutdown. What makes the path
constructible is that nothing waits for the creation thread:

```c
void VolumeCreator::Abort () { AbortRequested = true; }   // volatile bool, signal only
VolumeCreator::~VolumeCreator () { }                       // empty, no join
```

So: user aborts creation or closes the application → UI destructor runs `Stop()` and frees the
pool → the still-running creation thread sits between its `Running` check and the lock →
crash on the next pool access.

### Severity — deliberately not overstated

- Crash at shutdown. **No key disclosure** (the pool is being erased, not exposed) and no
  volume corruption.
- The window is very small and needs a specific interleaving.
- **Not** demonstrated in the real application, only in a driver against the same libraries.
- Whether wxWidgets actually permits that destruction order was not verified.

### Reproducer — keep this, it is what makes a fix verifiable

Not part of the test suite (a race test would be flaky). It is a standalone driver linked
against the built static libraries. Save as `race.cpp`:

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <pthread.h>
#include <unistd.h>
#include "Core/RandomNumberGenerator.h"
using namespace VeraCrypt;

static volatile bool go = false;

static void *feeder (void *)
{
    uint8 entropy[64];
    memset (entropy, 0x5A, sizeof (entropy));
    while (!go) { }
    for (int i = 0; i < 200; i++)
    {
        try { RandomNumberGenerator::AddToPool (ConstBufferPtr (entropy, sizeof (entropy))); }
        catch (...) { }            // NotInitialized is the healthy outcome
    }
    return NULL;
}

int main (int argc, char **argv)
{
    int rounds = atoi (argv[1]);
    for (int r = 0; r < rounds; r++)
    {
        RandomNumberGenerator::Start();
        pthread_t t;
        go = false;
        pthread_create (&t, NULL, feeder, NULL);
        go = true;
        usleep (atoi (argv[2]));          // let the feeder reach AddToPool
        RandomNumberGenerator::Stop();    // pull the pool out from under it
        pthread_join (t, NULL);
    }
    printf ("survived %d rounds\n", rounds);
    return 0;
}
```

Build and run (inside the Linux container, after a normal `make NOGUI=1`):

```bash
g++ -O0 -g -std=gnu++11 -o /tmp/race race.cpp \
    -I src -I src/Crypto -I src/Crypto/Argon2/include \
    -DARGON2_NO_THREADS -D_FILE_OFFSET_BITS=64 \
    src/Core/Core.a src/Volume/Volume.a src/Platform/Platform.a \
    src/Core/Core.a src/Volume/Volume.a src/Platform/Platform.a -lpthread

/tmp/race 2000 30          # unpatched: SIGSEGV, usually within a few hundred rounds
```

It is timing-dependent — 300 rounds sometimes survive, 2000 reliably did not. Under `gdb`:

```
Thread 2 "race" received signal SIGSEGV
#0  RandomNumberGenerator::AddToPool(ConstBufferPtr const&)
#1  feeder () at race.cpp:18
```

If a run needs help hitting the window, insert `usleep (2000);` between the `Running` check
and the `ScopeLock` — that only widens a window that already exists, it does not create one.

### Suggested fix

Three independent steps, smallest first:

1. **Move the guard inside the lock** in both `AddToPool` and `GetData`:

   ```c
   ScopeLock lock (AccessMutex);
   if (!Running)
       throw NotInitialized (SRC_POS);
   ```

   This alone closes the window: `Stop()` holds the same mutex while it frees the pool.

2. **Make the flag atomic.** `Running` is a plain `static bool` (`RandomNumberGenerator.h:55`)
   written under the lock and read outside it by `IsRunning()`. Even with step 1 that public
   accessor stays a data race. `std::atomic<bool>` — `volatile` does **not** help.

3. **Join the creation thread.** `VolumeCreator::Abort()` only sets a flag and
   `~VolumeCreator` is empty (`VolumeCreator.cpp:38, 42`), so nothing guarantees the thread
   has finished before the UI tears the generator down. This is the root cause; steps 1 and 2
   only make the symptom unreachable.

**Verifying a fix:** run the reproducer above with a high round count. Unpatched it segfaults;
patched it must print `survived N rounds`. Also re-run `veracrypt --test` — the existing
`TestRandomNumberGenerator` asserts the guard still rejects use before `Start()`, so a fix
that removes the check rather than moving it will be caught.

### Why no test was added

A race is non-deterministic; a test for it would be flaky, and a flaky test in a crypto suite
is worse than no test. The correct fix is to move the `Running` check **inside** the lock and
make the flag atomic — a change to production code, out of scope here. What *was* added is a
test that the guard exists at all, so it cannot be silently deleted: `TestRandomNumberGenerator`
in [#1850](https://github.com/veracrypt/VeraCrypt/pull/1850), see
[`test-coverage-work.md`](test-coverage-work.md).

The race itself was **not** reported upstream. #1850 contains only the guard test; nothing in
it mentions the crash.

## 2. `VolumeCreator` is the only thread that is neither joined nor detached

Every `Thread::Start` site in the tree, and what happens to the thread afterwards:

| Site | Handling |
|---|---|
| `Core/Unix/CoreService.cpp:416` | `Detach()` at :418 — deliberate fire-and-forget |
| `Core/Unix/CoreService.cpp:1824` | `Detach()` at :1825 |
| `Volume/EncryptionThreadPool.cpp` (workers) | `Join()` for every thread in `Stop()` |
| **`Core/VolumeCreator.cpp:436`** | **neither** |

`pthread_create` without a later `pthread_join` or `pthread_detach` leaks the thread's
resources until process exit. More importantly here, there is no point at which the creation
thread is known to have finished:

```c
void VolumeCreator::Abort () { AbortRequested = true; }   // signal only
VolumeCreator::~VolumeCreator () { }                       // empty
```

This is what makes finding 1 constructible: nothing waits for the creation thread, while the
UI destructor is free to run `RandomNumberGenerator::Stop()`.

## 3. `EncryptionThreadPool` has the same shape but is not exploitable

`BeginKeyDerivation` (`:41`), `DoWork` (`:97`) and `WorkThreadProc` (`:295`) all read
`ThreadPoolRunning` / `StopPending` outside their lock, and both flags are `volatile bool` —
which in C++ provides neither atomicity nor ordering.

It is nevertheless safe in practice, for two reasons worth remembering:

- `Stop()` **joins every worker** before clearing the flag.
- `Start()`/`Stop()` bracket the whole program: `Main/Unix/Main.cpp:74` starts the pool and
  line 75 registers `finally_do ({ EncryptionThreadPool::Stop(); })`. A concurrent stop during
  key derivation cannot be constructed.

The contrast with finding 1 is the lesson: the same unsynchronised check-then-lock is harmless
when the shutdown path joins its threads, and reachable when it does not.

## 4. Checked and cleared — do not re-investigate

Static mutable state without a mutex, all reachable from only one thread today:

| Class | State | Why it is safe *today* |
|---|---|---|
| `Common/SecurityToken` | `Initialized`, `Sessions` (a `std::map`), PKCS#11 pointers, callbacks | keyfile/token work runs in `VolumeCreator::CreateVolume` (lines 226–443, **UI thread**), not in `CreationThread` (53–224). Confirmed by locating `ApplyListToPassword` at `:358` |
| `Core/Unix/CoreService` | pipes and streams for the privileged-service IPC | request/response is strictly sequential on the calling thread |
| `Common/SCardLoader` | 24 members: module handle, function pointers | populated once at load, read-only afterwards |
| `Main/Application`, `Main/GraphicUserInterface` | exit code, wx command ids | UI thread only |

None is a defect now. All would break immediately if the work were parallelised — worth
knowing before anyone moves key derivation onto the worker thread.

One observation that *does* stand: `RandomNumberGenerator::GetData` is called from the UI
thread (`VolumeCreator.cpp:343, :353`) **and** from the worker (`:149, :181, :186, :191`).
Pool access itself is correctly serialised by `AccessMutex`; only the guard in front of it is
not — which is exactly finding 1.

## What to look for next — the pattern generalises

This was found by accident (a mis-targeted patch), not by searching. The same shape is worth
hunting systematically:

1. **check-then-lock** — any predicate read before `ScopeLock` and acted on after it
2. **non-atomic flags shared across threads** — `static bool` / `volatile bool` used as
   signals; `volatile` gives no atomicity or ordering in C++
3. **threads without a join** — `Thread::Start` with no matching wait, so lifetime is implicit
4. **static mutable state** in classes used from both UI and worker threads
