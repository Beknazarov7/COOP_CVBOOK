from django.contrib import admin
from .models import CVSubmission, Education, ProfessionalExperience, TechnicalSkill
from django.utils.html import format_html

class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
    fields = ('degree_title', 'university', 'university_location', 'start_date', 'expected_graduation')

class ProfessionalExperienceInline(admin.TabularInline):
    model = ProfessionalExperience
    extra = 0
    fields = ('position_title', 'company', 'dates', 'accomplishments')

class TechnicalSkillInline(admin.TabularInline):
    model = TechnicalSkill
    extra = 0
    fields = ('programming_languages', 'frameworks_databases', 'tools', 'web_development')

@admin.register(CVSubmission)
class CVSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'surname', 'email', 'major', 'is_uca_student', 'cohort_status', 'is_published_to_cvbook', 'admin_approved', 'submitted_at']
    list_filter = ['is_uca_student', 'cohort_status', 'is_published_to_cvbook', 'admin_approved', 'submitted_at', 'major']
    search_fields = ['name', 'surname', 'email', 'major']
    readonly_fields = ['submitted_at']
    list_per_page = 25
    ordering = ['-submitted_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'surname', 'email', 'major', 'country')
        }),
        ('Academic Information', {
            'fields': ('graduation_year', 'status_preference', 'is_uca_student', 'cohort_status')
        }),
        ('Publication Settings', {
            'fields': ('is_published_to_cvbook', 'admin_approved'),
            'description': 'Control whether this CV appears in the public CVBook'
        }),
        ('System Information', {
            'fields': ('submitted_at', 'status'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [EducationInline, ProfessionalExperienceInline, TechnicalSkillInline]

# These models are managed through inlines in CVSubmissionAdmin

