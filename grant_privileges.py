import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CVBOOK.settings')
django.setup()

from authentication.models import CustomUser
from django.contrib.auth.models import Group

user_email = "beknazarovnaim7@gmail.com"

try:
    user = CustomUser.objects.get(email=user_email)
    
    # 1. Grant Admin Privileges
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"GRANTED ADMIN PRIVILEGES to {user.username} (is_staff=True, is_superuser=True)")

    # 2. Grant Coordinator Privileges
    coordinator_group, created = Group.objects.get_or_create(name='Coordinator')
    if created:
        print("Created 'Coordinator' group.")
    else:
        print("'Coordinator' group already exists.")
    
    user.groups.add(coordinator_group)
    print(f"ADDED {user.username} to 'Coordinator' group.")

    # Verification
    user.refresh_from_db()
    print("-" * 30)
    print(f"User: {user.username}")
    print(f"is_staff: {user.is_staff}")
    print(f"is_superuser: {user.is_superuser}")
    print(f"Groups: {[g.name for g in user.groups.all()]}")
    print("-" * 30)
    print("SUCCESS: User privileges updated.")

except CustomUser.DoesNotExist:
    print(f"ERROR: User with email {user_email} not found.")
except Exception as e:
    print(f"ERROR: {e}")
