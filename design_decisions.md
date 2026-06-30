# Code Review Pipeline — Design Decisions
**Phase 2, Project 3 | CrewAI Multi-Agent System**

---

## 1. Input: GitHub PR URL

**Decision:** Accept a GitHub Pull Request URL as input.

**Reason:** This is the most real-world scenario. Code review in engineering teams happens on PRs, not on local files. A pipeline that takes a PR URL, fetches the diff via the GitHub API, and produces a structured review maps directly to a step in a real CI/CD workflow. Far more impressive on a resume than local file input or pasted code.

**Implementation:** Parse the URL to extract owner/repo/PR number, then call the GitHub REST API (`GET /repos/{owner}/{repo}/pulls/{pull_number}/files`) using the `requests` library and a `GITHUB_TOKEN` in `.env`.

---

## 2. Review Aspects: Three Specialist Domains

**Decision:** Review three aspects — bugs & logic, security, and style & best practices.

**Reason:** These are the three dimensions a real senior engineer covers in a code review. Each is distinct enough to warrant a dedicated agent, and together they produce a complete, well-rounded review.

---

## 3. Agents: Four Total

**Decision:** Three specialist reviewer agents + one report writer agent.

| Agent | Responsibility |
|---|---|
| Bug & Logic Reviewer | Finds errors, edge cases, incorrect logic |
| Security Reviewer | Spots vulnerabilities, unsafe patterns, exposed secrets |
| Style & Best Practices Reviewer | Checks readability, naming, structure, Pythonic patterns |
| Report Writer | Synthesizes all three reviews into a final report |

**Reason:** Mirrors how real code review works — specialists do focused analysis, then a summary brings it all together. Clean, easy to explain in an interview, and each agent has a well-scoped job.

---

## 4. Process: Sequential with Parallel Reviewers

**Decision:** The three reviewer agents run in parallel (`async_execution=True`), followed by the report writer sequentially.

**Reason:** The three reviewers are independent — they don't need each other's output. Running them in parallel is faster and more efficient. The report writer must wait for all three to finish, so it runs sequentially after. This is the most logical and performant structure for this workflow.

---

## 5. Delegation: Disabled

**Decision:** `allow_delegation=False` on all four agents.

**Reason:** The workflow is fully predefined. Each agent has a clear, fixed job and doesn't need to dynamically hand off work to another agent. Enabling delegation would add unnecessary complexity and risk agents going off-script. Delegation is useful for unpredictable workflows — not structured pipelines like this one.

---

## 6. LLM: CrewAI Built-in LLM Class (LiteLLM wrapper)

**Decision:** Use CrewAI's built-in `LLM` class with `temperature=0.3`.

```python
from crewai import LLM
llm = LLM(model="gemini/gemini-2.0-flash", temperature=0.3)
```

**Reason:** CrewAI's `LLM` class wraps LiteLLM, making it model-agnostic — swapping from Gemini to OpenAI or any other provider requires changing only the model string. Consistent with the project's design principle of model-agnosticism. Cleaner than pulling in LangChain just for an LLM call (the older approach shown in the starter template). All LLM config lives in one `llm.py` file and is imported everywhere else.

---

## 7. Output: Pydantic Structured Output → Markdown File

**Decision:** Each reviewer agent returns a typed Pydantic model. The report writer produces a `FinalReport` Pydantic model which is then rendered to a `.md` file on disk.

**Seven models in `models.py`:**
- `BugIssue` — individual bug with description, location, per-issue severity
- `BugReview` — list of `BugIssue`, overall_severity, summary
- `SecurityIssue` — individual vulnerability with description, location, per-issue severity
- `SecurityReview` — list of `SecurityIssue`, overall_severity, summary
- `StyleIssue` — individual suggestion with category, suggestion, location (no severity — style issues aren't critical/blocking)
- `StyleReview` — list of `StyleIssue`, summary
- `FinalReport` — four plain string fields (bug_summary, security_summary, style_summary, overall_summary)

**Reason:** Structured output is more reliable than trusting raw LLM strings. Using Pydantic is consistent with Phase 1 work and demonstrates ability to enforce structure on LLM output. The markdown file is a tangible artifact — it can be shown in the GitHub repo as a sample output, making the project more demonstrable.

### Pydantic model decisions

**`Field` with descriptions over plain type annotations**

All fields use `Field(description="...")` rather than bare type annotations.

**Reason:** When an LLM populates a Pydantic model, the `description` inside `Field()` acts as a hint — it tells the LLM exactly what to put in each field. Without it, the LLM only has the field name to go on, which is ambiguous. Using `Field` improves output quality and is the correct pattern when Pydantic models are LLM-facing.

**`Literal["low", "medium", "high"]` for severity over plain `str`**

Severity fields use `Literal` typing, constraining the LLM to exactly three valid values.

**Reason:** A plain `str` allows the LLM to return anything ("moderate", "critical", "not severe", etc.), making the output inconsistent and hard to render. `Literal` enforces a contract — the output is always one of three known values, making downstream rendering and comparison reliable.

**Per-issue severity, not per-review severity**

Severity lives on each individual `BugIssue` and `SecurityIssue`, not as a single value on `BugReview`/`SecurityReview` (plus an `overall_severity` field for the whole review).

**Reason:** A single PR can have one critical bug and five low-severity ones. A blanket severity on the whole review loses that nuance. Per-issue severity is more accurate and more useful.

**`StyleIssue` has no severity**

Style issues have `category`, `suggestion`, and `location` — but no severity field.

**Reason:** Style issues are suggestions, not failures. Assigning severity to them (low/medium/high) would be misleading — they're not bugs or vulnerabilities. Leaving severity off keeps the model semantically honest.

**`FinalReport` outputs flat strings, not nested models**

`FinalReport` has four `str` fields rather than embedding `BugReview`, `SecurityReview`, and `StyleReview` as nested objects.

**Reason:** The Report Writer agent receives the three structured reviews as input, but its job is to synthesize and write — not to reconstruct structured objects the other agents already produced. Asking it to re-emit nested Pydantic models would be redundant and error-prone. Flat string summaries are simpler, cleaner to render to markdown, and correctly reflect the Report Writer's role.

---

## 8. Tools: Selectively Assigned Per Agent

**Decision:** Each agent gets only the tools relevant to its specific job.

| Agent | Tools |
|---|---|
| Bug & Logic Reviewer | GitHub tool, Code Interpreter |
| Security Reviewer | Web search, Code Docs Search |
| Style & Best Practices Reviewer | Web search |
| Report Writer | None |

**Rationale per assignment:**
- **Bug Reviewer + GitHub tool:** Needs broader code context beyond just the diff (e.g., the full file) to reason about logic errors and edge cases.
- **Bug Reviewer + Code Interpreter:** Can execute snippets to verify edge cases — directly relevant to finding bugs.
- **Security Reviewer + Web search:** Can look up real CVEs and known vulnerabilities for libraries used in the code in real time.
- **Security Reviewer + Code Docs Search:** Can verify whether security-relevant APIs are being used correctly per their documentation.
- **Style Reviewer + Web search:** Can look up current Python best practices and style guidelines.
- **Report Writer + no tools:** Synthesizes text it already has — no external lookups needed.
- **Code Interpreter excluded from Security Reviewer:** Avoid executing potentially unsafe code in a security context.

**Reason for selective assignment:** Intentional tool assignment is more defensible in an interview than giving all agents all tools. Fewer tool calls also means faster, cheaper runs.

---

## Dependencies to Add

```
requests          # GitHub API calls
```
Run: `poetry add requests`
