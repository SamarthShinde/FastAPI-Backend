import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL

def generate_otp(length=6):
    """Generate a random OTP of specified length."""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(recipient_email, otp):
    """Send an email with OTP for verification."""
    # Create message
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = "Your OTP for Authentication"
    
    # Email body
    body = f"""
    <html>
    <body>
        <h2>Authentication OTP</h2>
        <p>Your One-Time Password (OTP) for authentication is:</p>
        <h1 style="color: #4CAF50; font-size: 32px;">{otp}</h1>
        <p>This OTP is valid for 10 minutes.</p>
        <p>If you did not request this OTP, please ignore this email.</p>
    </body>
    </html>
    """
    
    # Attach body to message
    message.attach(MIMEText(body, "html"))
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        # Send email
        server.send_message(message)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_welcome_email(recipient_email, username):
    """Send a welcome email to new users."""
    # Create message
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = "Welcome to Ollama Chat!"
    
    # Email body
    body = f"""
    <html>
    <body>
        <h2>Welcome to Ollama Chat, {username}!</h2>
        <p>Thank you for registering with our service.</p>
        <p>You now have access to our AI chat platform powered by Ollama models.</p>
        <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
        <p>Enjoy chatting with our AI!</p>
    </body>
    </html>
    """
    
    # Attach body to message
    message.attach(MIMEText(body, "html"))
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        # Send email
        server.send_message(message)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False 