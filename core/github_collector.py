"""
GitHub data collection using PyGithub.
Fetches PRs, commits, and issues from specified repositories.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from github import Github, GithubException
from github.Repository import Repository

from config.settings import settings
from data.github_models import (
    PullRequest,
    Commit,
    Issue,
    RepositoryActivity,
    GitHubActivityReport,
    PRState,
    IssueState
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GitHubCollectorError(Exception):
    """Raised when GitHub data collection fails."""
    pass


class GitHubCollector:
    """
    Collects activity data from GitHub repositories.
    
    Uses PyGithub to fetch PRs, commits, and issues within a date range.
    """
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        repos: Optional[List[str]] = None
    ):
        """
        Initialize GitHub collector.
        
        Args:
            access_token: GitHub personal access token (defaults to settings)
            repos: List of repo names in 'owner/repo' format (defaults to settings)
        """
        self.access_token = access_token or settings.github_token
        self.repos = repos or settings.get_repos_list()
        self.client = Github(self.access_token)
        
        logger.info(f"Initialized GitHub collector for {len(self.repos)} repos")
    
    def collect_activity(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> GitHubActivityReport:
        """
        Collect activity from all configured repositories.
        
        Args:
            since: Start date for activity (defaults to 7 days ago)
            until: End date for activity (defaults to now)
        
        Returns:
            Complete activity report across all repos
        
        Raises:
            GitHubCollectorError: If collection fails
        """
        # Default to last 7 days if not specified
        if since is None:
            since = datetime.utcnow() - timedelta(days=7)
        if until is None:
            until = datetime.utcnow()
        
        logger.info(f"Collecting activity from {since.date()} to {until.date()}")
        
        repositories = []
        
        for repo_name in self.repos:
            try:
                logger.info(f"Processing repository: {repo_name}")
                repo_activity = self._collect_repo_activity(repo_name, since, until)
                repositories.append(repo_activity)
                
                logger.info(
                    f"✓ {repo_name}: "
                    f"{repo_activity.total_prs} PRs, "
                    f"{repo_activity.total_commits} commits, "
                    f"{repo_activity.total_open_issues} open issues"
                )
            
            except GithubException as e:
                logger.error(f"GitHub API error for {repo_name}: {e.status} - {e.data}")
                raise GitHubCollectorError(
                    f"Failed to collect data from {repo_name}: {e.data}"
                ) from e
            
            except Exception as e:
                logger.error(f"Unexpected error for {repo_name}: {str(e)}")
                raise GitHubCollectorError(
                    f"Failed to collect data from {repo_name}: {str(e)}"
                ) from e
        
        report = GitHubActivityReport(
            repositories=repositories,
            date_range_start=since,
            date_range_end=until
        )
        
        logger.info(
            f"✓ Collection complete: "
            f"{report.total_prs_across_repos} total PRs, "
            f"{report.total_commits_across_repos} total commits"
        )
        
        return report
    
    def _collect_repo_activity(
        self,
        repo_name: str,
        since: datetime,
        until: datetime
    ) -> RepositoryActivity:
        """
        Collect activity from a single repository.
        
        Args:
            repo_name: Repository in 'owner/repo' format
            since: Start date
            until: End date
        
        Returns:
            Repository activity data
        """
        repo = self.client.get_repo(repo_name)
        
        pull_requests = self._collect_pull_requests(repo, since, until)
        commits = self._collect_commits(repo, since, until)
        open_issues = self._collect_open_issues(repo)
        
        return RepositoryActivity(
            repo_name=repo_name,
            pull_requests=pull_requests,
            commits=commits,
            open_issues=open_issues
        )
    
    def _collect_pull_requests(
        self,
        repo: Repository,
        since: datetime,
        until: datetime
    ) -> List[PullRequest]:
        """Collect pull requests within date range."""
        prs = []
        
        # Fetch all PRs (open and closed)
        for state in ["open", "closed"]:
            for pr in repo.get_pulls(state=state, sort="updated", direction="desc"):
                # Filter by date range
                if pr.created_at < since:
                    break  # Stop if we've gone past our date range
                
                if pr.created_at > until:
                    continue
                
                # Determine PR state
                if pr.merged:
                    pr_state = PRState.MERGED
                elif pr.state == "closed":
                    pr_state = PRState.CLOSED
                else:
                    pr_state = PRState.OPEN
                
                prs.append(PullRequest(
                    number=pr.number,
                    title=pr.title,
                    state=pr_state,
                    author=pr.user.login if pr.user else "unknown",
                    created_at=pr.created_at,
                    merged_at=pr.merged_at,
                    closed_at=pr.closed_at,
                    url=pr.html_url,
                    additions=pr.additions,
                    deletions=pr.deletions,
                    changed_files=pr.changed_files
                ))
        
        return prs
    
    def _collect_commits(
        self,
        repo: Repository,
        since: datetime,
        until: datetime
    ) -> List[Commit]:
        """Collect commits within date range."""
        commits = []
        
        for commit in repo.get_commits(since=since, until=until):
            # Skip merge commits (multiple parents)
            if len(commit.parents) > 1:
                continue
            
            commits.append(Commit(
                sha=commit.sha,
                message=commit.commit.message,
                author=commit.commit.author.name,
                author_email=commit.commit.author.email,
                date=commit.commit.author.date,
                url=commit.html_url,
                additions=commit.stats.additions if commit.stats else 0,
                deletions=commit.stats.deletions if commit.stats else 0
            ))
        
        return commits
    
    def _collect_open_issues(self, repo: Repository) -> List[Issue]:
        """Collect currently open issues (no date filtering)."""
        issues = []
        
        for issue in repo.get_issues(state="open"):
            # Skip pull requests (they appear as issues in GitHub API)
            if issue.pull_request:
                continue
            
            issues.append(Issue(
                number=issue.number,
                title=issue.title,
                state=IssueState.OPEN,
                author=issue.user.login if issue.user else "unknown",
                created_at=issue.created_at,
                closed_at=issue.closed_at,
                url=issue.html_url,
                labels=[label.name for label in issue.labels],
                assignees=[assignee.login for assignee in issue.assignees]
            ))
        
        return issues


if __name__ == "__main__":
    # Example usage
    from rich import print as rprint
    import asyncio
    
    collector = GitHubCollector()
    
    try:
        # Collect last 7 days of activity
        report = collector.collect_activity()
        
        rprint(f"[green]✓ Collected data from {report.total_repos} repositories[/green]")
        rprint(f"Total PRs: {report.total_prs_across_repos}")
        rprint(f"Total Commits: {report.total_commits_across_repos}")
        rprint(f"Total Open Issues: {report.total_open_issues_across_repos}")
        
        # Print per-repo breakdown
        for repo in report.repositories:
            rprint(f"\n[bold]{repo.repo_name}[/bold]")
            rprint(f"  PRs: {repo.total_prs} ({repo.merged_prs} merged)")
            rprint(f"  Commits: {repo.total_commits}")
            rprint(f"  Open Issues: {repo.total_open_issues}")
            rprint(f"  Contributors: {', '.join(repo.unique_contributors)}")
    
    except GitHubCollectorError as e:
        rprint(f"[red]✗ Collection failed: {e}[/red]")