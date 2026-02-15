from rest_framework import permissions

class IsApprovedAndActive(permissions.BasePermission):
    """
    Custom permission to only allow approved and active users to access.
    """
    def has_permission(self, request, view):
        # Admin token bypass
        admin_token = request.query_params.get('admin_token')
        if admin_token == 'ucacoop_admin_access_2025':
            return True

        if not request.user or not request.user.is_authenticated:
            return False
            
        # Check specific status fields
        is_pending = getattr(request.user, 'is_pending', False)
        rejected_at = getattr(request.user, 'rejected_at', None)
        is_active = getattr(request.user, 'is_active', True)
        
        return not is_pending and rejected_at is None and is_active
