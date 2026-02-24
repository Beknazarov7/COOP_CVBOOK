from django.urls import path
from .views import (
    SignupView,
    SigninView,
    PasswordResetConfirmView,
    password_reset_request,
    users_list_api,
    user_management_action,
    current_user_view,
    signout_view,
)
from . import admin_approval

urlpatterns = [
    # ── Auth core ─────────────────────────────────────────────────────────
    path('signup/',    SignupView.as_view(),  name='signup'),
    path('signin/',    SigninView.as_view(),  name='signin'),
    path('signout/',   signout_view,          name='signout'),   # NEW
    path('me/',        current_user_view,     name='me'),        # NEW – session check

    # ── Password reset ────────────────────────────────────────────────────
    path('password/reset/request/',                             password_reset_request,         name='password_reset'),
    path('password/reset/confirm-page/<uidb64>/<token>/',       PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # ── Admin / management ────────────────────────────────────────────────
    path('pending-users/',              admin_approval.pending_users_view, name='pending_users'),
    path('users/list/',                 users_list_api,           name='users_list_api'),
    path('users/management/action/',    user_management_action,   name='user_management_action'),
]