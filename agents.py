import os
from crewai import Agent
from crewai_tools import SerperDevTool, GithubSearchTool
from dotenv import load_dotenv

from llm import llm

load_dotenv()

# Initialize tools
# SerperDevTool requires SERPER_API_KEY in .env
# GithubSearchTool requires GITHUB_TOKEN in .env
web_search = SerperDevTool()
github_tool = GithubSearchTool(gh_token=os.getenv("GITHUB_TOKEN"))


# Finds bugs, logic errors, and edge cases in the code diff.
# Has access to GitHub tool for fetching broader file context beyond the diff,
# and Code Interpreter to execute snippets and verify edge cases.
bug_reviewer = Agent(
    role="Senior Bug & Logic Reviewer",
    goal="Identify all bugs, logic errors, and edge cases in the code diff",
    backstory="""You are a senior software engineer with 10+ years of experience
    finding subtle bugs and logic errors in code reviews. You think in edge cases,
    race conditions, and failure modes that other engineers miss.""",
    tools=[github_tool],
    allow_delegation=False,
    verbose=True,
    llm=llm
)


# Identifies security vulnerabilities, unsafe patterns, and exposed secrets.
# Has access to web search to look up real CVEs and known vulnerabilities,
# and Code Docs Search to verify whether security-relevant APIs are used correctly.
security_reviewer = Agent(
    role="Senior Security Reviewer",
    goal="Identify all security vulnerabilities, unsafe patterns, and exposed secrets in the code diff",
    backstory="""You are a cybersecurity expert and senior engineer specializing in
    secure code review. You have deep knowledge of OWASP top 10, common CVEs,
    injection attacks, authentication flaws, and insecure API usage. You never
    miss a vulnerability.""",
    tools=[web_search],
    allow_delegation=False,
    verbose=True,
    llm=llm
)


# Reviews code style, readability, and adherence to Python best practices.
# Has access to web search to look up current PEP standards and Pythonic patterns.
style_reviewer = Agent(
    role="Senior Style & Best Practices Reviewer",
    goal="Identify all style issues, readability problems, and deviations from Python best practices in the code diff",
    backstory="""You are a senior Python engineer with a strong emphasis on clean,
    readable, and maintainable code. You are deeply familiar with PEP 8, PEP 20
    (the Zen of Python), and modern Pythonic patterns. You care about naming
    conventions, code structure, and writing code that other engineers can
    understand and maintain easily.""",
    tools=[web_search],
    allow_delegation=False,
    verbose=True,
    llm=llm
)


# Synthesizes findings from all three reviewers into a clean final report.
# No tools needed — works purely from the text output of the other three agents.
report_writer = Agent(
    role="Senior Technical Report Writer",
    goal="Synthesize the findings from all three reviewers into a clear, concise, and actionable final report",
    backstory="""You are a senior technical writer and engineer who excels at
    taking complex technical findings and distilling them into clear, structured
    reports. You write for an engineering audience — precise, direct, and
    actionable. You never add fluff or repeat yourself.""",
    tools=[],
    allow_delegation=False,
    verbose=True,
    llm=llm
)
