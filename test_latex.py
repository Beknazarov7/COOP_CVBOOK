#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.insert(0, '/home/user/UCA/CV-Book-for-Cooperative-Department')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CVBOOK.settings')
django.setup()

from cv.models import CVSubmission
from cv.views import generate_pdf

# Get the latest CV
cv = CVSubmission.objects.latest('id')
print(f"Testing PDF generation for CV ID: {cv.id}")
print(f"Name: {cv.name} {cv.surname}")

try:
    pdf_url = generate_pdf(cv)
    print(f"✅ PDF generated successfully: {pdf_url}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()














