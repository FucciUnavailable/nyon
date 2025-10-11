"""
AI-powered summarization using OpenAI API.
Generates executive summaries of weekly project updates.
"""

from typing import Optional
from openai import AsyncOpenAI, OpenAIError

from config.settings import settings
from data.models import WeeklyReport  # The PROJECT report, not GitHub
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AISummarizerError(Exception):
    """Raised when AI summarization fails."""
    pass


class AISummarizer:
    """
    Generates AI-powered executive summaries of project updates.
    
    Uses OpenAI's GPT-4o-mini model (cheapest) to create friendly,
    concise introductions for weekly engineering reports.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",  # Cheapest model
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ):
        """
        Initialize AI summarizer.
        
        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Model name (defaults to gpt-4o-mini)
            system_prompt: Custom system prompt (defaults to settings)
            max_tokens: Max tokens for response (defaults to settings)
            temperature: Creativity level 0-1 (defaults to settings)
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model
        self.system_prompt = system_prompt or settings.ai_system_prompt
        self.max_tokens = max_tokens or settings.ai_max_tokens
        self.temperature = temperature or settings.ai_temperature
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        logger.info(f"Initialized AI summarizer with model: {self.model}")
    
    async def summarize_weekly_report(
        self,
        report: WeeklyReport,
        style: str = "executive"
    ) -> str:
        """
        Generate a 2-3 line executive summary of the weekly report.
        
        This introduces the report in a friendly, professional tone
        as if the AI is the owner's assistant.
        
        Args:
            report: Weekly project report to summarize
            style: Summary style ('executive', 'casual', 'detailed')
        
        Returns:
            AI-generated summary string (2-3 lines)
        
        Raises:
            AISummarizerError: If summarization fails
        """
        try:
            # Build user prompt with project data
            user_prompt = self._build_prompt(report, style)
            
            logger.info("Requesting AI summary from OpenAI")
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            summary = response.choices[0].message.content.strip()
            
            logger.info(f"✓ Generated summary ({len(summary)} chars)")
            return summary
        
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise AISummarizerError(f"Failed to generate summary: {str(e)}") from e
        
        except Exception as e:
            logger.error(f"Unexpected error during summarization: {str(e)}")
            raise AISummarizerError(f"Summarization failed: {str(e)}") from e
    
    def _build_prompt(
        self,
        report: WeeklyReport,
        style: str
    ) -> str:
        """
        Build user prompt from weekly report.
        
        Args:
            report: Weekly project report
            style: Summary style
        
        Returns:
            Formatted prompt string
        """
        # Build project overview
        project_lines = [
            f"Week: {report.week_start.isoformat()} to {report.week_end.isoformat()}",
            f"Team: {report.team_name}",
            f"Lead: {report.lead_name}",
            "",
            "Projects this week:"
        ]
        
        for project in report.projects:
            status_emoji = project.status.emoji()
            project_lines.append(
                f"- {project.name} ({status_emoji} {project.status.display_name()}): "
                f"Completed: {project.completed} | "
                f"In Progress: {project.in_progress} | "
                f"Blockers: {project.blockers}"
            )
        
        project_lines.append("")
        project_lines.append(f"Overall: {report.get_on_track_count()}/{report.get_total_count()} projects on track")
        project_lines.append(f"Next Milestone: {report.next_milestone}")
        
        prompt = "\n".join(project_lines)
        
        # Add style-specific instructions
        if style == "executive":
            instruction = (
                "\n\nWrite a friendly, professional 2-3 line summary of this week's progress. "
                "Introduce yourself as the engineering lead's assistant. "
                "Highlight the most important accomplishments and any concerns. "
                "Keep it concise and suitable for executives."
            )
        elif style == "casual":
            instruction = (
                "\n\nWrite a casual, upbeat 2-3 line summary of this week. "
                "Introduce yourself as the lead's AI assistant. "
                "Make it feel human and positive."
            )
        else:  # detailed
            instruction = (
                "\n\nWrite a detailed 3-4 line summary covering key progress, "
                "blockers, and next steps. Introduce yourself as the assistant."
            )
        
        return prompt + instruction


if __name__ == "__main__":
    # Example usage
    import asyncio
    from datetime import date
    from data.models import ProjectUpdate, ProjectStatus
    
    async def test_summarizer():
        # Create sample weekly report
        report = WeeklyReport(
            week_start=date(2025, 10, 6),
            week_end=date(2025, 10, 11),
            lead_name="Sebastian Lee",
            team_name="Product Engineering",
            projects=[
                ProjectUpdate(
                    name="API Platform",
                    status=ProjectStatus.ON_TRACK,
                    completed="Authentication refactor, rate limiter, staging fixes",
                    in_progress="Endpoint pagination, caching optimization",
                    blockers="Waiting DB migration window from DevOps",
                    next_week="Deploy v2.3 to staging and start load testing"
                ),
                ProjectUpdate(
                    name="Web Application",
                    status=ProjectStatus.SLIGHT_DELAY,
                    status_text="Slight Delay (UI dependency)",
                    completed="Dashboard backend, notification center",
                    in_progress="Frontend integration of chart components",
                    blockers="Waiting on UI assets from design",
                    next_week="Integrate analytics SDK and finalize responsiveness"
                )
            ],
            summary_bullets=[
                "2/4 projects on or ahead of schedule",
                "Minor delay on WebApp frontend integration"
            ],
            next_milestone="Sprint 15 completion",
            next_milestone_date=date(2025, 10, 18)
        )
        
        # Generate summary
        summarizer = AISummarizer()
        
        print("\n" + "="*60)
        print("EXECUTIVE STYLE:")
        print("="*60)
        summary = await summarizer.summarize_weekly_report(report, style="executive")
        print(f"\n{summary}\n")
        
        print("="*60)
        print("CASUAL STYLE:")
        print("="*60)
        summary = await summarizer.summarize_weekly_report(report, style="casual")
        print(f"\n{summary}\n")
    
    asyncio.run(test_summarizer())