from django.urls import path
from .views import SignupView, SigninView, PasswordResetView, PasswordResetConfirmView
from rest_framework_simplejwt.views import TokenRefreshView
from .import admin_approval

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('pending-users/', admin_approval.pending_users_view, name='pending_users'),

]