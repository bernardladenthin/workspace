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
- [llamacpp-ai-index-maven-plugin](https://github.com/bernardladenthin/llamacpp-ai-index-maven-plugin)
- [streambuffer](https://github.com/bernardladenthin/streambuffer)

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

Apache 2.0 — see [LICENSE](LICENSE).
