#!/usr/bin/env python3
"""
Test script to verify that students are being fetched from the Co-op database
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/home/student/coop/CV-Book-For-UCA-Students')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CVBOOK.settings')
django.setup()

from cv.admin_views import get_all_seniors

print("Testing get_all_seniors() function...")
print("=" * 60)

students = get_all_seniors()

if not students:
    print("❌ No students found!")
    print("\nPossible issues:")
    print("1. Database path is incorrect")
    print("2. No students in the Co-op database")
    print("3. Database connection error")
else:
    print(f"✅ Found {len(students)} student(s):\n")
    for i, student in enumerate(students, 1):
        print(f"{i}. {student['name']} {student['surname']}")
        print(f"   Email: {student['email']}")
        print(f"   Major: {student['major']}")
        print(f"   Cohort: {student['cohort_status']}")
        print(f"   Graduation Year: {student['graduation_year']}")
        print()

print("=" * 60)
print("Test complete!")
