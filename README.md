# Multi-Agent PR Code Review

An automated code review pipeline built with [CrewAI](https://docs.crewai.com) that takes a GitHub PR URL, fetches the diff, and runs three specialized AI agents in parallel to review for bugs, security vulnerabilities, and style issues — then synthesizes everything into a structured final report.

## Demo
<img width="988" height="768" alt="Screenshot 2026-06-30 at 11 23 16 AM" src="https://github.com/user-attachments/assets/e4c04377-bfef-4ad3-b4bf-0bef1743b2fb" />


## How It Works

```
GitHub PR URL
      │
      ▼
fetch_pr_diff()          ← GitHub REST API, no LLM
      │
      ▼
┌─────────────────────────────────────────────────┐
│  Bug Reviewer   │ Security Reviewer │ Style      │  ← parallel
│  (GitHub tool)  │ (web search)      │ (web       │
│                 │                   │  search)   │
└─────────────────────────────────────────────────┘
      │
      ▼
  Report Writer        ← synthesizes all three outputs
      │
      ▼
review_pr_<number>.md
```

Each reviewer runs a ReAct loop (Reason → Act with tools → Observe → Reason) capped at 5 iterations. The report writer is capped at 3. A 60-second rate-limit pause fires between every agent step to stay within API RPM limits.

## Agents

| Agent | Tools | Looks For |
|---|---|---|
| Bug & Logic Reviewer | GitHub Search | Bugs, edge cases, unhandled exceptions, race conditions |
| Security Reviewer | Web Search | OWASP top 10, CVEs, injection, hardcoded secrets, insecure APIs |
| Style Reviewer | Web Search | PEP 8, naming, readability, Pythonic patterns |
| Report Writer | None | Synthesizes all findings into a final structured report |

## Output

Each run produces a markdown file named `review_pr_<number>.md` containing:
- Bug & logic findings with severity ratings
- Security vulnerabilities with severity ratings
- Style and best practice suggestions
- Overall code quality assessment

## Setup

**Requirements:** Python 3.10–3.13, [Poetry](https://python-poetry.org/)

```bash
git clone https://github.com/<your-username>/MultiAgentOrchestration_CodeReview.git
cd MultiAgentOrchestration_CodeReview
poetry install
```

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_github_personal_access_token
SERPER_API_KEY=your_serper_api_key
GEMINI_API_KEY=your_gemini_api_key
```

- **GITHUB_TOKEN** — needed to fetch PR diffs and for the GitHub Search tool. Generate at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope.
- **SERPER_API_KEY** — powers web search for the security and style reviewers. Get one at [serper.dev](https://serper.dev).
- **GEMINI_API_KEY** — the LLM backbone (Gemini 2.5 Flash). Get one at [aistudio.google.com](https://aistudio.google.com).

## Usage

```bash
poetry run python main.py
```

When prompted, paste any GitHub PR URL in any of these formats:

```
https://github.com/owner/repo/pull/123
https://github.com/owner/repo/pull/123/files
https://github.com/owner/repo/pull/123/changes
https://github.com/owner/repo/pull/123#diff-abc123
```

The pipeline handles trailing path segments and hash fragments automatically.

## Project Structure

```
├── main.py            # Entry point — orchestrates the crew
├── agents.py          # Agent definitions (role, tools, limits)
├── tasks.py           # Task definitions (prompts, expected outputs)
├── models.py          # Pydantic output schemas for structured results
├── github_fetcher.py  # PR URL parser + GitHub API diff fetcher
├── llm.py             # LLM configuration (Gemini via CrewAI)
└── pyproject.toml     # Dependencies (Poetry)
```

## Dependencies

Managed via Poetry. Key packages:

- `crewai[google-genai]` — multi-agent orchestration framework
- `crewai-tools` — SerperDevTool, GithubSearchTool
- `PyGithub` — required by GithubSearchTool
- `requests` — GitHub REST API calls
- `python-dotenv` — environment variable loading
