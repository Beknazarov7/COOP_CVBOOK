
import os
import sys
import django
import logging

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'CV-Book-For-UCA-Students'))

# Setup Django source
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CVBOOK.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup failed: {e}")

from authentication.utils import notify_coordinators_new_signup

print("Testing Notify Coordinators...")

# This calls the Main App API
success = notify_coordinators_new_signup(
    "test_notify@example.com",
    "TestFirstName",
    "TestLastName"
)

if success:
    print("✓ Coordinator notification sent successfully!")
else:
    print("✗ Coordinator notification failed.")
