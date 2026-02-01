import requests
import logging
import os
from django.conf import settings

logger = logging.getLogger(__name__)

def send_postmark_email(to_email, subject, html_content, text_content=None):
    """
    Send an email using Postmark API via requests
    """
    api_key = os.environ.get('POSTMARK_API_KEY')
    if not api_key:
        logger.error("POSTMARK_API_KEY not set in environment")
        return False
        
    payload = {
        "From": os.environ.get('DEFAULT_FROM_EMAIL', 'admin@ucacoop.org'),
        "To": to_email,
        "Subject": subject,
        "HtmlBody": html_content,
        "TextBody": text_content or "",
        "MessageStream": "outbound"
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Postmark-Server-Token": api_key
    }
    
    try:
        response = requests.post("https://api.postmarkapp.com/email", json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"Postmark error for {to_email}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {str(e)}")
        return False

def notify_coordinators_new_signup(user_email, first_name, last_name):
    """
    Notify coordinators about a new signup via the main project's API.
    """
    # Try to coordinate with the main site URL
    # If not set, we'll try to guess based on the incoming request if possible, 
    # but here we don't have the request object.
    # We'll use environment variables.
    
    main_site_url = os.environ.get('MAIN_SITE_URL', 'http://localhost:8000')
    coordinator_endpoint = os.environ.get('COORDINATOR_NOTIFICATION_URL')
    
    if not coordinator_endpoint:
        # Use standard API endpoint exposed in cvbook/urls.py
        coordinator_endpoint = f"{main_site_url}/cvbook/notify-coordinators-api/"
        
    api_key = os.environ.get('CVBOOK_API_KEY', '') # Shared secret
    
    logger.info(f"Notifying coordinators at {coordinator_endpoint} for user {user_email}")
    
    try:
        payload = {
            'email': user_email,
            'first_name': first_name,
            'last_name': last_name,
            'type': 'cvbook_signup'
        }
        headers = {'X-API-Key': api_key}
        response = requests.post(coordinator_endpoint, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info("Main project successfully notified of new CVBook user")
            return True
        else:
            logger.error(f"Failed to notify main project. Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Failed to notify main project: {str(e)}")
        return False

