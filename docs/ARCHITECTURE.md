# Multi-agent architecture

## Overview

The research system uses three specialized agents to answer factual questions in the bounded domain of Maricopa Community College transfer pathways to ASU undergraduate programs. The agents share a structured evidence bundle, but have distinct responsibilities:

1. **Research agent** finds and retrieves candidate sources.
2. **Verification agent** evaluates whether those sources support the claims.
3. **Synthesis agent** answers from verified evidence or explicitly abstains.

An orchestrator coordinates handoffs, applies search and retrieval budgets, requests additional research when verification identifies an evidence gap, and records the run trace.

## Agent responsibilities

### Research agent

- Decompose the question into focused searches; use at least two queries for nontrivial questions.
- Prefer authoritative ASU sources, such as the Transfer Guide, degree maps, catalog, and admissions pages.
- Retrieve selected webpages and passages; search-result snippets alone are not evidence.
- Return candidate claims with source metadata and exact supporting passages.
- Respond to focused follow-up requests from the verification agent.
- Do not label claims as verified.

### Verification agent

- Evaluate each claim against its retrieved passage and assign `supported`, `contradicted`, or `insufficient`.
- Assess source authority, freshness, and independence.
- Verify linked steps independently. For example, distinguish whether MAT 265 transfers as a specific ASU course from whether that course satisfies a particular Computer Science degree requirement.
- Identify credible disagreements and consider explanations such as source date, academic year, scope, or the difference between course equivalency and degree applicability.
- Request targeted additional research when evidence is missing or unclear.
- Return insufficient evidence when public sources cannot establish a conclusion, including an individual student's final credit applicability.

### Synthesis agent

- Use verified claims and sources actually retrieved during the run.
- Answer the question directly, with citations to the supporting sources.
- Explain relevant uncertainty, conflicts, source dates, and limitations.
- Abstain explicitly when evidence is insufficient; do not turn an unverified claim into a factual answer.

## Handoff and control flow

```text
User question
    |
    v
Orchestrator -> Research agent -> candidate evidence bundle
                    ^                    |
                    |                    v
                    +-- targeted request <- Verification agent
                                             |
                                  verified claims and labels
                                             |
                                             v
                                      Synthesis agent
                                             |
                                             v
                                    Cited answer or abstention
```

The normal flow is research, verification, then synthesis. Verification may return a bounded follow-up request to research when a claim lacks support, a newer source is needed, or sources conflict. The orchestrator limits these cycles and records search queries, retrieved URLs, verification decisions, and the final response. If the budget is exhausted before evidence is sufficient, synthesis reports that limitation rather than guessing.

## Evidence handoff format

Each candidate or verified claim should be represented as a structured record with:

- Claim or research note;
- Source title and URL;
- Retrieval timestamp and source publication/update date when available;
- Supporting or contradicting quotation from the retrieved page;
- Source category or brief quality assessment;
- Verification label: `supported`, `contradicted`, or `insufficient`;
- Brief explanation of the verification decision.

Research may leave the verification label unset in its candidate bundle. The verification agent supplies the label and rationale. Synthesis uses these records to ensure citations map to retrieved evidence rather than search results it has not inspected.

## Application to the six-question suite

All six questions in [ASU Transfer.md](./ASU%20Transfer.md) use the same three-agent workflow:

- **Authoritative lookup:** research the official transfer listing; verification checks the exact course and any restrictions.
- **Multi-source comparison:** research official requirements for both programs; verification compares the same requirement categories across sources.
- **Multi-step research:** research the course equivalency and degree map; verification checks each link in the chain separately.
- **Time-sensitive research:** research the relevant admissions deadline; verification checks applicability, source date, and whether the deadline is general or program-specific.
- **Conflicting evidence:** research both relevant ASU pages; verification determines whether there is a real conflict and assesses possible date, scope, or terminology differences.
- **Insufficient evidence:** research the public credit policies and student-provided facts; verification determines whether those sources can support an exact credit-applicability conclusion. Synthesis abstains if they cannot.
