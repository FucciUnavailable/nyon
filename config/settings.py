"""
Configuration management using Pydantic Settings.
Loads environment variables and validates them at startup.
"""

from pathlib import Path
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # GitHub settings
    github_token: str = Field(..., description="GitHub Personal Access Token")
    github_repos: str = Field(..., description="Comma-separated list of repos (owner/repo)")
    
    # SendGrid settings
    sendgrid_api_key: str = Field(..., description="SendGrid API key")
    sendgrid_from_email: str = Field(..., description="Sender email address")
    report_recipient_emails: str = Field(..., description="Comma-separated recipient emails")
    
    # OpenAI settings
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model name")
    
    # Report settings
    report_output_dir: Path = Field(default=Path("./reports"), description="Directory for generated reports")
    log_level: str = Field(default="INFO", description="Logging level")
    
    @field_validator("github_repos")
    @classmethod
    def parse_repos(cls, v: str) -> str:
        """Validate GitHub repos format."""
        repos = [r.strip() for r in v.split(",")]
        for repo in repos:
            if "/" not in repo:
                raise ValueError(f"Invalid repo format: {repo}. Expected 'owner/repo'")
        return v
    
    @field_validator("report_output_dir", mode="before")
    @classmethod
    def create_output_dir(cls, v: str | Path) -> Path:
        """Ensure output directory exists."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_repos_list(self) -> List[str]:
        """Get list of repositories from comma-separated string."""
        return [r.strip() for r in self.github_repos.split(",")]
    
    def get_recipients_list(self) -> List[str]:
        """Get list of email recipients from comma-separated string."""
        return [e.strip() for e in self.report_recipient_emails.split(",")]


# Singleton instance
settings = Settings()


if __name__ == "__main__":
    # Example usage / validation test
    from rich import print as rprint
    
    rprint("[bold green]✓ Configuration loaded successfully![/bold green]")
    rprint(f"Repos: {settings.get_repos_list()}")
    rprint(f"Recipients: {settings.get_recipients_list()}")
    rprint(f"Output dir: {settings.report_output_dir}")