# Admissions Agent Coding Plan

Prioritized from existing strengths to remaining spec gaps. Focus on the admissions agent; UI work is out of scope.

## Strongly implemented

1. **Structured evidence:** Keep the per-run evidence records with exact retrieved passages, source details, retrieval timestamps, quality notes, verification labels, and reasons. Preserve the tool checks that quotes belong to successfully retrieved pages.
2. **Research tools and trace:** Retain live web search, full-page retrieval, and JSON traces containing search results, retrieved text, evidence, and the final answer.
3. **Bounded domain and task suite:** Keep the first-year ASU admissions scope, UArizona comparison, and six-question suite aligned with the required task categories.

## Partially met — strengthen next

4. **Adaptive research and verification:** Add checks that the agent actually follows evidence gaps, conflicting claims, and source quality with follow-up research; assess whether verification labels and reasons match the retrieved context.
5. **Evidence-backed citations:** Validate the final answer so factual claims cite only retrieved sources and are supported by saved evidence; flag unsupported or uncited claims for revision or abstention.
6. **Required research behavior:** Make two focused searches and independent sources the default for nontrivial questions, while allowing a justified single authoritative source. Confirm selected pages are retrieved before relying on their snippets.
7. **Budget and trace completeness:** Enforce the 20 model/tool-turn and 3 query-refinement-round limits, alongside the existing 8-search and 12-retrieval limits. Record counts and decisions in each trace.

## Not yet demonstrated — complete before claiming full compliance

8. **Evaluation and baseline:** Run the finalized six questions, inspect evidence and answers against expected outcomes, and compare results with a simple baseline. Report accuracy/support, citation quality, abstention, source quality, and tool cost.
