**CSE 571: Evidence-Seeking Web Research Agent Project** 

# **1 Project Overview** 

**Task.** Build an AI agent that answers factual research questions using live web-search and webpage-retrieval tools. The agent must decide what to search for, inspect retrieved sources, collect and verify evidence, identify missing or conflicting information, and produce a concise answer whose factual claims are supported by citations to sources it actually retrieved. 

This is not a one-shot chatbot or a single-prompt summarization task. Your system must execute a multi-step perception-reasoning-tool-use-memory-verification-answer loop: 

Question _→_ Generate queries _→_ Search _→_ Retrieve pages _→_ 

Extract evidence _→_ Verify claims _→_ Answer, abstain, or search again _._ 

The core goal is to build an agent that can gather evidence from the web and distinguish between claims that are supported, contradicted, or insufficiently supported by the sources it retrieved. 

# **2 Required Task Suite** 

Each team must choose **one bounded application domain** and create its own web-research task suite within that domain. The instructional staff will provide the project requirements only; teams are responsible for selecting their domain, creating their own questions, selecting their web-search and webpage-retrieval tools, and designing their evaluation. 

Possible domains include finance, law, travel, hospitality, education, sports, public policy, technology, health information, sustainability, or another approved domain. The selected domain must be narrow enough that the six questions form a coherent application rather than six unrelated web searches. 

Each team must define exactly **six concrete factual research questions** : one question from each required task category below. Teams must finalize their six questions before conducting their final evaluation. The final report must use the same six questions and clearly state the selected application domain. 

1. **Authoritative factual lookup.** Find a specific factual answer and support it using an official, primary, or otherwise authoritative source when one is available. 

2. **Multi-source comparison.** Compare two entities, policies, products, organizations, events, or options using a clearly stated criterion and at least two independent sources. 

3. **Multi-step or multi-hop research.** Answer a question that requires resolving at least two linked subquestions or combining evidence from more than one document. 

4. **Time-sensitive research.** Determine a current or recently updated fact. The agent must consider source date, update date, and source authority. 

5. **Conflicting-evidence research.** Identify credible disagreement between sources and explain the disagreement when possible, such as a difference in date, definition, methodology, jurisdiction, scope, or underlying data. 

6. **Insufficient-evidence or abstention question.** Determine whether available web evidence supports a conclusion. If it does not, the agent must explicitly report uncertainty or abstain rather than inventing an answer. 

Teams may include additional questions in their report, but these do not replace the six required questions. 

1 

## **Illustrative Example: Finance Domain** 

The following examples illustrate a possible six-question task suite in a finance domain. These are examples only; teams may choose finance or another bounded domain. 

1. **Authoritative factual lookup:** “What was the most recently reported annual dividend per share for Company X, according to its investor-relations or regulatory filing?” 

2. **Multi-source comparison:** “Compare the expense ratios and stated investment objectives of Fund A and Fund B using their official fund documents.” 

3. **Multi-step or multi-hop research:** “Which company acquired Company X, when was the acquisition completed, and what consideration was reported in the official announcement or regulatory filing?” 

4. **Time-sensitive research:** “What is the current target range for the federal funds rate according to the most recent Federal Reserve statement?” 

5. **Conflicting-evidence research:** “Do two credible financial sources report the same revenue-growth figure for Company X? If they differ, identify the reporting period, accounting definition, currency conversion, or source date that may explain the discrepancy.” 

6. **Insufficient-evidence or abstention question:** “Based only on publicly available sources retrieved by the agent, is there sufficient evidence to conclude that Company X will outperform Company Y during the next quarter? If not, explain why the evidence is insufficient.” 

# **3 Required Agent Behavior** 

Your agent must satisfy all of the following requirements: 

- Accept a natural-language factual research question as input. 

- Generate at least two focused search queries for a nontrivial question. 

- Use a web-search tool and retrieve the full text of selected webpages. Search-result snippets alone are not sufficient evidence. 

- Use at least two independent sources when answering a nontrivial question, unless the agent explicitly justifies why a single authoritative primary source is sufficient. 

- Maintain a structured evidence record for each important factual claim. 

- Make at least one adaptive decision based on intermediate results. For example, the agent may refine a query, seek a primary source, seek a newer source, investigate a counterclaim, retrieve additional evidence, or decide that available evidence is insufficient. 

- Verify claims against retrieved evidence before producing the final answer. 

- Produce citations only for sources that the agent actually retrieved during the run. 

- State uncertainty, disagreement, or insufficient evidence rather than presenting an unsupported claim as fact. 

- Log all important actions, including search queries, retrieved URLs, evidence records, verification decisions, final citations, and final answer. 

2 

# **4 Evidence Verification Requirement** 

A citation is not automatically valid merely because it is related to the topic. Before including an important factual claim in the final answer, the agent must create an evidence record that links the claim to supporting material from a retrieved webpage. 

At a minimum, each evidence record must contain: 

- The factual claim or research note; 

- The title and URL of the retrieved source; 

- The retrieval timestamp; 

- A supporting quotation or passage from the source; 

- A source category or brief source-quality assessment; 

- A verification label: `supported` , `contradicted` , or `insufficient` ; 

- A brief explanation of the verification decision. 

The final response must follow these rules: 

- Claims labeled `supported` may be presented as factual claims with citations. 

- Claims labeled `contradicted` must be described as disputed or uncertain. The response should cite the relevant conflicting sources where appropriate. 

- Claims labeled `insufficient` must be omitted, qualified, or explicitly reported as unresolved. 

- The final answer must not cite search-result snippets, sources that were not retrieved, invented URLs, or unsupported references. 

- Important factual claims should have citations at an appropriate level of detail. One citation should not be used to support several unrelated claims unless the source actually supports all of them. 

# **5 Live Web Search and Reproducibility** 

This project uses the live web. Search rankings, webpage content, availability, and publication dates may change over time. Therefore, every evaluated run must create a trace that allows the teaching staff to inspect the evidence used by the agent. 

For every search and retrieval action, the trace must include: 

- Execution timestamp; 

- Search query; 

- Search results returned to the agent, including title, URL, snippet, and rank when available; 

- URLs selected for page retrieval; 

- Retrieved page title and relevant extracted text; 

- Evidence records created from the page; 

- Final answer and claim-level citations. 

The system will be evaluated based on the evidence and trace submitted for the run. Teams are not expected to reproduce identical search rankings if the same question is run again at a later date. 

3 

# **6 Suggested Tool Interface** 

Teams may choose their own implementation tools. A minimal tool set could include the following: 

|**Tool**|**Purpose**|
|---|---|
|`web_search(query)`|Returns ranked search results, including title, URL, snippet,<br>rank, and available metadata.|
|`fetch_page(url)`|Retrieves readable text from a selected webpage.|
|`source_metadata(url)`|Returns available publisher, domain, author, publication date,<br>update date, and source-type information.|
|`save_evidence(claim, quote,`|Stores a structured claim-evidence-source record with a verifi-|
|`url, label)`|cation label.|
|`list_evidence()`|Returns evidence records collected so far for review before<br>final answer.|



Teams may use additional tools, such as a calculator, date parser, document parser, citation formatter, source-ranking tool, or contradiction-checking tool. Each tool must be documented with its purpose, inputs, outputs, and limitations. 

# **7 Agent Architectures** 

Teams may select one of the following architectures. 

## **Single-Agent System** 

A single agent plans searches, retrieves pages, records evidence, verifies claims, and writes the final answer. This is the standard project route and is fully sufficient for full credit. 

## **Multi-Agent System (Optional Advanced Route)** 

Teams may implement a multi-agent system with two or more specialized roles. For example: 

- A **research agent** that decomposes the question, generates search queries, and retrieves candidate sources; 

- A **verification agent** that reviews candidate claims against retrieved passages and assigns `supported` , `contradicted` , or `insufficient` labels; 

- A **synthesis agent** that writes the final response using only evidence that passed verification. 

A multi-agent implementation must include clear role definitions, separate role prompts or state, a documented information-sharing mechanism, and a structured evidence handoff between roles. 

A multi-agent system is not automatically better than a single-agent system. Teams choosing this route must compare it with a simpler single-agent version or an ablated version of their system and discuss whether the additional roles improved correctness, verification quality, source quality, efficiency, or robustness. 

# **8 Role of Ollama and LangChain** 

**Ollama (recommended model runtime).** Ollama can run an open-weight language model locally and expose it through a local API. In this project, the model serves as the agent’s reasoning and action-selection 

4 

component: it receives the user question, search results, retrieved evidence, and prior trace information, then decides whether to search, retrieve, verify, synthesize, abstain, or take another action. Teams can also choose any other LLM as the reasoning backbone, Gemini Pro and Chat GPT Edu are free for ASU students. 

**LangChain (optional, advanced).** LangChain may be used as an orchestration framework for connecting language models to tools, message history, structured outputs, and repeated model-tool execution loops. It is optional: a direct Python implementation using Ollama or another approved language-model interface receives equal credit if it provides the required tool use, evidence tracking, verification behavior, logging, and evaluation. 

Using Ollama or LangChain alone does not make a system agentic. The agentic component comes from the closed-loop behavior: observing tool results, maintaining evidence state, selecting actions, verifying claims, responding to missing or conflicting evidence, and changing later decisions based on earlier outcomes. 

# **9 Example Structured Tool Action** 

The agent should use machine-readable actions rather than relying on free-form text as an execution interface. For example: 

```
{
```

```
"tool":"web_search",
```

```
"arguments":{
```

```
"query":"officialsourcecurrentpolicyrenewableportfoliostandardArizona"
},
```

```
"reason":"Thecurrentsourcesaresecondarysummaries;seekanofficialprimarysource."
}
```

An example evidence record is: 

```
{
```

```
"claim":"Thepolicybecameeffectiveon[date].",
```

```
"source_title":"OfficialPolicyPage",
"url":"https://example.gov/policy",
"retrieval_timestamp":"2026-09-27T15:20:00-07:00",
"supporting_excerpt":"Thepolicybecameeffectiveon[date].",
```

```
"source_quality":"Officialgovernmentsource",
```

```
"verification_label":"supported",
```

```
"verification_reason":"Theretrievedpassagedirectlystatestheeffectivedate."
```

```
}
```

# **10 Search Budget and Stopping Policy** 

To prevent unbounded search and make efficiency measurable, the agent must use a documented search and retrieval budget. Teams should specify their limits in the project configuration. A reasonable default budget is: 

- At most 8 web-search calls per question; 

- At most 12 webpage retrievals per question; 

- At most 3 query-refinement rounds per question; 

- At most 20 model/tool turns per question. 

5 

Teams may propose different limits if they justify them in the report. The agent must stop when it has sufficient verified evidence, detects credible disagreement that can be reported, determines that evidence is insufficient, or reaches its assigned tool budget. 

# **11 Baseline and Evaluation** 

Each team must compare its proposed system against a simple baseline. Acceptable baselines include: 

- A one-shot language-model answer using the question and a fixed set of search snippets; 

- A fixed-query retrieval pipeline with no adaptive query refinement; 

- A search-and-summarize system that retrieves sources but does not use claim-level verification. 

The final evaluation will assess the team’s six-question task suite, agent traces, evidence records, verification decisions, baseline comparison, and analysis of successes and failures. The teaching staff may inspect the submitted traces and manually check a subset of final claims and citations. 

Suggested evaluation criteria are shown below. 

|**Criterion**|**What it measures**|
|---|---|
|Answer correctness|Whether the response agrees with instructor-reviewed reference<br>facts and appropriately addresses all parts of the question.|
|Citation validity|Whether each sampled citation actually supports the claim it is<br>attached to.|
|Citation completeness|Whether important factual claims are supported rather than left<br>uncited.|
|Verification quality|Whether the agent correctly distinguishes supported, contradicted,<br>and insufficiently supported claims.|
|Source quality|Whether the agent appropriately prefers official, primary, credible,<br>and current sources when available.|
|Adaptivity|Whether the agent changes its query, retrieval, or verification<br>behavior after inspecting intermediate results.|
|Robustness|Whether the agent avoids fabricated citations and appropriately<br>reports uncertainty, disagreement, or insufficient evidence.|
|Efficiency|Whether the agent uses a reasonable number of searches, page<br>fetches, model calls, and tool actions within its stated budget.|



# **12 Preliminary Report: Rational-Agent Analysis** 

Submit a one-page preliminary report describing your proposed agent. The report must map the project to the four factors that determine rational behavior: 

1. **Performance measure:** Define what counts as success. Consider correctness, citation validity, citation completeness, source quality, verification quality, robustness to missing evidence, and tool-use cost. 

2. **Prior knowledge:** State what the agent knows before acting, such as tool descriptions, source-quality heuristics, citation format, verification rules, stopping policy, and task constraints. 

3. **Available actions:** List the tools and actions available to the agent, such as query generation, web search, page retrieval, evidence storage, verification, source comparison, final answering, and abstention. 

6 

4. **Percept sequence:** Describe what the agent observes over time, including the user question, search results, retrieved webpage content, metadata, stored evidence, verification labels, and prior tool outputs. 

The report must also classify and justify the task environment using the following six properties: 

- Fully observable or partially observable; 

- Single-agent or multi-agent; 

- Deterministic or stochastic/nondeterministic; 

- Episodic or sequential; 

- Static or dynamic; 

- Discrete or continuous. 

# **13 Deliverables** 

- Source code on a private Git repository or in a ZIP archive. Code will not be graded line-by-line, but it must be available if requested for verification or reproducibility. 

- A one-page preliminary report containing the rational-agent and environment-property analysis (20/100). 

- A three-page technical report describing the system architecture, model/runtime, tools, prompts or decision policies, evidence-memory representation, claim-verification process, stopping policy, baseline, and limitations (25/100). 

- A results table for the team’s six required questions. For each question, include the task category, final answer, final outcome (answered, disputed, or abstained), number of searches, number of retrieved pages, number of model/tool calls, number of cited sources, and verification results (30/100). 

- Complete agent traces for representative successful, unsuccessful, conflicting-evidence, and insufficientevidence cases (10/100). 

- At least two qualitative case studies. At least one should show an adaptive search or verification decision that materially affected the final answer (10/100). 

- A disclosure of all model names and versions, frameworks, APIs, external data, prompts, tools, and generative-AI assistance used during development (5/100). 

- For multi-agent systems only: a comparison with a simpler single-agent or ablated version of the system, together with an analysis of whether specialization improved the results. 

7 

