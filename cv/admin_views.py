from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import CVSubmission
import json

@staff_member_required
def cv_management_dashboard(request):
    """
    Main dashboard for CV management with separate tabs for student and external CVs
    """
    # Get statistics
    total_cvs = CVSubmission.objects.count()
    student_cvs = CVSubmission.objects.filter(is_uca_student=True).count()
    external_cvs = CVSubmission.objects.filter(is_uca_student=False).count()
    published_cvs = CVSubmission.objects.filter(is_published_to_cvbook=True).count()
    pending_approval = CVSubmission.objects.filter(admin_approved=False).count()
    
    # Get recent CVs
    recent_cvs = CVSubmission.objects.select_related().order_by('-submitted_at')[:10]
    
    # Get cohort statistics for students
    cohort_stats = CVSubmission.objects.filter(is_uca_student=True).values('cohort_status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_cvs': total_cvs,
        'student_cvs': student_cvs,
        'external_cvs': external_cvs,
        'published_cvs': published_cvs,
        'pending_approval': pending_approval,
        'recent_cvs': recent_cvs,
        'cohort_stats': cohort_stats,
    }
    
    return render(request, 'cv/admin/cv_dashboard.html', context)

@staff_member_required
def student_cvs_management(request):
    """
    Management view specifically for UCA student CVs
    """
    # Get filter parameters
    cohort_filter = request.GET.get('cohort', '')
    major_filter = request.GET.get('major', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Build queryset
    cvs = CVSubmission.objects.filter(is_uca_student=True)
    
    if cohort_filter:
        cvs = cvs.filter(cohort_status=cohort_filter)
    
    if major_filter:
        cvs = cvs.filter(major__icontains=major_filter)
    
    if status_filter == 'published':
        cvs = cvs.filter(is_published_to_cvbook=True)
    elif status_filter == 'unpublished':
        cvs = cvs.filter(is_published_to_cvbook=False)
    elif status_filter == 'approved':
        cvs = cvs.filter(admin_approved=True)
    elif status_filter == 'pending':
        cvs = cvs.filter(admin_approved=False)
    
    if search_query:
        cvs = cvs.filter(
            Q(name__icontains=search_query) |
            Q(surname__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    cvs = cvs.order_by('-submitted_at')
    
    # Pagination
    paginator = Paginator(cvs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique values for filters
    cohorts = CVSubmission.objects.filter(is_uca_student=True).values_list('cohort_status', flat=True).distinct()
    majors = CVSubmission.objects.filter(is_uca_student=True).values_list('major', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'cohorts': cohorts,
        'majors': majors,
        'current_filters': {
            'cohort': cohort_filter,
            'major': major_filter,
            'status': status_filter,
            'search': search_query,
        }
    }
    
    return render(request, 'cv/admin/student_cvs.html', context)

@staff_member_required
def external_cvs_management(request):
    """
    Management view specifically for external CVs
    """
    # Get filter parameters
    major_filter = request.GET.get('major', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Build queryset
    cvs = CVSubmission.objects.filter(is_uca_student=False)
    
    if major_filter:
        cvs = cvs.filter(major__icontains=major_filter)
    
    if status_filter == 'published':
        cvs = cvs.filter(is_published_to_cvbook=True)
    elif status_filter == 'unpublished':
        cvs = cvs.filter(is_published_to_cvbook=False)
    elif status_filter == 'approved':
        cvs = cvs.filter(admin_approved=True)
    elif status_filter == 'pending':
        cvs = cvs.filter(admin_approved=False)
    
    if search_query:
        cvs = cvs.filter(
            Q(name__icontains=search_query) |
            Q(surname__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    cvs = cvs.order_by('-submitted_at')
    
    # Pagination
    paginator = Paginator(cvs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique values for filters
    majors = CVSubmission.objects.filter(is_uca_student=False).values_list('major', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'majors': majors,
        'current_filters': {
            'major': major_filter,
            'status': status_filter,
            'search': search_query,
        }
    }
    
    return render(request, 'cv/admin/external_cvs.html', context)

@staff_member_required
def toggle_cv_publication(request, cv_id):
    """
    AJAX endpoint to toggle CV publication status
    """
    if request.method == 'POST':
        cv = get_object_or_404(CVSubmission, id=cv_id)
        cv.is_published_to_cvbook = not cv.is_published_to_cvbook
        cv.save()
        
        return JsonResponse({
            'success': True,
            'published': cv.is_published_to_cvbook,
            'message': f'CV {"published to" if cv.is_published_to_cvbook else "removed from"} CVBook'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@staff_member_required
def toggle_cv_approval(request, cv_id):
    """
    AJAX endpoint to toggle CV approval status
    """
    if request.method == 'POST':
        cv = get_object_or_404(CVSubmission, id=cv_id)
        cv.admin_approved = not cv.admin_approved
        cv.save()
        
        return JsonResponse({
            'success': True,
            'approved': cv.admin_approved,
            'message': f'CV {"approved" if cv.admin_approved else "approval removed"}'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@staff_member_required
def bulk_cv_action(request):
    """
    Handle bulk actions on CVs
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        cv_ids = data.get('cv_ids', [])
        
        if not cv_ids:
            return JsonResponse({'success': False, 'message': 'No CVs selected'})
        
        cvs = CVSubmission.objects.filter(id__in=cv_ids)
        
        if action == 'publish':
            cvs.update(is_published_to_cvbook=True)
            message = f'{len(cv_ids)} CV(s) published to CVBook'
        elif action == 'unpublish':
            cvs.update(is_published_to_cvbook=False)
            message = f'{len(cv_ids)} CV(s) removed from CVBook'
        elif action == 'approve':
            cvs.update(admin_approved=True)
            message = f'{len(cv_ids)} CV(s) approved'
        elif action == 'unapprove':
            cvs.update(admin_approved=False)
            message = f'{len(cv_ids)} CV(s) unapproved'
        elif action == 'delete':
            cvs.delete()
            message = f'{len(cv_ids)} CV(s) deleted'
        else:
            return JsonResponse({'success': False, 'message': 'Invalid action'})
        
        return JsonResponse({'success': True, 'message': message})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

