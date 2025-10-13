from django.db import models

class CVSubmission(models.Model):
    name = models.CharField(max_length=100)  # User's first name
    surname = models.CharField(max_length=100)  # User's last name
    email = models.EmailField(unique=True)  # Unique email as identifier
    major = models.CharField(max_length=100, blank=True, default='')  # User's major
    country = models.CharField(max_length=100, blank=True, default='')  # User's country
    city = models.CharField(max_length=100, blank=True, default='')  # User's city
    phone = models.CharField(max_length=20, blank=True, default='')  # User's phone number
    linkedin = models.URLField(blank=True, default='')  # LinkedIn profile URL
    github = models.URLField(blank=True, default='')  # GitHub profile URL
    graduation_year = models.CharField(max_length=4, blank=True, default='')  # Class year
    status_preference = models.CharField(max_length=100, blank=True, default='')  # Job seeking status
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='processed')
    
    # Student tracking fields
    is_uca_student = models.BooleanField(default=False)  # True if CV is from UCA student
    cohort_status = models.CharField(max_length=50, blank=True, default='')  # Student's cohort status
    is_published_to_cvbook = models.BooleanField(default=False)  # Whether CV is displayed in public CVBook
    admin_approved = models.BooleanField(default=False)  # Admin approval for CVBook display

    def __str__(self):
        return f"CV-{self.name} {self.surname}"

class Education(models.Model):
    cv = models.ForeignKey(CVSubmission, on_delete=models.CASCADE, related_name='educations')
    degree_title = models.CharField(max_length=200, blank=True, default='')
    university = models.CharField(max_length=200, blank=True, default='')
    start_date = models.CharField(max_length=50, blank=True, default='')
    expected_graduation = models.CharField(max_length=50, blank=True, default='')
    university_location = models.CharField(max_length=100, blank=True, null=True)
    honors = models.TextField(blank=True, default='')  # Academic honors
    relevant_courses = models.TextField(blank=True, default='')  # Relevant coursework
    
    def __str__(self):
        return f"{self.degree_title} at {self.university}" if self.university else self.degree_title

class Certificate(models.Model):
    education = models.ForeignKey(Education, on_delete=models.CASCADE, related_name='certificates')
    certificate_title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200, blank=True, default='')
    year = models.CharField(max_length=4, blank=True, default='')

    def __str__(self):
        return self.certificate_title

class ProfessionalExperience(models.Model):
    cv = models.ForeignKey(CVSubmission, on_delete=models.CASCADE, related_name='experiences')
    position_title = models.CharField(max_length=200, blank=True, default='')
    company = models.CharField(max_length=200, blank=True, default='')
    dates = models.CharField(max_length=50, blank=True, default='')
    accomplishments = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.position_title} at {self.company}" if self.company else self.position_title

class ProfessionalCompetency(models.Model):
    cv = models.ForeignKey(CVSubmission, on_delete=models.CASCADE, related_name='competencies')
    competency_type = models.CharField(max_length=200)
    key_accomplishments = models.TextField(blank=True, default='')

    def __str__(self):
        return self.competency_type

class Project(models.Model):
    cv = models.ForeignKey(CVSubmission, on_delete=models.CASCADE, related_name='projects')
    project_title = models.CharField(max_length=200)
    year = models.CharField(max_length=4, blank=True, default='')
    technologies_used = models.TextField(blank=True, default='')
    summary = models.TextField(blank=True, default='')
    accomplishment = models.TextField(blank=True, default='')

    def __str__(self):
        return self.project_title

class TechnicalSkill(models.Model):
    cv = models.ForeignKey(CVSubmission, on_delete=models.CASCADE, related_name='technical_skills')
    programming_languages = models.CharField(max_length=200, blank=True, default='')
    frameworks_databases = models.CharField(max_length=200, blank=True, default='')
    tools = models.CharField(max_length=200, blank=True, default='')
    web_development = models.CharField(max_length=200, blank=True, default='')
    multimedia = models.CharField(max_length=200, blank=True, default='')
    network = models.CharField(max_length=200, blank=True, default='')
    operating_systems = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return f"Skills for {self.cv.name} {self.cv.surname}"
    
class Language(models.Model):
    cv = models.ForeignKey(CVSubmission, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return self.name

class CommunityInvolvement(models.Model):
    cv = models.ForeignKey(CVSubmission, on_delete=models.CASCADE, related_name='community_involvements')
    position_title = models.CharField(max_length=200, blank=True, default='')
    organization = models.CharField(max_length=200, blank=True, default='')
    dates = models.CharField(max_length=50, blank=True, default='')
    achievements = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.position_title} at {self.organization}" if self.organization else self.position_title

class Award(models.Model):
    cv = models.ForeignKey(CVSubmission, on_delete=models.CASCADE, related_name='awards')
    award_name = models.CharField(max_length=200)
    year = models.CharField(max_length=4, blank=True, default='')
    presenting_organization = models.CharField(max_length=200, blank=True, default='')  # Organization that presented the award
    short_description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.award_name

class Reference(models.Model):
    cv = models.ForeignKey(CVSubmission, on_delete=models.CASCADE, related_name='references')
    reference_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200, blank=True, default='')
    company = models.CharField(max_length=200, blank=True, default='')  # Company/Organization
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=15, blank=True, default='')

    def __str__(self):
        return self.reference_name