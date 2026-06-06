# Javadoc Conventions

> Canonical workspace policy. Each sibling repo's `CLAUDE.md` points to this
> file instead of duplicating the table.

## HTML Entities

In Javadoc comments, never use bare Unicode characters for operators and
symbols. Use HTML entities instead:

| Symbol | HTML entity |
|---|---|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `≤` | `&#x2264;` |
| `≥` | `&#x2265;` |
| `→` | `&#x2192;` |
| `←` | `&#x2190;` |
| `≠` | `&#x2260;` |

Use numeric hex entities (`&#xNNNN;`) for any Unicode symbol outside ASCII.
Named entities (`&lt;`, `&gt;`) are acceptable for `<` and `>`.
