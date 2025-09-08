from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from rest_framework.permissions import AllowAny
from django.conf import settings
import logging
import sys

# Set up logging
logger = logging.getLogger(__name__)

class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if not all([username, email, password]):
            return Response({'error': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if CustomUser.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        if CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_pending=True
            )
            logger.info(f"User created: {username}, awaiting approval")
            return Response({
                'message': 'Account created. Awaiting admin approval.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_pending': user.is_pending
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating user {username}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SigninView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not all([username, password]):
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_pending:
                return Response({'error': 'Your account is pending admin approval.'}, status=status.HTTP_403_FORBIDDEN)
            if user.rejected_at is not None:
                return Response({'error': 'Your account has been rejected and cannot log in.'}, status=status.HTTP_403_FORBIDDEN)
            refresh = RefreshToken.for_user(user)
            logger.info(f"User logged in: {username}")
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_pending': user.is_pending
                }
            })
        logger.warning(f"Invalid login attempt for username: {username}")
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

def password_reset_request(request):
    print("Entering password_reset_request", file=sys.stderr)
    if request.method == 'POST':
        print("Processing POST request", file=sys.stderr)
        email = request.POST.get('email')
        if not email:
            print("No email provided", file=sys.stderr)
            return render(request, 'authentication/password_reset.html', {'error': 'Email is required.'})
        try:
            print(f"Attempting to get user with email: {email}", file=sys.stderr)
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            print(f"User with email {email} not found", file=sys.stderr)
            return render(request, 'authentication/password_reset.html', {'error': 'No user with this email exists.'})
        
        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"http://localhost:8000/api/auth/password/reset/confirm-page/{uid}/{token}/"
        
        print(f"DEBUG: Attempting to send email to {email} with reset URL: {reset_url}", file=sys.stderr)
        try:
            print("DEBUG: Calling send_mail", file=sys.stderr)
            result = send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            print(f"DEBUG: send_mail result: {result}", file=sys.stderr)
            logger.info(f"Password reset email sent to: {email}")
            return render(request, 'authentication/password_reset.html', {'success': 'Password reset link sent.'})
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            print(f"DEBUG: Email sending error details: {str(e)}", file=sys.stderr)
            return render(request, 'authentication/password_reset.html', {'error': f'Failed to send reset email: {str(e)}'})
    
    print("Rendering initial password reset form for GET request", file=sys.stderr)
    return render(request, 'authentication/password_reset.html')

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64, token):
        # Render the frontend template for GET requests
        print("Rendering password reset confirm template for GET request", file=sys.stderr)
        return render(request, 'authentication/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})

    def post(self, request, uidb64, token):
        logger.debug(f"Password reset confirm request for uidb64: {uidb64}, token: {token}")
        print("Request data:", request.data)
        new_password = request.data.get('new_password')
        if not new_password or len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            logger.error(f"Invalid user ID in password reset: {uidb64}")
            return Response({"non_field_errors": ["Invalid user ID."]}, status=status.HTTP_400_BAD_REQUEST)
        if not PasswordResetTokenGenerator().check_token(user, token):
            logger.error(f"Invalid or expired token for user {user.username}")
            return Response({"non_field_errors": ["Invalid or expired token."]}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        logger.info(f"Password reset successful for user: {user.username}")
        return Response({"message": "Password has been reset successfully.", "redirect": "#login"}, status=status.HTTP_200_OK)