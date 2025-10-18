from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from cv.views import cv_cards_view, cv_detail_view, admin_cv_cards_view
from cv.views import CVListView

# Health check endpoint for Railway
def health_check(request):
    return JsonResponse({'status': 'healthy', 'message': 'Server is running'})

urlpatterns = [
    path('ping/', health_check, name='health_check'),  # Railway healthcheck
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
    path('', TemplateView.as_view(template_name='cv/authentication.html'), name='home'),
    path('', include('authentication.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)