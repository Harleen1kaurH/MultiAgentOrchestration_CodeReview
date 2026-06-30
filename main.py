from crewai import Crew, Process
from dotenv import load_dotenv

from github_fetcher import fetch_pr_diff
from agents import bug_reviewer, security_reviewer, style_reviewer, report_writer
from tasks import bug_review_task, security_review_task, style_review_task, report_writing_task
from models import FinalReport

load_dotenv()


def render_report(report: FinalReport, pr_url: str) -> str:
    """Renders the FinalReport Pydantic model into a markdown string."""
    return f"""# Code Review Report

**PR:** {pr_url}

---

## Bug & Logic Review
{report.bug_summary}

---

## Security Review
{report.security_summary}

---

## Style & Best Practices Review
{report.style_summary}

---

## Overall Assessment
{report.overall_summary}
"""


def save_report(report_md: str, pr_url: str) -> str:
    """Saves the markdown report to a file named after the PR number."""
    # Extract the PR number anchored on "pull/" so trailing segments don't break it
    parts = pr_url.strip("/").split("#")[0].split("/")
    pull_idx = parts.index("pull")
    pr_number = parts[pull_idx + 1]
    filename = f"review_pr_{pr_number}.md"
    with open(filename, "w") as f:
        f.write(report_md)
    return filename


if __name__ == "__main__":
    print("## Code Review Pipeline")
    print("-" * 40)

    # Get the PR URL from the user
    pr_url = input("Enter GitHub PR URL: ").strip()

    # Fetch the diff from GitHub API before starting the crew
    print("\nFetching PR diff from GitHub...")
    diff = fetch_pr_diff(pr_url)
    print(f"Fetched diff for PR: {pr_url}\n")

    # Assemble the crew with all four agents and tasks
    # Process.sequential ensures the report writer runs after the three parallel reviewers
    crew = Crew(
        agents=[bug_reviewer, security_reviewer, style_reviewer, report_writer],
        tasks=[bug_review_task, security_review_task, style_review_task, report_writing_task],
        process=Process.sequential,
        verbose=True
    )

    # inputs={"diff": diff} fills in the {diff} placeholder in all three reviewer task descriptions
    print("Starting code review crew...\n")
    result = crew.kickoff(inputs={"diff": diff})

    # result.pydantic gives us the FinalReport from the last task (report_writing_task)
    report: FinalReport = result.pydantic

    # Render the structured report to markdown and save to disk
    report_md = render_report(report, pr_url)
    filename = save_report(report_md, pr_url)

    print(f"\nReview complete. Report saved to: {filename}")
