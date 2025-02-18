import smtplib
from email.mime.text import MIMEText
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_otp_email(recipient_email: str, otp: str) -> bool:
    """
    Send OTP email with proper error handling and security measures.
    Returns True if successful, False otherwise.
    """
    try:
        # Validate environment variables
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        if not smtp_username or not smtp_password:
            logger.error("SMTP credentials not configured")
            return False

        # Configure SMTP settings
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        sender_email = os.getenv("SENDER_EMAIL", smtp_username)

        # Create email message
        msg = MIMEText(f"""
        Your verification code is: {otp}
        
        This code will expire in 10 minutes.
        If you didn't request this code, please ignore this message.
        """)
        msg["Subject"] = "Your Secure Verification Code"
        msg["From"] = sender_email
        msg["To"] = recipient_email

        # Send email using context manager
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, [recipient_email], msg.as_string())
            
        logger.info(f"OTP sent successfully to {recipient_email}")
        return True

    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to send OTP email: {str(e)}")
        return False