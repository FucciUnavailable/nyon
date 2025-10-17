"""
Data models for engineering reports using Pydantic.
Provides validation, serialization, and type safety.
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ProjectStatus(str, Enum):
    """Project health status with emoji representation."""
    ON_TRACK = "on_track"
    SLIGHT_DELAY = "slight_delay"
    AHEAD = "ahead"
    AT_RISK = "at_risk"
    
    def emoji(self) -> str:
        """Get emoji representation of status."""
        return {
            "on_track": "🟢",
            "slight_delay": "🟡",
            "ahead": "🔵",
            "at_risk": "🔴"
        }[self.value]
    
    def display_name(self) -> str:
        """Get human-readable status name."""
        return self.value.replace("_", " ").title()


class ProjectUpdate(BaseModel):
    """Weekly update for a single project."""
    
    name: str = Field(..., min_length=1, description="Project name")
    status: ProjectStatus = Field(default=ProjectStatus.ON_TRACK)
    status_text: str = Field(default="", description="Custom status description")
    completed: str = Field(default="None", description="What was completed this week")
    in_progress: str = Field(default="None", description="What's currently in progress")
    blockers: str = Field(default="None", description="Current blockers")
    next_week: str = Field(default="None", description="Plans for next week")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure project name is not empty or whitespace."""
        if not v.strip():
            raise ValueError("Project name cannot be empty")
        return v.strip()


class WeeklyReport(BaseModel):
    """Complete weekly engineering report."""

    week_start: date = Field(..., description="Start date of reporting week")
    week_end: date = Field(..., description="End date of reporting week")
    lead_name: str = Field(..., min_length=1, description="Name of engineering lead")
    team_name: str = Field(default="Product Engineering", description="Team name")
    projects: List[ProjectUpdate] = Field(..., min_items=1, description="Project updates")
    summary_bullets: List[str] = Field(
        default_factory=lambda: ["All projects progressing as planned"],
        description="High-level summary bullets"
    )
    next_milestone: str = Field(default="TBD", description="Next major milestone")
    next_milestone_date: Optional[date] = Field(default=None, description="Milestone target date")

    # Optional: bugs/tickets resolved this week
    bugs_fixed: int = Field(default=0, ge=0, description="Number of bugs fixed this week")
    tickets_resolved: int = Field(default=0, ge=0, description="Number of tickets resolved this week")
    features_shipped: int = Field(default=0, ge=0, description="Number of features shipped this week")
    
    @field_validator("week_end")
    @classmethod
    def validate_week_end(cls, v: date, info) -> date:
        """Ensure week_end is after week_start."""
        if "week_start" in info.data and v < info.data["week_start"]:
            raise ValueError("week_end must be after week_start")
        return v
    
    @field_validator("projects")
    @classmethod
    def validate_projects(cls, v: List[ProjectUpdate]) -> List[ProjectUpdate]:
        """Ensure at least one project exists."""
        if not v:
            raise ValueError("At least one project update is required")
        return v
    
    def get_project_list_str(self) -> str:
        """Get comma-separated list of project names."""
        return ", ".join([p.name for p in self.projects])
    
    def get_on_track_count(self) -> int:
        """Count projects that are on track or ahead."""
        return sum(
            1 for p in self.projects 
            if p.status in [ProjectStatus.ON_TRACK, ProjectStatus.AHEAD]
        )
    
    def get_total_count(self) -> int:
        """Get total number of projects."""
        return len(self.projects)


if __name__ == "__main__":
    # Example usage
    from rich import print as rprint
    
    report = WeeklyReport(
        week_start=date(2025, 10, 6),
        week_end=date(2025, 10, 11),
        lead_name="Sebastian Lee",
        projects=[
            ProjectUpdate(
                name="API Platform",
                status=ProjectStatus.ON_TRACK,
                completed="Auth refactor completed",
                in_progress="Endpoint pagination",
                blockers="Waiting on DB migration",
                next_week="Deploy v2.3 to staging"
            )
        ],
        summary_bullets=["1/1 projects on track"],
        next_milestone="Sprint 15",
        next_milestone_date=date(2025, 10, 18)
    )
    
    rprint("[green]✓ Valid report created![/green]")
    rprint(f"Projects: {report.get_project_list_str()}")
    rprint(f"On track: {report.get_on_track_count()}/{report.get_total_count()}")