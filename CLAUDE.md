# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`workspace` is the **cross-repo shared layer** for Bernard Ladenthin's
four Java projects:

- [BitcoinAddressFinder](https://github.com/bernardladenthin/BitcoinAddressFinder) — Bitcoin/altcoin private-key scanner (`net.ladenthin:bitcoinaddressfinder`)
- [java-llama.cpp](https://github.com/bernardladenthin/java-llama.cpp) — JNI bindings to llama.cpp (`net.ladenthin:llama`)
- [llamacpp-ai-index-maven-plugin](https://github.com/bernardladenthin/llamacpp-ai-index-maven-plugin) — Maven plugin generating AI summaries (`net.ladenthin:llamacpp-ai-index-maven-plugin`)
- [streambuffer](https://github.com/bernardladenthin/streambuffer) — `OutputStream`/`InputStream` bridge over a dynamic FIFO (`net.ladenthin:streambuffer`)

This repo carries **no production code and no build system** of its
own. It is read by AI assistants and human contributors as the single
source of truth for cross-cutting content. Sibling repos point to the
files here instead of duplicating them.

## Layout

```
.claude/skills/java-tdd-guide/SKILL.md   Canonical Java TDD skill
guides/CODE_WRITING_GUIDE.md             Canonical Java code conventions
guides/TEST_WRITING_GUIDE.md             Canonical Java test conventions
policies/javadoc-conventions.md          HTML-entity rules for Javadoc
policies/spotbugs-suppressions.md        spotbugs-exclude.xml maintenance
policies/jqwik-prompt-injection.md       jqwik pin + incident note
policies/code-quality-todos.md           Recurring per-repo audits
workflows/pull-request-workflow.md       gh / MCP PR steps
templates/CLAUDE.md.template             Standard per-repo CLAUDE.md
crossrepostatus.md                       Live cross-repo status table
```

## How the cross-repo dependency works

Each sibling repo's `CLAUDE.md` keeps repo-specific content (overview,
build commands, architecture, dependencies, repo-specific TODOs) and
replaces the previously-duplicated sections with one-line pointers into
this repo. The `java-tdd-guide` skill is loaded by the Claude harness
from `workspace/.claude/skills/`; sibling repos carry only a
`SKILL.pointer.md` marker file so a human reader can find the canonical
copy.

For the harness to discover the skill, `workspace` must be in the
session's repo scope alongside the active sibling repo. This is the
standard remote-execution setup for these projects — confirm via the
session scope listing if a sibling-repo session reports the skill as
missing.

## Editing rules

When editing files in this repo, remember that **the change propagates
to every sibling repo automatically** (because each sibling now reads
from here rather than carrying its own copy). Practical implications:

1. **Don't add repo-specific content** to the canonical guides or
   policies. If a rule only applies to one repo, it belongs in that
   repo's own supplement (e.g. BAF's `CODE_WRITING_GUIDE.md` for
   BitHelper radix constants).
2. **Treat the canonical text like a public API.** Renames break
   pointer URLs in every sibling. If the doc structure must change,
   plan a coordinated update of the sibling pointer lines in the
   same series of commits.
3. **`crossrepostatus.md` is the live status snapshot** — refresh it
   when cross-repo work lands. The structure is documented in the
   file's own header.

## Build / Test

There is no `mvn` here. The only sanity checks worth running:

- `diff -q .claude/skills/java-tdd-guide/SKILL.md <sibling-repo>/.claude/skills/java-tdd-guide/SKILL.md`
  should fail (the sibling-repo file is the deleted pointer marker, not
  a content duplicate) after Phase C of the workspace migration. If
  `diff -q` reports identical files, the sibling repo has fallen back
  to a stale duplicate.
- `grep -l "jqwik prompt-injection" /home/user/<sibling>/CLAUDE.md`
  should return zero hits after Phase C — the section moved to
  `policies/jqwik-prompt-injection.md` and only the pointer line
  remains per sibling.

## Open TODOs

- **Maintenance cadence.** Every time a cross-repo policy is touched
  (jqwik version review, SpotBugs guidance, code-quality TODO refresh),
  bump the corresponding row in `crossrepostatus.md` and verify the
  pointer URLs in each sibling repo still resolve.
- **Drift detection.** Consider a simple per-sibling check (CI job or
  pre-commit hook) that fails when a sibling repo re-introduces text
  that lives in `workspace/policies/`. Out of scope for the initial
  migration; ship after the migration has settled.
- **Workspace skill discovery.** Validate end-to-end that a Claude
  session opened against a sibling repo correctly loads the
  `java-tdd-guide` skill from `workspace/.claude/skills/` — document
  the actual mechanism (harness skill-discovery path) in this file
  once verified.

## License

Apache 2.0 — see [LICENSE](LICENSE).
