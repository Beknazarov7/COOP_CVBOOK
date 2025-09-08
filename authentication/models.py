from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    is_pending = models.BooleanField(default=True)  # True for pending approval
    approved_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_users')
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

    def approve(self, approver):
        self.is_pending = False
        self.approved_by = approver
        self.accepted_at = timezone.now()
        self.rejected_at = None
        self.save()

    def reject(self):
        self.is_pending = False
        self.rejected_at = timezone.now()
        self.save()