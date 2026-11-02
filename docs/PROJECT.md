# Three-Week Project Plan

This plan follows the project scope in [CSE571_Fall26.md](../CSE571_Fall26.md). This document covers planning only; implementation has not started.

Three weeks is achievable if the team chooses a narrow domain and builds a single-agent system. The assignment allows full credit for this approach. Plan for roughly **10–12 hours per person per week**, or **120–144 team hours** total. Confirm instructor submission deadlines before assigning calendar dates. These capacity estimates and milestones are planning recommendations, not additional course requirements.

## Team Responsibilities

Each person designs and codes a substantial component. These are human team responsibilities within a single-agent system, not separate AI agents. Everyone participates in integration, evaluation, and writing.

| Person | Component they design and code | Design decisions they own | Reviewer |
|---|---|---|---|
| A — Research controller | Question decomposition, query generation, adaptive agent loop, stopping rules | What should the agent do next, and when should it stop? | C |
| B — Retrieval and source selection | Search integration, webpage extraction, metadata, source ranking | Which sources should the agent prioritize and retrieve? | A |
| C — Evidence and verification engine | Structured evidence storage, claim checking, contradiction detection, citation validation | Does the retrieved evidence actually support the claim? | D |
| D — Answer synthesis and baseline | Answers from verified evidence, disagreement and abstention behavior, simpler comparison pipeline | How should the agent communicate its findings, and how does it compare with the baseline? | B |

A coordinates the research loop, B retrieves sources, C verifies evidence, and D synthesizes the answer. Missing or conflicting evidence feeds back to A. C builds executable verification logic; manual result review is shared. D builds a core agent component and the baseline; evaluation and report writing are shared.

### Balanced Work and Shared Responsibilities

- Aim for roughly **two-thirds of each person’s weekly time on implementation and technical experiments**. Use the remainder for integration, review, evaluation, and writing. Rebalance when actual effort differs; this is a planning target, not a quota.
- Choose the domain, six questions, scoring rubric, and interfaces together. Everyone owns tests, trace events, and documentation for their component.
- Each person writes their component’s report section and disclosure details. Rotate assembly: A assembles the preliminary report, B the technical report, C the results and case studies, and D the final package. Assembly means combining team contributions, not writing them alone.
- Divide the six evaluation questions so each person leads review of one or two questions. Assign a second reviewer to each question; at least one reviewer must not own the behavior being assessed. Resolve scoring disagreements together.
- Pair A with C and B with D for initial integration; rotate to A with B and C with D in week 2, then A with D and B with C in week 3.
- Share evaluation-run execution and task-board maintenance. Reassign shared work if one person becomes a bottleneck.

### Weekly Technical Contributions

| Person | Week 1: working foundation | Week 2: deeper behavior | Week 3: validation and improvement |
|---|---|---|---|
| A | Basic research loop | Adaptive query refinement and budgets | Analyze decision failures, make justified fixes, and validate stopping behavior |
| B | Search and full-page retrieval | Source ranking, date handling, retrieval failures | Analyze extraction and source-selection failures and validate fixes |
| C | Evidence schema and initial verifier | Contradictions and citation checks | Analyze verification errors and validate fixes |
| D | Cited answer generation and basic fixed-query baseline | Uncertainty handling and baseline integration | Compare systems, analyze synthesis errors, and validate fixes |

Week 3 technical work may be an experiment or validation with no code change when the component already meets its acceptance criteria.

## Week 1 — Establish Scope and Prove the Complete Workflow

**Milestone: one question runs from input to a cited answer, with inspectable evidence and a complete trace.**

| Work | Owner | Evidence of completion |
|---|---|---|
| Choose a bounded domain and finalize exactly six questions, one per required category | Team | Reviewed question list with expected evidence and scoring criteria |
| Agree on tool inputs/outputs, evidence schema, trace format, and budgets | Team | Short architecture document with example records |
| Connect search and full-page retrieval | B | Saved search results and retrieved page text |
| Build the first agent loop, verifier, and cited-answer synthesis | A + C + D | Demonstrated query → retrieval → evidence → verification → answer |
| Build a basic fixed-query baseline | D | Practice question produces a saved baseline answer |
| Complete the one-page preliminary report | All contribute; A assembles | All four rational-agent factors and six environment properties addressed |

Suggested sequence: scope and interfaces on days 1–2; parallel implementation on days 3–4; integration and review on days 5–7.

### Week 1 Progress Checks

- **6/6** required question categories defined.
- **1/1** complete end-to-end demonstration.
- **100%** of required evidence fields present in that demonstration.
- **1/1** preliminary report reviewed by another teammate.
- **4/4** people demonstrate an executable component and explain a design decision.
- Basic baseline runs on a practice question.

Use separate practice questions for development. Freeze the six evaluation questions before final evaluation.

## Week 2 — Complete Behavior and Establish the Comparison

**Milestone: the agent and baseline both run across the six-question suite, and failures are recorded.**

| Work | Owner | Evidence of completion |
|---|---|---|
| Implement adaptive searches and budget-based stopping | A | Trace showing a later action changed because of intermediate evidence |
| Add source ranking, date handling, and retrieval-failure handling | B | Traces show source-selection decisions and failed retrievals |
| Integrate complete run artifacts and the evaluation runner | Team; each owns component instrumentation | Inspectable traces and automated collection of run counts |
| Complete supported/contradicted/insufficient handling and citation validation | C | Reviewed examples of each label and corresponding answer behavior |
| Complete uncertainty-aware synthesis and integrate the fixed-query baseline | D | Supported claims are cited; disputed or insufficient claims are qualified or omitted; baseline conditions are documented |
| Run the six-question rehearsal and prioritize fixes | Team | Results table, scored claims, and defect list |

### Week 2 Progress Checks

- **6/6** agent runs and **6/6** baseline runs completed and saved.
- **100%** of agent runs stay within the configured budgets.
- **0** citations to sources the agent did not retrieve.
- At least **one demonstrated adaptive decision** and reviewed cases for disagreement and insufficient evidence.
- Every failure has an owner and a planned resolution or documented limitation.
- **4/4** people deliver a reviewed technical improvement and participate in integration.

A completed run can legitimately end in an abstention. Measure whether its outcome is justified, rather than counting all abstentions as failures.

## Week 3 — Validate, Analyze, and Package

**Milestone: a complete submission supported by frozen evaluation evidence.**

| Work | Owner | Evidence of completion |
|---|---|---|
| Fix correctness and trace gaps; freeze the evaluated version | All component owners | Recorded code version, configuration, prompts, and model details |
| Conduct final agent and baseline evaluation | Team; split question assignments | Six paired results with timestamps and saved evidence |
| Independently review claims, citations, and outcomes | Assigned primary and second reviewers | Reviewer scores and resolved disagreements |
| Finish reports, results table, and case studies | All write; B assembles technical report, C assembles results and cases | Three-page technical report and at least two case studies |
| Rehearse setup and audit the submission | Team; D assembles final package | Another teammate runs it from the documented instructions |

Complete final evaluation by roughly **day 17**, leaving the remaining days for analysis, packaging, and corrections.

### Week 3 Progress Checks

- **6/6** final results include every required reporting field.
- All important final claims receive human review.
- **2/2** case studies complete; at least one explains an adaptive decision that affected the answer.
- Traces cover successful, unsuccessful, conflicting-evidence, and insufficient-evidence cases.
- All deliverables and the AI/tool disclosure are reviewed and ready.
- **4/4** people complete a documented technical experiment, justified fix, or component validation and contribute their report section.

## Weekly Measurement

Maintain one shared task board with these fields:

`Task | Owner | Reviewer | Estimated hours | Work type | Due date | Acceptance criteria | Status | Evidence link | Blocker`

Use work types such as implementation, experiment, integration, evaluation, or documentation.

Use **Backlog → In progress → Review → Done**. Count work as done only when its acceptance criteria pass and the reviewer confirms the linked evidence.

At the start of each week, estimate tasks in hours and freeze the weekly commitment:

**Weekly completion = estimated hours of accepted tasks ÷ estimated hours committed × 100**

Track added work separately so the denominator cannot quietly change.

Review balance alongside completion each week:

- **Technical participation:** 4/4 people deliver a reviewed coding contribution or technical experiment; final-week component validation also qualifies.
- **Effort balance:** compare planned and actual hours per person against the 10–12-hour weekly assumption. Reassign work when someone is overloaded or lacks meaningful technical work.
- **Work mix:** check each person’s implementation/experiment time against the approximate two-thirds target and discuss deviations.
- **Ownership:** each person explains a design decision and links evidence of their component’s behavior.

Do not use lines of code or commit counts as measures of contribution. Review accepted functionality, technical ownership, experiments, and effort instead. Also report the milestone checks above: task completion alone does not demonstrate a working agent.

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
