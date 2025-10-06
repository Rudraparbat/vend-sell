import logging
import smtplib
from typing import Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from asyncio import sleep
from functools import wraps
import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_USE_TLS = True




class EmailException(Exception):
    """Custom exception for email sending errors"""
    pass

async def send_email_with_retry(
    recipient: str | List[str],
    subject: str,
    body: str,
    is_html: bool = False,
    max_retries: int = 3,
    retry_delay: int = 5
) -> bool:
    """
    Send email with retry logic and comprehensive error handling.
    
    Args:
        recipient: Single email address or list of addresses
        subject: Email subject line
        body: Email body content (plain text or HTML)
        is_html: Whether body contains HTML content
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries
    
    Returns:
        bool: True if email sent successfully, False otherwise
        
    Raises:
        EmailException: If all retry attempts fail
    """
    # Convert single recipient to list
    recipients = [recipient] if isinstance(recipient, str) else recipient
    
    for attempt in range(1, max_retries + 1):
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = EMAIL_FROM
            message['To'] = ', '.join(recipients)
            
            # Attach body content
            mime_type = 'html' if is_html else 'plain'
            message.attach(MIMEText(body, mime_type, 'utf-8'))
            
            # Create SMTP connection
            with smtplib.SMTP(
                EMAIL_HOST, 
                EMAIL_PORT,
                timeout=30
            ) as server:
                server.ehlo()
                
                if EMAIL_USE_TLS:
                    server.starttls()
                    server.ehlo()
                
                server.login(
                    EMAIL_USER, 
                   EMAIL_PASSWORD
                )
                
                # Send email
                server.send_message(message)
                
            logger.info(
                f"Email sent successfully to {recipients} "
                f"on attempt {attempt}"
            )
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(
                f"SMTP authentication failed on attempt {attempt}: {str(e)}"
            )
            # Don't retry authentication errors
            raise EmailException(
                f"Email authentication failed: {str(e)}"
            )
            
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(
                f"Recipients refused on attempt {attempt}: {str(e)}"
            )
            raise EmailException(
                f"Invalid recipient email address: {str(e)}"
            )
            
        except smtplib.SMTPException as e:
            logger.error(
                f"SMTP error on attempt {attempt}/{max_retries}: {str(e)}"
            )
            if attempt < max_retries:
                await sleep(retry_delay)
            else:
                raise EmailException(
                    f"Failed to send email after {max_retries} attempts: {str(e)}"
                )
                
        except ConnectionError as e:
            logger.error(
                f"Connection error on attempt {attempt}/{max_retries}: {str(e)}"
            )
            if attempt < max_retries:
                await sleep(retry_delay)
            else:
                raise EmailException(
                    f"Failed to connect to email server: {str(e)}"
                )
                
        except TimeoutError as e:
            logger.error(
                f"Timeout error on attempt {attempt}/{max_retries}: {str(e)}"
            )
            if attempt < max_retries:
                await sleep(retry_delay * 2)
            else:
                raise EmailException(
                    f"Email sending timed out after {max_retries} attempts"
                )
                
        except Exception as e:
            logger.error(
                f"Unexpected error on attempt {attempt}/{max_retries}: "
                f"{type(e).__name__}: {str(e)}"
            )
            if attempt < max_retries:
                await sleep(retry_delay)
            else:
                raise EmailException(
                    f"Unexpected error sending email: {str(e)}"
                )
    
    return False
