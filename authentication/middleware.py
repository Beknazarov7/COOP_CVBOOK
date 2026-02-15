from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class ActiveUserMiddleware:
    """
    Middleware to check if the authenticated user is still active, approved, and not rejected.
    If the user is pending or rejected, they are logged out immediately.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Admin token bypass should skip this check as it doesn't rely on session user
        admin_token = request.GET.get('admin_token')
        if admin_token == 'ucacoop_admin_access_2025':
            return self.get_response(request)

        if request.user.is_authenticated:
            # Check if user is pending, rejected, or inactive
            is_pending = getattr(request.user, 'is_pending', False)
            rejected_at = getattr(request.user, 'rejected_at', None)
            is_active = getattr(request.user, 'is_active', True)

            if is_pending or rejected_at or not is_active:
                username = request.user.username
                logger.warning(f"Session access denied for user '{username}': "
                              f"is_pending={is_pending}, rejected_at={rejected_at}, is_active={is_active}")
                
                logout(request)
                
                # Check if it's an API request
                if request.path.startswith('/api/') or request.path.startswith('/cv/api/'):
                    return JsonResponse(
                        {"error": "Your account is no longer active or approved."}, 
                        status=403
                    )
                
                # For standard pages, redirect to home/login
                return redirect('home')
                
        response = self.get_response(request)
        return response
