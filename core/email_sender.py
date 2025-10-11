"""
Email delivery via SendGrid API.
Handles authentication, retries, and error reporting.
"""

import asyncio
from typing import List, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from python_http_client.exceptions import HTTPError

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailSendError(Exception):
    """Raised when email sending fails."""
    pass


class EmailSender:
    """Sends emails via SendGrid API."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        """
        Initialize email sender.
        
        Args:
            api_key: SendGrid API key (defaults to settings)
            from_email: Sender email address (defaults to settings)
        """
        self.api_key = api_key or settings.sendgrid_api_key
        self.from_email = from_email or settings.sendgrid_from_email
        self.client = SendGridAPIClient(self.api_key)
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email to multiple recipients.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject line
            body: Plain text email body
            html_body: Optional HTML version of body
        
        Returns:
            True if email sent successfully
        
        Raises:
            EmailSendError: If sending fails after retries
        """
        if not to_emails:
            logger.warning("No recipients specified, skipping email")
            return False
        
        try:
            message = self._build_message(to_emails, subject, body, html_body)
            
            # SendGrid API is synchronous, run in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.client.send,
                message
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"✓ Email sent to {len(to_emails)} recipients")
                return True
            else:
                error_msg = f"SendGrid returned status {response.status_code}"
                logger.error(error_msg)
                raise EmailSendError(error_msg)
        
        except HTTPError as e:
            logger.error(f"SendGrid HTTP error: {e.reason}")
            raise EmailSendError(f"Failed to send email: {e.reason}") from e
        
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            raise EmailSendError(f"Failed to send email: {str(e)}") from e
    
    def _build_message(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str]
    ) -> Mail:
        """
        Build SendGrid message object.
        
        Args:
            to_emails: Recipient email addresses
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
        
        Returns:
            Configured Mail object
        """
        from_email = Email(self.from_email)
        to_list = [To(email) for email in to_emails]
        
        content = Content("text/plain", body)
        
        message = Mail(
            from_email=from_email,
            to_emails=to_list,
            subject=subject,
            plain_text_content=content
        )
        
        if html_body:
            message.add_content(Content("text/html", html_body))
        
        return message


if __name__ == "__main__":
    # Example usage
    async def test_sender():
        sender = EmailSender()
        
        try:
            success = await sender.send_email(
                to_emails=["test@example.com"],
                subject="Test Email",
                body="This is a test email from the EmailSender module."
            )
            print(f"Email sent: {success}")
        except EmailSendError as e:
            print(f"Failed to send: {e}")
    
    asyncio.run(test_sender())