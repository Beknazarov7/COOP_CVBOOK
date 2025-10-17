from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from cv.views import cv_cards_view, cv_detail_view, admin_cv_cards_view

from cv.views import CVListView

# Simple health check view
@csrf_exempt
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "CV Book"}, status=200)

# Even simpler health check for Railway
@csrf_exempt
def simple_health_check(request):
    return HttpResponse("OK", status=200)

# Minimal health check - just returns 200
@csrf_exempt
def minimal_health_check(request):
    return HttpResponse(status=200)

urlpatterns = [
    # Health check endpoint for Railway (primary)
    path('health/', health_check, name='health_check'),
    
    # Simple health check for Railway
    path('ping/', simple_health_check, name='ping'),
    
    # Minimal health check - just HTTP 200
    path('status/', minimal_health_check, name='status'),
    
    # Root health check as fallback
    path('', simple_health_check, name='root_health_check'),
    
    path('admin/', admin.site.urls),
    path('cv/', include('cv.urls')),
    path('api/auth/', include('authentication.urls')),
    
    # API routes are now handled in cv.urls
    
    # Public CV views - no authentication required
    path('cv-cards/', cv_cards_view, name='public_cv_cards'),
    path('cv-detail/<int:cv_id>/', cv_detail_view, name='public_cv_detail'),
    
    # Admin access to CVBook without separate authentication
    path('admin-cv-cards/', admin_cv_cards_view, name='admin_cv_cards'),
    
    # Direct access to CV form
    path('cv-form/', TemplateView.as_view(template_name='cv/cv-form-new.html'), name='public_cv_form'),
    
    # Authentication page
    path('auth/', TemplateView.as_view(template_name='cv/authentication.html'), name='authentication'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)