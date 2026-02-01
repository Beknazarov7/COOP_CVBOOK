
import os
import sys
import django

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'CV-Book-For-UCA-Students'))

# Setup Django source
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CVBOOK.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup failed: {e}")
    # Try to proceed anyway if it's just path issues, but utils needs settings potentially? 
    # utils.py uses os.environ for API key, not settings.

from authentication.utils import send_postmark_email

print("Testing Postmark Email Sending...")
api_key = os.environ.get('POSTMARK_API_KEY')
print(f"API Key present: {'Yes' if api_key else 'No'}")
if api_key:
    # Partial reveal for debug
    print(f"API Key start: {api_key[:5]}...")

to_email = "afzunovmustafo12@gmail.com" # Using admin email for test
success = send_postmark_email(
    to_email, 
    "Test Email from Debug Script", 
    "<html><body><h1>Test</h1><p>This is a test email.</p></body></html>"
)

if success:
    print("✓ Email sent successfully!")
else:
    print("✗ Email sending failed.")
