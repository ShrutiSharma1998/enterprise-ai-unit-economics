# Evidence base (Phase 0)

Built 2026-09-20. Status: first pass. Nothing here is a tool default yet; Phase 3 decides that.

The proof layer under the planning tool. Every benchmark the tool might show or default is logged with its definition, population, source, date and grade. If a number is not here, the tool does not use it.

## Files

- `source-register.md`: every source, how it was actually read, the publisher's interest, and its limits.
- `benchmarks.md`: the benchmark library, by topic.
- `disagreements-and-gaps.md`: where sources conflict and why, what no source answers, and what this means for Phases 1 to 3.

## Grades: the claim gets the grade, not the publisher

| Grade | Meaning | Tool use |
|---|---|---|
| A | Primary: a provider's own price or lifecycle page, a framework or standards document, a seller's own product definition | May become a default |
| B | Named survey or study with a visible method (sample, dates, population), even if self-reported | May become a default, with its population stated |
| C | Blog, vendor or consultancy assertion, or a number whose method is not visible | Directional. Shown as a range with a warning. Never a default |
| D | An assumption we make | Labeled as an assumption. The enterprise can override it |

- An asterisk (A\*, B\*, C\*) means provisional: the figure came from a search excerpt or a summary of the original, and the original was not opened. Confirm before it becomes a default.
- A primary publisher can still produce a grade C claim, for example a savings range with no visible method.
- Forecasts and predictions are labeled as such. They are not measurements.

## Entry schema

ID, claim, definition and population, source ID, source date, grade, how the tool should use it.

## How it was read (limits you should know)

- Pages were fetched on 2026-09-20 through a tool that summarises each page. Quotes and numbers are "as extracted". Before anything is published, open the cited URL and confirm the wording.
- Some originals could not be read (blocked, timed out or unreadable): see the "How read" column of the register. Figures known only from a search excerpt or a secondary write-up carry an asterisk or grade C, whatever the original publisher's standing.
- Prices here are a dated snapshot to show mechanics. The tool's price book is built fresh in Phase 4.
- Public sources only. No client or employer data.
