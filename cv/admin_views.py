from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import CVSubmission
import json
import sqlite3
import os
from django.conf import settings

def get_all_seniors():
    db_path = os.path.join(settings.BASE_DIR, '..', 'UCA-Co-op-Website', 'db.sqlite3')
    print(f"DEBUG: Checking DB path: {db_path}")
    
    if not os.path.exists(db_path):
        return [{
            'name': f"DB NOT FOUND: {db_path}",
            'surname': '',
            'email': '',
            'major': '',
            'cohort_status': 'ERROR',
            'graduation_year': '',
        }]
        
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all students (not just seniors)
        cursor.execute("""
            SELECT
                u.first_name,
                u.last_name,
                u.email,
                s.major,
                s.cohort_status,
                s.graduation_year
            FROM students s
            JOIN users u ON s.user_id = u.id
        """)
        
        seniors = []
        for row in cursor.fetchall():
            seniors.append({
                'name': row['first_name'],
                'surname': row['last_name'],
                'email': row['email'],
                'major': row['major'],
                'cohort_status': row['cohort_status'],
                'graduation_year': row['graduation_year'],
            })
            
        conn.close()
        print(f"DEBUG: Fetched {len(seniors)} students/seniors from Co-op DB")
        return seniors
    except Exception as e:
        error_msg = f"DB ERROR: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        # Return error as a dummy student so it shows in UI
        return [{
            'name': error_msg,
            'surname': '',
            'email': '',
            'major': '',
            'cohort_status': 'ERROR',
            'graduation_year': '',
        }]

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
    
    # Build queryset for existing CVs
    cvs = CVSubmission.objects.filter(is_uca_student=True)
    
    # Identify emails of existing CVs for quick lookup
    # We fetch relevant fields to construct the object
    existing_cvs_map = {cv.email.lower(): cv for cv in cvs}
    
    # Get all students from Co-op DB
    students = get_all_seniors()  # Note: function name kept for backward compatibility
    
    # Combine list
    combined_list = []
    
    # Process students -> some have CV, some don't
    if not students:
         print("DEBUG: students list is empty!")
         # Add warning purely for debugging
         combined_list.append({
            'type': 'senior',
            'name': 'WARNING: No students from DB',
            'surname': '',
            'email': '',
            'major': '',
            'cohort': '',
            'graduation_year': '',
            'has_cv': False,
            'cv_id': None,
            'is_published': False,
            'is_approved': False,
            'submitted_at': None
         })
         
    processed_emails = set()
    
    for s in students:
        s_email = s['email'].lower() if s['email'] else ''
        if s_email:
            processed_emails.add(s_email)
        
        if s_email in existing_cvs_map:
            # Student has a CV
            cv = existing_cvs_map[s_email]
            item = {
                'type': 'cv',
                'name': cv.name,
                'surname': cv.surname,
                'email': cv.email,
                'major': cv.major,
                'cohort': cv.cohort_status,
                'graduation_year': cv.graduation_year,
                'has_cv': True,
                'cv_id': cv.id,
                'is_published': cv.is_published_to_cvbook,
                'is_approved': cv.admin_approved,
                'submitted_at': cv.submitted_at
            }
        else:
            # Student does NOT have a CV
            item = {
                'type': 'senior',
                'name': s['name'],
                'surname': s['surname'],
                'email': s['email'],
                'major': s['major'],
                'cohort': s['cohort_status'],
                'graduation_year': s['graduation_year'],
                'has_cv': False,
                'cv_id': None,
                'is_published': False,
                'is_approved': False,
                'submitted_at': None
            }
        combined_list.append(item)
        
    # Add remaining CVs (non-seniors or seniors not in Co-op DB list for some reason)
    for email_lower, cv in existing_cvs_map.items():
        if email_lower not in processed_emails:
            combined_list.append({
                'type': 'cv',
                'name': cv.name,
                'surname': cv.surname,
                'email': cv.email,
                'major': cv.major,
                'cohort': cv.cohort_status,
                'graduation_year': cv.graduation_year,
                'has_cv': True,
                'cv_id': cv.id,
                'is_published': cv.is_published_to_cvbook,
                'is_approved': cv.admin_approved,
                'submitted_at': cv.submitted_at
            })

    # Add a debugging entry to confirm view is working
    combined_list.insert(0, {
        'type': 'senior',
        'name': 'SYSTEM CHECK',
        'surname': 'WORKING',
        'email': 'debug@system.check',
        'major': 'Debug Major',
        'cohort': 'Debug Status',
        'graduation_year': '2026',
        'has_cv': False,
        'cv_id': None,
        'is_published': False,
        'is_approved': False,
        'submitted_at': None
    })
    
    # Apply filters in memory
    filtered_list = []
    
    for item in combined_list:
        # Search Filter
        if search_query:
            q = search_query.lower()
            if (q not in item['name'].lower() and 
                q not in item['surname'].lower() and 
                q not in item['email'].lower()):
                continue
                
        # Major Filter
        if major_filter:
            if major_filter.lower() not in item['major'].lower():
                continue
                
        # Cohort Filter
        if cohort_filter:
            if cohort_filter != item['cohort']:
                continue
        
        # Status Filter
        if status_filter:
            if status_filter == 'published' and not item['is_published']:
                continue
            if status_filter == 'unpublished' and item['is_published']:
                continue
            if status_filter == 'approved' and not item['is_approved']:
                continue
            if status_filter == 'pending' and item['is_approved']:
                continue
            if status_filter == 'missing' and item['has_cv']: # Custom filter for missing
                continue
            if status_filter == 'submitted' and not item['has_cv']:
                continue
                
        filtered_list.append(item)
    
    # Sort: Missing CVs first, then by Name
    # False < True, so has_cv will sort False (Missing) first
    filtered_list.sort(key=lambda x: (x['has_cv'], x['name'], x['surname']))
    
    # Pagination
    paginator = Paginator(filtered_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique values for filters (from existing CVs for simplicity, or we could aggregate)
    # Using simplistic approach effectively
    cohorts = sorted(list(set(item['cohort'] for item in combined_list if item['cohort'])))
    majors = sorted(list(set(item['major'] for item in combined_list if item['major'])))
    
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

