import os
import requests
from dotenv import load_dotenv

load_dotenv()


def parse_pr_url(url: str) -> tuple[str, str, int]:
    """
    Parses a GitHub PR URL and extracts the owner, repo name, and PR number.

    Expected format: https://github.com/owner/repo/pull/123

    Returns a tuple of (owner, repo, pr_number).
    Raises a clear ValueError if the URL is malformed.
    """
    try:
        # Strip trailing slash and drop any fragment (#...) before splitting
        clean_url = url.strip("/").split("#")[0]
        parts = clean_url.split("/")

        # Validate that this looks like a GitHub PR URL
        if "github.com" not in parts or "pull" not in parts:
            raise ValueError

        # Anchor extraction on the "pull" segment so trailing path segments
        # like /changes, /files, /commits, or hash fragments don't break parsing.
        # e.g. ["https:", "", "github.com", "owner", "repo", "pull", "123", "changes"]
        pull_idx = parts.index("pull")
        owner = parts[pull_idx - 2]
        repo = parts[pull_idx - 1]
        pr_number = int(parts[pull_idx + 1])  # int() will raise ValueError if not a number

        return owner, repo, pr_number

    except (ValueError, IndexError):
        raise ValueError(
            f"Invalid GitHub PR URL: '{url}'. "
            "Expected format: https://github.com/owner/repo/pull/123"
        )


def fetch_pr_diff(url: str) -> str:
    """
    Fetches the code diff for a GitHub PR and returns it as a single string.

    Each changed file is prefixed with its filename so agents know which
    file each diff chunk belongs to. Binary files and renamed-only files
    (which have no patch) are skipped.

    Returns a single string ready to pass to CrewAI agents as input.
    """
    # Parse the URL to get the components we need for the API call
    owner, repo, pr_number = parse_pr_url(url)

    # Load GitHub token from .env — required for authentication
    # Without it, GitHub rejects the request or enforces a very low rate limit
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment variables. Add it to your .env file.")

    # Headers tell GitHub who we are and what response format we want
    # Authorization: Bearer proves our identity using the token
    # Accept: tells GitHub to respond in their recommended JSON format
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    # GitHub API endpoint that returns all changed files for a PR
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"

    # Make the HTTP GET request to the GitHub API
    # response is a Response object — not yet usable data
    response = requests.get(api_url, headers=headers)

    # Raise a clear HTTPError if GitHub returned 401, 404, 403, etc.
    # Without this, bad responses would silently pass through
    response.raise_for_status()

    # .json() converts the raw response text into a Python list of dicts
    # Each dict represents one changed file in the PR
    files = response.json()

    diff_text = []
    for file in files:
        filename = file["filename"]  # Always present — crash if missing (unexpected API change)
        patch = file.get("patch", "")  # Not always present — binary/renamed files have no patch

        if patch:
            # Prefix each file's diff with its filename so agents have context
            diff_text.append(f"### {filename}\n{patch}")

    # Join all file diffs into one string separated by blank lines
    return "\n\n".join(diff_text)
