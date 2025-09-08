from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from authentication.models import CustomUser  # Adjust import based on app name

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_admin)
def pending_users_view(request):
    # Query all users by status
    pending_users = CustomUser.objects.filter(is_pending=True)
    accepted_users = CustomUser.objects.filter(is_pending=False, accepted_at__isnull=False)
    rejected_users = CustomUser.objects.filter(is_pending=False, rejected_at__isnull=False)
    
    if request.method == 'POST':
        user_ids = request.POST.getlist('approve')
        decline_ids = request.POST.getlist('decline')
        current_user = request.user  # Admin performing the action
        
        # Approve selected users
        if user_ids:
            users_to_approve = CustomUser.objects.filter(id__in=user_ids)
            for user in users_to_approve:
                user.approve(current_user)
            messages.success(request, f"Approved {len(users_to_approve)} user(s)")
        
        # Reject selected users
        if decline_ids:
            users_to_decline = CustomUser.objects.filter(id__in=decline_ids)
            for user in users_to_decline:
                user.reject()
            messages.warning(request, f"Rejected {len(users_to_decline)} user(s)")
        
        # Redirect to refresh the page and reflect changes
        return redirect('pending_users')
    
    return render(request, 'admin/pending_users.html', {
        'pending_users': pending_users,
        'accepted_users': accepted_users,
        'rejected_users': rejected_users
    })