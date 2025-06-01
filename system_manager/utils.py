from mailjet_rest import Client
import os
from django.conf import settings


# Initialize the Mailjet Client
# api_key = os.getenv('MAILJET_API_KEY', 'your_public_key')
# api_secret = os.getenv('MAILJET_API_SECRET', 'your_private_key')
# mailjet = Client(auth=(api_key, api_secret), version='v3.1')

def send_email(subject, to_email, text_content, html_content=None, from_email=None, from_name="BiyerJuti"):
    """
    Sends an email using Mailjet's REST API.
    
    Args:
        subject (str): Subject of the email.
        to_email (str): Recipient's email address.
        text_content (str): Plain text version of the email content.
        html_content (str): HTML version of the email content (optional).
        from_email (str): Sender's email address (optional).
        from_name (str): Sender's name (default: "Your App").
    
    Returns:
        tuple: (status_code, response_json)
    """
    # Use the default sender email if not provided
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    # Initialize the Mailjet client
    mailjet = Client(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')

    # Prepare the email data
    data = {
        'Messages': [
            {
                "From": {
                    "Email": from_email,
                    "Name": from_name
                },
                "To": [
                    {
                        "Email": to_email,
                        "Name": "Recipient"
                    }
                ],
                "Subject": subject,
                "TextPart": text_content,
                "HTMLPart": html_content if html_content else text_content
            }
        ]
    }

    # Send the email and return the result
    result = mailjet.send.create(data=data)
    print(result)
    return result.status_code, result.json()


