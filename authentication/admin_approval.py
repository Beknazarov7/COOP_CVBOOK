from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from authentication.models import CustomUser  # Use your custom user model

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_admin)
def pending_users_view(request):
    # Explicitly filter only pending users (is_active=False)
    pending_users = CustomUser.objects.filter(is_pending=True)
    
    if request.method == 'POST':
        user_ids = request.POST.getlist('approve')
        decline_ids = request.POST.getlist('decline')
        
        # Approve selected users
        if user_ids:
            users_to_approve = CustomUser.objects.filter(id__in=user_ids)
            for user in users_to_approve:
                user.is_pending = False
                user.save()
            messages.success(request, f"Approved {len(users_to_approve)} user(s)")
        
        # Decline selected users
        if decline_ids:
            users_to_decline = CustomUser.objects.filter(id__in=decline_ids)
            for user in users_to_decline:
                user.delete()  # Or add a 'declined' field and set it to True
            messages.warning(request, f"Declined {len(users_to_decline)} user(s)")
        
        # Redirect to refresh the page and reflect changes
        return redirect('pending_users')
    
    return render(request, 'admin/pending_users.html', {'pending_users': pending_users})