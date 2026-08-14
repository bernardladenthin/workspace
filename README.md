# workspace

Cross-repo shared layer for Bernard Ladenthin's Java repositories.

This repo is the **single source of truth** for content that applies to
every sibling Java project — Claude Code skills, code/test writing
guides, shared policies (jqwik pin, Javadoc conventions, SpotBugs
suppressions), the standard `CLAUDE.md` template, and the cross-repo
PR workflow.

## Sibling repos

- [BitcoinAddressFinder](https://github.com/bernardladenthin/BitcoinAddressFinder)
- [java-llama.cpp](https://github.com/bernardladenthin/java-llama.cpp)
- [srcmorph](https://github.com/bernardladenthin/srcmorph) (formerly `llamacpp-ai-index-maven-plugin`)
- [streambuffer](https://github.com/bernardladenthin/streambuffer)

## Layout

```
.claude/skills/java-tdd-guide/SKILL.md   Canonical Java TDD skill (Jupiter, Java 8 baseline)
guides/src/CODE_WRITING_GUIDE-8.md       Production-code conventions (Java 8 baseline)
guides/src/CODE_WRITING_GUIDE-21.md      Java 21 production-code supplement (extends -8.md)
guides/test/TEST_WRITING_GUIDE-8.md      Test conventions (Java 8 baseline, Jupiter + Hamcrest)
guides/test/TEST_WRITING_GUIDE-21.md     Java 21 test supplement (extends -8.md)
policies/javadoc-conventions.md          HTML-entity rules for Javadoc
policies/spotbugs-suppressions.md        spotbugs-exclude.xml maintenance
policies/jqwik-prompt-injection.md       jqwik pin + incident note
policies/code-quality-todos.md           Recurring per-repo audits
workflows/pull-request-workflow.md       gh / MCP PR steps
templates/CLAUDE.md.template             Standard per-repo CLAUDE.md
crossrepostatus.md                       Live cross-repo status table
```

## Topic folders

Separate from the Java layer above, and not covered by any of its guides or
policies. These hold platform and upstream-contribution knowledge; none is a
tracked repository and none appears in `crossrepostatus.md`.

```
AIX/            Running AIX under QEMU, and what it takes to build there
qemu/           Defects found in QEMU itself, with patches
Linux/          Linux platform notes
subprocess.h/   Upstream contributions to sheredom/subprocess.h
utest.h/        Upstream contributions to sheredom/utest.h
llama.cpp/      llama.cpp notes
VeraCrypt/      VeraCrypt notes
```

`subprocess.h/` and `utest.h/` belong together: subprocess.h vendors utest.h, and
every utest.h defect recorded there surfaced while porting subprocess.h to AIX.

`AIX/` and `qemu/` split the same way. Trying to boot AIX 5.3 on
`qemu-system-ppc64` turned up eight defects in QEMU's PowerPC emulation. Two
have nothing to do with AIX: `mfsr` reading back zero on any 64-bit CPU model
breaks any 32-bit PowerPC guest, and `spapr_vscsi` wrapping a 16-bit descriptor
offset silently corrupts guest data on any transfer above 128 KiB. Those belong
in `qemu/`, with the patches; the AIX-specific walls stay in `AIX/5.3L/`.

## Versioned guide chain

Inside `guides/src/` and `guides/test/`, files are named
`<NAME>-<JAVA-VERSION>.md`. A higher-version file **extends** every
lower-version file in its chain — read every file from the lowest
applicable version up to the highest one your repo's `pom.xml`
`<release>` allows.

The baseline `-8.md` files apply to every sibling repo.
`BitcoinAddressFinder` is on Java 21 and additionally follows the
`-21.md` supplements. The other three repos (`streambuffer`,
`java-llama.cpp`, `srcmorph`) target Java 8 and
must not use Java 21 idioms.

## Style ground truth

`BitcoinAddressFinder` and `streambuffer` are hand-written by the
owner and are the authoritative references for code style. The
other two repos are predominantly AI-generated; their patterns are
data points, not canon.

## How sibling repos consume this

Each sibling repo carries its own `CLAUDE.md` with **repo-specific**
content only: project overview, build commands, architecture,
dependencies, repo-specific TODOs. Sections that are identical across
all four repos (Javadoc HTML entities, SpotBugs rules, jqwik policy,
the three recurring code-quality audits, the PR workflow) are replaced
in each repo by a one-line pointer to the canonical doc here.

The `java-tdd-guide` skill lives **only** in this repo; sibling repos
carry a `SKILL.pointer.md` marker file naming the canonical path.
Claude sessions reach the skill by having `workspace` in their session
scope alongside the active sibling repo.

## License

MIT OR Apache-2.0 — dual-licensed at your option; see [LICENSE](LICENSE) and the [`LICENSES/`](LICENSES) folder.
