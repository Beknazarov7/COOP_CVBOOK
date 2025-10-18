from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from cv.views import cv_cards_view, cv_detail_view, admin_cv_cards_view
from cv.views import CVListView

# Health check endpoint for Railway - MUST be first!
@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    logger.info(f"🏥 HEALTH CHECK ENDPOINT HIT")
    logger.info(f"  Path: {request.path}")
    logger.info(f"  Method: {request.method}")
    logger.info(f"  Full path: {request.get_full_path()}")
    logger.info(f"  User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
    return JsonResponse({'status': 'healthy', 'message': 'Server is running'}, status=200)

# Middleware to log all requests to health check paths
class HealthCheckDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if 'ping' in request.path or 'health' in request.path:
            logger.warning(f"🔍 MIDDLEWARE INTERCEPT: {request.path} | Method: {request.method}")
        
        response = self.get_response(request)
        
        if 'ping' in request.path or 'health' in request.path:
            logger.warning(f"🔙 MIDDLEWARE RESPONSE: {request.path} | Status: {response.status_code}")
        
        return response

# Main URL patterns
urlpatterns = [
    # Health check MUST come first before any catch-all patterns
    # Support both with and without trailing slash to avoid 301 redirects
    path('/ping', health_check, name='health_check_no_slash'),
    path('/ping/', health_check, name='health_check'),
    path('/health', health_check, name='health_no_slash'),
    path('/health/', health_check, name='health_slash'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API routes
    path('cv/', include('cv.urls')),
    path('api/auth/', include('authentication.urls')),
    
    # Public CV views - no authentication required
    path('cv-cards/', cv_cards_view, name='public_cv_cards'),
    path('cv-detail/<int:cv_id>/', cv_detail_view, name='public_cv_detail'),
    
    # Admin access to CVBook without separate authentication
    path('admin-cv-cards/', admin_cv_cards_view, name='admin_cv_cards'),
    
    # Direct access to CV form
    path('cv-form/', TemplateView.as_view(template_name='cv/cv-form-new.html'), name='public_cv_form'),
    
    # Home page
    path('', TemplateView.as_view(template_name='cv/authentication.html'), name='home'),
    path('', include('authentication.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)