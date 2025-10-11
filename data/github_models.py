"""
Data models for GitHub activity tracking.
Represents PRs, commits, issues, and repository metadata.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class PRState(str, Enum):
    """Pull request state."""
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class IssueState(str, Enum):
    """Issue state."""
    OPEN = "open"
    CLOSED = "closed"


class PullRequest(BaseModel):
    """Represents a GitHub pull request."""
    
    number: int = Field(..., description="PR number")
    title: str = Field(..., description="PR title")
    state: PRState = Field(..., description="PR state")
    author: str = Field(..., description="GitHub username of author")
    created_at: datetime = Field(..., description="Creation timestamp")
    merged_at: Optional[datetime] = Field(None, description="Merge timestamp")
    closed_at: Optional[datetime] = Field(None, description="Close timestamp")
    url: HttpUrl = Field(..., description="PR URL")
    additions: int = Field(default=0, description="Lines added")
    deletions: int = Field(default=0, description="Lines deleted")
    changed_files: int = Field(default=0, description="Number of files changed")
    
    @property
    def is_merged(self) -> bool:
        """Check if PR was merged."""
        return self.state == PRState.MERGED or self.merged_at is not None


class Commit(BaseModel):
    """Represents a GitHub commit."""
    
    sha: str = Field(..., description="Commit SHA hash")
    message: str = Field(..., description="Commit message")
    author: str = Field(..., description="Commit author name")
    author_email: str = Field(..., description="Author email")
    date: datetime = Field(..., description="Commit timestamp")
    url: HttpUrl = Field(..., description="Commit URL")
    additions: int = Field(default=0, description="Lines added")
    deletions: int = Field(default=0, description="Lines deleted")
    
    @property
    def short_sha(self) -> str:
        """Get shortened commit SHA."""
        return self.sha[:7]
    
    @property
    def short_message(self) -> str:
        """Get first line of commit message."""
        return self.message.split("\n")[0]


class Issue(BaseModel):
    """Represents a GitHub issue."""
    
    number: int = Field(..., description="Issue number")
    title: str = Field(..., description="Issue title")
    state: IssueState = Field(..., description="Issue state")
    author: str = Field(..., description="GitHub username of author")
    created_at: datetime = Field(..., description="Creation timestamp")
    closed_at: Optional[datetime] = Field(None, description="Close timestamp")
    url: HttpUrl = Field(..., description="Issue URL")
    labels: List[str] = Field(default_factory=list, description="Issue labels")
    assignees: List[str] = Field(default_factory=list, description="Assigned users")
    
    @property
    def is_open(self) -> bool:
        """Check if issue is still open."""
        return self.state == IssueState.OPEN


class RepositoryActivity(BaseModel):
    """Aggregated activity data for a single repository."""
    
    repo_name: str = Field(..., description="Repository full name (owner/repo)")
    collected_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Collection timestamp"
    )
    pull_requests: List[PullRequest] = Field(
        default_factory=list,
        description="Pull requests in date range"
    )
    commits: List[Commit] = Field(
        default_factory=list,
        description="Commits in date range"
    )
    open_issues: List[Issue] = Field(
        default_factory=list,
        description="Currently open issues"
    )
    
    @property
    def total_prs(self) -> int:
        """Total number of pull requests."""
        return len(self.pull_requests)
    
    @property
    def merged_prs(self) -> int:
        """Number of merged pull requests."""
        return sum(1 for pr in self.pull_requests if pr.is_merged)
    
    @property
    def total_commits(self) -> int:
        """Total number of commits."""
        return len(self.commits)
    
    @property
    def total_open_issues(self) -> int:
        """Number of open issues."""
        return len(self.open_issues)
    
    @property
    def unique_contributors(self) -> List[str]:
        """List of unique contributor usernames."""
        contributors = set()
        contributors.update(pr.author for pr in self.pull_requests)
        contributors.update(commit.author for commit in self.commits)
        return sorted(contributors)


class GitHubActivityReport(BaseModel):
    """Complete GitHub activity report across multiple repositories."""
    
    repositories: List[RepositoryActivity] = Field(
        default_factory=list,
        description="Activity from each repository"
    )
    date_range_start: Optional[datetime] = Field(
        None,
        description="Start of date range for activity"
    )
    date_range_end: Optional[datetime] = Field(
        None,
        description="End of date range for activity"
    )
    
    @property
    def total_repos(self) -> int:
        """Total number of repositories tracked."""
        return len(self.repositories)
    
    @property
    def total_prs_across_repos(self) -> int:
        """Total PRs across all repos."""
        return sum(repo.total_prs for repo in self.repositories)
    
    @property
    def total_commits_across_repos(self) -> int:
        """Total commits across all repos."""
        return sum(repo.total_commits for repo in self.repositories)
    
    @property
    def total_open_issues_across_repos(self) -> int:
        """Total open issues across all repos."""
        return sum(repo.total_open_issues for repo in self.repositories)


if __name__ == "__main__":
    # Example usage
    from rich import print as rprint
    
    pr = PullRequest(
        number=123,
        title="Add new feature",
        state=PRState.MERGED,
        author="developer1",
        created_at=datetime.utcnow(),
        merged_at=datetime.utcnow(),
        url="https://github.com/owner/repo/pull/123",
        additions=150,
        deletions=50,
        changed_files=5
    )
    
    rprint(f"[green]✓ Created PR #{pr.number}[/green]")
    rprint(f"Merged: {pr.is_merged}")
    rprint(f"Changes: +{pr.additions}/-{pr.deletions}")