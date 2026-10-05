# Starter values (grade D)

Built 2026-09-20. Status: draft for approval.

**Every number here is an assumption chosen by Claude to make the model run on day one. None of it is evidence.** The workbook flags each as "starter" until the enterprise confirms or replaces it, and every output shows the share of total cost resting on starter values. Low, base and high mean the low-cost, base and high-cost scenario values.

## Conventions

- **Person-day rate:** $800 (D). Cross-check: BLS median pay times 1.43 divided by 220 working days gives $781 (data scientists) to $883 (software developers) (LAB-02, derived; 220 days is itself an assumption).
- **Not a starter:** the hourly rate for time saved defaults to $46.89, the BLS private-industry average employer cost per hour worked (LAB-01, grade A).
- IDs refer to `research/cost-taxonomy.md`. "Cross-check" names the only evidence that touches the number, or "none".

## Effort and rate starters

| Line | Unit | Low | Base | High | How it was built | Cross-check |
|---|---|---|---|---|---|---|
| CL-01 | person-days per source system | 1 | 3 | 8 | Owner interview, access check, sample review | none (G1) |
| CL-02 | person-days per 100,000 documents | 5 | 20 | 60 | Automated pipeline plus sampled human review. Range kept wide because published shares conflict | CST-07 conflicts (C) |
| CL-03 | person-days per connector; yearly upkeep share of build | 5; 10% | 10; 15% | 25; 25% | Standard connector versus a custom source | none (G1) |
| CL-04 | person-days per source system; yearly change share | 2; 5% | 4; 10% | 10; 20% | Map groups to permissions once, revise on org change | ORG-03 (tag keys only) |
| CL-08 | share of documents changing a month | 1% | 3% | 10% | Slow policy content versus fast tickets | none |
| CL-09 | person-days once; yearly run share | 60; 10% | 120; 20% | 300; 30% | Configure or build a gateway with logging and access control | Base x $800 = $96,000, just under Gartner's $100,000 initial envelope for one use case (ENV-01, B\*, 2024) |
| CL-10 | person-days per use case | 15 | 40 | 120 | Connect one workflow and its systems | none (G11) |
| CL-11 | person-days per use case; once for the platform | 5; 15 | 10; 30 | 30; 60 | Privacy, security and legal reviewers, a few days each | none (G11) |
| CL-12 | person-days per use case; share re-done per model change | 8; 15% | 20; 25% | 60; 40% | Build a test set and scoring; re-run when the model changes | none (G11) |
| CL-13 | person-days per use case; yearly repeat share | 3; 25% | 8; 50% | 25; 100% | Adversarial testing before launch, repeated periodically | none (G11) |
| CL-14 | USD a month | 0 | 0 | 0 | **No starter (set to zero at approval, 2026-09-20).** Enter the enterprise's environment and cloud infrastructure cost; the line is off until then | none |
| CL-15 | USD a month | 0 | 0 | 0 | **No starter.** Enter the vendor quote or GPU rate; the line is off until then | Prices are quoted (BUY-05) |
| CL-17 | multiplier on tokens; agent steps per outcome | 1.05; 3 | 1.15; 6 | 1.50; 20 | Chat: a minority of calls retried. Agents: a plan, several tool calls, a check | none (G8) |
| CL-25 | cases a month per use case; minutes per case | 50; 5 | 200; 10 | 1,000; 20 | Sample outputs and score them | none |
| CL-26 | months between migration events; person-days per workflow per event | 25; 1 | 15; 3 | 12; 10 | Cadence from derived retirement data: minimum 12, median 14.5, maximum 25.4 months | PRC-06 (one provider) |
| CL-27 | yearly upkeep as a share of integration effort | 5% | 10% | 25% | Prompt changes and fixes | none |
| CL-28 | tickets per 1,000 active users a month; hours per ticket | 5; 0.5 | 20; 1 | 60; 2 | Questions and incidents from active users | none |
| CL-29 | FTE, hub platform team | 3 | 5 | 12 | Roles: product owner, two engineers, a data engineer, a governance lead | ORG-07 covers cost-governance teams only, so it is not comparable |
| CL-30 | FTE, AI cost governance | 0.5 | 1 | 3 | An AI share of a FinOps function | ORG-07: 8 to 10 practitioners for the whole function at $100M+ of cloud spend (B) |
| CL-31 | USD a year | 0 | 0 | 0 | **No starter (set to zero at approval, 2026-09-20).** Enter audit and governance cost; the line is off until then | none (G7) |
| CL-32 | USD a year | 0 | 0 | 0 | **No starter.** Enter quotes | none |
| CL-33 | hours per active user, one-time | 2 | 4 | 12 | A short course plus practice | none |
| CL-34 | share of outputs reviewed; minutes per review | see below | see below | see below | Regulated document work reviews everything; other archetypes sample | ORG-06: 27% review all output, a similar share 20% or less (B\*) |
| CL-35 | FTE per 1,000 licensed users, first 6 months; after | 0.25; 0.05 | 0.5; 0.1 | 1.0; 0.2 | Champions and communications during ramp | none |

**CL-34 review share by archetype (base):** A1 assistant 5%, A2 developer 20%, A3 service operations 10%, A4 regulated documents 100%, A5 embedded feature 2%, A6 data and analytics 25%. Low is base times 0.5; high is base times 2, capped at 100%. Minutes per review: low 2, base 3, high 6 (narrowed at Phase 5 approval from 1, 3 and 10, because the wide range drove 56% of the high-cost scenario's increase).

## Value-side starter

| Input | Low | Base | High | Note |
|---|---|---|---|---|
| Realisation share of self-reported time saved | 25% | 50% | 75% | No evidence converts self-reported time saved into cash (G5). Kill-number candidate |

## What the weak starters mean

Four lines have no starter and are off until the enterprise enters a value: CL-14 environments, CL-15 committed capacity, CL-31 compliance audit and CL-32 licences. Every output lists the lines that are off, because they understate cost. CL-09 is the only starter with a cross-check, and it is a 2024 envelope. If any remaining starter matters to a result, the sensitivity table will show it, and the evidence-share bar will show how much of the total it carries.
