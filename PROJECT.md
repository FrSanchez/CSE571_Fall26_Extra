# Three-Week Project Plan

This plan follows the project scope in [CSE571_Fall26.md](CSE571_Fall26.md). At planning time, `README.md` was not present. This document covers planning only; implementation has not started.

Three weeks is achievable if the team chooses a narrow domain and builds a single-agent system. The assignment allows full credit for this approach. Plan for roughly **10–12 hours per person per week**, or **120–144 team hours** total. Confirm instructor submission deadlines before assigning calendar dates. These capacity estimates and milestones are planning recommendations, not additional course requirements.

## Team Responsibilities

Each person owns a workstream, with a second person reviewing it. Everyone contributes to the final report.

| Person | Primary responsibility | Reviewer |
|---|---|---|
| A — Agent workflow | Query generation, adaptive decisions, agent loop, stopping policy | C |
| B — Web tools and traces | Search, full-page retrieval, source metadata, action logging | A |
| C — Evidence and verification | Evidence records, claim verification, citation checks, uncertainty handling | D |
| D — Evaluation and delivery | Six-question suite, baseline, scoring, reports, submission checklist | B |

Choose the domain and six questions together. D coordinates evaluation; the other three people also review results so evaluation does not become one person’s bottleneck.

## Week 1 — Establish Scope and Prove the Complete Workflow

**Milestone: one question runs from input to a cited answer, with inspectable evidence and a complete trace.**

| Work | Owner | Evidence of completion |
|---|---|---|
| Choose a bounded domain and finalize exactly six questions, one per required category | D + team | Reviewed question list with expected evidence and scoring criteria |
| Agree on tool inputs/outputs, evidence schema, trace format, and budgets | A, B, C | Short architecture document with example records |
| Connect search and full-page retrieval | B | Saved search results and retrieved page text |
| Build the first agent loop and evidence verification step | A + C | Demonstrated query → retrieval → evidence → verification → answer |
| Complete the one-page preliminary report | D + team | All four rational-agent factors and six environment properties addressed |

Suggested sequence: scope and interfaces on days 1–2; parallel implementation on days 3–4; integration and review on days 5–7.

### Week 1 Progress Checks

- **6/6** required question categories defined.
- **1/1** complete end-to-end demonstration.
- **100%** of required evidence fields present in that demonstration.
- **1/1** preliminary report reviewed by another teammate.

Use separate practice questions for development. Freeze the six evaluation questions before final evaluation.

## Week 2 — Complete Behavior and Establish the Comparison

**Milestone: the agent and baseline both run across the six-question suite, and failures are recorded.**

| Work | Owner | Evidence of completion |
|---|---|---|
| Implement adaptive searches and budget-based stopping | A | Trace showing a later action changed because of intermediate evidence |
| Handle retrieval failures and preserve complete run artifacts | B | Inspectable traces, including failed retrievals |
| Complete supported/contradicted/insufficient handling and citation validation | C | Reviewed examples of each label and corresponding answer behavior |
| Implement a simple fixed-query baseline and evaluation runner | D | Baseline results under documented, comparable conditions |
| Run the six-question rehearsal and prioritize fixes | Team | Results table, scored claims, and defect list |

### Week 2 Progress Checks

- **6/6** agent runs and **6/6** baseline runs completed and saved.
- **100%** of agent runs stay within the configured budgets.
- **0** citations to sources the agent did not retrieve.
- At least **one demonstrated adaptive decision** and reviewed cases for disagreement and insufficient evidence.
- Every failure has an owner and a planned resolution or documented limitation.

A completed run can legitimately end in an abstention. Measure whether its outcome is justified, rather than counting all abstentions as failures.

## Week 3 — Validate, Analyze, and Package

**Milestone: a complete submission supported by frozen evaluation evidence.**

| Work | Owner | Evidence of completion |
|---|---|---|
| Fix correctness and trace gaps; freeze the evaluated version | A + B + C | Recorded code version, configuration, prompts, and model details |
| Conduct final agent and baseline evaluation | D + team | Six paired results with timestamps and saved evidence |
| Independently review claims, citations, and outcomes | C coordinates | Reviewer scores and resolved disagreements |
| Finish reports, results table, and case studies | D coordinates; all write | Three-page technical report and at least two case studies |
| Rehearse setup and audit the submission | B + team | Another teammate runs it from the documented instructions |

Complete final evaluation by roughly **day 17**, leaving the remaining days for analysis, packaging, and corrections.

### Week 3 Progress Checks

- **6/6** final results include every required reporting field.
- All important final claims receive human review.
- **2/2** case studies complete; at least one explains an adaptive decision that affected the answer.
- Traces cover successful, unsuccessful, conflicting-evidence, and insufficient-evidence cases.
- All deliverables and the AI/tool disclosure are reviewed and ready.

## Weekly Measurement

Maintain one shared task board with these fields:

`Task | Owner | Reviewer | Due date | Acceptance criteria | Status | Evidence link | Blocker`

Use **Backlog → In progress → Review → Done**. Count work as done only when its acceptance criteria pass and the reviewer confirms the linked evidence.

At the start of each week, estimate tasks in hours and freeze the weekly commitment:

**Weekly completion = estimated hours of accepted tasks ÷ estimated hours committed × 100**

Track added work separately so the denominator cannot quietly change. Also report the milestone checks above: task completion alone does not demonstrate a working agent.

For system quality, use the same definitions in the rehearsal and final evaluation:

| Metric | Measurement |
|---|---|
| Correctness | Questions meeting the predefined answer/outcome rubric ÷ 6 |
| Citation validity | Claim–citation links that actually support the claim ÷ links reviewed |
| Citation completeness | Important factual claims with supporting citations ÷ important factual claims |
| Verification quality | Evidence labels agreeing with human review ÷ labels reviewed |
| Efficiency | Searches, page retrievals, model/tool calls, and elapsed time per question |

Treat **100% trace completeness, budget compliance, and citation retrieval validity** as acceptance gates. Report the other measured results honestly; do not assume the proposed agent must beat the baseline on every question.

Hold a short midweek blocker check and a weekly demonstration. If behind, cut optional UI, extra questions, and multi-agent extensions first. Preserve evaluation, evidence verification, traces, and reports—the core of the assignment and its grading.
