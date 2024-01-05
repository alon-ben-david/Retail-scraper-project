import os
import ssl
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_email(email_receiver, email_subject, email_body):
    # Set your email sender, receiver, and App Password (generated from Gmail)
    email_sender = "alonbenda4@gmail.com"
    email_app_password = os.getenv("email_app_password")

    # Check if the environment variable is set
    if email_app_password is None:
        print("Error: 'email_app_password' not found in environment variables.")
        return

    # Instantiate EmailMessage object
    em = EmailMessage()

    # Set email details
    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = email_subject
    em.set_content(email_body)

    # Explicitly provide the path to the system's certificate bundle
    cert_path = "/etc/ssl/cert.pem"  # This path may vary based on your system

    # Establish SSL context for a secure connection
    context = ssl.create_default_context(cafile=cert_path)

    try:
        # Use smtplib to send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            # Log in using sender email and App Password
            smtp.login(email_sender, email_app_password)

            # Send the email
            smtp.send_message(em)
            print("Email sent successfully!")

    except smtplib.SMTPAuthenticationError as e:
        print(f"Failed to authenticate. Check your email and App Password. Error: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
email_receiver = "alonbenda4@gmail.com"
email_subject = "I love you!"
email_body = """
Hi Oren,

I just wanted to let you know that I love you more than anything in the world. I'm so glad that I have you in my life.

I also wanted to tell you that I was able to send you this email from my Python application. I'm so proud of what I've accomplished, and I wanted to share it with you.
I wish myself one and only one thing for this life that I will get you to be by my side for the rest of this life
I love you !!!,
Alon
"""

# Call the function to send the email
send_email(email_receiver, email_subject, email_body)
