from django.urls import path
from .views import CVSubmitView, CVDetailView, CVListView, CVPDFView, CVEditView, access_denied_view
from django.views.generic import TemplateView
from . import views, admin_views

app_name = 'cv'  # Register the 'cv' namespace

urlpatterns = [
    # API and public views
    path('submit/', views.CVSubmitView.as_view(), name='cv-submit'),
    path('cards/', views.cv_cards_view, name='cv_cards'),    
    path('list/', CVListView.as_view(), name='cv-list'),
    path('<int:cv_id>/', CVDetailView.as_view(), name='cv-detail'),
    path('<int:cv_id>/download/', CVPDFView.as_view(), name='cv-download'),
    path('<int:cv_id>/edit/', CVEditView.as_view(), name='cv-edit'),
    path('create/', TemplateView.as_view(template_name='cv/cv-form-new.html'), name='cv-create'),
    path('detail/<int:cv_id>/', views.cv_detail_view, name='cv_detail'),
    
    # API routes for management system
    path('api/list/', CVListView.as_view(), name='api-cv-list'),
    path('api/management/action/', views.cv_management_action, name='cv_management_action'),
    
    # Admin management views
    path('admin/dashboard/', admin_views.cv_management_dashboard, name='cv-admin-dashboard'),
    path('admin/student-cvs/', admin_views.student_cvs_management, name='admin-student-cvs'),
    path('admin/external-cvs/', admin_views.external_cvs_management, name='admin-external-cvs'),
    path('admin/toggle-publication/<int:cv_id>/', admin_views.toggle_cv_publication, name='toggle-cv-publication'),
    path('admin/toggle-approval/<int:cv_id>/', admin_views.toggle_cv_approval, name='toggle-cv-approval'),
    path('admin/bulk-action/', admin_views.bulk_cv_action, name='bulk-cv-action'),

    # Error pages
    path('access-denied/', access_denied_view, name='cv-access-denied'),
]