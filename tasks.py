from crewai import Task
from agents import bug_reviewer, security_reviewer, style_reviewer, report_writer
from models import BugReview, SecurityReview, StyleReview, FinalReport


# Runs in parallel with security and style review tasks (async_execution=True).
# {diff} is a placeholder — the actual diff string is injected at runtime via
# crew.kickoff(inputs={"diff": diff_text})
bug_review_task = Task(
    description="""Review the following code diff for bugs, logic errors, and edge cases.

    Code diff:
    {diff}

    Look for: incorrect logic, unhandled exceptions, off-by-one errors,
    null/None handling, race conditions, and any other bugs.""",
    expected_output="A structured bug review with all issues found, their locations, severity, and a summary.",
    agent=bug_reviewer,
    output_pydantic=BugReview,
    async_execution=True
)


# Runs in parallel with bug and style review tasks (async_execution=True).
# Uses web search and code docs search to look up real CVEs and verify API usage.
security_review_task = Task(
    description="""Review the following code diff for security vulnerabilities,
    unsafe patterns, and exposed secrets.

    Code diff:
    {diff}

    Look for: injection attacks, hardcoded credentials, insecure API usage,
    broken authentication, sensitive data exposure, and known CVEs for any
    libraries used.""",
    expected_output="A structured security review with all vulnerabilities found, their locations, severity, and a summary.",
    agent=security_reviewer,
    output_pydantic=SecurityReview,
    async_execution=True
)


# Runs in parallel with bug and security review tasks (async_execution=True).
# Uses web search to look up current PEP standards and Pythonic patterns.
style_review_task = Task(
    description="""Review the following code diff for style issues and deviations
    from Python best practices.

    Code diff:
    {diff}

    Look for: PEP 8 violations, poor naming conventions, lack of readability,
    non-Pythonic patterns, missing docstrings, and structural issues.""",
    expected_output="A structured style review with all suggestions, their categories, locations, and a summary.",
    agent=style_reviewer,
    output_pydantic=StyleReview,
    async_execution=True
)


# Runs sequentially AFTER all three review tasks complete.
# context=[...] tells CrewAI to pass the outputs of the three parallel tasks
# into this task so the report writer has all findings available.
report_writing_task = Task(
    description="""Using the outputs from the bug review, security review, and style review,
    write a clear, concise, and actionable final report summarizing all findings.""",
    expected_output="A final report with a summary for each review domain and an overall assessment.",
    agent=report_writer,
    output_pydantic=FinalReport,
    context=[bug_review_task, security_review_task, style_review_task]
)
