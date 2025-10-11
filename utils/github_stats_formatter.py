"""
Utility for formatting GitHub activity into human-readable summaries.
Converts raw GitHub data into concise bullet points.
"""

from data.github_models import GitHubActivityReport
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GitHubStatsFormatter:
    """Formats GitHub activity reports into readable summaries."""
    
    @staticmethod
    def format_weekly_summary(report: GitHubActivityReport) -> str:
        """
        Format GitHub activity into a single-line summary.
        
        Args:
            report: GitHub activity report
        
        Returns:
            Formatted summary string (e.g., "Week's Coding: 15 PRs merged, 47 commits across 3 repos")
        """
        total_prs = report.total_prs_across_repos
        total_commits = report.total_commits_across_repos
        total_repos = report.total_repos
        
        # Count merged PRs
        merged_prs = sum(repo.merged_prs for repo in report.repositories)
        
        # Build summary parts
        parts = []
        
        if merged_prs > 0:
            parts.append(f"{merged_prs} PR{'s' if merged_prs != 1 else ''} merged")
        
        if total_commits > 0:
            parts.append(f"{total_commits} commit{'s' if total_commits != 1 else ''}")
        
        if total_repos > 1:
            parts.append(f"across {total_repos} repos")
        
        if not parts:
            return "Week's Coding: No activity tracked"
        
        summary = "Week's Coding: " + ", ".join(parts)
        
        logger.info(f"Formatted GitHub stats: {summary}")
        return summary
    
    @staticmethod
    def format_detailed_summary(report: GitHubActivityReport) -> str:
        """
        Format GitHub activity with per-repo breakdown.
        
        Args:
            report: GitHub activity report
        
        Returns:
            Multi-line formatted summary with repo details
        """
        lines = ["📊 Week's Coding Activity:"]
        
        for repo in report.repositories:
            repo_stats = []
            
            if repo.merged_prs > 0:
                repo_stats.append(f"{repo.merged_prs} PRs merged")
            
            if repo.total_commits > 0:
                repo_stats.append(f"{repo.total_commits} commits")
            
            if repo.total_open_issues > 0:
                repo_stats.append(f"{repo.total_open_issues} open issues")
            
            if repo_stats:
                lines.append(f"  • {repo.repo_name}: {', '.join(repo_stats)}")
        
        # Add contributor info
        all_contributors = set()
        for repo in report.repositories:
            all_contributors.update(repo.unique_contributors)
        
        if all_contributors:
            lines.append(f"  • {len(all_contributors)} contributor{'s' if len(all_contributors) != 1 else ''}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    from datetime import datetime, timedelta
    from data.github_models import (
        RepositoryActivity,
        PullRequest,
        Commit,
        PRState
    )
    
    # Create sample data
    pr = PullRequest(
        number=1,
        title="Test",
        state=PRState.MERGED,
        author="dev1",
        created_at=datetime.utcnow(),
        merged_at=datetime.utcnow(),
        url="https://github.com/test/repo/pull/1"
    )
    
    commit = Commit(
        sha="abc123",
        message="Test commit",
        author="dev1",
        author_email="dev1@test.com",
        date=datetime.utcnow(),
        url="https://github.com/test/repo/commit/abc123"
    )
    
    repo = RepositoryActivity(
        repo_name="test/repo",
        pull_requests=[pr],
        commits=[commit] * 10,  # Simulate 10 commits
        open_issues=[]
    )
    
    report = GitHubActivityReport(
        repositories=[repo],
        date_range_start=datetime.utcnow() - timedelta(days=7),
        date_range_end=datetime.utcnow()
    )
    
    formatter = GitHubStatsFormatter()
    
    print("\nSingle-line summary:")
    print(formatter.format_weekly_summary(report))
    
    print("\nDetailed summary:")
    print(formatter.format_detailed_summary(report))