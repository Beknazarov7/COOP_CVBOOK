from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.template.loader import render_to_string
# from rest_framework_simplejwt.tokens import RefreshToken  # Disabled for deployment
from .models import CustomUser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import logging
import sys
import re
import sqlite3
import os

# Set up logging
logger = logging.getLogger(__name__)

class SignupView(APIView):
    permission_classes = [AllowAny]
    
    def validate_password_strength(self, password):
        """Validate password strength"""
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        
        if not re.search(r'[A-Z]', password):
            return "Password must contain at least one uppercase letter."
        
        if not re.search(r'[a-z]', password):
            return "Password must contain at least one lowercase letter."
        
        if not re.search(r'\d', password):
            return "Password must contain at least one number."
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)."
        
        return None
    
    def check_email_exists_in_management_system(self, email):
        """Check if email exists in the management system database"""
        try:
            # Path to the management system database
            management_db_path = os.path.join(settings.BASE_DIR, '..', 'UCA-Co-op-Website', 'db.sqlite3')
            if os.path.exists(management_db_path):
                conn = sqlite3.connect(management_db_path)
                cursor = conn.cursor()
                
                # Check if email exists in main user table
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
                main_user_exists = cursor.fetchone()[0] > 0
                
                # Check if email exists in CVBook users table
                cursor.execute("SELECT COUNT(*) FROM cvbook_users WHERE email = ?", (email,))
                cvbook_user_exists = cursor.fetchone()[0] > 0
                
                conn.close()
                return main_user_exists or cvbook_user_exists
        except Exception as e:
            logger.error(f"Error checking email in management system: {str(e)}")
            return False
        
        return False
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        auto_approve = request.data.get('auto_approve', False)
        
        if not all([username, email, password]):
            return Response({'error': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'Please enter a valid email address.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password strength
        password_error = self.validate_password_strength(password)
        if password_error:
            return Response({'error': password_error}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username already exists
        if CustomUser.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email already exists in CVBook
        if CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email exists in management system (Removed as per request)
        # if not auto_approve and self.check_email_exists_in_management_system(email):
        #     return Response({'error': 'Email already exists in the system. Please use a different email or login if you have an account.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create user with appropriate approval status
            is_pending = not auto_approve
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_pending=is_pending,
                is_active=True
            )
            
            # If auto-approved, set approval timestamp
            if auto_approve:
                user.accepted_at = timezone.now()
                user.save()
                logger.info(f"User created and auto-approved: {username}")
                message = 'Account created and approved. User can login immediately.'
            else:
                logger.info(f"User created: {username}, awaiting approval")
                message = 'Account created. Awaiting admin approval.'
                
                # Send email to the user
                from .utils import send_postmark_email, notify_coordinators_new_signup
                
                user_subject = "Your CVBook Access Request is Pending"
                
                context = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'role': 'student', # Default role for CVBook signups
                    'current_year': timezone.now().year,
                }
                user_html = render_to_string('emails/pending_approval.html', context)
                
                send_postmark_email(email, user_subject, user_html, "Your CVBook request is pending approval.")
                
                # Notify coordinators
                notify_coordinators_new_signup(email, first_name, last_name)

            
            return Response({
                'message': message,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_pending': user.is_pending,
                    'is_approved': not user.is_pending
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating user {username}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SigninView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not all([email, password]):
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user by email
        try:
            user_obj = CustomUser.objects.get(email=email)
            username = user_obj.username
        except CustomUser.DoesNotExist:
            # Return generic error to prevent email enumeration
            logger.warning(f"Login attempt for non-existent email: {email}")
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_pending:
                return Response({'error': 'Your account is pending admin approval.'}, status=status.HTTP_403_FORBIDDEN)
            if user.rejected_at is not None:
                return Response({'error': 'Your account has been rejected and cannot log in.'}, status=status.HTTP_403_FORBIDDEN)
            # JWT tokens disabled for deployment - using session authentication
            # refresh = RefreshToken.for_user(user)
            logger.info(f"User logged in: {username}")
            return Response({
                # 'refresh': str(refresh),
                # 'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_pending': user.is_pending
                }
            })
        logger.warning(f"Invalid login attempt for email: {email}")
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
        
        from django.urls import reverse
        relative_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        reset_url = request.build_absolute_uri(relative_url)
        
        # In case build_absolute_uri doesn't work well behind proxies (like Railway)
        # we can check environment variables
        env_site_url = os.environ.get('SITE_URL')
        if env_site_url:
            if env_site_url.endswith('/'):
                env_site_url = env_site_url[:-1]
            reset_url = f"{env_site_url}{relative_url}"
        
        print(f"DEBUG: Attempting to send email to {email} with reset URL: {reset_url}", file=sys.stderr)
        try:
            from .utils import send_postmark_email
            
            subject = 'Password Reset Request'
            
            context = {
                'reset_url': reset_url,
                'current_year': timezone.now().year,
            }
            html_content = render_to_string('emails/password_reset.html', context)
            
            text_content = f"Click the link to reset your password: {reset_url}"
            
            result = send_postmark_email(email, subject, html_content, text_content)
            
            if result:
                logger.info(f"Password reset email sent to: {email}")
                return render(request, 'authentication/password_reset.html', {'success': 'Password reset link sent.'})
            else:
                raise Exception("Postmark API returned failure")
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            return render(request, 'authentication/password_reset.html', {'error': f'Failed to send reset email. Please try again later.'})

    
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

@api_view(['GET'])
@permission_classes([AllowAny])  # Allow access for management system
def users_list_api(request):
    """
    API endpoint to list external users for management system
    """
    try:
        # Get all users (external users are those who signed up through CVBook)
        users = CustomUser.objects.all().order_by('-date_joined')
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'company': getattr(user, 'company', ''),  # If company field exists
                'is_approved': not user.is_pending,  # Use is_pending field (inverted)
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            })
        
        return Response(users_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in users_list_api: {str(e)}")
        return Response({'error': 'Failed to fetch users'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow access for management system
def user_management_action(request):
    """
    Handle user management actions from admin panel
    """
    try:
        action = request.data.get('action')
        user_id = request.data.get('user_id')
        
        if not user_id or not action:
            return Response({'success': False, 'message': 'Missing required parameters'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.get(id=user_id)
        
        if action == 'approve':
            user.is_pending = False
            user.is_active = True
            user.accepted_at = timezone.now()
            user.rejected_at = None
            user.save()
            
            # Send approval email
            from .utils import send_postmark_email
            subject = "Your CVBook Request has been Approved"
            
            # Get login URL from request, setting, or environment
            site_url = os.environ.get('SITE_URL')
            if not site_url:
                site_url = request.build_absolute_uri('/')
            
            if site_url.endswith('/'):
                site_url = site_url[:-1]
            login_url = f"{site_url}/#login"
            
            context = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': 'student', # Default role
                'login_url': login_url,
                'current_year': timezone.now().year,
            }
            html = render_to_string('emails/account_approved.html', context)
            
            send_postmark_email(user.email, subject, html, "Your CVBook request has been approved.")
            
            return Response({'success': True, 'message': 'User approved successfully'})
            
        elif action == 'reject':
            user.is_pending = False
            user.is_active = False
            user.rejected_at = timezone.now()
            user.save()
            
            # Send rejection email
            from .utils import send_postmark_email
            subject = "Your CVBook Request Status"
            
            context = {
                'first_name': user.first_name,
                'current_year': timezone.now().year,
            }
            html = render_to_string('emails/account_rejected.html', context)
            
            send_postmark_email(user.email, subject, html, "Your CVBook request has been declined.")
            
            return Response({'success': True, 'message': 'User rejected successfully'})

            
        elif action == 'delete':
            user.delete()
            return Response({'success': True, 'message': 'User deleted successfully'})
            
        else:
            return Response({'success': False, 'message': 'Invalid action'}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
    except CustomUser.DoesNotExist:
        return Response({'success': False, 'message': 'User not found'}, 
                      status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in user_management_action: {str(e)}")
        return Response({'success': False, 'message': str(e)}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)