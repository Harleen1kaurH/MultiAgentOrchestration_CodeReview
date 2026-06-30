from typing import Literal
from pydantic import BaseModel, Field


class BugIssue(BaseModel):
    description: str = Field(description="A clear description of the bug or logic error found")
    location: str = Field(description="The function name, class, or line reference where the bug occurs")
    severity: Literal["low", "medium", "high"] = Field(description="How severe the bug is: low, medium, or high")


class BugReview(BaseModel):
    issues: list[BugIssue] = Field(description="List of all bugs and logic errors found in the code")
    overall_severity: Literal["low", "medium", "high"] = Field(description="Overall severity of all bugs combined: low, medium, or high")
    summary: str = Field(description="A concise paragraph summarizing all bugs and logic issues found")


class SecurityIssue(BaseModel):
    vulnerability: str = Field(description="A clear description of the security vulnerability found")
    location: str = Field(description="The function name, class, or line reference where the vulnerability occurs")
    severity: Literal["low", "medium", "high"] = Field(description="How severe the vulnerability is: low, medium, or high")


class SecurityReview(BaseModel):
    issues: list[SecurityIssue] = Field(description="List of all security vulnerabilities found in the code")
    overall_severity: Literal["low", "medium", "high"] = Field(description="Overall severity of all security issues combined: low, medium, or high")
    summary: str = Field(description="A concise paragraph summarizing all security vulnerabilities found")


class StyleIssue(BaseModel):
    category: str = Field(description="The category of the style issue, e.g. naming, readability, structure, Pythonic patterns")
    suggestion: str = Field(description="A clear, actionable suggestion for improving the code style")
    location: str = Field(description="The function name, class, or line reference where the style issue occurs")


class StyleReview(BaseModel):
    issues: list[StyleIssue] = Field(description="List of all style and best practice suggestions for the code")
    summary: str = Field(description="A concise paragraph summarizing all style and best practice feedback")


class FinalReport(BaseModel):
    bug_summary: str = Field(description="A clear summary of all bug and logic issues found by the bug reviewer")
    security_summary: str = Field(description="A clear summary of all security vulnerabilities found by the security reviewer")
    style_summary: str = Field(description="A clear summary of all style and best practice suggestions from the style reviewer")
    overall_summary: str = Field(description="An overall assessment of the code quality combining all three reviews")
