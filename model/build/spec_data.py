# SPDX-License-Identifier: Apache-2.0
"""Inputs for the thin workbook (v0.1). One source of truth for the builder and the reference model.

Everything about the organization is FICTIONAL and grade D. Prices are dated primary prices (grade A)
from evidence/benchmarks.md, fetched 2026-09-20. Effort starters come from spec/starter-values.md.
"""

FICTION = "Fictional worked example (Claude, 2026-09-20)"
STARTER = "spec/starter-values.md (Claude, 2026-09-20)"
D = "2026-09-20"

# ---- Org-level inputs: key -> (label text, value, unit, label, source, grade)
ORG = {
    "name":        ("Organization name", "Northwind Example Co (fictional)", "text", "assumed", FICTION, "D"),
    "horizon":     ("Horizon", 36, "months (max 60)", "assumed", "Project owner's choice, 2026-09-20", "D"),
    "scenario":    ("Scenario shown on Summary", "Base", "Low-cost / Base / High-cost (High-cost is a stress case: every parameter at its high value at once)", "assumed", "User choice", "D"),
    "value_case":  ("Value case (realisation share)", "Base", "Low / Base / High", "assumed", "User choice", "D"),
    "shape":       ("Org shape", "Hub-and-spoke", "Centralized / Federated / Hub-and-spoke", "assumed", "User choice; definitions in research/enterprise-structure.md", "D"),
    "alloc":       ("Allocation rule", "Usage-proportional", "Usage-proportional / Headcount proxy / Even split / Central budget", "assumed", "Default per shape (D), research/enterprise-structure.md", "D"),
    "pd_rate":     ("Person-day rate", 800, "USD per person-day", "assumed", STARTER + "; cross-check BLS LAB-02 (S41, S42)", "D"),
    "hours_day":   ("Hours per person-day", 8, "hours", "assumed", STARTER, "D"),
    "work_days":   ("Working days per year", 220, "days", "assumed", STARTER, "D"),
    "obs_per_out": ("Monitoring units per outcome", 5, "units", "assumed", FICTION, "D"),
}

# ---- Scenario parameters: key -> (description, unit, low, base, high, taxonomy line, rationale, grade)
# Low / Base / High are the low-cost, base and high-cost values.
PARAMS = {
    "src_pd":      ("Assess one source system", "person-days", 1, 3, 8, "CL-01", "Owner interview, access check, sample review", "D"),
    "clean_pd":    ("Clean and label 100,000 documents", "person-days", 5, 20, 60, "CL-02", "Pipeline plus sampled review; range wide because published shares conflict (CST-07)", "D"),
    "conn_pd":     ("Build one connector", "person-days", 5, 10, 25, "CL-03", "Standard vs custom source", "D"),
    "conn_up":     ("Connector upkeep per year", "share of build", 0.10, 0.15, 0.25, "CL-03", "Yearly upkeep share", "D"),
    "perm_pd":     ("Map permissions for one source", "person-days", 2, 4, 10, "CL-04", "Map groups once, revise on org change", "D"),
    "perm_up":     ("Permission upkeep per year", "share of build", 0.05, 0.10, 0.20, "CL-04", "Org change rate", "D"),
    "change_rate": ("Share of documents changing per month", "share", 0.01, 0.03, 0.10, "CL-08", "Slow policy content vs fast tickets", "D"),
    "plat_pd":     ("Platform or gateway, one-time", "person-days", 60, 120, 300, "CL-09", "Configure or build gateway with logging and access control; base x rate = $96,000 vs ENV-01 (B*, 2024)", "D"),
    "plat_run":    ("Platform run per year", "share of one-time", 0.10, 0.20, 0.30, "CL-09", "Yearly run share", "D"),
    "int_pd":      ("Integrate one use case", "person-days", 15, 40, 120, "CL-10", "Connect one workflow and its systems", "D"),
    "rev_uc_pd":   ("Security, privacy, legal review per use case", "person-days", 5, 10, 30, "CL-11", "A few days each from three reviewers", "D"),
    "rev_once_pd": ("Platform-level review, once", "person-days", 15, 30, 60, "CL-11", "One-time platform review", "D"),
    "eval_pd":     ("Evaluation harness per use case", "person-days", 8, 20, 60, "CL-12", "Build a test set and scoring", "D"),
    "eval_rerun":  ("Share of harness re-done per model change", "share", 0.15, 0.25, 0.40, "CL-12", "Re-run when the model changes", "D"),
    "rt_pd":       ("Red-team one use case", "person-days", 3, 8, 25, "CL-13", "Adversarial testing before launch", "D"),
    "rt_rep":      ("Red-team repeat per year", "share of one-time", 0.25, 0.50, 1.00, "CL-13", "Periodic repeat", "D"),
    "env_month":   ("Environments and base infrastructure", "USD per month", 0, 0, 0, "CL-14", "No starter: off until entered (approved 2026-09-20)", "D"),
    "retry":       ("Retry and failure multiplier on tokens", "multiplier", 1.05, 1.15, 1.50, "CL-17", "Minority of calls retried (G8)", "D"),
    "steps":       ("Agent steps per outcome (agentic teams)", "count", 3, 6, 20, "CL-17", "Plan, tool calls, check (G8)", "D"),
    "evalcases":   ("Quality-review cases per month per use case", "cases", 50, 200, 1000, "CL-25", "Sample outputs and score them", "D"),
    "eval_min":    ("Minutes per quality-review case", "minutes", 5, 10, 20, "CL-25", "Read and score one output", "D"),
    "mig_int":     ("Months between model migration events", "months", 25, 15, 12, "CL-26", "Derived from retirement data: min 12, median 14.5, max 25.4 (PRC-06, one provider)", "C"),
    "mig_pd":      ("Re-evaluate one workflow per migration event", "person-days", 1, 3, 10, "CL-26", "Effort per workflow (G12)", "D"),
    "maint":       ("Workflow maintenance per year", "share of integration", 0.05, 0.10, 0.25, "CL-27", "Prompt changes and fixes", "D"),
    "tickets":     ("Support tickets per 1,000 active users per month", "tickets", 5, 20, 60, "CL-28", "Questions and incidents", "D"),
    "tkt_hours":   ("Hours per support ticket", "hours", 0.5, 1, 2, "CL-28", "Handle one ticket", "D"),
    "plat_fte":    ("Hub platform team", "FTE", 3, 5, 12, "CL-29", "Product owner, two engineers, data engineer, governance lead", "D"),
    "gov_fte":     ("AI cost governance", "FTE", 0.5, 1, 3, "CL-30", "AI share of a FinOps function; ORG-07 covers the whole function (B)", "C"),
    "comp_year":   ("Compliance audit and governance", "USD per year", 0, 0, 0, "CL-31", "No starter: off until entered (approved 2026-09-20)", "D"),
    "lic_year":    ("Platform and vendor licences", "USD per year", 0, 0, 0, "CL-32", "No starter: enter quotes", "D"),
    "train_hours": ("Training per active user, one-time", "hours", 2, 4, 12, "CL-33", "Short course plus practice", "D"),
    "rev_mult":    ("Human review share multiplier", "multiplier (capped at 100%)", 0.5, 1, 2, "CL-34", "Low is base x 0.5; high is base x 2", "C"),
    "rev_min":     ("Minutes per human review", "minutes", 2, 3, 6, "CL-34", "Review one output; ORG-06 review shares (B*). Range narrowed from 1/3/10 at Phase 5 approval", "C"),
    "cm_ramp":     ("Change champions during first 6 months", "FTE per 1,000 licensed", 0.25, 0.5, 1.0, "CL-35", "Champions and communications during ramp", "D"),
    "cm_after":    ("Change champions after ramp", "FTE per 1,000 licensed", 0.05, 0.1, 0.2, "CL-35", "Sustaining communications", "D"),
    "tok_mult":    ("Tokens-per-outcome scenario multiplier", "multiplier", 0.7, 1.0, 1.5, "CL-16", "Wide band by design (FCS-01, C)", "D"),
    "fed_dup":     ("Federated: each unit's platform as share of a full hub platform", "share", 0.3, 0.5, 0.7, "org shape", "No evidence on duplication (G4)", "D"),
    "realise":     ("Realisation share of self-reported time saved", "share", 0.25, 0.50, 0.75, "value", "No evidence converts self-reported time saved to cash (G5)", "D"),
}

# ---- Price book: id -> dict. Prices are grade A, fetched 2026-09-20 (see evidence/benchmarks.md).
# kind: Model (per million tokens) | Seat (USD/user/month) | Outcome (USD/outcome) | Unit (USD per unit) | Plan (USD/month)
PRICEBOOK = [
    dict(id="M_HAIKU45", provider="Anthropic", product="Claude Haiku 4.5", kind="Model", p_in=1.0, p_out=5.0, c_read=0.1, c_write=1.25, batch=0.5, unit="USD per million tokens", src="S09", status="standard", to=None),
    dict(id="M_SONNET5", provider="Anthropic", product="Claude Sonnet 5", kind="Model", p_in=2.0, p_out=10.0, c_read=0.1, c_write=1.25, batch=0.5, unit="USD per million tokens", src="S09", status="standard", to=None),
    dict(id="M_OPUS5", provider="Anthropic", product="Claude Opus 5", kind="Model", p_in=5.0, p_out=25.0, c_read=0.1, c_write=1.25, batch=0.5, unit="USD per million tokens", src="S09", status="standard", to=None),
    dict(id="M_GPT54MINI", provider="OpenAI", product="GPT-5.4 Mini (name as extracted)", kind="Model", p_in=0.75, p_out=4.5, c_read=0.1, c_write=1.0, batch=0.5, unit="USD per million tokens", src="S12", status="standard", to=None),
    dict(id="M_GEM38FLASH", provider="Google", product="Gemini 3.8 Flash (name as extracted)", kind="Model", p_in=0.75, p_out=3.75, c_read=0.1, c_write=1.0, batch=0.5, unit="USD per million tokens", src="S11", status="promotional", to="2026-12-31"),
    dict(id="SEAT_TEAM_STD", provider="Anthropic", product="Claude Team standard seat (annual billing)", kind="Seat", p_in=20.0, unit="USD per user per month", src="S33", status="standard", to=None),
    dict(id="SEAT_TEAM_PREM", provider="Anthropic", product="Claude Team premium seat (annual billing)", kind="Seat", p_in=100.0, unit="USD per user per month", src="S33", status="standard", to=None),
    dict(id="SEAT_ENT", provider="Anthropic", product="Claude Enterprise seat (annual); usage billed at API rates", kind="Seat", p_in=20.0, unit="USD per user per month", src="S33", status="standard", to=None),
    dict(id="SEAT_M365_BUS", provider="Microsoft", product="Microsoft 365 Copilot Business (annual, promotional)", kind="Seat", p_in=18.0, unit="USD per user per month", src="S08", status="promotional", to="2026-12-31"),
    dict(id="SEAT_M365", provider="Microsoft", product="Microsoft 365 Copilot (paid yearly)", kind="Seat", p_in=30.0, unit="USD per user per month", src="S35", status="standard", to=None),
    dict(id="OUT_FIN", provider="Intercom", product="Fin AI agent, per outcome (outcome definition in BUY-06)", kind="Outcome", p_in=0.99, unit="USD per outcome", src="S37", status="standard", to=None),
    dict(id="U_TEXTRACT_TXT", provider="AWS", product="Textract detect text, first 1M pages", kind="Unit", p_in=0.0015, unit="USD per page", src="S45", status="standard", to=None),
    dict(id="U_TEXTRACT_TBL", provider="AWS", product="Textract tables, first 1M pages", kind="Unit", p_in=0.015, unit="USD per page", src="S45", status="standard", to=None),
    dict(id="U_EMB_3L", provider="OpenAI", product="text-embedding-3-large", kind="Unit", p_in=0.13, unit="USD per million tokens", src="S12", status="standard", to=None),
    dict(id="U_PINE_READ", provider="Pinecone", product="Read units (low end of range)", kind="Unit", p_in=16.0, unit="USD per million read units", src="S43", status="standard", to=None),
    dict(id="U_PINE_STORE", provider="Pinecone", product="Storage, Standard plan", kind="Unit", p_in=0.33, unit="USD per GB per month", src="S43", status="standard", to=None),
    dict(id="PL_PINE_STD", provider="Pinecone", product="Standard plan minimum", kind="Plan", p_in=50.0, unit="USD per month", src="S43", status="standard", to=None),
    dict(id="U_GUARD_CF", provider="AWS", product="Bedrock Guardrails content filters", kind="Unit", p_in=0.15, unit="USD per 1,000 text units", src="S46", status="standard", to=None),
    dict(id="U_TOOL_SEARCH", provider="Anthropic/OpenAI", product="Web search tool", kind="Unit", p_in=10.0, unit="USD per 1,000 calls", src="S09", status="standard", to=None),
    dict(id="PL_LANGFUSE_PRO", provider="Langfuse", product="Pro plan (100k units included)", kind="Plan", p_in=199.0, unit="USD per month", src="S44", status="standard", to=None),
    dict(id="U_LANGFUSE_OVER", provider="Langfuse", product="Overage per 100k units", kind="Unit", p_in=8.0, unit="USD per 100k units", src="S44", status="standard", to=None),
]
LANGFUSE_INCLUDED = 100_000   # units included in the Pro plan (S44)

# ---- Teams. One team per business unit in v0.1 (documented simplification).
# Field order is the row order on the Teams sheet.
TEAM_FIELDS = [
    ("name", "Team name", "text"), ("active", "Team is active (1 = counted, 0 = ignored)", "1 / 0"), ("archetype", "Archetype", "text"), ("bu", "Business unit and cost center", "text"),
    ("buy", "Buying model", "Seat / Seat + usage / Per-unit / Committed capacity"),
    ("seat_std", "Seat price (price book ID)", "ID"), ("seat_prem", "Premium seat price (price book ID)", "ID"),
    ("prem_share", "Share of licensed users on premium seats", "share"),
    ("allow", "Usage included per seat per month (hybrid)", "USD"),
    ("top_share", "Top segment share of active users", "share"), ("top_mult", "Top segment intensity vs the rest", "multiple"),
    ("unit_price", "Vendor per-outcome price (price book ID, or none)", "ID"),
    ("cap_cost", "Committed capacity cost", "USD per month"), ("cap_outcomes", "Committed capacity outcomes per month", "outcomes"),
    ("licensed", "Licensed users", "users"), ("plateau", "Active share of licensed users at plateau", "share"),
    ("start", "Launch month", "month"), ("ramp", "Months to plateau", "months"), ("curve", "Ramp curve", "Linear / S"),
    ("basis", "Outcome basis", "per user / direct volume"), ("o_user", "Outcomes per active user per month", "outcomes"),
    ("direct", "Direct volume at plateau", "outcomes per month"),
    ("model", "Main model (price book ID)", "ID"), ("cheap", "Cheaper model (price book ID)", "ID"), ("route", "Share routed to cheaper model", "share"),
    ("tok_in", "Input tokens per outcome", "tokens"), ("tok_out", "Output tokens per outcome", "tokens"),
    ("ctx", "Context-management reduction", "share"), ("cached", "Cached share of input", "share"), ("cwrite", "Cache-write share of input", "share"),
    ("async_", "Asynchronous (batch) share", "share"), ("resid", "Residency multiplier", "multiplier"), ("agentic", "Agentic workflow", "Yes / No"),
    ("tool_calls", "Tool calls per outcome", "calls"), ("tool_price", "Tool price (price book ID)", "ID"),
    ("guard_units", "Guardrail text units per outcome", "units"), ("guard_price", "Guardrail price (price book ID)", "ID"),
    ("review", "Human review share of outputs", "share"), ("rev_rate", "Reviewer loaded rate", "USD per hour"),
    ("nsrc", "Source systems", "count"), ("ndocs", "Documents", "count"), ("pages", "Pages per document", "pages"),
    ("parse_price", "Parsing price (price book ID)", "ID"), ("emb_tok", "Embedding tokens per document", "tokens"), ("emb_price", "Embedding price (price book ID)", "ID"),
    ("own_index", "Team runs its own index", "1 / 0"), ("gb", "Index storage", "GB"), ("read_units", "Read units per outcome", "units"),
    ("plan_price", "Index plan minimum (price book ID)", "ID"), ("store_price", "Storage price (price book ID)", "ID"), ("read_price", "Read price (price book ID)", "ID"),
    ("min_saved", "Minutes saved per outcome", "minutes"), ("b_rate", "Loaded hourly rate of time saved", "USD per hour"), ("accept", "Quality or acceptance rate", "share"),
]

TEAMS = [
    dict(active=1, name="Corporate knowledge assistant (conservative calibration)", archetype="A1 Knowledge-worker assistant", bu="Corporate functions",
         buy="Seat", seat_std="SEAT_TEAM_STD", seat_prem="SEAT_TEAM_PREM", prem_share=0.10, allow=0, top_share=0.10, top_mult=5,
         unit_price="", cap_cost=0, cap_outcomes=0, licensed=3000, plateau=0.60, start=1, ramp=6, curve="S", basis="per user",
         o_user=60, direct=0, model="M_SONNET5", cheap="M_HAIKU45", route=0.0, tok_in=2000, tok_out=500, ctx=0.0, cached=0.3,
         cwrite=0.05, async_=0.0, resid=1.0, agentic="No", tool_calls=0, tool_price="U_TOOL_SEARCH", guard_units=0, guard_price="U_GUARD_CF",
         review=0.05, rev_rate=46.89, nsrc=3, ndocs=20000, pages=5, parse_price="U_TEXTRACT_TXT", emb_tok=3000, emb_price="U_EMB_3L",
         own_index=1, gb=20, read_units=2, plan_price="PL_PINE_STD", store_price="U_PINE_STORE", read_price="U_PINE_READ",
         min_saved=2, b_rate=46.89, accept=0.90),
    dict(active=1, name="Engineering assistant", archetype="A2 Developer productivity and agents", bu="Engineering",
         buy="Seat + usage", seat_std="SEAT_ENT", seat_prem="SEAT_TEAM_PREM", prem_share=0.0, allow=0, top_share=0.10, top_mult=5,
         unit_price="", cap_cost=0, cap_outcomes=0, licensed=400, plateau=0.80, start=1, ramp=4, curve="Linear", basis="per user",
         o_user=400, direct=0, model="M_SONNET5", cheap="M_HAIKU45", route=0.0, tok_in=8000, tok_out=2000, ctx=0.10, cached=0.6,
         cwrite=0.05, async_=0.0, resid=1.0, agentic="Yes", tool_calls=0, tool_price="U_TOOL_SEARCH", guard_units=0, guard_price="U_GUARD_CF",
         review=0.20, rev_rate=46.89, nsrc=2, ndocs=50000, pages=3, parse_price="U_TEXTRACT_TXT", emb_tok=4000, emb_price="U_EMB_3L",
         own_index=1, gb=40, read_units=5, plan_price="PL_PINE_STD", store_price="U_PINE_STORE", read_price="U_PINE_READ",
         min_saved=4, b_rate=110.0, accept=0.85),
    dict(active=1, name="Customer service agent", archetype="A3 High-volume service operations", bu="Customer operations",
         buy="Per-unit", seat_std="SEAT_TEAM_STD", seat_prem="SEAT_TEAM_PREM", prem_share=0.0, allow=0, top_share=0.10, top_mult=5,
         unit_price="OUT_FIN", cap_cost=0, cap_outcomes=0, licensed=60, plateau=0.85, start=2, ramp=6, curve="S", basis="direct volume",
         o_user=0, direct=40000, model="M_SONNET5", cheap="M_HAIKU45", route=0.0, tok_in=0, tok_out=0, ctx=0.0, cached=0.0,
         cwrite=0.0, async_=0.0, resid=1.0, agentic="No", tool_calls=0, tool_price="U_TOOL_SEARCH", guard_units=0, guard_price="U_GUARD_CF",
         review=0.10, rev_rate=46.89, nsrc=3, ndocs=8000, pages=4, parse_price="U_TEXTRACT_TXT", emb_tok=0, emb_price="U_EMB_3L",
         own_index=0, gb=0, read_units=0, plan_price="PL_PINE_STD", store_price="U_PINE_STORE", read_price="U_PINE_READ",
         min_saved=6, b_rate=46.89, accept=0.85),
    dict(active=1, name="Regulated document review", archetype="A4 Regulated document and decision work", bu="Risk and legal",
         buy="Per-unit", seat_std="SEAT_TEAM_STD", seat_prem="SEAT_TEAM_PREM", prem_share=0.0, allow=0, top_share=0.10, top_mult=5,
         unit_price="", cap_cost=0, cap_outcomes=0, licensed=150, plateau=0.70, start=3, ramp=5, curve="S", basis="per user",
         o_user=120, direct=0, model="M_OPUS5", cheap="M_SONNET5", route=0.5, tok_in=30000, tok_out=1500, ctx=0.0, cached=0.3,
         cwrite=0.05, async_=0.4, resid=1.1, agentic="No", tool_calls=0, tool_price="U_TOOL_SEARCH", guard_units=126, guard_price="U_GUARD_CF",
         review=1.00, rev_rate=46.89, nsrc=4, ndocs=200000, pages=8, parse_price="U_TEXTRACT_TBL", emb_tok=6000, emb_price="U_EMB_3L",
         own_index=1, gb=300, read_units=10, plan_price="PL_PINE_STD", store_price="U_PINE_STORE", read_price="U_PINE_READ",
         min_saved=8, b_rate=46.89, accept=0.95),
    # Team 5: the same kind of seat-based assistant as Team 1, calibrated to the low published self-reported figure
    # (about 19 minutes a working day, grade C*, evidence VAL-04): 60 interactions a month x 7 minutes = 420 minutes / 21.7 days = 19.4 minutes a day.
    dict(active=1, name="Sales assistant (published-range calibration)", archetype="A1 Knowledge-worker assistant", bu="Sales and marketing",
         buy="Seat", seat_std="SEAT_TEAM_STD", seat_prem="SEAT_TEAM_PREM", prem_share=0.10, allow=0, top_share=0.10, top_mult=5,
         unit_price="", cap_cost=0, cap_outcomes=0, licensed=2000, plateau=0.60, start=1, ramp=6, curve="S", basis="per user",
         o_user=60, direct=0, model="M_SONNET5", cheap="M_HAIKU45", route=0.0, tok_in=2000, tok_out=500, ctx=0.0, cached=0.3,
         cwrite=0.05, async_=0.0, resid=1.0, agentic="No", tool_calls=0, tool_price="U_TOOL_SEARCH", guard_units=0, guard_price="U_GUARD_CF",
         review=0.05, rev_rate=46.89, nsrc=2, ndocs=10000, pages=5, parse_price="U_TEXTRACT_TXT", emb_tok=3000, emb_price="U_EMB_3L",
         own_index=1, gb=10, read_units=2, plan_price="PL_PINE_STD", store_price="U_PINE_STORE", read_price="U_PINE_READ",
         min_saved=7, b_rate=46.89, accept=0.90),
]
# 'async' is a Python keyword; teams use the key async_
