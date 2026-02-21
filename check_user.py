import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CVBOOK.settings')
django.setup()

from authentication.models import CustomUser
from django.contrib.auth.models import Group

user_email = "beknazarovnaim7@gmail.com"

print("-" * 50)
print(f"Checking for user: {user_email}")
try:
    user = CustomUser.objects.get(email=user_email)
    print(f"User found: {user.username}")
    print(f"is_staff: {user.is_staff}")
    print(f"is_superuser: {user.is_superuser}")
    print(f"Groups: {[g.name for g in user.groups.all()]}")
except CustomUser.DoesNotExist:
    print("User NOT found.")

print("-" * 50)
print("Existing Groups:")
for g in Group.objects.all():
    print(f"- {g.name}")
print("-" * 50)
