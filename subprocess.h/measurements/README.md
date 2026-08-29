# Windows test runs, August 2026

CTest output from eight Visual Studio builds of `subprocess.h/test`, recovered from a session
scratchpad on 2026-08-22 before the build directories were deleted. The builds themselves are
reproducible; these logs are not, because they record what a specific binary did on a specific
day.

Source tree: `X:/Privat/OpenSource/github/subprocess.h/test`, generator Visual Studio 17 2022.

## What the eight runs show

| Build | Cases | Passed | Skipped |
|---|---:|---:|---:|
| `x64-build`, `win32-build` | 389 | 388 | 1 |
| `w117-Win32`, `w117-x64` | 389 | 388 | 1 |
| `w117b-Win32`, `w117b-x64` | 389 | 388 | 1 |
| `w117c-Win32` | 389 | 388 | 1 |
| **`w117c-x64`** | **390** | 388 | **2** |

Seven runs are identical in shape. `w117c-x64` is the outlier: one test case more, and one more
skipped.

**The skipped tests are the ones this work was about.** Everywhere:

    c.create_does_not_inherit_another_subprocess_pipe

and in `w117c-x64` additionally:

    c.create_keeps_pipe_ends_off_the_standard_descriptors

Both belong to the Windows handle-inheritance work — the `lowfd` line of enquiry and PR #116,
"Restrict Windows subprocess handle inheritance". The second test appears only in the newest
build, which dates the moment it was added.

## Why these were kept

Nothing in [`../contributions.md`](../contributions.md) records a Windows run of this suite. The
PRs are documented, the CI matrix is documented, but not what the local Visual Studio builds
actually reported — and "388 passed, 2 skipped" is a different statement from "the PR was
merged".

**A skipped test is not a passing test.** Two of them sit in exactly the area the changes touch,
and neither the logs nor the notes say *why* they skip on Windows: whether the platform cannot
support the check, or whether the test guards itself out for a reason that no longer holds. That
is an open question, and it would have disappeared with the build directories.

## What was not kept

The eight build trees, 688 files each, 5 504 in total: `ALL_BUILD.vcxproj`, `CMakeCache.txt`,
`CMakeFiles/` and the compiled objects. Reproducible with CMake from the source tree above, and
checked for own files (`.md`, `.patch`, `.diff`) before deletion — none.
