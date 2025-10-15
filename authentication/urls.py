from django.urls import path
from .views import SignupView, SigninView, PasswordResetConfirmView, password_reset_request, users_list_api, user_management_action
# from rest_framework_simplejwt.views import TokenRefreshView  # Disabled for deployment
from . import admin_approval

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Disabled for deployment
    path('password/reset/request/', password_reset_request, name='password_reset'),
    path('password/reset/confirm-page/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('pending-users/', admin_approval.pending_users_view, name='pending_users'),
    path('users/list/', users_list_api, name='users_list_api'),
    path('users/management/action/', user_management_action, name='user_management_action'),
]